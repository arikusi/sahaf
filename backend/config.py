from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
FRONTEND_DIR = BASE_DIR / "frontend"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE_MB = 200
POLL_INTERVAL_SEC = 2
ALLOWED_EXTENSIONS = {".pdf", ".epub"}

# Classifier thresholds
MIN_TEXT_LENGTH = 50          # Minimum characters per page to count as digital
IMAGE_COVERAGE_THRESHOLD = 0.80  # 80% image coverage → scanned
