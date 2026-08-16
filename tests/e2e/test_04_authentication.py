"""
Automation for: docs/e2e/04_autenticacao.feature — registration, login and password reset (@p0)

Shared IDs with the spec:
  [E2E-04-001] … [E2E-04-007], [E2E-04-009], [E2E-04-010]
  tag @e2e-04-XXX  ↔  pytest.mark.e2e_04_XXX  ↔  test_e2e_04_XXX_*

Logout via UI (former E2E-04-008) is not automated: the app has no visible
Sair control yet, and product code must not be changed for E2E alone.

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.auth import (
    fill_registration_form,
    submit_login_form,
    submit_new_password,
    submit_password_reset_request,
    submit_registration_form,
)
from tests.e2e.helpers.email import password_reset_link, read_outbox
from tests.e2e.helpers.seed import seed
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


@pytest.mark.e2e
@pytest.mark.e2e_04_003
def test_e2e_04_003_visitor_opens_login_page(page: Page, app_url: str, db):
    """[E2E-04-003] Visitante acessa a tela de login"""
    response = page.goto(f"{app_url}/login/")
    assert response is not None
    assert response.status == 200

    expect(
        spotlight(page.get_by_role("heading", name="Acessar plataforma"))
    ).to_be_visible()
    form = spotlight(page.locator("form").filter(has=page.locator("#id_username")))
    expect(form).to_be_visible()
    expect(page.locator("#id_username")).to_be_visible()
    expect(page.locator("#id_password")).to_be_visible()
    expect(page.get_by_role("button", name="Entrar")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_04_004
@seed("auth_users")
def test_e2e_04_004_client_logs_in_with_email_and_reaches_portal(
    page: Page, app_url: str, db
):
    """[E2E-04-004] Cliente faz login com e-mail e acessa o portal"""
    page.goto(f"{app_url}/login/")
    submit_login_form(
        page, username="cliente@teste.com", password=CLIENT_PASSWORD
    )

    expect(page).to_have_url(f"{app_url}/portal/")
    expect(
        spotlight(page.get_by_text("Acesso realizado com sucesso."))
    ).to_be_visible()
    expect(spotlight(page.get_by_role("heading", name="Cliente Teste"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_04_005
@seed("auth_users")
def test_e2e_04_005_client_logs_in_with_username_and_reaches_portal(
    page: Page, app_url: str, db
):
    """[E2E-04-005] Cliente faz login com nome de usuário e acessa o portal"""
    page.goto(f"{app_url}/login/")
    submit_login_form(
        page, username="cliente.teste", password=CLIENT_PASSWORD
    )

    expect(page).to_have_url(f"{app_url}/portal/")
    expect(
        spotlight(page.get_by_text("Acesso realizado com sucesso."))
    ).to_be_visible()
    expect(spotlight(page.get_by_role("heading", name="Cliente Teste"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_04_006
@seed("auth_users")
def test_e2e_04_006_master_admin_logs_in_and_reaches_admin_panel(
    page: Page, app_url: str, db
):
    """[E2E-04-006] Administrador master faz login e acessa o painel admin"""
    page.goto(f"{app_url}/login/")
    submit_login_form(page, username="admin@teste.com", password=CLIENT_PASSWORD)

    expect(page).to_have_url(f"{app_url}/painel-admin/")
    expect(spotlight(page.get_by_role("heading", name="Painel de admin"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_04_007
@seed("auth_users")
def test_e2e_04_007_supervisor_logs_in_and_reaches_admin_panel(
    page: Page, app_url: str, db
):
    """[E2E-04-007] Supervisor faz login e acessa o painel administrativo"""
    page.goto(f"{app_url}/login/")
    submit_login_form(
        page, username="supervisor@teste.com", password=CLIENT_PASSWORD
    )

    expect(page).to_have_url(f"{app_url}/painel-admin/")
    expect(spotlight(page.get_by_role("heading", name="Painel de admin"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_04_009
@seed("auth_users")
def test_e2e_04_009_user_requests_password_reset_for_registered_email(
    page: Page, app_url: str, db, email_outbox
):
    """[E2E-04-009] Usuário solicita recuperação de senha com e-mail cadastrado"""
    page.goto(f"{app_url}/senha/recuperar/")
    submit_password_reset_request(page, email="cliente@teste.com")

    expect(page).to_have_url(f"{app_url}/senha/recuperar/enviado/")
    messages = read_outbox(email_outbox)
    assert len(messages) == 1
    assert messages[0]["to"] == "cliente@teste.com"
    assert password_reset_link(messages[0]).startswith(f"{app_url}/senha/redefinir/")


@pytest.mark.e2e
@pytest.mark.e2e_04_010
@seed("auth_users")
def test_e2e_04_010_user_resets_password_with_valid_link(
    page: Page, app_url: str, db, email_outbox
):
    """[E2E-04-010] Usuário redefine a senha pelo link válido"""
    page.goto(f"{app_url}/senha/recuperar/")
    submit_password_reset_request(page, email="cliente@teste.com")

    messages = read_outbox(email_outbox)
    assert len(messages) == 1
    page.goto(password_reset_link(messages[0]))
    expect(spotlight(page.get_by_role("heading", name="Redefinir senha"))).to_be_visible()

    submit_new_password(page, password="NovaSenha123!")

    expect(page).to_have_url(f"{app_url}/senha/redefinir/concluido/")
    expect(spotlight(page.get_by_role("heading", name="Senha redefinida"))).to_be_visible()
