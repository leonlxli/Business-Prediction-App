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


"""Implementation of gcloud genomics datasets add-iam-policy-binding
"""

from googlecloudsdk.calliope import base
from googlecloudsdk.core.iam import iam_util
from googlecloudsdk.api_lib import genomics as lib
from googlecloudsdk.api_lib.genomics import genomics_util


class AddIamPolicyBinding(base.Command):
  """Add IAM policy binding for a dataset.

  This command adds a policy binding to the IAM policy of a dataset,
  given a dataset ID and the binding.
  """

  detailed_help = iam_util.GetDetailedHelpForAddIamPolicyBinding(
      'dataset', '1000')

  @staticmethod
  def Args(parser):
    parser.add_argument('id', type=str,
                        help='The ID of the dataset.')
    iam_util.AddArgsForAddIamPolicyBinding(
        parser, 'id', 'genomics.datasets')

  @genomics_util.ReraiseHttpException
  def Run(self, args):
    apitools_client = self.context[lib.GENOMICS_APITOOLS_CLIENT_KEY]
    messages = self.context[lib.GENOMICS_MESSAGES_MODULE_KEY]
    resources = self.context[lib.GENOMICS_RESOURCES_KEY]

    dataset_resource = resources.Parse(args.id, collection='genomics.datasets')

    policy_request = messages.GenomicsDatasetsGetIamPolicyRequest(
        resource='datasets/{0}'.format(dataset_resource.Name()),
        getIamPolicyRequest=messages.GetIamPolicyRequest(),
    )
    policy = apitools_client.datasets.GetIamPolicy(policy_request)

    iam_util.AddBindingToIamPolicy(messages, policy, args)

    policy_request = messages.GenomicsDatasetsSetIamPolicyRequest(
        resource='datasets/{0}'.format(dataset_resource.Name()),
        setIamPolicyRequest=messages.SetIamPolicyRequest(policy=policy),
    )
    return apitools_client.datasets.SetIamPolicy(policy_request)

  def Display(self, args, result):
    """This method is called to print the result of the Run() method.

    Args:
      args: The arguments that command was run with.
      result: The value returned from the Run() method.
    """
    _ = args  # in case lint gets unhappy about unused args.
    # pylint:disable=not-callable, self.format is callable.
    self.format(result)
