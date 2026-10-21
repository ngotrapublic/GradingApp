"""Copy the laptop data (data/grading.db) into the online Postgres database used on Vercel – once, before going online.

    DATABASE_URL='postgres://…' .venv/bin/python tools/upload_to_cloud.py

Copies classes, students (without PINs), records, team marks, Canvas sync, gradebook, publish switches, photos and
submissions. The online database must be empty (nothing is overwritten)."""
import os, sqlite3, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not (os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')):
    sys.exit('Set DATABASE_URL first (Vercel → Storage → your database → .env.local).')

from backend.config import DB               # noqa: E402
from backend import db                      # noqa: E402

if not os.path.exists(DB):
    sys.exit(f'No laptop data found at {DB}')

src = sqlite3.connect(DB); src.row_factory = sqlite3.Row
db.init_db()                                # online tables
COPY = {'classes': ['cls', 'name'],
        'students': ['cls', 'sid', 'name', 'team', 'member'],
        'records': ['cls', 'lab', 'sid', 'tick', 'vals', 'manual', 'src', 'updated', 'override', 'reason'],
        'team_marks': ['cls', 'lab', 'team', 'field', 'value'],
        'sync': ['cls', 'lab', 'time', 'scores'],
        'gradebook': ['cls', 'time', 'name', 'rows'],
        'publish': ['cls', 'lab', 'card', 'marks', 'submit'],
        'photos': ['cls', 'lab', 'sid', 'file', 'time', 'ip', 'data'],
        'submissions': ['cls', 'lab', 'sid', 'vals', 'time', 'ip', 'agent']}
with db.connect() as dst:
    if dst.execute('SELECT COUNT(*) FROM students').fetchone()[0]:
        sys.exit('The online database already has students – nothing copied.')
    for table, cols in COPY.items():
        have = [r[1] for r in src.execute(f'PRAGMA table_info({table})')]
        use = [c for c in cols if c in have]
        rows = src.execute(f'SELECT {", ".join(use)} FROM {table}').fetchall()
        if table == 'photos' and 'data' not in have:
            print('  photos: start the laptop app once with start.command first (it moves the photos into the database)')
            continue
        for r in rows:
            if table == 'classes':              # the 3 classes exist already: copy the names
                dst.execute('UPDATE classes SET name=? WHERE cls=?', (r['name'], r['cls']))
            else:
                dst.execute(f'INSERT INTO {table} ({", ".join(use)}) VALUES ({", ".join("?" * len(use))})', tuple(r[c] for c in use))
        print(f'  {table}: {len(rows)}')
print('Done. Students choose their PIN at the first sign-in on the online page.')
