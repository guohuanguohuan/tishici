# -*- coding: utf-8 -*-
"""②F_02_探针v2.py — 丢失集元素级重建（k 位配对版，不改写文件）。
实例＝段直接子级中含 m:oMath 后代的元素（stable 枚举）；k＝该元素前全局去空白 w:t 字符数。
配对：同 k 内按文档序逐一配对；donor 剩余＝丢失，cur 剩余＝cur独有。
内容指纹＝m: 命名空间子树标签序列＋m:t 文本（对 rPr 底纹漂移免疫）。
三层对照：donor(bak_标签行) / postT5(bak_底纹批) / cur(副本 ②-C 终态)。
落盘 → 报告/②F_02_探针v2.md"""
import sys, io, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
from collections import defaultdict

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
WS_RE = re.compile(r'[\s　\xa0​]+')
def norm(s): return WS_RE.sub('', s)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def wlen(el): return sum(len(t.text or '') for t in el.iter(q('t')))

BASE = os.path.dirname(os.path.abspath(__file__))
D_DIR = os.path.join(BASE, '副本_②B留档')
P_DIR = os.path.join(BASE, '副本_工具建设期留档')
C_DIR = os.path.join(BASE, '副本')
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
EXP_PRE = {'衔接1': 882, '上61': 3261, '下79': 2876, '衔接2': 243, '92': 2699, '90': 2914, '68': 2362, '89': 4039}
EXP_POST = {'衔接1': 876, '上61': 3254, '下79': 2856, '衔接2': 241, '92': 2680, '90': 2898, '68': 2348, '89': 4021}
EXP_LOST = {'衔接1': 6, '上61': 7, '下79': 20, '衔接2': 2, '92': 19, '90': 16, '68': 14, '89': 18}


def load(path):
    z = zipfile.ZipFile(path)
    tree = etree.fromstring(z.read('word/document.xml'))
    z.close()
    return tree


def instances(tree):
    """[(k, om_n, fp, para_idx, para_text)]，文档序；om_n＝该直接子级内 oMath 计数。"""
    body = tree.find(q('body'))
    out = []
    nk = 0
    for pi, p in enumerate(body.iter(q('p'))):
        txt = ptext(p)
        off = 0
        for ch in p:
            n_om = sum(1 for _ in ch.iter(qm('oMath')))
            if n_om:
                k_local = len(norm(txt[:off]))
                out.append((nk + k_local, n_om, fp(ch), pi, txt))
            off += wlen(ch)
        nk += len(norm(txt))
    return out


def fp(el):
    """数学内容指纹：m: 命名空间子树的标签序列＋m:t 文本拼接（无视 w: 格式属性）。"""
    parts = []
    for e in el.iter():
        ens = etree.QName(e).namespace
        ln = etree.QName(e).localname
        if ens == M:
            parts.append(ln)
            if ln == 't':
                parts.append(e.text or '')
    return '|'.join(parts)


def pair(D, C):
    """同 k 组内按序配对 → (lost, only, shd_or_fmt_diff, content_diff)。"""
    dk, ck = defaultdict(list), defaultdict(list)
    for inst in D:
        dk[inst[0]].append(inst)
    for inst in C:
        ck[inst[0]].append(inst)
    lost, only, fmt, cdiff = [], [], 0, 0
    for k in sorted(set(dk) | set(ck)):
        dd, cc = dk.get(k, []), ck.get(k, [])
        n = min(len(dd), len(cc))
        for i in range(n):
            if dd[i][2] != cc[i][2]:
                cdiff += 1
        lost += dd[n:]
        only += cc[n:]
    return lost, only, cdiff


OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

tot_t5 = 0
store = {}
for sh, base in NAMES:
    dt = load(os.path.join(D_DIR, base + '.docx.bak_标签行'))
    pt = load(os.path.join(P_DIR, base + '.docx.bak_底纹批'))
    ct = load(os.path.join(C_DIR, base + '.docx'))
    D, P, C = instances(dt), instances(pt), instances(ct)
    d_om = sum(p_i for p_i in (sum(1 for _ in p.iter(qm('oMath'))) for p in dt.find(q('body')).iter(q('p'))))
    p_om = sum(p_i for p_i in (sum(1 for _ in p.iter(qm('oMath'))) for p in pt.find(q('body')).iter(q('p'))))
    c_om = sum(p_i for p_i in (sum(1 for _ in p.iter(qm('oMath'))) for p in ct.find(q('body')).iter(q('p'))))
    ldp, lop, cdp = pair(D, P)     # donor→postT5：T5 纯边界
    lpc, loc, cpc = pair(P, C)     # postT5→cur：后续轮漂移
    ldc, loc2, cdc = pair(D, C)    # donor→cur：全跨度
    nT5 = sum(x[1] for x in ldp)
    tot_t5 += nT5
    store[sh] = (dt, ct, D, C, ldp, lpc)
    say('## %s：om总数 D=%d(期望%d) P=%d(期望%d) C=%d ｜D→P k丢失 %d元素/%d实例(期望丢%d)｜P→C 丢%d/独%d/内容异%d｜D→C 丢%d/独%d'
        % (sh, d_om, EXP_PRE[sh], p_om, EXP_POST[sh], c_om,
           nT5, len(ldp), EXP_LOST[sh],
           sum(x[1] for x in lpc), len(loc), cpc,
           sum(x[1] for x in ldc), len(loc2)))
    if lpc:
        for x in lpc[:6]:
            say('   P→C丢 k=%d n=%d 段%r' % (x[0], x[1], x[4][:50]))
    if loc:
        for x in loc[:6]:
            say('   P→C独 k=%d n=%d 段%r' % (x[0], x[1], x[4][:50]))

say('')
say('=== 八件 D→P（T5 纯边界）k 配对丢失合计 %d 元素（摘要口径 102） ===' % tot_t5)

# 衔接2 k=1775 区域细察（donor vs postT5 vs cur）
say('')
say('## 衔接2 三态对照（区域 k∈[1700,1850]）')
for tag_, tr in (('D', store['衔接2'][0]), ('C', store['衔接2'][1])):
    body = tr.find(q('body'))
    nk = 0
    for pi, p in enumerate(body.iter(q('p'))):
        txt = ptext(p)
        n0, n1 = nk, nk + len(norm(txt))
        n_om = sum(1 for _ in p.iter(qm('oMath')))
        if n1 >= 1700 and n0 <= 1850:
            # 逐子级 om 偏移
            det = []
            off = 0
            for ch in p:
                no = sum(1 for _ in ch.iter(qm('oMath')))
                if no:
                    det.append('om%d@k%d' % (no, n0 + len(norm(txt[:off]))))
                off += wlen(ch)
            say('  %s[p%d] k[%d,%d) om%d %s %r' % (tag_, pi, n0, n1, n_om, ' '.join(det), txt[:56]))
        nk = n1

out = os.path.join(BASE, '报告', '②F_02_探针v2.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('# ②F 探针 v2 — k 位配对元素级三态对照（donor preT5 / postT5 / cur ②-C 终态）\n\n```text\n' + '\n'.join(OUT) + '\n```\n')
print('REPORT:', out, flush=True)
