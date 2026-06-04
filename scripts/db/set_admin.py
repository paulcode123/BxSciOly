#!/usr/bin/env python3
"""Set admin_status for a member by DOE email. Usage: python scripts/db/set_admin.py email@nycstudents.net full"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT / ".env.local")

from db import members as members_db  # noqa: E402


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python scripts/db/set_admin.py <doeEmail> <none|full|EM|SD/BD>")
        sys.exit(1)
    email, status = sys.argv[1], sys.argv[2]
    row = members_db.find_by_doe_email(email)
    if not row:
        print(f"No member found for {email}")
        sys.exit(1)
    members_db.update(row["id"], {"adminStatus": status}, merge=True)
    print(f"Updated {row['id']} adminStatus -> {status}")


if __name__ == "__main__":
    main()
