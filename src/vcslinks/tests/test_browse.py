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
