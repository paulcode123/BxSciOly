# Agent instructions — BxSciOly

## Database (members / login)

- **Postgres (Neon)** holds `members` and `password_resets`. Use `DATABASE_URL` from `.env.local` or Vercel env.
- **Firestore** is still used for non-member collections (Events, Meeting, Binders, etc.).
- Read `docs/DATABASE.md` and `db/schema.sql` before changing auth or member data.
- Use `from db import members as members_db` or `from routes import member_store` — do not add new `db.collection('Members')` calls.
- Never log or return plaintext passwords. Hash with `members_db.hash_password` / verify with `members_db.verify_password`.
- Prefer `scripts/db/*.py` for one-off data changes.

## Deploy

- App deploys on Vercel (`bxscioly`). After schema changes, run `scripts/db/apply_schema.py` against the target database (usually via pulled production `DATABASE_URL` only when intentional).
