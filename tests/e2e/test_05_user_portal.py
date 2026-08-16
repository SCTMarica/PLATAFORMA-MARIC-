"""
Automation for: docs/e2e/05_portal_permissoes.feature — portal e permissões (@p0)

Shared IDs with the spec:
  [E2E-05-001] … [E2E-05-005]
  tag @e2e-05-XXX  ↔  pytest.mark.e2e_05_XXX  ↔  test_e2e_05_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.auth import submit_login_form
from tests.e2e.helpers.seed import seed
from tests.e2e.helpers.ui import spotlight

PASSWORD = "SenhaSegura123!"


def sign_in(page: Page, app_url: str, *, email: str) -> None:
    page.goto(f"{app_url}/login/")
    submit_login_form(page, username=email, password=PASSWORD)


@pytest.mark.e2e
@pytest.mark.e2e_05_001
def test_e2e_05_001_visitor_is_redirected_from_user_portal(
    page: Page, app_url: str, db
):
    """[E2E-05-001] Visitante não autenticado é redirecionado ao tentar abrir o portal"""
    page.goto(f"{app_url}/portal/")

    expect(page).to_have_url(f"{app_url}/login/?next=/portal/")


@pytest.mark.e2e
@pytest.mark.e2e_05_002
@seed("auth_users")
def test_e2e_05_002_authenticated_client_accesses_user_portal(
    page: Page, app_url: str, db
):
    """[E2E-05-002] Cliente autenticado acessa o portal"""
    sign_in(page, app_url, email="cliente@teste.com")
    expect(page).to_have_url(f"{app_url}/portal/")

    response = page.goto(f"{app_url}/portal/")
    assert response is not None
    assert response.status == 200
    expect(spotlight(page.get_by_role("heading", name="Cliente Teste"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_05_003
@seed("auth_users")
def test_e2e_05_003_client_cannot_access_admin_panel(page: Page, app_url: str, db):
    """[E2E-05-003] Cliente final não acessa o painel administrativo"""
    sign_in(page, app_url, email="cliente@teste.com")
    expect(page).to_have_url(f"{app_url}/portal/")

    response = page.goto(f"{app_url}/painel-admin/")
    assert response is not None
    assert response.status == 403
    expect(page.get_by_role("heading", name="Painel de admin")).to_have_count(0)


@pytest.mark.e2e
@pytest.mark.e2e_05_004
@seed("auth_users")
def test_e2e_05_004_supervisor_accesses_admin_panel(page: Page, app_url: str, db):
    """[E2E-05-004] Supervisor acessa o painel administrativo"""
    sign_in(page, app_url, email="supervisor@teste.com")
    expect(page).to_have_url(f"{app_url}/painel-admin/")

    response = page.goto(f"{app_url}/painel-admin/")
    assert response is not None
    assert response.status == 200
    expect(spotlight(page.get_by_role("heading", name="Painel de admin"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_05_005
@seed("auth_users")
def test_e2e_05_005_master_admin_accesses_admin_panel(page: Page, app_url: str, db):
    """[E2E-05-005] Administrador master acessa o painel administrativo"""
    sign_in(page, app_url, email="admin@teste.com")
    expect(page).to_have_url(f"{app_url}/painel-admin/")

    response = page.goto(f"{app_url}/painel-admin/")
    assert response is not None
    assert response.status == 200
    expect(spotlight(page.get_by_role("heading", name="Painel de admin"))).to_be_visible()
