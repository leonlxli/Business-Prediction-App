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
"""Utility functions that don't belong in the other utility modules."""

# TODO(user): Move the top-level functions in base_classes.py here.

import argparse
import cStringIO
import re
import urlparse
from googlecloudsdk.api_lib.compute import constants
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.core import apis as core_apis
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resolvers
from googlecloudsdk.core import resources
from googlecloudsdk.core.console import console_io


class InstanceNotReadyError(calliope_exceptions.ToolException):
  """The user is attempting to perform an operation on a not-ready instance."""


class InvalidUserError(calliope_exceptions.ToolException):
  """The user provided an invalid username."""


class MissingDependencyError(calliope_exceptions.ToolException):
  """An external dependency is missing."""


class TimeoutError(calliope_exceptions.ToolException):
  """The user command timed out."""


class WrongInstanceTypeError(calliope_exceptions.ToolException):
  """The instance type is not appropriate for this command."""


def ZoneNameToRegionName(zone_name):
  """Converts zone name to region name: 'us-central1-a' -> 'us-central1'."""
  return zone_name.rsplit('-', 1)[0]


def CollectionToResourceType(collection):
  """Converts a collection to a resource type: 'compute.disks' -> 'disks'."""
  return collection.split('.', 1)[1]


def _GetApiNameFromCollection(collection):
  """Converts a collection to an api: 'compute.disks' -> 'compute'."""
  return collection.split('.', 1)[0]


def GetApiCollection(resource_type):
  """Coverts a resource type to a collection."""
  if resource_type in ['users', 'groups', 'globalAccountsOperations']:
    return 'clouduseraccounts.' + resource_type
  return 'compute.' + resource_type


def HasApiParamDefaultValue(api_resources, resource_type, param):
  """Returns whether the param has a default value."""
  collection = GetApiCollection(resource_type)
  api = _GetApiNameFromCollection(collection)
  try:
    api_resources.GetParamDefault(
        api=api,
        collection=resource_type,
        param=param)
  except properties.RequiredPropertyError:
    return False
  return True


def NormalizeGoogleStorageUri(uri):
  """Converts gs:// to http:// if uri begins with gs:// else returns uri."""
  if uri and uri.startswith('gs://'):
    return 'http://storage.googleapis.com/' + uri[len('gs://'):]
  else:
    return uri


def CamelCaseToOutputFriendly(string):
  """Converts camel case text into output friendly text.

  Args:
    string: The string to convert.

  Returns:
    The string converted from CamelCase to output friendly text.

  Examples:
    'camelCase' -> 'camel case'
    'CamelCase' -> 'camel case'
    'camelTLA' -> 'camel tla'
  """
  return re.sub('([A-Z]+)', r' \1', string).strip().lower()


def ConstructList(title, items):
  """Returns a string displaying the items and a title."""
  buf = cStringIO.StringIO()
  printer = console_io.ListPrinter(title)
  printer.Print(sorted(set(items)), output_stream=buf)
  return buf.getvalue()


def RaiseToolException(problems, error_message=None):
  """Raises a ToolException with the given list of problems."""
  RaiseException(problems, calliope_exceptions.ToolException, error_message)


def RaiseException(problems, exception, error_message=None):
  """Raises the provided exception with the given list of problems."""
  errors = []
  for _, message in problems:
    errors.append(message)

  raise exception(
      ConstructList(
          error_message or 'Some requests did not succeed:',
          errors))


def PromptForDeletion(refs, scope_name=None, prompt_title=None):
  """Prompts the user to confirm deletion of resources."""
  if not refs:
    return
  resource_type = CollectionToResourceType(refs[0].Collection())
  resource_name = CamelCaseToOutputFriendly(resource_type)
  prompt_list = []
  for ref in refs:
    if scope_name:
      item = '[{0}] in [{1}]'.format(ref.Name(), getattr(ref, scope_name))
    else:
      item = '[{0}]'.format(ref.Name())
    prompt_list.append(item)

  PromptForDeletionHelper(resource_name, prompt_list, prompt_title=prompt_title)


def PromptForDeletionHelper(resource_name, prompt_list, prompt_title=None):
  prompt_title = (prompt_title or
                  'The following {0} will be deleted:'.format(resource_name))
  prompt_message = ConstructList(prompt_title, prompt_list)
  if not console_io.PromptContinue(message=prompt_message):
    raise calliope_exceptions.ToolException('Deletion aborted by user.')


def BytesToGb(size):
  """Converts a disk size in bytes to GB."""
  if not size:
    return None

  if size % constants.BYTES_IN_ONE_GB != 0:
    raise calliope_exceptions.ToolException(
        'Disk size must be a multiple of 1 GB. Did you mean [{0}GB]?'
        .format(size / constants.BYTES_IN_ONE_GB + 1))

  return size / constants.BYTES_IN_ONE_GB


def WarnIfDiskSizeIsTooSmall(size_gb, disk_type):
  """Writes a warning message if the given disk size is too small."""
  if not size_gb:
    return

  if disk_type and 'pd-ssd' in disk_type:
    warning_threshold_gb = constants.SSD_DISK_PERFORMANCE_WARNING_GB
  else:
    warning_threshold_gb = constants.STANDARD_DISK_PERFORMANCE_WARNING_GB

  if size_gb < warning_threshold_gb:
    log.warn(
        'You have selected a disk size of under [%sGB]. This may result in '
        'poor I/O performance. For more information, see: '
        'https://developers.google.com/compute/docs/disks#pdperformance.',
        warning_threshold_gb)


def SetResourceParamDefaults():
  """Sets resource parsing default parameters to point to properties."""
  core_values = properties.VALUES.core
  compute_values = properties.VALUES.compute
  for api, param, prop in (
      ('compute', 'project', core_values.project),
      ('clouduseraccounts', 'project', core_values.project),
      ('resourceviews', 'projectName', core_values.project),
      ('compute', 'zone', compute_values.zone),
      ('resourceviews', 'zone', compute_values.zone),
      ('compute', 'region', compute_values.region),
      ('resourceviews', 'region', compute_values.region)):
    resources.SetParamDefault(
        api=api,
        collection=None,
        param=param,
        resolver=resolvers.FromProperty(prop))


def UpdateContextEndpointEntries(context, api_client_default='v1'):
  """Updates context to set API endpoints."""

  context['project'] = properties.VALUES.core.project.Get(required=True)

  api_client = core_apis.ResolveVersion('compute', api_client_default)
  compute = core_apis.GetClientInstance('compute', api_client)
  context['api-version'] = api_client
  context['compute'] = compute
  context['resources'] = resources.REGISTRY.CloneAndSwitchAPIs(compute)

  # Turn the endpoint into just the host.
  # eg. https://www.googleapis.com/compute/v1 -> https://www.googleapis.com
  compute_url = properties.VALUES.api_endpoint_overrides.compute.Get()
  u_endpoint = urlparse.urlparse(compute_url or 'https://www.googleapis.com')
  api_host = '%s://%s' % (u_endpoint.scheme, u_endpoint.netloc)
  context['batch-url'] = urlparse.urljoin(api_host, 'batch')

  # Construct cloud user accounts client.
  try:
    # TODO(user): User a separate API override from compute.
    clouduseraccounts = core_apis.GetClientInstance('clouduseraccounts',
                                                    api_client)
  except core_apis.UnknownVersionError:
    # Throw an error here once clouseuseraccounts has a v1 API version.
    clouduseraccounts = core_apis.GetClientInstance('clouduseraccounts', 'beta')

  context['clouduseraccounts'] = clouduseraccounts
  context['clouduseraccounts-resources'] = (
      resources.REGISTRY.CloneAndSwitchAPIs(clouduseraccounts))


def IsValidIPV4(ip):
  """Accepts an ipv4 address in string form and returns True if valid."""
  match = re.match(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', ip)
  if not match:
    return False

  octets = [int(x) for x in match.groups()]

  # first octet must not be 0
  if octets[0] == 0:
    return False

  for n in octets:
    if n < 0 or n > 255:
      return False

  return True


def IPV4Argument(value):
  """Argparse argument type that checks for a valid ipv4 address."""
  if not IsValidIPV4(value):
    raise argparse.ArgumentTypeError("invalid ipv4 value: '{0}'".format(value))

  return value
