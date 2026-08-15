import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_visitor_can_open_home(page: Page, app_url: str, db):
    page.goto(f"{app_url}/")

    expect(page).to_have_title("Plataforma Maric E2E")
    expect(page.get_by_role("main")).to_be_visible()
