"""EPUB to Markdown conversion pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from backend.config import OUTPUT_DIR
from backend.models import TaskState, TaskStatus

log = logging.getLogger(__name__)


def _extract_body_markdown(html_bytes: bytes) -> str:
    """Convert an EPUB HTML document to Markdown."""
    html = html_bytes.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body")
    if not body:
        return ""
    return md(str(body), heading_style="ATX").strip()


def convert_epub(task: TaskState, epub_path: Path, page_from: int = 0, page_to: int = 0) -> None:
    """Run EPUB→Markdown conversion in a background thread."""
    try:
        task.status = TaskStatus.CONVERTING
        task.progress = 5

        log.info("[%s] Reading EPUB...", task.task_id)
        book = epub.read_epub(str(epub_path))
        task.progress = 20

        # Build spine-ordered item lookup
        items_by_id = {item.get_id(): item for item in book.get_items()}
        spine_ids = [item_id for item_id, _linear in book.spine]

        # Extract images
        task_output_dir = OUTPUT_DIR / task.task_id / "images"
        task_output_dir.mkdir(parents=True, exist_ok=True)

        image_names: list[str] = []
        for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
            img_name = Path(item.get_name()).name
            img_path = task_output_dir / img_name
            img_path.write_bytes(item.get_content())
            image_names.append(img_name)

        task.progress = 40
        log.info("[%s] Extracted %d images, converting chapters...", task.task_id, len(image_names))

        # Convert chapters in spine order, applying page range if specified
        # page_from/page_to are 1-indexed chapter positions among ITEM_DOCUMENT entries
        sections: list[str] = []
        chapter_index = 0  # 1-indexed counter for document items
        for item_id in spine_ids:
            item = items_by_id.get(item_id)
            if item is None or item.get_type() != ebooklib.ITEM_DOCUMENT:
                continue
            chapter_index += 1
            if page_from > 0 and chapter_index < page_from:
                continue
            if page_to > 0 and chapter_index > page_to:
                break
            text = _extract_body_markdown(item.get_content())
            if text and len(text.strip()) > 5:
                sections.append(text)

        task.progress = 80

        # Combine all sections
        markdown = "\n\n---\n\n".join(sections)

        # Rewrite image paths for web display
        import re

        def rewrite_web(match: re.Match) -> str:
            alt = match.group(1)
            img_name = match.group(2).split("/")[-1]
            return f"![{alt}](/api/images/{task.task_id}/{img_name})"

        def rewrite_zip(match: re.Match) -> str:
            alt = match.group(1)
            img_name = match.group(2).split("/")[-1]
            return f"![{alt}](images/{img_name})"

        web_markdown = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", rewrite_web, markdown)
        zip_markdown = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", rewrite_zip, markdown)

        # Save markdown files
        md_path = OUTPUT_DIR / task.task_id / "output.md"
        md_path.write_text(web_markdown, encoding="utf-8")

        zip_md_path = OUTPUT_DIR / task.task_id / "output_zip.md"
        zip_md_path.write_text(zip_markdown, encoding="utf-8")

        task.markdown = web_markdown
        task.images = image_names
        task.progress = 100
        task.status = TaskStatus.COMPLETED
        log.info("[%s] EPUB conversion completed successfully.", task.task_id)

    except Exception as e:
        log.error("[%s] EPUB conversion failed: %s", task.task_id, e, exc_info=True)
        task.status = TaskStatus.FAILED
        task.error = str(e)
