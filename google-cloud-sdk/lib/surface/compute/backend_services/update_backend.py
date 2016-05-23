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

"""Command for updating a backend in a backend service."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import instance_groups_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.backend_services import backend_flags
from googlecloudsdk.command_lib.compute.backend_services import flags
from googlecloudsdk.third_party.py27 import py27_copy as copy


@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class UpdateBackend(base_classes.ReadWriteCommand):
  """Update an existing backend in a backend service."""

  @staticmethod
  def Args(parser):
    flags.AddBackendServiceName(parser)
    backend_flags.AddDescription(parser)
    backend_flags.AddInstanceGroup(
        parser, operation_type='update', multizonal=False,
        with_deprecated_zone=True)
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

    backend_to_update = None
    for backend in replacement.backends:
      if group_ref.SelfLink() == backend.group:
        backend_to_update = backend

    if not backend_to_update:
      scope_type = None
      scope_name = None
      if hasattr(group_ref, 'zone'):
        scope_type = 'zone'
        scope_name = group_ref.zone
      if hasattr(group_ref, 'region'):
        scope_type = 'region'
        scope_name = group_ref.region
      raise exceptions.ToolException(
          'No backend with name [{0}] in {1} [{2}] is part of the backend '
          'service [{3}].'.format(
              group_ref.Name(), scope_type, scope_name, self.ref.Name()))

    if args.description:
      backend_to_update.description = args.description
    elif args.description is not None:
      backend_to_update.description = None

    if args.balancing_mode:
      backend_to_update.balancingMode = (
          self.messages.Backend.BalancingModeValueValuesEnum(
              args.balancing_mode))

      # If the balancing mode is being changed to RATE, we must clear
      # the max utilization field, otherwise the server will reject
      # the request.
      if (backend_to_update.balancingMode ==
          self.messages.Backend.BalancingModeValueValuesEnum.RATE):
        backend_to_update.maxUtilization = None

    # Now, we set the parameters that control load balancing. The user
    # can still provide a control parameter that is incompatible with
    # the balancing mode; like the add-backend subcommand, we leave it
    # to the server to perform validation on this.
    #
    # TODO(user): In the future, we probably should do this
    # validation client-side, so we can produce better error messages.
    if args.max_utilization is not None:
      backend_to_update.maxUtilization = args.max_utilization

    if args.max_rate is not None:
      backend_to_update.maxRate = args.max_rate
      backend_to_update.maxRatePerInstance = None

    if args.max_rate_per_instance is not None:
      backend_to_update.maxRate = None
      backend_to_update.maxRatePerInstance = args.max_rate_per_instance

    if args.capacity_scaler is not None:
      backend_to_update.capacityScaler = args.capacity_scaler

    return replacement

  def Run(self, args):
    if not any([
        args.description is not None,
        args.balancing_mode,
        args.max_utilization is not None,
        args.max_rate is not None,
        args.max_rate_per_instance is not None,
        args.capacity_scaler is not None,
    ]):
      raise exceptions.ToolException('At least one property must be modified.')

    return super(UpdateBackend, self).Run(args)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateBackendAlpha(UpdateBackend,
                         instance_groups_utils.InstanceGroupReferenceMixin):
  """Update an existing backend in a backend service."""

  @staticmethod
  def Args(parser):
    flags.AddBackendServiceName(parser)
    backend_flags.AddDescription(parser)
    backend_flags.AddInstanceGroup(
        parser, operation_type='update', multizonal=True)
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


UpdateBackend.detailed_help = {
    'brief': 'Update an existing backend in a backend service',
    'DESCRIPTION': """
        *{command}* updates a backend that is part of a backend
        service. This is useful for changing the way a backend
        behaves. Example changes that can be made include changing the
        load balancing policy and ``draining'' a backend by setting
        its capacity scaler to zero.

        Backends are named by their associated instances groups, and one
        of the ``--group'' or ``--instance-group'' flags is required to
        identify the backend that you are modifying.  You cannot "change"
        the instance group associated with a backend, but you can accomplish
        something similar with ``backend-services remove-backend'' and
        ``backend-services add-backend''.

        'gcloud compute backend-services edit' can also be used to
        update a backend if the use of a text editor is desired.
        """,
}
UpdateBackendAlpha.detailed_help = UpdateBackend.detailed_help
