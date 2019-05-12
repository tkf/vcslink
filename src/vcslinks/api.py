from .git import GitRepoAnalyzer, Pathish, choose_local_branch
from .weburl import WebURL


def analyze(path: Pathish = ".", **kwargs) -> WebURL:
    """
    Analyze a Git repository and return a `WebURL` instance.

    Argument `path` can point to any file or directory inside the Git
    repository to be analyzed.  The root of the Git repository is
    found automatically by the ``git`` command.

    ..
       >>> from vcslinks.testing import dummy_weburl
       >>> weburl = dummy_weburl()

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
