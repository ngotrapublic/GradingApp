"""Database connection: SQLite on the laptop, Postgres (Neon) on Vercel when DATABASE_URL is set.
All SQL in the app is written so it runs on both (ON CONFLICT upserts, RETURNING); only the
placeholders differ (? for SQLite, %s for Postgres) and are converted here."""
import os, sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
PG = bool(DATABASE_URL)


class Row(dict):
    """A result row readable by name (r['sid']) and by position (r[0]), like sqlite3.Row."""
    def __init__(self, names, values):
        super().__init__(zip(names, values))
        self._v = list(values)

    def __getitem__(self, k):
        return self._v[k] if isinstance(k, int) else super().__getitem__(k)


class _Cursor:
    def __init__(self, cur):
        self.cur = cur
        self.names = [d[0] for d in cur.description] if cur.description else []

    def _row(self, t):
        return None if t is None else Row(self.names, [bytes(x) if isinstance(x, memoryview) else x for x in t])

    def fetchone(self):
        return self._row(self.cur.fetchone())

    def fetchall(self):
        return [self._row(t) for t in self.cur.fetchall()]

    def __iter__(self):
        return iter(self.fetchall())


class PgCon:
    def __init__(self):
        import psycopg
        self.con = psycopg.connect(DATABASE_URL, connect_timeout=10)

    def execute(self, sql, params=()):
        cur = self.con.cursor()
        cur.execute(sql.replace('%', '%%').replace('?', '%s'), tuple(params))
        return _Cursor(cur)

    def executescript(self, sql):
        with self.con.cursor() as cur:
            cur.execute(sql)

    def commit(self):
        self.con.commit()

    def __enter__(self):
        return self

    def __exit__(self, kind, *_):
        (self.con.rollback if kind else self.con.commit)()
        self.con.close()


class LiteCon(sqlite3.Connection):
    """sqlite3 connection that also closes at the end of a `with` block (the default only commits)."""
    def __exit__(self, kind, *rest):
        try:
            return super().__exit__(kind, *rest)
        finally:
            self.close()


def connect(path):
    if PG:
        return PgCon()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path, timeout=10, factory=LiteCon)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    return con
