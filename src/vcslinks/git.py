import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from typing import TYPE_CHECKING, List, Optional, Sequence

from .base import ApplicationError, BaseRepoAnalyzer, Pathish
from .weburl import WebURL

if TYPE_CHECKING:
    from typing import Final


class NoRemoteError(ApplicationError):
    def __init__(self, branch: str):
        self.branch: "Final[str]" = branch

    def __str__(self) -> str:
        return f"Branch `{self.branch}` does not have remote."


class GitRepoAnalyzer(BaseRepoAnalyzer):
    @classmethod
    def from_path(cls, path: Pathish) -> "GitRepoAnalyzer":
        cwd = Path(path)
        if not cwd.is_dir():
            cwd = cwd.parent
        return cls(cwd=cwd)

    def __init__(self, cwd: Pathish):
        self.cwd: "Final[Path]" = Path(cwd)
        self.root: "Final[Path]" = Path(
            self.git("rev-parse", "--show-toplevel").stdout.strip()
        )

    def run(self, *args: str, **options) -> CompletedProcess:
        kwargs = dict(
            cwd=str(self.cwd),
            check=True,
            # capture_output=True
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # text=True
            universal_newlines=True,
        )
        kwargs.update(options)
        return subprocess.run(args, **kwargs)  # type: ignore

    def git(self, *args: str, **options) -> CompletedProcess:
        return self.run("git", *args, **options)

    def git_config(self, config: str) -> str:
        return self.git("config", "--get", config).stdout.rstrip()

    def try_git_config(self, config: str) -> Optional[str]:
        try:
            return self.git_config(config)
        except subprocess.CalledProcessError:
            return None

    def resolve_revision(self, revision: str) -> str:
        return self.git("rev-parse", "--verify", revision).stdout.strip()

    @staticmethod
    def choose_url(url_list: Sequence[str]) -> str:
        for host in ["gitlab", "github", "bitbucket"]:
            for url in url_list:
                if host in url:
                    return url
        return url_list[0]

    def remote_of_branch(self, branch: str) -> Optional[str]:
        return (
            self.try_git_config(f"branch.{branch}.remote")
            or self.try_git_config(f"branch.{branch}.pushRemote")
            or self.try_git_config("remote.pushDefault")
        )

    def remote_all_urls(self, branch: str = "master") -> List[str]:
        remote: str = self.remote_of_branch(branch) or "origin"
        try:
            return self.git(
                "config", "--get-all", f"remote.{remote}.url"
            ).stdout.splitlines()
        except subprocess.CalledProcessError:
            raise NoRemoteError(branch)

    def remote_url(self, branch: str = "master") -> str:
        return self.choose_url(self.remote_all_urls(branch))

    def remote_branch(self, branch: str) -> str:
        ref = self.try_git_config(f"branch.{branch}.merge")
        if not ref:
            return branch  # assuming `pushRemote`
        assert ref.startswith("refs/heads/")
        return ref[len("refs/heads/") :]

    def current_branch(self) -> str:
        return self.git("rev-parse", "--abbrev-ref", "HEAD").stdout.rstrip()

    def need_pull_request(self, branch: str) -> bool:
        return not (branch == "master" or self.remote_of_branch(branch) == "origin")

    def relpath(self, path: Pathish) -> Path:
        relpath = Path(path).resolve().relative_to(self.root)
        assert not str(relpath).startswith("..")
        return relpath


class LocalBranch:
    repo: BaseRepoAnalyzer
    name: str

    def __init__(self, repo: BaseRepoAnalyzer, name: Optional[str] = None):
        self.repo = repo
        if name is None:
            name = repo.current_branch()
        self.name = name

    def remote_url(self) -> str:
        return self.repo.remote_url(branch=self.name)

    def remote_branch(self) -> str:
        return self.repo.remote_branch(branch=self.name)

    def need_pull_request(self) -> bool:
        return self.repo.need_pull_request(self.name)

    def weburl(self) -> WebURL:
        return WebURL(self)


def is_supported_url(url: str) -> bool:
    # TODO: improve!
    for host in ["gitlab", "github", "bitbucket"]:
        if host in url:
            return True
    return False


def choose_local_branch(
    repo: BaseRepoAnalyzer, branch: Optional[str] = None
) -> LocalBranch:

    if branch is not None:
        return LocalBranch(repo, name=branch)

    branch = repo.current_branch()
    if is_supported_url(repo.remote_url(branch=branch)):
        return LocalBranch(repo, name=branch)

    return LocalBranch(repo, name="master")
