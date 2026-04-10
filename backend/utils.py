"""Shared utility functions."""

from __future__ import annotations

import re


def rewrite_image_paths(markdown: str, task_id: str) -> str:
    """Rewrite image paths in markdown to point to the API endpoint."""
    def replacer(match: re.Match) -> str:
        alt = match.group(1)
        img_name = match.group(2).split("/")[-1]
        return f"![{alt}](/api/images/{task_id}/{img_name})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replacer, markdown)


def rewrite_image_paths_for_zip(markdown: str) -> str:
    """Rewrite image paths for ZIP download (relative images/ dir)."""
    def replacer(match: re.Match) -> str:
        alt = match.group(1)
        img_name = match.group(2).split("/")[-1]
        return f"![{alt}](images/{img_name})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replacer, markdown)
