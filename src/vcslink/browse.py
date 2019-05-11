import argparse
import subprocess
import sys
import webbrowser

from .git import GitRepoAnalyzer


def open_url(dry_run, url):
    if dry_run:
        print("Open:", url)
    else:
        webbrowser.open(url)


def cli_auto(dry_run):
    repo = GitRepoAnalyzer.from_path(".")
    if repo.need_pr():
        url = repo.weburl.pr()
    else:
        url = repo.weburl.root
    open_url(dry_run, url)


def cli_commit(dry_run, revision):
    repo = GitRepoAnalyzer.from_path(".")
    url = repo.weburl.commit(revision)
    open_url(dry_run, url)


def cli_log(dry_run, revision):
    repo = GitRepoAnalyzer.from_path(".")
    url = repo.weburl.log(revision)
    open_url(dry_run, url)


def cli_file(dry_run, **kwargs):
    repo = GitRepoAnalyzer.from_path(".")
    url = repo.weburl.file(**kwargs)
    open_url(dry_run, url)


class CustomFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def make_parser(doc=__doc__):
    parser = argparse.ArgumentParser(
        formatter_class=CustomFormatter, description=__doc__
    )
    parser.add_argument("--dry-run", action="store_true")

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
        (lambda func, **kwds: func(**kwds))(**vars(ns))
    except subprocess.CalledProcessError as err:
        print(err, file=sys.stderr)
        print_outputs(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
