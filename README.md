# Sahaf

Local PDF & EPUB to Markdown converter with automatic digital/scanned detection, OCR support, smart splitting, and page-range selection. Converts books to clean, self-contained Markdown files with embedded images using Marker (95.67% accuracy) and Surya OCR (90+ languages). No cloud APIs — runs entirely on your hardware.

<p align="center">
  <video src="https://github.com/user-attachments/assets/76b2484c-b69b-4cf2-8436-1ef2ae3cef20" width="480" autoplay loop muted>
  </video>
</p>

## Features

- **PDF & EPUB support** — handles both formats natively
- **Automatic PDF classification** — detects digital, scanned, or mixed PDFs via PyMuPDF
- **High-accuracy conversion** — Marker with 95.67% benchmark accuracy
- **Built-in OCR** — Surya OCR supports 90+ languages (Turkish, English, Arabic, etc.)
- **Page/chapter range selection** — convert only a specific section of the book (e.g. pages 19-88)
- **Smart splitting** — split output into N parts, cutting at heading/paragraph boundaries instead of mid-sentence
- **Self-contained output** — images embedded as base64 directly in Markdown, no separate files
- **Split preview** — see exactly how parts will be divided before downloading
- **Bilingual UI** — Turkish / English interface with one-click toggle
- **Dark/light theme** — lavender-toned design, persistent toggle
- **Drag & drop UI** — clean single-page web interface

## Install

```bash
git clone https://github.com/arikusi/sahaf.git
cd sahaf
pip install -e .
```

> Marker models (~2-3GB) are downloaded automatically on first conversion.

## Quick Start

**Windows:** Double-click `install.bat` then `start.bat`.

**Manual:**

```bash
uvicorn backend.main:app --reload
```

Open `http://localhost:8000` in your browser.

## How It Works

1. **Upload** — drag & drop a PDF or EPUB file
2. **Classify** — PyMuPDF analyzes PDF type; EPUB chapters are counted
3. **Select range** *(optional)* — pick specific pages or chapters to convert
4. **Convert** — Marker processes PDF; ebooklib + markdownify handles EPUB
5. **Split** *(optional)* — choose how many parts to split the output into
6. **Download** — get a single `.md` or a ZIP with split parts, all images embedded inline

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/upload` | Upload PDF/EPUB, returns `task_id` |
| `GET` | `/api/classify/{task_id}` | Detect PDF type + page count, or EPUB chapter count |
| `POST` | `/api/convert/{task_id}?page_from=&page_to=` | Start conversion (optional page range) |
| `GET` | `/api/status/{task_id}` | Poll conversion progress |
| `GET` | `/api/result/{task_id}` | Get markdown + image list |
| `GET` | `/api/download/{task_id}` | Download `.md` with embedded images |
| `GET` | `/api/download/{task_id}/zip?parts=N` | Download ZIP with N split `.md` files |
| `GET` | `/api/split-preview/{task_id}?parts=N` | Preview split structure before download |

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **PDF Classification**: PyMuPDF
- **PDF Conversion**: Marker (marker-pdf) + Surya OCR
- **EPUB Conversion**: ebooklib + markdownify
- **Smart Splitting**: Custom algorithm — heading/HR/paragraph boundary detection
- **Frontend**: Vanilla HTML/CSS/JS + marked.js
- **i18n**: TR/EN with client-side toggle

## Requirements

- Python 3.10+
- 4-6GB RAM (when Marker models are loaded)
- **GPU strongly recommended for PDF** — CPU-only is extremely slow (~1 hour for a 27-page mixed PDF on i5 + 40GB RAM). A CUDA-capable GPU converts the same file in minutes.
- EPUB conversion is lightweight — no GPU needed, runs instantly

## License

GPL-3.0
