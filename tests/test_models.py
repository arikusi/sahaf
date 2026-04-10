"""Tests for backend.models."""

from backend.models import PdfType, TaskState, TaskStatus


class TestPdfType:
    def test_enum_values(self):
        assert PdfType.DIGITAL.value == "digital"
        assert PdfType.SCANNED.value == "scanned"
        assert PdfType.MIXED.value == "mixed"
        assert PdfType.UNKNOWN.value == "unknown"

    def test_string_comparison(self):
        assert PdfType.DIGITAL == "digital"


class TestTaskStatus:
    def test_status_values(self):
        statuses = [s.value for s in TaskStatus]
        assert "uploaded" in statuses
        assert "completed" in statuses
        assert "failed" in statuses


class TestTaskState:
    def test_defaults(self):
        task = TaskState(task_id="abc123", filename="test.pdf")
        assert task.status == TaskStatus.UPLOADED
        assert task.pdf_type == PdfType.UNKNOWN
        assert task.page_count == 0
        assert task.progress == 0
        assert task.error is None
        assert task.markdown == ""
        assert task.images == []

    def test_to_dict(self):
        task = TaskState(task_id="abc123", filename="test.pdf")
        d = task.to_dict()
        assert d["task_id"] == "abc123"
        assert d["filename"] == "test.pdf"
        assert d["status"] == "uploaded"
        assert d["pdf_type"] == "unknown"
        assert d["page_count"] == 0
        assert d["progress"] == 0
        assert d["error"] is None
        assert d["images"] == []

    def test_to_dict_with_state_changes(self):
        task = TaskState(task_id="abc123", filename="test.pdf")
        task.status = TaskStatus.COMPLETED
        task.pdf_type = PdfType.DIGITAL
        task.page_count = 42
        task.progress = 100
        d = task.to_dict()
        assert d["status"] == "completed"
        assert d["pdf_type"] == "digital"
        assert d["page_count"] == 42
        assert d["progress"] == 100

    def test_images_field_isolation(self):
        """Ensure default mutable field doesn't share state."""
        t1 = TaskState(task_id="a", filename="a.pdf")
        t2 = TaskState(task_id="b", filename="b.pdf")
        t1.images.append("img.png")
        assert t2.images == []
