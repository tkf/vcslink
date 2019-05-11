from pathlib import Path

from .base import BaseRepoAnalyzer
from .git import LocalBranch
from .weburl import WebURL


class DummyRepoAnalyzer(BaseRepoAnalyzer):
    def current_branch(self):
        return "master"

    def remote_url(self, branch: str = "master") -> str:
        return "git@github.com:USER/PROJECT.git"

    _need_pull_request = False

    def need_pull_request(self, branch: str) -> bool:
        return self._need_pull_request

    def resolve_revision(self, revision: str) -> str:
        return {
            "master": "55150afe539493d650889224db136bc8d9b7ecb8",
            "HEAD": "55150afe539493d650889224db136bc8d9b7ecb8",
        }[revision]

    def relpath(self, path):
        p = Path(path)
        assert not p.is_absolute()
        return p


def dummy_weburl() -> WebURL:
    return LocalBranch(DummyRepoAnalyzer()).weburl()
