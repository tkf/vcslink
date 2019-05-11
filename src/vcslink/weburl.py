import re
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple, Union

if TYPE_CHECKING:
    from .base import BaseRepoAnalyzer
    from .git import LocalBranch

Pathish = Union[str, Path]


def rooturl(url):
    """
    Turn Git `url` to something web browsers recognize.

    >>> rooturl("git@github.com:group/project.git")
    'https://github.com/group/project'
    >>> rooturl("git@gitlab.com:group/project.git")
    'https://gitlab.com/group/project'
    >>> rooturl("git@bitbucket.org:group/project.git")
    'https://bitbucket.org/group/project'
    >>> rooturl("ssh://git@bitbucket.org/group/project.git")
    'https://bitbucket.org/group/project'

    >>> rooturl("git@gitlab.com:group/project.wiki.git")
    'https://gitlab.com/group/project/wikis'
    """
    return _specialurl(_rooturl(url))


def _rooturl(url):
    match = re.match(r"^https?://(.*?)(.git)?$", url)
    if match:
        return f"https://{match.group(1)}"
    if "@" not in url:
        raise ValueError(f"Unsupported URL: {url}")
    _, web = url.split("@", 1)
    if ":" in web:
        host, path = web.split(":", 1)
    elif "/" in web:
        host, path = web.split("/", 1)
    else:
        raise ValueError(f"Unsupported URL: {url}")
    if path.endswith(".git"):
        path = path[: -len(".git")]
    return f"https://{host}/{path}"


def _specialurl(url):
    host, path = url.split("://", 1)[1].split("/", 1)
    if "gitlab" in host and path.endswith(".wiki"):
        return f"https://{host}/{path[:-len('.wiki')]}/wikis"
    return url


LinesSpecifier = Union[None, int, Tuple[int, int]]


def parselines(lines: Optional[str]) -> LinesSpecifier:
    if not lines:
        return None
    if "-" in lines:
        beg, end = lines.split("-")
        return (int(beg), int(end))
    else:
        return int(lines)


class WebURL:
    local_branch: "LocalBranch"
    repo: "BaseRepoAnalyzer"
    rooturl: str

    def __init__(self, local_branch: "LocalBranch"):
        self.local_branch = local_branch
        self.repo = local_branch.repo
        self.rooturl = rooturl(local_branch.remote_url())

    def is_bitbucket(self):
        return "//bitbucket.org" in self.rooturl

    def is_gitlab(self):
        return "//gitlab.com" in self.rooturl

    def is_github(self):
        return "//github.com" in self.rooturl

    def pull_request(self):
        branch = self.local_branch.name
        if self.is_github():
            # https://github.com/{user}/{repo}/pull/new/{branch}
            return self.rooturl + "/pull/new/" + branch
        raise NotImplementedError

    def commit(self, revision: str) -> str:
        revision = self.repo.resolve_revision(revision)
        if self.is_bitbucket():
            return f"{self.rooturl}/commits/{revision}"
        else:
            return f"{self.rooturl}/commit/{revision}"

    def log(self, branch: Optional[str] = None) -> str:
        if not branch:
            branch = self.local_branch.name
        if self.is_bitbucket():
            return f"{self.rooturl}/commits/branch/{branch}"
        else:
            return f"{self.rooturl}/commits/{branch}"

    def _format_lines(self, lines: LinesSpecifier) -> str:
        if not lines:
            return ""

        nums: Union[Tuple[int], Tuple[int, int]] = lines if isinstance(
            lines, tuple
        ) else (lines,)

        if self.is_bitbucket():
            fragment = "lines-" + ":".join(map(str, nums))
        elif self.is_gitlab():
            fragment = "L" + "-".join(map(str, nums))
        else:
            # github.com
            fragment = "-".join(f"L{x}" for x in nums)

        return f"#{fragment}"

    def file(
        self,
        file: Pathish,
        lines: LinesSpecifier = None,
        revision: str = "master",
        permalink: Optional[bool] = None,
    ) -> str:
        """
        Get an URL to file.

        ..
           >>> from vcslink.testing import dummy_weburl
           >>> weburl = dummy_weburl()

        >>> weburl.file("README.md")
        'https://github.com/USER/PROJECT/blob/master/README.md'
        >>> weburl.file("README.md", permalink=True)
        'https://github.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md'
        >>> weburl.file("README.md", lines=1)
        'https://github.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md#L1'
        >>> weburl.file("README.md", lines=(1, 2))
        'https://github.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md#L1-L2'
        >>> weburl.file("README.md", lines=(1, 2), permalink=False)
        'https://github.com/USER/PROJECT/blob/master/README.md#L1-L2'
        """
        if permalink is None:
            permalink = lines is not None
        if permalink:
            revision = self.repo.resolve_revision(revision)
        else:
            revision = "master"
        relurl = "/".join(self.repo.relpath(file).parts)
        fragment = self._format_lines(lines)
        if self.is_bitbucket():
            return f"{self.rooturl}/src/{revision}/{relurl}{fragment}"
        else:
            return f"{self.rooturl}/blob/{revision}/{relurl}{fragment}"
