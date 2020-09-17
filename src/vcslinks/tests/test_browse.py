import shlex
import sys

import pytest  # type: ignore

from ..browse import main


def dry_run(*args):
    main(("--dry-run",) + args)


def test_smoke(github_repository):
    dry_run("auto")
    dry_run("commit")
    dry_run("log")
    dry_run("file", "README.md")
    dry_run("diff")
    dry_run("blame", "README.md")


def test_smoke_browser(github_repository):
    # No-op command:
    browser = " ".join(map(shlex.quote, [sys.executable, "-c", ""]))
    main(["--browser", browser])


def test_noremote(noremote_repository, capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--dry-run"])
    captured = capsys.readouterr()
    assert excinfo.value.code == 1
    assert "Branch `master` does not have remote." in captured.err
