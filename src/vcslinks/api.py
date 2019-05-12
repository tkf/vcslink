from typing import Optional

from .git import GitRepoAnalyzer, Pathish, choose_local_branch
from .weburl import LinesSpecifier, WebURL


def analyze(path: Pathish = ".", **kwargs) -> WebURL:
    """
    Analyze a Git repository and return a `WebURL` instance.

    Argument `path` can point to any file or directory inside the Git
    repository to be analyzed.  The root of the Git repository is
    found automatically by the ``git`` command.

    ..
       >>> from vcslinks.testing import dummy_github_weburl
       >>> weburl = dummy_github_weburl()

    >>> weburl = analyze()                                 # doctest: +SKIP
    >>> weburl.rooturl
    'https://github.com/USER/PROJECT'
    >>> weburl.commit("master")
    'https://github.com/USER/PROJECT/commit/55150afe539493d650889224db136bc8d9b7ecb8'
    >>> weburl.file("README.md")
    'https://github.com/USER/PROJECT/blob/master/README.md'
    >>> weburl.log()
    'https://github.com/USER/PROJECT/commits/master'
    >>> weburl.pull_request()
    'https://github.com/USER/PROJECT/pull/new/master'
    """
    repo = GitRepoAnalyzer.from_path(path)
    local_branch = choose_local_branch(repo, **kwargs)
    return local_branch.weburl()


def root(*, path: Pathish = ".", **kwargs) -> str:
    """
    Get a URL to GitHub/GitLab/Bitbucket.

    ..
       >>> getfixture("patch_analyze")

    **GitHub**

    >>> import vcslinks
    >>> vcslinks.root()
    'https://github.com/USER/PROJECT'

    **GitLab**

    >>> vcslinks.root(path="path/to/gitlab/clone")
    'https://gitlab.com/USER/PROJECT'

    **Bitbucket**

    >>> vcslinks.root(path="path/to/bitbucket/clone")
    'https://bitbucket.org/USER/PROJECT'
    """
    return analyze(path, **kwargs).rooturl


def pull_request(path: Pathish = ".", **kwargs) -> str:
    """
    Get a URL to the web page for submitting a PR.

    ..
       >>> getfixture("patch_analyze")

    **GitHub**

    >>> import vcslinks
    >>> vcslinks.pull_request()
    'https://github.com/USER/PROJECT/pull/new/master'

    **GitLab**

    >>> vcslinks.pull_request(path="path/to/gitlab/clone")
    'https://gitlab.com/USER/PROJECT/merge_requests/new?merge_request%5Bsource_branch%5D=master'

    **Bitbucket**

    >>> vcslinks.pull_request(path="path/to/bitbucket/clone")
    'https://bitbucket.org/USER/PROJECT/pull-requests/new?source=master'
    """
    return analyze(path, **kwargs).pull_request()


def commit(revision: str = "HEAD", *, path: Pathish = ".", **kwargs) -> str:
    """
    Get a URL to commit page.

    ..
       >>> getfixture("patch_analyze")

    **GitHub**

    >>> import vcslinks
    >>> vcslinks.commit()
    'https://github.com/USER/PROJECT/commit/55150afe539493d650889224db136bc8d9b7ecb8'
    >>> vcslinks.commit("dev")
    'https://github.com/USER/PROJECT/commit/40539486fdaf08a39b57519eb06e0e200c932cfd'

    **GitLab**

    >>> vcslinks.commit(path="path/to/gitlab/clone")
    'https://gitlab.com/USER/PROJECT/commit/55150afe539493d650889224db136bc8d9b7ecb8'

    **Bitbucket**

    >>> vcslinks.commit(path="path/to/bitbucket/clone")
    'https://bitbucket.org/USER/PROJECT/commits/55150afe539493d650889224db136bc8d9b7ecb8'
    """
    return analyze(path, **kwargs).commit(revision)


def log(branch: Optional[str] = None, *, path: Pathish = ".", **kwargs) -> str:
    """
    Get a URL to history page.

    ..
       >>> getfixture("patch_analyze")

    **GitHub**

    >>> import vcslinks
    >>> vcslinks.log()
    'https://github.com/USER/PROJECT/commits/master'
    >>> vcslinks.log("dev")
    'https://github.com/USER/PROJECT/commits/dev'

    **GitLab**

    >>> vcslinks.log(path="path/to/gitlab/clone/")
    'https://gitlab.com/USER/PROJECT/commits/master'

    **Bitbucket**

    >>> vcslinks.log(path="path/to/bitbucket/clone/")
    'https://bitbucket.org/USER/PROJECT/commits/branch/master'
    """
    return analyze(path, **kwargs).log(branch)


def file(
    file: Pathish,
    lines: LinesSpecifier = None,
    revision: str = "master",
    permalink: Optional[bool] = None,
    **kwargs,
) -> str:
    """
    Get a URL to file.

    ..
       >>> getfixture("patch_analyze")

    **GitHub**

    >>> import vcslinks
    >>> vcslinks.file("README.md")
    'https://github.com/USER/PROJECT/blob/master/README.md'
    >>> vcslinks.file("README.md")
    'https://github.com/USER/PROJECT/blob/master/README.md'
    >>> vcslinks.file("README.md", permalink=True)
    'https://github.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md'
    >>> vcslinks.file("README.md", lines=1)
    'https://github.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md#L1'
    >>> vcslinks.file("README.md", lines=(1, 2))
    'https://github.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md#L1-L2'
    >>> vcslinks.file("README.md", lines=(1, 2), permalink=False)
    'https://github.com/USER/PROJECT/blob/master/README.md#L1-L2'

    **GitLab**

    >>> vcslinks.file("path/to/gitlab/clone/README.md")
    'https://gitlab.com/USER/PROJECT/blob/master/README.md'
    >>> vcslinks.file("path/to/gitlab/clone/README.md", lines=1)
    'https://gitlab.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md#L1'
    >>> vcslinks.file("path/to/gitlab/clone/README.md", lines=(1, 2))
    'https://gitlab.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/README.md#L1-2'

    **Bitbucket**

    >>> vcslinks.file("path/to/bitbucket/clone/README.md")
    'https://bitbucket.org/USER/PROJECT/src/master/README.md'
    >>> vcslinks.file("path/to/bitbucket/clone/README.md", lines=1)
    'https://bitbucket.org/USER/PROJECT/src/55150afe539493d650889224db136bc8d9b7ecb8/README.md#lines-1'
    >>> vcslinks.file("path/to/bitbucket/clone/README.md", lines=(1, 2))
    'https://bitbucket.org/USER/PROJECT/src/55150afe539493d650889224db136bc8d9b7ecb8/README.md#lines-1:2'

    """
    return analyze(file, **kwargs).file(
        file, lines=lines, revision=revision, permalink=permalink
    )


def diff(
    revision1: Optional[str] = None,
    revision2: Optional[str] = None,
    permalink: bool = False,
    path: Pathish = ".",
    **kwargs,
) -> str:
    """
    Get a URL to diff page.

    ..
       >>> getfixture("patch_analyze")

    **GitHub**

    >>> import vcslinks
    >>> vcslinks.diff("dev")
    'https://github.com/USER/PROJECT/compare/master...dev'
    >>> vcslinks.diff(permalink=True)
    'https://github.com/USER/PROJECT/compare/master...55150afe539493d650889224db136bc8d9b7ecb8'
    >>> vcslinks.diff("master", "dev", permalink=True) == (
    ...     'https://github.com/USER/PROJECT/compare/'
    ...     '55150afe539493d650889224db136bc8d9b7ecb8'
    ...     '...'
    ...     '40539486fdaf08a39b57519eb06e0e200c932cfd'
    ... )
    True

    **GitLab**

    >>> vcslinks.diff("dev", path="path/to/gitlab/clone/")
    'https://gitlab.com/USER/PROJECT/compare/master...dev'

    **Bitbucket**

    >>> vcslinks.diff("dev", path="path/to/bitbucket/clone/")
    'https://bitbucket.org/USER/PROJECT/branches/compare/dev%0Dmaster#diff'
    """
    return analyze(path, **kwargs).diff(
        revision1=revision1, revision2=revision2, permalink=permalink
    )


def blame(
    file: Pathish,
    lines: LinesSpecifier = None,
    revision: str = "master",
    permalink: Optional[bool] = None,
    **kwargs,
) -> str:
    """
    Get a URL to blame/annotate page.

    ..
       >>> getfixture("patch_analyze")

    **GitHub**

    >>> import vcslinks
    >>> vcslinks.blame("README.md")
    'https://github.com/USER/PROJECT/blame/master/README.md'

    **GitLab**

    >>> vcslinks.blame("path/to/gitlab/clone/README.md")
    'https://gitlab.com/USER/PROJECT/blame/master/README.md'

    **Bitbucket**

    >>> vcslinks.blame("path/to/bitbucket/clone/README.md")
    'https://bitbucket.org/USER/PROJECT/annotate/master/README.md'
    """
    return analyze(file, **kwargs).blame(
        file, lines=lines, revision=revision, permalink=permalink
    )
