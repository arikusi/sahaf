# Changelog

All notable changes to Sahaf will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-04-10

### Added

* PyPI package — `pip install sahaf`
* Publish workflow (trusted publisher, auto-publish on release)
* CI, PyPI, and license badges in README

## [0.2.0] - 2026-04-10

### Added

* CLI entry point — run `sahaf` after `pip install -e .`
* Unit test suite for splitter, models, classifier, and utils (26 tests)
* GitHub Actions CI pipeline (lint + test on Python 3.10-3.12)
* Shared `backend/utils.py` module for image path rewriting

### Changed

* Badge labels and split-part labels now use i18n translations
* `marker-pdf` dependency pinned to `>=1.0.0,<2.0.0`
* Inline ebooklib import in api.py moved to module level
* Default server binds to `127.0.0.1` (localhost only) for security
* Enriched pyproject.toml with classifiers, keywords, URLs, and dev dependencies

### Fixed

* Duplicate `rangeLabel`, `rangeFrom`, `rangeTo` keys in lang.js

### Removed

* Windows `install.bat` and `start.bat` scripts (replaced by CLI entry point)

## [0.1.0] - 2025-06-08

Initial release.

### Added

* PDF to Markdown conversion via Marker (95.67% accuracy) with Surya OCR (90+ languages)
* EPUB to Markdown conversion via ebooklib + markdownify
* Automatic PDF classification (digital / scanned / mixed) using PyMuPDF
* Page range selection for partial PDF conversion
* Chapter range selection for partial EPUB conversion
* Smart splitting algorithm that cuts at heading/paragraph boundaries
* Self-contained output with base64-embedded images
* Split preview endpoint to inspect part boundaries before download
* ZIP download for split outputs
* Bilingual UI (Turkish / English) with client-side toggle
* Dark/light theme with persistent toggle
* Drag & drop single-page web interface
* FastAPI REST API with upload, classify, convert, status, result, and download endpoints
* Windows install.bat and start.bat scripts

[0.2.1]: https://github.com/arikusi/sahaf/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/arikusi/sahaf/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/arikusi/sahaf/releases/tag/v0.1.0
