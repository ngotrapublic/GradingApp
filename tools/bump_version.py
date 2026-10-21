"""Bump APP_VERSION patch in public/js/core/version.js (0.0.1 → 0.0.2). Run before each push."""
import pathlib
import re
import sys

PATH = pathlib.Path(__file__).resolve().parents[1] / 'public' / 'js' / 'core' / 'version.js'
text = PATH.read_text(encoding='utf-8')
m = re.search(r"const APP_VERSION = '(\d+)\.(\d+)\.(\d+)'", text)
if not m:
    sys.exit('APP_VERSION not found in version.js')
major, minor, patch = map(int, m.groups())
new = f'{major}.{minor}.{patch + 1}'
PATH.write_text(text[:m.start(1)] + new + text[m.end(3):], encoding='utf-8')
print(new)
