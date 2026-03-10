from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field


class PdfType(str, Enum):
    DIGITAL = "digital"
    SCANNED = "scanned"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class TaskStatus(str, Enum):
    UPLOADED = "uploaded"
    CLASSIFYING = "classifying"
    CLASSIFIED = "classified"
    CONVERTING = "converting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskState:
    task_id: str
    filename: str
    status: TaskStatus = TaskStatus.UPLOADED
    pdf_type: PdfType = PdfType.UNKNOWN
    page_count: int = 0
    progress: int = 0  # 0-100
    error: str | None = None
    markdown: str = ""
    images: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "filename": self.filename,
            "status": self.status.value,
            "pdf_type": self.pdf_type.value,
            "page_count": self.page_count,
            "progress": self.progress,
            "error": self.error,
            "images": self.images,
        }
