from pathlib import Path
from unittest.mock import Mock

from .base import BaseRepoAnalyzer
from .git import LocalBranch
from .weburl import WebURL


class DummyRepoAnalyzer(BaseRepoAnalyzer):
    def __init__(self):
        self.mock = Mock()
        self.mock.current_branch.return_value = "master"
        self.mock.remote_url.return_value = "git@github.com:USER/PROJECT.git"
        self.mock.remote_branch.return_value = "master"
        self.mock.need_pull_request.return_value = False

    def current_branch(self):
        return self.mock.current_branch()

    def remote_url(self, branch: str = "master") -> str:
        return self.mock.remote_url(branch)

    def remote_branch(self, branch: str) -> str:
        return self.mock.remote_branch(branch)

    def need_pull_request(self, branch: str) -> bool:
        return self.mock.need_pull_request(branch)

    def resolve_revision(self, revision: str) -> str:
        # Use mock to record invocations:
        self.mock.resolve_revision(revision)
        return {
            "master": "55150afe539493d650889224db136bc8d9b7ecb8",
            "HEAD": "55150afe539493d650889224db136bc8d9b7ecb8",
            "dev": "40539486fdaf08a39b57519eb06e0e200c932cfd",
        }[revision]

    def relpath(self, path):
        # Use mock to record invocations:
        self.mock.relpath(path)
        # Treat everything as "top-level" file:
        return Path(Path(path).name)


dummy_github_repo = DummyRepoAnalyzer


def dummy_gitlab_repo() -> BaseRepoAnalyzer:
    repo = DummyRepoAnalyzer()
    repo.mock.remote_url.return_value = "git@gitlab.com:USER/PROJECT.git"
    return repo


def dummy_bitbucket_repo() -> BaseRepoAnalyzer:
    repo = DummyRepoAnalyzer()
    repo.mock.remote_url.return_value = "git@bitbucket.org:USER/PROJECT.git"
    return repo


def dummy_github_weburl() -> WebURL:
    return LocalBranch(DummyRepoAnalyzer()).weburl()


def dummy_gitlab_weburl() -> WebURL:
    return LocalBranch(dummy_gitlab_repo()).weburl()


def dummy_bitbucket_weburl() -> WebURL:
    return LocalBranch(dummy_bitbucket_repo()).weburl()
