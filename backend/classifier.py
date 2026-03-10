"""PyMuPDF ile PDF sınıflandırma: digital / scanned / mixed."""

from pathlib import Path

import pymupdf

from backend.config import MIN_TEXT_LENGTH, IMAGE_COVERAGE_THRESHOLD
from backend.models import PdfType


def classify_pdf(pdf_path: Path) -> tuple[PdfType, int]:
    """Classify a PDF as digital, scanned, or mixed.

    Returns (pdf_type, page_count).
    """
    doc = pymupdf.open(str(pdf_path))
    page_count = len(doc)

    if page_count == 0:
        doc.close()
        return PdfType.UNKNOWN, 0

    digital_pages = 0
    scanned_pages = 0

    for page in doc:
        text = page.get_text().strip()
        has_text = len(text) >= MIN_TEXT_LENGTH

        # Calculate image coverage ratio
        page_area = abs(page.rect.width * page.rect.height)
        image_area = 0.0
        if page_area > 0:
            for img in page.get_images(full=True):
                xref = img[0]
                try:
                    rects = page.get_image_rects(xref)
                    for rect in rects:
                        image_area += abs(rect.width * rect.height)
                except Exception:
                    pass
            coverage = image_area / page_area
        else:
            coverage = 0.0

        if has_text and coverage < IMAGE_COVERAGE_THRESHOLD:
            digital_pages += 1
        else:
            scanned_pages += 1

    doc.close()

    if digital_pages > 0 and scanned_pages == 0:
        pdf_type = PdfType.DIGITAL
    elif scanned_pages > 0 and digital_pages == 0:
        pdf_type = PdfType.SCANNED
    elif digital_pages > 0 and scanned_pages > 0:
        pdf_type = PdfType.MIXED
    else:
        pdf_type = PdfType.UNKNOWN

    return pdf_type, page_count
