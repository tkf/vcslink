from .git import GitRepoAnalyzer, Pathish
from .weburl import WebURL


def analyze(path: Pathish, **kwargs) -> WebURL:
    return GitRepoAnalyzer.from_path(path).local_branch(**kwargs).weburl()
