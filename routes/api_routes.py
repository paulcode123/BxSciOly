"""HTTP API backed by Neon Postgres (no Firebase)."""

from __future__ import annotations

import json
import logging
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from flask import Blueprint, jsonify, request, session

from db.connection import postgres_enabled
from routes import member_store

logger = logging.getLogger(__name__)

api_routes = Blueprint("api_routes", __name__)

_ROOT = Path(__file__).resolve().parent.parent


def _require_database():
    if not postgres_enabled():
        return jsonify({"error": "Database not configured"}), 503
    return None


def _smtp_config() -> dict:
    cfg = {}
    for key in (
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "SMTP_FROM",
        "SMTP_USE_TLS",
    ):
        val = os.environ.get(key)
        if val is not None:
            cfg[key] = val
    path = _ROOT / "api_keys.json"
    if path.is_file():
        try:
            with open(path, encoding="utf-8") as f:
                file_cfg = json.load(f)
            for k, v in file_cfg.items():
                cfg.setdefault(k, v)
        except (OSError, json.JSONDecodeError):
            pass
    return cfg


def _send_password_reset_email(to_email: str, reset_link: str) -> None:
    cfg = _smtp_config()
    host = cfg.get("SMTP_HOST")
    port = int(cfg.get("SMTP_PORT", 587))
    user = cfg.get("SMTP_USER")
    password = cfg.get("SMTP_PASSWORD")
    from_addr = cfg.get("SMTP_FROM") or user
    use_tls = str(cfg.get("SMTP_USE_TLS", "true")).lower() not in ("0", "false", "no")

    if not all([host, port, user, password, from_addr]):
        raise RuntimeError("SMTP not configured (set SMTP_* env vars)")

    subject = "Reset your Bronx Science Olympiad password"
    text_body = (
        "You requested a password reset.\n\n"
        f"Click the link to reset your password: {reset_link}\n\n"
        "This link expires in 1 hour. If you did not request this, ignore this email."
    )
    html_body = (
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222">'
        "<p>You requested a password reset.</p>"
        f'<p><a href="{reset_link}">Reset Password</a></p>'
        f"<p>Or copy this link: {reset_link}</p>"
        "<p>This link expires in 1 hour.</p></div>"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(host, port, timeout=15) as server:
        if use_tls:
            server.starttls()
        server.login(user, password)
        server.send_message(msg)


def _on_roster(member_api: dict) -> bool:
    if not member_api:
        return False
    if member_api.get("adminStatus", "none") != "none":
        return True
    if member_api.get("house"):
        return True
    if member_api.get("onRoster") is True:
        return True
    return member_api.get("memberStatus") == "returning"


# --- Auth ---


@api_routes.route("/api/auth/login", methods=["POST"])
def auth_login():
    err = _require_database()
    if err:
        return err
    from db import members as members_db

    data = request.get_json() or {}
    doe_email = data.get("doeEmail") or data.get("email")
    password = data.get("password") or ""
    if not doe_email or not password:
        return jsonify({"error": "doeEmail and password are required"}), 400

    profile = members_db.authenticate(doe_email, password)
    if not profile:
        return jsonify({"error": "Invalid email or password"}), 401

    member_id = profile.get("id")
    session["currentUser"] = profile
    return jsonify({member_id: profile}), 200


@api_routes.route("/api/auth/sync-session", methods=["POST"])
def sync_session():
    err = _require_database()
    if err:
        return err
    from db import members as members_db

    data = request.get_json() or {}
    user_info = data.get("user")
    if not user_info:
        return jsonify({"status": "error", "message": "No user info provided"}), 400

    uid = user_info.get("id") or user_info.get("uid")
    if uid:
        row = members_db.get_by_id(uid)
        if row:
            user_info = members_db.row_to_api_public(row)
    user_info.pop("password", None)
    session["currentUser"] = user_info
    return jsonify({"status": "success", "message": "Session synced"}), 200


@api_routes.route("/api/auth/request-password-reset", methods=["POST"])
def request_password_reset():
    err = _require_database()
    if err:
        return err
    from db import members as members_db

    data = request.get_json() or {}
    email = data.get("doeEmail") or data.get("email")
    if not email:
        return jsonify({"error": "doeEmail is required"}), 400

    row = members_db.find_by_doe_email(email)
    if not row:
        return jsonify({"message": "If an account exists, a reset email was sent."}), 200

    token = members_db.create_password_reset(row["id"], email)
    base_url = request.host_url.rstrip("/")
    reset_link = f"{base_url}/reset-password?token={token}"

    try:
        _send_password_reset_email(to_email=email, reset_link=reset_link)
    except Exception as send_err:
        logger.error("Password reset email failed: %s", send_err)

    body = {"message": "If an account exists, a reset email was sent."}
    if os.environ.get("FLASK_DEBUG") or os.environ.get("VERCEL_ENV") == "development":
        body["token"] = token
    return jsonify(body), 200


@api_routes.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    err = _require_database()
    if err:
        return err
    from db import members as members_db

    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("newPassword")
    if not token or not new_password:
        return jsonify({"error": "token and newPassword are required"}), 400

    ok, message = members_db.reset_password_with_token(token, new_password)
    if not ok:
        return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200


# --- Members ---


@api_routes.route("/api/Members/find-by-doe-email", methods=["POST"])
def find_member_by_doe_email_post():
    err = _require_database()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    doe_email = data.get("doeEmail") or data.get("email") or ""
    shaped = member_store.find_by_doe_email_shape(doe_email)
    if not shaped:
        return jsonify({"error": "No member found with this DOE email"}), 404
    return jsonify(shaped), 200


@api_routes.route("/api/Members", methods=["POST"])
def create_member():
    err = _require_database()
    if err:
        return err
    from db import members as members_db

    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "No data provided"}), 400

    doe_email = data.get("doeEmail")
    if doe_email and members_db.find_by_doe_email(doe_email):
        return jsonify({"error": "Email already in use. Try again."}), 409

    member_data = {k: v for k, v in data.items() if k != "events"}
    try:
        member_id = members_db.create(member_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"id": member_id, "message": "Member created successfully"}), 201


@api_routes.route("/api/Members/<member_id>", methods=["GET"])
def get_member(member_id):
    err = _require_database()
    if err:
        return err

    api = member_store.get_api(member_id)
    if not api:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(api), 200


@api_routes.route("/api/Members/<member_id>", methods=["PUT", "PATCH"])
def update_member(member_id):
    err = _require_database()
    if err:
        return err
    from db import members as members_db

    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if not members_db.exists(member_id):
        return jsonify({"error": "Member not found"}), 404

    members_db.update(member_id, data, merge=True)
    api = member_store.get_api(member_id)
    return jsonify(api), 200


# --- Roster ---


@api_routes.route("/api/roster-status/<user_id>", methods=["GET"])
def api_roster_status(user_id):
    err = _require_database()
    if err:
        return err

    profile = member_store.get_api(user_id)
    if not profile:
        return jsonify({"onRoster": False}), 200
    return jsonify({"onRoster": _on_roster(profile)}), 200


# --- Merch ---


@api_routes.route("/api/merch/check-eligibility/<user_id>", methods=["GET"])
def check_merch_eligibility(user_id):
    err = _require_database()
    if err:
        return err
    from db import merch as merch_db

    profile = member_store.get_api(user_id)
    if not profile:
        return jsonify({"eligible": False, "message": "Account not found."}), 404

    if not _on_roster(profile):
        return jsonify({
            "eligible": False,
            "message": "Merch ordering is for team members. Contact the board if you believe this is an error.",
        }), 403

    existing = merch_db.get_by_member_id(user_id)
    is_admin = profile.get("adminStatus", "none") != "none"
    return jsonify({
        "eligible": True,
        "alreadySubmitted": existing is not None,
        "isAdmin": is_admin,
    }), 200


@api_routes.route("/api/merch/submit", methods=["POST"])
def submit_merch_order():
    err = _require_database()
    if err:
        return err
    from db import merch as merch_db

    data = request.get_json() or {}
    user_id = data.get("memberId") or data.get("firebaseID")
    if not user_id:
        return jsonify({"error": "memberId is required"}), 400

    profile = member_store.get_api(user_id)
    if not profile:
        return jsonify({"error": "Account not found"}), 404
    if not _on_roster(profile):
        return jsonify({"error": "Not eligible for merch ordering"}), 403

    if merch_db.get_by_member_id(user_id):
        return jsonify({"error": "You have already submitted an order"}), 400

    design_votes = data.get("designVotes", [])
    items = data.get("items", [])
    spend_limit = data.get("spendLimit")

    if not design_votes:
        return jsonify({"error": "Design votes are required"}), 400
    if not items:
        return jsonify({"error": "At least one merch item is required"}), 400

    required_items = {"t-shirt", "hoodie", "sweatshirt"}
    if not any(item.get("type") in required_items for item in items):
        return jsonify({
            "error": "You must select at least one of: T-shirt, Hoodie, or Sweatshirt to attend tournaments",
        }), 400

    merch_db.create_order(user_id, design_votes, items, spend_limit)
    return jsonify({"success": True, "message": "Your order has been submitted successfully!"}), 200


@api_routes.route("/api/merch/get-order/<user_id>", methods=["GET"])
def get_merch_order(user_id):
    err = _require_database()
    if err:
        return err
    from db import merch as merch_db

    profile = member_store.get_api(user_id)
    if not profile:
        return jsonify({"error": "Account not found"}), 404

    row = merch_db.get_by_member_id(user_id)
    if not row:
        return jsonify({"error": "No order found"}), 404
    return jsonify(merch_db.order_to_api(row, profile)), 200
