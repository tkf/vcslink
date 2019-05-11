from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

Pathish = Union[str, Path]


class BaseRepoAnalyzer(ABC):
    @abstractmethod
    def current_branch(self):
        ...

    @abstractmethod
    def remote_url(self, branch: str = "master") -> str:
        ...

    @abstractmethod
    def remote_branch(self, branch: str) -> str:
        ...

    @abstractmethod
    def need_pull_request(self, branch: str) -> bool:
        ...

    @abstractmethod
    def resolve_revision(self, revision: str) -> str:
        ...

    @abstractmethod
    def relpath(self, path: Pathish) -> Path:
        ...
