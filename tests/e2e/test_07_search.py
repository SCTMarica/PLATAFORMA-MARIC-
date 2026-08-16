"""
Automation for: docs/e2e/07_busca_i18n_acessibilidade.feature — busca (@p0)

Shared IDs with the spec:
  [E2E-07-001] … [E2E-07-003]
  tag @e2e-07-XXX  ↔  pytest.mark.e2e_07_XXX  ↔  test_e2e_07_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.seed import seed
from tests.e2e.helpers.ui import spotlight


@pytest.mark.e2e
@pytest.mark.e2e_07_001
@seed("search_content")
def test_e2e_07_001_search_returns_published_news(page: Page, app_url: str, db):
    """[E2E-07-001] Visitante busca conteúdo e vê resultados de notícias"""
    response = page.goto(f"{app_url}/busca/?q=feira")
    assert response is not None
    assert response.status == 200

    news_block = page.locator(".col-12").filter(
        has=page.get_by_role("heading", name="Notícias", exact=True)
    )
    expect(
        spotlight(news_block.get_by_role("heading", name="Feira de ciências"))
    ).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_07_002
@seed("search_content")
def test_e2e_07_002_search_returns_published_events(page: Page, app_url: str, db):
    """[E2E-07-002] Visitante busca conteúdo e vê resultados de eventos"""
    response = page.goto(f"{app_url}/busca/?q=cultural")
    assert response is not None
    assert response.status == 200

    events_block = page.locator(".col-12").filter(
        has=page.get_by_role("heading", name="Eventos", exact=True)
    )
    expect(
        spotlight(events_block.get_by_role("heading", name="Feira cultural"))
    ).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_07_003
@seed("search_content")
def test_e2e_07_003_search_returns_active_signup_forms(page: Page, app_url: str, db):
    """[E2E-07-003] Visitante busca conteúdo e vê resultados de formulários"""
    response = page.goto(f"{app_url}/busca/?q=inscri%C3%A7%C3%A3o")
    assert response is not None
    assert response.status == 200

    forms_block = page.locator(".col-12").filter(
        has=page.get_by_role("heading", name="Inscrições", exact=True)
    )
    expect(
        spotlight(forms_block.get_by_role("heading", name="Inscrição cultural"))
    ).to_be_visible()
