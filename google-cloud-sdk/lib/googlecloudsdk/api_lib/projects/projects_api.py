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
"""Useful commands for interacting with the Cloud Resource Management API."""


from googlecloudsdk.api_lib.projects import util
from googlecloudsdk.third_party.apitools.base.py import list_pager


def List(client=None, messages=None, limit=None):
  if not client:
    client = util.GetClient()
  messages = messages or util.GetMessages()
  return list_pager.YieldFromList(
      client.projects,
      messages.CloudresourcemanagerProjectsListRequest(),
      limit=limit,
      field='projects',
      predicate=util.IsActive,
      batch_size_attribute='pageSize')
