# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Unreleased
### Fixed
 - Fix pip installation in ARM environments.

## [0.4] - 2019-10-23
### Added
  - Add `Block.to_dict()`

### Changed
 - Improved performance when encoding or decoding account IDs.
 - Reduced memory footprint for Block instances.

## [0.3] - 2019-06-08
### Added
 - Add support for Windows (x86 and x86-64) using the MSVC compiler.
 - Add support for Linux (ARM) using the GCC compiler.
 - Add support for the NEON instruction set on ARM for better performance when generating PoW.
 - Add `nanolib.accounts.validate_seed` function for validating seeds.
 - Add `nanolib.work.validate_difficulty`, `nanolib.work.get_work_value`, `nanolib.work.derive_work_difficulty` and `nanolib.work.derive_work_multiplier` functions to help with dynamic PoW difficulty.
 - Add `Block.difficulty` property to adjust the required work difficulty on a per-block basis.
 - Add `Block.work_value` property to get the value of the included work.

### Changed
 - Enable multithreading when generating PoW by releasing GIL.

### Fixed
 - Fix conversions between MILLINANO and MEGANANO units when using strings as denomination parameters.
 - Verify epoch V1 state blocks correctly. See [nanocurrency/nano-node#955](https://github.com/nanocurrency/nano-node/pull/955) for details.

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

[Unreleased]: https://github.com/Matoking/nanolib/compare/0.4...HEAD
[0.4]: https://github.com/Matoking/nanolib/compare/0.3...0.4
[0.3]: https://github.com/Matoking/nanolib/compare/0.2...0.3
[0.2]: https://github.com/Matoking/nanolib/compare/0.1...0.2
