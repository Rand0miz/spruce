# Changelog

All notable changes to this project are documented here. This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-07-30

First public release of the `sprucekit` evidence compiler.

### Added

- Training-free tokenizer-level radix-2 lexical hierarchy.
- Beam-16 traversal with four final source blocks.
- Exact-text paragraph expansion and source-order stitching.
- Python API (`SpruceCompiler`, `CompilerConfig`) and the `sprucekit compile`,
  `sprucekit answer`, and `sprucekit info` commands.
- Explicit Qwen YaRN configuration helpers for long-context reading.
- Frozen 16K–128K paper-result artifacts: report, tables, and figures.
- Colab quickstart, two runnable examples, and unit tests.

### Notes

- Qwen2.5-Coder-1.5B-Instruct is the only verified reader. Other Qwen sizes
  are experimental pending frozen cross-size validation.
- The experimental learned selector and sparse-attention kernels remain in the
  research archive and are not part of this runtime.

[Unreleased]: https://github.com/Rand0miz/spruce/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Rand0miz/spruce/releases/tag/v0.1.0
