#!/usr/bin/env python3
"""Apply db/schema.sql to Neon. Run from repo root."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT / ".env.local")

from db.connection import get_connection  # noqa: E402


def main() -> None:
    schema_path = _ROOT / "db" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    print(f"Applied schema from {schema_path}")


if __name__ == "__main__":
    main()
