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
"""Commands for updating backend services.

   There are separate alpha, beta, and GA command classes in this file.
"""

from googlecloudsdk.api_lib.compute import backend_services_utils
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.backend_services import flags
from googlecloudsdk.third_party.py27 import py27_copy as copy


@base.ReleaseTracks(base.ReleaseTrack.GA)
class UpdateGA(base_classes.ReadWriteCommand):
  """Update a backend service."""

  @staticmethod
  def Args(parser):
    flags.AddBackendServiceName(parser)
    flags.AddDescription(parser)
    flags.AddHttpHealthChecks(parser)
    flags.AddHttpsHealthChecks(parser)
    flags.AddTimeout(parser, default=None)
    flags.AddPortName(parser)
    flags.AddProtocol(parser, default=None)

  @property
  def service(self):
    return self.compute.backendServices

  @property
  def resource_type(self):
    return 'backendServices'

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name)

  def GetGetRequest(self, args):
    return (
        self.service,
        'Get',
        self.messages.ComputeBackendServicesGetRequest(
            project=self.project,
            backendService=self.ref.Name()))

  def GetSetRequest(self, args, replacement, _):
    return (
        self.service,
        'Update',
        self.messages.ComputeBackendServicesUpdateRequest(
            project=self.project,
            backendService=self.ref.Name(),
            backendServiceResource=replacement))

  def Modify(self, args, existing):
    replacement = copy.deepcopy(existing)

    if args.description:
      replacement.description = args.description
    elif args.description is not None:
      replacement.description = None

    health_checks = backend_services_utils.GetHealthChecks(args, self)
    if health_checks:
      replacement.healthChecks = health_checks

    if args.timeout:
      replacement.timeoutSec = args.timeout

    if args.port:
      replacement.port = args.port

    if args.port_name:
      replacement.portName = args.port_name

    if args.protocol:
      replacement.protocol = (self.messages.BackendService
                              .ProtocolValueValuesEnum(args.protocol))

    return replacement

  def Run(self, args):
    if not any([
        args.protocol,
        args.description is not None,
        args.http_health_checks,
        args.https_health_checks,
        args.timeout is not None,
        args.port,
        args.port_name,
    ]):
      raise exceptions.ToolException('At least one property must be modified.')

    return super(UpdateGA, self).Run(args)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(UpdateGA):
  """Update a backend service."""

  @staticmethod
  def Args(parser):
    flags.AddBackendServiceName(parser)
    flags.AddDescription(parser)
    flags.AddHttpHealthChecks(parser)
    flags.AddHttpsHealthChecks(parser)
    flags.AddTimeout(parser, default=None)
    flags.AddPortName(parser)
    flags.AddProtocol(parser, default=None)

    flags.AddConnectionDrainingTimeout(parser)
    flags.AddEnableCdn(parser)
    flags.AddHealthChecks(parser)
    flags.AddSessionAffinity(parser)
    flags.AddAffinityCookieTtl(parser)

  def Modify(self, args, existing):
    replacement = super(UpdateAlpha, self).Modify(args, existing)

    if args.connection_draining_timeout is not None:
      replacement.connectionDraining = self.messages.ConnectionDraining(
          drainingTimeoutSec=args.connection_draining_timeout)

    if args.enable_cdn is not None:
      replacement.enableCDN = args.enable_cdn

    if args.session_affinity is not None:
      replacement.sessionAffinity = (
          self.messages.BackendService.SessionAffinityValueValuesEnum(
              args.session_affinity))

    if args.affinity_cookie_ttl is not None:
      replacement.affinityCookieTtlSec = args.affinity_cookie_ttl

    return replacement

  def Run(self, args):
    if not any([
        args.protocol,
        args.description is not None,
        getattr(args, 'health_checks', None),
        args.http_health_checks,
        getattr(args, 'https_health_checks', None),
        args.timeout is not None,
        args.port,
        args.port_name,
        args.connection_draining_timeout is not None,
        args.enable_cdn is not None,
        args.session_affinity is not None,
        args.affinity_cookie_ttl is not None
    ]):
      raise exceptions.ToolException('At least one property must be modified.')

    return super(UpdateGA, self).Run(args)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(UpdateGA):
  """Update a backend service."""

  @staticmethod
  def Args(parser):
    flags.AddBackendServiceName(parser)
    flags.AddDescription(parser)
    flags.AddHttpHealthChecks(parser)
    flags.AddHttpsHealthChecks(parser)
    flags.AddTimeout(parser, default=None)
    flags.AddPortName(parser)
    flags.AddProtocol(parser, default=None)

    flags.AddEnableCdn(parser)
    flags.AddSessionAffinity(parser)
    flags.AddAffinityCookieTtl(parser)

  def Modify(self, args, existing):
    replacement = super(UpdateBeta, self).Modify(args, existing)

    if args.enable_cdn is not None:
      replacement.enableCDN = args.enable_cdn

    if args.session_affinity is not None:
      replacement.sessionAffinity = (
          self.messages.BackendService.SessionAffinityValueValuesEnum(
              args.session_affinity))

    if args.affinity_cookie_ttl is not None:
      replacement.affinityCookieTtlSec = args.affinity_cookie_ttl

    return replacement

  def Run(self, args):
    if not any([
        args.protocol,
        args.description is not None,
        args.http_health_checks,
        args.https_health_checks,
        args.timeout is not None,
        args.port,
        args.port_name,
        args.enable_cdn is not None,
        args.session_affinity is not None,
        args.affinity_cookie_ttl is not None
    ]):
      raise exceptions.ToolException('At least one property must be modified.')

    return super(UpdateGA, self).Run(args)


UpdateGA.detailed_help = {
    'brief': 'Update a backend service',
    'DESCRIPTION': """
        *{command}* is used to update backend services.
        """,
}
UpdateAlpha.detailed_help = UpdateGA.detailed_help
UpdateBeta.detailed_help = UpdateGA.detailed_help
