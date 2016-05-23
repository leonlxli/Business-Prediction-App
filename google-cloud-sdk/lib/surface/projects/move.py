# Copyright 2016 Google Inc. All Rights Reserved.
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
"""Command to move a project into an organization."""

import textwrap

from googlecloudsdk.api_lib.projects import errors
from googlecloudsdk.api_lib.projects import util
from googlecloudsdk.calliope import base
from googlecloudsdk.core import list_printer
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Move(util.ProjectCommand):
  """Move a project into an organization.

  Moves the given project into the given organization.

  This command can fail for the following reasons:
      * There is no project with the given ID.
      * There is no organization with the given ID.
      * The active account does not have  the
        resourcemanager.projects.update permission for the given
        project.
      * The active account does not have  the
        resourcemanager.projects.create permission for the given
        organization.
      * The given project is already in an organization.
  """

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          The following command moves a project with the ID
          `super-awesome-project` into the organization `25872158`:

            $ {command} super-awesome-project --organization=25872158
    """),
  }

  @staticmethod
  def Args(parser):
    parser.add_argument('id',
                        metavar='PROJECT_ID',
                        completion_resource='cloudresourcemanager.projects',
                        list_command_path='projects',
                        help='ID for the project you want to update.')
    parser.add_argument(
        '--organization',
        metavar='ORGANIZATION_ID',
        completion_resource='cloudresourcemanager.organizations',
        list_command_path='organizations',
        required=True,
        help='ID of the organization to move the project into.')

  @util.HandleHttpError
  def Run(self, args):
    projects = self.context['projects_client']
    messages = self.context['projects_messages']
    project_ref = self.GetProject(args.id)
    project = projects.projects.Get(project_ref.Request())
    if project.parent is not None:
      raise errors.ProjectMoveError(project, args.organization)
    project.parent = messages.ResourceId(id=args.organization,
                                         type='organization')
    result = projects.projects.Update(project)
    log.UpdatedResource(project_ref)
    return result

  def Display(self, args, result):
    """This method is called to print the result of the Run() method.

    Args:
      args: The arguments that command was run with.
      result: The value returned from the Run() method.
    """
    list_printer.PrintResourceList('cloudresourcemanager.projects', [result])
