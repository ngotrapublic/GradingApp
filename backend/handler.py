"""HTTP handler: static files + JSON API (/api/...). Runs on the laptop (server.py) and on Vercel (api/index.py).

Staff (admin / lecturer / TA) sign in with username + password; students with student ID + password.
Per class: the owner (lecturer) and the admin may do everything ('manage'); a TA may grade and open cards / submissions ('grade')."""
import base64, http.server, io, json, math, os, re, secrets, socketserver, time, urllib.parse

from .config import LOCK, PORT, STATIC
from .courses import COURSES, asset, keys, keys_live
from .db import (ROLES, add_hit, allow, as_int, assign_random, check_pw, class_role, connect, count_hits, delete_class, hash_pw,
                 load, new_session, now, set_gradebook, set_sync, set_team_mark, upsert_student, user_from_token, visible_class_ids)
from .network import lan_ips, qr_svg
from .quiz import (build_paper, course_has_quizzes, grade_paper, is_left_submit, is_phone_or_tablet_ua, leave_cooldown_sec,
                   list_banks, load_bank, should_unlock_hints)
from .scoring import export_xlsx, score, variant, rule_of, qvalue

PUBLIC_URL = os.environ.get('PUBLIC_URL', '').rstrip('/')
ON_VERCEL = bool(os.environ.get('VERCEL'))
TOO_MANY = {'error': 'Too many tries. Wait a few minutes.', 'error_vi': 'Thử quá nhiều lần. Đợi vài phút.'}
NO_RIGHT = {'error': 'You do not have the right to do this in this class.', 'error_vi': 'Bạn không có quyền làm việc này trong lớp này.'}
MANAGE, GRADE = ('admin', 'owner'), ('admin', 'owner', 'ta')
USERNAME = re.compile(r'[a-z0-9._-]{3,30}')


def err(en, vi):
    return {'error': en, 'error_vi': vi}


QUIZ_DEVICE = err('Use a phone or tablet only. Computers are blocked.', 'Chỉ dùng điện thoại hoặc máy tính bảng. Máy tính bị chặn.')


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

    def quiz_user(self, con):
        """Open quiz identity (free name + student ID, no password)."""
        tok = self.cookie('qtok')
        r = tok and con.execute(
            'SELECT token, sid, name, class_id FROM quiz_sessions WHERE token=?', (tok,)).fetchone()
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
            tgt = (query.get('target') or [''])[0]
            if 'student' in query or tgt == 'student':
                target = '/student/'
            elif 'quiz' in query or tgt == 'quiz':
                cid = (query.get('cls') or [''])[0]
                target = '/quiz/?cls=' + cid if cid else '/quiz/'
            else:
                target = ''
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
            if path == '/api/quiz':
                return self.staff_quiz_get(con, me, query)
            if path == '/api/keys':
                return self.send_json({c: keys_live(con, c) for c in COURSES})
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
                    classes = list(load(con, me, ids).get('classes', {}).values())
                    packs = {c['course']: keys_live(con, c['course']) for c in classes}
                    b = export_xlsx(classes, packs)
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
                if lab not in K['labs'] and not (lab == 'exam' and K.get('exam')): return self.send_json({'error': 'bad lab'}, 400)
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
            elif path == '/api/exam_groups':    # final exam: the drawn groups {sid: group or None}; clear = also delete the group marks
                if not manage: return self.send_json(NO_RIGHT, 403)
                if not K.get('exam'): return self.send_json({'error': 'no exam'}, 400)
                inclass = {r['sid'] for r in con.execute('SELECT sid FROM enrollments WHERE class_id=?', (cid,)).fetchall()}
                if body.get('clear'):
                    con.execute("DELETE FROM team_marks WHERE class_id=? AND lab='exam'", (cid,))
                for sid, g in (body.get('groups') or {}).items():
                    if sid not in inclass: continue
                    con.execute("INSERT INTO records (class_id, lab, sid, tick, manual) VALUES (?,'exam',?,0,?) ON CONFLICT DO NOTHING", (cid, sid, '{}'))
                    r = con.execute("SELECT manual FROM records WHERE class_id=? AND lab='exam' AND sid=?", (cid, sid)).fetchone()
                    man = json.loads(r['manual'] or '{}')
                    if g is None: man.pop('group', None)
                    else: man['group'] = int(g)
                    con.execute("UPDATE records SET manual=?, updated=? WHERE class_id=? AND lab='exam' AND sid=?", (json.dumps(man), now(), cid, sid))
            elif path == '/api/quiz':
                return self.staff_quiz_post(con, me, body)
            elif path == '/api/key_override':   # fix a wrong answer key for one variant (all students with that variant)
                if not manage:
                    return self.send_json(NO_RIGHT, 403)
                lab, var = str(body.get('lab', '')), str(body.get('variant', ''))
                L = K['labs'].get(lab)
                if not L or var not in L.get('variants', {}):
                    return self.send_json(err('No such lab / variant.', 'Không có lab / mã đề này.'), 400)
                n = len(L['questions'])
                if body.get('keys') is None:
                    con.execute('DELETE FROM key_overrides WHERE course=? AND lab=? AND variant=?', (course, lab, var))
                else:
                    raw = body['keys']
                    if not isinstance(raw, list) or len(raw) != n:
                        return self.send_json(err(f'Need {n} key values.', f'Cần đúng {n} đáp án.'), 400)
                    vals = []
                    for x in raw:
                        try:
                            vals.append(float(str(x).replace(',', '.')))
                        except (TypeError, ValueError):
                            return self.send_json(err('Keys must be numbers.', 'Đáp án phải là số.'), 400)
                    con.execute(
                        'INSERT INTO key_overrides (course, lab, variant, keys, updated) VALUES (?,?,?,?,?) '
                        'ON CONFLICT (course, lab, variant) DO UPDATE SET keys=excluded.keys, updated=excluded.updated',
                        (course, lab, var, json.dumps(vals), now()))
            else:
                return self.send_json({'error': 'not found'}, 404)
            con.commit()
            if path == '/api/key_override':
                return self.send_json({'data': load(con, me), 'keys': {code: keys_live(con, code) for code in COURSES}})
            return self.send_json(load(con, me))

    # ---------------- staff accounts ----------------
    def staff_login(self, con, body):
        username = str(body.get('username', '')).strip().lower()
        ip_key, user_key = 'login-fail:' + self.ip(), 'login-fail-user:' + username
        if count_hits(con, ip_key, 900) >= 30 or count_hits(con, user_key, 900) >= 8:      # wait 15 minutes (a whole campus may share one IP)
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
            if not allow(con, 'get:' + self.ip(), 3000):     # generous: every phone on the school Wi-Fi has the same public IP
                return self.send_json(TOO_MANY, 429)
            if path == '/api/public/quiz/class':
                if not is_phone_or_tablet_ua(self.headers.get('User-Agent'), self.headers.get('X-Quiz-Client')):
                    return self.send_json(QUIZ_DEVICE, 403)
                return self.public_quiz_class_info(con)
            if path == '/api/public/quiz/me':
                if not is_phone_or_tablet_ua(self.headers.get('User-Agent'), self.headers.get('X-Quiz-Client')):
                    return self.send_json(QUIZ_DEVICE, 403)
                return self.public_quiz_me(con)
            st = self.student(con)
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
                C = load(con, None, [c['id']])['classes'][str(c['id'])]
                return self.send_json(student_view(C, st['sid'], keys_live(con, C['course'])))
            m = re.fullmatch(r'/api/public/photo/(\d+)\.jpg', path)
            if m:                               # only the student's own photos
                r = con.execute('SELECT class_id, lab, sid, data FROM photos WHERE id=?', (int(m.group(1)),)).fetchone()
                if r and r['sid'] != st['sid']:   # team lab: the photo of the teammate who submitted for the team
                    c = self.enrolled(con, st, r['class_id'])
                    if not (c and keys(c['course'])['labs'].get(r['lab'], {}).get('team_submit')
                            and r['sid'] in team_sids(con, c['id'], st['sid'])):
                        r = None
                if not r or r['data'] is None:
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
        if path == '/api/public/quiz/identify':
            if not is_phone_or_tablet_ua(self.headers.get('User-Agent'), self.headers.get('X-Quiz-Client')):
                return self.send_json(QUIZ_DEVICE, 403)
            return self.public_quiz_identify(con, body)
        if path == '/api/public/quiz/logout':
            tok = self.cookie('qtok')
            if tok:
                con.execute('DELETE FROM quiz_sessions WHERE token=?', (tok,))
            return self.send_json({'ok': True}, cookie=self.set_cookie('qtok', '', 0, 'Lax'))
        if path in ('/api/public/quiz/start', '/api/public/quiz/submit', '/api/public/quiz/review', '/api/public/quiz/finish_explain'):
            if not is_phone_or_tablet_ua(self.headers.get('User-Agent'), self.headers.get('X-Quiz-Client')):
                return self.send_json(QUIZ_DEVICE, 403)
            qu = self.quiz_user(con)
            if not qu:
                return self.send_json(err('Please enter your name and student ID again.', 'Nhập lại họ tên và MSSV.'), 401)
            if not allow(con, 'quiz:' + qu['sid'], 60):
                return self.send_json(TOO_MANY, 429)
            if path == '/api/public/quiz/start':
                return self.public_quiz_start(con, qu, body)
            if path == '/api/public/quiz/submit':
                return self.public_quiz_submit(con, qu, body)
            if path == '/api/public/quiz/review':
                return self.public_quiz_review(con, qu, body)
            return self.public_quiz_finish_explain(con, qu, body)
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
        if path in ('/api/public/confirm', '/api/public/unconfirm'):
            return self.public_confirm(con, st, c, body, undo=path.endswith('unconfirm'))
        if path in ('/api/public/photo', '/api/public/photo_delete'):
            return self.public_photo(con, st, c, body, delete=path.endswith('delete'))
        return self.send_json({'error': 'not found'}, 404)

    def student_login(self, con, body, check_only):
        """Step 1 (check): student ID -> name to confirm + whether a password exists.
        Step 2 (login): first time the student creates the password; later student ID + password."""
        # per IP only a loose limit (a class shares one public IP); student IDs that do not exist are limited harder,
        # wrong passwords are limited per student (below)
        if not allow(con, 'stu-login:' + self.ip(), 1500, 600) or count_hits(con, 'stu-miss:' + self.ip(), 600) >= 60:
            return self.send_json(TOO_MANY, 429)
        sid = str(body.get('sid', '')).strip().upper()
        row = con.execute('SELECT s.sid, s.name, s.pw FROM students s WHERE s.sid=? AND EXISTS (SELECT 1 FROM enrollments e WHERE e.sid=s.sid)',
                          (sid,)).fetchone()
        if not row:
            add_hit(con, 'stu-miss:' + self.ip())
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

    def _open_lab(self, con, st, c, lab, *, for_unsubmit=False, allow_partial=False):
        """Checks before a student changes one lab. Returns True or sends the error.
        allow_partial: part_submit labs may keep src=web while another task is still open."""
        if lab not in keys(c['course'])['labs']:
            self.send_json({'error': 'bad lab'}, 400); return False
        pub = con.execute('SELECT submit FROM publish WHERE class_id=? AND lab=?', (c['id'], lab)).fetchone()
        if not pub or not pub['submit']:
            self.send_json(err('Submissions for this lab are closed.', 'Lab này đang không nhận bài.'), 403); return False
        rec = con.execute('SELECT tick, src FROM records WHERE class_id=? AND lab=? AND sid=?', (c['id'], lab, st['sid'])).fetchone()
        if rec and rec['tick']:
            self.send_json(err('Already checked by the lecturer – locked.', 'Giảng viên đã xác nhận – đã khóa.'), 409); return False
        if not for_unsubmit and not allow_partial and rec and rec['src'] == 'web':
            self.send_json(err('Already submitted. Unsubmit first to edit.', 'Đã nộp. Bấm Hủy nộp trước rồi mới sửa.'), 409); return False
        return True

    def public_submit(self, con, st, c, body):
        lab = str(body.get('lab', ''))
        L = keys(c['course'])['labs'].get(lab)
        if not L:
            return self.send_json({'error': 'bad lab'}, 400)
        part_submit = bool(L.get('part_submit') and L.get('parts'))
        part = body.get('part', None)
        if part_submit:
            if part is None or as_int(part) is None or not (0 <= as_int(part) < len(L['parts'])):
                return self.send_json(err('Choose which task to submit.', 'Chọn bài (Task) cần nộp.'), 400)
            part = as_int(part)
        if not self._open_lab(con, st, c, lab, allow_partial=part_submit):
            return
        cid, sid = c['id'], st['sid']
        n = len(L['questions']); vals = []
        for x in (body.get('values') or [])[:n]:
            try:
                vals.append(None if x in (None, '') else float(str(x).replace(',', '.')))
            except ValueError:
                return self.send_json(err('Numbers only, please.', 'Chỉ nhập số.'), 400)
        vals += [None] * (n - len(vals))
        if L.get('team_submit'):     # one member submits for the team, the others confirm
            own = con.execute('SELECT src FROM records WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone()
            if own and own['src'] == 'team':
                return self.send_json(err('You confirmed your team\'s values. Undo the confirmation first.',
                                          'Bạn đã xác nhận số của nhóm. Bấm Hủy xác nhận trước.'), 409)
            by = team_submitter(con, cid, lab, sid)
            if by and by != sid:
                return self.send_json(err('Your team has already submitted. Check the values and confirm them.',
                                          'Nhóm bạn đã nộp rồi. Xem lại số và bấm Xác nhận.'), 409)
        con.execute('INSERT INTO records (class_id, lab, sid, tick, manual) VALUES (?,?,?,0,?) ON CONFLICT DO NOTHING', (cid, lab, sid, '{}'))
        row = con.execute('SELECT vals, manual, src FROM records WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone()
        man = json.loads(row['manual'] or '{}')
        done = list(man.get('_parts') or [])
        if part_submit:
            if part in done:
                return self.send_json(err('This task is already submitted. Unsubmit it first to edit.',
                                          'Bài này đã nộp. Bấm Hủy nộp trước rồi mới sửa.'), 409)
            idxs = list(L['parts'][part].get('questions') or [])
            if not idxs or all(vals[i] is None for i in idxs if i < n):
                return self.send_json(err('Type at least one value for this task.', 'Nhập ít nhất một số cho bài này.'), 400)
            merged = json.loads(row['vals']) if row['vals'] else [None] * n
            merged += [None] * (n - len(merged))
            for i in idxs:
                if i < n:
                    merged[i] = vals[i]
            vals = merged[:n]
            photo_part = (L.get('photo') or {}).get('part', 0) if L.get('photo') else None
            if photo_part is not None and part == photo_part:
                if not con.execute('SELECT 1 FROM photos WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone():
                    need = (L.get('photo') or {}).get('need')
                    if need:
                        return self.send_json(err(need[0], need[1]), 400)
                    return self.send_json(err('Take one photo of your circuit first.', 'Chụp một ảnh mạch trước đã.'), 400)
            done = sorted(set(done) | {part})
            man['_parts'] = done
        else:
            if all(v is None for v in vals):
                return self.send_json(err('Type at least one value.', 'Nhập ít nhất một số.'), 400)
            if L.get('photo') and not con.execute('SELECT 1 FROM photos WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone():
                need = (L.get('photo') or {}).get('need')
                if need:
                    return self.send_json(err(need[0], need[1]), 400)
                return self.send_json(err('Take one photo of your circuit first.', 'Chụp một ảnh mạch trước đã.'), 400)
            man.pop('_parts', None)
        t = now()
        con.execute("UPDATE records SET vals=?, manual=?, src='web', updated=? WHERE class_id=? AND lab=? AND sid=?",
                    (json.dumps(vals), json.dumps(man), t, cid, lab, sid))
        con.execute('INSERT INTO submissions (class_id, lab, sid, vals, time, ip, agent) VALUES (?,?,?,?,?,?,?)',
                    (cid, lab, sid, json.dumps(vals), t, self.ip(), (self.headers.get('User-Agent') or '')[:200]))
        if L.get('team_submit'):     # values changed: teammates must confirm again
            clear_team_confirms(con, cid, lab, sid)
        return self.send_json({'ok': True, 'time': t, 'parts': done if part_submit else None})

    def public_unsubmit(self, con, st, c, body):
        lab = str(body.get('lab', ''))
        L = keys(c['course'])['labs'].get(lab)
        if not L:
            return self.send_json({'error': 'bad lab'}, 400)
        if not self._open_lab(con, st, c, lab, for_unsubmit=True):
            return
        cid, sid = c['id'], st['sid']
        rec = con.execute('SELECT src, vals, manual FROM records WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone()
        if not rec or rec['src'] != 'web':
            return self.send_json(err('Nothing to unsubmit.', 'Chưa có bài để hủy nộp.'), 400)
        part_submit = bool(L.get('part_submit') and L.get('parts'))
        part = body.get('part', None)
        if part_submit and part is not None:
            part = as_int(part)
            if part is None or not (0 <= part < len(L['parts'])):
                return self.send_json(err('Choose which task to unsubmit.', 'Chọn bài (Task) cần hủy nộp.'), 400)
            man = json.loads(rec['manual'] or '{}')
            done = list(man.get('_parts') or [])
            if part not in done:
                return self.send_json(err('This task is not submitted.', 'Bài này chưa nộp.'), 400)
            n = len(L['questions'])
            vals = json.loads(rec['vals']) if rec['vals'] else [None] * n
            vals += [None] * (n - len(vals))
            for i in (L['parts'][part].get('questions') or []):
                if i < n:
                    vals[i] = None
            done = [p for p in done if p != part]
            if done:
                man['_parts'] = done
                con.execute('UPDATE records SET vals=?, manual=?, updated=? WHERE class_id=? AND lab=? AND sid=?',
                            (json.dumps(vals[:n]), json.dumps(man), now(), cid, lab, sid))
            else:
                man.pop('_parts', None)
                con.execute('UPDATE records SET vals=?, manual=?, src=NULL WHERE class_id=? AND lab=? AND sid=?',
                            (json.dumps(vals[:n]), json.dumps(man), cid, lab, sid))
        else:
            man = json.loads(rec['manual'] or '{}')
            man.pop('_parts', None)
            con.execute('UPDATE records SET src=NULL, manual=? WHERE class_id=? AND lab=? AND sid=?', (json.dumps(man), cid, lab, sid))
        if L.get('team_submit'):     # the values may change: teammates confirm again
            clear_team_confirms(con, cid, lab, sid)
        return self.send_json({'ok': True})

    def public_confirm(self, con, st, c, body, undo=False):
        """Team lab: a member confirms the values a teammate submitted for the team (their own copy of the values), so a
        student who was not in the lab gets no marks unless they confirm (or the lecturer confirms for them)."""
        lab = str(body.get('lab', ''))
        if not self._open_lab(con, st, c, lab, for_unsubmit=True):
            return
        cid, sid = c['id'], st['sid']
        if not keys(c['course'])['labs'][lab].get('team_submit'):
            return self.send_json({'error': 'not a team lab'}, 400)
        rec = con.execute('SELECT src FROM records WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone()
        if undo:
            if not rec or rec['src'] != 'team':
                return self.send_json(err('Nothing to undo.', 'Chưa xác nhận.'), 400)
            con.execute('UPDATE records SET src=NULL, vals=NULL WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid))
            return self.send_json({'ok': True})
        if rec and rec['src'] == 'web':
            return self.send_json(err('You submitted for the team yourself.', 'Bạn là người nộp cho nhóm.'), 400)
        by = team_submitter(con, cid, lab, sid)
        if not by:
            return self.send_json(err('Nobody in your team has submitted yet.', 'Nhóm bạn chưa có ai nộp.'), 400)
        vals = con.execute('SELECT vals FROM records WHERE class_id=? AND lab=? AND sid=?', (cid, lab, by)).fetchone()['vals']
        t = now()
        con.execute('INSERT INTO records (class_id, lab, sid, tick, manual) VALUES (?,?,?,0,?) ON CONFLICT DO NOTHING', (cid, lab, sid, '{}'))
        con.execute("UPDATE records SET vals=?, src='team', updated=? WHERE class_id=? AND lab=? AND sid=?", (vals, t, cid, lab, sid))
        con.execute('INSERT INTO submissions (class_id, lab, sid, vals, time, ip, agent) VALUES (?,?,?,?,?,?,?)',
                    (cid, lab, sid, vals, t, self.ip(), ('confirm ' + (self.headers.get('User-Agent') or ''))[:200]))
        return self.send_json({'ok': True, 'time': t})

    def public_photo(self, con, st, c, body, delete=False):
        lab = str(body.get('lab', ''))
        L = keys(c['course'])['labs'].get(lab)
        if not L:
            return self.send_json({'error': 'bad lab'}, 400)
        part_submit = bool(L.get('part_submit') and L.get('parts') and L.get('photo'))
        # part_submit: photo belongs to one task – allow upload while other tasks are already submitted
        if not self._open_lab(con, st, c, lab, allow_partial=part_submit):
            return
        cid, sid = c['id'], st['sid']
        if part_submit:
            photo_part = (L.get('photo') or {}).get('part', 0)
            row = con.execute('SELECT manual, src FROM records WHERE class_id=? AND lab=? AND sid=?', (cid, lab, sid)).fetchone()
            done = list(json.loads((row['manual'] if row else None) or '{}').get('_parts') or [])
            if photo_part in done:
                return self.send_json(err('Task with the photo is already submitted. Unsubmit it first.',
                                          'Bài kèm ảnh đã nộp. Bấm Hủy nộp trước.'), 409)
            if row and row['src'] == 'team':
                return self.send_json(err('You confirmed your team\'s values. Undo the confirmation first.',
                                          'Bạn đã xác nhận số của nhóm. Bấm Hủy xác nhận trước.'), 409)
            by = team_submitter(con, cid, lab, sid) if L.get('team_submit') else None
            if by and by != sid:
                return self.send_json(err('Your team has already submitted. Check the values and confirm them.',
                                          'Nhóm bạn đã nộp rồi. Xem lại số và bấm Xác nhận.'), 409)
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


def team_sids(con, cid, sid):
    """Student IDs of the other members of this student's team in one class."""
    e = con.execute('SELECT team FROM enrollments WHERE class_id=? AND sid=?', (cid, sid)).fetchone()
    if not e or not e['team']:
        return []
    return [r['sid'] for r in con.execute('SELECT sid FROM enrollments WHERE class_id=? AND team=? AND sid<>?', (cid, e['team'], sid)).fetchall()]


def team_submitter(con, cid, lab, sid):
    """Team lab: the member of this student's team (maybe the student) who submitted for the team, or None."""
    for m in [sid] + team_sids(con, cid, sid):
        r = con.execute('SELECT src FROM records WHERE class_id=? AND lab=? AND sid=?', (cid, lab, m)).fetchone()
        if r and r['src'] == 'web':
            return m
    return None


def clear_team_confirms(con, cid, lab, sid):
    """After the submitter changes values: teammates who confirmed must confirm again."""
    for m in team_sids(con, cid, sid):
        con.execute("UPDATE records SET src=NULL, vals=NULL WHERE class_id=? AND lab=? AND sid=? AND src='team' AND tick=0",
                    (cid, lab, m))


def student_view(C, sid, keypack=None):
    """Only this student's own information in one class. Answer keys only when marks are released."""
    K = keypack or keys(C['course'])
    st = next(s for s in C['students'] if s['sid'] == sid)
    v = variant(C['vset'], st)
    mates = [s['name'] for s in C['students'] if st.get('team') and s.get('team') == st['team'] and s['sid'] != st['sid']]
    labs = []
    for lab, L in K['labs'].items():
        pub = C.get('publish', {}).get(lab, {})
        item = {'lab': lab, 'title': L['title'], 'total': L['total'], 'card': None, 'figs': [], 'image': None, 'files': [],
                'parts': L.get('parts') or [], 'photo': L.get('photo') or None, 'part_submit': bool(L.get('part_submit')),
                'team': None, 'marks': None, 'review': None, 'submit': None}
        V = L['variants'].get(str(v)) if v else None
        if pub.get('card') and V:
            item['card'] = V.get('card')
            item['figs'] = V.get('figs', [])
            item['files'] = L.get('files', [])
            if V.get('image'):
                item['image'] = f"/api/public/image/{C['id']}/{lab}.png"
        rec = C['labs'].get(lab, {}).get(sid, {})
        if pub.get('marks') or rec.get('show_marks'):
            item['marks'] = score(C, lab, st, K)
            if V:                               # their own variant keys + band (ok / half / bad = green / orange / red)
                ans, yours = V['keys'], rec.get('values') or []
                rows = []
                for i, q in enumerate(L['questions']):
                    rule = rule_of(K, q)
                    key = ans[i] if i < len(ans) else None
                    try:
                        x = float(yours[i]) if i < len(yours) and yours[i] not in (None, '') else None
                    except (TypeError, ValueError):
                        x = None
                    calc = None                         # Lab 2 Task 1: marked on fc from R and C, not on C itself
                    if x is not None and rule.get('calc'):
                        try:
                            calc = qvalue(q, yours, i)
                        except (TypeError, ValueError, IndexError, ZeroDivisionError):
                            calc = None
                    if not q[3]:                        # input only, no marks: no colour, no key
                        rows.append({'label': q[1], 'unit': q[2], 'yours': x, 'key': None, 'band': 'none', 'ok': False, 'max': 0,
                                     'tol': [rule['full'], rule['half']]})
                        continue
                    band = 'bad'
                    if rule.get('calc') and calc is not None and key not in (None, 0):
                        err = abs(calc / float(key) - 1)
                        band = 'ok' if err <= rule['full'] else ('half' if err <= rule['half'] else 'bad')
                    elif not rule.get('calc') and x is not None and key not in (None, 0):
                        err = abs(x / float(key) - 1)
                        if err <= rule['full']:
                            band = 'ok'
                        elif err <= rule['half']:
                            band = 'half'
                    elif x is not None and key == 0:
                        if abs(x) <= 1e-12:
                            band = 'ok'
                    rows.append({'label': q[1], 'unit': q[2], 'yours': x, 'key': key, 'band': band, 'ok': band == 'ok', 'max': q[3],
                                 'tol': [rule['full'], rule['half']], 'calc': calc})
                item['review'] = rows
        if L.get('team_submit') and st.get('team'):
            mates = [s for s in C['students'] if s.get('team') == st['team']]
            recs = C['labs'].get(lab, {})
            by = next((s for s in mates if recs.get(s['sid'], {}).get('src') == 'web'), None)
            br = recs.get(by['sid'], {}) if by else {}
            state = lambda s: ('submitted' if recs.get(s['sid'], {}).get('src') == 'web' else
                               'confirmed' if recs.get(s['sid'], {}).get('src') == 'team' else 'waiting')
            parts_done = list((br.get('manual') or {}).get('_parts') or []) if by else []
            if L.get('part_submit') and by and br.get('src') == 'web' and not parts_done and L.get('parts'):
                parts_done = list(range(len(L['parts'])))
            item['team'] = {'by': by and by['name'], 'bySid': by and by['sid'], 'me': state(st), 'values': br.get('values'),
                            'time': br.get('updated'), 'parts_done': parts_done,
                            'photos': [{'id': p['id'], 'url': f"/api/public/photo/{p['id']}.jpg"}
                                       for p in C.get('photos', {}).get(lab, {}).get(by['sid'], [])] if by else [],
                            'members': [{'name': s['name'], 'state': state(s)} for s in mates]}
        if pub.get('submit') and v:
            submitted = rec.get('src') == 'web'
            parts_done = list((rec.get('manual') or {}).get('_parts') or []) if L.get('part_submit') else []
            # legacy whole-lab submit (no _parts yet): treat every part as done once src=web
            if L.get('part_submit') and submitted and not parts_done and L.get('parts'):
                parts_done = list(range(len(L['parts'])))
            item['submit'] = {'questions': [[q[1], q[2]] for q in L['questions']],   # label + unit only
                              'values': rec.get('values'),
                              'time': rec.get('updated') if submitted else None,
                              'submitted': submitted,
                              'parts_done': parts_done,
                              'locked': bool(rec.get('tick')),
                              'photos': [{'id': p['id'], 'url': f"/api/public/photo/{p['id']}.jpg", 'time': p['time']}
                                         for p in C.get('photos', {}).get(lab, {}).get(sid, [])]}
        labs.append(item)
    return {'id': C['id'], 'name': st['name'], 'sid': sid, 'className': C['name'], 'courseName': C['courseName'], 'term': C['term'],
            'team': st.get('team'), 'member': st.get('member'), 'variant': v, 'teammates': mates, 'labs': labs}


def _quiz_settings(con, class_id, course, slug):
    """Merge bank defaults with per-class publish row."""
    banks = {b['slug']: b for b in list_banks(course)}
    bank = banks.get(slug) or load_bank(course, slug)
    if not bank and slug not in banks:
        return None
    meta = banks.get(slug) or {
        'slug': slug,
        'title': (bank or {}).get('title') or slug,
        'n': len((bank or {}).get('questions') or []),
        'n_pick': int((bank or {}).get('n_pick') or 10),
        'pass_score': int((bank or {}).get('pass_score') or 7),
    }
    row = con.execute('SELECT open, n_pick, pass_score FROM quiz_publish WHERE class_id=? AND slug=?',
                      (class_id, slug)).fetchone()
    return {
        'slug': meta['slug'],
        'title': meta['title'],
        'n': meta['n'],
        'n_pick': int(row['n_pick']) if row else int(meta['n_pick']),
        'pass_score': int(row['pass_score']) if row else int(meta['pass_score']),
        'open': bool(row and row['open']),
    }


def staff_quiz_get(self, con, me, query):
    """Staff: quiz banks + open flags + pass list for one class."""
    cid = as_int((query.get('cls') or [None])[0])
    if not cid or not class_role(con, me, cid):
        return self.send_json(NO_RIGHT, 403)
    row = con.execute('SELECT id, course, name FROM classes WHERE id=?', (cid,)).fetchone()
    if not row:
        return self.send_json({'error': 'not found'}, 404)
    banks = list_banks(row['course'])
    sets = []
    for b in banks:
        s = _quiz_settings(con, cid, row['course'], b['slug'])
        passed = con.execute(
            'SELECT COUNT(*) AS n FROM quiz_reveal WHERE class_id=? AND slug=? AND seen=1',
            (cid, b['slug'])).fetchone()['n']
        attempts = con.execute(
            'SELECT COUNT(DISTINCT sid) AS n FROM quiz_attempts WHERE class_id=? AND slug=?',
            (cid, b['slug'])).fetchone()['n']
        sets.append({**s, 'passed': passed, 'attempted': attempts})
    roster = []
    log = []
    slug = (query.get('slug') or [None])[0]
    if slug:
        def _quiz_name(sid):
            n = con.execute(
                'SELECT name FROM quiz_sessions WHERE class_id=? AND sid=? ORDER BY created DESC LIMIT 1',
                (cid, sid)).fetchone()
            if n and n['name']:
                return n['name']
            n = con.execute('SELECT name FROM students WHERE sid=?', (sid,)).fetchone()
            return n['name'] if n and n['name'] else sid

        rows = con.execute(
            'SELECT DISTINCT sid FROM quiz_attempts WHERE class_id=? AND slug=?', (cid, slug)).fetchall()
        for r0 in rows:
            sid = r0['sid']
            best = con.execute(
                'SELECT MAX(score) AS score, MAX(passed) AS passed, COUNT(*) AS tries FROM quiz_attempts '
                'WHERE class_id=? AND slug=? AND sid=?', (cid, slug, sid)).fetchone()
            rev = con.execute('SELECT seen, first_pass FROM quiz_reveal WHERE class_id=? AND slug=? AND sid=?',
                              (cid, slug, sid)).fetchone()
            roster.append({
                'sid': sid, 'name': _quiz_name(sid),
                'best': best['score'], 'tries': best['tries'] or 0,
                'passed': bool(best['passed']), 'solutions_seen': bool(rev and rev['seen']),
                'first_pass': rev['first_pass'] if rev else None,
            })
        roster.sort(key=lambda r: (not r['passed'], (r['name'] or '').lower()))
        for a in con.execute(
                'SELECT id, sid, score, total, passed, answers, created FROM quiz_attempts '
                'WHERE class_id=? AND slug=? ORDER BY id DESC', (cid, slug)).fetchall():
            answers = a['answers']
            if answers is None:
                status = 'open'
            elif a['passed']:
                status = 'pass'
            else:
                try:
                    ans = json.loads(answers) if isinstance(answers, str) else (answers or {})
                except (TypeError, ValueError, json.JSONDecodeError):
                    ans = {}
                status = 'left' if (not ans or set(ans.keys()) <= {'__left'}) else 'fail'
            log.append({
                'id': a['id'],
                'sid': a['sid'],
                'name': _quiz_name(a['sid']),
                'score': a['score'],
                'total': a['total'],
                'passed': bool(a['passed']),
                'status': status,
                'created': a['created'] or '',
            })
    return self.send_json({
        'class_id': cid, 'course': row['course'], 'className': row['name'],
        'has_quizzes': course_has_quizzes(row['course']),
        'sets': sets, 'roster': roster, 'log': log, 'slug': slug,
        'quiz_url': f'/quiz/?cls={cid}',
    })


def staff_quiz_post(self, con, me, body):
    """Staff: open/close a quiz set, or reset one student so they may retry."""
    cid = as_int(body.get('cls'))
    if not cid or class_role(con, me, cid) not in GRADE:
        return self.send_json(NO_RIGHT, 403)
    row = con.execute('SELECT course FROM classes WHERE id=?', (cid,)).fetchone()
    slug = str(body.get('slug') or '').strip()
    if not row or not slug or not load_bank(row['course'], slug):
        return self.send_json(err('Quiz set not found.', 'Không tìm thấy bộ quiz.'), 404)
    if body.get('action') == 'reset':
        sid = str(body.get('sid') or '').strip().upper()
        if not sid:
            return self.send_json(err('Missing student ID.', 'Thiếu MSSV.'), 400)
        con.execute('DELETE FROM quiz_attempts WHERE class_id=? AND slug=? AND sid=?', (cid, slug, sid))
        con.execute('DELETE FROM quiz_reveal WHERE class_id=? AND slug=? AND sid=?', (cid, slug, sid))
        con.execute('DELETE FROM quiz_leave WHERE class_id=? AND slug=? AND sid=?', (cid, slug, sid))
        con.execute('DELETE FROM quiz_sessions WHERE class_id=? AND sid=?', (cid, sid))
        return self.send_json({'ok': True, 'reset': True, 'sid': sid, 'slug': slug})
    bank = load_bank(row['course'], slug)
    n_pick = as_int(body.get('n_pick'))
    if n_pick is None:
        n_pick = int(bank.get('n_pick') or 20)
    pass_score = as_int(body.get('pass_score'))
    if pass_score is None:
        pass_score = int(bank.get('pass_score') or 14)
    open_flag = 1 if body.get('open') else 0
    con.execute(
        'INSERT INTO quiz_publish (class_id, slug, open, n_pick, pass_score) VALUES (?,?,?,?,?) '
        'ON CONFLICT(class_id, slug) DO UPDATE SET open=excluded.open, n_pick=excluded.n_pick, pass_score=excluded.pass_score',
        (cid, slug, open_flag, n_pick, pass_score))
    return self.send_json({'ok': True, 'open': bool(open_flag), 'n_pick': n_pick, 'pass_score': pass_score})


def public_quiz_class_info(self, con):
    """Public class label for the quiz landing page (?cls=)."""
    qs = self.route_query()
    cid = as_int((qs.get('cls') or [None])[0])
    row = cid and con.execute('SELECT id, course, name, term FROM classes WHERE id=?', (cid,)).fetchone()
    if not row or not course_has_quizzes(row['course']):
        return self.send_json(err('Quiz class not found.', 'Không tìm thấy lớp quiz.'), 404)
    open_n = con.execute('SELECT COUNT(*) AS n FROM quiz_publish WHERE class_id=? AND open=1', (cid,)).fetchone()['n']
    return self.send_json({
        'id': row['id'],
        'name': row['name'],
        'term': row['term'],
        'courseName': COURSES.get(row['course'], {}).get('name', row['course']),
        'open_sets': open_n,
    })


def public_quiz_me(self, con):
    """Current free quiz session + open sets."""
    qu = self.quiz_user(con)
    if not qu:
        return self.send_json({'error': 'signin'}, 401)
    row = con.execute('SELECT id, course, name, term FROM classes WHERE id=?', (qu['class_id'],)).fetchone()
    if not row:
        return self.send_json(err('Class missing.', 'Lớp không còn.'), 404)
    sets = []
    for b in list_banks(row['course']):
        s = _quiz_settings(con, row['id'], row['course'], b['slug'])
        if not s['open']:
            continue
        best = con.execute(
            'SELECT MAX(score) AS score, MAX(passed) AS passed, COUNT(*) AS tries FROM quiz_attempts '
            'WHERE class_id=? AND slug=? AND sid=?', (row['id'], b['slug'], qu['sid'])).fetchone()
        rev = con.execute('SELECT seen FROM quiz_reveal WHERE class_id=? AND slug=? AND sid=?',
                          (row['id'], b['slug'], qu['sid'])).fetchone()
        passed = bool(best['passed'])
        attended = bool(rev and rev['seen'])
        leave = con.execute(
            'SELECT leaves, cooldown_until FROM quiz_leave WHERE class_id=? AND slug=? AND sid=?',
            (row['id'], b['slug'], qu['sid'])).fetchone()
        leaves = int(leave['leaves']) if leave else 0
        until = float(leave['cooldown_until']) if leave else 0.0
        wait = max(0, int(math.ceil(until - time.time())))
        sets.append({
            **s,
            'best': best['score'],
            'tries': best['tries'] or 0,
            'passed': passed,
            'solutions_seen': attended,
            'needs_explanations': passed and not attended,
            'attendance_done': attended,
            'leave_count': leaves,
            'cooldown_sec': wait if not attended else 0,
        })
    return self.send_json({
        'sid': qu['sid'],
        'name': qu['name'],
        'cls': row['id'],
        'className': row['name'],
        'term': row['term'],
        'courseName': COURSES.get(row['course'], {}).get('name', row['course']),
        'sets': sets,
    })


def public_quiz_identify(self, con, body):
    """Free name + student ID. Returning students may re-enter with name OR MSSV only."""
    if not allow(con, 'quiz-id:' + self.ip(), 80, 600):
        return self.send_json(TOO_MANY, 429)
    cid = as_int(body.get('cls'))
    sid = str(body.get('sid') or '').strip().upper()
    name = str(body.get('name') or '').strip()
    if not cid:
        return self.send_json(err('Missing class.', 'Thiếu lớp.'), 400)
    if len(name) > 80 or len(sid) > 40:
        return self.send_json(err('Name or student ID is too long.', 'Họ tên hoặc MSSV quá dài.'), 400)
    row = con.execute('SELECT id, course, name, term FROM classes WHERE id=?', (cid,)).fetchone()
    if not row or not course_has_quizzes(row['course']):
        return self.send_json(err('Quiz class not found.', 'Không tìm thấy lớp quiz.'), 404)

    prior = None
    if sid and len(sid) >= 3:
        prior = con.execute(
            'SELECT sid, name FROM quiz_sessions WHERE class_id=? AND sid=? ORDER BY created DESC LIMIT 1',
            (cid, sid)).fetchone()
        if not prior:
            prior = con.execute(
                'SELECT a.sid AS sid, COALESCE('
                '(SELECT s.name FROM quiz_sessions s WHERE s.class_id=a.class_id AND s.sid=a.sid ORDER BY s.created DESC LIMIT 1), '
                '(SELECT st.name FROM students st WHERE st.sid=a.sid)'
                ') AS name FROM quiz_attempts a WHERE a.class_id=? AND a.sid=? ORDER BY a.id DESC LIMIT 1',
                (cid, sid)).fetchone()
    if not prior and name and len(name) >= 2:
        hits = con.execute(
            'SELECT DISTINCT sid, name FROM quiz_sessions WHERE class_id=? AND lower(name)=lower(?)',
            (cid, name)).fetchall()
        if len(hits) > 1:
            return self.send_json(err(
                'Several students share this name — enter your student ID.',
                'Trùng tên — hãy nhập MSSV.'), 400)
        if len(hits) == 1:
            prior = hits[0]
        else:
            hits = con.execute(
                'SELECT DISTINCT a.sid AS sid, COALESCE('
                '(SELECT s.name FROM quiz_sessions s WHERE s.class_id=a.class_id AND s.sid=a.sid ORDER BY s.created DESC LIMIT 1), '
                '(SELECT st.name FROM students st WHERE st.sid=a.sid)'
                ') AS name FROM quiz_attempts a WHERE a.class_id=? AND lower(COALESCE('
                '(SELECT s2.name FROM quiz_sessions s2 WHERE s2.class_id=a.class_id AND s2.sid=a.sid ORDER BY s2.created DESC LIMIT 1), '
                '(SELECT st2.name FROM students st2 WHERE st2.sid=a.sid)'
                '))=lower(?)',
                (cid, name)).fetchall()
            if len(hits) > 1:
                return self.send_json(err(
                    'Several students share this name — enter your student ID.',
                    'Trùng tên — hãy nhập MSSV.'), 400)
            if len(hits) == 1:
                prior = hits[0]

    if prior:
        sid = str(prior['sid']).strip().upper()
        name = str(prior['name'] or name or sid).strip()
    else:
        if not sid or len(sid) < 3 or not name or len(name) < 2:
            return self.send_json(err(
                'First time: enter both name and student ID. Returning: either one is enough.',
                'Lần đầu: nhập cả họ tên và MSSV. Vào lại: chỉ cần đúng một trong hai.'), 400)

    con.execute(
        'INSERT INTO students (sid, name) VALUES (?, ?) ON CONFLICT (sid) DO UPDATE SET name=excluded.name',
        (sid, name))
    tok = secrets.token_hex(24)
    con.execute('DELETE FROM quiz_sessions WHERE sid=? AND class_id=?', (sid, cid))
    con.execute('INSERT INTO quiz_sessions (token, sid, name, class_id, created) VALUES (?,?,?,?,?)',
                (tok, sid, name, cid, now()))
    return self.send_json({
        'ok': True,
        'sid': sid,
        'name': name,
        'cls': cid,
        'className': row['name'],
        'courseName': COURSES.get(row['course'], {}).get('name', row['course']),
    }, cookie=self.set_cookie('qtok', tok, 86400, 'Lax'))


def public_quiz_start(self, con, qu, body):
    """Student: start a shuffled attempt of an open quiz."""
    cid = qu['class_id']
    row = con.execute('SELECT id, course FROM classes WHERE id=?', (cid,)).fetchone()
    if not row:
        return self.send_json(err('Class missing.', 'Lớp không còn.'), 404)
    slug = str(body.get('slug') or '').strip()
    s = _quiz_settings(con, cid, row['course'], slug) if slug else None
    if not s or not s['open']:
        return self.send_json(err('This quiz is closed.', 'Quiz này đang đóng.'), 403)
    done = con.execute(
        'SELECT 1 FROM quiz_attempts WHERE class_id=? AND slug=? AND sid=? AND passed=1 LIMIT 1',
        (cid, slug, qu['sid'])).fetchone()
    if done:
        return self.send_json(err('Already passed — no more retries.', 'Đã đạt rồi — không được làm lại.'), 403)
    leave = con.execute(
        'SELECT leaves, cooldown_until FROM quiz_leave WHERE class_id=? AND slug=? AND sid=?',
        (cid, slug, qu['sid'])).fetchone()
    if leave and float(leave['cooldown_until'] or 0) > time.time():
        wait = max(1, int(math.ceil(float(leave['cooldown_until']) - time.time())))
        leaves = int(leave['leaves'] or 0)
        mins = max(1, int(math.ceil(wait / 60)))
        return self.send_json({
            **err(
                f'Wait {mins} min before retrying. Penalty for leaving the quiz app {leaves} times '
                f'(from the 2nd leave: 1 min, then doubles each time).',
                f'Chờ {mins} phút mới làm tiếp. Phạt vì thoát app quiz {leaves} lần '
                f'(từ lần 2: 1 phút, lần sau nhân đôi).'),
            'cooldown_sec': wait,
            'leave_count': leaves,
        }, 403)
    bank = load_bank(row['course'], slug)
    import random as _random
    rng = _random.Random(f"{qu['sid']}|{cid}|{slug}|{secrets.token_hex(8)}")
    paper, client = build_paper(bank, n_pick=s['n_pick'], rng=rng)
    if not paper:
        return self.send_json(err('Empty quiz bank.', 'Ngân hàng câu hỏi trống.'), 400)
    prior = con.execute(
        'SELECT score, total FROM quiz_attempts WHERE class_id=? AND slug=? AND sid=? AND answers IS NOT NULL '
        'ORDER BY id', (cid, slug, qu['sid'])).fetchall()
    prior_scores = [r['score'] for r in prior]
    total_ref = int(s['n_pick'] or len(client) or 20)
    hints_ready = should_unlock_hints(prior_scores, total=total_ref)
    att = con.execute(
        'INSERT INTO quiz_attempts (class_id, slug, sid, score, total, passed, paper, answers, created) '
        'VALUES (?,?,?,?,?,?,?,?,?) RETURNING id',
        (cid, slug, qu['sid'], None, len(paper), 0, json.dumps(paper), None, now())).fetchone()
    return self.send_json({
        'attempt_id': att['id'],
        'slug': slug,
        'title': s['title'],
        'pass_score': s['pass_score'],
        'total': len(client),
        'questions': client,
        'hints_ready': hints_ready,
        'hint_after_sec': 20 * 60,
        'prior_tries': len(prior),
    })


def _review_from_pass(con, cid, sid, slug):
    """Build review rows from the latest passing attempt."""
    att = con.execute(
        'SELECT * FROM quiz_attempts WHERE class_id=? AND slug=? AND sid=? AND passed=1 AND answers IS NOT NULL '
        'ORDER BY id DESC LIMIT 1', (cid, slug, sid)).fetchone()
    if not att:
        return None, None
    paper = json.loads(att['paper'])
    answers = json.loads(att['answers'] or '{}')
    score, total, review = grade_paper(paper, answers)
    return att, {'score': score, 'total': total, 'review': review, 'attempt_id': att['id'], 'slug': slug}


def public_quiz_submit(self, con, qu, body):
    """Fail → score only. Pass → return review for forced English explanations (attendance later)."""
    cid = qu['class_id']
    aid = as_int(body.get('attempt_id'))
    att = aid and con.execute(
        'SELECT * FROM quiz_attempts WHERE id=? AND class_id=? AND sid=?',
        (aid, cid, qu['sid'])).fetchone()
    if not att:
        return self.send_json(err('Attempt not found.', 'Không tìm thấy lần làm.'), 404)
    if att['answers'] is not None:
        return self.send_json(err('Already submitted.', 'Đã nộp rồi.'), 400)
    row = con.execute('SELECT course FROM classes WHERE id=?', (cid,)).fetchone()
    paper = json.loads(att['paper'])
    answers = body.get('answers') or {}
    left = is_left_submit(answers, flag=bool(body.get('left_app')))
    if left:
        answers = {'__left': 1}
    score, total, review = grade_paper(paper, {} if left else answers)
    s = _quiz_settings(con, cid, row['course'], att['slug']) if row else None
    pass_score = s['pass_score'] if s else 14
    passed = 0 if left else (1 if score >= pass_score else 0)
    con.execute(
        'UPDATE quiz_attempts SET score=?, total=?, passed=?, answers=? WHERE id=?',
        (score, total, passed, json.dumps(answers), aid))
    out = {
        'attempt_id': aid,
        'slug': att['slug'],
        'score': score,
        'total': total,
        'pass_score': pass_score,
        'passed': bool(passed),
    }
    if left:
        row_l = con.execute(
            'SELECT leaves FROM quiz_leave WHERE class_id=? AND slug=? AND sid=?',
            (cid, att['slug'], qu['sid'])).fetchone()
        leaves = int(row_l['leaves']) + 1 if row_l else 1
        cool = leave_cooldown_sec(leaves)
        until = time.time() + cool if cool else 0.0
        con.execute(
            'INSERT INTO quiz_leave (class_id, slug, sid, leaves, cooldown_until) VALUES (?,?,?,?,?) '
            'ON CONFLICT(class_id, slug, sid) DO UPDATE SET leaves=excluded.leaves, cooldown_until=excluded.cooldown_until',
            (cid, att['slug'], qu['sid'], leaves, until))
        out['left_app'] = True
        out['leave_count'] = leaves
        out['cooldown_sec'] = cool
        if leaves == 1:
            out['penalty_note'] = 'First time leaving the app — no wait yet. Next leave adds a 1-minute wait before retry.'
            out['penalty_note_vi'] = 'Lần thoát app đầu — chưa phạt chờ. Lần thoát tiếp theo phải chờ 1 phút mới làm lại.'
        else:
            mins = max(1, cool // 60)
            out['penalty_note'] = (
                f'You left the quiz app {leaves} times. Wait {mins} minute(s) before the next attempt '
                f'(from the 2nd leave: 1 min, then doubles each time).')
            out['penalty_note_vi'] = (
                f'Bạn đã thoát app quiz {leaves} lần. Chờ {mins} phút mới làm tiếp '
                f'(từ lần 2: 1 phút, các lần sau nhân đôi).')
        return self.send_json(out)
    if not passed:
        return self.send_json(out)
    rev = con.execute(
        'SELECT seen FROM quiz_reveal WHERE class_id=? AND slug=? AND sid=?',
        (cid, att['slug'], qu['sid'])).fetchone()
    if rev and rev['seen']:
        out['attendance_done'] = True
        return self.send_json(out)
    out['needs_explanations'] = True
    out['review'] = review
    return self.send_json(out)


def public_quiz_review(self, con, qu, body):
    """Resume explanation walkthrough after a pass, before attendance."""
    cid = qu['class_id']
    slug = str(body.get('slug') or '').strip()
    rev = con.execute(
        'SELECT seen FROM quiz_reveal WHERE class_id=? AND slug=? AND sid=?',
        (cid, slug, qu['sid'])).fetchone()
    if rev and rev['seen']:
        return self.send_json({'attendance_done': True, 'slug': slug})
    att, payload = _review_from_pass(con, cid, qu['sid'], slug)
    if not att:
        return self.send_json(err('No passing attempt to review.', 'Chưa có bài đạt để xem giải thích.'), 404)
    row = con.execute('SELECT course FROM classes WHERE id=?', (cid,)).fetchone()
    s = _quiz_settings(con, cid, row['course'], slug) if row else None
    return self.send_json({
        'needs_explanations': True,
        'passed': True,
        'slug': slug,
        'score': payload['score'],
        'total': payload['total'],
        'pass_score': s['pass_score'] if s else payload['score'],
        'attempt_id': payload['attempt_id'],
        'review': payload['review'],
    })


def public_quiz_finish_explain(self, con, qu, body):
    """Mark attendance after the student finishes all forced explanations."""
    cid = qu['class_id']
    slug = str(body.get('slug') or '').strip()
    att, _ = _review_from_pass(con, cid, qu['sid'], slug)
    if not att:
        return self.send_json(err('No passing attempt.', 'Chưa có bài đạt.'), 404)
    con.execute(
        'INSERT INTO quiz_reveal (class_id, slug, sid, seen, first_pass) VALUES (?,?,?,1,?) '
        'ON CONFLICT(class_id, slug, sid) DO UPDATE SET seen=1, first_pass=COALESCE(quiz_reveal.first_pass, excluded.first_pass)',
        (cid, slug, qu['sid'], now()))
    return self.send_json({
        'ok': True,
        'attendance_done': True,
        'slug': slug,
        'message': 'Attendance recorded. You may leave.',
        'message_vi': 'Đã điểm danh. Bạn có thể ra về.',
    })


H.staff_quiz_get = staff_quiz_get
H.staff_quiz_post = staff_quiz_post
H.public_quiz_class_info = public_quiz_class_info
H.public_quiz_me = public_quiz_me
H.public_quiz_identify = public_quiz_identify
H.public_quiz_start = public_quiz_start
H.public_quiz_submit = public_quiz_submit
H.public_quiz_review = public_quiz_review
H.public_quiz_finish_explain = public_quiz_finish_explain


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
