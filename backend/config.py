"""Paths and port. Override the data folder with GRADING_DATA_DIR (used for testing)."""
import os, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get('GRADING_DATA_DIR') or os.path.join(ROOT, 'data')
DB = os.path.join(DATA_DIR, 'grading.db')
OLD_JSON = os.path.join(DATA_DIR, 'data.json')
PHOTOS = os.path.join(DATA_DIR, 'photos')    # photos of the first version (now stored in the database)
STATIC = os.path.join(ROOT, 'public')        # web pages (Vercel serves this folder directly)
COURSES_DIR = os.path.join(ROOT, 'courses')  # one folder per lab course: course.json + keys.json + private assets
PORT = int(os.environ.get('PORT', '8000'))
LOCK = threading.Lock()
