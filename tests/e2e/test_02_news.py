"""
Automation for: docs/e2e/02_noticias_eventos_midia.feature — notícias (@p0)

Shared IDs with the spec:
  [E2E-02-001], [E2E-02-002]
  tag @e2e-02-XXX  ↔  pytest.mark.e2e_02_XXX  ↔  test_e2e_02_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.seed import seed
from tests.e2e.helpers.ui import spotlight


@pytest.mark.e2e
@pytest.mark.e2e_02_001
@seed("published_news")
def test_e2e_02_001_visitor_lists_published_news(page: Page, app_url: str, db):
    """[E2E-02-001] Visitante lista notícias publicadas"""
    response = page.goto(f"{app_url}/noticias/")
    assert response is not None
    assert response.status == 200

    news_grid = spotlight(page.locator(".news-grid"))
    expect(news_grid).to_be_visible()

    for title, slug in (
        ("Abertura do portal", "abertura-do-portal"),
        ("Programação cultural", "programacao-cultural"),
    ):
        article_link = news_grid.get_by_role("link", name=title)
        expect(article_link).to_be_visible()
        expect(article_link).to_have_attribute("href", f"/noticias/{slug}/")


@pytest.mark.e2e
@pytest.mark.e2e_02_002
@seed("published_news")
def test_e2e_02_002_visitor_opens_published_news_detail(
    page: Page, app_url: str, db
):
    """[E2E-02-002] Visitante abre o detalhe de uma notícia publicada"""
    response = page.goto(f"{app_url}/noticias/abertura-do-portal/")
    assert response is not None
    assert response.status == 200

    expect(spotlight(page.get_by_role("heading", name="Abertura do portal"))).to_be_visible()
    expect(
        spotlight(
            page.get_by_text(
                "O portal está aberto para conectar a população aos serviços."
            )
        )
    ).to_be_visible()
