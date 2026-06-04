#!/usr/bin/env python3
"""Verify Firestore read access for GOOGLE_APPLICATION_CREDENTIALS."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT / ".env.local")

PROJECT = "bxscioly-455318"


def main() -> None:
    cred_path = (os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
    if not cred_path or not Path(cred_path).is_file():
        print("Set GOOGLE_APPLICATION_CREDENTIALS to your JSON key path.")
        sys.exit(1)

    info = json.loads(Path(cred_path).read_text(encoding="utf-8"))
    email = info.get("client_email", "?")
    print(f"Project: {PROJECT}")
    print(f"Credentials: {cred_path}")
    print(f"Service account: {email}")

    from google.cloud import firestore
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file(cred_path)
    db = firestore.Client(project=PROJECT, credentials=creds)
    try:
        docs = list(db.collection("Members").limit(1).stream())
        print(f"OK — Firestore read works (sample size {len(docs)}).")
        if docs:
            print(f"Sample document id: {docs[0].id}")
        sys.exit(0)
    except Exception as exc:
        print(f"FAILED: {exc}")
        print(
            "\nIn Google Cloud IAM (project bxscioly-455318), grant THIS service account:\n"
            "  Role: Cloud Datastore User  (roles/datastore.user)\n"
            "At project level (not only Artifact Registry).\n"
            "Artifact Registry Reader does not grant Firestore access.\n"
            "Wait 1–2 minutes after saving, then retry.\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
