from __future__ import annotations

from datetime import datetime, timedelta, timezone

import psycopg


def seed_published_events(conn: psycopg.Connection) -> None:
    """Create published public events for list and detail scenarios."""
    now = datetime.now(timezone.utc)
    rows = (
        (
            "Feira cultural",
            "feira-cultural",
            "Encontro cultural aberto à comunidade.",
            "A feira cultural reúne artistas, gastronomia e atividades para famílias.",
            now + timedelta(days=2, hours=10),
            now + timedelta(days=2, hours=16),
            "Praça Central",
        ),
        (
            "Oficina de cidadania",
            "oficina-de-cidadania",
            "Atividade formativa para moradores.",
            "A oficina aborda participação social e serviços públicos.",
            now + timedelta(days=5, hours=9),
            None,
            "Casa da Cultura",
        ),
    )
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO core_event (
                created_at, updated_at, title, slug, summary, description,
                cover_image_url, start_at, end_at, location, registration_url,
                is_published, published_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s
            )
            """,
            [
                (
                    now,
                    now,
                    title,
                    slug,
                    summary,
                    description,
                    "",
                    start_at,
                    end_at,
                    location,
                    "",
                    now,
                )
                for title, slug, summary, description, start_at, end_at, location in rows
            ],
        )
