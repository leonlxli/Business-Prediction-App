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

"""Delete command for gcloud debug snapshots command group."""

from googlecloudsdk.api_lib.debug import debug
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


class Delete(base.DeleteCommand):
  """Delete debug snapshots.

  This command deletes snapshots from a Cloud Debugger debug target.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'id_or_location_regexp', metavar='(ID|LOCATION-REGEXP)', nargs='+',
        help="""\
            One or more snapshot IDs, resource identifiers, or regular
            expressions to match against snapshot locations. All snapshots
            matching any of these values will be deleted.
        """)
    parser.add_argument(
        '--all-users', action='store_true', default=False,
        help="""\
            If set, matching snapshots from all users will be deleted, rather
            than only snapshots created by the current user.
        """)
    parser.add_argument(
        '--include-inactive', action='store_true', default=False,
        help="""\
            If set, also delete snapshots which have been completed. By default,
            only pending snapshots will be deleted.
        """)

  def Run(self, args):
    """Run the delete command."""
    project_id = properties.VALUES.core.project.Get(required=True)
    debugger = debug.Debugger(project_id)
    debuggee = debugger.FindDebuggee(args.target)
    snapshots = debuggee.ListBreakpoints(
        args.id_or_location_regexp, include_all_users=args.all_users,
        include_inactive=args.include_inactive,
        restrict_to_type=debugger.SNAPSHOT_TYPE)
    if not console_io.PromptContinue(
        message='This command will delete {0} snapshots.'.format(
            len(snapshots))):
      raise calliope_exceptions.ToolException('Delete aborted by user.')
    for s in snapshots:
      debuggee.DeleteBreakpoint(s.id)
    # Guaranteed we have at least one snapshot, since ListMatchingBreakpoints
    # would raise an exception otherwise.
    if len(snapshots) == 1:
      log.status.write('Deleted 1 snapshot.\n')
    else:
      log.status.write('Deleted {0} snapshots.\n'.format(len(snapshots)))
    return snapshots

  def Collection(self):
    return 'debug.snapshots'
