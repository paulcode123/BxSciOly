"""Members persistence — Neon Postgres only."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from flask import jsonify, request

from db.connection import postgres_enabled


def _pg():
    from db import members as members_db

    return members_db


def use_postgres() -> bool:
    return postgres_enabled()


def get_row(member_id: str) -> Optional[Dict[str, Any]]:
    return _pg().get_by_id(member_id)


def get_api(member_id: str) -> Optional[Dict[str, Any]]:
    row = _pg().get_by_id(member_id)
    return _pg().row_to_api_public(row)


def exists(member_id: str) -> bool:
    return _pg().exists(member_id)


def find_by_doe_email_shape(doe_email: str) -> Optional[Dict[str, Dict[str, Any]]]:
    return _pg().find_by_doe_email_firebase_shape(doe_email)


def list_all_api_shape() -> list:
    return _pg().list_all_api_firebase_shape()


def list_all_rows(order_by_last_name: bool = False) -> List[Dict[str, Any]]:
    return _pg().list_all(order_by_last_name=order_by_last_name)


def require_full_admin():
    """Return (admin_api_dict, error_response) — error_response is None on success."""
    admin_id = request.headers.get("X-Admin-ID")
    if not admin_id:
        return None, (jsonify({"error": "Admin authentication required"}), 401)
    api = get_api(admin_id)
    if not api:
        return None, (jsonify({"error": "Invalid admin session"}), 401)
    if api.get("adminStatus") != "full":
        return None, (jsonify({"error": "Full admin privileges required"}), 403)
    return api, None
