"""Storage: schema, upgrade of older databases, accounts, passwords, loading state, rate limits, random teams.
SQLite (data/grading.db) on the laptop, Postgres when DATABASE_URL is set (Vercel) – see store.py.

Model: users (admin / lecturer / ta) – classes (course + term + name + variant set, one owner) – class_staff (TAs)
– students (one account per student ID, one password for every course) – enrollments (student in a class, team, member)."""
import datetime, hashlib, hmac, json, os, secrets, time

from .config import DB, OLD_JSON, PHOTOS
from .courses import COURSES
from .store import PG, connect as _connect

TABLES = """
CREATE TABLE IF NOT EXISTS config   (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS users    (id {ID}, username TEXT UNIQUE, name TEXT, role TEXT, pw TEXT, active INTEGER DEFAULT 1, created TEXT,
                                     must_change INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER, created TEXT);
CREATE TABLE IF NOT EXISTS classes  (id {ID}, course TEXT, term TEXT, name TEXT, vset INTEGER, owner INTEGER, created TEXT);
CREATE TABLE IF NOT EXISTS class_staff (class_id INTEGER, user_id INTEGER, PRIMARY KEY (class_id, user_id));
CREATE TABLE IF NOT EXISTS students (sid TEXT PRIMARY KEY, name TEXT, pw TEXT);
CREATE TABLE IF NOT EXISTS enrollments (class_id INTEGER, sid TEXT, team INTEGER, member INTEGER, PRIMARY KEY (class_id, sid));
CREATE TABLE IF NOT EXISTS stu_sessions (token TEXT PRIMARY KEY, sid TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS records  (class_id INTEGER, lab TEXT, sid TEXT, tick INTEGER DEFAULT 0, vals TEXT, manual TEXT, src TEXT,
                                     updated TEXT, override REAL, reason TEXT, PRIMARY KEY (class_id, lab, sid));
CREATE TABLE IF NOT EXISTS team_marks (class_id INTEGER, lab TEXT, team TEXT, field TEXT, value REAL, PRIMARY KEY (class_id, lab, team, field));
CREATE TABLE IF NOT EXISTS sync     (class_id INTEGER, lab TEXT, time TEXT, scores TEXT, PRIMARY KEY (class_id, lab));
CREATE TABLE IF NOT EXISTS gradebook (class_id INTEGER PRIMARY KEY, time TEXT, name TEXT, rows TEXT);
CREATE TABLE IF NOT EXISTS publish  (class_id INTEGER, lab TEXT, card INTEGER DEFAULT 0, marks INTEGER DEFAULT 0, submit INTEGER DEFAULT 0, PRIMARY KEY (class_id, lab));
CREATE TABLE IF NOT EXISTS photos   (id {ID}, class_id INTEGER, lab TEXT, sid TEXT, file TEXT, time TEXT, ip TEXT, data {BLOB});
CREATE TABLE IF NOT EXISTS submissions (id {ID}, class_id INTEGER, lab TEXT, sid TEXT, vals TEXT, time TEXT, ip TEXT, agent TEXT);
CREATE TABLE IF NOT EXISTS hits     (k TEXT, t REAL);
CREATE INDEX IF NOT EXISTS hits_k ON hits (k, t);
"""
SCHEMA = TABLES.format(ID='SERIAL PRIMARY KEY', BLOB='BYTEA') if PG else TABLES.format(ID='INTEGER PRIMARY KEY AUTOINCREMENT', BLOB='BLOB')
ROLES = ('admin', 'lecturer', 'ta')
LEGACY_TERM = 'Fall 2026'           # term given to the classes of the first version (one course, 3 fixed classes)
# default account 'admin' (only the hash is stored here); its password must be changed at the first sign-in
DEFAULT_ADMIN_PW = 'pbkdf2$12201068aebc99efad0b66bd6220755f$50960dacc7a5954bacd07373fc739fd94c84c8da94500f2e23e77cb7a0224bb1'

_ready = False


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime('%d/%m/%Y %H:%M')   # Vietnam time


def connect():
    return _connect(DB)


# ---------------- passwords ----------------
def hash_pw(pw):
    salt = secrets.token_hex(16)
    return f'pbkdf2${salt}$' + hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 120_000).hex()


def check_pw(pw, stored):
    try:
        _, salt, h = (stored or '').split('$')
    except ValueError:
        return False
    return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 120_000).hex(), h)


# ---------------- schema ----------------
def init_db():
    """Create the tables (safe to call at every start, also on each Vercel cold start)."""
    global _ready
    if _ready:
        return
    with connect() as con:
        if not PG and is_legacy(con):
            upgrade_legacy(con)
        con.executescript(SCHEMA)
        if PG:
            con.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change INTEGER DEFAULT 0')
        elif 'must_change' not in [r[1] for r in con.execute('PRAGMA table_info(users)').fetchall()]:
            con.execute('ALTER TABLE users ADD COLUMN must_change INTEGER DEFAULT 0')
        if os.environ.get('ADMIN_PASSWORD'):           # optional: the admin password as a server setting (Vercel)
            u = con.execute("SELECT id FROM users WHERE username='admin'").fetchone()
            if u:
                con.execute("UPDATE users SET pw=?, role='admin', active=1 WHERE id=?", (hash_pw(os.environ['ADMIN_PASSWORD']), u['id']))
            else:
                con.execute("INSERT INTO users (username, name, role, pw, created) VALUES ('admin', 'Admin', 'admin', ?, ?)",
                            (hash_pw(os.environ['ADMIN_PASSWORD']), now()))
        elif not con.execute('SELECT 1 FROM users').fetchone():   # first start: default admin account
            con.execute("INSERT INTO users (username, name, role, pw, created, must_change) VALUES ('admin', 'Admin', 'admin', ?, ?, 1)",
                        (DEFAULT_ADMIN_PW, now()))
    _ready = True


def tables(con):
    return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def is_legacy(con):
    return 'cls' in [r[1] for r in con.execute('PRAGMA table_info(classes)').fetchall()]


def upgrade_legacy(con):
    """First version: one course (SE009), classes '1','2','3', student PINs. Move everything into the new model.
    The old tables are kept, renamed legacy_*. The classes have no owner yet: the admin gives them to a lecturer."""
    old = ['classes', 'students', 'records', 'team_marks', 'sync', 'gradebook', 'publish', 'photos', 'submissions', 'sessions', 'stu_sessions']
    have = tables(con)
    for t in old:
        if t in have:
            con.execute(f'ALTER TABLE {t} RENAME TO legacy_{t}')
    con.executescript(SCHEMA)
    have = tables(con)
    cols = lambda t: [r[1] for r in con.execute(f'PRAGMA table_info(legacy_{t})').fetchall()] if f'legacy_{t}' in have else []
    ids = {}
    for r in con.execute('SELECT cls, name FROM legacy_classes ORDER BY cls').fetchall():
        ids[r['cls']] = con.execute('INSERT INTO classes (course, term, name, vset, owner, created) VALUES (?,?,?,?,NULL,?) RETURNING id',
                                    ('SE009', LEGACY_TERM, r['name'], int(r['cls']), now())).fetchone()[0]
    for r in con.execute('SELECT * FROM legacy_students').fetchall():
        sid = r['sid'].strip().upper()
        con.execute('INSERT INTO students (sid, name) VALUES (?, ?) ON CONFLICT DO NOTHING', (sid, r['name']))
        con.execute('INSERT INTO enrollments VALUES (?,?,?,?) ON CONFLICT DO NOTHING', (ids[r['cls']], sid, r['team'], r['member']))

    def copy(table, fields):
        src = [f for f in fields if f in cols(table)]
        for r in con.execute(f'SELECT cls, {", ".join(src)} FROM legacy_{table}').fetchall():
            vals = [r[f].strip().upper() if f == 'sid' and r[f] else r[f] for f in src]
            con.execute(f'INSERT INTO {table} (class_id, {", ".join(src)}) VALUES ({", ".join("?" * (len(src) + 1))}) ON CONFLICT DO NOTHING',
                        (ids[r['cls']], *vals))
    copy('records', ['lab', 'sid', 'tick', 'vals', 'manual', 'src', 'updated', 'override', 'reason'])
    copy('team_marks', ['lab', 'team', 'field', 'value'])
    copy('sync', ['lab', 'time', 'scores'])
    copy('gradebook', ['time', 'name', 'rows'])
    copy('publish', ['lab', 'card', 'marks', 'submit'])
    copy('submissions', ['lab', 'sid', 'vals', 'time', 'ip', 'agent'])
    if cols('photos'):
        for r in con.execute('SELECT * FROM legacy_photos').fetchall():
            data = r['data'] if 'data' in cols('photos') else None
            if data is None and r['file'] and os.path.exists(os.path.join(PHOTOS, r['file'])):
                data = open(os.path.join(PHOTOS, r['file']), 'rb').read()
            con.execute('INSERT INTO photos (class_id, lab, sid, file, time, ip, data) VALUES (?,?,?,?,?,?,?)',
                        (ids[r['cls']], r['lab'], r['sid'].upper(), r['file'], r['time'], r['ip'], data))
    if os.path.exists(OLD_JSON):
        os.rename(OLD_JSON, OLD_JSON + '.unused')


# ---------------- writes used in several places (same SQL on SQLite and Postgres) ----------------
def upsert_student(con, class_id, sid, name, team, member):
    """Add or update a student in a class. The student's account (password) is shared by all classes."""
    sid = sid.strip().upper()
    con.execute('INSERT INTO students (sid, name) VALUES (?, ?) ON CONFLICT (sid) DO UPDATE SET name=excluded.name', (sid, name))
    con.execute('INSERT INTO enrollments VALUES (?,?,?,?) ON CONFLICT (class_id, sid) DO UPDATE SET team=excluded.team, member=excluded.member',
                (class_id, sid, team, member))


def set_team_mark(con, class_id, lab, team, field, value):
    con.execute('INSERT INTO team_marks VALUES (?,?,?,?,?) ON CONFLICT (class_id, lab, team, field) DO UPDATE SET value=excluded.value',
                (class_id, str(lab), str(team), field, value))


def set_sync(con, class_id, lab, t, scores):
    con.execute('INSERT INTO sync VALUES (?,?,?,?) ON CONFLICT (class_id, lab) DO UPDATE SET time=excluded.time, scores=excluded.scores',
                (class_id, str(lab), t, json.dumps(scores)))


def set_gradebook(con, class_id, t, name, rows):
    con.execute('INSERT INTO gradebook VALUES (?,?,?,?) ON CONFLICT (class_id) DO UPDATE SET time=excluded.time, name=excluded.name, rows=excluded.rows',
                (class_id, t, name, json.dumps(rows)))


def delete_class(con, class_id):
    for t in ('records', 'team_marks', 'sync', 'gradebook', 'publish', 'photos', 'submissions', 'enrollments', 'class_staff'):
        con.execute(f'DELETE FROM {t} WHERE class_id=?', (class_id,))
    con.execute('DELETE FROM classes WHERE id=?', (class_id,))


# ---------------- who may see what ----------------
def user_from_token(con, tok):
    if not tok:
        return None
    r = con.execute('SELECT u.id, u.username, u.name, u.role, u.must_change FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND u.active=1',
                    (tok,)).fetchone()
    return {**dict(r), 'must_change': bool(r['must_change'])} if r else None


def class_role(con, user, class_id):
    """'admin' / 'owner' / 'ta' / None for this user and class."""
    c = con.execute('SELECT owner FROM classes WHERE id=?', (class_id,)).fetchone()
    if not c or not user:
        return None
    if user['role'] == 'admin':
        return 'admin'
    if c['owner'] == user['id']:
        return 'owner'
    if con.execute('SELECT 1 FROM class_staff WHERE class_id=? AND user_id=?', (class_id, user['id'])).fetchone():
        return 'ta'
    return None


def visible_class_ids(con, user):
    if user['role'] == 'admin':
        q = con.execute('SELECT id FROM classes')
    else:
        q = con.execute('SELECT id FROM classes WHERE owner=? UNION SELECT class_id FROM class_staff WHERE user_id=?', (user['id'], user['id']))
    return [r[0] for r in q.fetchall()]


def load(con, user, ids=None):
    """State for the staff page: the classes this user may see, in the JSON shape the page expects.
    With `ids` (student page): exactly these classes, no user."""
    if ids is None:
        ids = visible_class_ids(con, user)
    d = {'me': user, 'courses': [{'code': c['code'], 'name': c['name'], 'sets': c.get('sets', 1)} for c in COURSES.values()], 'classes': {}}
    if not ids:
        return d
    q = ','.join('?' * len(ids))
    users = {r['id']: dict(r) for r in con.execute('SELECT id, username, name, role FROM users').fetchall()}
    for r in con.execute(f'SELECT * FROM classes WHERE id IN ({q}) ORDER BY term, course, name', ids).fetchall():
        own = users.get(r['owner'])
        d['classes'][str(r['id'])] = {'id': r['id'], 'course': r['course'], 'courseName': COURSES.get(r['course'], {}).get('name', r['course']),
                                      'term': r['term'], 'name': r['name'], 'vset': r['vset'], 'owner': own and own['username'],
                                      'ownerName': own and own['name'], 'role': class_role(con, user, r['id']), 'staff': [],
                                      'students': [], 'labs': {}, 'team': {}, 'sync': {}, 'publish': {}, 'photos': {}}
    C = lambda cid: d['classes'][str(cid)]
    for r in con.execute(f'SELECT class_id, user_id FROM class_staff WHERE class_id IN ({q})', ids).fetchall():
        u = users.get(r['user_id'])
        if u: C(r['class_id'])['staff'].append({'id': u['id'], 'username': u['username'], 'name': u['name']})
    for r in con.execute(f'SELECT e.class_id, e.sid, s.name, e.team, e.member, s.pw FROM enrollments e JOIN students s ON s.sid=e.sid '
                         f'WHERE e.class_id IN ({q}) ORDER BY s.name', ids).fetchall():
        C(r['class_id'])['students'].append({'sid': r['sid'], 'name': r['name'], 'team': r['team'], 'member': r['member'], 'hasPin': bool(r['pw'])})
    for r in con.execute(f'SELECT * FROM records WHERE class_id IN ({q})', ids).fetchall():
        rec = {'tick': bool(r['tick'])}
        if r['vals']: rec['values'] = json.loads(r['vals'])
        if r['manual']: rec['manual'] = json.loads(r['manual'])
        if r['src']: rec['src'] = r['src']
        if r['updated']: rec['updated'] = r['updated']
        if r['override'] is not None: rec['override'] = r['override']; rec['reason'] = r['reason'] or ''
        C(r['class_id'])['labs'].setdefault(r['lab'], {})[r['sid']] = rec
    for r in con.execute(f'SELECT * FROM team_marks WHERE class_id IN ({q})', ids).fetchall():
        C(r['class_id'])['team'].setdefault(r['lab'], {}).setdefault(r['team'], {})[r['field']] = r['value']
    for r in con.execute(f'SELECT * FROM sync WHERE class_id IN ({q})', ids).fetchall():
        C(r['class_id'])['sync'][r['lab']] = {'time': r['time'], 'scores': json.loads(r['scores'])}
    for r in con.execute(f'SELECT id, class_id, lab, sid, time FROM photos WHERE class_id IN ({q}) ORDER BY id', ids).fetchall():
        C(r['class_id'])['photos'].setdefault(r['lab'], {}).setdefault(r['sid'], []).append({'id': r['id'], 'time': r['time']})
    for r in con.execute(f'SELECT * FROM publish WHERE class_id IN ({q})', ids).fetchall():
        C(r['class_id'])['publish'][r['lab']] = {'card': bool(r['card']), 'marks': bool(r['marks']), 'submit': bool(r['submit'])}
    for r in con.execute(f'SELECT * FROM gradebook WHERE class_id IN ({q})', ids).fetchall():
        C(r['class_id'])['gb'] = {'time': r['time'], 'name': r['name'], 'rows': json.loads(r['rows'])}
    return d


def new_session(con, table, owner):
    tok = secrets.token_hex(24)
    con.execute(f'INSERT INTO {table} VALUES (?, ?, ?)', (tok, owner, now()))
    return tok


# ---------------- rate limits (kept in the database: Vercel has no shared memory) ----------------
def count_hits(con, key, window):
    return con.execute('SELECT COUNT(*) FROM hits WHERE k=? AND t>?', (key, time.time() - window)).fetchone()[0]


def add_hit(con, key):
    t = time.time()
    if secrets.randbelow(50) == 0:                       # clean up now and then
        con.execute('DELETE FROM hits WHERE t<?', (t - 86400,))
    con.execute('INSERT INTO hits VALUES (?, ?)', (key, t))


def allow(con, key, limit, window=60):
    """Count this request; False when `key` made more than `limit` requests in the last `window` seconds."""
    add_hit(con, key)
    return count_hits(con, key, window) <= limit


# ---------------- random teams ----------------
def assign_random(con, class_id, reshuffle=False):
    """Put students without a team into free slots at random: 6 teams x members 1-3 first, then member 4."""
    import random
    if reshuffle:
        con.execute('UPDATE enrollments SET team=NULL, member=NULL WHERE class_id=?', (class_id,))
    rows = con.execute('SELECT sid, team, member FROM enrollments WHERE class_id=?', (class_id,)).fetchall()
    used = {(r['team'], r['member']) for r in rows if r['team'] and r['member']}
    todo = [r['sid'] for r in rows if not (r['team'] and r['member'])]
    random.shuffle(todo)
    free3 = [(t, m) for t in range(1, 7) for m in (1, 2, 3) if (t, m) not in used]
    random.shuffle(free3)
    free3.sort(key=lambda tm: tm[1])          # fill member 1 of every team, then 2, then 3 -> teams stay balanced
    free4 = [(t, 4) for t in range(1, 7) if (t, 4) not in used]
    random.shuffle(free4)
    slots = free3 + free4
    for sid, (t, m) in zip(todo, slots):
        con.execute('UPDATE enrollments SET team=?, member=? WHERE class_id=? AND sid=?', (t, m, class_id, sid))
    return max(0, len(todo) - len(slots))     # students that could not be placed (more than 24)


def as_int(x):
    try:
        return int(x) if x not in (None, '') else None
    except (TypeError, ValueError):
        return None
