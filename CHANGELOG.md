# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
 - Add support for Windows (x86 and x86-64) using the MSVC compiler.
 - Add support for Linux (ARM) using the GCC compiler.
 - Add support for the NEON instruction set on ARM for better performance when generating PoW.
 - Add `nanolib.accounts.validate_seed` function for validating seeds
 - Add `nanolib.work.validate_threshold` and `nanolib.work.get_work_value` functions
 - Add `Block.threshold` property to adjust the required work threshold on a per-block basis
 - Add `Block.work_value` property to get the value of the included work

### Fixed
 - Fix conversions between MILLINANO and MEGANANO units when using strings as denomination parameters.

## [0.2] - 2019-03-07
### Added
 - `Block.has_valid_work` and `Block.has_valid_signature` properties are cached to prevent redundant work.

### Changed
 - PyPI package `pynanocurrency` and module `nanocurrency` have both been renamed to `nanolib`.
 - Improved performance when encoding or decoding account IDs.

### Fixed
 - Raise a `decimal.Inexact` exception when trying to convert amounts with higher precision than a single raw.

## 0.1 - 2019-03-01
### Added
- Initial release

[Unreleased]: https://github.com/Matoking/nanolib/compare/0.2...HEAD
[0.2]: https://github.com/Matoking/nanolib/compare/0.1...0.2
