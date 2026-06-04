-- Bronx Science Olympiad — Postgres schema (Neon)

CREATE TABLE IF NOT EXISTS members (
    id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    doe_email TEXT NOT NULL,
    personal_email TEXT,
    phone_number TEXT,
    grade TEXT,
    password_hash TEXT NOT NULL,
    member_status TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio TEXT,
    interest_reason TEXT,
    how_did_you_hear_about_us TEXT,
    past_experience TEXT,
    return_reason TEXT,
    years_in_team INTEGER,
    preseason_hrs DOUBLE PRECISION,
    regseason_hrs DOUBLE PRECISION,
    postseason_hrs DOUBLE PRECISION,
    profile_pic_url TEXT,
    important_notification TEXT,
    team_notification TEXT,
    event_notification TEXT,
    house TEXT,
    admin_status TEXT NOT NULL DEFAULT 'none',
    extra JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE UNIQUE INDEX IF NOT EXISTS members_doe_email_lower_idx
    ON members (LOWER(doe_email));

CREATE INDEX IF NOT EXISTS members_last_name_idx ON members (last_name);

CREATE TABLE IF NOT EXISTS password_resets (
    token TEXT PRIMARY KEY,
    member_id TEXT NOT NULL REFERENCES members (id) ON DELETE CASCADE,
    doe_email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_in_seconds INTEGER NOT NULL DEFAULT 3600,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    used_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS password_resets_member_id_idx ON password_resets (member_id);

CREATE TABLE IF NOT EXISTS merch_orders (
    id TEXT PRIMARY KEY,
    member_id TEXT NOT NULL REFERENCES members (id) ON DELETE CASCADE,
    design_votes JSONB NOT NULL DEFAULT '[]'::jsonb,
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    spend_limit DOUBLE PRECISION,
    status TEXT NOT NULL DEFAULT 'pending',
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS merch_orders_member_id_idx ON merch_orders (member_id);
