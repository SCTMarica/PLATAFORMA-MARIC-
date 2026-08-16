from __future__ import annotations

import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from tests.e2e.db.cleanup import truncate_app_tables
from tests.e2e.db.connection import open_connection
from tests.e2e.db.seeds import seed_baseline
from tests.e2e.helpers.artifacts import (
    portuguese_title_from_item,
    scenario_folder_from_item,
    scenario_id_from_item,
)
from tests.e2e.helpers.seed import apply_marked_seeds
from tests.e2e.helpers.video import (
    INTRO_FILE,
    RAW_VIDEO_FILE,
    RESULT_FILE,
    attach_cards,
    render_card,
)

TITLE_BACKGROUND = "#0b132b"
SCENARIO_MARK_RE = re.compile(r"^e2e_(\d+)_(\d+)$")
EMAIL_OUTBOX_DIR = Path("test-results/e2e-mail-outbox")


def evidence_enabled(config) -> bool:
    """True only when video recording was requested explicitly."""
    return config.getoption("--video") == "on"


def pytest_configure(config):
    """Route artifacts: timestamped under test-results/ only when recording."""
    if evidence_enabled(config):
        run_id = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d_%H-%M-%S")
        run_dir = Path("test-results") / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        config.option.output = str(run_dir)
        config._e2e_run_dir = run_dir  # noqa: SLF001
        (run_dir / "README.txt").write_text(
            f"E2E run started at {run_id}\n"
            "Each subfolder contains the ID and a filesystem-safe Portuguese name.\n",
            encoding="utf-8",
        )
        return

    # Quiet runs must not create project test-results/ folders.
    quiet_dir = Path(tempfile.mkdtemp(prefix="plataforma-maric-e2e-quiet-"))
    config.option.output = str(quiet_dir)
    config._e2e_quiet_dir = quiet_dir  # noqa: SLF001


def pytest_sessionfinish(session, exitstatus):
    quiet_dir = getattr(session.config, "_e2e_quiet_dir", None)
    if quiet_dir is not None:
        shutil.rmtree(quiet_dir, ignore_errors=True)
        return

    run_dir = getattr(session.config, "_e2e_run_dir", None)
    if run_dir is None:
        return

    # Playwright writes WebM; attach_cards emits the final shareable MP4.
    for video in sorted(Path(run_dir).glob(f"*/{RAW_VIDEO_FILE}")):
        attach_cards(video.parent)


def pytest_collection_modifyitems(items):
    """Reject new E2E tests without the metadata used in evidence videos."""
    errors = []
    for item in items:
        scenario_marks = [
            mark.name for mark in item.iter_markers() if SCENARIO_MARK_RE.match(mark.name)
        ]
        if len(scenario_marks) != 1:
            errors.append(
                f"{item.nodeid}: informe exatamente um marcador e2e_XX_XXX"
            )
            continue

        scenario_id = scenario_id_from_item(item)
        raw_title = (getattr(item.function, "__doc__", None) or "").strip()
        if not raw_title.startswith(f"[{scenario_id}] "):
            errors.append(
                f"{item.nodeid}: adicione uma docstring em português iniciada por "
                f"'[{scenario_id}] '"
            )

    if errors:
        raise pytest.UsageError(
            "Metadados obrigatórios dos testes E2E:\n- " + "\n- ".join(errors)
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose each test phase result to fixtures during teardown."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"report_{report.when}", report)


@pytest.fixture
def output_path(pytestconfig, request) -> str:
    """
    Override pytest-playwright default slug folders.

    Result:
      test-results/2026-08-15_21-58-00/
        E2E-01-001_visitante-acessa-a-pagina-inicial/
    """
    run_dir = Path(pytestconfig.getoption("--output")).resolve()
    scenario_dir = run_dir / scenario_folder_from_item(request.node)
    scenario_dir.mkdir(parents=True, exist_ok=True)
    return str(scenario_dir)


def _portuguese_heading(item) -> str:
    scenario_id = scenario_id_from_item(item)
    title = portuguese_title_from_item(item)
    return re.sub(rf"^\[{re.escape(scenario_id)}\]\s*", "", title, flags=re.IGNORECASE).strip() or title


def _result_card(item) -> tuple[str, str, str]:
    report = getattr(item, "report_call", None)
    if report is not None and report.passed:
        return "APROVADO", "Todas as verificações deste teste passaram.", "#146c43"
    if report is not None and getattr(report, "wasxfail", None):
        return (
            "REPROVADO",
            "Falha conhecida e esperada: funcionalidade ainda pendente.",
            "#b02a37",
        )
    if report is not None and report.skipped:
        return "NÃO EXECUTADO", "O teste foi ignorado durante esta execução.", "#5c636a"
    return "REPROVADO", "Uma ou mais verificações deste teste falharam.", "#b02a37"


@pytest.fixture(autouse=True)
def portuguese_title_card(page, browser, request, pytestconfig):
    """
    Prepare the Portuguese intro card and the result card for the video.

    Cards are rendered in a separate, non-recorded context and joined around
    the recording by ffmpeg at the end of the session. The test footage itself
    is never covered or trimmed.

    Only runs when `--video on` was requested (make e2e-video / e2e-demo).
    """
    if not evidence_enabled(pytestconfig):
        yield
        return

    scenario_id = scenario_id_from_item(request.node)
    scenario_dir = Path(request.getfixturevalue("output_path"))
    render_card(
        browser,
        scenario_dir / INTRO_FILE,
        scenario_id,
        _portuguese_heading(request.node),
        "Iniciando teste automatizado",
        TITLE_BACKGROUND,
    )
    yield

    if not page.is_closed():
        page.screenshot(path=str(scenario_dir / "pagina-final.png"), type="png")

    heading, detail, background = _result_card(request.node)
    render_card(browser, scenario_dir / RESULT_FILE, scenario_id, heading, detail, background)


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Match the application default language (pt)."""
    return {
        **browser_context_args,
        "locale": "pt-BR",
        "extra_http_headers": {"Accept-Language": "pt-BR,pt;q=0.9"},
    }


@pytest.fixture
def db(request):
    """
    One DB connection per test, owned by Playwright.

    Flow:
    1. open connection
    2. truncate app tables
    3. apply baseline seed
    4. apply any @seed(...) marked on the test
    5. COMMIT so web-e2e can read the data over HTTP
    6. run the test
    7. truncate again and commit

    Why we commit: PostgreSQL never exposes uncommitted rows to another
    connection. Isolation comes from truncate-before/after, not from leaving
    a transaction open.
    """
    conn = open_connection()
    try:
        truncate_app_tables(conn)
        seed_baseline(conn)
        apply_marked_seeds(request.node, conn)
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


@pytest.fixture
def email_outbox():
    """Empty the E2E mail outbox before and after a scenario."""
    EMAIL_OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    for message in EMAIL_OUTBOX_DIR.iterdir():
        if message.is_file():
            message.unlink()
    yield EMAIL_OUTBOX_DIR
    for message in EMAIL_OUTBOX_DIR.iterdir():
        if message.is_file():
            message.unlink()
