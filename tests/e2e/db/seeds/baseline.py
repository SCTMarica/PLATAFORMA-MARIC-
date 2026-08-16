from __future__ import annotations

from datetime import datetime, timezone

import psycopg


def seed_baseline(conn: psycopg.Connection) -> None:
    """Minimal deterministic data shared by every E2E scenario."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO core_sitesettings (
                created_at,
                updated_at,
                site_name,
                tagline,
                hero_title,
                hero_subtitle,
                about_title,
                about_content,
                contact_email,
                contact_phone,
                whatsapp,
                address,
                logo_url,
                primary_color,
                secondary_color,
                accent_color,
                footer_text,
                hero_badge,
                hero_button_label,
                hero_panel_title,
                hero_panel_item_1,
                hero_panel_item_2,
                hero_panel_item_3,
                about_home_heading,
                about_home_summary_title,
                about_home_highlight,
                about_home_paragraph_1,
                about_home_paragraph_2,
                about_home_image_url,
                signup_button_label,
                signup_info_title,
                signup_info_text,
                signup_address_title,
                signup_address_text,
                news_eyebrow,
                news_title,
                news_button_label,
                contact_email_destination
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                now,
                now,
                "Plataforma Maric E2E",
                "Ambiente isolado de testes E2E",
                "Plataforma Maric para testes E2E",
                "Dados determinísticos para automação.",
                "Sobre a instituição",
                "Conteúdo institucional do ambiente E2E.",
                "",
                "",
                "",
                "",
                "",
                "#0d6efd",
                "#0b132b",
                "#f59e0b",
                "",
                "Portal institucional",
                "Conheca mais",
                "Pronto para comecar?",
                "",
                "",
                "",
                "Sobre nos",
                "",
                "",
                "",
                "",
                "",
                "Inscreva-se",
                "",
                "",
                "",
                "",
                "Noticias",
                "Ultimas noticias",
                "Ver todas",
                "",
            ),
        )
