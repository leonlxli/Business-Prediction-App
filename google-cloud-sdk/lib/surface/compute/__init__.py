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

"""The super-group for the compute CLI."""

import argparse
import sys

from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core import properties


DETAILED_HELP = {
    'brief': 'Read and manipulate Google Compute Engine resources',
}


def _DoFilter(context, api_client_default):
  """Set up paramter defaults."""
  utils.SetResourceParamDefaults()
  utils.UpdateContextEndpointEntries(context, api_client_default)


@base.ReleaseTracks(base.ReleaseTrack.GA)
class Compute(base.Group):
  """Read and manipulate Google Compute Engine resources."""
  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    pass

  def Filter(self, context, unused_args):
    _DoFilter(context, 'v1')


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ComputeBeta(base.Group):
  """Read and manipulate Google Compute Engine resources."""
  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    pass

  def Filter(self, context, unused_args):
    _DoFilter(context, 'beta')


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ComputeAlpha(base.Group):
  """Read and manipulate Google Compute Engine resources."""
  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    pass

  def Filter(self, context, unused_args):
    _DoFilter(context, 'alpha')
