"""
Google Sheets sync for team attendance.

Requires:
  - ATTENDANCE_SPREADSHEET_ID (or GOOGLE_SHEETS_SPREADSHEET_ID): spreadsheet ID from the URL
  - Service account JSON either in GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON (raw JSON string)
    or a file path in GOOGLE_SHEETS_CREDENTIALS (defaults to ./google_sheets_service_key.json)

Share the spreadsheet with the service account client_email with Editor access.

Sheets:
  - Codes: Date | Event | Block | Code | MeetingId
  - Members: rebuilt by admin "Update member %" action
  - One tab per event (sanitized event name): row1 labels, row2 meeting IDs, data from row3
"""
from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

CODES_SHEET = "Codes"
MEMBERS_SHEET = "Members"
RESERVED = frozenset({CODES_SHEET, MEMBERS_SHEET})

PRESENT_VALUES = frozenset(
    {"Y", "YES", "TRUE", "1", "X", "P", "✓", "YEP"}
)


def _spreadsheet_id() -> str:
    return (
        os.environ.get("ATTENDANCE_SPREADSHEET_ID", "").strip()
        or os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID", "").strip()
    )


def _get_gspread_client():
    try:
        import gspread
    except ImportError:
        logger.warning("gspread not installed; attendance sheets disabled")
        return None

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    json_str = os.environ.get("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON", "").strip()
    if json_str:
        try:
            info = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error("Invalid GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON: %s", e)
            return None
        return gspread.service_account_from_dict(info, scopes=scopes)

    cred_path = os.environ.get(
        "GOOGLE_SHEETS_CREDENTIALS",
        os.path.join(os.path.dirname(__file__), "google_sheets_service_key.json"),
    )
    if not os.path.isfile(cred_path):
        return None
    return gspread.service_account(filename=cred_path, scopes=scopes)


def sheets_enabled() -> bool:
    return bool(_spreadsheet_id() and _get_gspread_client())


def _open_spreadsheet():
    sid = _spreadsheet_id()
    if not sid:
        return None
    gc = _get_gspread_client()
    if not gc:
        return None
    try:
        return gc.open_by_key(sid)
    except Exception as e:
        logger.warning("Could not open attendance spreadsheet: %s", e)
        return None


def safe_sheet_title(event_name: str, used_titles: Optional[Set[str]] = None) -> str:
    s = (event_name or "").strip()
    s = re.sub(r"[\[\]\\*?:/]", "_", s)
    if not s:
        s = "Event"
    s = s[:95]
    if used_titles is None:
        return s
    title = s
    n = 1
    while title in used_titles:
        suffix = f"_{n}"
        title = (s[: 100 - len(suffix)] + suffix)[:100]
        n += 1
    used_titles.add(title)
    return title


def _firestore_date_to_date(m: Dict[str, Any]) -> Optional[datetime]:
    d = m.get("date")
    if d is None:
        return None
    if hasattr(d, "timestamp"):
        return datetime.fromtimestamp(d.timestamp(), tz=timezone.utc)
    if isinstance(d, dict) and "seconds" in d:
        return datetime.fromtimestamp(d["seconds"], tz=timezone.utc)
    if isinstance(d, str):
        try:
            return datetime.fromisoformat(d.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _meeting_label(m: Dict[str, Any]) -> str:
    dt = _firestore_date_to_date(m)
    block = (m.get("block") or "").strip()
    if dt:
        ds = dt.strftime("%Y-%m-%d")
        if block:
            return f"{ds} B{block}"
        return ds
    return m.get("id", "Meeting")[:12]


def _cell_present(val: Any) -> bool:
    if val is None or val == "":
        return False
    if isinstance(val, bool):
        return val
    t = str(val).strip().upper()
    return t in PRESENT_VALUES


def _get_db():
    try:
        from db_init import db

        return db
    except Exception:
        from firebase_admin import firestore

        return firestore.client()


def _event_members_and_name(event_name: str) -> Tuple[str, List[Tuple[str, str]]]:
    """Return canonical eventName from Firestore and [(member_id, display_name), ...]."""
    db = _get_db()
    q = db.collection("Events").where("eventName", "==", event_name).limit(1).stream()
    docs = list(q)
    if not docs:
        return event_name, []
    doc = docs[0]
    data = doc.to_dict() or {}
    canonical = data.get("eventName") or event_name
    member_ids = data.get("members") or []
    rows: List[Tuple[str, str]] = []
    for mid in member_ids:
        md = db.collection("Members").document(mid).get()
        if not md.exists:
            rows.append((mid, mid))
            continue
        m = md.to_dict() or {}
        fn = (m.get("firstName") or "").strip()
        ln = (m.get("lastName") or "").strip()
        name = f"{ln}, {fn}".strip(", ") or mid
        rows.append((mid, name))
    rows.sort(key=lambda x: x[1].lower())
    return canonical, rows


def _ensure_codes_sheet(sh) -> Any:
    try:
        return sh.worksheet(CODES_SHEET)
    except Exception:
        ws = sh.add_worksheet(title=CODES_SHEET, rows=2000, cols=10)
        ws.append_row(["Date", "Event", "Block", "Code", "MeetingId"], value_input_option="USER_ENTERED")
        return ws


def _ensure_members_sheet(sh) -> Any:
    try:
        return sh.worksheet(MEMBERS_SHEET)
    except Exception:
        ws = sh.add_worksheet(title=MEMBERS_SHEET, rows=2000, cols=50)
        return ws


def _ensure_event_worksheet(sh, title: str):
    try:
        return sh.worksheet(title)
    except Exception:
        return sh.add_worksheet(title=title, rows=2000, cols=100)


def _append_codes_row_ws(ws, meeting_id: str, meeting: Dict[str, Any]) -> None:
    dt = _firestore_date_to_date(meeting)
    date_s = dt.strftime("%Y-%m-%d") if dt else ""
    ev = meeting.get("eventName") or ""
    block = meeting.get("block") or ""
    code = meeting.get("code") or ""
    ws.append_row([date_s, ev, block, code, meeting_id], value_input_option="USER_ENTERED")


def append_codes_row(meeting_id: str, meeting: Dict[str, Any]) -> None:
    sh = _open_spreadsheet()
    if not sh:
        return
    try:
        ws = _ensure_codes_sheet(sh)
        _append_codes_row_ws(ws, meeting_id, meeting)
    except Exception as e:
        logger.warning("append_codes_row failed: %s", e)


def ensure_meeting_column(meeting_id: str, meeting: Dict[str, Any]) -> None:
    """Ensure event tab exists with a column for this meeting and roster rows."""
    sh = _open_spreadsheet()
    if not sh:
        return
    event_name = meeting.get("eventName") or ""
    if not event_name:
        return
    try:
        _, roster = _event_members_and_name(event_name)
        title = safe_sheet_title(event_name)
        ws = _ensure_event_worksheet(sh, title)
        all_vals = [list(r) for r in ws.get_all_values()]

        if len(all_vals) < 2:
            all_vals = [
                ["Member ID", "Name"],
                ["", ""],
            ]
        header_row = all_vals[0]
        if len(header_row) < 2:
            header_row = ["Member ID", "Name"] + header_row[2:]
            all_vals[0] = header_row
        mid_row = all_vals[1] if len(all_vals) > 1 else ["", ""]
        while len(mid_row) < len(header_row):
            mid_row.append("")
        all_vals[1] = mid_row

        label = _meeting_label({**meeting, "id": meeting_id})
        col_idx = None
        for j in range(2, len(mid_row)):
            if mid_row[j] == meeting_id:
                col_idx = j
                break

        if col_idx is None:
            new_h = header_row + [label]
            new_m = mid_row + [meeting_id]
            new_vals = [new_h, new_m]
            width = len(new_h)
            for r in range(2, len(all_vals)):
                row = list(all_vals[r])
                while len(row) < width - 1:
                    row.append("")
                row.append("")
                new_vals.append(row)
            all_vals = new_vals
            nrows = max(len(all_vals), 2 + len(roster), 50)
            ws.resize(rows=nrows, cols=max(width, 10))
            ws.update(
                f"A1:{_a1_col(width)}{len(all_vals)}",
                [row + [""] * (width - len(row)) for row in all_vals],
                value_input_option="USER_ENTERED",
            )
            all_vals = [list(r) for r in ws.get_all_values()]

        width = len(all_vals[0])
        existing_ids = {row[0] for row in all_vals[2:] if row and row[0]}
        to_add = [(mid, name) for mid, name in roster if mid not in existing_ids]
        if to_add:
            ws.append_rows(
                [[mid, name] + [""] * (width - 2) for mid, name in to_add],
                value_input_option="USER_ENTERED",
            )
    except Exception as e:
        logger.warning("ensure_meeting_column failed: %s", e)


def _a1_col(n: int) -> str:
    """1-based column index to A1 column letters (1 -> A)."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s or "A"


def mark_member_meeting(meeting_id: str, meeting: Dict[str, Any], member_id: str, present: bool) -> None:
    sh = _open_spreadsheet()
    if not sh:
        return
    event_name = meeting.get("eventName") or ""
    if not event_name:
        return
    try:
        title = safe_sheet_title(event_name)
        ws = sh.worksheet(title)
        all_vals = ws.get_all_values()
        if len(all_vals) < 2:
            ensure_meeting_column(meeting_id, meeting)
            all_vals = ws.get_all_values()
        mids = all_vals[1]
        col = None
        for i, m in enumerate(mids):
            if i >= 2 and m == meeting_id:
                col = i + 1
                break
        if col is None:
            ensure_meeting_column(meeting_id, meeting)
            all_vals = ws.get_all_values()
            mids = all_vals[1]
            for i, m in enumerate(mids):
                if i >= 2 and m == meeting_id:
                    col = i + 1
                    break
        if col is None:
            return
        row = None
        for r in range(2, len(all_vals)):
            if len(all_vals[r]) > 0 and all_vals[r][0] == member_id:
                row = r + 1
                break
        if row is None:
            _, roster = _event_members_and_name(event_name)
            name = next((n for mid, n in roster if mid == member_id), member_id)
            ws.append_row(
                [member_id, name] + [""] * (len(all_vals[0]) - 2 if all_vals else 0),
                value_input_option="USER_ENTERED",
            )
            all_vals = ws.get_all_values()
            row = len(all_vals)

        cell = f"{_a1_col(col)}{row}"
        val = "Y" if present else ""
        ws.update(cell, [[val]], value_input_option="USER_ENTERED")
    except Exception as e:
        logger.warning("mark_member_meeting failed: %s", e)


def sync_meeting_column_from_firestore(meeting_id: str, meeting: Dict[str, Any]) -> None:
    """Set entire meeting column from Firestore attended list."""
    sh = _open_spreadsheet()
    if not sh:
        return
    event_name = meeting.get("eventName") or ""
    attended = set(meeting.get("attended") or [])
    if not event_name:
        return
    try:
        title = safe_sheet_title(event_name)
        ws = sh.worksheet(title)
        all_vals = ws.get_all_values()
        if len(all_vals) < 2:
            ensure_meeting_column(meeting_id, meeting)
            all_vals = ws.get_all_values()
        mids = all_vals[1]
        col = None
        for i, m in enumerate(mids):
            if i >= 2 and m == meeting_id:
                col = i + 1
                break
        if col is None:
            ensure_meeting_column(meeting_id, meeting)
            all_vals = ws.get_all_values()
            mids = all_vals[1]
            for i, m in enumerate(mids):
                if i >= 2 and m == meeting_id:
                    col = i + 1
                    break
        if col is None:
            return
        updates = []
        for r in range(2, len(all_vals)):
            if not all_vals[r]:
                continue
            mid = all_vals[r][0]
            if not mid:
                continue
            val = "Y" if mid in attended else ""
            updates.append({"range": f"{_a1_col(col)}{r+1}", "values": [[val]]})
        if updates:
            for i in range(0, len(updates), 90):
                ws.batch_update(updates[i : i + 90], value_input_option="USER_ENTERED")
    except Exception as e:
        logger.warning("sync_meeting_column_from_firestore failed: %s", e)


def on_meeting_created(meeting_id: str, meeting: Dict[str, Any], *, append_code: bool = True) -> None:
    if append_code:
        append_codes_row(meeting_id, meeting)
    ensure_meeting_column(meeting_id, meeting)


def on_meeting_checkin(meeting_id: str, meeting: Dict[str, Any], member_id: str) -> None:
    mark_member_meeting(meeting_id, meeting, member_id, True)


def rebuild_members_summary() -> Dict[str, Any]:
    """Rebuild Members sheet from event tabs. Returns stats for API response."""
    sh = _open_spreadsheet()
    if not sh:
        return {"ok": False, "error": "Spreadsheet not configured"}
    db = _get_db()
    try:
        event_docs = list(db.collection("Events").stream())
        event_names_ordered = sorted(
            [(d.to_dict() or {}).get("eventName") or d.id for d in event_docs],
            key=lambda x: x.lower(),
        )
        event_to_members: Dict[str, Set[str]] = {}
        for d in event_docs:
            data = d.to_dict() or {}
            en = data.get("eventName") or d.id
            event_to_members[en] = set(data.get("members") or [])

        used_titles: Set[str] = set()
        event_to_sheet_title: Dict[str, str] = {}
        for en in event_names_ordered:
            event_to_sheet_title[en] = safe_sheet_title(en, used_titles)

        member_meta: Dict[str, Tuple[str, str, str]] = {}
        for d in db.collection("Members").stream():
            m = d.to_dict() or {}
            fn = (m.get("firstName") or "").strip()
            ln = (m.get("lastName") or "").strip()
            em = (m.get("doeEmail") or m.get("email") or "").strip()
            member_meta[d.id] = (ln, fn, em)

        all_member_ids: Set[str] = set()
        for s in event_to_members.values():
            all_member_ids |= s

        worksheets = {w.title: w for w in sh.worksheets()}

        def stats_for_member_event(mid: str, en: str) -> Tuple[Optional[float], int, int]:
            """Return (percent, present_count, total_meetings) for member on event sheet."""
            if mid not in event_to_members.get(en, set()):
                return None, 0, 0
            st = event_to_sheet_title.get(en, safe_sheet_title(en))
            ws = worksheets.get(st)
            if not ws:
                return None, 0, 0
            all_vals = ws.get_all_values()
            if len(all_vals) < 3:
                return None, 0, 0
            ncols = max(0, len(all_vals[0]) - 2)
            if ncols <= 0:
                return None, 0, 0
            target_row = None
            for row in all_vals[2:]:
                if row and row[0] == mid:
                    target_row = row
                    break
            if not target_row:
                return 0.0, 0, ncols
            present = 0
            for ci in range(2, 2 + ncols):
                if ci < len(target_row) and _cell_present(target_row[ci]):
                    present += 1
            pct = round(100.0 * present / ncols, 1)
            return pct, present, ncols

        rows_out: List[List[Any]] = []
        header = ["Last Name", "First Name", "Email", "Member ID"] + [f"{e} %" for e in event_names_ordered] + [
            "Overall %"
        ]
        rows_out.append(header)

        stat_cache: Dict[Tuple[str, str], Tuple[Optional[float], int, int]] = {}

        for mid in sorted(
            all_member_ids,
            key=lambda x: (member_meta.get(x, ("", "", ""))[0].lower(), member_meta.get(x, ("", "", ""))[1].lower()),
        ):
            ln, fn, em = member_meta.get(mid, ("", "", ""))
            row = [ln, fn, em, mid]
            overall_p = 0
            overall_t = 0
            for en in event_names_ordered:
                if mid not in event_to_members.get(en, set()):
                    row.append("")
                    continue
                key = (mid, en)
                if key not in stat_cache:
                    stat_cache[key] = stats_for_member_event(mid, en)
                pct, present, ncols = stat_cache[key]
                if pct is None:
                    row.append("")
                    continue
                row.append(pct)
                overall_p += present
                overall_t += ncols
            if overall_t > 0:
                row.append(round(100.0 * overall_p / overall_t, 1))
            else:
                row.append("")
            rows_out.append(row)

        ws_m = _ensure_members_sheet(sh)
        ws_m.clear()
        ws_m.update(f"A1:{_a1_col(len(header))}{len(rows_out)}", rows_out, value_input_option="USER_ENTERED")
        return {"ok": True, "membersWritten": len(rows_out) - 1, "events": len(event_names_ordered)}
    except Exception as e:
        logger.exception("rebuild_members_summary failed")
        return {"ok": False, "error": str(e)}


def init_attendance_workbook() -> Dict[str, Any]:
    """Create Codes/Members headers, rebuild Codes from Firestore, sync meeting columns for all meetings."""
    sh = _open_spreadsheet()
    if not sh:
        return {"ok": False, "error": "Spreadsheet not configured"}
    try:
        _ensure_members_sheet(sh)
        ws_codes = _ensure_codes_sheet(sh)
        ws_codes.clear()
        ws_codes.append_row(
            ["Date", "Event", "Block", "Code", "MeetingId"], value_input_option="USER_ENTERED"
        )

        db = _get_db()
        used: Set[str] = set()
        for d in db.collection("Events").stream():
            data = d.to_dict() or {}
            en = data.get("eventName")
            if not en:
                continue
            st = safe_sheet_title(en, used)
            ws_ev = _ensure_event_worksheet(sh, st)
            if not ws_ev.get_all_values():
                ws_ev.update(
                    "A1:B2",
                    [["Member ID", "Name"], ["", ""]],
                    value_input_option="USER_ENTERED",
                )

        meetings = list(db.collection("Meeting").stream())

        def _sort_key(doc):
            m = doc.to_dict() or {}
            dt = _firestore_date_to_date(m)
            return dt or datetime.min.replace(tzinfo=timezone.utc)

        meetings.sort(key=_sort_key)
        for doc in meetings:
            m = doc.to_dict() or {}
            mid = doc.id
            full = {**m, "id": mid}
            _append_codes_row_ws(ws_codes, mid, full)
            on_meeting_created(mid, full, append_code=False)
        return {"ok": True, "meetingsProcessed": len(meetings)}
    except Exception as e:
        logger.exception("init_attendance_workbook failed")
        return {"ok": False, "error": str(e)}
