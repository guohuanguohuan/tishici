# -*- coding: utf-8 -*-
"""T3验收脚本（一次性，工作区子文件夹内）：八项验收实测落盘
①run字号解析值抽查计数 ②行距解析值计数 ③docDefaults实测 ④docGrid实测
⑤零文字diff（w:t/m:t流恒等＋段落文本逐段＋oMath子树sha256） ⑦幂等二跑zip成员级DIFF
⑧跳过/待人工清单计数   ⑥COM页数在 _COM页数.py 单独跑"""
import sys, io, os, re, json, zipfile, hashlib, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
TOOL = r'C:\Users\28120\Desktop\提示词\工具\字号双档改版.py'

def q(t):
    return '{%s}%s' % (W, t)

def loc(el):
    try:
        return etree.QName(el).localname
    except ValueError:
        return ''

def ptext(el):
    return ''.join(t.text or '' for t in el.iter(q('t')))

def load_doc(path):
    z = zipfile.ZipFile(path)
    d = etree.fromstring(z.read('word/document.xml'))
    st = etree.fromstring(z.read('word/styles.xml'))
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    return d, st, parts

def under_drawing(r):
    a = r.getparent()
    while a is not None:
        if loc(a) in ('drawing', 'pict', 'txbxContent', 'object'):
            return True
        a = a.getparent()
    return False

def run_sz(r):
    rpr = r.find(q('rPr'))
    if rpr is None:
        return None
    sz = rpr.find(q('sz'))
    return sz.get(q('val')) if sz is not None else None

def resolved(r, default='24'):
    return run_sz(r) or default

def classify_replay(doc, h3ids):
    """与工具同规则的独立重放（验收①用）——单遍完成分类＋run解析值核对
    （lxml代理id跨遍历不稳定，必须单遍内持引用完成）"""
    body = doc.find(q('body'))
    els = list(body)
    zone = 'INIT'
    expected = 1
    first = False
    cnt = {'正文run=24': 0, '正文run≠24': 0, '解析run=18': 0, '解析run≠18': 0,
           '标题run(豁免)': 0, '跳过run(纯图/PUA/图内)': 0}
    bad = []
    samples24, samples18 = [], []

    def tally(p, cls_):
        for r in p.iter(q('r')):
            if under_drawing(r):
                cnt['跳过run(纯图/PUA/图内)'] += 1
                continue
            has_txt = any(t.text for t in r.findall(q('t')))
            if r.find(q('drawing')) is not None or r.find(q('pict')) is not None:
                if not has_txt:
                    cnt['跳过run(纯图/PUA/图内)'] += 1
                    continue
            if any(t.text and re.search(r'[\uE000-\uF8FF]', t.text) for t in r.findall(q('t'))):
                cnt['跳过run(纯图/PUA/图内)'] += 1
                continue
            rpr = r.find(q('rPr'))
            szel = rpr.find(q('sz')) if rpr is not None else None
            v = szel.get(q('val')) if szel is not None else '24(继承)'
            if cls_ == '标题':
                cnt['标题run(豁免)'] += 1
            elif cls_ == '正文':
                if v == '24':
                    cnt['正文run=24'] += 1
                    if len(samples24) < 25:
                        samples24.append(ptext(p)[:24])
                else:
                    cnt['正文run≠24'] += 1
                    bad.append({'段': ptext(p)[:20], '解析值': v, '判档': cls_})
            else:
                if v == '18':
                    cnt['解析run=18'] += 1
                    if len(samples18) < 25:
                        samples18.append(ptext(p)[:24])
                else:
                    cnt['解析run≠18'] += 1
                    bad.append({'段': ptext(p)[:20], '解析值': v, '判档': cls_})

    for bi, el in enumerate(els):
        tag = loc(el)
        if tag == 'tbl':
            rows = el.findall(q('tr'))
            frow = ptext(rows[0]) if rows else ''
            is_nav = ('题型组数' in frow) or ('节名' in frow and '题号区间' in frow)
            for p in el.iter(q('p')):
                tally(p, '解析' if (is_nav or zone == 'ANS') else '正文')
            continue
        if tag != 'p':
            continue
        text = ptext(el)
        ps = el.find(q('pPr'))
        pstyle = ''
        if ps is not None:
            pst = ps.find(q('pStyle'))
            pstyle = pst.get(q('val')) if pst is not None else ''
        if not text.strip():
            tally(el, '解析' if zone == 'ANS' else '正文')
            continue
        is_title = False
        if not first:
            is_title = True
        elif (pstyle in h3ids and re.match(r'^\d+(\.\d+)+\s+\S', text)) \
                or re.match(r'^\d+(\.\d+)*\s*方法讲解[｜|]', text) \
                or re.match(r'^\d+(\.\d+)+\s+\S', text):
            is_title = True
        first = True
        if is_title:
            tally(el, '标题')
            zone = 'LECT' if re.match(r'^\d+(\.\d+)*\s*方法讲解[｜|]', text) else 'INIT'
            continue
        mq = re.match(r'^(\d{1,4})．（', text)
        if mq and int(mq.group(1)) == expected:
            expected += 1
            zone = 'STEM'
            tally(el, '正文')
            continue
        if mq and zone == 'ANS':
            tally(el, '解析')
            continue
        if mq:
            expected = int(mq.group(1)) + 1
            zone = 'STEM'
            tally(el, '正文')
            continue
        if re.match(r'^(?:本节|全件)\d+题', text):
            tally(el, '解析')
            continue
        if re.match(r'^〔基〕＝', text):
            tally(el, '解析')
            continue
        if re.match(r'^【[^】]{1,30}】', text):
            if zone in ('STEM', 'ANS'):
                zone = 'ANS'
            tally(el, '解析')
            continue
        if zone == 'ANS':
            tally(el, '解析')
            continue
        tally(el, '正文')
    return cnt, bad[:12], samples18[:10], samples24[:10]

def verify(base_path, out_path, tag):
    rep = {'tag': tag, 'base': base_path, 'out': out_path}
    bdoc, bst, bparts = load_doc(base_path)
    odoc, ost, oparts = load_doc(out_path)

    # ⑤ 零文字diff
    def stream(doc):
        return [t.text or '' for t in doc.iter() if isinstance(t.tag, str) and loc(t) == 't']
    rep['⑤文字流恒等'] = (stream(bdoc) == stream(odoc))
    bparas = [ptext(p) for p in bdoc.find(q('body')).iter(q('p'))]
    oparas = [ptext(p) for p in odoc.find(q('body')).iter(q('p'))]
    rep['⑤段落文本逐段恒等'] = (bparas == oparas)
    rep['⑤段落数'] = [len(bparas), len(oparas)]
    # oMath子树哈希（公式区零改动）
    def omath_hash(doc):
        h = hashlib.sha256()
        n = 0
        for om in doc.iter('{%s}oMath' % M):
            h.update(etree.tostring(om))
            n += 1
        return h.hexdigest()[:16], n
    rep['⑤oMath子树sha256[基线,输出]与块数'] = [omath_hash(bdoc), omath_hash(odoc)]

    # ① 字号解析值（分类重放→逐run核对，非抽样：全量计数）
    h3ids = set()
    for st_el in ost.findall(q('style')):
        nm = st_el.find(q('name'))
        if nm is not None and nm.get(q('val')) in ('heading 2', '标题2', 'heading 3', '标题3'):
            h3ids.add(st_el.get(q('styleId')))
    cnt, bad, samples18, samples24 = classify_replay(odoc, h3ids)
    rep['①字号全量计数'] = cnt
    rep['①偏差样例(前12)'] = bad
    rep['①解析run抽查样本(前10)'] = samples18
    rep['①正文run抽查样本(前10)'] = samples24
    rep['①全量全过'] = (cnt['正文run≠24'] == 0 and cnt['解析run≠18'] == 0)

    # ①b 固定锚点抽验（基线勘测已知元素序）
    body_o = list(odoc.find(q('body')))
    anchors = []
    def anchor(idx, expect):
        p = body_o[idx]
        szs = set()
        for r in p.iter(q('r')):
            if under_drawing(r):
                continue
            v = run_sz(r)
            if v:
                szs.add(v)
        anchors.append({'元素序': idx, '文本': ptext(p)[:20], '期望档': expect,
                        '显式sz集合': sorted(szs), '过': (szs == {expect})})
    if 'X2' in tag:
        for i, e in [(2, '24'), (3, '24'), (14, '24'), (15, '24'), (16, '18'), (17, '18'),
                     (23, '18'), (26, '18'), (29, '18'), (30, '18'), (45, '18'), (46, '18')]:
            anchor(i, e)
    else:
        for i, e in [(8, '24'), (9, '24'), (18, '24'), (26, '24'), (33, '24'), (47, '24'),
                     (48, '24'), (1, '18'), (5, '18'), (7, '18'), (10, '18'), (11, '18'),
                     (12, '18'), (29, '18'), (406, '18'), (409, '24'), (412, '24'),
                     (415, '24'), (418, '24'), (622, '18')]:
            anchor(i, e)
    rep['①固定锚点抽验'] = anchors
    rep['①锚点全过'] = all(a['过'] for a in anchors)

    # ② 行距解析值计数
    sp = {'410-atLeast': 0, '280-atLeast': 0, '其他': []}
    for s in odoc.iter(q('spacing')):
        key = (s.get(q('line')), s.get(q('lineRule')))
        if key == ('410', 'atLeast'):
            sp['410-atLeast'] += 1
        elif key == ('280', 'atLeast'):
            sp['280-atLeast'] += 1
        elif loc(s.getparent()) == 'pPr' or s.getparent().tag == q('pPr'):
            sp['其他'].append({loc(k): v for k, v in s.attrib.items()})
    rep['②行距计数'] = {k: (v if not isinstance(v, list) else v[:5]) for k, v in sp.items()}
    # 页眉页脚
    hdr = [n for n in oparts if re.match(r'word/header\d*\.xml$', n)]
    ftr = [n for n in oparts if re.match(r'word/footer\d*\.xml$', n)]
    hdr_skip = 0
    hdr_detail = []
    for n in hdr:
        hroot = etree.fromstring(oparts[n])
        for p in hroot.iter(q('p')):
            ppr = p.find(q('pPr'))
            spel = ppr.find(q('spacing')) if ppr is not None else None
            val = {loc(k): v for k, v in spel.attrib.items()} if spel is not None else None
            hdr_detail.append(val)
            hdr_skip += 1
        rep['②页眉段跳过数'] = hdr_skip
        rep['②页眉段spacing实测'] = hdr_detail
    rep['②页脚部件字节等同基线(跳过不动)'] = all(oparts[n] == bparts[n] for n in ftr)

    # ③ docDefaults实测
    dd = ost.find(q('docDefaults'))
    got = {}
    rprd = dd.find(q('rPrDefault'))
    if rprd is not None and rprd.find(q('rPr')) is not None:
        rpr = rprd.find(q('rPr'))
        rf = rpr.find(q('rFonts'))
        got['rPrDefault.rFonts'] = {loc(k): v for k, v in rf.attrib.items()} if rf is not None else None
        got['rPrDefault.sz'] = rpr.find(q('sz')).get(q('val')) if rpr.find(q('sz')) is not None else None
        szcs = rpr.find(q('szCs'))
        got['rPrDefault.szCs'] = szcs.get(q('val')) if szcs is not None else None
    pprd = dd.find(q('pPrDefault'))
    if pprd is not None and pprd.find(q('pPr')) is not None:
        s2 = pprd.find(q('pPr')).find(q('spacing'))
        got['pPrDefault.spacing'] = {loc(k): v for k, v in s2.attrib.items()} if s2 is not None else None
    rep['③docDefaults实测'] = got
    rep['③docDefaults全过'] = (got.get('rPrDefault.sz') == '24' and got.get('rPrDefault.szCs') == '24'
                           and (got.get('pPrDefault.spacing') or {}).get('line') == '410'
                           and (got.get('pPrDefault.spacing') or {}).get('lineRule') == 'atLeast'
                           and (got.get('pPrDefault.spacing') or {}).get('before') == '0'
                           and (got.get('pPrDefault.spacing') or {}).get('after') == '0'
                           and (got.get('rPrDefault.rFonts') or {}).get('eastAsia') == '宋体'
                           and (got.get('rPrDefault.rFonts') or {}).get('ascii') == 'Times New Roman'
                           and not any('Theme' in k for k in (got.get('rPrDefault.rFonts') or {})))

    # ④ docGrid实测
    grids = []
    for dg in odoc.iter(q('docGrid')):
        grids.append({loc(k): v for k, v in dg.attrib.items()})
    rep['④docGrid实测'] = grids if grids else '无docGrid元素'
    rep['④docGrid无行网格'] = all(g.get('type') not in ('lines', 'linesAndChars') for g in grids)

    # ⑦ 幂等二跑：zip成员级DIFF
    out2 = out_path.replace('.docx', '.二跑.docx')
    subprocess.run([sys.executable, TOOL, out_path, out2], check=True,
                   capture_output=True)
    z1 = zipfile.ZipFile(out_path)
    z2 = zipfile.ZipFile(out2)
    m1 = {n: z1.read(n) for n in z1.namelist()}
    m2 = {n: z2.read(n) for n in z2.namelist()}
    z1.close()
    z2.close()
    rep['⑦幂等二跑成员级DIFF'] = {'成员集等': set(m1) == set(m2),
                            '差异成员': sorted(n for n in m1 if m1.get(n) != m2.get(n))}
    rep['⑦幂等'] = set(m1) == set(m2) and all(m1[n] == m2[n] for n in m1)
    os.remove(out2)
    j2 = out2.replace('.docx', '.docx.字号双档.json')
    if os.path.exists(j2):
        os.remove(j2)

    # ⑧ 待人工清单
    jp = out_path + '.字号双档.json'
    if os.path.exists(jp):
        tj = json.load(open(jp, encoding='utf-8'))
        rep['⑧待人工数'] = len(tj['待人工'])
        rep['⑧标题段跳过计数'] = tj['分类计数']['标题段跳过']
        rep['⑧跳过计数'] = {k: tj['run计数'][k] for k in
                       ('纯图run跳过', 'PUA run跳过', '图形内部run跳过', '标题豁免run数(留T4)')}
    return rep


if __name__ == '__main__':
    wd = os.path.dirname(os.path.abspath(__file__))
    reports = []
    for base, out, tag in [('小件X2.docx', '改版X2.docx', 'X2小件'),
                           ('大件B讲上.docx', '改版B讲上.docx', 'B讲上大件')]:
        bp, op = os.path.join(wd, base), os.path.join(wd, out)
        # 重跑一遍保证用的是当前工具版
        subprocess.run([sys.executable, TOOL, bp, op,
                        '--qcount', '13' if 'X2' in base else '61'], check=True, capture_output=True)
        reports.append(verify(bp, op, tag))
    with open(os.path.join(wd, '验收实测.json'), 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=1)
    ok = True
    for r in reports:
        print('=====', r['tag'])
        for k in ['⑤文字流恒等', '⑤段落文本逐段恒等', '⑤oMath子树sha256[基线,输出]与块数',
                  '①字号全量计数', '①锚点全过', '②行距计数', '②页眉段跳过数', '②页眉段spacing实测',
                  '②页脚部件字节等同基线(跳过不动)', '③docDefaults实测', '③docDefaults全过',
                  '④docGrid实测', '④docGrid无行网格', '⑦幂等', '⑧待人工数', '⑧标题段跳过计数', '⑧跳过计数']:
            print(' ', k, '→', r.get(k))
        for a in r.get('①固定锚点抽验', []):
            if not a['过']:
                print('   锚点FAIL:', a)
                ok = False
        ok = ok and r['⑤文字流恒等'] and r['⑤段落文本逐段恒等'] and r['①锚点全过'] \
            and r['①全量全过'] and r['③docDefaults全过'] and r['④docGrid无行网格'] and r['⑦幂等']
    print('总判定:', 'ALL PASS' if ok else 'FAIL')
