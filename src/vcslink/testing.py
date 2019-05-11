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
        self.mock.need_pull_request.return_value = False

    def current_branch(self):
        return self.mock.current_branch()

    def remote_url(self, branch: str = "master") -> str:
        return self.mock.remote_url(branch)

    def need_pull_request(self, branch: str) -> bool:
        return self.mock.need_pull_request(branch)

    def resolve_revision(self, revision: str) -> str:
        # Use mock to record invocations:
        self.mock.resolve_revision(revision)
        return {
            "master": "55150afe539493d650889224db136bc8d9b7ecb8",
            "HEAD": "55150afe539493d650889224db136bc8d9b7ecb8",
        }[revision]

    def relpath(self, path):
        # Use mock to record invocations:
        self.mock.relpath(path)
        p = Path(path)
        assert not p.is_absolute()
        return p


def dummy_weburl() -> WebURL:
    return LocalBranch(DummyRepoAnalyzer()).weburl()
