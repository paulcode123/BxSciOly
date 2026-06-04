# Agent instructions — BxSciOly

## Database (Neon Postgres)

- All app data uses **Neon Postgres** via `DATABASE_URL` (Vercel env or `.env.local`).
- Schema: `db/schema.sql` — `members`, `password_resets`, `merch_orders`.
- Use `from db import members as members_db` or `from routes import member_store`.
- Never log or return plaintext passwords.

## API

- **Live:** `routes/api_routes.py` — auth, members, merch, roster-status.
- **Stub (503):** `routes/stub_routes.py` — legacy Firebase-backed endpoints until migrated.
- Do not reintroduce `firebase_routes` or Firestore.

## Deploy

- App deploys on Vercel (`bxscioly`). After schema changes: `python scripts/db/apply_schema.py`.
