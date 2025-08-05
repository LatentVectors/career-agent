"""Utilities for parsing and formatting experience Markdown files with YAML front-matter."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import frontmatter  # type: ignore[import-untyped]
from pydantic import ValidationError

from src.resume.types import Experience


def parse_experience_file(text: str) -> Tuple[Experience, str]:
    """Parse a Markdown experience file into (``Experience``, body).

    The input **must** start with a valid YAML front-matter block delimited by
    ``---``.  If the front-matter is missing or cannot be parsed, a
    ``ValueError`` is raised.
    """

    # ------------------------------------------------------------------
    # 1. Ensure the file actually contains YAML front-matter
    # ------------------------------------------------------------------
    if not text.lstrip().startswith("---"):
        raise ValueError("Missing YAML front-matter in experience file")

    # ------------------------------------------------------------------
    # 2. Parse the file with *python-frontmatter*
    # ------------------------------------------------------------------
    try:
        post = frontmatter.loads(text)
        data: dict = post.metadata or {}
    except Exception as exc:  # pragma: no cover – rely on unit-tests instead
        raise ValueError("Invalid YAML front-matter in experience file") from exc

    # ------------------------------------------------------------------
    # 3. Normalise values for Pydantic validation
    # ------------------------------------------------------------------
    import datetime

    if isinstance(data.get("start_date"), datetime.date):
        data["start_date"] = data["start_date"].isoformat()
    if isinstance(data.get("end_date"), datetime.date):
        data["end_date"] = data["end_date"].isoformat()

    # Provide defaults for optional fields
    data.setdefault("title", "")
    data.setdefault("company", "")
    data.setdefault("location", "")
    data.setdefault("start_date", "")
    data.setdefault("end_date", "")
    data.setdefault("points", [])

    # ------------------------------------------------------------------
    # 4. Validate against the Experience schema
    # ------------------------------------------------------------------
    try:
        exp = Experience.model_validate(data)
    except ValidationError as exc:  # pragma: no cover – easier debugging
        raise ValueError("Experience metadata failed validation") from exc

    return exp, post.content


def format_experience(exp: Experience, body: str) -> str:
    """Render an :class:`Experience` plus *body* into a Markdown string."""

    # Only include non-empty fields in the YAML
    data = exp.model_dump(mode="json")
    filtered_data = {k: v for k, v in data.items() if v not in ("", [], None)}

    # Use python-frontmatter to format the post (front & body)
    post = frontmatter.Post(body, **filtered_data)
    result: str = frontmatter.dumps(post)

    # ------------------------------------------------------------------
    # Post-process YAML to remove unnecessary single-quotes that PyYAML
    # adds around date-like strings (e.g. '2020-01-15').  We keep the
    # transformation *generic* so the behaviour is data-independent and
    # we do **not** need to update the code whenever test fixtures change.
    # ------------------------------------------------------------------
    import re

    # Replace **single-quoted** ISO-8601 dates – only within the YAML
    # front-matter block to avoid touching the body.
    def _strip_yaml_quotes(text: str) -> str:
        """Return *text* with single-quotes around YYYY-MM-DD removed."""

        pattern = re.compile(r"^(?P<key>\s*\w+:)\s*'(?P<date>\d{4}-\d{2}-\d{2})'$", re.MULTILINE)
        return pattern.sub(lambda m: f"{m.group('key')} {m.group('date')}", text)

    # Split on the first two '---' delimiters to isolate YAML.
    parts = result.split("---", 2)
    if len(parts) >= 3:
        parts[1] = _strip_yaml_quotes(parts[1])  # only transform YAML section
        result = "---".join(parts)
    else:  # pragma: no cover – safeguard; should never happen
        result = _strip_yaml_quotes(result)

    # Ensure the output always ends with a trailing newline so that
    # tests (and typical POSIX tools) treat the final line correctly.
    if not result.endswith("\n"):
        result += "\n"

    return result


# Convenience helpers -------------------------------------------------------


def read_experience_file(path: Path) -> Tuple[Experience, str]:
    text = path.read_text()
    return parse_experience_file(text)


def write_experience_file(path: Path, exp: Experience, body: str) -> None:
    formatted = format_experience(exp, body)
    path.write_text(formatted)
