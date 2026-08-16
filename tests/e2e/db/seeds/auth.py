from __future__ import annotations

from datetime import datetime, timezone

import psycopg

E2E_PASSWORD = "SenhaSegura123!"
E2E_PASSWORD_HASH = (
    "pbkdf2_sha256$1000000$hs8tTe1810L3IFW0rnbZHE$"
    "PrQbZSBkVCTEl3tDrzSdt4ghwNHe9xaOymU2anmh74I="
)


def seed_auth_users(conn: psycopg.Connection) -> None:
    """Create deterministic accounts for login and logout scenarios."""
    now = datetime.now(timezone.utc)
    users = (
        (
            "cliente.teste",
            "cliente@teste.com",
            "Cliente",
            "Teste",
            "cliente_final",
            False,
            False,
        ),
        (
            "admin.teste",
            "admin@teste.com",
            "Administrador",
            "Teste",
            "administrador_master",
            True,
            True,
        ),
        (
            "supervisor.teste",
            "supervisor@teste.com",
            "Supervisor",
            "Teste",
            "supervisor_coordenador",
            True,
            False,
        ),
    )
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO core_user (
                username, email, password, first_name, last_name, role,
                phone, is_active, is_staff, is_superuser, date_joined
            ) VALUES (%s, %s, %s, %s, %s, %s, '', TRUE, %s, %s, %s)
            """,
            [
                (*user[:2], E2E_PASSWORD_HASH, *user[2:], now)
                for user in users
            ],
        )
