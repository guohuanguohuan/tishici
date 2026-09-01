# -*- coding: utf-8 -*-
# 一次性脚本（E1衔接）：改制前后文字流逐段diff对账（body/header/footer分件；段落级对齐＋差异归类）
import sys, io, zipfile, difflib, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)

def part_paras(zf, name):
    root = etree.fromstring(zf.read(name))
    out = []
    for p in root.iter(q('p')):
        buf = []
        for node in p.iter():
            if node.tag in (q('t'), qm('t')):
                buf.append(node.text or '')
            elif node.tag == q('instrText'):
                buf.append('')
        out.append(''.join(buf))
    return out

base, work = sys.argv[1], sys.argv[2]
za, zb = zipfile.ZipFile(base), zipfile.ZipFile(work)
report = {}
for part in ['word/document.xml', 'word/header1.xml', 'word/footer1.xml']:
    if part not in za.namelist() or part not in zb.namelist():
        report[part] = {'状态': '部件缺省跳过'}
        continue
    A, B = part_paras(za, part), part_paras(zb, part)
    sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
    diffs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        diffs.append({'op': tag, '基线段': A[max(0, i1 - 1):i2 + 1], '成品段': B[max(0, j1 - 1):j2 + 1]})
    report[part] = {'基线段数': len(A), '成品段数': len(B), '差异块数': len(diffs), '差异': diffs}
za.close(); zb.close()
print(json.dumps(report, ensure_ascii=False, indent=1))
with open(sys.argv[3], 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
