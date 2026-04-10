"""Tests for backend.classifier — uses mocked PyMuPDF."""

from unittest.mock import MagicMock, patch

from backend.classifier import classify_pdf
from backend.models import PdfType


def _make_mock_page(text, image_coverage):
    """Create a mock PyMuPDF page."""
    page = MagicMock()
    page.get_text.return_value = text
    page.rect.width = 100
    page.rect.height = 100

    if image_coverage > 0:
        img_rect = MagicMock()
        img_rect.width = 100
        img_rect.height = image_coverage * 100
        page.get_images.return_value = [(1,)]
        page.get_image_rects.return_value = [img_rect]
    else:
        page.get_images.return_value = []

    return page


def _make_mock_doc(pages):
    """Create a mock PyMuPDF document."""
    doc = MagicMock()
    doc.__len__ = lambda self: len(pages)
    doc.__iter__ = lambda self: iter(pages)
    return doc


class TestClassifyPdf:
    @patch("backend.classifier.pymupdf")
    def test_digital_pdf(self, mock_pymupdf):
        pages = [_make_mock_page("A" * 100, 0.0)]
        mock_pymupdf.open.return_value = _make_mock_doc(pages)

        pdf_type, count = classify_pdf("fake.pdf")
        assert pdf_type == PdfType.DIGITAL
        assert count == 1

    @patch("backend.classifier.pymupdf")
    def test_scanned_pdf(self, mock_pymupdf):
        pages = [_make_mock_page("", 0.95)]
        mock_pymupdf.open.return_value = _make_mock_doc(pages)

        pdf_type, count = classify_pdf("fake.pdf")
        assert pdf_type == PdfType.SCANNED
        assert count == 1

    @patch("backend.classifier.pymupdf")
    def test_mixed_pdf(self, mock_pymupdf):
        pages = [
            _make_mock_page("A" * 100, 0.0),
            _make_mock_page("", 0.95),
        ]
        mock_pymupdf.open.return_value = _make_mock_doc(pages)

        pdf_type, count = classify_pdf("fake.pdf")
        assert pdf_type == PdfType.MIXED
        assert count == 2

    @patch("backend.classifier.pymupdf")
    def test_empty_pdf(self, mock_pymupdf):
        mock_pymupdf.open.return_value = _make_mock_doc([])

        pdf_type, count = classify_pdf("fake.pdf")
        assert pdf_type == PdfType.UNKNOWN
        assert count == 0
