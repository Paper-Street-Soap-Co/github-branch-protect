import json
import os

from github import Github
from google.cloud import secretmanager


"""load JSON config"""
with open("config.json", "r") as f:
    conf = json.load(f)


def github_api():
    """Use Github API (authenticate using GCP secretmanager credentials)
    Args:
        None
    Returns:
        github api object
    """
    client = secretmanager.SecretManagerServiceClient()
    secret_name = conf["secret_name"]
    project_id = os.environ["GCP_PROJECT"]
    resource = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(resource)
    return Github(response.payload.data.decode("UTF-8"))


def create_issue(gh, full_name, default_branch, login):
    """Create Github Issue.
    Args:
        gh (github.Github): The github api object (pygithub).
        <https://developer.github.com/v3/repos/branches/#update-branch-protection>
        <https://pygithub.readthedocs.io/en/latest/github.html#>
        full_name: The github organization and repository (org/repo)
        default_branch: The github repo default branch
        login: The github user that created the repository
    Returns:
        bool
    """
    title = f"branch protection enabled on {default_branch}"
    branch_protections = "\n".join([f"|{key}|{value}|" for key, value in conf["branch_protections"].items()])
    body = f"""@{login}

The following protections have been enabled on **{full_name}:{default_branch}**    
|**protection**|**setting**|
|---:|---:|
{branch_protections}

For more information about these settings, please refer to the [API Documentation](https://developer.github.com/v3/repos/branches/#update-branch-protection)."""

    gh.create_issue(
        title=title, body=body, assignee=login
    )
    return True


def update_branch_protection(gh, default_branch):
    """Update GitHub Branch Protection.
    Args:
        gh (github.Github): The github api object (pygithub).
        <https://developer.github.com/v3/repos/branches/#update-branch-protection>
        <https://pygithub.readthedocs.io/en/latest/github.html#>
        default_branch: The github default branch, sourced from request payload
    Returns:
        bool
    """
    branch = gh.get_branch(branch=default_branch)
    branch.edit_protection(**conf["branch_protections"])
    return True


def repository_event_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    json = request.get_json()
    if json and "action" in json:
        default_branch = json["repository"]["default_branch"]
        full_name = json["repository"]["full_name"]
        login = json["sender"]["login"]
        gh = github_api().get_repo(full_name)
        update_branch_protection(gh, default_branch)
        create_issue(gh, full_name, default_branch, login)
        return f"branch protection enabled for {full_name}:{default_branch}"
    else:
        return "branch protection skipped"
