"""Storage: schema, upgrades of older databases, loading state, sessions, PINs, rate limits, random teams.
SQLite (data/grading.db) on the laptop, Postgres when DATABASE_URL is set (Vercel) – see store.py."""
import datetime, hashlib, json, os, secrets, time

from .config import CLASSES, DB, OLD_JSON, PHOTOS
from .store import PG, connect as _connect

TABLES = """
CREATE TABLE IF NOT EXISTS config   (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, created TEXT);
CREATE TABLE IF NOT EXISTS stu_sessions (token TEXT PRIMARY KEY, cls TEXT, sid TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS classes  (cls TEXT PRIMARY KEY, name TEXT);
CREATE TABLE IF NOT EXISTS students (cls TEXT, sid TEXT, name TEXT, team INTEGER, member INTEGER, pin TEXT, PRIMARY KEY (cls, sid));
CREATE TABLE IF NOT EXISTS records  (cls TEXT, lab TEXT, sid TEXT, tick INTEGER DEFAULT 0, vals TEXT, manual TEXT, src TEXT,
                                     updated TEXT, override REAL, reason TEXT, PRIMARY KEY (cls, lab, sid));
CREATE TABLE IF NOT EXISTS team_marks (cls TEXT, lab TEXT, team TEXT, field TEXT, value REAL, PRIMARY KEY (cls, lab, team, field));
CREATE TABLE IF NOT EXISTS sync     (cls TEXT, lab TEXT, time TEXT, scores TEXT, PRIMARY KEY (cls, lab));
CREATE TABLE IF NOT EXISTS gradebook (cls TEXT PRIMARY KEY, time TEXT, name TEXT, rows TEXT);
CREATE TABLE IF NOT EXISTS publish  (cls TEXT, lab TEXT, card INTEGER DEFAULT 0, marks INTEGER DEFAULT 0, submit INTEGER DEFAULT 0, PRIMARY KEY (cls, lab));
CREATE TABLE IF NOT EXISTS photos   (id {ID}, cls TEXT, lab TEXT, sid TEXT, file TEXT, time TEXT, ip TEXT, data {BLOB});
CREATE TABLE IF NOT EXISTS submissions (id {ID}, cls TEXT, lab TEXT, sid TEXT, vals TEXT, time TEXT, ip TEXT, agent TEXT);
CREATE TABLE IF NOT EXISTS hits     (k TEXT, t REAL);
CREATE INDEX IF NOT EXISTS hits_k ON hits (k, t);
"""
SCHEMA = TABLES.format(ID='SERIAL PRIMARY KEY', BLOB='BYTEA') if PG else TABLES.format(ID='INTEGER PRIMARY KEY AUTOINCREMENT', BLOB='BLOB')

# columns added after the first version (an older SQLite file gets them on start)
ADDED = {'records': [('override', 'REAL'), ('reason', 'TEXT')], 'publish': [('submit', 'INTEGER DEFAULT 0')],
         'students': [('pin', 'TEXT')], 'photos': [('data', 'BLOB')]}

_ready = False


def now():
    return datetime.datetime.now(tz_vn()).strftime('%d/%m/%Y %H:%M')


def tz_vn():
    return datetime.timezone(datetime.timedelta(hours=7))   # Vercel runs in UTC; the class is in Vietnam


def connect():
    return _connect(DB)


def init_db():
    """Create the tables (safe to call at every start, also on each Vercel cold start)."""
    global _ready
    if _ready:
        return
    with connect() as con:
        con.executescript(SCHEMA)
        if not PG:
            for table, cols in ADDED.items():
                have = [r[1] for r in con.execute(f'PRAGMA table_info({table})')]
                for c, typ in cols:
                    if c not in have:
                        con.execute(f'ALTER TABLE {table} ADD COLUMN {c} {typ}')
            photos_into_db(con)
        for c in CLASSES:
            con.execute('INSERT INTO classes VALUES (?, ?) ON CONFLICT DO NOTHING', (c, f'Lớp {c}'))
        if not PG:
            migrate_json(con)
    _ready = True


def photos_into_db(con):
    """Earlier versions kept photos as files in data/photos – copy them into the database (files are kept)."""
    for r in con.execute("SELECT id, file FROM photos WHERE data IS NULL AND file <> ''").fetchall():
        f = os.path.join(PHOTOS, r['file'])
        if os.path.exists(f):
            con.execute('UPDATE photos SET data=? WHERE id=?', (open(f, 'rb').read(), r['id']))


def migrate_json(con):
    """One-time import of the old data/data.json (first version of the app)."""
    if not os.path.exists(OLD_JSON) or con.execute('SELECT COUNT(*) FROM students').fetchone()[0]:
        return
    d = json.load(open(OLD_JSON, encoding='utf8'))
    if d.get('pin'):
        set_config(con, 'pin', d['pin'])
    for cls, C in d.get('classes', {}).items():
        con.execute('INSERT INTO classes VALUES (?, ?) ON CONFLICT (cls) DO UPDATE SET name=excluded.name', (cls, C.get('name') or f'Lớp {cls}'))
        for s in C.get('students', []):
            upsert_student(con, cls, s['sid'], s['name'], s.get('team'), s.get('member'))
        for lab, recs in C.get('labs', {}).items():
            for sid, r in recs.items():
                con.execute('INSERT INTO records (cls, lab, sid, tick, vals, manual, src, updated) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT DO NOTHING',
                            (cls, lab, sid, 1 if r.get('tick') else 0, json.dumps(r.get('values')), json.dumps(r.get('manual') or {}), r.get('src'), now()))
        for lab, teams in C.get('team', {}).items():
            for team, fields in teams.items():
                for f, v in fields.items():
                    set_team_mark(con, cls, lab, team, f, v)
        for lab, sy in C.get('sync', {}).items():
            set_sync(con, cls, lab, sy['time'], sy['scores'])
        if C.get('gb'):
            g = C['gb']; set_gradebook(con, cls, g.get('time'), g.get('name'), g['rows'])
    os.rename(OLD_JSON, OLD_JSON + '.migrated')


# ---------------- writes used in several places (same SQL on SQLite and Postgres) ----------------
def set_config(con, key, value):
    con.execute('INSERT INTO config VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value=excluded.value', (key, value))


def upsert_student(con, cls, sid, name, team, member):
    """Add or update a student. Keeps the student's own PIN."""
    con.execute('INSERT INTO students (cls, sid, name, team, member) VALUES (?,?,?,?,?) '
                'ON CONFLICT (cls, sid) DO UPDATE SET name=excluded.name, team=excluded.team, member=excluded.member',
                (cls, sid, name, team, member))


def set_team_mark(con, cls, lab, team, field, value):
    con.execute('INSERT INTO team_marks VALUES (?,?,?,?,?) ON CONFLICT (cls, lab, team, field) DO UPDATE SET value=excluded.value',
                (cls, str(lab), str(team), field, value))


def set_sync(con, cls, lab, t, scores):
    con.execute('INSERT INTO sync VALUES (?,?,?,?) ON CONFLICT (cls, lab) DO UPDATE SET time=excluded.time, scores=excluded.scores',
                (cls, str(lab), t, json.dumps(scores)))


def set_gradebook(con, cls, t, name, rows):
    con.execute('INSERT INTO gradebook VALUES (?,?,?,?) ON CONFLICT (cls) DO UPDATE SET time=excluded.time, name=excluded.name, rows=excluded.rows',
                (cls, t, name, json.dumps(rows)))


def load(con):
    """Whole state in the JSON shape the lecturer page expects (no PINs, only whether one is set)."""
    d = {'classes': {}}
    for r in con.execute('SELECT * FROM classes ORDER BY cls'):
        d['classes'][r['cls']] = {'name': r['name'], 'students': [], 'labs': {}, 'team': {}, 'sync': {}, 'publish': {}, 'photos': {}}
    for r in con.execute('SELECT cls, sid, name, team, member, pin FROM students ORDER BY cls, name'):
        d['classes'][r['cls']]['students'].append({'sid': r['sid'], 'name': r['name'], 'team': r['team'], 'member': r['member'], 'hasPin': bool(r['pin'])})
    for r in con.execute('SELECT * FROM records'):
        rec = {'tick': bool(r['tick'])}
        if r['vals']: rec['values'] = json.loads(r['vals'])
        if r['manual']: rec['manual'] = json.loads(r['manual'])
        if r['src']: rec['src'] = r['src']
        if r['updated']: rec['updated'] = r['updated']
        if r['override'] is not None: rec['override'] = r['override']; rec['reason'] = r['reason'] or ''
        d['classes'][r['cls']]['labs'].setdefault(r['lab'], {})[r['sid']] = rec
    for r in con.execute('SELECT * FROM team_marks'):
        d['classes'][r['cls']]['team'].setdefault(r['lab'], {}).setdefault(r['team'], {})[r['field']] = r['value']
    for r in con.execute('SELECT * FROM sync'):
        d['classes'][r['cls']]['sync'][r['lab']] = {'time': r['time'], 'scores': json.loads(r['scores'])}
    for r in con.execute('SELECT id, cls, lab, sid, time FROM photos ORDER BY id'):
        d['classes'][r['cls']]['photos'].setdefault(r['lab'], {}).setdefault(r['sid'], []).append({'id': r['id'], 'time': r['time']})
    for r in con.execute('SELECT * FROM publish'):
        d['classes'][r['cls']]['publish'][r['lab']] = {'card': bool(r['card']), 'marks': bool(r['marks']), 'submit': bool(r['submit'])}
    for r in con.execute('SELECT * FROM gradebook'):
        d['classes'][r['cls']]['gb'] = {'time': r['time'], 'name': r['name'], 'rows': json.loads(r['rows'])}
    return d


# ---------------- lecturer PIN and sessions ----------------
def get_pin(con):
    """Hash of the lecturer PIN. On Vercel it comes from the LECTURER_PIN setting, so nobody can set it from the web."""
    if os.environ.get('LECTURER_PIN'):
        return h(os.environ['LECTURER_PIN'])
    r = con.execute("SELECT value FROM config WHERE key='pin'").fetchone()
    return r[0] if r else None


def h(pin):
    return hashlib.sha256(('ecl-' + pin).encode()).hexdigest()


def new_session(con):
    tok = secrets.token_hex(16)
    con.execute('INSERT INTO sessions VALUES (?, ?)', (tok, now()))
    return tok


# ---------------- student PIN (4 digits, chosen by the student at the first sign-in) ----------------
def h_student(cls, sid, pin):
    return hashlib.sha256(f'ecl-stu-{cls}-{sid.lower()}-{pin}'.encode()).hexdigest()


def new_student_session(con, cls, sid):
    tok = secrets.token_hex(16)
    con.execute('INSERT INTO stu_sessions VALUES (?, ?, ?, ?)', (tok, cls, sid, now()))
    return tok


def reset_student_pin(con, cls, sid):
    con.execute('UPDATE students SET pin=NULL WHERE cls=? AND sid=?', (cls, sid))
    con.execute('DELETE FROM stu_sessions WHERE cls=? AND sid=?', (cls, sid))
    con.execute('DELETE FROM hits WHERE k=?', (f'stu-fail:{cls}:{sid}',))      # unlock after wrong PINs


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
def assign_random(con, cls, reshuffle=False):
    """Put students without a team into free slots at random: 6 teams x members 1-3 first, then member 4."""
    import random
    if reshuffle:
        con.execute('UPDATE students SET team=NULL, member=NULL WHERE cls=?', (cls,))
    rows = con.execute('SELECT sid, team, member FROM students WHERE cls=?', (cls,)).fetchall()
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
        con.execute('UPDATE students SET team=?, member=? WHERE cls=? AND sid=?', (t, m, cls, sid))
    return max(0, len(todo) - len(slots))     # students that could not be placed (more than 24)


def as_int(x):
    try:
        return int(x) if x not in (None, '') else None
    except (TypeError, ValueError):
        return None
