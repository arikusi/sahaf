"""FastAPI app — static mount, root route, API router."""

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api import router as api_router
from backend.config import FRONTEND_DIR

app = FastAPI(
    title="Sahaf",
    description="PDF to Markdown converter with OCR support.",
    version="0.2.0",
)

app.include_router(api_router)

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


def run() -> None:
    """Launch the Sahaf development server."""
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    run()
