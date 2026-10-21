"""Course packages: courses/<CODE>/course.json (name, number of variant sets) + keys.json (labs, variants, answer keys)
+ assets/ (private images, e.g. Lab 3 scope screens). Public images of a course live in public/courses/<CODE>/.
A new lab course = a new folder here."""
import copy
import json
import os

from .config import COURSES_DIR


def _load():
    out = {}
    for code in sorted(os.listdir(COURSES_DIR)):
        d = os.path.join(COURSES_DIR, code)
        if not os.path.isfile(os.path.join(d, 'course.json')):
            continue
        meta = json.load(open(os.path.join(d, 'course.json'), encoding='utf8'))
        meta['keys'] = json.load(open(os.path.join(d, 'keys.json'), encoding='utf8'))
        meta['dir'] = d
        out[meta['code']] = meta
    return out


COURSES = _load()


def keys(course):
    return COURSES[course]['keys']


def keys_live(con, course):
    """Answer keys with lecturer overrides from the database applied (deepcopy only when needed)."""
    K = keys(course)
    rows = con.execute('SELECT lab, variant, keys FROM key_overrides WHERE course=?', (course,)).fetchall()
    if not rows:
        return K
    K = copy.deepcopy(K)
    for r in rows:
        lab, var = r['lab'], str(r['variant'])
        V = K.get('labs', {}).get(lab, {}).get('variants', {}).get(var)
        if not V:
            continue
        V['keys'] = json.loads(r['keys'])
        V['keys_edited'] = True
    return K


def asset(course, rel):
    """Path of a private asset of a course, or None (also refuses paths that leave the folder)."""
    base = os.path.realpath(os.path.join(COURSES[course]['dir'], 'assets'))
    f = os.path.realpath(os.path.join(base, rel))
    return f if f.startswith(base + os.sep) and os.path.isfile(f) else None


def summary():
    return [{'code': c['code'], 'name': c['name'], 'sets': c.get('sets', 1)} for c in COURSES.values()]
