# Copyright 2015 Google Inc. All Rights Reserved.
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
"""Implementation of gcloud genomics operations cancel.
"""

from googlecloudsdk.api_lib import genomics as lib
from googlecloudsdk.api_lib.genomics import genomics_util
from googlecloudsdk.api_lib.genomics.exceptions import GenomicsError
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io

_OPERATIONS_PREFIX = 'operations/'


class Cancel(base.Command):
  """Cancels an operation.
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument('name',
                        type=str,
                        help='The name of the operation to be canceled. The '
                        '"{0}" prefix for the name is optional.'
                        .format(_OPERATIONS_PREFIX))

  @genomics_util.ReraiseHttpException
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace, All the arguments that were provided to this
        command invocation.

    Raises:
      HttpException: An http error response was received while executing api
          request.
    Returns:
      None
    """
    apitools_client = self.context[lib.GENOMICS_APITOOLS_CLIENT_KEY]
    genomics_messages = self.context[lib.GENOMICS_MESSAGES_MODULE_KEY]

    name = args.name
    if not name.startswith(_OPERATIONS_PREFIX):
      name = _OPERATIONS_PREFIX + name

    # Look it up first so that we can display it
    op = apitools_client.operations.Get(
        genomics_messages.GenomicsOperationsGetRequest(name=name))
    self.format(op)

    if not console_io.PromptContinue(message='This operation will be canceled'):
      raise GenomicsError('Cancel aborted by user.')

    apitools_client.operations.Cancel(
        genomics_messages.GenomicsOperationsCancelRequest(name=name))
    log.status.write('Canceled [{0}].\n'.format(name))
