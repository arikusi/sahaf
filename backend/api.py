"""All API endpoints."""

from __future__ import annotations

import base64
import io
import re
import threading
import urllib.parse
import uuid
import zipfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from backend.classifier import classify_pdf
from backend.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, OUTPUT_DIR, UPLOAD_DIR
from backend.converter import convert_pdf
from backend.epub_converter import convert_epub
from backend.models import PdfType, TaskState, TaskStatus
from backend.splitter import split_markdown

router = APIRouter(prefix="/api")


def _safe_filename(name: str) -> str:
    """Replace non-latin-1 characters with ASCII equivalents for HTTP headers."""
    try:
        name.encode("latin-1")
        return name
    except UnicodeEncodeError:
        return name.encode("ascii", errors="replace").decode("ascii")

# In-memory task store
tasks: dict[str, TaskState] = {}


@router.post("/upload")
async def upload_pdf(file: UploadFile):
    """Upload a PDF file and return a task_id."""
    if not file.filename:
        raise HTTPException(400, "Dosya adı bulunamadı.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Sadece PDF ve EPUB dosyaları kabul edilir. Gönderilen: {ext}")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(400, f"Dosya çok büyük ({size_mb:.1f}MB). Maksimum: {MAX_FILE_SIZE_MB}MB")

    task_id = uuid.uuid4().hex[:12]
    task_dir = UPLOAD_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = task_dir / file.filename
    pdf_path.write_bytes(content)

    task = TaskState(task_id=task_id, filename=file.filename)
    tasks[task_id] = task

    return {"task_id": task_id, "filename": file.filename}


def _get_task(task_id: str) -> TaskState:
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(404, f"Görev bulunamadı: {task_id}")
    return task


def _get_pdf_path(task: TaskState) -> Path:
    return UPLOAD_DIR / task.task_id / task.filename


@router.get("/classify/{task_id}")
async def classify(task_id: str):
    """Classify the uploaded PDF as digital, scanned, or mixed."""
    task = _get_task(task_id)
    pdf_path = _get_pdf_path(task)

    if not pdf_path.exists():
        raise HTTPException(404, "Dosya bulunamadı.")

    is_epub = Path(task.filename).suffix.lower() == ".epub"

    if is_epub:
        # EPUB files are always digital text — skip PDF classification
        import ebooklib
        from ebooklib import epub as _epub
        book = _epub.read_epub(str(pdf_path))
        items_by_id = {i.get_id(): i for i in book.get_items()}
        chapter_count = sum(
            1 for item_id, _ in book.spine
            if (item := items_by_id.get(item_id)) and item.get_type() == ebooklib.ITEM_DOCUMENT
        )
        task.pdf_type = PdfType.DIGITAL
        task.page_count = 0
        task.status = TaskStatus.CLASSIFIED
    else:
        chapter_count = 0
        task.status = TaskStatus.CLASSIFYING
        pdf_type, page_count = classify_pdf(pdf_path)
        task.pdf_type = pdf_type
        task.page_count = page_count
        task.status = TaskStatus.CLASSIFIED

    response = {
        "task_id": task_id,
        "pdf_type": task.pdf_type.value,
        "page_count": task.page_count,
    }
    if is_epub:
        response["chapter_count"] = chapter_count
    return response


@router.post("/convert/{task_id}")
async def convert(
    task_id: str,
    page_from: int = Query(0, ge=0, alias="page_from"),
    page_to: int = Query(0, ge=0, alias="page_to"),
):
    """Start background PDF/EPUB→Markdown conversion.

    Optional query params:
    - page_from: first page/chapter to convert (1-indexed, 0 = start from beginning)
    - page_to:   last page/chapter to convert  (1-indexed, 0 = convert to end)
    """
    task = _get_task(task_id)
    pdf_path = _get_pdf_path(task)

    if not pdf_path.exists():
        raise HTTPException(404, "PDF dosyası bulunamadı.")

    if task.status == TaskStatus.CONVERTING:
        raise HTTPException(409, "Dönüşüm zaten devam ediyor.")

    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(409, "Dönüşüm zaten tamamlandı.")

    is_epub = Path(task.filename).suffix.lower() == ".epub"
    target_fn = convert_epub if is_epub else convert_pdf

    thread = threading.Thread(
        target=target_fn,
        args=(task, pdf_path, page_from, page_to),
        daemon=True,
    )
    thread.start()

    return {"task_id": task_id, "status": "converting"}


@router.get("/status/{task_id}")
async def status(task_id: str):
    """Poll conversion status."""
    task = _get_task(task_id)
    return task.to_dict()


@router.get("/result/{task_id}")
async def result(task_id: str):
    """Get conversion result (markdown + image list)."""
    task = _get_task(task_id)

    if task.status == TaskStatus.FAILED:
        raise HTTPException(500, f"Dönüşüm başarısız: {task.error}")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(409, "Dönüşüm henüz tamamlanmadı.")

    return {
        "task_id": task_id,
        "markdown": task.markdown,
        "images": task.images,
        "page_count": task.page_count,
        "pdf_type": task.pdf_type.value,
    }


@router.get("/download/{task_id}")
async def download_md(task_id: str):
    """Download the converted markdown file with embedded images."""
    task = _get_task(task_id)
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(409, "Dönüşüm henüz tamamlanmadı.")

    task_dir = OUTPUT_DIR / task_id
    zip_md_path = task_dir / "output_zip.md"
    images_dir = task_dir / "images"

    if not zip_md_path.exists():
        raise HTTPException(404, "Markdown dosyası bulunamadı.")

    full_text = zip_md_path.read_text(encoding="utf-8")
    embedded = _embed_images(full_text, images_dir)

    stem = Path(task.filename).stem
    safe_name = _safe_filename(f"{stem}.md")
    encoded = urllib.parse.quote(f"{stem}.md")

    return StreamingResponse(
        io.BytesIO(embedded.encode("utf-8")),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
    )


@router.get("/split-preview/{task_id}")
async def split_preview(task_id: str, parts: int = Query(1, ge=1, le=100)):
    """Preview how the markdown would be split — returns part sizes and first lines."""
    task = _get_task(task_id)
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(409, "Dönüşüm henüz tamamlanmadı.")

    zip_md_path = OUTPUT_DIR / task_id / "output_zip.md"
    if not zip_md_path.exists():
        raise HTTPException(404, "Çıktı dosyası bulunamadı.")

    full_text = zip_md_path.read_text(encoding="utf-8")
    chunks = split_markdown(full_text, parts)

    preview = []
    for i, chunk in enumerate(chunks, 1):
        # First non-empty line as label
        first_line = ""
        for line in chunk.split("\n"):
            stripped = line.strip().lstrip("#").strip()
            if stripped and stripped != "---":
                first_line = stripped[:80]
                break
        preview.append({
            "part": i,
            "chars": len(chunk),
            "lines": chunk.count("\n") + 1,
            "starts_with": first_line,
        })

    return {
        "task_id": task_id,
        "total_parts": len(chunks),
        "total_chars": len(full_text),
        "parts": preview,
    }


_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def _embed_images(markdown: str, images_dir: Path) -> str:
    """Replace image paths with inline base64 data URIs."""

    def _replacer(match: re.Match) -> str:
        alt = match.group(1)
        img_name = match.group(2).split("/")[-1]
        img_file = images_dir / img_name

        if not img_file.exists():
            return match.group(0)

        mime = _MIME.get(img_file.suffix.lower(), "application/octet-stream")
        b64 = base64.b64encode(img_file.read_bytes()).decode("ascii")
        return f"![{alt}](data:{mime};base64,{b64})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _replacer, markdown)


@router.get("/download/{task_id}/zip")
async def download_zip(
    task_id: str,
    parts: int = Query(1, ge=1, le=100),
    range_from: int = Query(0, ge=0, alias="from"),
    range_to: int = Query(0, ge=0, alias="to"),
):
    """Download markdown as ZIP with embedded images.

    - parts=1  → single file
    - parts=N  → split into N parts
    - from=3&to=7  → only include parts 3-7 (requires parts>1)
    """
    task = _get_task(task_id)
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(409, "Dönüşüm henüz tamamlanmadı.")

    task_dir = OUTPUT_DIR / task_id
    zip_md_path = task_dir / "output_zip.md"
    images_dir = task_dir / "images"

    if not zip_md_path.exists():
        raise HTTPException(404, "Çıktı dosyası bulunamadı.")

    full_text = zip_md_path.read_text(encoding="utf-8")
    embedded = _embed_images(full_text, images_dir)
    stem = Path(task.filename).stem

    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if parts <= 1:
            zf.writestr(f"{stem}.md", embedded)
        else:
            chunks = split_markdown(embedded, parts)
            pad = len(str(len(chunks)))
            total = len(chunks)

            # Apply range filter
            start = max(range_from, 1) if range_from else 1
            end = min(range_to, total) if range_to else total

            if start > total:
                raise HTTPException(400, f"Baslangic ({start}) toplam parca sayisindan ({total}) buyuk.")

            for i, chunk in enumerate(chunks, 1):
                if start <= i <= end:
                    zf.writestr(f"{stem}_part{str(i).zfill(pad)}.md", chunk)

    buf.seek(0)
    encoded = urllib.parse.quote(f"{stem}.zip")
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
    )


@router.get("/images/{task_id}/{name}")
async def serve_image(task_id: str, name: str):
    """Serve an extracted image."""
    img_path = OUTPUT_DIR / task_id / "images" / name
    if not img_path.exists():
        raise HTTPException(404, "Görsel bulunamadı.")

    # Determine media type from extension
    ext = img_path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(path=str(img_path), media_type=media_type)
