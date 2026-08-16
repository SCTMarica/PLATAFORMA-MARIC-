from __future__ import annotations

import re
import unicodedata

import pytest


_SCENARIO_MARK_RE = re.compile(r"^e2e_(\d+)_(\d+)$")


def scenario_id_from_item(item: pytest.Item) -> str:
    """
    Resolve E2E-01-001 from pytest marks or the test function name.
    """
    for mark in item.iter_markers():
        match = _SCENARIO_MARK_RE.match(mark.name)
        if match:
            return f"E2E-{match.group(1)}-{match.group(2)}"

    match = re.search(r"e2e_(\d+)_(\d+)", item.name)
    if match:
        return f"E2E-{match.group(1)}-{match.group(2)}"

    return item.name


def portuguese_title_from_item(item: pytest.Item) -> str:
    doc = (getattr(item.function, "__doc__", None) or "").strip()
    if doc:
        return " ".join(doc.split())
    return item.name


def scenario_folder_from_item(item: pytest.Item) -> str:
    """Build a readable, filesystem-safe folder name in Portuguese."""
    scenario_id = scenario_id_from_item(item)
    title = portuguese_title_from_item(item)
    title_without_id = re.sub(
        rf"^\[{re.escape(scenario_id)}\]\s*",
        "",
        title,
        flags=re.IGNORECASE,
    )
    ascii_title = unicodedata.normalize("NFKD", title_without_id).encode(
        "ascii", "ignore"
    ).decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    return f"{scenario_id}_{slug}" if slug else scenario_id
