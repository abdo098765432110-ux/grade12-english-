-- ============================================================================
-- Learn for Grade 12 — the visitor register (Supabase, free plan)
--
-- Run this whole file ONCE in your Supabase project:
--   Supabase Dashboard → SQL Editor → New query → paste → Run.
-- Running it again is safe (it only creates what is missing and replaces the
-- functions and policies with the same ones).
--
-- What it makes:
--   public.visitors   one row per registered student (per device):
--                     the full three-part Arabic name, the first registration
--                     time, the last visit time and the number of visits.
--   public.visits     the visit history: one row each time a registered
--                     student opens the site (a new browser session).
--   public.founders   the accounts allowed to read the register (only you).
--
-- Security (Row Level Security):
--   * Students (the public "anon" key used by the website) can NOT read,
--     change or delete anything in these tables. They can only call two
--     functions: register_visitor (adds a new student, or counts a return
--     visit for one that already exists) and touch_visitor (counts a return
--     visit). Both check the name and never change an existing name.
--   * Only a signed-in account listed in public.founders can read the
--     register (select). Nobody can update or delete rows through the API;
--     you can still edit rows yourself in the Supabase Table Editor.
--   * The website never uses the secret / service_role key.
-- ============================================================================

-- ---------------------------------------------------------------- the tables
create table if not exists public.visitors (
  id          uuid primary key,                       -- made by the student's browser, kept on that device
  full_name   text not null check (char_length(full_name) between 8 and 80),
  first_seen  timestamptz not null default now(),     -- first registration
  last_seen   timestamptz not null default now(),     -- last visit
  visits      integer not null default 1 check (visits >= 1)
);

create table if not exists public.visits (
  id          bigint generated always as identity primary key,
  visitor_id  uuid not null references public.visitors (id) on delete cascade,
  visited_at  timestamptz not null default now(),
  kind        text not null check (kind in ('register', 'return'))
);
create index if not exists visits_visited_at on public.visits (visited_at desc);
create index if not exists visits_visitor on public.visits (visitor_id);

create table if not exists public.founders (
  user_id     uuid primary key references auth.users (id) on delete cascade
);

alter table public.visitors enable row level security;
alter table public.visits   enable row level security;
alter table public.founders enable row level security;

-- No direct access for the public key; the founder may only read.
revoke all on public.visitors, public.visits, public.founders from public, anon, authenticated;
grant select on public.visitors, public.visits to authenticated;

-- ---------------------------------------------------------------- who is the founder
create or replace function public.is_founder()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (select 1 from public.founders f where f.user_id = (select auth.uid()));
$$;
revoke execute on function public.is_founder() from public, anon;
grant execute on function public.is_founder() to authenticated;

drop policy if exists "founder reads visitors" on public.visitors;
create policy "founder reads visitors" on public.visitors
  for select to authenticated using ((select public.is_founder()));

drop policy if exists "founder reads visits" on public.visits;
create policy "founder reads visits" on public.visits
  for select to authenticated using ((select public.is_founder()));
-- (no insert / update / delete policies: nobody can write through the API)

-- ---------------------------------------------------------------- the name check
-- A full Arabic name of at least three parts: Arabic letters only, each part at
-- least two letters. Extra spaces, tatweel (ـ) and short vowels are removed.
-- Returns the cleaned name, or raises an error.
create or replace function public.clean_visitor_name(p_name text)
returns text
language plpgsql
immutable
set search_path = ''
as $$
declare
  v text;
begin
  v := coalesce(p_name, '');
  v := regexp_replace(v, '[ـً-ٰٟ]', '', 'g');           -- tatweel (ـ) and short vowels
  v := regexp_replace(v, '[[:space:]]+', ' ', 'g');
  v := btrim(v);
  if char_length(v) > 80 then
    raise exception 'name too long' using errcode = '22023';
  end if;
  if v !~ '^[ء-ي]{2,}( [ء-ي]{2,}){2,}$' then
    raise exception 'a full three-part Arabic name is required' using errcode = '22023';
  end if;
  return v;
end;
$$;
revoke execute on function public.clean_visitor_name(text) from public, anon, authenticated;

-- ---------------------------------------------------------------- what the website calls
-- A new student: adds the row. A student already registered on that device
-- (same id): keeps the original row and name, and counts a return visit.
-- Returns 'new' or 'returning'.
create or replace function public.register_visitor(p_id uuid, p_name text)
returns text
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  v_name text := public.clean_visitor_name(p_name);
begin
  if p_id is null then
    raise exception 'missing visitor id' using errcode = '22023';
  end if;
  insert into public.visitors (id, full_name) values (p_id, v_name)
    on conflict (id) do nothing;
  if found then
    insert into public.visits (visitor_id, kind) values (p_id, 'register');
    return 'new';
  end if;
  update public.visitors set last_seen = now(), visits = visits + 1 where id = p_id;
  insert into public.visits (visitor_id, kind) values (p_id, 'return');
  return 'returning';
end;
$$;

-- A return visit (a new browser session) of a registered student. Returns
-- false if this id is not in the register (the website then registers again).
create or replace function public.touch_visitor(p_id uuid)
returns boolean
language plpgsql
volatile
security definer
set search_path = ''
as $$
begin
  update public.visitors set last_seen = now(), visits = visits + 1 where id = p_id;
  if not found then
    return false;
  end if;
  insert into public.visits (visitor_id, kind) values (p_id, 'return');
  return true;
end;
$$;

revoke execute on function public.register_visitor(uuid, text) from public;
revoke execute on function public.touch_visitor(uuid) from public;
grant execute on function public.register_visitor(uuid, text) to anon, authenticated;
grant execute on function public.touch_visitor(uuid) to anon, authenticated;

-- ============================================================================
-- After creating your founder account (Authentication → Users → Add user),
-- run this ONE line in a new query, with YOUR email in place of the example:
--
--   insert into public.founders (user_id) select id from auth.users where email = 'your-email@example.com';
--
-- ============================================================================
