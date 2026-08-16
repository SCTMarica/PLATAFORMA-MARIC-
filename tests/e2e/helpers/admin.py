"""UI helpers for the admin panel."""

from __future__ import annotations

from playwright.sync_api import Page

from tests.e2e.helpers.auth import submit_login_form

ADMIN_PASSWORD = "SenhaSegura123!"


def login_as_master_admin(page: Page, app_url: str) -> None:
    page.goto(f"{app_url}/login/")
    submit_login_form(page, username="admin@teste.com", password=ADMIN_PASSWORD)


def open_admin_editor(page: Page, *, section: str) -> None:
    page.evaluate(
        """
        (section) => {
          const drawer = document.getElementById("home-editor-drawer");
          const title = document.getElementById("home-editor-title");
          const panels = Array.from(document.querySelectorAll("[data-editor-panel]"));
          const labels = {
            hero: "Destaque principal",
            identity: "Identidade e cabeçalho",
            general: "Configurações gerais",
            colors: "Cores do sistema",
          };
          panels.forEach((panel) => {
            panel.hidden = panel.dataset.editorPanel !== section;
          });
          if (title) {
            title.textContent = labels[section] || "Página inicial";
          }
          drawer.classList.add("is-open");
          drawer.setAttribute("aria-hidden", "false");
          document.body.classList.add("drawer-open");
        }
        """,
        section,
    )


def save_admin_settings(page: Page) -> None:
    page.locator(".home-editor-drawer__actions").get_by_role(
        "button", name="Salvar alterações"
    ).click()
