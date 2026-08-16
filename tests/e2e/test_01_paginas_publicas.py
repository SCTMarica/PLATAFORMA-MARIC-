"""
Automation for: docs/e2e/01_paginas_publicas.feature

Shared IDs with the spec:
  [E2E-01-001], [E2E-01-002], [E2E-01-003], [E2E-01-007]
  tag @e2e-01-XXX  ↔  pytest.mark.e2e_01_XXX  ↔  test_e2e_01_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.seed import seed
from tests.e2e.helpers.ui import spotlight


@pytest.mark.e2e
@pytest.mark.e2e_01_001
def test_e2e_01_001_visitor_opens_home(page: Page, app_url: str, db):
    """[E2E-01-001] Visitante acessa a página inicial"""
    response = page.goto(f"{app_url}/")
    assert response is not None
    assert response.status == 200

    expect(page).to_have_title("Plataforma Maric E2E")
    expect(page.locator("html")).to_have_attribute("lang", "pt")

    header = spotlight(page.locator("header, .site-header, nav.navbar").first)
    expect(header).to_be_visible()

    main = spotlight(page.get_by_role("main"))
    expect(main).to_be_visible()

    footer = spotlight(page.locator("footer.site-footer"))
    expect(footer).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_01_002
@seed("home_banners")
def test_e2e_01_002_home_shows_active_banners_only(page: Page, app_url: str, db):
    """[E2E-01-002] Página inicial exibe banners ativos do carrossel"""
    page.goto(f"{app_url}/")

    carousel = spotlight(page.locator("#homeCarousel"))
    expect(carousel).to_be_visible()

    active_banner = spotlight(carousel.get_by_role("heading", name="Banner ativo 1"))
    expect(active_banner).to_be_visible()
    expect(carousel.get_by_text("Banner inativo")).to_have_count(0)


@pytest.mark.e2e
@pytest.mark.e2e_01_003
@seed("home_news")
def test_e2e_01_003_home_shows_published_featured_news(page: Page, app_url: str, db):
    """[E2E-01-003] Página inicial exibe notícias em destaque publicadas"""
    page.goto(f"{app_url}/")

    news = spotlight(page.get_by_role("heading", name="Notícia destaque publicada"))
    expect(news).to_be_visible()
    expect(page.get_by_text("Notícia rascunho oculta")).to_have_count(0)


@pytest.mark.e2e
@pytest.mark.e2e_01_007
def test_e2e_01_007_visitor_opens_about_page(page: Page, app_url: str, db):
    """[E2E-01-007] Visitante acessa a página Sobre"""
    response = page.goto(f"{app_url}/sobre/")
    assert response is not None
    assert response.status == 200

    expect(page.locator("html")).to_have_attribute("lang", "pt")

    about = spotlight(page.locator("section.about"))
    expect(about).to_be_visible()

    heading = spotlight(page.get_by_role("heading", name="Quem somos"))
    expect(heading).to_be_visible()
