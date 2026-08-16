"""
Automation for: docs/e2e/06_painel_admin.feature — notícias, carrossel e formulários (@p0)

Shared IDs with the spec:
  [E2E-06-005] … [E2E-06-010]
  tag @e2e-06-XXX  ↔  pytest.mark.e2e_06_XXX  ↔  test_e2e_06_XXX_*

Code identifiers: English. UI assertions and seed content: Portuguese.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.helpers.admin import login_as_master_admin
from tests.e2e.helpers.seed import seed
from tests.e2e.helpers.ui import spotlight


@pytest.mark.e2e
@pytest.mark.e2e_06_005
@seed("auth_users")
def test_e2e_06_005_admin_creates_news_article(page: Page, app_url: str, db):
    """[E2E-06-005] Admin cadastra uma nova notícia"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/noticias/nova/")

    page.locator("#id_title").fill("Nova edição")
    page.locator("#id_slug").fill("nova-edicao")
    page.locator("#id_summary").fill("Resumo da nova edição")
    page.locator("#id_content").fill("Conteúdo completo da nova edição.")
    page.locator("#id_published_at").fill("2026-01-15T10:00")
    page.locator("#id_is_published").check()
    page.get_by_role("button", name="Salvar noticia").click()

    expect(page).to_have_url(f"{app_url}/painel-admin/")
    expect(spotlight(page.get_by_text("Noticia cadastrada com sucesso."))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_06_006
@seed("auth_users")
def test_e2e_06_006_created_news_appears_on_public_list(page: Page, app_url: str, db):
    """[E2E-06-006] Notícia cadastrada aparece na listagem pública quando publicada"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/noticias/nova/")
    page.locator("#id_title").fill("Nova edição")
    page.locator("#id_slug").fill("nova-edicao")
    page.locator("#id_summary").fill("Resumo da nova edição")
    page.locator("#id_content").fill("Conteúdo completo da nova edição.")
    page.locator("#id_published_at").fill("2026-01-15T10:00")
    page.locator("#id_is_published").check()
    page.get_by_role("button", name="Salvar noticia").click()
    expect(page).to_have_url(f"{app_url}/painel-admin/")

    page.goto(f"{app_url}/noticias/")
    expect(spotlight(page.get_by_role("link", name="Nova edição"))).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_06_007
@seed("auth_users")
def test_e2e_06_007_admin_creates_carousel_banner(page: Page, app_url: str, db):
    """[E2E-06-007] Admin cadastra imagem no carrossel"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/carrossel/novo/")

    page.locator("#id_title").fill("Campanha verão")
    page.locator("#id_image_url").fill("https://example.com/campanha-verao.jpg")
    page.locator("#id_sort_order").fill("1")
    page.locator("#id_is_active").check()
    page.get_by_role("button", name="Salvar imagem").click()

    expect(page).to_have_url(f"{app_url}/painel-admin/")
    expect(
        spotlight(page.get_by_text("Imagem do carrossel cadastrada com sucesso."))
    ).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_06_008
@seed("auth_users")
def test_e2e_06_008_created_banner_appears_on_home(page: Page, app_url: str, db):
    """[E2E-06-008] Banner cadastrado aparece na home quando ativo"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/carrossel/novo/")
    page.locator("#id_title").fill("Campanha verão")
    page.locator("#id_image_url").fill("https://example.com/campanha-verao.jpg")
    page.locator("#id_sort_order").fill("1")
    page.locator("#id_is_active").check()
    page.get_by_role("button", name="Salvar imagem").click()
    expect(page).to_have_url(f"{app_url}/painel-admin/")

    page.goto(f"{app_url}/")
    carousel = spotlight(page.locator("#homeCarousel"))
    expect(carousel).to_be_visible()
    expect(carousel.get_by_role("heading", name="Campanha verão")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_06_009
@seed("auth_users")
def test_e2e_06_009_admin_creates_signup_form(page: Page, app_url: str, db):
    """[E2E-06-009] Admin cria formulário de inscrição"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/formularios/novo/")

    page.locator("#id_title").fill("Inscrição 2026")
    page.locator("#id_slug").fill("inscricao-2026")
    page.locator("#id_description").fill("Formulário ativo para o ciclo 2026.")
    page.locator("#id_fields_text").fill("Nome completo|text|required\nEmail|email|required")
    page.locator("#id_is_active").check()
    page.get_by_role("button", name="Salvar formulario").click()

    expect(page).to_have_url(f"{app_url}/painel-admin/")
    expect(
        spotlight(page.get_by_text("Formulario de inscricao criado com sucesso."))
    ).to_be_visible()


@pytest.mark.e2e
@pytest.mark.e2e_06_010
@seed("auth_users")
def test_e2e_06_010_created_signup_form_appears_on_public_list(
    page: Page, app_url: str, db
):
    """[E2E-06-010] Formulário criado aparece na listagem pública de inscrições quando ativo"""
    login_as_master_admin(page, app_url)
    page.goto(f"{app_url}/painel-admin/formularios/novo/")
    page.locator("#id_title").fill("Inscrição 2026")
    page.locator("#id_slug").fill("inscricao-2026")
    page.locator("#id_description").fill("Formulário ativo para o ciclo 2026.")
    page.locator("#id_fields_text").fill("Nome completo|text|required")
    page.locator("#id_is_active").check()
    page.get_by_role("button", name="Salvar formulario").click()
    expect(page).to_have_url(f"{app_url}/painel-admin/")

    page.goto(f"{app_url}/inscreva-se/")
    expect(spotlight(page.get_by_role("heading", name="Inscrição 2026"))).to_be_visible()
