# -*- coding: utf-8 -*-
"""②D_01b_差源逐器探针.py — oMath 段计数逐器溯源。
对 衔接1/衔接2/下79/89 四件，用 ②工具/副本_工具建设期留档 的 .bak 链分 era 清点：
  bak_题号终态(=X0 同步盘复制态) → bak_统计段拆(pre-T3) → bak_标签行(pre-T5)
  → bak_底纹批(pre-T6a) → 主件(=X1 工具建设期末态)
各 era 按 T9 工具同口径清点 oMath 段（短≤60/长>60/总数），定位计数变化发生在哪个工具执行。
另对比 X1 与 ②-C 终态副本（现副本）的 oMath 段序列，确认 ②-B/②-C 对 oMath 段序列的影响。
报告落盘：报告/②D_01b_差源逐器探针.md"""
import sys, io, os, zipfile, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
WJ = '⁠'
def eff_len(s):
    return sum(1.0 if ord(c) > 0x2E7F else 0.5 for c in s)
def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def omath_sig(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    out = []
    for p in body.iter(q('p')):
        n_om = len(list(p.iter(qm('oMath'))))
        if not n_om:
            continue
        t = ptext(p)
        out.append((round(eff_len(t), 1), n_om, t.replace(WJ, '')[:44]))
    return out

ARCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本_工具建设期留档')
CUR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本')
ERA_BAKS = [
    ('X0=bak_题号终态', '.docx.bak_题号终态'),
    ('preT3=bak_统计段拆', '.docx.bak_统计段拆'),
    ('preT5=bak_标签行', '.docx.bak_标签行'),
    ('preT6a=bak_底纹批', '.docx.bak_底纹批'),
    ('X1=主件', '.docx'),
]
NAMES = {
    '衔接1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）',
    '衔接2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）',
    '下79': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）',
    '89': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）',
    '上61': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）',
}
# T9_dry 基线（②-A 前登记）：短/长
DRY_BASE = {'衔接1': (142, 4), '衔接2': (64, 5), '下79': (459, 187), '89': (822, 153), '上61': (646, 79)}

OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

for sh, base in NAMES.items():
    db = DRY_BASE[sh]
    say('## %s（T9_dry 基线 短%d/长%d/%d）' % (sh, db[0], db[1], db[0] + db[1]))
    sigs = {}
    for tag, suf in ERA_BAKS:
        p = os.path.join(ARCH, base + suf)
        if not os.path.exists(p):
            say('  %-18s 缺档' % tag)
            continue
        L = omath_sig(p)
        s = sum(1 for e, _, _ in L if e <= 60)
        g = sum(1 for e, _, _ in L if e > 60)
        n_om = sum(n for _, n, _ in L)
        sigs[tag] = L
        say('  %-18s 段%4d（短%4d/长%4d）｜oMath元素 %4d' % (tag, len(L), s, g, n_om))
    # X0 vs preT3 vs preT5：序列 diff（只报增删，不报 eff 漂移）
    def diff(ta, a, tb, b, cap=8):
        sm = difflib.SequenceMatcher(a=[x[2] for x in a], b=[x[2] for x in b], autojunk=False)
        rows = []
        for tagc, i1, i2, j1, j2 in sm.get_opcodes():
            if tagc == 'equal':
                continue
            for e, n, t in a[i1:i2]:
                rows.append('    [%s−] eff=%s oMath=%d | %s' % (ta, e, n, t))
            for e, n, t in b[j1:j2]:
                rows.append('    [%s+] eff=%s oMath=%d | %s' % (tb, e, n, t))
        return rows[:cap], len(rows)
    pairs = [('X0=bak_题号终态', 'preT3=bak_统计段拆'), ('preT3=bak_统计段拆', 'preT5=bak_标签行'),
             ('preT5=bak_标签行', 'preT6a=bak_底纹批'), ('preT6a=bak_底纹批', 'X1=主件')]
    for ta, tb in pairs:
        if ta in sigs and tb in sigs:
            rows, ntot = diff(ta, sigs[ta], tb, sigs[tb], cap=40)
            if ntot:
                say('  diff %s→%s：%d 行差异（前%d）' % (ta, tb, ntot, min(ntot, 40)))
                for r in rows:
                    say(r)
    if 'X1=主件' in sigs:
        cur = omath_sig(os.path.join(CUR, NAMES[sh] + '.docx'))
        sm = difflib.SequenceMatcher(a=[x[2] for x in sigs['X1=主件']], b=[x[2] for x in cur], autojunk=False)
        nd = sum(1 for t_, i1, i2, j1, j2 in sm.get_opcodes() if t_ != 'equal')
        s2 = sum(1 for e, _, _ in cur if e <= 60)
        g2 = sum(1 for e, _, _ in cur if e > 60)
        say('  X1→②C终态: 段%d（短%d/长%d）｜序列差异 opcode=%d %s'
            % (len(cur), s2, g2, nd, '（一致）' if nd == 0 else '!!需细查'))
    say('')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '报告', '②D_01b_差源逐器探针.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('# ②D oMath 段计数逐器溯源（X0→X1 逐工具 + X1→②C）\n\n```text\n' + '\n'.join(OUT) + '\n```\n')
print('REPORT:', out, flush=True)
