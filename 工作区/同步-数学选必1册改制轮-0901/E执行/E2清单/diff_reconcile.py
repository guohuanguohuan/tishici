# -*- coding: utf-8 -*-
"""E2一次性：归一化diff对账（规格书§1口径J）——基线vs工作 document.xml 段落文字流（w:t+m:t线性化）
授权差异仅：①条目号/题号重编号（N．→节号-序号．，余文恒等）②页眉页脚同串重建（部件级，另核）
③节名锚段插入（文本=节标题）④空图段清删的纯空白run（口径B工具债①授权）＋⑤分型补空格（登记数）
其余=0。输出逐笔登记表。
用法: python diff_reconcile.py <基线.docx> <工作.docx> <登记.md>"""
import sys, re, difflib, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)

def para_flow(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    out = []
    for p in body.iter(q('p')):
        s = ''
        for el in p.iter():
            ln = etree.QName(el).localname if isinstance(el.tag, str) else '?'
            if ln == 't':
                s += el.text or ''
        if s.strip():
            out.append(s)
    return out

ENT_OLD = re.compile(r'^(\d{1,3})．')
ENT_NEW = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){1,3})-(\d{1,3})．')

def main(base, work, md):
    a = para_flow(base)
    b_raw = para_flow(work)
    # 授权③节名锚段＝节标题文本在 b 中多出的重复份（锚段文本=节标题原文，插在真标题前）
    from collections import Counter
    ca = Counter(a)
    cb = Counter(b_raw)
    anchor_drops = []
    b = []
    seen = Counter()
    SEC = re.compile(r'^\d+\.\d+(\.\d+)?\s+\S')
    for t in b_raw:
        if SEC.match(t) and seen[t] < cb[t] - ca.get(t, 0):
            # 该文本多出的第一份＝锚段（锚在真标题前，序列中先出现）
            seen[t] += 1
            anchor_drops.append(t)
            continue
        b.append(t)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    rows = [('授权③节名锚段插入', '', t[:40]) for t in anchor_drops]
    ok = True
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        if op == 'replace':
            # 配对重编号：等长且逐对满足「N．→节号-序号．＋余文恒等」
            if i2 - i1 == j2 - j1:
                allrenum = True
                for x in range(i2 - i1):
                    old, new = a[i1 + x], b[j1 + x]
                    mo, mn = ENT_OLD.match(old), ENT_NEW.match(new)
                    if not (mo and mn and old[mo.end():] == new[mn.end():]):
                        allrenum = False
                        rows.append(('未授权·replace', old[:60], new[:60]))
                if allrenum:
                    for x in range(i2 - i1):
                        old, new = a[i1 + x], b[j1 + x]
                        rows.append(('授权①条目号重编', old[:24], new[:24]))
                    continue
            ok = False
            for x in range(i1, i2): rows.append(('未授权·replace', a[x][:60], ''))
            for y in range(j1, j2): rows.append(('未授权·replace→', '', b[y][:60]))
        elif op == 'insert':
            for y in range(j1, j2):
                t = b[y]
                ok = False
                rows.append(('未授权·insert', '', t[:60]))
        elif op == 'delete':
            for x in range(i1, i2):
                ok = False
                rows.append(('未授权·delete', a[x][:60], ''))
    with open(md, 'w', encoding='utf-8') as f:
        f.write('# 归一化diff对账登记表：%s → %s\n\n' % (base, work))
        f.write('- 基线段落数（非空文字）%d｜工作 %d\n' % (len(a), len(b)))
        f.write('- 结论：%s（未授权差异=%d笔）\n\n' % ('PASS' if ok else 'FAIL',
                  sum(1 for r in rows if r[0].startswith('未授权'))))
        f.write('| 类别 | 基线 | 工作 |\n|---|---|---|\n')
        for c, x, y in rows:
            f.write('| %s | %s | %s |\n' % (c, x.replace('|', '/'), y.replace('|', '/')))
    print('%s 未授权=%d 授权登记=%d 段落 %d→%d' % ('PASS' if ok else 'FAIL',
        sum(1 for r in rows if r[0].startswith('未授权')), len(rows), len(a), len(b)))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
