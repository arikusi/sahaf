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
    version="0.1.0",
)

app.include_router(api_router)

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
