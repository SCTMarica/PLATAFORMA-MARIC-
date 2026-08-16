"""Visual helpers so demo videos show what is being checked."""

from __future__ import annotations

import time

from playwright.sync_api import Locator


def spotlight(locator: Locator, pause_ms: int = 700) -> Locator:
    """
    Highlight an element long enough for the recorded video to show it.

    Uses Playwright's locator.highlight() (debug aid) plus a short pause.
    """
    locator.scroll_into_view_if_needed()
    locator.highlight()
    time.sleep(pause_ms / 1000)
    return locator
