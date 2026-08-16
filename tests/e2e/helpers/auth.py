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
