"""
Automation for: docs/e2e/06_painel_admin.feature — branding e cores (@p0)

Shared IDs with the spec:
  [E2E-06-001] … [E2E-06-004]
  tag @e2e-06-XXX  ↔  pytest.mark.e2e_06_XXX  ↔  test_e2e_06_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.admin import (
    login_as_master_admin,
    open_admin_editor,
    save_admin_settings,
)
from tests.e2e.helpers.seed import seed
from tests.e2e.helpers.ui import spotlight


@pytest.mark.e2e
@pytest.mark.e2e_06_001
@seed("auth_users")
def test_e2e_06_001_admin_opens_admin_panel(page: Page, app_url: str, db):
    """[E2E-06-001] Admin acessa o painel administrativo"""
    login_as_master_admin(page, app_url)
    response = page.goto(f"{app_url}/painel-admin/")
    assert response is not None
    assert response.status == 200

    expect(spotlight(page.get_by_role("heading", name="Painel de admin"))).to_be_visible()
    expect(spotlight(page.locator("form.admin-panel__form"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_06_002
@seed("auth_users")
def test_e2e_06_002_admin_updates_general_site_settings(page: Page, app_url: str, db):
    """[E2E-06-002] Admin atualiza configurações gerais do site"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/")

    open_admin_editor(page, section="identity")
    page.locator("#id_site_name").fill("Portal Maricá Config")
    open_admin_editor(page, section="hero")
    page.locator("#id_hero_title").fill("Novo título do hero E2E")
    save_admin_settings(page)

    expect(
        spotlight(page.get_by_text("Conteudo do site atualizado com sucesso."))
    ).to_be_visible()

    page.goto(f"{app_url}/painel-admin/")
    open_admin_editor(page, section="identity")
    expect(page.locator("#id_site_name")).to_have_value("Portal Maricá Config")
    open_admin_editor(page, section="hero")
    expect(page.locator("#id_hero_title")).to_have_value("Novo título do hero E2E")


@pytest.mark.e2e
@pytest.mark.e2e_06_003
@seed("auth_users")
def test_e2e_06_003_branding_changes_appear_on_public_home(
    page: Page, app_url: str, db
):
    """[E2E-06-003] Alterações de branding aparecem na página pública"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/")
    open_admin_editor(page, section="identity")
    page.locator("#id_site_name").fill("Portal Maricá")
    save_admin_settings(page)

    page.goto(f"{app_url}/")
    expect(spotlight(page.get_by_text("Portal Maricá", exact=True).first)).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_06_004
@seed("auth_users")
def test_e2e_06_004_admin_updates_system_colors(page: Page, app_url: str, db):
    """[E2E-06-004] Admin atualiza cores do sistema pelo modal dedicado"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/")

    page.get_by_role("button", name="Cores do sistema").click()
    page.locator("#id_primary_color").fill("#bc202e")
    page.locator("#id_secondary_color").fill("#123456")
    page.locator("#id_accent_color").fill("#abcdef")
    save_admin_settings(page)

    expect(
        spotlight(page.get_by_text("Conteudo do site atualizado com sucesso."))
    ).to_be_visible()

    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT primary_color, secondary_color, accent_color
            FROM core_sitesettings
            ORDER BY id
            LIMIT 1
            """
        )
        row = cursor.fetchone()
    assert row == ("#bc202e", "#123456", "#abcdef")
