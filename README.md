nanolib
=======

[![image](https://img.shields.io/pypi/v/nanolib.svg)](https://pypi.org/project/nanolib/)
[![codecov](https://codecov.io/gh/Matoking/nanolib/branch/master/graph/badge.svg)](https://codecov.io/gh/Matoking/nanolib)
[![Build Status](https://travis-ci.com/Matoking/nanolib.png?branch=master)](https://travis-ci.com/Matoking/nanolib)
[![image](https://readthedocs.org/projects/nanolib/badge/?version=latest)](https://nanolib.readthedocs.io/en/latest/?badge=latest)


A set of tools for handling functions related to the NANO cryptocurrency protocol.

Features
========
* Solve and verify proof-of-work
* Create and deserialize legacy and universal blocks
* Account generation from seed using the same algorithm as the original NANO wallet and NanoVault
* Functions for converting between different NANO denominations
* High performance cryptographic operations using C extensions (signing and verifying blocks, and solving block proof-of-work)
  * Proof-of-work solving supports SSE2, SSSE3, SSE4.1 and AVX instruction sets for improved performance. The best supported implementation is selected at runtime with a fallback implementation with universal compatibility.
* Backed by automated tests
* Compatible with Python 3.6 and up
* Licensed under the very permissive *Creative Commons Zero* license

Documentation
=============

An online copy of the documentation can be found at [Read the Docs](https://nanolib.readthedocs.io/en/latest/).

You can also build the documentation yourself by running `python setup.py build_sphinx`.

Commands
========

The `setup.py` script comes with a few additional commands besides installation:

* `build_sphinx`
  * Build the documentation in `build/sphinx/html`.
* `test`
  * Run tests using pytest
* `speed`
  * Run a benchmark testing the performance of various cryptographic operations used in the library.

Donations
=========

**xrb_33psgb1exxuftgjthbz4tsgzm5qmyzawrfzptpmp3nwzousbypqf6bcmrk69**
