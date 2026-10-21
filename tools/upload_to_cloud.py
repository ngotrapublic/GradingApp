"""Copy the laptop data (data/grading.db) into the online Postgres database used on Vercel – once, before going online.

    DATABASE_URL='postgres://…' .venv/bin/python tools/upload_to_cloud.py

Copies accounts, classes, TAs, students (with their passwords), enrollments, records, marks, publish switches, photos
and submissions. The online database must be empty (nothing is overwritten). Start the laptop app once before
(start.command) so an older data file is upgraded first."""
import os, sqlite3, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not (os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')):
    sys.exit('Set DATABASE_URL first (Vercel → Storage → your database → .env.local).')

from backend.config import DB               # noqa: E402
from backend import db                      # noqa: E402

TABLES = ['users', 'classes', 'class_staff', 'students', 'enrollments', 'records', 'team_marks', 'sync', 'gradebook',
          'publish', 'photos', 'submissions']
SERIAL = ['users', 'classes', 'photos', 'submissions']      # tables with an id counter

if not os.path.exists(DB):
    sys.exit(f'No laptop data found at {DB}')
src = sqlite3.connect(DB); src.row_factory = sqlite3.Row
if 'cls' in [r[1] for r in src.execute('PRAGMA table_info(classes)')]:
    sys.exit('The laptop data is from an older version: start the app once with start.command, then run this again.')

db.init_db()                                # online tables (+ the admin account when ADMIN_PASSWORD is set)
with db.connect() as dst:
    if dst.execute('SELECT COUNT(*) FROM classes').fetchone()[0]:
        sys.exit('The online database already has classes – nothing copied.')
    uid = {}                                # laptop user id -> online user id
    for r in src.execute('SELECT * FROM users').fetchall():
        old = dst.execute('SELECT id FROM users WHERE username=?', (r['username'],)).fetchone()
        uid[r['id']] = old[0] if old else dst.execute(      # 'admin' made from ADMIN_PASSWORD on the server stays as it is
            'INSERT INTO users (username, name, role, pw, active, created, must_change) VALUES (?,?,?,?,?,?,?) RETURNING id',
            (r['username'], r['name'], r['role'], r['pw'], r['active'], r['created'], r['must_change'] if 'must_change' in r.keys() else 0)).fetchone()[0]
    print(f'  users: {len(uid)}')
    for table in TABLES[1:]:
        cols = [r[1] for r in src.execute(f'PRAGMA table_info({table})')]
        rows = src.execute(f'SELECT {", ".join(cols)} FROM {table}').fetchall()
        for r in rows:
            vals = [uid.get(r[c]) if c in ('owner', 'user_id') else r[c] for c in cols]
            dst.execute(f'INSERT INTO {table} ({", ".join(cols)}) VALUES ({", ".join("?" * len(cols))})', vals)
        print(f'  {table}: {len(rows)}')
    for table in SERIAL:                    # next ids continue after the copied ones
        dst.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)")
print('Done.')
