from __future__ import annotations

from datetime import datetime, timedelta, timezone

import psycopg


def seed_search_content(conn: psycopg.Connection) -> None:
    """Deterministic news, event and form titles for public search scenarios."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO core_newsarticle (
                created_at, updated_at, title, slug, summary, content,
                cover_image_url, is_featured, is_published, published_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE, TRUE, %s)
            """,
            (
                now,
                now,
                "Feira de ciências",
                "feira-de-ciencias",
                "Mostra escolar de projetos científicos.",
                "Estudantes apresentam experimentos e pesquisas.",
                "",
                now - timedelta(hours=1),
            ),
        )
        cursor.execute(
            """
            INSERT INTO core_event (
                created_at, updated_at, title, slug, summary, description,
                cover_image_url, start_at, end_at, location, registration_url,
                is_published, published_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, TRUE, %s
            )
            """,
            (
                now,
                now,
                "Feira cultural",
                "feira-cultural",
                "Encontro cultural aberto à comunidade.",
                "Programação cultural com shows e oficinas.",
                "",
                now + timedelta(days=3, hours=10),
                "Praça Central",
                "",
                now,
            ),
        )
        cursor.execute(
            """
            INSERT INTO core_signupform (
                created_at, updated_at, title, slug, description, fields_schema, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, TRUE)
            """,
            (
                now,
                now,
                "Inscrição cultural",
                "inscricao-cultural",
                "Formulário para atividades culturais.",
                "[]",
            ),
        )
