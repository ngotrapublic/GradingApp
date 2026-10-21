"""Paths, port, answer keys. Override the data folder with GRADING_DATA_DIR (used for testing)."""
import json, os, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get('GRADING_DATA_DIR') or os.path.join(ROOT, 'data')
DB = os.path.join(DATA_DIR, 'grading.db')
OLD_JSON = os.path.join(DATA_DIR, 'data.json')
PHOTOS = os.path.join(DATA_DIR, 'photos')           # students' circuit photos (evidence)
STATIC = os.path.join(ROOT, 'public')        # web pages (Vercel serves this folder directly)
ASSETS = os.path.join(ROOT, 'assets')        # Lab 3 oscilloscope screens (served only when the lab card is open)
KEYS = json.load(open(os.path.join(ROOT, 'keys.json'), encoding='utf8'))
PORT = int(os.environ.get('PORT', '8000'))
LOCK = threading.Lock()
CLASSES = ('1', '2', '3')
