import re

from ..api import analyze

SHA_RE_STR = "(?:[a-z0-9]{40})"


def test_file(github_repository):
    weburl = analyze()
    rooturl = "http://github.com/USER/PROJECT"
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
