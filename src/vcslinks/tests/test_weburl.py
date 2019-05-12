import re

import pytest  # type: ignore

from ..api import analyze
from ..git import LocalBranch
from ..testing import DummyRepoAnalyzer, dummy_bitbucket_weburl, dummy_gitlab_weburl
from ..weburl import UnsupportedURLError, rooturl

SHA_RE_STR = "(?:[a-z0-9]{40})"


def test_file(github_repository):
    weburl = analyze()
    rooturl = "https://github.com/USER/PROJECT"
    assert weburl.rooturl == rooturl

    url = weburl.file("README.md")
    assert url == f"{rooturl}/blob/master/README.md"

    url = weburl.file("README.md", permalink=True)
    assert re.match(f"^{rooturl}/blob/{SHA_RE_STR}/README.md$", url)

    url = weburl.file("README.md", lines=1)
    assert re.match(f"^{rooturl}/blob/{SHA_RE_STR}/README.md#L1$", url)

    url = weburl.file("README.md", lines=(1, 2))
    assert re.match(f"^{rooturl}/blob/{SHA_RE_STR}/README.md#L1-L2$", url)

    url = weburl.file("README.md", lines=(1, 2), permalink=False)
    assert url == f"{rooturl}/blob/master/README.md#L1-L2"


@pytest.mark.parametrize(
    "git_url",
    [
        "git@github.com:USER/PROJECT.git",
        "https://github.com/USER/PROJECT.git",
        "https://github.com/USER/PROJECT",
        "http://github.com/USER/PROJECT.git",
        "http://github.com/USER/PROJECT",
    ],
)
def test_github_url_variants(git_url):
    repo = DummyRepoAnalyzer()
    repo.mock.remote_url.return_value = git_url
    weburl = LocalBranch(repo).weburl()
    assert weburl.rooturl == "https://github.com/USER/PROJECT"


def test_gitlab_file():
    weburl = dummy_gitlab_weburl()
    rooturl = "https://gitlab.com/USER/PROJECT"
    assert weburl.rooturl == rooturl

    url = weburl.file("README.md")
    assert url == f"{rooturl}/blob/master/README.md"

    url = weburl.file("README.md", permalink=True)
    assert re.match(f"^{rooturl}/blob/{SHA_RE_STR}/README.md$", url)

    url = weburl.file("README.md", lines=1)
    assert re.match(f"^{rooturl}/blob/{SHA_RE_STR}/README.md#L1$", url)

    url = weburl.file("README.md", lines=(1, 2))
    assert re.match(f"^{rooturl}/blob/{SHA_RE_STR}/README.md#L1-2$", url)

    url = weburl.file("README.md", lines=(1, 2), permalink=False)
    assert url == f"{rooturl}/blob/master/README.md#L1-2"


def test_bitbucket_file():
    weburl = dummy_bitbucket_weburl()
    rooturl = "https://bitbucket.org/USER/PROJECT"
    assert weburl.rooturl == rooturl

    url = weburl.file("README.md")
    assert url == f"{rooturl}/src/master/README.md"

    url = weburl.file("README.md", permalink=True)
    assert re.match(f"^{rooturl}/src/{SHA_RE_STR}/README.md$", url)

    url = weburl.file("README.md", lines=1)
    assert re.match(f"^{rooturl}/src/{SHA_RE_STR}/README.md#lines-1$", url)

    url = weburl.file("README.md", lines=(1, 2))
    assert re.match(f"^{rooturl}/src/{SHA_RE_STR}/README.md#lines-1:2$", url)

    url = weburl.file("README.md", lines=(1, 2), permalink=False)
    assert url == f"{rooturl}/src/master/README.md#lines-1:2"


@pytest.mark.parametrize(
    "git_url",
    [
        # List of links that would throw UnsupportedURLError:
        "unsupported.host",
        "unsupported.host:some/remote/path",
        "git@host",
    ],
)
def test_unsupported_rooturl(git_url):
    with pytest.raises(UnsupportedURLError) as exc_info:
        rooturl(git_url)
    assert exc_info.value.url == git_url
