# Database (Neon Postgres)

All production data is in **Neon Postgres** (`DATABASE_URL` on Vercel or `.env.local` locally).

## Schema

- Source of truth: `db/schema.sql`
- Apply: `python scripts/db/apply_schema.py`

## Tables

| Table | Purpose |
|-------|---------|
| `members` | Accounts, profiles, `admin_status`, notification prefs |
| `password_resets` | One-time password reset tokens |
| `merch_orders` | Team merch design votes and item selections (one order per member) |

Passwords are **bcrypt** hashes only. API responses never include `password` or `password_hash`.

## Auth

1. `POST /api/auth/login` with `doeEmail` + `password`
2. Server verifies bcrypt hash in Postgres
3. Client stores profile via `BxSciOlyAuth` (no password in response)

## Merch eligibility

A member can order merch if they have `admin_status` ≠ `none`, a non-empty `house`, or `member_status` = `returning`.

## Scripts

- `scripts/db/apply_schema.py` — apply schema
- `scripts/db/set_admin.py` — grant admin
- `scripts/db/import_members_json.py` — bulk import from JSON export
