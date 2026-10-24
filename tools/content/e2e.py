"""End-to-end test against a running server (scratch data only): one class of 19 students, everything correct -> 50/50."""
import base64, http.cookiejar, io, json, sys, urllib.request
BASE = sys.argv[1]
KEYS = json.load(open('/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/courses/SE009/keys.json'))['labs']


class Client:
    def __init__(self):
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def call(self, path, body=None, ok=True):
        req = urllib.request.Request(BASE + path, data=None if body is None else json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json'})
        try:
            r = self.op.open(req); code = r.status; raw = r.read()
        except urllib.error.HTTPError as e:
            code = e.code; raw = e.read()
        try: j = json.loads(raw)
        except Exception: j = raw
        if ok and code != 200: raise SystemExit(f'{path} -> {code} {j}')
        return code, j


import math


def answers(lab, v):
    """What a perfect student submits: the keys, except a design question (Lab 2 Task 1: R, C for a target fc)."""
    vals = list(KEYS[lab]['variants'][v]['keys'])
    for i, q in enumerate(KEYS[lab]['questions']):
        r = q[4] if len(q) > 4 and isinstance(q[4], dict) else {}
        if r.get('calc') == 'rc_fc':
            R, C_ = min(((R, C_) for R in (220, 330, 470, 680, 1000, 1500, 2200, 3300, 4700, 6800, 10000, 15000, 22000) for C_ in (10, 22, 47)),
                        key=lambda p: abs(1 / (2 * math.pi * p[0] * p[1] * 1e-9) / 1e3 / vals[i] - 1))
            vals[r['from']], vals[i] = R, C_
    return vals


from PIL import Image
buf = io.BytesIO(); Image.new('RGB', (40, 30), 'gray').save(buf, 'JPEG'); JPG = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

admin = Client()
admin.call('/api/login', {'username': 'admin', 'password': 'abcXYZ123$'})
code, _ = admin.call('/api/user_create', {'username': 'x', 'name': 'x', 'role': 'ta', 'password': 'xxxxxxxx'}, ok=False)
assert code == 403, 'default admin must change the password first'
admin.call('/api/password', {'old': 'abcXYZ123$', 'new': 'Admin-test-2026'})
admin.call('/api/user_create', {'username': 'gvtest', 'name': 'GV', 'role': 'lecturer', 'password': 'lecturer-1'})
gv = Client(); gv.call('/api/login', {'username': 'gvtest', 'password': 'lecturer-1'}); gv.call('/api/password', {'old': 'lecturer-1', 'new': 'lecturer-2'})
d = gv.call('/api/class_create', {'course': 'SE009', 'term': 'Fall 2026', 'name': 'SE009.2', 'vset': 2})[1]; cid = d['created']
students = [{'sid': f'AUS{900 + i}', 'name': f'Student {i:02d}'} for i in range(19)]
d = gv.call('/api/roster_merge', {'cls': cid, 'students': students})[1]
C = d['classes'][str(cid)]
for lab in '1234':
    gv.call('/api/publish', {'cls': cid, 'lab': lab, 'card': True, 'submit': True, 'marks': True})
var = lambda st: C['vset'] * 100 + (3 * (st['team'] - 1) + st['member'] if st['member'] <= 3 else 18 + st['team'])
fours = [s for s in C['students'] if s['member'] == 4]
print('students', len(C['students']), '| team of 4:', [(s['team'], var(s)) for s in fours])
for st in C['students']:
    s = Client()
    assert s.call('/api/public/check', {'sid': st['sid'].lower()})[1]['name'] == st['name']
    s.call('/api/public/login', {'sid': st['sid'], 'password': 'pw-' + st['sid']})
    v = str(var(st))
    view = s.call(f'/api/public/class/{cid}')[1]
    assert view['variant'] == int(v), (view['variant'], v)
    for lab in '1234':
        s.call('/api/public/photo', {'cls': cid, 'lab': lab, 'data': JPG})
        s.call('/api/public/submit', {'cls': cid, 'lab': lab, 'values': answers(lab, v)})
    for lab in '1234':
        gv.call('/api/record', {'cls': cid, 'lab': lab, 'sid': st['sid'], 'tick': True})
    gv.call('/api/record', {'cls': cid, 'lab': '2', 'sid': st['sid'], 'manual': {'graph': 3}})
for t in range(1, 7):
    gv.call('/api/team', {'cls': cid, 'lab': '4', 'team': t, 'field': 'demo', 'value': 4})
# marks seen by students
tot = {}
for st in C['students']:
    s = Client(); s.call('/api/public/login', {'sid': st['sid'], 'password': 'pw-' + st['sid']})
    view = s.call(f'/api/public/class/{cid}')[1]
    tot[st['sid']] = [L['marks'] for L in view['labs']]
bad = {k: v for k, v in tot.items() if v != [12, 14, 14, 10]}
print('students with full marks:', len(tot) - len(bad), '/', len(tot), '| not full:', bad)
# tolerance rule on one student, Lab 1: +9% full, +15% half, +25% zero (per value)
st = C['students'][0]; v = str(var(st)); k = KEYS['1']['variants'][v]['keys']
s = Client(); s.call('/api/public/login', {'sid': st['sid'], 'password': 'pw-' + st['sid']})
gv.call('/api/record', {'cls': cid, 'lab': '1', 'sid': st['sid'], 'tick': False})
s.call('/api/public/unsubmit', {'cls': cid, 'lab': '1'})
s.call('/api/public/submit', {'cls': cid, 'lab': '1', 'values': [k[0] * 1.09, k[1] * 1.15, k[2] * 1.25, k[3] * 0.91]})
gv.call('/api/record', {'cls': cid, 'lab': '1', 'sid': st['sid'], 'tick': True})
m = [L['marks'] for L in s.call(f'/api/public/class/{cid}')[1]['labs']][0]
print('tolerance test Lab 1 (expect 3+1.5+0+3 = 7.5):', m)
# Lab 2: same Task 2 keys inside each team, different Task 1
for t in range(1, 7):
    mem = [str(var(x)) for x in C['students'] if x['team'] == t]
    k2 = {tuple(KEYS['2']['variants'][x]['keys'][1:]) for x in mem}; k1 = {KEYS['2']['variants'][x]['keys'][0] for x in mem}
    assert len(k2) == 1 and len(k1) == len(mem), (t, mem)
print('Lab 2 team check ok')
# Lab 2 Task 1 design rule: R, C giving fc 8 % above the target -> half marks (1 of 2), 3 % -> full
st = C['students'][0]; v = str(var(st)); vals = answers('2', v); tgt = KEYS['2']['variants'][v]['keys'][0]
s = Client(); s.call('/api/public/login', {'sid': st['sid'], 'password': 'pw-' + st['sid']})
for off, want in ((1.08, 13), (1.03, 14)):
    gv.call('/api/record', {'cls': cid, 'lab': '2', 'sid': st['sid'], 'tick': False}); s.call('/api/public/unsubmit', {'cls': cid, 'lab': '2'})
    ri = KEYS['2']['questions'][0][4]['from']                                      # index of R (Task 1)
    vals[0] = 1 / (2 * math.pi * vals[ri] * tgt * off * 1e3) * 1e9              # C (nF) for fc = target × off with the same R
    s.call('/api/public/submit', {'cls': cid, 'lab': '2', 'values': vals})
    gv.call('/api/record', {'cls': cid, 'lab': '2', 'sid': st['sid'], 'tick': True})
    m = [L['marks'] for L in s.call(f'/api/public/class/{cid}')[1]['labs']][1]
    assert m == want, (off, m, want)
print('Lab 2 Task 1 (R, C -> fc) rule ok: +8 % half, +3 % full')
import urllib.request as U
r=gv.op.open(BASE+'/api/export.xlsx'); b=r.read(); open('/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/_build/e2e_export.xlsx','wb').write(b); print('excel bytes', len(b))
open('/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/_build/e2e_cookie.txt', 'w').write('lecturer gv / lecturer-2')
