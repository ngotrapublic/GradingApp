"""Variant numbers, the scoring rule (same as the web page) and the Excel export."""
import io

from .config import KEYS


def variant(cls, st):
    if not st.get('team') or not st.get('member'):
        return None
    t, m = int(st['team']), int(st['member'])
    return int(cls) * 100 + (3 * (t - 1) + m if m <= 3 else 18 + t)   # member 4 (team of 4): 119..124


def score(cls, lab, st, data):
    lab = str(lab); L = KEYS['labs'][lab]; v = variant(cls, st)
    rec = data['classes'][cls]['labs'].get(lab, {}).get(st['sid'], {})
    if rec.get('override') is not None:          # lecturer's manual score wins
        return float(rec['override'])
    total = 0.0
    if v and str(v) in L['variants'] and rec.get('tick'):
        keys = L['variants'][str(v)]['keys']
        for i, q in enumerate(L['questions']):
            try:
                x = float((rec.get('values') or [None] * len(keys))[i])
            except (TypeError, ValueError, IndexError):
                continue
            err = abs(x / keys[i] - 1)
            total += q[3] if err <= KEYS['rule']['full'] else (q[3] / 2 if err <= KEYS['rule']['half'] else 0)
    for m in L['manual']:
        if m[3] == 'student':
            total += float((rec.get('manual') or {}).get(m[0], 0) or 0)
        elif st.get('team'):
            total += float(data['classes'][cls].get('team', {}).get(lab, {}).get(str(st['team']), {}).get(m[0], 0) or 0)
    return total


def export_xlsx(data):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook(); wb.remove(wb.active)
    for cls, C in data['classes'].items():
        ws = wb.create_sheet((C.get('name') or f'Lớp {cls}')[:30])
        hdr = ['MSSV', 'Họ tên', 'Nhóm', 'TV', 'Mã đề'] + [f'Lab {l} (/{KEYS["labs"][l]["total"]})' for l in '1234'] + ['Tổng /50', 'Quy về /10 (50%)']
        ws.append(hdr)
        for c in ws[1]:
            c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='549E39'); c.alignment = Alignment(horizontal='center', wrap_text=True)
        for st in sorted(C['students'], key=lambda s: (int(s.get('team') or 99), int(s.get('member') or 9), s['name'])):
            sc = [score(cls, l, st, data) for l in '1234']
            ws.append([st['sid'], st['name'], st.get('team'), st.get('member'), variant(cls, st)] + sc + [sum(sc), round(sum(sc) / 5, 2)])
        for col, w in zip('ABCDEFGHIJK', [14, 28, 7, 5, 8, 11, 11, 11, 11, 10, 12]):
            ws.column_dimensions[col].width = w
        ws.freeze_panes = 'C2'
    bio = io.BytesIO(); wb.save(bio); return bio.getvalue()
