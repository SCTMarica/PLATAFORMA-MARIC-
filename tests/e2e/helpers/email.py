"""Helpers for E2E emails written by Django's file-based backend."""

from __future__ import annotations

import re
from email import policy
from email.parser import BytesParser
from pathlib import Path

PASSWORD_RESET_LINK_RE = re.compile(r"https?://\S+/senha/redefinir/\S+")


def read_outbox(outbox_dir: Path) -> list:
    """Read all messages written during one E2E scenario."""
    return [
        BytesParser(policy=policy.default).parsebytes(message.read_bytes())
        for message in sorted(outbox_dir.glob("*"))
        if message.is_file()
    ]


def password_reset_link(message) -> str:
    """Extract the password reset URL from the plain-text message body."""
    match = PASSWORD_RESET_LINK_RE.search(message.get_body(preferencelist=("plain",)).get_content())
    if match is None:
        raise AssertionError("Password reset email did not contain a reset link.")
    return match.group(0)
