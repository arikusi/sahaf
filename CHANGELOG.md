# Changelog

All notable changes to Sahaf will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/arikusi/sahaf/releases/tag/v0.1.0
