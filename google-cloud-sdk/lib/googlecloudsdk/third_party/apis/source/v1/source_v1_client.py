"""Generated client library for source version v1."""
# NOTE: This file is autogenerated and should not be edited by hand.
from googlecloudsdk.third_party.apitools.base.py import base_api
from googlecloudsdk.third_party.apis.source.v1 import source_v1_messages as messages


class SourceV1(base_api.BaseApiClient):
  """Generated client library for service source version v1."""

  MESSAGES_MODULE = messages
  BASE_URL = u'https://source.googleapis.com/'

  _PACKAGE = u'source'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform']
  _VERSION = u'v1'
  _CLIENT_ID = '1042881264118.apps.googleusercontent.com'
  _CLIENT_SECRET = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _USER_AGENT = 'x_Tw5K8nnjoRAqULM9PFAC2b'
  _CLIENT_CLASS_NAME = u'SourceV1'
  _URL_VERSION = u'v1'
  _API_KEY = None

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new source handle."""
    url = url or self.BASE_URL
    super(SourceV1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.projects_repos_workspaces = self.ProjectsReposWorkspacesService(self)
    self.projects_repos = self.ProjectsReposService(self)
    self.projects = self.ProjectsService(self)

  class ProjectsReposWorkspacesService(base_api.BaseApiService):
    """Service class for the projects_repos_workspaces resource."""

    _NAME = u'projects_repos_workspaces'

    def __init__(self, client):
      super(SourceV1.ProjectsReposWorkspacesService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'source.projects.repos.workspaces.create',
              ordered_params=[u'projectId', u'repoName'],
              path_params=[u'projectId', u'repoName'],
              query_params=[],
              relative_path=u'v1/projects/{projectId}/repos/{repoName}/workspaces',
              request_field=u'createWorkspaceRequest',
              request_type_name=u'SourceProjectsReposWorkspacesCreateRequest',
              response_type_name=u'Workspace',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'source.projects.repos.workspaces.delete',
              ordered_params=[u'projectId', u'repoName', u'name'],
              path_params=[u'name', u'projectId', u'repoName'],
              query_params=[u'currentSnapshotId', u'uid'],
              relative_path=u'v1/projects/{projectId}/repos/{repoName}/workspaces/{name}',
              request_field='',
              request_type_name=u'SourceProjectsReposWorkspacesDeleteRequest',
              response_type_name=u'Empty',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'source.projects.repos.workspaces.get',
              ordered_params=[u'projectId', u'repoName', u'name'],
              path_params=[u'name', u'projectId', u'repoName'],
              query_params=[u'uid'],
              relative_path=u'v1/projects/{projectId}/repos/{repoName}/workspaces/{name}',
              request_field='',
              request_type_name=u'SourceProjectsReposWorkspacesGetRequest',
              response_type_name=u'Workspace',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'source.projects.repos.workspaces.list',
              ordered_params=[u'projectId', u'repoName'],
              path_params=[u'projectId', u'repoName'],
              query_params=[u'uid', u'view'],
              relative_path=u'v1/projects/{projectId}/repos/{repoName}/workspaces',
              request_field='',
              request_type_name=u'SourceProjectsReposWorkspacesListRequest',
              response_type_name=u'ListWorkspacesResponse',
              supports_download=False,
          ),
          'ModifyWorkspace': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'source.projects.repos.workspaces.modifyWorkspace',
              ordered_params=[u'projectId', u'repoName', u'name'],
              path_params=[u'name', u'projectId', u'repoName'],
              query_params=[],
              relative_path=u'v1/projects/{projectId}/repos/{repoName}/workspaces/{name}:modifyWorkspace',
              request_field=u'modifyWorkspaceRequest',
              request_type_name=u'SourceProjectsReposWorkspacesModifyWorkspaceRequest',
              response_type_name=u'Workspace',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Creates a workspace.

      Args:
        request: (SourceProjectsReposWorkspacesCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Workspace) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes a workspace. Uncommitted changes are lost. If the workspace does.
not exist, NOT_FOUND is returned. Returns ABORTED when the workspace is
simultaneously modified by another client.

      Args:
        request: (SourceProjectsReposWorkspacesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Empty) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns workspace metadata.

      Args:
        request: (SourceProjectsReposWorkspacesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Workspace) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Returns all workspaces belonging to a repo.

      Args:
        request: (SourceProjectsReposWorkspacesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListWorkspacesResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def ModifyWorkspace(self, request, global_params=None):
      """Applies an ordered sequence of file modification actions to a workspace.
Returns ABORTED if current_snapshot_id in the request does not refer to
the most recent update to the workspace or if the workspace is
simultaneously modified by another client.

      Args:
        request: (SourceProjectsReposWorkspacesModifyWorkspaceRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Workspace) The response message.
      """
      config = self.GetMethodConfig('ModifyWorkspace')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsReposService(base_api.BaseApiService):
    """Service class for the projects_repos resource."""

    _NAME = u'projects_repos'

    def __init__(self, client):
      super(SourceV1.ProjectsReposService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'source.projects.repos.create',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'v1/projects/{projectId}/repos',
              request_field='<request>',
              request_type_name=u'Repo',
              response_type_name=u'Repo',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'source.projects.repos.delete',
              ordered_params=[u'projectId', u'repoName'],
              path_params=[u'projectId', u'repoName'],
              query_params=[u'uid'],
              relative_path=u'v1/projects/{projectId}/repos/{repoName}',
              request_field='',
              request_type_name=u'SourceProjectsReposDeleteRequest',
              response_type_name=u'Empty',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'source.projects.repos.get',
              ordered_params=[u'projectId', u'repoName'],
              path_params=[u'projectId', u'repoName'],
              query_params=[u'uid'],
              relative_path=u'v1/projects/{projectId}/repos/{repoName}',
              request_field='',
              request_type_name=u'SourceProjectsReposGetRequest',
              response_type_name=u'Repo',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'source.projects.repos.list',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'v1/projects/{projectId}/repos',
              request_field='',
              request_type_name=u'SourceProjectsReposListRequest',
              response_type_name=u'ListReposResponse',
              supports_download=False,
          ),
          'Update': base_api.ApiMethodInfo(
              http_method=u'PUT',
              method_id=u'source.projects.repos.update',
              ordered_params=[u'projectId', u'repoName'],
              path_params=[u'projectId', u'repoName'],
              query_params=[],
              relative_path=u'v1/projects/{projectId}/repos/{repoName}',
              request_field=u'updateRepoRequest',
              request_type_name=u'SourceProjectsReposUpdateRequest',
              response_type_name=u'Repo',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Creates a repo in the given project. The provided repo message should have.
its name field set to the desired repo name. No other repo fields should
be set. Omitting the name is the same as specifying "default"

Repo names must satisfy the regular expression
`a-z{1,61}[a-z0-9]`. (Note that repo names must contain at
least three characters and may not contain underscores.) The special name
"default" is the default repo for the project; this is the repo shown when
visiting the Cloud Developers Console, and can be accessed via git's HTTP
protocol at `https://source.developers.google.com/p/PROJECT_ID`. You may
create other repos with this API and access them at
`https://source.developers.google.com/p/PROJECT_ID/r/NAME`.

      Args:
        request: (Repo) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Repo) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes a repo.

      Args:
        request: (SourceProjectsReposDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Empty) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns information about a repo.

      Args:
        request: (SourceProjectsReposGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Repo) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Returns all repos belonging to a project, specified by its project ID. The.
response list is sorted by name with the default repo listed first.

      Args:
        request: (SourceProjectsReposListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListReposResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Update(self, request, global_params=None):
      """Updates an existing repo. The only things you can change about a repo are:.
  1) its repo_sync_config (and then only to add one that is not present);
  2) its last-updated time; and
  3) its name.

      Args:
        request: (SourceProjectsReposUpdateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Repo) The response message.
      """
      config = self.GetMethodConfig('Update')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = u'projects'

    def __init__(self, client):
      super(SourceV1.ProjectsService, self).__init__(client)
      self._method_configs = {
          }

      self._upload_configs = {
          }