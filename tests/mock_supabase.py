"""A small stand-in for the Supabase project, for the browser tests of the
registration screen and the founder's dashboard (tests/e2e_test.py).

It answers the requests visitor.js and founder.js make, the way the real project
does with tools/visitors/supabase-setup.sql (that file itself is tested on a
real PostgreSQL by tests/visitors_sql_test.py):
  POST /rest/v1/rpc/register_visitor, touch_visitor, is_founder
  GET  /rest/v1/visitors, /rest/v1/visits      only for the founder's token
  POST /auth/v1/token?grant_type=password | refresh_token, /auth/v1/logout
The public key may only call the two functions; reading the tables with it is
refused, and another signed-in account reads nothing (Row Level Security).
Set .down = True to answer 503 (the project paused or no internet)."""
import datetime
import http.server
import json
import re
import threading
import urllib.parse
import uuid

KEY = "sb_publishable_test_key"
FOUNDER = ("founder@example.com", "founder-pass-2026")
OTHER = ("someone@example.com", "other-pass-2026")
NAME = re.compile(r"^[ء-ي]{2,}( [ء-ي]{2,}){2,}$")


def clean(name):
    v = re.sub(r"[ـً-ٰٟ]", "", name or "")
    return re.sub(r"\s+", " ", v).strip()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class Mock:
    def __init__(self):
        self.visitors = {}       # id → row
        self.visits = []         # rows, oldest first
        self.tokens = {}         # access token → email
        self.refresh = {}        # refresh token → email
        self.calls = []          # (method, path) of every request with the key
        self.down = False
        self.lock = threading.Lock()
        mock = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def cors(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "apikey, authorization, content-type, range, x-client-info, prefer")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

            def reply(self, status, body=None):
                self.send_response(status)
                self.cors()
                if status == 204:          # no content (like the real sign-out answer)
                    self.end_headers()
                    return
                data = json.dumps(body, ensure_ascii=False).encode("utf-8")
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_OPTIONS(self):
                self.send_response(204)
                self.cors()
                self.end_headers()

            def do_GET(self):
                mock.handle(self, "GET")

            def do_POST(self):
                mock.handle(self, "POST")

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:%d" % self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()

    # ---------------------------------------------------------------- the database
    def register(self, vid, name):
        name = clean(name)
        if len(name) > 80 or not NAME.match(name):
            return 400, {"code": "22023", "message": "a full three-part Arabic name is required"}
        with self.lock:
            if vid in self.visitors:
                row = self.visitors[vid]
                row["last_seen"] = now()
                row["visits"] += 1
                self.visits.append({"visitor_id": vid, "visited_at": now(), "kind": "return"})
                return 200, "returning"
            t = now()
            self.visitors[vid] = {"id": vid, "full_name": name, "first_seen": t, "last_seen": t, "visits": 1}
            self.visits.append({"visitor_id": vid, "visited_at": t, "kind": "register"})
            return 200, "new"

    def touch(self, vid):
        with self.lock:
            row = self.visitors.get(vid)
            if not row:
                return 200, False
            row["last_seen"] = now()
            row["visits"] += 1
            self.visits.append({"visitor_id": vid, "visited_at": now(), "kind": "return"})
            return 200, True

    def count(self, path):
        return sum(1 for m, p in self.calls if p == path)

    # ---------------------------------------------------------------- requests
    def handle(self, h, method):
        parsed = urllib.parse.urlparse(h.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        length = int(h.headers.get("Content-Length") or 0)
        body = json.loads(h.rfile.read(length) or b"{}") if length else {}
        if h.headers.get("apikey") != KEY:
            return h.reply(401, {"message": "Invalid API key"})
        self.calls.append((method, path))
        if self.down:
            return h.reply(503, {"message": "project paused"})
        bearer = (h.headers.get("Authorization") or "").replace("Bearer ", "")
        user = self.tokens.get(bearer)
        if path == "/auth/v1/token" and method == "POST":
            grant = query.get("grant_type", [""])[0]
            if grant == "password":
                pair = (body.get("email"), body.get("password"))
                if pair not in (FOUNDER, OTHER):
                    return h.reply(400, {"error": "invalid_grant", "error_description": "Invalid login credentials"})
                email = pair[0]
            elif grant == "refresh_token" and body.get("refresh_token") in self.refresh:
                email = self.refresh.pop(body["refresh_token"])
            else:
                return h.reply(400, {"error": "invalid_grant"})
            access, refresh = uuid.uuid4().hex, uuid.uuid4().hex
            self.tokens[access] = email
            self.refresh[refresh] = email
            return h.reply(200, {"access_token": access, "refresh_token": refresh, "expires_in": 3600, "token_type": "bearer", "user": {"email": email}})
        if path == "/auth/v1/logout" and method == "POST":
            self.tokens.pop(bearer, None)
            return h.reply(204)
        if path == "/rest/v1/rpc/register_visitor" and method == "POST":
            try:
                vid = str(uuid.UUID(str(body.get("p_id"))))
            except ValueError:
                return h.reply(400, {"code": "22P02"})
            status, result = self.register(vid, body.get("p_name"))
            return h.reply(status, result)
        if path == "/rest/v1/rpc/touch_visitor" and method == "POST":
            status, result = self.touch(str(body.get("p_id")))
            return h.reply(status, result)
        if path == "/rest/v1/rpc/is_founder" and method == "POST":
            if not user:
                return h.reply(401, {"code": "42501", "message": "permission denied for function is_founder"})
            return h.reply(200, user == FOUNDER[0])
        if path in ("/rest/v1/visitors", "/rest/v1/visits") and method == "GET":
            if not user:
                return h.reply(401, {"code": "42501", "message": "permission denied for table"})
            if user != FOUNDER[0]:
                return h.reply(200, [])            # RLS: no row for another account
            with self.lock:
                if path.endswith("visitors"):
                    rows = list(self.visitors.values())
                else:
                    rows = list(self.visits)
                    since = query.get("visited_at", [""])[0]
                    if since.startswith("gte."):
                        rows = [r for r in rows if r["visited_at"] >= since[4:]]
            order = query.get("order", [""])[0]
            if order:
                field, _, direction = order.partition(".")
                rows.sort(key=lambda r: r[field], reverse=direction == "desc")
            offset = int(query.get("offset", ["0"])[0])
            limit = int(query.get("limit", ["1000"])[0])
            fields = query.get("select", ["*"])[0].split(",")
            rows = [{k: r[k] for k in r if fields == ["*"] or k in fields} for r in rows[offset:offset + limit]]
            return h.reply(200, rows)
        return h.reply(404, {"message": "not found"})
