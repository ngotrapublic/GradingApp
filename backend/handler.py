"""HTTP handler: static files + JSON API (/api/...). Runs on the laptop (server.py) and on Vercel (api/index.py).

Staff (admin / lecturer / TA) sign in with username + password; students with student ID + password.
Per class: the owner (lecturer) and the admin may do everything ('manage'); a TA may grade and open cards / submissions ('grade')."""
import base64, http.server, io, json, os, re, socketserver, urllib.parse

from .config import LOCK, PORT, STATIC
from .courses import COURSES, asset, keys
from .db import (ROLES, add_hit, allow, as_int, assign_random, check_pw, class_role, connect, count_hits, delete_class, hash_pw,
                 load, new_session, now, set_gradebook, set_sync, set_team_mark, upsert_student, user_from_token, visible_class_ids)
from .network import lan_ips, qr_svg
from .scoring import export_xlsx, score, variant

PUBLIC_URL = os.environ.get('PUBLIC_URL', '').rstrip('/')
ON_VERCEL = bool(os.environ.get('VERCEL'))
TOO_MANY = {'error': 'Too many tries. Wait a few minutes.', 'error_vi': 'Thử quá nhiều lần. Đợi vài phút.'}
NO_RIGHT = {'error': 'You do not have the right to do this in this class.', 'error_vi': 'Bạn không có quyền làm việc này trong lớp này.'}
MANAGE, GRADE = ('admin', 'owner'), ('admin', 'owner', 'ta')
USERNAME = re.compile(r'[a-z0-9._-]{3,30}')


def err(en, vi):
    return {'error': en, 'error_vi': vi}


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=STATIC, **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        if not self.route_path().startswith('/api/'):              # web pages: always check for a newer version (after an update)
            self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    # ---------------- helpers ----------------
    def route_path(self):
        """Path used for API routing. Vercel rewrites /api/* → /api/index and may replace self.path;
        the original suffix is passed as ?__path= (see vercel.json)."""
        url = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(url.query)
        if qs.get('__path'):
            return '/api/' + qs['__path'][0].lstrip('/')
        for h in ('x-forwarded-uri', 'x-invoke-path'):
            raw = self.headers.get(h) or ''
            p = urllib.parse.urlparse(raw).path if raw else ''
            if not p and raw.startswith('/'):
                p = raw.split('?', 1)[0]
            if p.startswith('/api/') and p not in ('/api', '/api/', '/api/index', '/api/index.py'):
                return p
        return url.path

    def route_query(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        qs.pop('__path', None)
        return qs

    def ip(self):
        fwd = self.headers.get('X-Forwarded-For') if ON_VERCEL else None   # only trust the header behind Vercel's proxy
        return (fwd.split(',')[0].strip() if fwd else self.client_address[0]) or '?'

    def https(self):
        return ON_VERCEL or self.headers.get('X-Forwarded-Proto') == 'https'

    def cookie(self, name):
        c = self.headers.get('Cookie', '')
        return dict(p.strip().split('=', 1) for p in c.split(';') if '=' in p).get(name)

    def user(self, con):
        return user_from_token(con, self.cookie('tok'))

    def student(self, con):
        """The signed-in student (sid, name) or None."""
        tok = self.cookie('stu')
        r = tok and con.execute('SELECT s.sid, s.name FROM stu_sessions x JOIN students s ON s.sid=x.sid WHERE x.token=?', (tok,)).fetchone()
        return dict(r) if r else None

    def set_cookie(self, name, value, age, same='Strict'):
        return f'{name}={value}; Path=/; Max-Age={age}; SameSite={same}; HttpOnly' + ('; Secure' if self.https() else '')

    def send_json(self, obj, code=200, cookie=None):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers(); self.wfile.write(b)

    def send_bytes(self, b, ctype, cache='private, max-age=3600'):
        self.send_response(200); self.send_header('Content-Type', ctype); self.send_header('Cache-Control', cache)
        self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)

    def base_url(self):
        if PUBLIC_URL:
            return PUBLIC_URL
        if ON_VERCEL:
            return 'https://' + (self.headers.get('X-Forwarded-Host') or self.headers.get('Host') or '')
        ips = lan_ips()
        return f'http://{ips[0]}:{PORT}' if ips else ''

    # ---------------- GET ----------------
    def do_GET(self):
        path = self.route_path()
        query = self.route_query()
        if path.startswith('/api/public/'):     # student page – the student's own information only
            return self.public_get(path)
        if path == '/api/qr.svg':               # QR code of the page address (no secret inside)
            target = '/student/' if 'student' in query or (query.get('target') or [''])[0] == 'student' else ''
            base = self.base_url()
            if not base:
                return self.send_json(err('No Wi-Fi address found on this computer', 'Không tìm thấy địa chỉ wifi của máy'), 404)
            try:
                b = qr_svg(base + target)
            except ImportError:
                return self.send_json(err('The segno library is missing. Start the app with start.command to install it.', 'Thiếu thư viện segno. Chạy bằng start.command để tự cài.'), 500)
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml'); self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Url', base + target); self.send_header('Content-Length', str(len(b)))
            self.end_headers(); self.wfile.write(b); return
        if not path.startswith('/api/'):
            if path == '/':
                self.path = '/index.html'
            return super().do_GET()
        with connect() as con:
            me = self.user(con)
            if path == '/api/status':
                return self.send_json({'me': me})
            if not me:
                return self.send_json({'error': 'auth'}, 401)
            if path == '/api/keys':
                return self.send_json({c: keys(c) for c in COURSES})
            if path == '/api/data':
                return self.send_json(load(con, me))
            if path == '/api/users':            # admin: every account; lecturer: the TA accounts (to add a TA to a class)
                if me['role'] == 'admin':
                    rows = con.execute('SELECT id, username, name, role, active, created FROM users ORDER BY role, username').fetchall()
                else:
                    rows = con.execute("SELECT id, username, name, role FROM users WHERE role='ta' AND active=1 ORDER BY username").fetchall()
                return self.send_json({'users': [dict(r) for r in rows]})
            m = re.fullmatch(r'/api/photo/(\d+)\.jpg', path)
            if m:
                r = con.execute('SELECT class_id, data FROM photos WHERE id=?', (int(m.group(1)),)).fetchone()
                if not r or r['data'] is None or not class_role(con, me, r['class_id']):
                    return self.send_json({'error': 'not found'}, 404)
                return self.send_bytes(bytes(r['data']), 'image/jpeg')
            m = re.fullmatch(r'/api/asset/([A-Za-z0-9_-]+)/(.+)', path)
            if m:                               # private image of a course (e.g. Lab 3 scope screen) – staff only
                f = m.group(1) in COURSES and asset(m.group(1), urllib.parse.unquote(m.group(2)))
                return self.send_bytes(open(f, 'rb').read(), 'image/png') if f else self.send_json({'error': 'not found'}, 404)
            if path == '/api/export.xlsx':      # classes this user manages (or one class: ?cls=)
                ids = [i for i in visible_class_ids(con, me) if class_role(con, me, i) in MANAGE]
                if 'cls' in query:
                    ids = [i for i in ids if str(i) == query['cls'][0]]
                if not ids:
                    return self.send_json(NO_RIGHT, 403)
                try:
                    b = export_xlsx(list(load(con, me, ids).get('classes', {}).values()))
                except ImportError:
                    return self.send_json(err('The openpyxl library is missing. Start the app with start.command to install it.', 'Thiếu thư viện openpyxl. Chạy bằng start.command để tự cài.'), 500)
                self.send_response(200)
                self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                self.send_header('Content-Disposition', 'attachment; filename="Lab_marks.xlsx"')
                self.send_header('Content-Length', str(len(b)))
                self.end_headers(); self.wfile.write(b); return
            return self.send_json({'error': 'not found'}, 404)

    # ---------------- POST ----------------
    def do_POST(self):
        path = self.route_path()
        n = int(self.headers.get('Content-Length', '0') or 0)
        if n > 6_000_000:
            return self.send_json({'error': 'too large'}, 413)
        try:
            body = json.loads(self.rfile.read(n) or b'{}')
        except json.JSONDecodeError:
            return self.send_json({'error': 'bad json'}, 400)
        with LOCK, connect() as con:
            if path.startswith('/api/public/'):
                return self.public_post(con, path, body)
            if path == '/api/login':
                return self.staff_login(con, body)
            me = self.user(con)
            if not me:
                return self.send_json({'error': 'auth'}, 401)
            if path == '/api/logout':
                con.execute('DELETE FROM sessions WHERE token=?', (self.cookie('tok'),))
                return self.send_json({'ok': True}, cookie=self.set_cookie('tok', '', 0))
            if me['must_change'] and path != '/api/password':      # first sign-in with a given password: change it first
                return self.send_json(err('Change your password first.', 'Đổi mật khẩu trước đã.'), 403)
            if path == '/api/password':         # change my own password
                row = con.execute('SELECT pw FROM users WHERE id=?', (me['id'],)).fetchone()
                if me['username'] == 'admin' and os.environ.get('ADMIN_PASSWORD'):
                    return self.send_json(err('The admin password is set on the server (ADMIN_PASSWORD).', 'Mật khẩu admin đặt trên server (ADMIN_PASSWORD).'), 403)
                if not check_pw(str(body.get('old', '')), row['pw']):
                    return self.send_json(err('The current password is wrong.', 'Mật khẩu hiện tại sai.'), 403)
                if len(str(body.get('new', ''))) < 8:
                    return self.send_json(err('The new password needs at least 8 characters.', 'Mật khẩu mới cần ít nhất 8 ký tự.'), 400)
                if str(body['new']) == str(body.get('old', '')):
                    return self.send_json(err('Choose a new password, different from the current one.', 'Chọn mật khẩu mới, khác mật khẩu hiện tại.'), 400)
                con.execute('UPDATE users SET pw=?, must_change=0 WHERE id=?', (hash_pw(str(body['new'])), me['id']))
                con.execute('DELETE FROM sessions WHERE user_id=? AND token<>?', (me['id'], self.cookie('tok')))   # sign out other devices
                return self.send_json({'ok': True})
            if path in ('/api/user_create', '/api/user_update'):
                if me['role'] != 'admin':
                    return self.send_json(NO_RIGHT, 403)
                return self.create_user(con, body) if path == '/api/user_create' else self.update_user(con, me, body)
            if path == '/api/readsheet':        # .xlsx -> rows (first sheet), for the roster upload
                return self.read_sheet(body)
            if path == '/api/class_create':
                return self.class_create(con, me, body)
            # ----- everything below works on one class -----
            cid = as_int(body.get('cls'))
            role = class_role(con, me, cid) if cid else None
            if not role:
                return self.send_json(NO_RIGHT, 403)
            manage = role in MANAGE
            course = con.execute('SELECT course FROM classes WHERE id=?', (cid,)).fetchone()['course']
            K = keys(course)
            if path == '/api/class_update':     # name, term, variant set; the admin may also give the class to another lecturer
                if not manage: return self.send_json(NO_RIGHT, 403)
                if body.get('name'):
                    con.execute('UPDATE classes SET name=? WHERE id=?', (str(body['name']).strip()[:40], cid))
                if body.get('term'):
                    con.execute('UPDATE classes SET term=? WHERE id=?', (str(body['term']).strip()[:40], cid))
                if body.get('vset'):
                    vset = as_int(body['vset'])
                    if not vset or not 1 <= vset <= COURSES[course].get('sets', 1):
                        return self.send_json(err('No such variant set.', 'Không có bộ đề này.'), 400)
                    con.execute('UPDATE classes SET vset=? WHERE id=?', (vset, cid))
                if 'owner' in body and me['role'] == 'admin':
                    o = con.execute("SELECT id FROM users WHERE username=? AND role IN ('lecturer','admin')", (str(body['owner']),)).fetchone()
                    if not o: return self.send_json(err('No lecturer with this username.', 'Không có giảng viên với username này.'), 400)
                    con.execute('UPDATE classes SET owner=? WHERE id=?', (o['id'], cid))
            elif path == '/api/class_delete':
                if not manage: return self.send_json(NO_RIGHT, 403)
                delete_class(con, cid)
            elif path == '/api/staff_add':      # add a TA (by username) to this class
                if not manage: return self.send_json(NO_RIGHT, 403)
                u = con.execute("SELECT id FROM users WHERE username=? AND role='ta' AND active=1", (str(body.get('username', '')).strip().lower(),)).fetchone()
                if not u: return self.send_json(err('No TA account with this username. Ask the admin to create it.', 'Không có tài khoản TA với username này. Nhờ admin tạo.'), 400)
                con.execute('INSERT INTO class_staff VALUES (?, ?) ON CONFLICT DO NOTHING', (cid, u['id']))
            elif path == '/api/staff_remove':
                if not manage: return self.send_json(NO_RIGHT, 403)
                con.execute('DELETE FROM class_staff WHERE class_id=? AND user_id=?', (cid, as_int(body.get('user_id'))))
            elif path == '/api/class':          # full roster (replaces the list) + name
                if not manage: return self.send_json(NO_RIGHT, 403)
                if body.get('name'):
                    con.execute('UPDATE classes SET name=? WHERE id=?', (str(body['name']).strip()[:40], cid))
                if 'students' in body:
                    keep = []
                    for s in body['students']:
                        sid = str(s.get('sid', '')).strip().upper()
                        if not sid: continue
                        keep.append(sid)
                        upsert_student(con, cid, sid, str(s.get('name', '')).strip(), as_int(s.get('team')), as_int(s.get('member')))
                    q = ','.join('?' * len(keep))
                    con.execute(f'DELETE FROM enrollments WHERE class_id=? AND sid NOT IN ({q})' if keep else 'DELETE FROM enrollments WHERE class_id=?', (cid, *keep))
            elif path == '/api/roster_merge':   # add / update students, keep existing team & member
                if not manage: return self.send_json(NO_RIGHT, 403)
                for s in body.get('students', []):
                    sid = str(s.get('sid', '')).strip().upper()
                    if not sid: continue
                    old = con.execute('SELECT team, member FROM enrollments WHERE class_id=? AND sid=?', (cid, sid)).fetchone()
                    team = as_int(s.get('team')) or (old['team'] if old else None)
                    member = as_int(s.get('member')) or (old['member'] if old else None)
                    upsert_student(con, cid, sid, str(s.get('name', '')).strip(), team, member)
                assign_random(con, cid)
            elif path == '/api/shuffle':        # re-draw all teams of a class
                if not manage: return self.send_json(NO_RIGHT, 403)
                assign_random(con, cid, reshuffle=True)
            elif path == '/api/student_pw_reset':   # student forgot the password: they choose a new one at the next sign-in
                if not manage: return self.send_json(NO_RIGHT, 403)
                sid = str(body.get('sid', ''))
                if not con.execute('SELECT 1 FROM enrollments WHERE class_id=? AND sid=?', (cid, sid)).fetchone():
                    return self.send_json(NO_RIGHT, 403)
                con.execute('UPDATE students SET pw=NULL WHERE sid=?', (sid,))
                con.execute('DELETE FROM stu_sessions WHERE sid=?', (sid,))
                con.execute('DELETE FROM hits WHERE k=?', (f'stu-fail:{sid}',))
            elif path == '/api/record':         # one student's record for one lab
                lab = str(body['lab']); sid = str(body['sid'])
                if lab not in K['labs']: return self.send_json({'error': 'bad lab'}, 400)
                if 'override' in body and not manage: return self.send_json(NO_RIGHT, 403)
                con.execute('INSERT INTO records (class_id, lab, sid, tick, manual) VALUES (?,?,?,0,?) ON CONFLICT DO NOTHING', (cid, lab, sid, '{}'))
                if 'tick' in body: con.execute('UPDATE records SET tick=? WHERE class_id=? AND lab=? AND sid=?', (1 if body['tick'] else 0, cid, lab, sid))
                if 'values' in body: con.execute('UPDATE records SET vals=? WHERE class_id=? AND lab=? AND sid=?', (json.dumps(body['values']), cid, lab, sid))
                if 'manual' in body: con.execute('UPDATE records SET manual=? WHERE class_id=? AND lab=? AND sid=?', (json.dumps(body['manual']), cid, lab, sid))
                if 'src' in body: con.execute('UPDATE records SET src=? WHERE class_id=? AND lab=? AND sid=?', (str(body['src'])[:10], cid, lab, sid))
                if 'override' in body:          # manual score (None = back to the automatic score)
                    ov = body['override']
                    if ov is not None:
                        ov = float(ov)
                        if not 0 <= ov <= K['labs'][lab]['total']:
                            return self.send_json(err(f"Score must be 0–{K['labs'][lab]['total']}", f"Điểm phải từ 0 đến {K['labs'][lab]['total']}"), 400)
                    con.execute('UPDATE records SET override=?, reason=? WHERE class_id=? AND lab=? AND sid=?', (ov, str(body.get('reason', ''))[:200], cid, lab, sid))
                if 'show_marks' in body:        # release this student's marks on the student page (lecturer only)
                    if not manage: return self.send_json(NO_RIGHT, 403)
                    con.execute('UPDATE records SET show_marks=? WHERE class_id=? AND lab=? AND sid=?', (1 if body['show_marks'] else 0, cid, lab, sid))
                con.execute('UPDATE records SET updated=? WHERE class_id=? AND lab=? AND sid=?', (now(), cid, lab, sid))
            elif path == '/api/sync':           # remember what was sent to Canvas (+ the gradebook file)
                if not manage: return self.send_json(NO_RIGHT, 403)
                t = now()
                for lab, sc in body.get('scores', {}).items():
                    set_sync(con, cid, lab, t, sc)
                if body.get('gb'):
                    set_gradebook(con, cid, t, str(body.get('gbname', ''))[:80], body['gb'][:3000])
            elif path == '/api/publish':        # what students may see; releasing marks is for the lecturer only
                lab = str(body['lab'])
                if 'marks' in body and not manage: return self.send_json(NO_RIGHT, 403)
                con.execute('INSERT INTO publish (class_id, lab) VALUES (?, ?) ON CONFLICT DO NOTHING', (cid, lab))
                for k in ('card', 'marks', 'submit'):
                    if k in body:
                        con.execute(f'UPDATE publish SET {k}=? WHERE class_id=? AND lab=?', (1 if body[k] else 0, cid, lab))
            elif path == '/api/team':           # team-level manual marks (Lab 4 demo)
                if body.get('value') is None:   # tapping the selected mark again clears it
                    con.execute('DELETE FROM team_marks WHERE class_id=? AND lab=? AND team=? AND field=?', (cid, str(body['lab']), str(body['team']), body['field']))
                else:
                    set_team_mark(con, cid, body['lab'], body['team'], body['field'], body['value'])
            else:
                return self.send_json({'error': 'not found'}, 404)
            con.commit()
            return self.send_json(load(con, me))

    # ---------------- staff accounts ----------------
    def staff_login(self, con, body):
        username = str(body.get('username', '')).strip().lower()
        ip_key, user_key = 'login-fail:' + self.ip(), 'login-fail-user:' + username
        if count_hits(con, ip_key, 900) >= 10 or count_hits(con, user_key, 900) >= 8:      # wait 15 minutes
            return self.send_json(TOO_MANY, 429)
        u = con.execute('SELECT id, pw, active FROM users WHERE username=?', (username,)).fetchone()
        if u and u['active'] and check_pw(str(body.get('password', '')), u['pw']):
            return self.send_json({'ok': True}, cookie=self.set_cookie('tok', new_session(con, 'sessions', u['id']), 15552000))
        add_hit(con, ip_key); add_hit(con, user_key)
        return self.send_json(err('Wrong username or password.', 'Sai username hoặc mật khẩu.'), 403)

    def create_user(self, con, body):
        username = str(body.get('username', '')).strip().lower()
        role, pw = str(body.get('role', '')), str(body.get('password', ''))
        if not USERNAME.fullmatch(username):
            return self.send_json(err('Username: 3–30 characters, a–z, 0–9, dot, dash, underscore.', 'Username: 3–30 ký tự, a–z, 0–9, dấu chấm, gạch ngang, gạch dưới.'), 400)
        if role not in ROLES:
            return self.send_json(err('Unknown role.', 'Vai trò không hợp lệ.'), 400)
        if len(pw) < 8:
            return self.send_json(err('The password needs at least 8 characters.', 'Mật khẩu cần ít nhất 8 ký tự.'), 400)
        if con.execute('SELECT 1 FROM users WHERE username=?', (username,)).fetchone():
            return self.send_json(err('This username already exists.', 'Username này đã có.'), 400)
        uid = con.execute('INSERT INTO users (username, name, role, pw, created, must_change) VALUES (?,?,?,?,?,1) RETURNING id',
                          (username, str(body.get('name', '')).strip()[:60] or username, role, hash_pw(pw), now())).fetchone()[0]
        return self.send_json({'ok': True, 'id': uid})

    def update_user(self, con, me, body):
        uid = as_int(body.get('id'))
        u = con.execute('SELECT id, username FROM users WHERE id=?', (uid,)).fetchone()
        if not u:
            return self.send_json({'error': 'not found'}, 404)
        if u['id'] == me['id'] and ('active' in body or 'role' in body):
            return self.send_json(err('You cannot lock or change your own account here.', 'Không tự khóa / đổi vai trò tài khoản của mình ở đây.'), 400)
        if body.get('name'):
            con.execute('UPDATE users SET name=? WHERE id=?', (str(body['name']).strip()[:60], uid))
        if body.get('role') in ROLES:
            con.execute('UPDATE users SET role=? WHERE id=?', (body['role'], uid))
        if 'active' in body:
            con.execute('UPDATE users SET active=? WHERE id=?', (1 if body['active'] else 0, uid))
            if not body['active']:
                con.execute('DELETE FROM sessions WHERE user_id=?', (uid,))
        if body.get('password'):
            if len(str(body['password'])) < 8:
                return self.send_json(err('The password needs at least 8 characters.', 'Mật khẩu cần ít nhất 8 ký tự.'), 400)
            con.execute('UPDATE users SET pw=?, must_change=1 WHERE id=?', (hash_pw(str(body['password'])), uid))   # they choose their own at the next sign-in
            con.execute('DELETE FROM sessions WHERE user_id=?', (uid,))
        return self.send_json({'ok': True})

    def class_create(self, con, me, body):
        if me['role'] not in ('lecturer', 'admin'):
            return self.send_json(NO_RIGHT, 403)
        course, term, name = str(body.get('course', '')), str(body.get('term', '')).strip()[:40], str(body.get('name', '')).strip()[:40]
        vset = as_int(body.get('vset')) or 1
        if course not in COURSES or not term or not name:
            return self.send_json(err('Choose a course, a term and a class name.', 'Chọn môn, học kỳ và đặt tên lớp.'), 400)
        if not 1 <= vset <= COURSES[course].get('sets', 1):
            return self.send_json(err('No such variant set.', 'Không có bộ đề này.'), 400)
        owner = me['id']
        if me['role'] == 'admin' and body.get('owner'):
            o = con.execute("SELECT id FROM users WHERE username=? AND role IN ('lecturer','admin')", (str(body['owner']),)).fetchone()
            if not o: return self.send_json(err('No lecturer with this username.', 'Không có giảng viên với username này.'), 400)
            owner = o['id']
        cid = con.execute('INSERT INTO classes (course, term, name, vset, owner, created) VALUES (?,?,?,?,?,?) RETURNING id',
                          (course, term, name, vset, owner, now())).fetchone()[0]
        con.commit()
        return self.send_json({**load(con, me), 'created': cid})

    def read_sheet(self, body):
        try:
            from openpyxl import load_workbook
        except ImportError:
            return self.send_json(err('openpyxl is missing. Start with start.command, or save the file as CSV.', 'Thiếu openpyxl. Chạy bằng start.command, hoặc lưu file dạng CSV.'), 500)
        try:
            wb = load_workbook(io.BytesIO(base64.b64decode(body['b64'])), read_only=True, data_only=True)
            rows = [['' if v is None else (str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)) for v in r]
                    for r in wb.worksheets[0].iter_rows(values_only=True)]
        except Exception as e:
            return self.send_json(err(f'Could not read the file: {e}', f'Không đọc được file: {e}'), 400)
        return self.send_json({'rows': [r for r in rows if any(x.strip() for x in r)][:2000]})

    # ---------------- student page ----------------
    def enrolled(self, con, st, cid):
        """The class row if this student is in class `cid`."""
        if not st or not cid:
            return None
        return con.execute('SELECT c.id, c.course, c.vset FROM enrollments e JOIN classes c ON c.id=e.class_id WHERE e.class_id=? AND e.sid=?',
                           (cid, st['sid'])).fetchone()

    def public_get(self, path):
        with connect() as con:
            st = self.student(con)
            if not allow(con, 'get:' + self.ip(), 240):
                return self.send_json(TOO_MANY, 429)
            if not st:
                return self.send_json({'error': 'signin'}, 401)
            if path == '/api/public/me':        # my classes (all courses, all terms)
                rows = con.execute('SELECT c.id, c.course, c.term, c.name FROM enrollments e JOIN classes c ON c.id=e.class_id '
                                   'WHERE e.sid=? ORDER BY c.id DESC', (st['sid'],)).fetchall()
                return self.send_json({**st, 'classes': [{**dict(r), 'courseName': COURSES.get(r['course'], {}).get('name', r['course'])} for r in rows]})
            m = re.fullmatch(r'/api/public/class/(\d+)', path)
            if m:
                c = self.enrolled(con, st, int(m.group(1)))
                if not c:
                    return self.send_json({'error': 'not found'}, 404)
                return self.send_json(student_view(load(con, None, [c['id']])['classes'][str(c['id'])], st['sid']))
            m = re.fullmatch(r'/api/public/photo/(\d+)\.jpg', path)
            if m:                               # only the student's own photos
                r = con.execute('SELECT sid, data FROM photos WHERE id=?', (int(m.group(1)),)).fetchone()
                if not r or r['data'] is None or r['sid'] != st['sid']:
                    return self.send_json({'error': 'not found'}, 404)
                return self.send_bytes(bytes(r['data']), 'image/jpeg', 'no-store')
            m = re.fullmatch(r'/api/public/image/(\d+)/(\w+)\.png', path)
            if m:                               # the private image of my own variant (e.g. Lab 3 scope screen), when the card is open
                c = self.enrolled(con, st, int(m.group(1))); lab = m.group(2)
                pub = c and con.execute('SELECT card FROM publish WHERE class_id=? AND lab=?', (c['id'], lab)).fetchone()
                e = c and con.execute('SELECT team, member FROM enrollments WHERE class_id=? AND sid=?', (c['id'], st['sid'])).fetchone()
                v = e and variant(c['vset'], dict(e))
                V = v and keys(c['course'])['labs'].get(lab, {}).get('variants', {}).get(str(v), {})
                f = V and V.get('image') and pub and pub['card'] and asset(c['course'], V['image'])
                return self.send_bytes(open(f, 'rb').read(), 'image/png') if f else self.send_json({'error': 'not available'}, 404)
        return self.send_json({'error': 'not found'}, 404)

    def public_post(self, con, path, body):
        if path in ('/api/public/check', '/api/public/login'):
            return self.student_login(con, body, check_only=path.endswith('check'))
        if path == '/api/public/logout':
            con.execute('DELETE FROM stu_sessions WHERE token=?', (self.cookie('stu'),))
            return self.send_json({'ok': True}, cookie=self.set_cookie('stu', '', 0, 'Lax'))
        st = self.student(con)
        if not st:
            return self.send_json(err('Please sign in again.', 'Đăng nhập lại.'), 401)
        if not allow(con, 'post:' + st['sid'], 40):
            return self.send_json(TOO_MANY, 429)
        c = self.enrolled(con, st, as_int(body.get('cls')))
        if not c:
            return self.send_json(NO_RIGHT, 403)
        if path == '/api/public/submit':
            return self.public_submit(con, st, c, body)
        if path == '/api/public/unsubmit':
            return self.public_unsubmit(con, st, c, body)
        if path in ('/api/public/photo', '/api/public/photo_delete'):
            return self.public_photo(con, st, c, body, delete=path.endswith('delete'))
        return self.send_json({'error': 'not found'}, 404)

    def student_login(self, con, body, check_only):
        """Step 1 (check): student ID -> name to confirm + whether a password exists.
        Step 2 (login): first time the student creates the password; later student ID + password."""
        if not allow(con, 'stu-login:' + self.ip(), 40, 600):
            return self.send_json(TOO_MANY, 429)
        sid = str(body.get('sid', '')).strip().upper()
        row = con.execute('SELECT s.sid, s.name, s.pw FROM students s WHERE s.sid=? AND EXISTS (SELECT 1 FROM enrollments e WHERE e.sid=s.sid)',
                          (sid,)).fetchone()
        if not row:
            return self.send_json(err('Student ID not found. Check it (e.g. AUS15128).', 'Không tìm thấy MSSV. Kiểm tra lại (vd AUS15128).'), 404)
        if check_only:
            return self.send_json({'sid': row['sid'], 'name': row['name'], 'hasPassword': bool(row['pw'])})
        fail_key = f"stu-fail:{row['sid']}"
        if count_hits(con, fail_key, 900) >= 5:
            return self.send_json(err('Too many wrong passwords. Wait 15 minutes or ask the lecturer to reset your password.',
                                      'Sai mật khẩu quá nhiều lần. Đợi 15 phút hoặc nhờ giảng viên đặt lại mật khẩu.'), 429)
        pw = str(body.get('password', ''))
        if not row['pw']:                       # first sign-in: the student creates the password
            if len(pw) < 6:
                return self.send_json(err('The password needs at least 6 characters.', 'Mật khẩu cần ít nhất 6 ký tự.'), 400)
            con.execute('UPDATE students SET pw=? WHERE sid=?', (hash_pw(pw), row['sid']))
        elif not check_pw(pw, row['pw']):
            add_hit(con, fail_key)
            return self.send_json(err('Wrong password.', 'Sai mật khẩu.'), 403)
        tok = new_session(con, 'stu_sessions', row['sid'])
        return self.send_json({'ok': True}, cookie=self.set_cookie('stu', tok, 15552000, 'Lax'))

    def _open_lab(self, con, st, c, lab, *, for_unsubmit=False):
        """Checks before a student changes one lab. Returns True or sends the error."""
        if lab not in keys(c['course'])['labs']:
            self.send_json({'error': 'bad lab'}, 400); return False
        pub = con.execute('SELECT submit FROM publish WHERE class_id=? AND lab=?', (c['id'], lab)).fetchone()
        if not pub or not pub['submit']:
            self.send_json(err('Submissions for this lab are closed.', 'Lab này đang không nhận bài.'), 403); return False
        rec = con.execute('SELECT tick, src FROM records WHERE class_id=? AND lab=? AND sid=?', (c['id'], lab, st['sid'])).fetchone()
        if rec and rec['tick']:
            self.send_json(err('Already checked by the lecturer – locked.', 'Giảng viên đã xác nhận – đã khóa.'), 409); return False
        if not for_unsubmit and rec and rec['src'] == 'web':
            self.send_json(err('Already submitted. Unsubmit first to edit.', 'Đã nộp. Bấm Hủy nộp trước rồi mới sửa.'), 409); return False
        return True

    def public_submit(self, con, st, c, body):
        lab = str(body.get('lab', ''))
        if not self._open_lab(con, st, c, lab):
            return
        cid, sid = c['id'], st['sid']
        n = len(keys(c['course'])['labs'][lab]['questions']); vals = []
        for x in (body.get('values') or [])[:n]:
            try:
                vals.append(None if x in (None, '') else float(str(x).replace(',', '.')))
            except ValueError:
                return self.send_json(err('Numbers only, please.', 'Chỉ nhập số.'), 400)
        vals += [None] * (n - len(vals))
        if all(v is None for v in vals):
            return self.send_json(err('Type at least one value.', 'Nhập ít nhất một số.'), 400)
        if not con.execute('SELECT 1 FROM photos WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone():
            return self.send_json(err('Take one photo of your circuit first.', 'Chụp một ảnh mạch trước đã.'), 400)
        t = now()
        con.execute('INSERT INTO records (class_id, lab, sid, tick, manual) VALUES (?,?,?,0,?) ON CONFLICT DO NOTHING', (cid, lab, sid, '{}'))
        con.execute("UPDATE records SET vals=?, src='web', updated=? WHERE class_id=? AND lab=? AND sid=?", (json.dumps(vals), t, cid, lab, sid))
        con.execute('INSERT INTO submissions (class_id, lab, sid, vals, time, ip, agent) VALUES (?,?,?,?,?,?,?)',
                    (cid, lab, sid, json.dumps(vals), t, self.ip(), (self.headers.get('User-Agent') or '')[:200]))
        return self.send_json({'ok': True, 'time': t})

    def public_unsubmit(self, con, st, c, body):
        lab = str(body.get('lab', ''))
        if not self._open_lab(con, st, c, lab, for_unsubmit=True):
            return
        cid, sid = c['id'], st['sid']
        rec = con.execute('SELECT src FROM records WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone()
        if not rec or rec['src'] != 'web':
            return self.send_json(err('Nothing to unsubmit.', 'Chưa có bài để hủy nộp.'), 400)
        con.execute('UPDATE records SET src=NULL WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid))
        return self.send_json({'ok': True})

    def public_photo(self, con, st, c, body, delete=False):
        lab = str(body.get('lab', ''))
        if not self._open_lab(con, st, c, lab):
            return
        cid, sid = c['id'], st['sid']
        if delete:
            con.execute('DELETE FROM photos WHERE id=? AND class_id=? AND lab=? AND sid=?', (as_int(body.get('id')) or 0, cid, lab, sid))
            return self.send_json({'ok': True})
        n = con.execute('SELECT COUNT(*) FROM photos WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone()[0]
        if n >= 1:
            return self.send_json(err('Only one photo is allowed. Delete it first to replace.', 'Chỉ được 1 ảnh. Xóa ảnh cũ trước nếu muốn chụp lại.'), 400)
        try:
            raw = base64.b64decode(str(body.get('data', '')).split(',')[-1], validate=True)
        except Exception:
            raw = b''
        if not raw.startswith(b'\xff\xd8') or len(raw) > 3_000_000:
            return self.send_json(err('Photo not accepted (JPEG, max 3 MB).', 'Ảnh không hợp lệ (JPEG, tối đa 3 MB).'), 400)
        t = now()
        pid = con.execute("INSERT INTO photos (class_id, lab, sid, file, time, ip, data) VALUES (?,?,?,'',?,?,?) RETURNING id",
                          (cid, lab, sid, t, self.ip(), raw)).fetchone()[0]
        return self.send_json({'ok': True, 'id': pid, 'time': t})


def student_view(C, sid):
    """Only this student's own information in one class. Never the answer keys."""
    K = keys(C['course'])
    st = next(s for s in C['students'] if s['sid'] == sid)
    v = variant(C['vset'], st)
    mates = [s['name'] for s in C['students'] if st.get('team') and s.get('team') == st['team'] and s['sid'] != st['sid']]
    labs = []
    for lab, L in K['labs'].items():
        pub = C.get('publish', {}).get(lab, {})
        item = {'lab': lab, 'title': L['title'], 'total': L['total'], 'card': None, 'figs': [], 'image': None, 'files': [], 'marks': None, 'submit': None}
        V = L['variants'].get(str(v)) if v else None
        if pub.get('card') and V:
            item['card'] = V.get('card')
            item['figs'] = V.get('figs', [])
            item['files'] = L.get('files', [])
            if V.get('image'):
                item['image'] = f"/api/public/image/{C['id']}/{lab}.png"
        rec = C['labs'].get(lab, {}).get(sid, {})
        if pub.get('marks') or rec.get('show_marks'):
            item['marks'] = score(C, lab, st)
        if pub.get('submit') and v:
            submitted = rec.get('src') == 'web'
            item['submit'] = {'questions': [[q[1], q[2]] for q in L['questions']],   # label + unit only
                              'values': rec.get('values'),
                              'time': rec.get('updated') if submitted else None,
                              'submitted': submitted,
                              'locked': bool(rec.get('tick')),
                              'photos': [{'id': p['id'], 'url': f"/api/public/photo/{p['id']}.jpg", 'time': p['time']}
                                         for p in C.get('photos', {}).get(lab, {}).get(sid, [])]}
        labs.append(item)
    return {'id': C['id'], 'name': st['name'], 'sid': sid, 'className': C['name'], 'courseName': C['courseName'], 'term': C['term'],
            'team': st.get('team'), 'member': st.get('member'), 'variant': v, 'teammates': mates, 'labs': labs}


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
