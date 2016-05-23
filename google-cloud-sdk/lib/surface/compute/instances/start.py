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

"""Command for starting an instance."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.command_lib.compute import flags


class Start(base_classes.NoOutputAsyncMutator):
  """Start a stopped virtual machine instance.

  *{command}* is used to start a stopped Google Compute Engine virtual machine.
  Only a stopped virtual machine can be started.
  """

  @staticmethod
  def Args(parser):
    flags.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='start')

    parser.add_argument(
        'name',
        nargs='+',
        completion_resource='compute.instances',
        help='The names of the instances to start.')

  @property
  def service(self):
    return self.compute.instances

  @property
  def method(self):
    return 'Start'

  @property
  def resource_type(self):
    return 'instances'

  def CreateRequests(self, args):
    request_list = []
    for name in args.name:
      instance_ref = self.CreateZonalReference(name, args.zone)

      request = self.messages.ComputeInstancesStartRequest(
          instance=instance_ref.Name(),
          project=self.project,
          zone=instance_ref.zone)

      request_list.append(request)
    return request_list

  def Format(self, _):
    # There is no need to display anything when starting an
    # instance. Instead, format 'none' consumes the generator returned from
    # Run() # to invoke the logic that waits for the start to complete.
    return 'none'
