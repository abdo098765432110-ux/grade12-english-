"""Tests tools/visitors/supabase-setup.sql on a local PostgreSQL that copies the
parts of Supabase it relies on: the roles anon and authenticated, auth.users,
auth.uid() (the signed-in user's id), and Supabase's default grants (every new
table and function in the public schema is open to anon and authenticated, so
the file must close them itself).

    python3 tests/visitors_sql_test.py [host-folder] [port]

Needs a running PostgreSQL 16 server you can reach as the postgres user (for
example: initdb, then pg_ctl start). It creates and drops the database
"visitors_test". Exits with code 1 if a check fails."""
import pathlib
import subprocess
import sys
import uuid

HOST = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pgvis"
PORT = sys.argv[2] if len(sys.argv) > 2 else "55432"
SQL = pathlib.Path(__file__).resolve().parent.parent / "tools" / "visitors" / "supabase-setup.sql"
DB = "visitors_test"
results = []


def psql(sql, db=DB, role=None, user=None):
    """Runs sql (as the role, and as the signed-in user id if given). Returns (ok, output)."""
    prefix = ""
    if user:
        prefix += "set request.jwt.claim.sub = '%s';\n" % user
    if role:
        prefix += "set role %s;\n" % role
    run = subprocess.run(["psql", "-h", HOST, "-p", PORT, "-U", "postgres", "-d", db, "-v", "ON_ERROR_STOP=1", "-Atq", "-c", prefix + sql],
                         capture_output=True, text=True)
    return run.returncode == 0, (run.stdout.strip() if run.returncode == 0 else run.stderr.strip())


def check(label, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else "  →  " + detail))


def expect(label, sql, want, role=None, user=None):
    ok, out = psql(sql, role=role, user=user)
    check(label, ok and out == want, out)


def refused(label, sql, role=None, user=None, words=("permission denied",)):
    ok, out = psql(sql, role=role, user=user)
    check(label, not ok and any(w in out for w in words), out)


def main():
    psql("drop database if exists %s;" % DB, db="postgres")
    ok, out = psql("create database %s;" % DB, db="postgres")
    assert ok, out
    # what a Supabase project already has
    ok, out = psql("""
      do $$ begin
        if not exists (select 1 from pg_roles where rolname = 'anon') then create role anon nologin; end if;
        if not exists (select 1 from pg_roles where rolname = 'authenticated') then create role authenticated nologin; end if;
      end $$;
      create schema auth;
      create table auth.users (id uuid primary key, email text unique);
      create function auth.uid() returns uuid language sql stable
        as $f$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $f$;
      grant usage on schema auth to anon, authenticated;
      grant execute on function auth.uid() to anon, authenticated;
      grant usage on schema public to anon, authenticated;
      alter default privileges in schema public grant all on tables to anon, authenticated;
      alter default privileges in schema public grant all on functions to anon, authenticated;
      alter default privileges in schema public grant all on sequences to anon, authenticated;
    """)
    assert ok, out
    sql = SQL.read_text(encoding="utf-8")
    ok, out = psql(sql)
    check("the setup file runs without an error", ok, out)
    ok, out = psql(sql)
    check("running the setup file a second time is safe", ok, out)

    founder, other = str(uuid.uuid4()), str(uuid.uuid4())
    psql("insert into auth.users values ('%s', 'founder@example.com'), ('%s', 'someone@example.com');" % (founder, other))
    ok, out = psql("insert into public.founders (user_id) select id from auth.users where email = 'founder@example.com';")
    check("the founder line from the end of the file works", ok, out)

    a, b, c = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    # --- a student (the website's public key = role anon)
    expect("a new student is registered → 'new'", "select public.register_visitor('%s', 'أحمد محمد علي');" % a, "new", role="anon")
    expect("names are cleaned (spaces, tatweel, short vowels)",
           "select public.register_visitor('%s', '  مُحَمَّـد   عبد الله    حسن ');" % b, "new", role="anon")
    expect("a four-part name is accepted", "select public.register_visitor('%s', 'سارة أحمد محمود السيد');" % c, "new", role="anon")
    expect("the same student again (same device id) → 'returning'", "select public.register_visitor('%s', 'أحمد محمد علي');" % a, "returning", role="anon")
    expect("the same device id with another name keeps the original record",
           "select public.register_visitor('%s', 'اسم آخر مختلف');" % a, "returning", role="anon")
    expect("a return visit of a registered student → true", "select public.touch_visitor('%s');" % b, "t", role="anon")
    expect("a return visit of an unknown id → false (the website registers again)", "select public.touch_visitor('%s');" % uuid.uuid4(), "f", role="anon")
    for bad, why in [("أحمد محمد", "two parts"), ("أحمد", "one part"), ("", "empty"), ("   ", "spaces only"),
                     ("Ahmed Mohamed Ali", "Latin letters"), ("أحمد م علي", "a one-letter part"), ("أحمد محمد 3", "a digit"),
                     ("أحمد محمد علي٣", "an Arabic digit"), ("أحمد <b>محمد</b> علي", "HTML"), ("أحمد " * 20, "too long")]:
        refused("a name with %s is refused" % why, "select public.register_visitor('%s', '%s');" % (uuid.uuid4(), bad),
                role="anon", words=("three-part", "too long"))
    refused("a missing id is refused", "select public.register_visitor(null, 'أحمد محمد علي');", role="anon", words=("missing visitor id",))
    # students can not read, change or delete the register
    refused("a student can not read the register", "select count(*) from public.visitors;", role="anon")
    refused("a student can not read the visit history", "select count(*) from public.visits;", role="anon")
    refused("a student can not read the founders", "select count(*) from public.founders;", role="anon")
    refused("a student can not add a row directly", "insert into public.visitors (id, full_name) values ('%s', 'أحمد محمد علي');" % uuid.uuid4(), role="anon")
    refused("a student can not change a row", "update public.visitors set full_name = 'تغيير الاسم هنا';", role="anon")
    refused("a student can not delete a row", "delete from public.visitors;", role="anon")
    refused("a student can not delete the history", "delete from public.visits;", role="anon")
    refused("a student can not make himself a founder", "insert into public.founders values ('%s');" % other, role="anon")
    refused("a student can not call the founder check", "select public.is_founder();", role="anon")
    refused("a student can not call the name check directly", "select public.clean_visitor_name('أحمد محمد علي');", role="anon")
    # --- a signed-in account that is not the founder
    expect("another signed-in account sees no student (RLS)", "select count(*) from public.visitors;", "0", role="authenticated", user=other)
    expect("… and no visit", "select count(*) from public.visits;", "0", role="authenticated", user=other)
    expect("… and is not the founder", "select public.is_founder();", "f", role="authenticated", user=other)
    refused("… and can not change a row", "update public.visitors set full_name = 'تغيير الاسم هنا';", role="authenticated", user=other)
    refused("… and can not make itself a founder", "insert into public.founders values ('%s');" % other, role="authenticated", user=other)
    # --- the founder
    expect("the founder is the founder", "select public.is_founder();", "t", role="authenticated", user=founder)
    expect("the founder sees every student, once each (3 unique students)", "select count(*) from public.visitors;", "3", role="authenticated", user=founder)
    expect("the original name was kept, and the visits were counted",
           "select full_name || '|' || visits from public.visitors where id = '%s';" % a, "أحمد محمد علي|3", role="authenticated", user=founder)
    expect("the cleaned name was stored", "select full_name from public.visitors where id = '%s';" % b, "محمد عبد الله حسن", role="authenticated", user=founder)
    expect("last visit moves forward, first registration stays",
           "select (last_seen >= first_seen)::text from public.visitors where id = '%s';" % a, "true", role="authenticated", user=founder)
    expect("the visit history has every visit in order (3 registrations, 3 returns)",
           "select string_agg(kind, ',' order by id) from public.visits;", "register,register,register,return,return,return",
           role="authenticated", user=founder)
    refused("even the founder can not change a row through the API", "update public.visitors set full_name = 'تغيير الاسم هنا';",
            role="authenticated", user=founder)
    refused("even the founder can not delete through the API", "delete from public.visitors;", role="authenticated", user=founder)
    # nothing is lost
    expect("rows stay (nothing deletes them)", "select count(*) from public.visitors;", "3")
    psql("drop database if exists %s;" % DB, db="postgres")
    print("%d checks, %d failed" % (len(results), results.count(False)))
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
