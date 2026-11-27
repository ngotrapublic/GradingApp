"""Review quiz banks under courses/<CODE>/quizzes/*.json and attempt shuffle/grading."""
import json
import math
import os
import random
import re
import secrets

from .config import COURSES_DIR
from .courses import COURSES

_MOBILE_UA = re.compile(
    r'Android|webOS|iPhone|iPod|iPad|Tablet|Kindle|Silk|BlackBerry|IEMobile|Opera Mini|Mobile|CriOS|FxiOS',
    re.I,
)
_DESKTOP_UA = re.compile(r'Windows NT|Macintosh|X11|Linux x86_64|CrOS', re.I)


def is_phone_or_tablet_ua(ua, client_claim=''):
    """Allow phones/tablets; reject typical desktop browsers (UA/claim can be spoofed)."""
    s = ua or ''
    claim = (client_claim or '').strip().lower()
    if _MOBILE_UA.search(s):
        return True
    # iPadOS / some tablets report a desktop UA; trust the page's touch check claim
    if claim in ('phone', 'tablet') and re.search(r'Macintosh|Windows NT', s, re.I):
        return True
    if _DESKTOP_UA.search(s):
        return False
    return False


def quiz_dir(course):
    return os.path.join(COURSES_DIR, course, 'quizzes')


def list_banks(course):
    """Return [{slug, title, n}] for JSON banks of a course."""
    d = quiz_dir(course)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if not name.endswith('.json'):
            continue
        path = os.path.join(d, name)
        try:
            bank = json.load(open(path, encoding='utf8'))
        except (OSError, json.JSONDecodeError):
            continue
        slug = bank.get('slug') or name[:-5]
        out.append({
            'slug': slug,
            'title': bank.get('title') or slug,
            'n': len(bank.get('questions') or []) + sum(map(len, bank.get('required_questions') or [])),
            'n_pick': int(bank.get('n_pick') or 20),
            'pass_score': int(bank.get('pass_score') or 14),
        })
    return out


def load_bank(course, slug):
    """Load one bank dict or None."""
    d = quiz_dir(course)
    if not os.path.isdir(d):
        return None
    for name in os.listdir(d):
        if not name.endswith('.json'):
            continue
        path = os.path.join(d, name)
        try:
            bank = json.load(open(path, encoding='utf8'))
        except (OSError, json.JSONDecodeError):
            continue
        if (bank.get('slug') or name[:-5]) == slug:
            return bank
    return None


def course_has_quizzes(course):
    return bool(list_banks(course))


def leave_cooldown_sec(leaves):
    """1st leave: 1 min; each further leave doubles (2, 4, 8, …)."""
    if leaves < 1:
        return 0
    return 60 * (2 ** (leaves - 1))


def is_left_submit(answers, flag=False):
    """Leave-app submit: explicit flag or empty / marker payload."""
    if flag:
        return True
    if not answers:
        return True
    if isinstance(answers, dict) and set(answers.keys()) <= {'__left'}:
        return True
    return False


def parse_number(raw):
    if raw is None:
        return None
    try:
        value = float(str(raw).strip().replace(',', '.').replace('−', '-').replace(' ', ''))
    except (ValueError, OverflowError):
        return None
    return value if math.isfinite(value) else None


def parse_mantissa_exp(raw, legacy_power10=0):
    """Parse the two-field answer, scientific notation, or a legacy coefficient."""
    invalid = (None, None, None)
    if raw is None or raw == '':
        return invalid
    if isinstance(raw, dict):
        mantissa = raw.get('m', raw.get('mantissa'))
        exponent = raw.get('e', raw.get('exp', raw.get('power10')))
    else:
        parts = re.split(r'[eE]', str(raw).strip(), maxsplit=1)
        mantissa = parts[0]
        exponent = parts[1] if len(parts) == 2 else legacy_power10
    m = parse_number(mantissa)
    e = 0.0 if exponent is None or exponent == '' else parse_number(exponent)
    if m is None or e is None or not e.is_integer() or abs(e) > 308:
        return invalid
    e = int(e)
    value = m * (10.0 ** e)
    return (value, m, e) if math.isfinite(value) else invalid


def numeric_ok(chosen, correct, tol_rel=0.03, tol_abs=None):
    """Accept within relative or absolute tolerance."""
    if chosen is None or correct is None:
        return False
    correct = float(correct)
    chosen = float(chosen)
    if tol_abs is None:
        tol_abs = max(1e-12, abs(correct) * 1e-6)
    if abs(chosen - correct) <= tol_abs:
        return True
    if correct == 0:
        return abs(chosen) <= tol_abs
    return abs(chosen - correct) <= abs(correct) * float(tol_rel)


def hint_band_ok(score, total=20):
    """Stuck band scaled from old 5–7 / 10 → exclusive (half_pass, pass)."""
    if score is None:
        return False
    try:
        s = float(score)
    except (TypeError, ValueError):
        return False
    lo = float(total) * 0.5   # was 5/10
    hi = float(total) * 0.7   # was 7/10 (= pass mark)
    return lo < s < hi


def should_unlock_hints(prior_scores, total=20):
    """Unlock hints on next try if: >5 finished tries (any scores), or 3+ tries all stuck in (10,14)/20."""
    scores = [s for s in (prior_scores or []) if s is not None]
    if len(scores) > 5:
        return True
    if len(scores) < 3:
        return False
    return all(hint_band_ok(s, total=total) for s in scores)


def build_paper(bank, n_pick=None, rng=None):
    """Pick questions, shuffle MCQ choices. Numeric items keep a typed answer key."""
    rng = rng or random.Random(secrets.token_hex(8))
    qs = list(bank.get('questions') or [])
    required = [rng.choice(forms) for forms in (bank.get('required_questions') or [])]
    n = min(int(n_pick or bank.get('n_pick') or 20), len(qs) + len(required))
    if n <= 0:
        return None, []
    picked = required[:n] + rng.sample(qs, max(0, n - len(required)))
    rng.shuffle(picked)
    paper = []
    client = []
    for q in picked:
        qtype = q.get('type') or 'mcq'
        hint = (q.get('hint') or '').strip()
        if qtype == 'numeric':
            power10 = int(q.get('power10') or 0)
            item = {
                'id': q['id'],
                'type': 'numeric',
                'stem': q['stem'],
                'answer': float(q['answer']),
                'unit': q.get('unit') or '',
                'power10': power10,
                'tol_rel': float(q.get('tol_rel') or 0.03),
                'tol_abs': q.get('tol_abs'),
                'explain': q.get('explain') or '',
                'hint': hint,
            }
            paper.append(item)
            client.append({
                'id': q['id'],
                'type': 'numeric',
                'stem': q['stem'],
                'unit': item['unit'],
                'hint': hint,
            })
            continue
        choices = list(q['choices'])
        order = list(range(len(choices)))
        rng.shuffle(order)
        shuffled = [choices[i] for i in order]
        correct_pos = order.index(int(q['answer']))
        paper.append({
            'id': q['id'],
            'type': 'mcq',
            'stem': q['stem'],
            'choices': shuffled,
            'answer': correct_pos,
            'explain': q.get('explain') or '',
            'hint': hint,
        })
        client.append({
            'id': q['id'],
            'type': 'mcq',
            'stem': q['stem'],
            'choices': shuffled,
            'hint': hint,
        })
    return paper, client


def grade_paper(paper, answers):
    """answers: {qid: choice_index or number string}. Returns score, total, review rows."""
    total = len(paper)
    score = 0
    review = []
    ans = answers or {}
    for q in paper:
        raw = ans.get(q['id'], ans.get(str(q['id'])))
        qtype = q.get('type') or 'mcq'
        if qtype == 'numeric':
            chosen, mantissa, exp = parse_mantissa_exp(raw, legacy_power10=int(q.get('power10') or 0))
            ok = numeric_ok(chosen, q['answer'], tol_rel=q.get('tol_rel') or 0.03, tol_abs=q.get('tol_abs'))
            if ok:
                score += 1
            review.append({
                'id': q['id'],
                'type': 'numeric',
                'stem': q['stem'],
                'unit': q.get('unit') or '',
                'power10': exp if exp is not None else int(q.get('power10') or 0),
                'correct': q['answer'],
                'chosen': chosen,
                'mantissa': mantissa,
                'exp': exp,
                'ok': ok,
                'explain': q.get('explain') or '',
            })
            continue
        try:
            chosen = int(raw) if raw is not None and raw != '' else None
        except (TypeError, ValueError, OverflowError):
            chosen = None
        ok = chosen is not None and chosen == int(q['answer'])
        if ok:
            score += 1
        review.append({
            'id': q['id'],
            'type': 'mcq',
            'stem': q['stem'],
            'choices': q.get('choices') or [],
            'correct': int(q['answer']),
            'chosen': chosen,
            'ok': ok,
            'explain': q.get('explain') or '',
        })
    return score, total, review


def courses_with_quizzes():
    return [c for c in COURSES if course_has_quizzes(c)]
