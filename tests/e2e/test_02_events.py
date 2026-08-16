"""
Automation for: docs/e2e/02_noticias_eventos_midia.feature — eventos (@p0)

Shared IDs with the spec:
  [E2E-02-003], [E2E-02-004], [E2E-02-005]
  tag @e2e-02-XXX  ↔  pytest.mark.e2e_02_XXX  ↔  test_e2e_02_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.seed import seed
from tests.e2e.helpers.ui import spotlight


@pytest.mark.e2e
@pytest.mark.e2e_02_003
@seed("published_events")
def test_e2e_02_003_visitor_lists_published_events(page: Page, app_url: str, db):
    """[E2E-02-003] Visitante lista eventos publicados"""
    response = page.goto(f"{app_url}/eventos/")
    assert response is not None
    assert response.status == 200

    for title, slug in (
        ("Feira cultural", "feira-cultural"),
        ("Oficina de cidadania", "oficina-de-cidadania"),
    ):
        event_link = page.get_by_role("link", name=title)
        expect(spotlight(event_link)).to_be_visible()
        expect(event_link).to_have_attribute("href", f"/eventos/{slug}/")


@pytest.mark.e2e
@pytest.mark.e2e_02_004
@seed("published_events")
def test_e2e_02_004_visitor_opens_published_event_detail(
    page: Page, app_url: str, db
):
    """[E2E-02-004] Visitante abre o detalhe de um evento publicado"""
    response = page.goto(f"{app_url}/eventos/feira-cultural/")
    assert response is not None
    assert response.status == 200

    expect(spotlight(page.get_by_role("heading", name="Feira cultural"))).to_be_visible()
    expect(spotlight(page.locator("dd").filter(has_text="Praça Central"))).to_be_visible()
    expect(
        spotlight(
            page.get_by_text(
                "A feira cultural reúne artistas, gastronomia e atividades para famílias."
            )
        )
    ).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_02_005
def test_e2e_02_005_visitor_opens_event_calendar(page: Page, app_url: str, db):
    """[E2E-02-005] Visitante acessa o calendário de eventos"""
    response = page.goto(f"{app_url}/eventos/calendario/")
    assert response is not None
    assert response.status == 200

    expect(
        spotlight(page.get_by_role("heading", name="Calendario de eventos"))
    ).to_be_visible()
    expect(spotlight(page.locator(".event-calendar"))).to_be_visible()
