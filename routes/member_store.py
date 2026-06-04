"""Members persistence: Neon Postgres (preferred) with Firestore fallback."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from flask import jsonify

from db.connection import postgres_enabled

_members_db = None
_firestore_db = None


def _pg():
    global _members_db
    if _members_db is None:
        from db import members as members_db

        _members_db = members_db
    return _members_db


def _fs():
    global _firestore_db
    if _firestore_db is None:
        from routes.firebase_routes import db as firestore_db

        _firestore_db = firestore_db
    return _firestore_db


def use_postgres() -> bool:
    return postgres_enabled()


def get_row(member_id: str) -> Optional[Dict[str, Any]]:
    if use_postgres():
        return _pg().get_by_id(member_id)
    doc = _fs().collection("Members").document(member_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    data["id"] = doc.id
    return data


def get_api(member_id: str) -> Optional[Dict[str, Any]]:
    if use_postgres():
        row = _pg().get_by_id(member_id)
        return _pg().row_to_api_public(row)
    doc = _fs().collection("Members").document(member_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    data["id"] = doc.id
    data.pop("password", None)
    data.pop("passwordHash", None)
    return data


def exists(member_id: str) -> bool:
    if use_postgres():
        return _pg().exists(member_id)
    return _fs().collection("Members").document(member_id).get().exists


def find_by_doe_email_shape(doe_email: str) -> Optional[Dict[str, Dict[str, Any]]]:
    if use_postgres():
        return _pg().find_by_doe_email_firebase_shape(doe_email)
    key = (doe_email or "").strip()
    keys = [key]
    low = key.lower()
    if low not in keys:
        keys.append(low)
    for k in keys:
        q = _fs().collection("Members").where("doeEmail", "==", k).limit(1).stream()
        results = list(q)
        if results:
            doc = results[0]
            data = doc.to_dict() or {}
            data.pop("password", None)
            return {doc.id: data}
    return None


def list_all_api_shape() -> list:
    if use_postgres():
        return _pg().list_all_api_firebase_shape()
    docs = _fs().collection("Members").stream()
    return [{doc.id: doc.to_dict()} for doc in docs]


def list_all_rows(order_by_last_name: bool = False) -> List[Dict[str, Any]]:
    if use_postgres():
        return _pg().list_all(order_by_last_name=order_by_last_name)
    docs = _fs().collection("Members").stream()
    out = []
    for doc in docs:
        data = doc.to_dict() or {}
        data["id"] = doc.id
        out.append(data)
    if order_by_last_name:
        out.sort(key=lambda r: ((r.get("lastName") or ""), (r.get("firstName") or "")))
    return out


def require_full_admin():
    """Return (admin_api_dict, error_response) — error_response is None on success."""
    from flask import request

    admin_id = request.headers.get("X-Admin-ID")
    if not admin_id:
        return None, (jsonify({"error": "Admin authentication required"}), 401)
    api = get_api(admin_id)
    if not api:
        return None, (jsonify({"error": "Invalid admin session"}), 401)
    if api.get("adminStatus") != "full":
        return None, (jsonify({"error": "Full admin privileges required"}), 403)
    return api, None
