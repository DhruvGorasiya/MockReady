---
name: Database Connection — Supabase Session Pooler
description: How to connect to the Supabase database correctly (Session Pooler, not direct)
type: project
---

The direct Supabase connection (`db.gesbqomvmnykadzqmkwa.supabase.co:5432`) does NOT work — it requires IPv6 and the machine is on IPv4-only network.

**Use the Session Pooler URL instead.**

The `DATABASE_URL` in `backend/.env` must use:
- Host: `aws-0-*.pooler.supabase.com` (Session Pooler)
- User: `postgres.[project-ref]` (project ref appended to username)
- Prefix: `postgresql+asyncpg://` (NOT `postgresql://` — asyncpg is required for SQLAlchemy async)
- Port: `5432`

Example format:
```
DATABASE_URL=postgresql+asyncpg://postgres.gesbqomvmnykadzqmkwa:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

**Why:** Supabase free tier uses IPv6 for direct connections. Session Pooler is IPv4-compatible.
**How to apply:** Any time DATABASE_URL is set or migrations are run, verify this format is used.
