# -*- coding: utf-8 -*-
"""标题字号梯子.py — 2026-08-28 拍板「标题字号梯子」（纯格式，零字符）：
  章/讲标题（文内开头标题段）→ 四号（28半点）加粗；
  教材节标题（extract_structure 判定的 section，含二级 1.1 与三级 1.1.1）→ 小四（24）加粗；
  题型标题（group，「X.Y.Z 标题：题型」）→ 五号（21）加粗。
章首导航表等表格内段落不动；节标题序号底纹不动（本脚本只管字号与加粗）。
标题分类复用升级版 extract_structure 的判定（节标题数/题型标题数与自检①⑧同源对账）。
用法: python 标题字号梯子.py <docx> <报告txt>"""
import sys, io, zipfile, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_structure import structure

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

LADDER = {'chapter': 28, 'section': 24, 'group': 21}

def set_sz_b(r, halfpt):
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    if rpr.find(q('b')) is None:
        # b/bCs 序在 rFonts 之后
        b = etree.Element(q('b'))
        rf = rpr.find(q('rFonts'))
        rpr.insert(list(rpr).index(rf) + 1 if rf is not None else 0, b)
    for stag in ('sz', 'szCs'):
        el = rpr.find(q(stag))
        if el is None:
            el = etree.Element(q(stag))
            # sz/szCs 序在 kern/position 之后、highlight 之前；简化：追加在已有 szCs 位或末尾前
            rpr.append(el)
        el.set(q('val'), str(halfpt))

def ladder(path, report):
    st = structure(path)
    secs = {x['el'] for x in st['items'] if x['kind'] == 'section'}
    grps = {x['el'] for x in st['items'] if x['kind'] == 'group'}
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    els = list(body)
    cnt = {'chapter': 0, 'section': 0, 'group': 0}
    touched_runs = 0
    for i, el in enumerate(els):
        if tag(el) != 'p':
            continue
        if i == 0:
            kind = 'chapter'   # 文内开头标题＝章/讲标题
        elif i in secs:
            kind = 'section'
        elif i in grps:
            kind = 'group'
        else:
            continue
        for r in el.findall(q('r')):
            set_sz_b(r, LADDER[kind])
            touched_runs += 1
        cnt[kind] += 1
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.ladder'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name, b in parts.items():
        zo.writestr(name, b)
    zo.close()
    for k in range(12):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            time.sleep(6)
    else:
        raise RuntimeError('locked: ' + path)
    with open(report, 'w', encoding='utf-8') as f:
        f.write('标题字号梯子：%s\n章/讲标题(28) %d 段｜节标题(24) %d 段｜题型标题(21) %d 段｜动run %d\n'
                % (os.path.basename(path), cnt['chapter'], cnt['section'], cnt['group'], touched_runs))
        f.write('节标题数与题型标题数取自 extract_structure（与自检①⑧同源）。\n')
    try:
        print('梯子:', cnt, '动run', touched_runs)
    except ValueError:
        pass  # extract_structure 导入时重包 stdout，旧包装被 GC 连带关闭缓冲；结果以报告文件为准

if __name__ == '__main__':
    ladder(sys.argv[1], sys.argv[2])
