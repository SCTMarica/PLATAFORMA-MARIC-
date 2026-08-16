from __future__ import annotations

from datetime import datetime, timedelta, timezone

import psycopg


def seed_published_news(conn: psycopg.Connection) -> None:
    """Create published news that is visible in the public listing."""
    now = datetime.now(timezone.utc)
    rows = (
        (
            "Abertura do portal",
            "abertura-do-portal",
            "Conheça o novo portal institucional.",
            "O portal está aberto para conectar a população aos serviços.",
            now - timedelta(hours=1),
        ),
        (
            "Programação cultural",
            "programacao-cultural",
            "Agenda cultural da semana.",
            "Confira atividades culturais gratuitas para toda a comunidade.",
            now - timedelta(hours=2),
        ),
    )
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO core_newsarticle (
                created_at, updated_at, title, slug, summary, content,
                cover_image_url, is_featured, is_published, published_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s)
            """,
            [
                (now, now, title, slug, summary, content, "", False, published_at)
                for title, slug, summary, content, published_at in rows
            ],
        )
