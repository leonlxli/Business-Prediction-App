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

"""Command to add IAM policy binding for an organization."""

import httplib

from googlecloudsdk.api_lib.organizations import errors
from googlecloudsdk.api_lib.organizations import orgs_base
from googlecloudsdk.api_lib.util import http_retry
from googlecloudsdk.calliope import base
from googlecloudsdk.core.iam import iam_util


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AddIamPolicyBinding(orgs_base.OrganizationCommand):
  """Add IAM policy binding for an organization.

  Adds a policy binding to the IAM policy of an organization,
  given an organization ID and the binding.
  """

  detailed_help = iam_util.GetDetailedHelpForAddIamPolicyBinding('organization',
                                                                 '123456789')

  @staticmethod
  def Args(parser):
    orgs_base.OrganizationCommand.IdArg(
        parser, 'ID for the organization to which you want to add a binding')
    iam_util.AddArgsForAddIamPolicyBinding(parser, 'id',
                                           'cloudresourcemanager.organizations')

  @errors.HandleHttpError
  @http_retry.RetryOnHttpStatus(httplib.CONFLICT)
  def Run(self, args):
    messages = self.OrganizationsMessages()
    org_name = self.GetOrganizationRef(args.id).Name()

    get_policy_request = (
        messages.CloudresourcemanagerOrganizationsGetIamPolicyRequest(
            resource=org_name,
            getIamPolicyRequest=messages.GetIamPolicyRequest()))
    policy = self.OrganizationsClient().GetIamPolicy(get_policy_request)

    iam_util.AddBindingToIamPolicy(messages, policy, args)

    set_policy_request = (
        messages.CloudresourcemanagerOrganizationsSetIamPolicyRequest(
            resource=org_name,
            setIamPolicyRequest=messages.SetIamPolicyRequest(policy=policy)))

    return self.OrganizationsClient().SetIamPolicy(set_policy_request)
