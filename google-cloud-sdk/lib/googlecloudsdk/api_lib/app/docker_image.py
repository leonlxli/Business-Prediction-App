# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The Image class is a helper for building/pushing Docker images.

Provides stdio output parsing code and retry logic.
"""

import json
import re
import time

from docker import docker
from googlecloudsdk.api_lib.app import metric_names
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import metrics
from googlecloudsdk.core.console import console_attr_os

# Use the default width for logs that don't necessarily go to the screen
DOCKER_OUTPUT_BEGIN = ' DOCKER BUILD OUTPUT '
DOCKER_OUTPUT_LINE_CHAR = '-'
_SUCCESSFUL_BUILD_PATTERN = re.compile(r'Successfully built ([a-zA-Z0-9]{12})')

_RETRIES = 60
_STREAM = 'stream'


class Error(Exception):
  """Base exception for registry module."""


class ImageBuildError(exceptions.Error):
  """Image build related errors."""


class Image(object):
  """Docker image that requires building and should be removed afterwards."""

  def __init__(self, dockerfile_dir=None, repo=None, tag=None, nocache=False,
               rm=True):
    """Initializer for Image.

    Args:
      dockerfile_dir: str, Path to the directory with the Dockerfile.
      repo: str, Repository name to be applied to the image in case of
          successful build.
      tag: str, Repository tag to be applied to the image in case of successful
          build.
      nocache: boolean, True if cache should not be used when building the
          image.
      rm: boolean, True if intermediate images should be removed after a
          successful build. Default value is set to True because this is the
          default value used by "docker build" command.
    """
    self._dockerfile_dir = dockerfile_dir
    self._repo = repo
    self._tag = tag
    self._nocache = nocache
    self._rm = rm
    # Will be set during Build() method.
    self._id = None

  @property
  def dockerfile_dir(self):
    """Returns the directory the image is to be built from."""
    return self._dockerfile_dir

  @property
  def id(self):
    """Returns 64 hexadecimal digit string identifying the image."""
    # Might also be a first 12-characters shortcut.
    return self._id

  @property
  def repo(self):
    """Returns image repo string."""
    return self._repo

  @property
  def tag(self):
    """Returns image tag string."""
    return self._tag

  @property
  def tagged_repo(self):
    """Returns image repo string with tag, if it exists."""
    return '{0}:{1}'.format(self.repo, self.tag) if self.tag else self.repo

  def Build(self, docker_client):
    """Calls "docker build" command.

    Args:
      docker_client: instance of docker.Client connected to a Docker daemon.

    Raises:
      ImageBuildError: if the image could not be built.
    """
    log.info('Building docker image {0} from {1}/Dockerfile:'.format(
        self.tagged_repo, self._dockerfile_dir))

    width, _ = console_attr_os.GetTermSize()
    log.status.Print(DOCKER_OUTPUT_BEGIN.center(width, DOCKER_OUTPUT_LINE_CHAR))

    build_res = docker_client.build(
        path=self._dockerfile_dir, tag=self.tagged_repo, quiet=False,
        fileobj=None, nocache=self._nocache, rm=self._rm, pull=False)

    info = None
    error = None
    error_detail = None
    log_records = []
    try:
      for line in build_res:
        line = line.strip()
        if not line:
          continue
        log_record = json.loads(line)
        log_records.append(log_record)
        if 'stream' in log_record:
          info = log_record['stream'].strip()
          log.status.Print(info)
        if 'error' in log_record:
          error = log_record['error'].strip()
          # will be logged to log.error in the thrown exception
          log.status.Print(error)
        if 'errorDetail' in log_record:
          error_detail = log_record['errorDetail']['message'].strip()
          log.status.Print(error_detail)
    except docker.errors.APIError as e:
      log.error(e.explanation)
      error = e.explanation
      error_detail = ''
    finally:
      log.status.Print(DOCKER_OUTPUT_LINE_CHAR * width + '\n')

    if not log_records:
      raise ImageBuildError(
          'Error building docker image {0} [with no output]'.format(
              self.tagged_repo))

    success_message = log_records[-1].get(_STREAM)
    if success_message:
      m = _SUCCESSFUL_BUILD_PATTERN.match(success_message)
      if m:
        # The build was successful.
        self._id = m.group(1)
        log.info('Image %s built, id = %s', self.tagged_repo, self.id)
        return

    raise ImageBuildError('Docker build aborted: ' + error)

  def Push(self, docker_client):
    """Calls "docker push" command.

    Args:
      docker_client: instance of docker.Client connected to a Docker daemon.

    Raises:
      Error: if the push fails, even after retries.
    """
    docker_client.tag(self.id, self.repo, tag=self.tag, force=True)
    log.info('Pushing image to Google Container Registry...\n')
    def InnerPush():
      for line in docker_client.push(self.repo, tag=self.tag, stream=True):
        # Check for errors.
        _ProcessStreamingOutput(line)

    _Retry(InnerPush)
    metrics.CustomTimedEvent(metric_names.DOCKER_PUSH)


def _Retry(func, *args, **kwargs):
  """Retries the function if an exception occurs.

  Args:
    func: The function to call and retry.
    *args: Args to pass to the function.
    **kwargs: Kwargs to pass to the function.

  Returns:
    Whatever the function returns.
  """
  retries = _RETRIES
  while True:
    try:
      return func(*args, **kwargs)
    except Exception as e:  # pylint: disable=broad-except
      retries -= 1
      if retries > 0:
        log.info('Exception {e} thrown in {func}. Retrying.'.format(
            e=e, func=func.__name__))
        time.sleep(1)
      else:
        raise


def _ProcessStreamingOutput(line):
  """Handles the streaming output of the docker client.

  Args:
    line: a single line of streamed output.
  Raises:
    Error: if a problem occured during the operation with an explanation
           string if possible.
  """
  line = line.strip()
  if not line:
    return
  log_record = json.loads(line)
  if 'status' in log_record:
    feedback = log_record['status'].strip()
    if 'progress' in log_record:
      feedback += ': ' + log_record['progress'] + '\r'
    else:
      feedback += '\n'
    log.info(feedback)
  elif 'error' in log_record:
    error = log_record['error'].strip()
    log.error(error)
    raise Error('Unable to push the image to the registry: "%s"' % error)
  elif 'errorDetail' in log_record:
    error_detail = log_record['errorDetail'] or 'Unknown Error'
    raise Error('Unable to push the image to the registry: "%s"'
                % error_detail)
