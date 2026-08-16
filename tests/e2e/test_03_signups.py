"""
Automation for: docs/e2e/03_inscricoes_contato.feature — inscrições (@p0)

Shared IDs with the spec:
  [E2E-03-001] … [E2E-03-004]
  tag @e2e-03-XXX  ↔  pytest.mark.e2e_03_XXX  ↔  test_e2e_03_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import re
from datetime import date

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.seed import seed
from tests.e2e.helpers.ui import spotlight


def fill_valid_signup(page: Page) -> dict[str, str]:
    """Complete each visible step of the public signup form."""
    values = {
        "nome_completo": "Maria da Silva E2E",
        "email": "maria.e2e@teste.com",
        "telefone": "21999990000",
        "citizen_cpf": "12345678900",
        "citizen_birth_date": "1990-01-15",
        "citizen_nationality": "Brasileira",
        "citizen_mother_name": "Joana da Silva",
        "addr_street": "Rua das Flores",
        "addr_number": "100",
        "addr_district": "Centro",
        "addr_city": "Maricá",
        "addr_state": "RJ",
        "addr_zip": "24900-000",
    }
    for name in (
        "nome_completo",
        "email",
        "telefone",
        "citizen_cpf",
        "citizen_birth_date",
        "citizen_nationality",
        "citizen_mother_name",
    ):
        page.locator(f'[name="{name}"]').fill(values[name])
    page.locator('[name="citizen_race"]').select_option("Parda")
    page.get_by_role("button", name="Avançar").click()

    page.get_by_role("button", name="Avançar").click()

    for name in (
        "addr_street",
        "addr_number",
        "addr_district",
        "addr_city",
        "addr_state",
        "addr_zip",
    ):
        page.locator(f'[name="{name}"]').fill(values[name])
    page.get_by_role("button", name="Avançar").click()

    page.locator("#lgpd_science").check()
    page.locator("#lgpd_purpose").check()
    return values


def submission_data(db, email: str) -> dict | None:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT submission.data
            FROM core_signupsubmission AS submission
            JOIN core_signupform AS form ON form.id = submission.form_id
            WHERE form.slug = 'cadastro-geral'
              AND submission.data->>'email' = %s
            """,
            (email,),
        )
        row = cursor.fetchone()
    return row[0] if row else None


@pytest.mark.e2e
@pytest.mark.e2e_03_001
@seed("signup_forms")
def test_e2e_03_001_visitor_lists_active_signup_forms(page: Page, app_url: str, db):
    """[E2E-03-001] Visitante lista formulários de inscrição ativos"""
    response = page.goto(f"{app_url}/inscreva-se/")
    assert response is not None
    assert response.status == 200

    for title, slug in (
        ("Cadastro geral", "cadastro-geral"),
        ("Oficina comunitária", "oficina-comunitaria"),
    ):
        card = page.locator("article").filter(has=page.get_by_role("heading", name=title))
        expect(spotlight(card)).to_be_visible()
        expect(card.get_by_role("link", name="Abrir formulário")).to_have_attribute(
            "href", f"/inscreva-se/{slug}/"
        )
    expect(page.get_by_text("Encerrado", exact=True)).to_have_count(0)


@pytest.mark.e2e
@pytest.mark.e2e_03_002
@seed("signup_forms")
def test_e2e_03_002_visitor_opens_active_signup_form(page: Page, app_url: str, db):
    """[E2E-03-002] Visitante abre um formulário de inscrição ativo"""
    response = page.goto(f"{app_url}/inscreva-se/cadastro-geral/")
    assert response is not None
    assert response.status == 200

    expect(spotlight(page.get_by_role("heading", name="Cadastro geral"))).to_be_visible()
    expect(page.locator('[name="nome_completo"]')).to_be_visible()
    expect(page.locator('[name="email"]')).to_be_visible()
    expect(page.get_by_role("button", name="Avançar")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_03_003
@seed("signup_forms")
def test_e2e_03_003_visitor_submits_valid_signup_and_receives_registration_id(
    page: Page, app_url: str, db
):
    """[E2E-03-003] Visitante envia inscrição válida e recebe ID de cadastro"""
    page.goto(f"{app_url}/inscreva-se/cadastro-geral/")
    fill_valid_signup(page)
    page.get_by_role("button", name="Confirmar Inscrição").click()

    expect(page).to_have_url(f"{app_url}/inscreva-se/")
    expect(
        spotlight(
            page.get_by_text(re.compile(r"ID de Cadastro é: MARICA-\d{4}-[A-Z0-9]{5}"))
        )
    ).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_03_004
@seed("signup_forms")
def test_e2e_03_004_signup_submission_is_persisted(page: Page, app_url: str, db):
    """[E2E-03-004] Inscrição enviada é persistida no banco"""
    page.goto(f"{app_url}/inscreva-se/cadastro-geral/")
    values = fill_valid_signup(page)
    page.get_by_role("button", name="Confirmar Inscrição").click()

    expect(page).to_have_url(f"{app_url}/inscreva-se/")
    data = submission_data(db, values["email"])
    assert data is not None
    assert data["nome_completo"] == values["nome_completo"]
    assert data["id_cadastro"].startswith(f"MARICA-{date.today().year}-")
