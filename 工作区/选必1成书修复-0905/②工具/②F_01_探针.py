# -*- coding: utf-8 -*-
"""②F_01_探针.py — ②-F 丢失集元素级重建预检（探针，不改写任何文件）。
口径：donor=副本_②B留档/*.bak_标签行(preT5)，cur=副本/*.docx(②-C 终态)。
匹配键＝(oMath 单元 canonical 序列化, k)=（单元内 m:oMath 计数, 单元前非空白 w:t 字符数）。
输出：逐件 om 总数、双向 multiset 差、全文归一文本守恒、k 匹配丢失集、题号段样例。
落盘 → 报告/②F_01_探针.md"""
import sys, io, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
from collections import Counter

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
WS_RE = re.compile(r'[\s　\xa0​]+')
def norm(s): return WS_RE.sub('', s)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

BASE = os.path.dirname(os.path.abspath(__file__))
DONOR = os.path.join(BASE, '副本_②B留档')
CUR = os.path.join(BASE, '副本')
NAMES = [
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）'),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）'),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）'),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）'),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）'),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）'),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）'),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）'),
]
EXPECT_LOST = {'衔接1': 6, '上61': 7, '下79': 20, '衔接2': 2, '92': 19, '90': 16, '68': 14, '89': 18}
EXPECT_PRE = {'衔接1': 882, '上61': 3261, '下79': 2876, '衔接2': 243, '92': 2699, '90': 2914, '68': 2362, '89': 4039}
EXPECT_POST = {'衔接1': 876, '上61': 3254, '下79': 2856, '衔接2': 241, '92': 2680, '90': 2898, '68': 2348, '89': 4021}


def load(path):
    z = zipfile.ZipFile(path)
    tree = etree.fromstring(z.read('word/document.xml'))
    parts = {i.filename: z.read(i.filename) for i in z.infolist()}
    z.close()
    return tree, parts


def math_units(p):
    """段直接子级的 m:oMath / m:oMathPara 单元；并检出更深层的散落 oMath。"""
    units, deep = [], 0
    for ch in p:
        t = etree.QName(ch).localname
        ns = etree.QName(ch).namespace
        if ns == M and t in ('oMath', 'oMathPara'):
            units.append(ch)
    seen = set()
    for u in units:
        for d in u.iter(qm('oMath')):
            seen.add(id(d))
    for om in p.iter(qm('oMath')):
        if id(om) not in seen:
            deep += 1
    return units, deep


def wlen(el):
    return sum(len(t.text or '') for t in el.iter(q('t')))


def instances(tree):
    """全文档数学单元实例：[(canon, k_global, para_idx, k_local, para_text)]，按文档序。"""
    body = tree.find(q('body'))
    out = []
    nk = 0
    pidx = 0
    for p in body.iter(q('p')):
        txt = ptext(p)
        units, deep = math_units(p)
        off = 0
        pout = []
        for ch in p:
            wl = wlen(ch)
            if etree.QName(ch).namespace == M and etree.QName(ch).localname in ('oMath', 'oMathPara'):
                k_local = len(norm(txt[:off]))
                pout.append((etree.tostring(ch, encoding='unicode'), nk + k_local, pidx, k_local, txt))
            off += wl
        if deep:
            pout.append(('__DEEP__%d' % deep, None, pidx, None, txt))
        for inst in pout:
            out.append(inst)
        nk += len(norm(txt))
        pidx += 1
    return out


OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

grand_lost = 0
for sh, base in NAMES:
    dtree, _ = load(os.path.join(DONOR, base + '.docx.bak_标签行'))
    ctree, _ = load(os.path.join(CUR, base + '.docx'))
    D, C = instances(dtree), instances(ctree)
    dc_om = sum(1 for c, k, *_ in D if not c.startswith('__DEEP__'))
    cc_om = sum(1 for c, k, *_ in C if not c.startswith('__DEEP__'))
    deepD = [d for d in D if d[0].startswith('__DEEP__')]
    deepC = [c for c in C if c[0].startswith('__DEEP__')]
    # 全文归一文本守恒
    dtxt = ''.join(ptext(p) for p in dtree.find(q('body')).iter(q('p')))
    ctxt = ''.join(ptext(p) for p in ctree.find(q('body')).iter(q('p')))
    teq = norm(dtxt) == norm(ctxt)
    # k 匹配（按 canon 分组，组内按 k multiset 匹配）
    dcanon = Counter(c for c, k, *_ in D if not c.startswith('__DEEP__'))
    ccanon = Counter(c for c, k, *_ in C if not c.startswith('__DEEP__'))
    lost = []          # donor 未匹配实例
    only_cur = []      # cur 独有实例
    coll = []          # 同 k 异 canon 疑似
    from collections import defaultdict
    dk = defaultdict(list); ck = defaultdict(list)
    for c, k, pi, kl, txt in D:
        if c.startswith('__DEEP__'): continue
        dk[c].append(k)
    for c, k, pi, kl, txt in C:
        if c.startswith('__DEEP__'): continue
        ck[c].append(k)
    for c in dcanon:
        dd = sorted(dk[c]); cc = sorted(ck.get(c, []))
        cnt_d, cnt_c = Counter(dd), Counter(cc)
        for k, n in (cnt_d - cnt_c).items():
            lost += [(c, k)] * n
        for k, n in (cnt_c - cnt_d).items():
            only_cur += [(c, k)] * n
    # 同 k 异 canon 检查：donor 丢失实例的 k 上，cur 是否有别的 canon
    ck_by_k = defaultdict(set)
    for c, k, pi, kl, txt in C:
        if c.startswith('__DEEP__'): continue
        ck_by_k[k].add(hash(c) & 0xffffff)
    ncoll = sum(1 for c, k in lost if hash(c) & 0xffffff in ck_by_k.get(k, set()))
    ok_expect = (len(lost) == EXPECT_LOST[sh] and dc_om == EXPECT_PRE[sh] and cc_om == EXPECT_POST[sh])
    grand_lost += len(lost)
    say('## %s：donor om %d（期望 %d）｜cur om %d（期望 %d）｜k匹配丢失 %d（期望 %d）｜cur独有 %d｜深散 om D/C=%d/%d｜同k异canon碰撞 %d｜归一文本守恒 %s → %s'
        % (sh, dc_om, EXPECT_PRE[sh], cc_om, EXPECT_POST[sh], len(lost), EXPECT_LOST[sh], len(only_cur),
           sum(int(d[0][8:]) for d in deepD), sum(int(c[0][8:]) for c in deepC), ncoll, teq,
           'OK' if ok_expect and teq and not only_cur and not deepD and not deepC else '!!ATTENTION'))

say('')
say('=== 八件合计 k 匹配丢失元素 %d（期望 102） ===' % grand_lost)

# 衔接2 丢失实例明细 + 题号段样例
say('')
say('## 衔接2 丢失实例明细（插入点上下文）')
dtree, _ = load(os.path.join(DONOR, NAMES[3][1] + '.docx.bak_标签行'))
ctree, _ = load(os.path.join(CUR, NAMES[3][1] + '.docx'))
D, C = instances(dtree), instances(ctree)
from collections import defaultdict
dk = defaultdict(list); ck = defaultdict(list)
for c, k, pi, kl, txt in D:
    if not c.startswith('__DEEP__'): dk[c].append((k, pi, kl, txt))
for c, k, pi, kl, txt in C:
    if not c.startswith('__DEEP__'): ck[c].append((k, pi, kl, txt))
dparas = list(dtree.find(q('body')).iter(q('p')))
cparas = list(ctree.find(q('body')).iter(q('p')))
for c, dlist in dk.items():
    cnt_c = Counter(k for k, *_ in ck.get(c, []))
    used = set()
    for k, pi, kl, txt in sorted(dlist):
        if k in cnt_c and cnt_c[k] > 0:
            cnt_c[k] -= 1
            used.add(k)
            continue
        say('  丢失 k=%d donor段[p%d] %r' % (k, pi, txt[:70]))
        # cur 上下文：找 k 所在 cur 段
        nk = 0
        for cj, cp in enumerate(cparas):
            t2 = ptext(cp)
            n2 = len(norm(t2))
            if nk + n2 >= k:
                say('    cur[p%d] nk=%d k-nk=%d 段文 %r' % (cj, nk, k - nk, t2[:70]))
                for adj in (-1, 1):
                    if 0 <= cj + adj < len(cparas):
                        say('    cur[p%d%+d] %r' % (cj, adj, ptext(cparas[cj + adj])[:70]))
                break
            nk += n2

say('')
say('## 衔接2 题号段样例（前 12 段文本，donor）')
for i, p in enumerate(dparas[:12]):
    say('  [p%d] %r' % (i, ptext(p)[:60]))

out = os.path.join(BASE, '报告', '②F_01_探针.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('# ②F 探针 — 丢失集元素级重建预检（donor preT5 vs 现态 ②-C 终态）\n\n```text\n' + '\n'.join(OUT) + '\n```\n')
print('REPORT:', out, flush=True)
