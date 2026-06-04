"""Merch orders — Postgres replacement for Firestore MerchOrders."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from db.connection import get_connection


def _serialize_ts(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _new_id() -> str:
    return uuid.uuid4().hex[:20]


def get_by_member_id(member_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM merch_orders WHERE member_id = %s LIMIT 1",
                (member_id,),
            )
            return cur.fetchone()


def order_to_api(row: Dict[str, Any], member_api: Dict[str, Any]) -> Dict[str, Any]:
    design_votes = row.get("design_votes") or []
    items = row.get("items") or []
    if isinstance(design_votes, str):
        design_votes = json.loads(design_votes)
    if isinstance(items, str):
        items = json.loads(items)
    return {
        "id": row["id"],
        "memberId": row["member_id"],
        "firebaseID": row["member_id"],
        "bxsciolyID": member_api.get("bxsciolyID", ""),
        "firstName": member_api.get("firstName", ""),
        "lastName": member_api.get("lastName", ""),
        "house": member_api.get("house", ""),
        "designVotes": design_votes,
        "items": items,
        "spendLimit": row.get("spend_limit"),
        "status": row.get("status"),
        "submittedAt": _serialize_ts(row.get("submitted_at")),
    }


def create_order(
    member_id: str,
    design_votes: List[Any],
    items: List[Any],
    spend_limit: Optional[float],
) -> str:
    order_id = _new_id()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO merch_orders (id, member_id, design_votes, items, spend_limit)
                VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
                """,
                (
                    order_id,
                    member_id,
                    json.dumps(design_votes),
                    json.dumps(items),
                    spend_limit,
                ),
            )
    return order_id
