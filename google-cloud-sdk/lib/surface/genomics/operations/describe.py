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
"""Implementation of gcloud genomics operations describe.
"""

from googlecloudsdk.api_lib import genomics as lib
from googlecloudsdk.api_lib.genomics import genomics_util
from googlecloudsdk.calliope import base

_OPERATIONS_PREFIX = 'operations/'


class Describe(base.Command):
  """Returns details about an operation.
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument('name',
                        type=str,
                        help=('The name of the operation to be described. The '
                              '"{0}" prefix for the name is optional.'
                              .format(_OPERATIONS_PREFIX)))

  @genomics_util.ReraiseHttpException
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace, All the arguments that were provided to this
        command invocation.

    Returns:
      a Operation message
    """
    apitools_client = self.context[lib.GENOMICS_APITOOLS_CLIENT_KEY]
    genomics_messages = self.context[lib.GENOMICS_MESSAGES_MODULE_KEY]

    name = args.name
    if not name.startswith(_OPERATIONS_PREFIX):
      name = _OPERATIONS_PREFIX + name
    return apitools_client.operations.Get(
        genomics_messages.GenomicsOperationsGetRequest(name=name))

  def Display(self, args_unused, operation):
    """This method is called to print the result of the Run() method.

    Args:
      args_unused: The arguments that command was run with.
      operation: The Operation message returned from the Run() method.
    """
    self.format(operation)
