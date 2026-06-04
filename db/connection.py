"""Postgres connection for Neon (DATABASE_URL from Vercel integration)."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row


def database_url() -> str:
    url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
        or ""
    ).strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Run `npx vercel env pull .env.local` after connecting Neon."
        )
    return url


def postgres_enabled() -> bool:
    return bool(
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
    )


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(database_url(), row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
