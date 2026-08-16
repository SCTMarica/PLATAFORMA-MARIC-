"""Declarative scenario seeds for E2E tests.

Usage:

    from tests.e2e.db.seeds import seed_home_banners
    from tests.e2e.helpers.seed import seed

    @seed(seed_home_banners)
    def test_...(page, app_url, db):
        ...

    # or by registered name:
    @seed("home_banners", "home_news")
    def test_...(page, app_url, db):
        ...
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from tests.e2e.db.seeds import seed_auth_users, seed_home_banners, seed_home_news

SeedFn = Callable[[Any], None]

SEED_REGISTRY: dict[str, SeedFn] = {
    "auth_users": seed_auth_users,
    "home_banners": seed_home_banners,
    "home_news": seed_home_news,
}


def seed(*seeds: str | SeedFn):
    """
    Mark a test to load extra seeds after the baseline, before the test body.

    The `db` fixture applies these and commits once so web-e2e can read them.
    """
    if not seeds:
        raise ValueError("@seed(...) requires at least one seed name or callable")
    return pytest.mark.seed(*seeds)


def resolve_seed(entry: str | SeedFn) -> SeedFn:
    if callable(entry):
        return entry
    try:
        return SEED_REGISTRY[entry]
    except KeyError as exc:
        known = ", ".join(sorted(SEED_REGISTRY))
        raise KeyError(
            f"Unknown seed {entry!r}. Register it in SEED_REGISTRY or pass the "
            f"callable. Known names: {known}"
        ) from exc


def apply_marked_seeds(item: pytest.Item, conn) -> bool:
    """
    Run all @seed(...) / @pytest.mark.seed(...) entries for the test item.

    Returns True if any seed was applied (caller should commit).
    """
    applied = False
    for mark in item.iter_markers("seed"):
        if mark.kwargs:
            raise TypeError(
                "@seed / pytest.mark.seed only accepts positional seed names "
                f"or callables, got kwargs={mark.kwargs!r}"
            )
        for entry in mark.args:
            resolve_seed(entry)(conn)
            applied = True
    return applied
