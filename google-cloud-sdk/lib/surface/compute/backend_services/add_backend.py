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

"""Command for adding a backend to a backend service."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import instance_groups_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.backend_services import backend_flags
from googlecloudsdk.command_lib.compute.backend_services import flags
from googlecloudsdk.third_party.py27 import py27_copy as copy


@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class AddBackend(base_classes.ReadWriteCommand):
  """Add a backend to a backend service."""

  @staticmethod
  def Args(parser):
    flags.AddBackendServiceName(parser)
    backend_flags.AddDescription(parser)
    backend_flags.AddInstanceGroup(
        parser, operation_type='add to',
        multizonal=False, with_deprecated_zone=True)
    backend_flags.AddBalancingMode(parser)
    backend_flags.AddMaxUtilization(parser)
    backend_flags.AddRate(parser)
    backend_flags.AddCapacityScalar(parser)

  @property
  def service(self):
    return self.compute.backendServices

  @property
  def resource_type(self):
    return 'backendServices'

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name)

  def GetGetRequest(self, args):
    return (self.service,
            'Get',
            self.messages.ComputeBackendServicesGetRequest(
                backendService=self.ref.Name(),
                project=self.project))

  def GetSetRequest(self, args, replacement, existing):
    return (self.service,
            'Update',
            self.messages.ComputeBackendServicesUpdateRequest(
                backendService=self.ref.Name(),
                backendServiceResource=replacement,
                project=self.project))

  def CreateGroupReference(self, args):
    return self.CreateZonalReference(
        args.instance_group,
        args.instance_group_zone,
        resource_type='instanceGroups')

  def Modify(self, args, existing):
    backend_flags.WarnOnDeprecatedFlags(args)
    replacement = copy.deepcopy(existing)

    group_ref = self.CreateGroupReference(args)

    group_uri = group_ref.SelfLink()

    for backend in existing.backends:
      if group_uri == backend.group:
        raise exceptions.ToolException(
            'Backend [{0}] in zone [{1}] already exists in backend service '
            '[{2}].'.format(group_ref.Name(),
                            group_ref.zone,
                            args.name))

    if args.balancing_mode:
      balancing_mode = self.messages.Backend.BalancingModeValueValuesEnum(
          args.balancing_mode)
    else:
      balancing_mode = None

    backend = self.messages.Backend(
        balancingMode=balancing_mode,
        capacityScaler=args.capacity_scaler,
        description=args.description,
        group=group_uri,
        maxRate=args.max_rate,
        maxRatePerInstance=args.max_rate_per_instance,
        maxUtilization=args.max_utilization)

    replacement.backends.append(backend)
    return replacement


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AddBackendAlpha(AddBackend,
                      instance_groups_utils.InstanceGroupReferenceMixin):
  """Add a backend to a backend service."""

  @staticmethod
  def Args(parser):
    flags.AddBackendServiceName(parser)
    backend_flags.AddDescription(parser)
    backend_flags.AddInstanceGroup(
        parser, operation_type='add to', multizonal=True)
    backend_flags.AddBalancingMode(parser)
    backend_flags.AddMaxUtilization(parser)
    backend_flags.AddRate(parser)
    backend_flags.AddCapacityScalar(parser)

  def CreateGroupReference(self, args):
    return self.CreateInstanceGroupReference(
        name=args.instance_group,
        region=args.instance_group_region,
        zone=args.instance_group_zone,
        zonal_resource_type='instanceGroups',
        regional_resource_type='regionInstanceGroups')


AddBackend.detailed_help = {
    'brief': 'Add a backend to a backend service',
    'DESCRIPTION': """
        *{command}* is used to add a backend to a backend service. A
        backend is a group of tasks that can handle requests sent to a
        backend service. Currently, the group of tasks can be one or
        more Google Compute Engine virtual machine instances grouped
        together using an instance group.

        Traffic is first spread evenly across all virtual machines in
        the group. When the group is full, traffic is sent to the next
        nearest group(s) that still have remaining capacity.

        To modify the parameters of a backend after it has been added
        to the backend service, use 'gcloud compute backend-services
        update-backend' or 'gcloud compute backend-services edit'.
        """,
}
AddBackendAlpha.detailed_help = AddBackend.detailed_help
