
print("DATABASE_URL >>>", DATABASE_URL)

import os
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")  # Supabase Postgres connection string
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")  # set this in Railway variables

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Provide Supabase Postgres connection string.")

app = FastAPI(title="AI Suit Project Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True)

class LeadIn(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: str = Field("", max_length=80)
    message: str = Field("", max_length=1000)

@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.now(timezone.utc).isoformat()}

@app.post("/api/leads")
def create_lead(payload: LeadIn, request: Request):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                insert into leads (full_name, email, role, message, ip_address)
                values (%s, %s, %s, %s, %s)
                returning id, full_name, email, role, message, created_at;
                """,
                (payload.full_name.strip(), payload.email, payload.role.strip(), payload.message.strip(), request.client.host if request.client else None)
            )
            row = cur.fetchone()
            return row

def check_admin(x_admin_token: str = Header(default="")):
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.get("/api/leads", dependencies=[Depends(check_admin)])
def list_leads(limit: int = 200):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("select id, full_name, email, role, message, created_at from leads order by created_at desc limit %s;", (limit,))
            rows = cur.fetchall()
            return rows

ADMIN_HTML = """
<!doctype html>
<meta charset="utf-8">
<title>Leads — AI Suit Project</title>
<style>
  body{font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto; margin:0; background:#0b0b0b; color:#fff}
  .wrap{max-width:1000px;margin:40px auto;padding:0 16px}
  h1{font-weight:700; letter-spacing:-.02em}
  table{width:100%; border-collapse:collapse; margin-top:16px; background:#111; border:1px solid #222}
  th,td{padding:12px 10px; border-bottom:1px solid #222; font-size:14px; vertical-align:top}
  input{padding:10px 12px; border-radius:10px; border:1px solid #333; background:#0e0e0e; color:#fff; width:380px}
  button{padding:10px 14px; border-radius:10px; border:0; background:#fff; color:#000; font-weight:700; margin-left:8px}
  .muted{color:#aaa; font-size:12px}
</style>
<div class="wrap">
  <h1>AI Suit Project — Leads</h1>
  <div class="muted">Enter your admin token (set as <code>ADMIN_TOKEN</code> on Railway).</div>
  <p><input id="token" placeholder="ADMIN_TOKEN"> <button onclick="load()">Load</button></p>
  <table id="t"><thead><tr><th>When</th><th>Name</th><th>Email</th><th>Role</th><th>Message</th></tr></thead><tbody></tbody></table>
</div>
<script>
async function load(){
  const token = document.getElementById('token').value.trim();
  const res = await fetch('/api/leads', {headers: {'X-Admin-Token': token}});
  if(!res.ok){ alert('Auth failed'); return; }
  const data = await res.json();
  const tb = document.querySelector('#t tbody');
  tb.innerHTML = '';
  for(const r of data){
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${new Date(r.created_at).toLocaleString()}</td><td>${r.full_name}</td><td>${r.email}</td><td>${r.role||''}</td><td>${(r.message||'').replace(/</g,'&lt;')}</td>`;
    tb.appendChild(tr);
  }
}
</script>
"""
@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return HTMLResponse(ADMIN_HTML)

@app.get("/", response_class=HTMLResponse)
def index():
    path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    return FileResponse(path)
