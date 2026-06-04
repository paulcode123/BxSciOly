# Database (Neon Postgres)

Member accounts and login live in **Neon Postgres**, provisioned through the Vercel project `bxscioly`. Everything else (events, meetings, binders, etc.) still uses **Firebase Firestore** until a feature is migrated.

## Connection

- Production and preview: Vercel injects `DATABASE_URL` automatically (Neon integration).
- Local dev: run `npx vercel env pull .env.local` from the repo root (requires Vercel CLI login).

## Schema

- SQL source of truth: `db/schema.sql`
- Apply locally: `python scripts/db/apply_schema.py`

## Tables

| Table | Purpose |
|-------|---------|
| `members` | Login, profiles, `admin_status`, notification prefs |
| `password_resets` | One-time password reset tokens |

Passwords are stored as **bcrypt hashes** only. API responses never include `password` or `password_hash`.

## Common tasks (tell Cursor)

Examples the board can paste into Cursor:

- *"Grant full admin to jane.doe@nycstudents.net"* → updates `members.admin_status` to `full`
- *"List all members with admin status"* → SQL or admin API
- *"Export member emails for the team"* → query `doe_email`, `personal_email`
- *"Re-run Firebase member import"* → `python scripts/db/migrate_from_firebase.py` (one-time / refresh only)

Use scripts under `scripts/db/` for repeatable changes; avoid hand-editing production without a review.

## Auth flow

1. Browser `POST /api/auth/login` with `doeEmail` + `password`
2. Server verifies bcrypt hash in Postgres
3. Client stores public profile via `BxSciOlyAuth` (no password in response)

## One-time migration from Firebase

```bash
python scripts/db/apply_schema.py
python scripts/db/migrate_from_firebase.py
```

For a dedicated export service account, grant **Cloud Datastore User** (`roles/datastore.user`) on project `bxscioly-455318`. Artifact Registry roles do not include Firestore.

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\your-key.json"
python scripts/db/migrate_from_firebase.py
```

If `service_key.json` is expired (`invalid_grant`), regenerate the key in Google Cloud IAM, or export the `Members` collection to JSON and run:

```bash
python scripts/db/import_members_json.py data/members_export.json
```

After migration, redeploy on Vercel so production uses the new login API.

## Legacy Firebase

- `database.txt` describes the old Firestore layout.
- Firestore `Members` is **deprecated** once Neon is populated; other collections remain on Firebase.
