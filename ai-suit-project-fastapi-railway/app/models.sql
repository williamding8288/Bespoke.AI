
create table if not exists public.leads (
  id bigserial primary key,
  full_name text not null,
  email text not null,
  role text,
  message text,
  ip_address text,
  created_at timestamptz not null default now()
);
create index if not exists leads_created_at_idx on public.leads (created_at desc);
create index if not exists leads_email_idx on public.leads (email);
