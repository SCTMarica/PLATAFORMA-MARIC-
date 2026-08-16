"""
Automation for: docs/e2e/04_autenticacao.feature — cadastro de usuário (@p0)

Shared IDs with the spec:
  [E2E-04-001], [E2E-04-002]
  tag @e2e-04-XXX  ↔  pytest.mark.e2e_04_XXX  ↔  test_e2e_04_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.auth import fill_registration_form, submit_registration_form
from tests.e2e.helpers.ui import spotlight

CLIENT_PASSWORD = "SenhaSegura123!"


def _user_role_by_email(db, email: str) -> str | None:
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT role FROM core_user WHERE lower(email) = lower(%s)",
            (email,),
        )
        row = cursor.fetchone()
    return row[0] if row else None


@pytest.mark.e2e
@pytest.mark.e2e_04_001
def test_e2e_04_001_visitor_opens_registration_page(page: Page, app_url: str, db):
    """[E2E-04-001] Visitante acessa a tela de cadastro"""
    response = page.goto(f"{app_url}/cadastro/")
    assert response is not None
    assert response.status == 200

    heading = spotlight(page.get_by_role("heading", name="Criar cadastro"))
    expect(heading).to_be_visible()

    form = spotlight(page.locator("form").filter(has=page.locator("#id_full_name")))
    expect(form).to_be_visible()
    expect(page.locator("#id_full_name")).to_be_visible()
    expect(page.locator("#id_email")).to_be_visible()
    expect(page.locator("#id_phone")).to_be_visible()
    expect(page.locator("#id_password")).to_be_visible()
    expect(page.locator("#id_confirm_password")).to_be_visible()
    expect(page.get_by_role("button", name="Cadastrar")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_04_002
def test_e2e_04_002_visitor_registers_as_client_and_reaches_portal(
    page: Page, app_url: str, db
):
    """[E2E-04-002] Visitante se cadastra como cliente final e acessa o portal"""
    email = "cliente@teste.com"
    assert _user_role_by_email(db, email) is None

    page.goto(f"{app_url}/cadastro/")
    fill_registration_form(
        page,
        full_name="Cliente Teste E2E",
        email=email,
        phone="21999990000",
        password=CLIENT_PASSWORD,
    )
    submit_registration_form(page)

    expect(page).to_have_url(f"{app_url}/portal/")
    expect(
        spotlight(page.get_by_text("Cadastro concluído. Seu acesso já está ativo."))
    ).to_be_visible()
    expect(spotlight(page.get_by_text("Cliente final"))).to_be_visible()
    expect(spotlight(page.get_by_role("heading", name="Cliente Teste E2E"))).to_be_visible()

    assert _user_role_by_email(db, email) == "cliente_final"
