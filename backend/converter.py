"""Marker integration — PDF to Markdown conversion pipeline."""

from __future__ import annotations

import logging
import re
import threading
from pathlib import Path

from backend.config import OUTPUT_DIR
from backend.models import PdfType, TaskState, TaskStatus

log = logging.getLogger(__name__)

# Singleton model storage
_models: dict | None = None
_models_lock = threading.Lock()


def _get_models() -> dict:
    """Load Marker models once (thread-safe singleton)."""
    global _models
    if _models is None:
        with _models_lock:
            if _models is None:
                log.info("Loading Marker models (first run requires download)...")
                from marker.models import create_model_dict
                _models = create_model_dict()
                log.info("Marker models ready.")
    return _models


def _rewrite_image_paths(markdown: str, task_id: str) -> str:
    """Rewrite image paths in markdown to point to our API endpoint."""
    def replacer(match: re.Match) -> str:
        alt = match.group(1)
        img_name = match.group(2).split("/")[-1]
        return f"![{alt}](/api/images/{task_id}/{img_name})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replacer, markdown)


def _rewrite_for_zip(markdown: str) -> str:
    """Rewrite image paths for ZIP download (relative images/ dir)."""
    def replacer(match: re.Match) -> str:
        alt = match.group(1)
        img_name = match.group(2).split("/")[-1]
        return f"![{alt}](images/{img_name})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replacer, markdown)


def _extract_page_range(pdf_path: Path, page_from: int, page_to: int) -> Path:
    """Extract pages [page_from, page_to] (1-indexed inclusive) into a temp PDF."""
    import fitz
    src = fitz.open(str(pdf_path))
    dst = fitz.open()
    # page_from and page_to are 1-indexed, fitz uses 0-indexed
    start = max(page_from - 1, 0)
    end = min(page_to, len(src))  # page_to is inclusive
    dst.insert_pdf(src, from_page=start, to_page=end - 1)
    temp_path = pdf_path.parent / f"_range_{page_from}_{page_to}.pdf"
    dst.save(str(temp_path))
    dst.close()
    src.close()
    return temp_path


def convert_pdf(task: TaskState, pdf_path: Path, page_from: int = 0, page_to: int = 0) -> None:
    """Run Marker conversion in a background thread."""
    try:
        task.status = TaskStatus.CONVERTING
        task.progress = 5

        from marker.converters.pdf import PdfConverter
        from marker.config.parser import ConfigParser
        from marker.output import text_from_rendered

        log.info("[%s] Loading models...", task.task_id)
        models = _get_models()
        task.progress = 20
        log.info("[%s] Models ready, starting conversion...", task.task_id)

        # Extract page range if specified
        if page_from > 0:
            log.info("[%s] Extracting page range %d-%d...", task.task_id, page_from, page_to)
            pdf_path = _extract_page_range(pdf_path, page_from, page_to)

        force_ocr = task.pdf_type in (PdfType.SCANNED, PdfType.MIXED)

        config: dict = {"output_format": "markdown"}
        if force_ocr:
            config["force_ocr"] = True

        config_parser = ConfigParser(config)

        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=models,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
        )

        task.progress = 30
        log.info("[%s] Marker converting PDF...", task.task_id)
        rendered = converter(str(pdf_path))
        task.progress = 80
        log.info("[%s] Conversion done, writing outputs...", task.task_id)

        text, _, images = text_from_rendered(rendered)

        # Save images
        task_output_dir = OUTPUT_DIR / task.task_id / "images"
        task_output_dir.mkdir(parents=True, exist_ok=True)

        image_names: list[str] = []
        for img_name, img in images.items():
            img.save(str(task_output_dir / img_name))
            image_names.append(img_name)

        # Rewrite image paths for web display
        markdown = _rewrite_image_paths(text, task.task_id)

        # Save markdown file
        md_path = OUTPUT_DIR / task.task_id / "output.md"
        md_path.write_text(markdown, encoding="utf-8")

        # Also save ZIP-friendly version
        zip_md = _rewrite_for_zip(text)
        zip_md_path = OUTPUT_DIR / task.task_id / "output_zip.md"
        zip_md_path.write_text(zip_md, encoding="utf-8")

        task.markdown = markdown
        task.images = image_names
        task.progress = 100
        task.status = TaskStatus.COMPLETED
        log.info("[%s] Task completed successfully.", task.task_id)

    except Exception as e:
        log.error("[%s] Conversion failed: %s", task.task_id, e, exc_info=True)
        task.status = TaskStatus.FAILED
        task.error = str(e)
