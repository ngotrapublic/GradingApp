"""Minimal builder to assemble HCM decks from the HN decks (same template)."""
import os, re, shutil, zipfile
from xml.sax.saxutils import escape
from PIL import Image

EMU = 914400
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
SLIDE_CT = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
REL_SLIDE = NS_R + '/slide'
REL_IMG = NS_R + '/image'
REL_LAYOUT = NS_R + '/slideLayout'


def unzip(src, dst):
    shutil.rmtree(dst, ignore_errors=True)
    zipfile.ZipFile(src).extractall(dst)


def slide_order(d):
    """Return slide file names (e.g. 'slide12.xml') in presentation order."""
    pres = open(f'{d}/ppt/presentation.xml', encoding='utf8').read()
    rels = open(f'{d}/ppt/_rels/presentation.xml.rels', encoding='utf8').read()
    rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
    rmap.update({a: b for b, a in re.findall(r'Target="slides/(slide\d+\.xml)"[^>]*Id="(rId\d+)"', rels)})
    return [rmap[r] for r in re.findall(r'<p:sldId [^>]*r:id="(rId\d+)"', pres)]


class Deck:
    def __init__(self, base_pptx, workdir):
        self.d = workdir
        unzip(base_pptx, workdir)
        self.order = slide_order(workdir)
        self.base_order = list(self.order)
        files = os.listdir(f'{workdir}/ppt/slides')
        self.next_slide = max(int(re.findall(r'\d+', f)[0]) for f in files if f.endswith('.xml')) + 1
        self.next_media = 1
        self.new_files = []

    # ---------- helpers ----------
    def _new_slide_name(self):
        n = f'slide{self.next_slide}.xml'; self.next_slide += 1; return n

    def _copy_media(self, path, prefix='hcm'):
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        name = f'{prefix}{self.next_media}.{ext}'; self.next_media += 1
        shutil.copy(path, f'{self.d}/ppt/media/{name}')
        self._ensure_ext(ext)
        return name

    def _ensure_ext(self, ext):
        p = f'{self.d}/[Content_Types].xml'
        ct = open(p, encoding='utf8').read()
        mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif', 'emf': 'image/x-emf', 'wmf': 'image/x-wmf', 'svg': 'image/svg+xml', 'tif': 'image/tiff', 'tiff': 'image/tiff'}[ext]
        if f'Extension="{ext}"' not in ct:
            ct = ct.replace('<Default Extension="xml"', f'<Default Extension="{ext}" ContentType="{mime}"/><Default Extension="xml"')
            open(p, 'w', encoding='utf8').write(ct)

    def slide_file(self, n):
        """File name of the n-th slide (1-based) of the ORIGINAL base deck."""
        return self.base_order[n - 1]

    # ---------- import / create ----------
    def import_slide(self, src_dir, src_file, prefix):
        """Copy a slide from another unpacked deck built on the same template."""
        name = self._new_slide_name()
        xml = open(f'{src_dir}/ppt/slides/{src_file}', encoding='utf8').read()
        rels = open(f'{src_dir}/ppt/slides/_rels/{src_file}.rels', encoding='utf8').read()
        out = []
        for m in re.finditer(r'<Relationship [^>]*/>', rels):
            r = m.group(0)
            if '/notesSlide"' in r:
                continue
            if '/image"' in r and 'TargetMode="External"' not in r:
                tgt = re.search(r'Target="\.\./media/([^"]+)"', r).group(1)
                new = self._copy_media(f'{src_dir}/ppt/media/{tgt}', prefix)
                r = r.replace(f'../media/{tgt}', f'../media/{new}')
            out.append(r)
        open(f'{self.d}/ppt/slides/{name}', 'w', encoding='utf8').write(xml)
        self._write_rels(name, out)
        self.new_files.append(name)
        return name

    def new_slide(self, shapes_xml, images=()):
        """shapes_xml may reference {img0}, {img1}... for r:embed ids of `images`."""
        name = self._new_slide_name()
        rels = [f'<Relationship Id="rId1" Type="{REL_LAYOUT}" Target="../slideLayouts/slideLayout7.xml"/>',
                f'<Relationship Id="rId2" Type="{REL_IMG}" Target="../media/image1.png"/>']
        ids = {}
        for i, p in enumerate(images):
            media = self._copy_media(p)
            rid = f'rId{i + 3}'
            rels.append(f'<Relationship Id="{rid}" Type="{REL_IMG}" Target="../media/{media}"/>')
            ids[f'img{i}'] = rid
        body = shapes_xml.format(**ids) if ids else shapes_xml
        xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
               'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
               'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree>'
               '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
               '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
               + body + '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')
        open(f'{self.d}/ppt/slides/{name}', 'w', encoding='utf8').write(xml)
        self._write_rels(name, rels)
        self.new_files.append(name)
        return name

    def _write_rels(self, name, rels):
        os.makedirs(f'{self.d}/ppt/slides/_rels', exist_ok=True)
        open(f'{self.d}/ppt/slides/_rels/{name}.rels', 'w', encoding='utf8').write(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + ''.join(rels) + '</Relationships>')

    def edit_text(self, name, pairs):
        p = f'{self.d}/ppt/slides/{name}'
        x = open(p, encoding='utf8').read()
        for old, new in pairs:
            o, n = f'<a:t>{escape(old)}</a:t>', f'<a:t>{escape(new)}</a:t>'
            assert o in x, (name, old)
            x = x.replace(o, n)
        open(p, 'w', encoding='utf8').write(x)

    # ---------- finalize ----------
    def finalize(self, order, out_pptx):
        d = self.d
        pres_p, rels_p, ct_p = f'{d}/ppt/presentation.xml', f'{d}/ppt/_rels/presentation.xml.rels', f'{d}/[Content_Types].xml'
        rels = open(rels_p, encoding='utf8').read()
        # drop all slide rels, rebuild
        rels = re.sub(r'<Relationship [^>]*Type="' + re.escape(REL_SLIDE) + r'"[^>]*/>', '', rels)
        used = set(int(x) for x in re.findall(r'Id="rId(\d+)"', rels))
        nid = max(used) + 1
        sld = []
        for i, f in enumerate(order):
            rid = f'rId{nid + i}'
            rels = rels.replace('</Relationships>', f'<Relationship Id="{rid}" Type="{REL_SLIDE}" Target="slides/{f}"/></Relationships>')
            sld.append(f'<p:sldId id="{300 + i}" r:id="{rid}"/>')
        open(rels_p, 'w', encoding='utf8').write(rels)
        pres = open(pres_p, encoding='utf8').read()
        pres = re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>', '<p:sldIdLst>' + ''.join(sld) + '</p:sldIdLst>', pres, flags=re.S)
        open(pres_p, 'w', encoding='utf8').write(pres)
        ct = open(ct_p, encoding='utf8').read()
        for f in order:
            part = f'/ppt/slides/{f}'
            if f'PartName="{part}"' not in ct:
                ct = ct.replace('</Types>', f'<Override PartName="{part}" ContentType="{SLIDE_CT}"/></Types>')
        open(ct_p, 'w', encoding='utf8').write(ct)
        # remove section list (old sections would reference deleted slides)
        pres = open(pres_p, encoding='utf8').read()
        pres = re.sub(r'<p:ext uri="\{521415D9-36F7-43E2-AB2F-B90AF26B5E84\}">.*?</p:ext>', '', pres, flags=re.S)
        open(pres_p, 'w', encoding='utf8').write(pres)


# ---------------- shape XML generators (match HN style) ----------------
def E(v):
    return int(round(v * EMU))


class Ids:
    def __init__(self):
        self.n = 10

    def __call__(self):
        self.n += 1
        return self.n


def rpr(sz, bold=False, color=None, italic=False, sub=False):
    c = f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' if color else ''
    return (f'<a:rPr lang="en-US" sz="{int(sz * 100)}"{" b=\"1\"" if bold else ""}{" i=\"1\"" if italic else ""}{" baseline=\"-25000\"" if sub else ""} dirty="0">{c}'
            '<a:latin typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/>'
            '<a:cs typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/></a:rPr>')


SUB_RE = re.compile(r'(?<![A-Za-z0-9])([A-Za-z]{1,2})_([A-Za-z0-9]{1,5})(?![A-Za-z0-9])|(?<![A-Za-z0-9])(V)(out|in)(,pp)?(?![A-Za-z0-9])|(?<![A-Za-z0-9])([fZ])(0)(?![A-Za-z0-9])')


def runs(text, sz, color=None):
    """**bold** markup -> runs."""
    out = []
    for i, part in enumerate(re.split(r'\*\*', text)):
        if not part:
            continue
        b = i % 2 == 1
        # subscripts: R_eq, I_A, f_max ...; Vin/Vout (+ ",pp"); f0, Z0
        pos = 0
        for m in SUB_RE.finditer(part):
            base, sub = (m.group(1), m.group(2)) if m.group(1) else ((m.group(3), m.group(4) + (m.group(5) or '')) if m.group(3) else (m.group(6), m.group(7)))
            if m.start() > pos:
                out.append(f'<a:r>{rpr(sz, bold=b, color=color)}<a:t>{escape(part[pos:m.start()])}</a:t></a:r>')
            out.append(f'<a:r>{rpr(sz, bold=b, color=color)}<a:t>{escape(base)}</a:t></a:r>')
            out.append(f'<a:r>{rpr(sz, bold=b, color=color, sub=True)}<a:t>{escape(sub)}</a:t></a:r>')
            pos = m.end()
        if pos < len(part):
            out.append(f'<a:r>{rpr(sz, bold=b, color=color)}<a:t>{escape(part[pos:])}</a:t></a:r>')
    return ''.join(out) or f'<a:endParaRPr lang="en-US" sz="{int(sz*100)}"/>'


def para(text, sz, level=0, bullet=None, align=None, color=None, space_after=6):
    """bullet: None | 'dot' | 'num'"""
    marl = {0: 342900, 1: 800100, 2: 1257300}[level]
    algn = f' algn="{align}"' if align else ''
    sa = f'<a:spcAft><a:spcPts val="{space_after * 100}"/></a:spcAft>'
    if bullet == 'dot':
        ppr = f'<a:pPr marL="{marl}" lvl="{level}" indent="-342900"{algn}>{sa}<a:buFont typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/><a:buChar char="•"/></a:pPr>'
    elif bullet == 'num':
        ppr = f'<a:pPr marL="{marl}" lvl="{level}" indent="-342900"{algn}>{sa}<a:buFont typeface="+mj-lt"/><a:buAutoNum type="arabicPeriod"/></a:pPr>'
    else:
        ppr = f'<a:pPr{algn}>{sa}<a:buNone/></a:pPr>'
    return f'<a:p>{ppr}{runs(text, sz, color)}</a:p>'


def header(ids, title):
    """Blue title bar + logo, identical geometry to HN slides."""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids()}" name="Title Bar"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="886397"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            '<a:solidFill><a:schemeClr val="accent1"/></a:solidFill></p:spPr>'
            '<p:txBody><a:bodyPr wrap="square" anchor="ctr"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            '<a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-US" sz="2400" spc="-150"><a:solidFill><a:schemeClr val="bg1"/></a:solidFill>'
            '<a:latin typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/><a:cs typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/></a:rPr>'
            f'<a:t>{escape(title)}</a:t></a:r></a:p></p:txBody></p:sp>'
            + pic(ids, 'rId2', 0, 0, 1872791 / EMU, 879378 / EMU, 'Logo'))


def textbox(ids, x, y, w, h, paras_xml, anchor='t', fill=None, line=None, geom='rect', inset=0.1):
    f = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
    ln = f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>' if line else ''
    ins = E(inset)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids()}" name="TextBox {ids.n}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm><a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>{f}{ln}</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{ins}" tIns="{ins}" rIns="{ins}" bIns="{ins}" rtlCol="0" anchor="{anchor}"><a:normAutofit/></a:bodyPr><a:lstStyle/>{paras_xml}</p:txBody></p:sp>')


def pic(ids, rid, x, y, w, h, name='Picture'):
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{ids()}" name="{name} {ids.n}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')


def fit_pic(ids, rid, path, x, y, w, h):
    """Place image inside box (x,y,w,h) keeping aspect, centred."""
    iw, ih = Image.open(path).size
    s = min(w / iw, h / ih)
    pw, ph = iw * s, ih * s
    return pic(ids, rid, x + (w - pw) / 2, y + (h - ph) / 2, pw, ph)


def table(ids, x, y, colw, rows, sz=14, header_fill='549E39', row_h=0.4):
    """rows[0] is header. Cells may use **bold**."""
    grid = ''.join(f'<a:gridCol w="{E(c)}"/>' for c in colw)
    trs = []
    for ri, row in enumerate(rows):
        tcs = []
        for cell in row:
            lines = cell.split('\n')
            bul = '<a:pPr marL="228600" indent="-228600"><a:buFont typeface="Arial"/><a:buChar char="&#8226;"/></a:pPr>'
            ps = ''.join(f'<a:p>{bul if l.startswith("- ") else ""}{runs(l[2:] if l.startswith("- ") else l, sz, "FFFFFF" if ri == 0 else None)}</a:p>' for l in lines)
            fill = f'<a:solidFill><a:srgbClr val="{header_fill}"/></a:solidFill>' if ri == 0 else (
                '<a:solidFill><a:srgbClr val="EEF5EA"/></a:solidFill>' if ri % 2 == 0 else '<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>')
            bd = ''.join(f'<a:{s} w="9525"><a:solidFill><a:srgbClr val="BFBFBF"/></a:solidFill></a:{s}>' for s in ('lnL', 'lnR', 'lnT', 'lnB'))
            tcs.append(f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>{ps}</a:txBody><a:tcPr marL="91440" marR="91440" marT="45720" marB="45720" anchor="ctr">{bd}{fill}</a:tcPr></a:tc>')
        trs.append(f'<a:tr h="{E(row_h)}">{"".join(tcs)}</a:tr>')
    return (f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{ids()}" name="Table {ids.n}"/><p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(sum(colw))}" cy="{E(row_h * len(rows))}"/></p:xfrm>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
            f'<a:tbl><a:tblPr firstRow="1" bandRow="1"/><a:tblGrid>{grid}</a:tblGrid>{"".join(trs)}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>')


def section(ids, title, subtitle=''):
    """Section divider: full-width blue band in the middle, like HN section slides."""
    p = para(title, 36, align='ctr', color='FFFFFF', space_after=0)
    if subtitle:
        p += para(subtitle, 24, align='ctr', color='FFFFFF', space_after=0)
    return (pic(ids, 'rId2', 0, 0, 1872791 / EMU, 879378 / EMU, 'Logo')
            + f'<p:sp><p:nvSpPr><p:cNvPr id="{ids()}" name="Section Band"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="0" y="{E(2.6)}"/><a:ext cx="12192000" cy="{E(2.2)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            '<a:solidFill><a:schemeClr val="accent1"/></a:solidFill></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" anchor="ctr"><a:normAutofit/></a:bodyPr><a:lstStyle/>{p}</p:txBody></p:sp>')


def card(ids, x, y, w, h, num, title, body, sz=16):
    """Numbered step card: circle with number + bold title + body text."""
    circ = (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids()}" name="Step {num}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{E(x + w / 2 - 0.35)}" y="{E(y)}"/><a:ext cx="{E(0.7)}" cy="{E(0.7)}"/></a:xfrm><a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
            '<a:solidFill><a:schemeClr val="accent1"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr anchor="ctr" lIns="0" rIns="0" tIns="0" bIns="0"/><a:lstStyle/>{para(str(num), 24, align="ctr", color="FFFFFF", space_after=0).replace("<a:r><a:rPr", "<a:r><a:rPr b=\"1\"", 1)}</p:txBody></p:sp>')
    box = textbox(ids, x, y + 0.45, w, h - 0.45,
                  para('', 8, space_after=0) + para(f'**{title}**', sz + 2, align='ctr') + ''.join(para(b, sz, align='ctr') for b in body),
                  fill='F3F7F0', line='B7CFA8', geom='roundRect', inset=0.15)
    return box + circ


# ---------------- tone edits for reused HN slides (deck, slide no) ----------------
U1 = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/_build/u1'
EDITS = {
    (1, 12): [('Or you risk damaging the device!!!', 'Otherwise you may damage the device.')],
    (1, 57): [('“But lecturer, WhY dO I nEeD tO dO tHiS?”', 'Why do we need this?'),
              ('Unless you own an electronic component manufacturing company and want to waste your money', 'So we combine standard values to get the value we need')],
    (2, 26): [('WHY????', 'Why?')],
    (2, 66): [('We get: 0.1Vpp, 500 Hz signal at the speaker???', 'We get: 0.1 Vpp, 500 Hz signal at the speaker. Why?')],
    (2, 71): [('ONLY NOISES!!!', 'Only noise is visible.')],
    (2, 82): [('Does that mean we can just use smaller R for better Q???', 'Does a smaller R always give a better filter? Check it in the exercise.')],
    (3, 16): [('What is it doing here???', 'What is this capacitor for?')],
    (3, 21): [('752 mVpp????', '752 mVpp.')],
    (3, 22): [('752 mVpp????', '752 mVpp.'), ('RIGHT???????????', 'Let us check.')],
    (3, 25): [('SURPRISED????', 'Why not?')],
    (3, 26): [('SURPRISED????', 'Why not?')],
    (3, 27): [('Remember this from lab session 2????', 'Remember the speaker test from earlier today?')],
    (3, 63): [('Watch out for the correct polarity of the capacitors!!!', 'Watch out for the correct polarity of the capacitors.'),
              ('Or you blow up your capacitors!!!', 'A reversed electrolytic capacitor can burst.')],
    (3, 65): [('Look at that!!!', 'Result:')],
    (3, 68): [('Look at that!!!', 'Result:')],
    (3, 77): [('Right????', 'Is it?')],
    (3, 78): [('You will hear a horrible echo sound', 'You will hear a loud echo (acoustic feedback)')],
    (3, 79): [('You will hear a horrible echo sound', 'You will hear a loud echo (acoustic feedback)')],
}


def para_replace(x, old, new):
    """Replace a whole paragraph whose (run-joined) text equals `old`. Keeps the first run's formatting."""
    from xml.sax.saxutils import unescape
    def fix(m):
        pxml = m.group(0)
        txt = ''.join(unescape(t) for t in re.findall(r'<a:t>([^<]*)</a:t>', pxml))
        if txt.strip() != old.strip():
            return pxml
        first = [True]
        def rep(mm):
            if first[0]:
                first[0] = False
                return f'<a:t>{escape(new)}</a:t>'
            return '<a:t></a:t>'
        return re.sub(r'<a:t>[^<]*</a:t>', rep, pxml)
    return re.sub(r'<a:p>.*?</a:p>', fix, x, flags=re.S)


def tone(dk, name, deck, n):
    p = f'{dk.d}/ppt/slides/{name}'
    x = open(p, encoding='utf8').read()
    for old, new in EDITS.get((deck, n), []):
        x = para_replace(x, old, new)
    open(p, 'w', encoding='utf8').write(x)
    return name


def hn_section(dk, title, subtitle=''):
    """Copy the HN section-divider slide (deck 1, slide 52) and change its text."""
    src = slide_order(U1)[51]
    name = dk.import_slide(U1, src, 'sec_')
    dk.edit_text(name, [('Basic DC circuits', title), ('Construct more resistors', subtitle or ' ')])
    return name

# ---- grammar / clarity fixes in reused HN slides ----
EDITS.update({
    (1, 10): [('A digital multimeter often have the following functions:', 'A digital multimeter usually has these functions:')],
    (1, 16): [('Lecturer will now instruct the students to measure resistors', 'Now we measure resistors'),
              ('Remember: Never trust the manufacturers!', 'Remember: the printed value is not exact.'),
              ('Always re-measure your components for the exact value!', 'Always measure your components again.')],
    (1, 25): [('Different row and columns have different metal connections', 'Rows and columns are connected by metal strips inside'),
              ('Could be different for the one you buy', 'Other breadboards may be different')],
    (1, 26): [('Long lines connected horizonally', 'Long lines are connected horizontally'),
              ('Short lines connected veritically', 'Short lines are connected vertically'),
              ('But they stop at the middle', 'They stop at the middle gap')],
    (1, 27): [('Anyone first tries using breadboard often connects it wrong….', 'Beginners often connect the breadboard wrongly.'),
              ('Because they don’t notice the metal connections below', 'They forget the metal strips under the holes.')],
    (1, 35): [('When you construct circuits, you just need to construct node by node', 'Build your circuit node by node'),
              ('You only care about which branches are connected at every single node.', 'At each node, check which parts are connected.')],
    (3, 34): [('It takes the different between V+(non-inverting) and V-(inverting) inputs', 'It takes the difference between the V+ (non-inverting) and V− (inverting) inputs')],
    (3, 38): [('Only work if you feed enough voltage', 'It works only with a supply voltage')],
    (3, 39): [('Only work if you feed enough voltage', 'It works only with a supply voltage')],
    (3, 42): [('Alright', 'Now')],
    (3, 43): [('We’re gonna use LM358', 'We will use the LM358'), ('Many pins aren’t there?', 'It has 8 pins.'),
              ('What features should we watch out?', 'What should we check first?')],
    (3, 46): [('Always check for its ratings before using', 'Always check the ratings before use'),
              ('Or your device may blow up', 'Otherwise the IC can be damaged'),
              ('Or it doesn’t work and you blame other people for your mistake', 'or the circuit does not work')],
})
EDITS[(2, 55)] = []


KEYWORDS = {
 1: [('Multimeter (DMM)', 'One meter that measures voltage, current and resistance', 'Set it to V to measure voltage'),
     ('Probe', 'The wire and metal tip that touches the circuit', 'Red probe = +, black probe = COM'),
     ('Breadboard', 'A board to build circuits without soldering', 'Holes in one short line are connected'),
     ('Node', 'A point where two or more parts are connected', 'Node X in the exercise'),
     ('Series / parallel', 'Series: one after another, same current. Parallel: side by side, same voltage', '1 kΩ + 1 kΩ = 2 kΩ;  1 kΩ ∥ 1 kΩ = 500 Ω'),
     ('Equivalent resistance', 'One resistor that can replace a group of resistors', 'R_eq of your circuit'),
     ('Current limit', 'The highest current the power supply will give', 'Set it to 1 A or less'),
     ('Oscilloscope / function generator', 'Shows a signal as a wave / makes a signal (sine, square…)', 'CH1 = yellow, CH2 = blue'),
     ('Peak-to-peak (Vpp)', 'From the lowest point to the highest point of a wave', '10 Vpp = from −5 V to +5 V')],
 2: [('Filter', 'A circuit that lets some frequencies pass and blocks others', 'A radio picks one station'),
     ('Low-pass / high-pass', 'Passes low frequencies / passes high frequencies', 'Bass / treble in music'),
     ('Band-pass', 'Passes only frequencies near one value', 'Near f0 only'),
     ('Cut-off frequency (fc)', 'The frequency where Vout = 0.707 × Vin', 'fc = 1 / (2πRC)'),
     ('Capacitor / inductor', 'C stores charge (unit F) / L is a coil of wire (unit H)', '22 nF, 1 mH'),
     ('Resonance (f0)', 'The frequency where the effects of L and C cancel', 'f0 ≈ 32 kHz today'),
     ('Quality factor (Q)', 'How sharp the peak is. Big Q = narrow, high peak', 'Q = 2'),
     ('Bandwidth (BW)', 'How wide the passed band is', 'BW = f_H − f_L'),
     ('Tolerance', 'How far a real part can be from its printed value', '±5%')],
 3: [('Op-amp', 'An IC that amplifies the difference between its two inputs', 'LM358 has 2 op-amps'),
     ('Gain', 'How many times bigger the output is', 'Vin 0.1 V → Vout 2 V: gain = 20'),
     ('Inverting', 'The output is upside down compared with the input', 'Gain = −R2 / R1'),
     ('Phase shift', 'How far one wave is moved from the other, in degrees', '180° = upside down'),
     ('Feedback resistor', 'The resistor from the output back to the input', 'R2 in the exercise'),
     ('Supply pins (Vcc, Vee)', 'Pins that give power to the IC', 'Pin 8 = +6 V, pin 4 = −6 V'),
     ('Datasheet', 'The document from the maker with pins and limits', 'Search “LM358 datasheet”'),
     ('Decoupling capacitor', 'A capacitor from the supply to GND that removes noise', '470 µF and 100 nF'),
     ('Clipping', 'The wave is cut flat because the output cannot go higher', 'Vout too big for ±6 V')],
 4: [('Speaker', 'Turns an AC voltage into sound', '8 Ω speaker on the PB-503A'),
     ('Electret microphone', 'A small microphone that turns sound into a small voltage', 'Signal in mV'),
     ('Bias', 'The DC voltage a part needs to work', 'Microphone gets DC through a resistor'),
     ('Coupling capacitor', 'Passes AC, blocks DC between two parts of a circuit', '1 µF between mic and amplifier'),
     ('Decoupling capacitor', 'Sends noise on the supply to GND', '470 µF on each rail'),
     ('Stage', 'One part of a circuit with several parts in a row', 'Stage 1 → stage 2'),
     ('Load', 'What is connected to an output and takes current', 'The speaker is the load'),
     ('Acoustic feedback', 'The speaker sound goes back into the microphone → loud echo', 'Turn the gain down'),
     ('Troubleshoot', 'Find and fix a fault in a circuit', 'Measure stage by stage')],
}


def keywords_slide(dk, lab):
    ids = Ids()
    rows = [['Word', 'Meaning (simple English)', 'Example']] + [[f'**{a}**', b, c] for a, b, c in KEYWORDS[lab]]
    return dk.new_slide(header(ids, f'Key words for Lab {lab}') + table(ids, 0.45, 1.15, [3.0, 5.6, 3.8], rows, sz=14, row_h=0.58))


POS = {'R': (8.65, 6.0, 4.3, 0.75), 'L': (0.4, 6.15, 4.6, 0.7), 'N': (0.25, 5.6, 2.6, 1.0), 'T': (4.6, 1.05, 3.1, 0.8), 'P': (9.8, 6.3, 3.2, 0.65), 'TR': (10.6, 1.1, 2.6, 1.0)}


def add_callout(dk, name, term, meaning, pos='R'):
    """Small 'New word' box on an existing slide."""
    x, y, w, h = POS[pos]
    p = f'{dk.d}/ppt/slides/{name}'
    xml = open(p, encoding='utf8').read()
    ids = Ids(); ids.n = 900
    box = (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids()}" name="Key word callout"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
           f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>'
           '<a:solidFill><a:srgbClr val="FFF4D6"/></a:solidFill><a:ln w="12700"><a:solidFill><a:srgbClr val="E0A800"/></a:solidFill></a:ln></p:spPr>'
           f'<p:txBody><a:bodyPr wrap="square" lIns="91440" tIns="45720" rIns="91440" bIns="45720" anchor="ctr"><a:normAutofit/></a:bodyPr><a:lstStyle/>'
           f'{para(f"**New word: {term}** = {meaning}", 13, space_after=0)}</p:txBody></p:sp>')
    xml = xml.replace('</p:spTree>', box + '</p:spTree>', 1)
    open(p, 'w', encoding='utf8').write(xml)
    return name


def review_slides(dk, lab):
    """Two slides reviewing the key words of `lab`: questions first, then answers."""
    words = KEYWORDS[lab]
    ids = Ids()
    rows = [['Word', 'Can you explain it?']] + [[f'**{a}**', ''] for a, _, _ in words]
    q = dk.new_slide(header(ids, f'Review – words from Lab {lab}') + table(ids, 0.45, 1.15, [3.6, 8.8], rows, sz=15, row_h=0.58))
    ids = Ids()
    rows = [['Word', 'Meaning (simple English)', 'Example']] + [[f'**{a}**', b, c] for a, b, c in words]
    a = dk.new_slide(header(ids, f'Review – words from Lab {lab} (answers)') + table(ids, 0.45, 1.15, [3.0, 5.6, 3.8], rows, sz=14, row_h=0.58))
    return [q, a]


def add_line_after(dk, name, find, new):
    """Insert a new paragraph (copy of the one containing `find`) after it, with text `new`."""
    p = f'{dk.d}/ppt/slides/{name}'
    x = open(p, encoding='utf8').read()
    for m in re.finditer(r'<a:p>.*?</a:p>', x, flags=re.S):
        if f'<a:t>{escape(find)}</a:t>' in m.group(0):
            new_p = re.sub(r'<a:t>[^<]*</a:t>', f'<a:t>{escape(new)}</a:t>', m.group(0), count=1)
            x = x[:m.end()] + new_p + x[m.end():]
            open(p, 'w', encoding='utf8').write(x)
            return
    raise AssertionError((name, find))


def widen_shape(dk, name, find, width_in):
    p = f'{dk.d}/ppt/slides/{name}'
    x = open(p, encoding='utf8').read()
    for m in re.finditer(r'<p:sp>.*?</p:sp>', x, flags=re.S):
        if f'<a:t>{escape(find)}</a:t>' in m.group(0):
            sp = re.sub(r'(<a:xfrm[^>]*><a:off [^/]*/><a:ext cx=")\d+(")', lambda mm: mm.group(1) + str(E(width_in)) + mm.group(2), m.group(0), count=1)
            x = x[:m.start()] + sp + x[m.end():]
            open(p, 'w', encoding='utf8').write(x)
            return
    raise AssertionError((name, find))
