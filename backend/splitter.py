"""Smart markdown splitter — splits at heading/paragraph boundaries."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class _SplitCandidate:
    pos: int    # character offset (start of line)
    score: int  # higher = better place to split


def _find_candidates(text: str) -> list[_SplitCandidate]:
    """Scan markdown for all potential split points, scored by quality."""
    candidates: list[_SplitCandidate] = []

    for match in re.finditer(r"^(#{1,6}\s|---\s*$)", text, re.MULTILINE):
        line_start = text.rfind("\n", 0, match.start()) + 1
        raw = match.group(1).rstrip()

        if raw == "---":
            score = 85
        elif raw.startswith("# "):
            score = 100
        elif raw.startswith("## "):
            score = 90
        elif raw.startswith("### "):
            score = 80
        else:
            score = 70  # h4-h6

        candidates.append(_SplitCandidate(line_start, score))

    # Paragraph breaks (blank line between content)
    for match in re.finditer(r"\n\n+", text):
        pos = match.end()
        # Only add if not already covered by a header/hr at this position
        if not any(c.pos == pos for c in candidates):
            candidates.append(_SplitCandidate(pos, 50))

    candidates.sort(key=lambda c: c.pos)
    return candidates


def split_markdown(text: str, num_parts: int) -> list[str]:
    """Split *text* into *num_parts* pieces, cutting at smart boundaries.

    Algorithm
    ---------
    1. Calculate ideal cut positions (equal-size chunks).
    2. For each ideal position, search a window of ±30 % target size.
    3. Pick the highest-scored candidate in that window; break ties by
       proximity to the ideal position.
    4. Collect the resulting slices and strip whitespace.
    """
    if num_parts <= 1:
        return [text]

    total = len(text)
    if total == 0:
        return [""]

    target = total / num_parts
    candidates = _find_candidates(text)

    if not candidates:
        # Fallback: brute-force equal split at character level
        parts = []
        for i in range(num_parts):
            start = int(i * target)
            end = int((i + 1) * target) if i < num_parts - 1 else total
            parts.append(text[start:end].strip())
        return [p for p in parts if p]

    cuts: list[int] = []
    prev_cut = 0

    for i in range(1, num_parts):
        ideal = int(i * target)
        window = int(target * 0.35)

        in_window = [
            c for c in candidates
            if ideal - window <= c.pos <= ideal + window
            and c.pos > prev_cut + int(target * 0.2)  # don't cut too close to prev
        ]

        if in_window:
            best = max(in_window, key=lambda c: (c.score, -abs(c.pos - ideal)))
        else:
            # Expand search: nearest candidate after prev_cut
            after_prev = [c for c in candidates if c.pos > prev_cut + 100]
            if after_prev:
                best = min(after_prev, key=lambda c: abs(c.pos - ideal))
            else:
                # Absolute fallback
                best = _SplitCandidate(ideal, 0)

        cuts.append(best.pos)
        prev_cut = best.pos

    # Deduplicate and sort
    cuts = sorted(set(cuts))

    # Build parts
    parts: list[str] = []
    start = 0
    for cut in cuts:
        chunk = text[start:cut].strip()
        if chunk:
            parts.append(chunk)
        start = cut

    tail = text[start:].strip()
    if tail:
        parts.append(tail)

    return parts if parts else [text]
