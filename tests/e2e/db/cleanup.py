from __future__ import annotations

import psycopg

# Application tables only. Keep django_migrations / contenttypes / permissions.
APP_TABLES = (
    "core_signupsubmission",
    "core_contactmessage",
    "core_signupform",
    "core_newsarticle",
    "core_event",
    "core_mediaitem",
    "core_sociallink",
    "core_sitesettings",
    "core_user_groups",
    "core_user_user_permissions",
    "core_user",
    "django_session",
    "django_admin_log",
)


def truncate_app_tables(conn: psycopg.Connection) -> None:
    tables = ", ".join(APP_TABLES)
    with conn.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE")
