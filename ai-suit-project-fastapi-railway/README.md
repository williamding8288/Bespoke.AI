# AI Suit Project — FastAPI Backend (Railway) + Supabase (Postgres)

Real submission pipeline: HTML landing → FastAPI on Railway → Supabase Postgres.

## Endpoints
- `/` serves the elegant landing
- `POST /api/leads` saves Name/Email/Role/Message to Postgres
- `GET /api/leads` (admin only) returns JSON (header `X-Admin-Token: <token>`)
- `/admin` simple viewer page (paste token → Load)

## Deploy (summary)
1) Create Supabase project → copy `DATABASE_URL` (Project Settings → Database → Connection string)
2) In Supabase SQL editor, run `app/models.sql`
3) Push this repo to GitHub (or upload folder to Railway)
4) Create Railway project → Deploy with Dockerfile
5) Railway → Variables:
   - `DATABASE_URL` = (from Supabase)
   - `ADMIN_TOKEN` = (any long random string)
6) Open your Railway URL → submit the form → check `/admin`

## Dev
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgres://...
export ADMIN_TOKEN=dev-token
uvicorn app.main:app --reload
```