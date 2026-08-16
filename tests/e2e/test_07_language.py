"""
Automation for: docs/e2e/07_busca_i18n_acessibilidade.feature — idioma (@p0)

Shared IDs with the spec:
  [E2E-07-004], [E2E-07-005]
  tag @e2e-07-XXX  ↔  pytest.mark.e2e_07_XXX  ↔  test_e2e_07_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.ui import spotlight


def switch_language(page: Page, *, code: str) -> None:
    page.locator("form.language-switcher").get_by_role(
        "button", name=code.upper()
    ).click()


@pytest.mark.e2e
@pytest.mark.e2e_07_004
def test_e2e_07_004_visitor_switches_site_language(page: Page, app_url: str, db):
    """[E2E-07-004] Visitante troca o idioma do site"""
    page.goto(f"{app_url}/")
    switch_language(page, code="en")

    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(
        spotlight(page.locator("form.language-switcher button.is-active"))
    ).to_have_text("EN")
    page.goto(f"{app_url}/sobre/")
    expect(spotlight(page.get_by_role("heading", name="About us"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_07_005
def test_e2e_07_005_selected_language_persists_across_navigation(
    page: Page, app_url: str, db
):
    """[E2E-07-005] Idioma selecionado permanece na sessão ao navegar"""
    page.goto(f"{app_url}/")
    switch_language(page, code="en")
    expect(page.locator("html")).to_have_attribute("lang", "en")

    page.goto(f"{app_url}/sobre/")
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(
        spotlight(page.locator("form.language-switcher button.is-active"))
    ).to_have_text("EN")
