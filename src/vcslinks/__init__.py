r"""
`vcslinks`: Get URLs to commit/file/log/etc. pages in GitHub/GitLab/Bitbucket
=============================================================================

|docs-latest| |build-status| |coveralls| |mypy| |black|


.. |docs-latest|
   image:: https://img.shields.io/badge/docs-latest-blue.svg
   :target: https://vcslinks.readthedocs.io/en/latest/
   :alt: Latest Documentation

.. |build-status|
   image:: https://travis-ci.com/tkf/vcslinks.svg?branch=master
   :target: https://travis-ci.com/tkf/vcslinks
   :alt: Build Status

.. |coveralls|
   image:: https://coveralls.io/repos/github/tkf/vcslinks/badge.svg?branch=master
   :target: https://coveralls.io/github/tkf/vcslinks?branch=master
   :alt: Test Coverage

.. |black|
   image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black

.. |mypy|
   image:: http://www.mypy-lang.org/static/mypy_badge.svg
   :target: http://mypy-lang.org/
"""

__version__ = "0.0.0"
__author__ = "Takafumi Arakaki"
__license__ = "MIT"

from .api import analyze, blame, commit, diff, file, log, pull_request, root
from .weburl import WebURL
