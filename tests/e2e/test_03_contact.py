"""
Automation for: docs/e2e/03_inscricoes_contato.feature — contato (@p0)

Shared IDs with the spec:
  [E2E-03-005] … [E2E-03-007]
  tag @e2e-03-XXX  ↔  pytest.mark.e2e_03_XXX  ↔  test_e2e_03_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.ui import spotlight

CONTACT = {
    "name": "Ana Contato E2E",
    "email": "ana.contato@teste.com",
    "subject": "Dúvida sobre inscrição",
    "message": "Gostaria de mais informações sobre os formulários abertos.",
}


def fill_contact_form(page: Page) -> None:
    page.locator("#id_name").fill(CONTACT["name"])
    page.locator("#id_email").fill(CONTACT["email"])
    page.locator("#id_subject").fill(CONTACT["subject"])
    page.locator("#id_message").fill(CONTACT["message"])


def contact_row(db, email: str) -> tuple | None:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT name, email, subject, message, status
            FROM core_contactmessage
            WHERE lower(email) = lower(%s)
            """,
            (email,),
        )
        return cursor.fetchone()


@pytest.mark.e2e
@pytest.mark.e2e_03_005
def test_e2e_03_005_visitor_opens_contact_page(page: Page, app_url: str, db):
    """[E2E-03-005] Visitante acessa a página de contato"""
    response = page.goto(f"{app_url}/contato/")
    assert response is not None
    assert response.status == 200

    expect(
        spotlight(page.get_by_role("heading", name="Contato institucional"))
    ).to_be_visible()
    form = spotlight(page.locator("#contactForm"))
    expect(form).to_be_visible()
    expect(page.locator("#id_name")).to_be_visible()
    expect(page.locator("#id_email")).to_be_visible()
    expect(page.locator("#id_subject")).to_be_visible()
    expect(page.locator("#id_message")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_03_006
def test_e2e_03_006_visitor_sends_valid_contact_message(page: Page, app_url: str, db):
    """[E2E-03-006] Visitante envia mensagem de contato válida"""
    page.goto(f"{app_url}/contato/")
    fill_contact_form(page)
    page.locator("#contactForm").get_by_role("button").click()

    expect(page).to_have_url(f"{app_url}/contato/")
    expect(
        spotlight(
            page.get_by_text(
                "Mensagem enviada com sucesso! Entraremos em contato em breve."
            )
        )
    ).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_03_007
def test_e2e_03_007_contact_message_is_persisted(page: Page, app_url: str, db):
    """[E2E-03-007] Mensagem de contato é persistida no banco"""
    page.goto(f"{app_url}/contato/")
    fill_contact_form(page)
    page.locator("#contactForm").get_by_role("button").click()

    expect(page).to_have_url(f"{app_url}/contato/")
    row = contact_row(db, CONTACT["email"])
    assert row is not None
    assert row == (
        CONTACT["name"],
        CONTACT["email"],
        CONTACT["subject"],
        CONTACT["message"],
        "new",
    )
