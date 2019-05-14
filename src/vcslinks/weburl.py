import re
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple, Union

if TYPE_CHECKING:
    from .base import BaseRepoAnalyzer
    from .git import LocalBranch

Pathish = Union[str, Path]


class UnsupportedURLError(ValueError):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return f"Unsupported URL: {self.url}"


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

    >>> rooturl("unsupported.host:some/remote/path")
    Traceback (most recent call last):
      ...
    vcslinks...UnsupportedURLError: Unsupported URL: unsupported.host:some/remote/path
    """
    return _specialurl(_rooturl(url))


def _rooturl(url):
    match = re.match(r"^https?://(.*?)(.git)?$", url)
    if match:
        return f"https://{match.group(1)}"
    if "@" not in url:
        raise UnsupportedURLError(url)
    _, web = url.split("@", 1)
    if ":" in web:
        host, path = web.split(":", 1)
    elif "/" in web:
        host, path = web.split("/", 1)
    else:
        raise UnsupportedURLError(url)
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
    """
    Parse `lines` argument from the CLI.

    >>> parselines(None) is None
    True
    >>> parselines("1")
    1
    >>> parselines("1-2")
    (1, 2)
    """
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
        """
        Get a URL to the web page for submitting a PR.

        ..
           >>> from vcslinks import testing
           >>> weburl_github = testing.dummy_github_weburl()
           >>> weburl_gitlab = testing.dummy_gitlab_weburl()
           >>> weburl_bitbucket = testing.dummy_bitbucket_weburl()

        >>> weburl_github.pull_request()
        'https://github.com/USER/PROJECT/pull/new/master'
        >>> weburl_gitlab.pull_request()
        'https://gitlab.com/USER/PROJECT/merge_requests/new?merge_request%5Bsource_branch%5D=master'
        >>> weburl_bitbucket.pull_request()
        'https://bitbucket.org/USER/PROJECT/pull-requests/new?source=master'
        """
        branch = self.local_branch.remote_branch()
        if self.is_github():
            # https://github.com/{user}/{repo}/pull/new/{branch}
            return self.rooturl + "/pull/new/" + branch
        elif self.is_gitlab():
            # https://gitlab.com/{user}/{repo}/merge_requests/new?merge_request%5Bsource_branch%5D={dev}
            return (
                self.rooturl
                + "/merge_requests/new?merge_request%5Bsource_branch%5D="
                + branch
            )
        elif self.is_bitbucket():
            # https://bitbucket.org/{user}/{repo}/pull-requests/new?source={branch}
            return self.rooturl + "/pull-requests/new?source=" + branch

    def commit(self, revision: str) -> str:
        """
        Get a URL to commit page.

        ..
           >>> from vcslinks.testing import dummy_github_weburl
           >>> weburl = dummy_github_weburl()

        >>> weburl.commit("master")
        'https://github.com/USER/PROJECT/commit/55150afe539493d650889224db136bc8d9b7ecb8'
        """
        revision = self.repo.resolve_revision(revision)
        if self.is_bitbucket():
            return f"{self.rooturl}/commits/{revision}"
        else:
            return f"{self.rooturl}/commit/{revision}"

    def log(self, branch: Optional[str] = None) -> str:
        """
        Get a URL to history page.

        ..
           >>> from vcslinks import testing
           >>> weburl_github = testing.dummy_github_weburl()
           >>> weburl_gitlab = testing.dummy_gitlab_weburl()
           >>> weburl_bitbucket = testing.dummy_bitbucket_weburl()

        >>> weburl_github.log()
        'https://github.com/USER/PROJECT/commits/master'
        >>> weburl_gitlab.log()
        'https://gitlab.com/USER/PROJECT/commits/master'
        >>> weburl_bitbucket.log()
        'https://bitbucket.org/USER/PROJECT/commits/branch/master'

        >>> weburl_github.log("dev")
        'https://github.com/USER/PROJECT/commits/dev'
        """
        if not branch:
            branch = self.local_branch.remote_branch()
        if self.is_bitbucket():
            return f"{self.rooturl}/commits/branch/{branch}"
        else:
            return f"{self.rooturl}/commits/{branch}"

    def _format_lines(
        self, lines: LinesSpecifier, bitbucket_prefix: str = "lines"
    ) -> str:
        if not lines:
            return ""

        nums: Union[Tuple[int], Tuple[int, int]] = lines if isinstance(
            lines, tuple
        ) else (lines,)

        if self.is_bitbucket():
            fragment = bitbucket_prefix + "-" + ":".join(map(str, nums))
        elif self.is_gitlab():
            fragment = "L" + "-".join(map(str, nums))
        else:
            # github.com
            fragment = "-".join(f"L{x}" for x in nums)

        return f"#{fragment}"

    def _remote_revision(self, revision: Optional[str], permalink: bool) -> str:
        if permalink:
            return self.repo.resolve_revision(revision or self.local_branch.name)
        elif not revision:
            # Now that we know that `revision` is not required to be
            # resolved, we can safely return (unqualified) remote
            # branch name:
            return self.local_branch.remote_branch()
        return revision

    def _file_revision(
        self, lines: LinesSpecifier, revision: Optional[str], permalink: Optional[bool]
    ) -> str:
        if permalink is None:
            permalink = lines is not None
        return self._remote_revision(revision, permalink)

    def file(
        self,
        file: Pathish,
        lines: LinesSpecifier = None,
        revision: Optional[str] = None,
        permalink: Optional[bool] = None,
    ) -> str:
        """
        Get a URL to file.

        **GitHub**

        ..
           >>> from vcslinks import testing
           >>> weburl = testing.dummy_github_weburl()

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

        **GitLab**

        ..
           >>> weburl = testing.dummy_gitlab_weburl()

        >>> weburl.file("README.md", lines=1)
        'https://gitlab.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md#L1'
        >>> weburl.file("README.md", lines=(1, 2))
        'https://gitlab.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md#L1-2'

        **Bitbucket**

        ..
           >>> weburl = testing.dummy_bitbucket_weburl()

        >>> weburl.file("README.md")
        'https://bitbucket.org/USER/PROJECT/src/master/README.md'
        >>> weburl.file("README.md", lines=1)
        'https://bitbucket.org/USER/PROJECT/src/55150afe539493d650889224db136bc8d9b7ecb8/README.md#lines-1'
        >>> weburl.file("README.md", lines=(1, 2))
        'https://bitbucket.org/USER/PROJECT/src/55150afe539493d650889224db136bc8d9b7ecb8/README.md#lines-1:2'
        """
        revision = self._file_revision(lines, revision, permalink)
        relurl = "/".join(self.repo.relpath(file).parts)
        fragment = self._format_lines(lines)
        if self.is_bitbucket():
            return f"{self.rooturl}/src/{revision}/{relurl}{fragment}"
        else:
            return f"{self.rooturl}/blob/{revision}/{relurl}{fragment}"

    def tree(
        self,
        directory: Optional[Pathish] = None,
        revision: Optional[str] = None,
        permalink: bool = False,
    ):
        """
        Get a URL to tree page.
        """
        revision = self._remote_revision(revision, permalink)
        if self.is_bitbucket():
            baseurl = f"{self.rooturl}/src/{revision}"
        else:
            baseurl = f"{self.rooturl}/tree/{revision}"
        if not directory:
            return baseurl
        relurl = "/".join(self.repo.relpath(directory).parts)
        return f"{baseurl}/{relurl}"

    def diff(
        self,
        revision1: Optional[str] = None,
        revision2: Optional[str] = None,
        permalink: bool = False,
    ) -> str:
        """
        Get a URL to diff page.

        **GitHub**

        ..
           >>> from vcslinks import testing
           >>> weburl = testing.dummy_github_weburl()

        >>> weburl.diff("dev")
        'https://github.com/USER/PROJECT/compare/master...dev'
        >>> weburl.diff(permalink=True)
        'https://github.com/USER/PROJECT/compare/master...55150afe539493d650889224db136bc8d9b7ecb8'
        >>> weburl.diff("master", "dev", permalink=True) == (
        ...     'https://github.com/USER/PROJECT/compare/'
        ...     '55150afe539493d650889224db136bc8d9b7ecb8'
        ...     '...'
        ...     '40539486fdaf08a39b57519eb06e0e200c932cfd'
        ... )
        True

        **GitLab**

        ..
           >>> weburl = testing.dummy_gitlab_weburl()

        >>> weburl.diff("dev")
        'https://gitlab.com/USER/PROJECT/compare/master...dev'

        **Bitbucket**

        ..
           >>> weburl = testing.dummy_bitbucket_weburl()

        >>> weburl.diff("dev")
        'https://bitbucket.org/USER/PROJECT/branches/compare/dev%0Dmaster#diff'
        """
        if not revision1:
            revision1 = self.local_branch.remote_branch()
        if permalink:
            revision1 = self.repo.resolve_revision(revision1)
            if revision2:
                revision2 = self.repo.resolve_revision(revision2)
        if not revision2:
            revision2 = revision1
            revision1 = "master"
        rooturl = self.rooturl
        if self.is_bitbucket():
            return f"{rooturl}/branches/compare/{revision2}%0D{revision1}#diff"
        else:
            return f"{rooturl}/compare/{revision1}...{revision2}"

    def blame(
        self,
        file: Pathish,
        lines: LinesSpecifier = None,
        revision: Optional[str] = None,
        permalink: Optional[bool] = None,
    ) -> str:
        """
        Get a URL to blame/annotate page.

        **GitHub**

        ..
           >>> from vcslinks import testing
           >>> weburl = testing.dummy_github_weburl()

        >>> weburl.blame("README.md")
        'https://github.com/USER/PROJECT/blame/master/README.md'

        **GitLab**

        ..
           >>> weburl = testing.dummy_gitlab_weburl()

        >>> weburl.blame("README.md")
        'https://gitlab.com/USER/PROJECT/blame/master/README.md'

        **Bitbucket**

        ..
           >>> weburl = testing.dummy_bitbucket_weburl()

        >>> weburl.blame("README.md")
        'https://bitbucket.org/USER/PROJECT/annotate/master/README.md'
        """
        revision = self._file_revision(lines, revision, permalink)
        relurl = "/".join(self.repo.relpath(file).parts)
        fragment = self._format_lines(lines, bitbucket_prefix=relurl)
        if self.is_bitbucket():
            return f"{self.rooturl}/annotate/{revision}/{relurl}{fragment}"
        else:
            return f"{self.rooturl}/blame/{revision}/{relurl}{fragment}"
