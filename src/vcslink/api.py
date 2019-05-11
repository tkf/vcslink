from .git import GitRepoAnalyzer
from .weburl import WebURL


def analyze(path, **kwargs) -> WebURL:
    return GitRepoAnalyzer.from_path(path).local_branch(**kwargs).weburl()
