`vcslinks`: Get URLs to commit/file/log/etc. pages in GitHub/GitLab/Bitbucket
=============================================================================

|docs-latest| |pypi| |build-status| |codecov| |mypy| |black| |commits-since|

`vcslinks` is a Python package for analyzing a local Git repository to
find a URL for web pages in the hosted services like GitHub, GitLab,
and Bitbucket.  For example, a permalink to the file ``setup.py`` with
lines 5 to 10 highlighted can be obtained by

..
   >>> getfixture("patch_analyze")

>>> import vcslinks
>>> vcslinks.file("setup.py", lines=(5, 10))
'https://github.com/USER/PROJECT/blob/55150afe539493d650889224db136bc8d9b7ecb8/setup.py#L5-L10'

`vcslinks` also comes with command line program `vcsbrowse` for
opening relevant pages of GitHub/GitLab/Bitbucket in web browser.

.. |docs-latest|
   image:: https://img.shields.io/badge/docs-latest-blue.svg
   :target: https://vcslinks.readthedocs.io/en/latest/
   :alt: Latest Documentation

.. |pypi|
   image:: https://img.shields.io/pypi/pyversions/vcslinks.svg
   :target: http://pypi.org/project/vcslinks
   :alt: PyPI - Python Version

.. |commits-since|
   image:: https://img.shields.io/github/commits-since/tkf/vcslinks/v0.1.2.svg?style=social
   :target: https://github.com/tkf/vcslinks
   :alt: GitHub commits since tagged version

.. |build-status|
   image:: https://travis-ci.com/tkf/vcslinks.svg?branch=master
   :target: https://travis-ci.com/tkf/vcslinks
   :alt: Build Status

.. |coveralls|
   image:: https://coveralls.io/repos/github/tkf/vcslinks/badge.svg?branch=master
   :target: https://coveralls.io/github/tkf/vcslinks?branch=master
   :alt: Test Coverage

.. |codecov|
   image:: https://codecov.io/gh/tkf/vcslinks/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/tkf/vcslinks
   :alt: Test Coverage

.. |black|
   image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black

.. |mypy|
   image:: http://www.mypy-lang.org/static/mypy_badge.svg
   :target: http://mypy-lang.org/
