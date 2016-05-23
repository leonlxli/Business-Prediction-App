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

"""Command for getting health status of backend(s) in a backend service."""

from googlecloudsdk.api_lib.compute import request_helper
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.backend_services import flags
from googlecloudsdk.core import exceptions


class GetHealth(base.Command):
  """Get backend health statuses from a backend service.

  *{command}* is used to request the current health status of
  instances in a backend service. Every group in the service
  is checked and the health status of each configured instance
  is printed.

  If a group contains names of instances that don't exist or
  instances that haven't yet been pushed to the load-balancing
  system, they will not show up. Those that are listed as
  ``HEALTHY'' are able to receive load-balanced traffic. Those that
  are marked as ``UNHEALTHY'' are either failing the configured
  health-check or not responding to it.

  Since the health checks are performed continuously and in
  a distributed manner, the state returned by this command is
  the most recent result of a vote of several redundant health
  checks. Backend services that do not have a valid global
  forwarding rule referencing it will not be health checked and
  so will have no health status.
  """

  @staticmethod
  def Args(parser):
    flags.AddBackendServiceName(parser)

  def _GetBackendService(self, client, backend_service_ref):
    """Fetches the backend service resource."""
    errors = []
    messages = client.MESSAGES_MODULE
    objects = list(request_helper.MakeRequests(
        requests=[(client.backendServices,
                   'Get',
                   messages.ComputeBackendServicesGetRequest(
                       project=backend_service_ref.project,
                       backendService=backend_service_ref.Name()
                   ))],
        http=client.http,
        batch_url=self.context['batch-url'],
        errors=errors,
        custom_get_requests=None))
    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not fetch backend service:')
    return objects[0]

  def Run(self, args):
    """Returns a list of backendServiceGroupHealth objects."""
    backend_service_ref = self.context['resources'].Parse(
        args.name,
        collection='compute.backendServices')
    client = self.context['compute']
    backend_service = self._GetBackendService(client, backend_service_ref)
    if not backend_service.backends:
      return

    messages = client.MESSAGES_MODULE
    # Call GetHealth for each group in the backend service
    requests = []
    for backend in backend_service.backends:
      request_message = messages.ComputeBackendServicesGetHealthRequest(
          resourceGroupReference=messages.ResourceGroupReference(
              group=backend.group),
          project=backend_service_ref.project,
          backendService=backend_service_ref.Name())
      requests.append((client.backendServices, 'GetHealth', request_message))

    # Instead of batching-up all requests and making a single
    # request_helper.MakeRequests call, go one backend at a time.
    # We do this because getHealth responses don't say what resource
    # they correspond to.  It's not obvious how to reliably match up
    # responses and backends when there are errors.  Addtionally the contract
    # for MakeRequests doesn't guarantee response order will match
    # request order.
    #
    # TODO(b/25015230) Simply make a batch request once the response
    # gives more information.
    errors = []
    for request in requests:
      # The list() call below is itended to force the generator returned by
      # MakeRequests.  If there are exceptions the command will abort, which is
      # expected.  Having a list simplifies some of the checks that follow.
      resources = list(request_helper.MakeRequests(
          requests=[request],
          http=client.http,
          batch_url=self.context['batch-url'],
          errors=errors,
          custom_get_requests=None))

      if len(resources) is 0:
        #  Request failed, error information will accumulate in errors
        continue

      try:
        [resource] = resources
      except ValueError:
        # Intended to throw iff resources contains more than one element.  Just
        # want to avoid a user potentially seeing an index out of bounds
        # exception.
        raise exceptions.InternalError('Invariant failure')

      yield {
          'backend': request[2].resourceGroupReference.group,
          'status': resource
      }

    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not get health for some groups:')
