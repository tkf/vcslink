import os
from contextlib import contextmanager
from subprocess import run

import pytest  # type: ignore

from .testing import dummy_bitbucket_repo, dummy_github_repo, dummy_gitlab_repo


@contextmanager
def chdir(path):
    orig_cwd = os.getcwd()
    try:
        os.chdir(str(path))
        yield path
    finally:
        os.chdir(orig_cwd)


def dummy_file_content(fmt, nlines):
    return "\n".join(fmt.format(n=i + 1) for i in range(nlines))


@pytest.fixture(scope="session")
def prepare_github_repository(tmp_path_factory):
    path = tmp_path_factory.mktemp("vcslinks-github")

    def git(*args, **kwargs):
        cmd = [
            "git",
            "-c",
            "user.email=dummy@vcslinks",
            "-c",
            "user.name=Dummy VCS Links Tester",
        ]
        cmd.extend(args)
        return run(cmd, check=True, cwd=str(path), **kwargs)

    git("init")
    git("remote", "add", "origin", "http://github.com/USER/PROJECT")
    (path / "README.md").write_text(dummy_file_content("README.md: line {n}", 5))
    git("add", "README.md")
    git("commit", "--message", "Add README.md")
    git("config", "branch.master.remote", "origin")
    git("config", "branch.master.merge", "refs/heads/master")

    return path


@pytest.fixture
def github_repository(prepare_github_repository):
    with chdir(prepare_github_repository) as path:
        yield path


@pytest.fixture
def patch_analyze():
    from . import api

    GitRepoAnalyzer = api.GitRepoAnalyzer

    class FakeGitRepoAnalyzer:
        @classmethod
        def from_path(cls, path):
            if "/gitlab/" in path:
                return dummy_gitlab_repo()
            elif "/bitbucket/" in path:
                return dummy_bitbucket_repo()
            else:
                return dummy_github_repo()

    try:
        api.GitRepoAnalyzer = FakeGitRepoAnalyzer
        yield
    finally:
        api.GitRepoAnalyzer = GitRepoAnalyzer
