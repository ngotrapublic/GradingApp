"""Electric Circuit Lab – grading web app (lecturer only).

Run:  python3 server.py            (or double-click start.command)
Then open the printed address on your phone (same Wi-Fi).
Data is stored in data/grading.db (SQLite) next to this file.
Code: backend/ (Python) and public/ (web page, one folder per tab).
On Vercel the same code runs through api/index.py with a Postgres database (DATABASE_URL).
"""
from backend.config import DB, PORT
from backend.store import PG
from backend.db import init_db
from backend.handler import H, Server
from backend.network import lan_ips, print_qr


if __name__ == '__main__':
    init_db()
    srv = Server(('0.0.0.0', PORT), H)
    print('\n  Electric Circuit Lab – grading / chấm điểm')
    print(f'  On this computer / Trên laptop:   http://localhost:{PORT}')
    ips = lan_ips()
    for ip in ips:
        print(f'  On a phone (same Wi-Fi) / Trên điện thoại (cùng wifi):   http://{ip}:{PORT}')
    if ips:
        print_qr(f'http://{ips[0]}:{PORT}')
    print(f'  Data / Dữ liệu: {"Postgres (DATABASE_URL)" if PG else DB}')
    print('  Stop / Dừng: Ctrl+C\n', flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
