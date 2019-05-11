import argparse
import shlex
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from typing import List

from .git import GitRepoAnalyzer


@dataclass
class Application:
    dry_run: bool
    browser: List[str]

    @classmethod
    def run(cls, dry_run, browser, func, **kwargs):
        browser_cmd = shlex.split(browser) if browser else []
        return func(cls(dry_run=dry_run, browser=browser_cmd), **kwargs)

    def open_url(self, url):
        if self.dry_run:
            print("Open:", url)
        elif self.browser:
            subprocess.check_call(self.browser + [url])
        else:
            webbrowser.open(url)


def cli_auto(app):
    repo = GitRepoAnalyzer.from_path(".")
    branch = repo.current_branch()
    if repo.need_pr(branch):
        url = repo.weburl.pr(branch)
    else:
        url = repo.weburl.root
    app.open_url(url)


def cli_commit(app, revision):
    repo = GitRepoAnalyzer.from_path(".")
    url = repo.weburl.commit(revision)
    app.open_url(url)


def cli_log(app, revision):
    repo = GitRepoAnalyzer.from_path(".")
    url = repo.weburl.log(revision)
    app.open_url(url)


def cli_file(app, **kwargs):
    repo = GitRepoAnalyzer.from_path(".")
    url = repo.weburl.file(**kwargs)
    app.open_url(url)


class CustomFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def make_parser(doc=__doc__):
    parser = argparse.ArgumentParser(
        formatter_class=CustomFormatter, description=__doc__
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--browser")

    subparsers = parser.add_subparsers()

    def subp(command, func):
        doc = func.__doc__
        title = None
        for title in filter(None, map(str.strip, (doc or "").splitlines())):
            break
        p = subparsers.add_parser(
            command, formatter_class=CustomFormatter, help=title, description=doc
        )
        p.set_defaults(func=func)
        return p

    p = subp("auto", cli_auto)

    p = subp("commit", cli_commit)
    p.add_argument("revision", nargs="?", default="HEAD")

    p = subp("log", cli_log)
    p.add_argument("revision", nargs="?", default="HEAD")

    p = subp("file", cli_file)
    p.add_argument("file")
    p.add_argument("lines", nargs="?")
    p.add_argument("revision", nargs="?", default="HEAD")

    parser.set_defaults(func=cli_auto)
    return parser


def print_outputs(proc):
    if proc.stdout:
        print("STDOUT:", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
    if proc.stderr:
        print("STDERR:", file=sys.stderr)
        print(proc.stderr, file=sys.stderr)


def main(args=None):
    parser = make_parser()
    ns = parser.parse_args(args)
    try:
        Application.run(**vars(ns))
    except subprocess.CalledProcessError as err:
        print(err, file=sys.stderr)
        print_outputs(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
