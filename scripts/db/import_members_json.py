#!/usr/bin/env python3
"""Import members from a JSON export (Firebase console or custom).

File format: object keyed by member id, or list of {id, ...fields}.
  { "abc123": { "firstName": "...", "doeEmail": "...", "password": "..." }, ... }
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT / ".env.local")
load_dotenv(_ROOT / ".env.production.local")

from db import members as members_db  # noqa: E402


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else _ROOT / "data" / "members_export.json")
    if not path.exists():
        print(f"Missing file: {path}")
        print("Export Firestore Members to this path, or pass a JSON file argument.")
        sys.exit(1)
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = []
    if isinstance(raw, dict):
        items = [(k, v) for k, v in raw.items()]
    elif isinstance(raw, list):
        for entry in raw:
            mid = entry.pop("id", None) or entry.get("_id")
            if mid:
                items.append((mid, entry))
    else:
        print("Unsupported JSON shape")
        sys.exit(1)
    for doc_id, data in items:
        members_db.import_firestore_member(doc_id, data)
        print(f"  imported {doc_id}")
    print(f"Done. {len(items)} members.")


if __name__ == "__main__":
    main()
