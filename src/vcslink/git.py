import subprocess
from pathlib import Path
from typing import Optional, Union

from .weburl import WebURL

Pathish = Union[str, Path]


class GitRepoAnalyzer:
    cwd: Path
    root: Path

    @classmethod
    def from_path(cls, path: Pathish) -> "GitRepoAnalyzer":
        cwd = Path(path)
        if not cwd.is_dir():
            cwd = cwd.parent
        return cls(cwd=cwd)

    def __init__(self, cwd):
        self.cwd = Path(cwd)
        self.root = Path(self.git("rev-parse", "--show-toplevel").stdout.strip())

    def run(self, *args, **options):
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
        return subprocess.run(args, **kwargs)

    def git(self, *args, **options):
        return self.run("git", *args, **options)

    def git_config(self, config):
        return self.git("config", "--get", config).stdout.rstrip()

    def git_revision(self, revision):
        return self.git("rev-parse", "--verify", revision).stdout.strip()

    @staticmethod
    def choose_url(url_list):
        for host in ["gitlab", "github", "bitbucket"]:
            for url in url_list:
                if host in url:
                    return url
        return url_list[0]

    def remote_all_urls(self, branch="master"):
        remote = self.git_config(f"branch.{branch}.remote")
        return self.git(
            "config", "--get-all", f"remote.{remote}.url"
        ).stdout.splitlines()

    def remote_url(self, **kwargs):
        return self.choose_url(self.remote_all_urls(**kwargs))

    def current_branch(self):
        return self.git("rev-parse", "--abbrev-ref", "HEAD").stdout.rstrip()

    def need_pr(self, branch):
        return not (
            branch == "master" and self.git_config(f"branch.master.remote") == "origin"
        )

    def local_branch(self, **kwargs):
        return LocalBranch(self, **kwargs)


class LocalBranch:
    repo: GitRepoAnalyzer
    name: str

    def __init__(self, repo: GitRepoAnalyzer, name: Optional[str] = None):
        self.repo = repo
        if name is None:
            name = repo.current_branch()
        self.name = name

    def remote_url(self) -> str:
        return self.repo.remote_url(branch=self.name)

    def need_pr(self) -> bool:
        return self.repo.need_pr(self.name)

    def weburl(self) -> WebURL:
        return WebURL(self)
