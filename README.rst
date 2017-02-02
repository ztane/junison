========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |coveralls| |codecov|
    * - package
      - | |version| |downloads| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/junison/badge/?style=flat
    :target: https://readthedocs.org/projects/junison
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/ztane/junison.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ztane/junison

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/ztane/junison?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ztane/junison

.. |requires| image:: https://requires.io/github/ztane/junison/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/ztane/junison/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/ztane/junison/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/ztane/junison

.. |codecov| image:: https://codecov.io/github/ztane/junison/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/ztane/junison

.. |version| image:: https://img.shields.io/pypi/v/junison.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/junison

.. |commits-since| image:: https://img.shields.io/github/commits-since/ztane/junison/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/ztane/junison/compare/v0.1.0...master

.. |downloads| image:: https://img.shields.io/pypi/dm/junison.svg
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/junison

.. |wheel| image:: https://img.shields.io/pypi/wheel/junison.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/junison

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/junison.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/junison

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/junison.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/junison


.. end-badges

The ultimate JSON 3-way merger.

* Free software: BSD license

Installation
============

::

    pip install junison

Documentation
=============

https://junison.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
