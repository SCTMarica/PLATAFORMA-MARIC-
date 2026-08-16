"""UI helpers for authentication flows."""

from __future__ import annotations

from playwright.sync_api import Page


def fill_registration_form(
    page: Page,
    *,
    full_name: str,
    email: str,
    phone: str,
    password: str,
) -> None:
    page.locator("#id_full_name").fill(full_name)
    page.locator("#id_email").fill(email)
    page.locator("#id_phone").fill(phone)
    page.locator("#id_password").fill(password)
    page.locator("#id_confirm_password").fill(password)


def submit_registration_form(page: Page) -> None:
    page.get_by_role("button", name="Cadastrar").click()


def submit_login_form(page: Page, *, username: str, password: str) -> None:
    page.locator("#id_username").fill(username)
    page.locator("#id_password").fill(password)
    page.get_by_role("button", name="Entrar").click()


def submit_password_reset_request(page: Page, *, email: str) -> None:
    page.locator("#id_email").fill(email)
    page.get_by_role("button", name="Enviar link").click()


def submit_new_password(page: Page, *, password: str) -> None:
    page.locator("#id_new_password1").fill(password)
    page.locator("#id_new_password2").fill(password)
    page.get_by_role("button", name="Salvar nova senha").click()
