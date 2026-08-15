from __future__ import annotations

import os

import pytest

from tests.e2e.db.cleanup import truncate_app_tables
from tests.e2e.db.connection import open_connection
from tests.e2e.db.seeds import seed_baseline


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture
def db():
    """
    One DB connection per test, owned by Playwright.

    Flow:
    1. open connection
    2. truncate app tables
    3. insert seeds
    4. COMMIT so web-e2e can read the data over HTTP
    5. run the test
    6. truncate again (cleanup) and commit

    Why we commit: PostgreSQL never exposes uncommitted rows to another
    connection. The Django process in web-e2e cannot see a rollback-only seed.
    Isolation comes from truncate-before/after, not from leaving a transaction open.
    """
    conn = open_connection()
    try:
        truncate_app_tables(conn)
        seed_baseline(conn)
        conn.commit()
        yield conn
    finally:
        try:
            if not conn.closed:
                conn.rollback()
                truncate_app_tables(conn)
                conn.commit()
        finally:
            conn.close()
