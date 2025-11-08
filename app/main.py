from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client
import os

app = FastAPI()

# ENV VARS
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class Lead(BaseModel):
    full_name: str
    email: str
    role: str | None = None
    message: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/leads")
def create_lead(lead: Lead):
    supabase.table("leads").insert({
        "full_name": lead.full_name,
        "email": lead.email,
        "role": lead.role,
        "message": lead.message
    }).execute()

    return {"status": "saved"}
