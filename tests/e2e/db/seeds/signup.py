from __future__ import annotations

from datetime import datetime, timezone

import psycopg


def seed_signup_forms(conn: psycopg.Connection) -> None:
    """Create active and inactive forms for public signup scenarios."""
    now = datetime.now(timezone.utc)
    rows = (
        (
            "Cadastro geral",
            "cadastro-geral",
            "Inscrição geral para atividades institucionais.",
            True,
        ),
        (
            "Oficina comunitária",
            "oficina-comunitaria",
            "Inscrição para a oficina comunitária.",
            True,
        ),
        ("Encerrado", "encerrado", "Formulário indisponível.", False),
    )
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO core_signupform (
                created_at, updated_at, title, slug, description, fields_schema, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)
            """,
            [(now, now, title, slug, description, "[]", is_active) for title, slug, description, is_active in rows],
        )
