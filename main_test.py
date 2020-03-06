import unittest
from unittest.mock import MagicMock, patch

import main


class TestBranchProtect(unittest.TestCase):
    @patch("main.Github")
    @patch("google.cloud.secretmanager.SecretManagerServiceClient")
    def test_github_api(self, MockSecretManagerServiceClient, MockGithub):
        gh = main.github_api()

    @patch("main.Github")
    @patch("google.cloud.secretmanager.SecretManagerServiceClient")
    def test_create_issue(self, MockSecretManagerServiceClient, MockGithub):
        gh = main.github_api()
        main.create_issue(gh, "initrode/test-repo", "master", "cvega")

    @patch("main.Github")
    @patch("google.cloud.secretmanager.SecretManagerServiceClient")
    def test_update_branch_protection(self, MockSecretManagerServiceClient, MockGithub):
        gh = main.github_api()
        main.update_branch_protection(gh, "master")

    @patch("main.Github")
    @patch("google.cloud.secretmanager.SecretManagerServiceClient")
    def test_repository_event_http(self, MockSecretManagerServiceClient, MockGithub):
        request = MagicMock()
        request.get_json = MagicMock(
            return_value={
                "action": {},
                "repository": {
                    "default_branch": "master",
                    "full_name": "initrode/test-repo",
                },
                "sender": {"login": "cvega"},
            }
        )
        main.repository_event_http(request)

    @patch("main.Github")
    @patch("google.cloud.secretmanager.SecretManagerServiceClient")
    def test_repository_event_http_without_action(
        self, MockSecretManagerServiceClient, MockGithub
    ):
        request = MagicMock()
        main.repository_event_http(request)
