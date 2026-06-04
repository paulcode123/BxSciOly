"""Members table — replaces Firebase ``Members`` collection."""

from __future__ import annotations

import json
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import bcrypt

from db.connection import get_connection

# API (camelCase) <-> Postgres (snake_case)
_FIELD_MAP = {
    "firstName": "first_name",
    "lastName": "last_name",
    "doeEmail": "doe_email",
    "personalEmail": "personal_email",
    "phoneNumber": "phone_number",
    "memberStatus": "member_status",
    "createdAt": "created_at",
    "updatedAt": "updated_at",
    "interestReason": "interest_reason",
    "howDidYouHearAboutUs": "how_did_you_hear_about_us",
    "pastExperience": "past_experience",
    "returnReason": "return_reason",
    "yearsInTeam": "years_in_team",
    "preseasonHrs": "preseason_hrs",
    "regseasonHrs": "regseason_hrs",
    "postseasonHrs": "postseason_hrs",
    "profilePicUrl": "profile_pic_url",
    "importantNotification": "important_notification",
    "teamNotification": "team_notification",
    "eventNotification": "event_notification",
    "adminStatus": "admin_status",
    "house": "house",
    "grade": "grade",
    "bio": "bio",
}
_REVERSE_MAP = {v: k for k, v in _FIELD_MAP.items()}
_CORE_SNAKE = set(_FIELD_MAP.values()) | {"id", "password_hash", "extra"}
_SENSITIVE = {"password", "password_hash"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if hasattr(value, "timestamp"):
        return datetime.fromtimestamp(value.timestamp(), tz=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _serialize_ts(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    if not plain or not password_hash:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def row_to_api(row: Optional[Dict[str, Any]], include_password: bool = False) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    out: Dict[str, Any] = {"id": row["id"]}
    for snake, camel in _REVERSE_MAP.items():
        val = row.get(snake)
        if val is not None:
            out[camel] = _serialize_ts(val)
    extra = row.get("extra") or {}
    if isinstance(extra, str):
        try:
            extra = json.loads(extra)
        except json.JSONDecodeError:
            extra = {}
    if isinstance(extra, dict):
        for k, v in extra.items():
            if k not in out and k not in _SENSITIVE:
                out[k] = _serialize_ts(v)
    if include_password:
        pass
    else:
        out.pop("password", None)
        out.pop("passwordHash", None)
    return out


def row_to_api_public(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return row_to_api(row, include_password=False)


def api_to_row(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Split API payload into column updates and extra JSON."""
    row: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}
    for key, value in data.items():
        if key in ("id", "password", "passwordHash", "events"):
            continue
        if key in _FIELD_MAP:
            snake = _FIELD_MAP[key]
            if snake in ("created_at", "updated_at"):
                row[snake] = _parse_ts(value)
            elif snake == "phone_number" and value is not None:
                row[snake] = str(value)
            else:
                row[snake] = value
        elif key not in _SENSITIVE:
            extra[key] = value
    return row, extra


def _new_id() -> str:
    return uuid.uuid4().hex[:20]


def find_by_doe_email(doe_email: str) -> Optional[Dict[str, Any]]:
    key = (doe_email or "").strip()
    if not key:
        return None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM members
                WHERE LOWER(doe_email) = LOWER(%s)
                LIMIT 1
                """,
                (key,),
            )
            return cur.fetchone()


def find_by_legacy_email(email: str) -> Optional[Dict[str, Any]]:
    key = (email or "").strip()
    if not key:
        return None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM members
                WHERE LOWER(personal_email) = LOWER(%s)
                   OR LOWER(doe_email) = LOWER(%s)
                LIMIT 1
                """,
                (key, key),
            )
            return cur.fetchone()


def get_by_id(member_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM members WHERE id = %s", (member_id,))
            return cur.fetchone()


def exists(member_id: str) -> bool:
    return get_by_id(member_id) is not None


def list_all(order_by_last_name: bool = False) -> List[Dict[str, Any]]:
    order = "ORDER BY last_name NULLS LAST, first_name NULLS LAST" if order_by_last_name else ""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM members {order}")
            return list(cur.fetchall())


def list_all_api_firebase_shape() -> List[Dict[str, Any]]:
    """Legacy ``get_all('Members')`` shape: ``[{id: fields}, ...]``."""
    items = []
    for row in list_all():
        api = row_to_api_public(row) or {}
        mid = api.pop("id", row["id"])
        items.append({mid: api})
    return items


def find_by_doe_email_firebase_shape(doe_email: str) -> Optional[Dict[str, Dict[str, Any]]]:
    row = find_by_doe_email(doe_email)
    if not row:
        return None
    api = row_to_api_public(row) or {}
    mid = api.pop("id", row["id"])
    return {mid: api}


def create(data: Dict[str, Any], member_id: Optional[str] = None) -> str:
    row, extra = api_to_row(data)
    mid = member_id or data.get("id") or _new_id()
    plain = data.get("password") or ""
    if not plain:
        raise ValueError("password is required for new members")
    row["id"] = mid
    row["password_hash"] = hash_password(plain)
    row["doe_email"] = row.get("doe_email") or data.get("doeEmail") or ""
    if not row["doe_email"]:
        raise ValueError("doeEmail is required")
    row.setdefault("admin_status", data.get("adminStatus") or "none")
    row.setdefault("created_at", _parse_ts(data.get("createdAt")) or _utc_now())
    row["updated_at"] = _utc_now()
    row["extra"] = json.dumps(extra)

    cols = list(row.keys())
    placeholders = ", ".join(["%s"] * len(cols))
    col_names = ", ".join(cols)
    values = [row[c] for c in cols]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO members ({col_names}) VALUES ({placeholders})",
                values,
            )
    return mid


def update(member_id: str, data: Dict[str, Any], merge: bool = True) -> bool:
    if not exists(member_id):
        return False
    row, extra = api_to_row(data)
    if "password" in data and data["password"]:
        row["password_hash"] = hash_password(data["password"])
    row["updated_at"] = _utc_now()

    with get_connection() as conn:
        with conn.cursor() as cur:
            if merge:
                if extra:
                    cur.execute(
                        """
                        UPDATE members
                        SET extra = COALESCE(extra, '{}'::jsonb) || %s::jsonb
                        WHERE id = %s
                        """,
                        (json.dumps(extra), member_id),
                    )
                for col, val in row.items():
                    if col == "extra":
                        continue
                    cur.execute(
                        f"UPDATE members SET {col} = %s WHERE id = %s",
                        (val, member_id),
                    )
            else:
                existing = get_by_id(member_id)
                if not existing:
                    return False
                merged_extra = dict(existing.get("extra") or {})
                merged_extra.update(extra)
                row["extra"] = json.dumps(merged_extra)
                cols = [k for k in row.keys() if k != "id"]
                set_clause = ", ".join(f"{c} = %s" for c in cols)
                values = [row[c] for c in cols] + [member_id]
                cur.execute(
                    f"UPDATE members SET {set_clause} WHERE id = %s",
                    values,
                )
    return True


def replace(member_id: str, data: Dict[str, Any]) -> bool:
    existing = get_by_id(member_id)
    if not existing:
        return False
    row, extra = api_to_row(data)
    plain = data.get("password")
    if plain:
        row["password_hash"] = hash_password(plain)
    else:
        row["password_hash"] = existing["password_hash"]
    row["id"] = member_id
    row["doe_email"] = row.get("doe_email") or data.get("doeEmail") or existing["doe_email"]
    row.setdefault("admin_status", "none")
    row["updated_at"] = _utc_now()
    row["extra"] = json.dumps(extra)
    row.setdefault("created_at", _parse_ts(data.get("createdAt")) or _utc_now())

    cols = [k for k in row.keys()]
    set_clause = ", ".join(f"{c} = %s" for c in cols if c != "id")
    values = [row[c] for c in cols if c != "id"] + [member_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE members SET {set_clause} WHERE id = %s",
                values,
            )
    return True


def delete(member_id: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM members WHERE id = %s", (member_id,))
            return cur.rowcount > 0


def authenticate(doe_email: str, password: str) -> Optional[Dict[str, Any]]:
    row = find_by_doe_email(doe_email)
    if not row:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    return row_to_api_public(row)


# --- Password resets ---


def create_password_reset(member_id: str, doe_email: str) -> str:
    token = secrets.token_urlsafe(32)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO password_resets (token, member_id, doe_email)
                VALUES (%s, %s, %s)
                """,
                (token, member_id, doe_email),
            )
    return token


def get_password_reset(token: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM password_resets WHERE token = %s", (token,))
            return cur.fetchone()


def mark_password_reset_used(token: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE password_resets
                SET used = TRUE, used_at = NOW()
                WHERE token = %s
                """,
                (token,),
            )


def reset_password_with_token(token: str, new_password: str) -> Tuple[bool, str]:
    rec = get_password_reset(token)
    if not rec:
        return False, "Invalid or expired token"
    if rec.get("used"):
        return False, "Token already used"
    created = rec.get("created_at")
    ttl = int(rec.get("expires_in_seconds") or 3600)
    if created:
        if isinstance(created, datetime):
            age = (_utc_now() - created.replace(tzinfo=timezone.utc)).total_seconds()
        else:
            age = 0
        if age > ttl:
            return False, "Token expired"
    member_id = rec.get("member_id")
    if not member_id or not exists(member_id):
        return False, "User not found"
    update(member_id, {"password": new_password}, merge=True)
    mark_password_reset_used(token)
    return True, "Password has been reset successfully"


def import_firestore_member(doc_id: str, data: Dict[str, Any]) -> str:
    """Upsert one Firestore member document (migration)."""
    payload = dict(data)
    payload["id"] = doc_id
    plain = payload.pop("password", None) or ""
    row, extra = api_to_row(payload)
    row["id"] = doc_id
    row["doe_email"] = row.get("doe_email") or payload.get("doeEmail") or f"unknown-{doc_id}@import.local"
    if plain:
        if plain.startswith("$2") and len(plain) > 50:
            row["password_hash"] = plain
        else:
            row["password_hash"] = hash_password(plain)
    else:
        row["password_hash"] = hash_password(secrets.token_urlsafe(16))
    row.setdefault("admin_status", payload.get("adminStatus") or "none")
    row["created_at"] = _parse_ts(payload.get("createdAt")) or _utc_now()
    row["updated_at"] = _utc_now()
    row["extra"] = json.dumps(extra)

    cols = list(row.keys())
    placeholders = ", ".join(["%s"] * len(cols))
    col_names = ", ".join(cols)
    updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != "id")
    values = [row[c] for c in cols]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO members ({col_names}) VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET {updates}
                """,
                values,
            )
    return doc_id
