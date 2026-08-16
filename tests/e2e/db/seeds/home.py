from __future__ import annotations

from datetime import datetime, timedelta, timezone

import psycopg


def seed_home_banners(conn: psycopg.Connection) -> None:
    now = datetime.now(timezone.utc)
    rows = [
        ("Banner ativo 1", "banner", "Primeiro banner", "https://example.com/banner-1.jpg", 1, True),
        ("Banner ativo 2", "banner", "Segundo banner", "https://example.com/banner-2.jpg", 2, True),
        ("Banner inativo", "banner", "Não deve aparecer", "https://example.com/banner-off.jpg", 3, False),
    ]
    with conn.cursor() as cursor:
        for title, media_type, description, image_url, sort_order, is_active in rows:
            cursor.execute(
                """
                INSERT INTO core_mediaitem (
                    created_at, updated_at, title, media_type, description,
                    image_url, video_url, external_url, sort_order, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (now, now, title, media_type, description, image_url, "", "", sort_order, is_active),
            )


def seed_home_news(conn: psycopg.Connection) -> None:
    now = datetime.now(timezone.utc)
    rows = [
        (
            "Notícia destaque publicada",
            "noticia-destaque-publicada",
            "Resumo da notícia em destaque",
            "Conteúdo da notícia em destaque",
            True,
            True,
            now - timedelta(hours=1),
        ),
        (
            "Notícia rascunho oculta",
            "noticia-rascunho-oculta",
            "Resumo do rascunho",
            "Conteúdo do rascunho",
            True,
            False,
            now - timedelta(hours=2),
        ),
    ]
    with conn.cursor() as cursor:
        for title, slug, summary, content, is_featured, is_published, published_at in rows:
            cursor.execute(
                """
                INSERT INTO core_newsarticle (
                    created_at, updated_at, title, slug, summary, content,
                    cover_image_url, is_featured, is_published, published_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    now,
                    now,
                    title,
                    slug,
                    summary,
                    content,
                    "",
                    is_featured,
                    is_published,
                    published_at,
                ),
            )


def seed_home_events(conn: psycopg.Connection) -> None:
    now = datetime.now(timezone.utc)
    rows = [
        (
            "Evento publicado futuro",
            "evento-publicado-futuro",
            "Resumo do evento publicado",
            "Descrição do evento publicado",
            now + timedelta(days=3),
            True,
            now,
        ),
        (
            "Evento oculto",
            "evento-oculto",
            "Resumo do evento oculto",
            "Descrição do evento oculto",
            now + timedelta(days=5),
            False,
            now,
        ),
    ]
    with conn.cursor() as cursor:
        for title, slug, summary, description, start_at, is_published, published_at in rows:
            cursor.execute(
                """
                INSERT INTO core_event (
                    created_at, updated_at, title, slug, summary, description,
                    cover_image_url, start_at, end_at, location, registration_url,
                    is_published, published_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    now,
                    now,
                    title,
                    slug,
                    summary,
                    description,
                    "",
                    start_at,
                    None,
                    "Centro de Maricá",
                    "",
                    is_published,
                    published_at,
                ),
            )
