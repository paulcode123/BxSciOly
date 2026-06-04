#!/usr/bin/env python3
"""One-time import of Firestore Members into Neon Postgres."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT / ".env.local")


def _init_firestore():
    import firebase_admin
    from firebase_admin import credentials, firestore

    if firebase_admin._apps:
        return firestore.client()

    def _firebase_credentials():
        cred_path = (os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
        if cred_path and Path(cred_path).is_file():
            return credentials.Certificate(cred_path)
        for key in (
            "FIREBASE_SERVICE_ACCOUNT_JSON",
            "GOOGLE_APPLICATION_CREDENTIALS_JSON",
            "GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON",
        ):
            raw = os.environ.get(key, "").strip()
            if raw:
                return credentials.Certificate(json.loads(raw))
        fallback = _ROOT / "service_key.json"
        if fallback.is_file():
            return credentials.Certificate(str(fallback))
        raise FileNotFoundError(
            "No credentials found. Set GOOGLE_APPLICATION_CREDENTIALS to your JSON key path."
        )

    firebase_admin.initialize_app(
        _firebase_credentials(),
        {"storageBucket": "bxscioly-455318.appspot.com"},
    )
    return firestore.client()


def main() -> None:
    from db.connection import postgres_enabled
    from db.members import import_firestore_member

    if not postgres_enabled():
        print("DATABASE_URL not set. Run: npx vercel env pull .env.local")
        sys.exit(1)

    try:
        fs = _init_firestore()
        docs = list(fs.collection("Members").stream())
    except Exception as exc:
        err = str(exc).lower()
        print("Failed to read Firestore Members:", exc)
        if "permission" in err or "403" in err:
            print(
                "\nService account lacks Firestore read access.\n"
                "  In Google Cloud IAM, grant this account one of:\n"
                "    - Role: Cloud Datastore User  (roles/datastore.user)\n"
                "    - Or: Firebase Admin SDK Administrator Service Agent\n"
                "  Artifact Registry Reader does NOT include Firestore.\n"
            )
        if "invalid_grant" in err or "invalid jwt" in err:
            print(
                "\nYour local service account key is expired or invalid.\n"
                "  1) In Google Cloud Console, create a new key for the Firebase service account.\n"
                "  2) Save it as service_key.json (or set FIREBASE_SERVICE_ACCOUNT_JSON).\n"
                "  3) Re-run this script.\n"
                "\nAlternatively, export Members to data/members_export.json and run:\n"
                "  python scripts/db/import_members_json.py path/to/export.json\n"
            )
        sys.exit(1)
    print(f"Found {len(docs)} Firestore Members documents")

    import psycopg

    imported = 0
    skipped = 0
    for doc in docs:
        data = doc.to_dict() or {}
        try:
            import_firestore_member(doc.id, data)
            imported += 1
            print(f"  imported {doc.id} ({data.get('doeEmail', '?')})")
        except psycopg.errors.UniqueViolation as exc:
            skipped += 1
            print(f"  SKIP {doc.id} ({data.get('doeEmail', '?')}): duplicate email — {exc.diag.message_detail or exc}")

    print(f"Done. imported={imported} skipped={skipped} total_firestore={len(docs)}")


if __name__ == "__main__":
    main()
