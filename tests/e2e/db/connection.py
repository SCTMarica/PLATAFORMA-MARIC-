from __future__ import annotations

import os
from urllib.parse import urlparse

import psycopg


def database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is required for E2E database access.")

    database_name = urlparse(url).path.lstrip("/")
    if not database_name.endswith("_e2e"):
        raise RuntimeError(
            f"Refusing to use database '{database_name}'. E2E seeds only target *_e2e."
        )
    return url


def open_connection() -> psycopg.Connection:
    """Open one connection per test. Autocommit stays off until we decide to persist."""
    return psycopg.connect(database_url(), autocommit=False)
