from pathlib import Path


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
    """
    return _specialurl(_rooturl(url))


def _rooturl(url):
    if url.startswith("http"):
        if url.endswith(".git"):
            return url[: -len(".git")]
        return url
    if "@" not in url:
        raise ValueError(f"Unsupported URL: {url}")
    _, web = url.split("@", 1)
    if ":" in web:
        host, path = web.split(":", 1)
    elif "/" in web:
        host, path = web.split("/", 1)
    else:
        raise ValueError(f"Unsupported URL: {url}")
    if path.endswith(".git"):
        path = path[: -len(".git")]
    return f"https://{host}/{path}"


def _specialurl(url):
    host, path = url.split("://", 1)[1].split("/", 1)
    if "gitlab" in host and path.endswith(".wiki"):
        return f"https://{host}/{path[:-len('.wiki')]}/wikis"
    return url


class WebURL:
    def __init__(self, local_branch):
        self.local_branch = local_branch
        self.repo = local_branch.repo
        self.rooturl = rooturl(local_branch.remote_url())

    def is_bitbucket(self):
        return "//bitbucket.org" in self.rooturl

    def is_gitlab(self):
        return "//gitlab.com" in self.rooturl

    def is_github(self):
        return "//github.com" in self.rooturl

    def pr(self):
        branch = self.local_branch.name
        if self.is_github():
            # https://github.com/{user}/{repo}/pull/new/{branch}
            return self.rooturl + "/pull/new/" + branch
        raise NotImplementedError

    def commit(self, revision):
        revision = self.repo.git_revision(revision)
        if self.is_bitbucket():
            return f"{self.rooturl}/commits/{revision}"
        else:
            return f"{self.rooturl}/commit/{revision}"

    def log(self, branch=None):
        if not branch:
            branch = self.local_branch.name
        if self.is_bitbucket():
            return f"{self.rooturl}/commits/branch/{branch}"
        else:
            return f"{self.rooturl}/commits/{branch}"

    def _format_lines(self, lines):
        if not lines:
            return ""

        if self.is_bitbucket():
            fragment = "lines-" + ":".join(lines.split("-"))
        elif self.is_gitlab():
            fragment = f"L{lines}"
        else:
            # github.com
            fragment = "-".join(f"L{x}" for x in lines.split("-"))

        return f"#{fragment}"

    def file(self, file, lines=None, revision="master"):
        path = Path(file)
        relpath = path.absolute().relative_to(self.repo.root)
        assert not str(relpath).startswith("..")
        relurl = "/".join(relpath.parts)
        fragment = self._format_lines(lines)
        if self.is_bitbucket():
            return f"{self.rooturl}/src/{revision}/{relurl}{fragment}"
        else:
            return f"{self.rooturl}/blob/{revision}/{relurl}{fragment}"
