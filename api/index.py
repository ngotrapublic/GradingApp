"""Vercel entry point: every /api/... request comes here (see vercel.json). The web pages in public/ are served by Vercel."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import init_db          # noqa: E402
from backend.handler import H           # noqa: E402

init_db()                               # creates the tables on the first start


class handler(H):                       # Vercel looks for a class named `handler`
    pass
