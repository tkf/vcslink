import re

import pytest  # type: ignore

from ..api import analyze
from ..git import LocalBranch
from ..testing import DummyRepoAnalyzer

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
