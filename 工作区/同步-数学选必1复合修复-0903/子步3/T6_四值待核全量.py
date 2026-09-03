# -*- coding: utf-8 -*-
"""子步3 T6 四值待核项【全量】二层核验 v2：讲部块页域＝全部讲部标题（知识讲解＋方法讲解）
至下一块级标题页；待核页须落入某页域。归因复刻 灰度四值校验.py 逻辑。"""
import sys, io, re, json, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pymupdf
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def pfill(p):
    ppr = p.find(q('pPr'))
    s = ppr.find(q('shd')) if ppr is not None else None
    return s.get(q('fill')) if s is not None else None

SUB3 = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3'
NAMES = {'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
         'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
         'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
         'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
         'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
         'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'}
RED = re.compile(r'卡壳看答案|【答案】|【详解】|【分析】|【点睛】|（简单|（中档|（难·')
RE_ENT = re.compile(r'^\d+(?:\.\d+)+-\d+．')
RE_SUB = re.compile(r'^（\d+）')
HDR = ('节名', '题量', '题型组数', '简单/中档/难', '节内题号')
TOL = 2  # 与灰度四值校验.py match_target tol_ch=2 一致

ok_all = True
result = {}
for vol, fn in NAMES.items():
    z = zipfile.ZipFile(SUB3 + '\\定稿\\' + fn)
    root = etree.fromstring(z.read('word/document.xml'))
    titles = []
    for el in root.find(q('body')):
        if tag(el) != 'p':
            continue
        f = pfill(el)
        if f not in ('C6D4E3', 'ADC2DA'):
            continue
        t = re.sub(r'\s+', '', ptext(el))
        is_lec = ('方法讲解｜' in t) or ('知识讲解｜' in t)
        titles.append((t[:14], is_lec))
    doc = pymupdf.open(SUB3 + '\\pdf\\%s.pdf' % vol)
    page_txt = [re.sub(r'\s+', '', doc[p].get_text()) for p in range(len(doc))]
    pages = []
    cur = 0
    for key, is_lec in titles:
        found = None
        for p in range(cur, len(doc)):
            if key in page_txt[p]:
                found = p
                break
        if found is None:
            k2 = re.match(r'^(\d+(?:\.\d+)+)', key).group(1)
            k2 += '方法讲解｜' if '方法讲解｜' in key else ('知识讲解｜' if '知识讲解｜' in key else '')
            for p in range(cur, len(doc)):
                if k2 in page_txt[p]:
                    found = p
                    break
        assert found is not None, (vol, key)
        pages.append((found + 1, is_lec))
        cur = found
    zones = []
    for i, (pg, is_lec) in enumerate(pages):
        if is_lec:
            end = pages[i + 1][0] if i + 1 < len(pages) else len(doc)
            zones.append((pg, end))
    attr = {'条目号式': 0, '第一子层式': 0, '导航表表头': 0}
    todo = []
    for pno in range(len(doc)):
        for d in doc[pno].get_drawings():
            f = d.get('fill')
            if not f:
                continue
            rgb = (round(f[0] * 255), round(f[1] * 255), round(f[2] * 255))
            if not all(abs(c - 201) <= TOL for c in rgb):
                continue
            rc = d['rect']
            clip = pymupdf.Rect(rc.x0 - 1, rc.y0 - 1, rc.x1 + 1, rc.y1 + 1)
            txt = re.sub(r'[\s　]+', '', doc[pno].get_text('text', clip=clip))
            txt = txt.replace('‐', '-').replace('‑', '-').replace('\xad', '-')
            if RE_ENT.match(txt):
                attr['条目号式'] += 1
            elif RE_SUB.match(txt):
                attr['第一子层式'] += 1
            elif any(w in txt for w in HDR):
                attr['导航表表头'] += 1
            else:
                todo.append((pno + 1, txt[:24]))
    bad_red = [(p, t) for p, t in todo if RED.search(t)]
    bad_zone = [(p, t) for p, t in todo if not any(f <= p <= l for f, l in zones)]
    ok = not bad_red and not bad_zone
    ok_all &= ok
    result[vol] = {'讲部块页域数': len(zones), '归因': attr, '待核总数': len(todo),
                   '红旗': bad_red[:5], '页域外': bad_zone[:8]}
    print(vol, '讲部页域', len(zones), '待核', len(todo), '红旗', len(bad_red),
          '页域外', len(bad_zone), '判定', 'PASS' if ok else 'FAIL')
    if bad_zone[:4]:
        print('   样本', bad_zone[:4])
    doc.close()
json.dump(result, open(SUB3 + '\\四值2\\待核全量核验.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('总判定:', 'PASS' if ok_all else 'FAIL')
