from .git import GitRepoAnalyzer, Pathish, choose_local_branch
from .weburl import WebURL


def analyze(path: Pathish = ".", **kwargs) -> WebURL:
    repo = GitRepoAnalyzer.from_path(path)
    local_branch = choose_local_branch(repo, **kwargs)
    return local_branch.weburl()
