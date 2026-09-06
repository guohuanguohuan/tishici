# -*- coding: utf-8 -*-
"""⑧轮债1探针：逐腿定位 extract_structure 题量提取=0 的地面真相（只读）。
腿1：题号头三族形态普查（括注形/〔条目形/裸形），WJ 归一前后计数对照。
腿2：X2 全件 kind 序列 + 题目区/详解区块结构（题号头到标签行的间隔内容）。
腿3：B 首题区 + 详解区 题头形态。
腿4：SM 图例演示段题号头形态。
"""
import sys, io, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:/提示词/工具')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
WJ = '\u2060'

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def paras(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    return [(i, el, ptext(el)) for i, el in enumerate(list(body)) if el.tag == q('p')]

def vis(s):
    return s.replace(WJ, '⟨WJ⟩')

BASE = r'C:/提示词/高中数学/高中数学同步'
FILES = {
    'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C':  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F':  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G':  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H':  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    'SM': '人教B版选必1·使用说明.docx',
    'TOC': '人教B版选必1·册目录页.docx',
}

QSTART_RAW = re.compile(r'^(?:\d+(?:\.\d+)+-\d+|\d+)．')
# 括注形：档位（简单/中档/难）与衔接必会，兼容 legacy ·卡壳看答案 后缀
KUOHAO = re.compile(r'^(\d+(?:\.\d+)+-\d+|\d+)．（((?:简单|中档|难)(?:·(?:保60%|保80%|冲100%))?(?:·卡壳看答案)?|衔接必会(?:·卡壳看答案)?)）')
LEGACY_OLD = re.compile(r'^(\d+(?:\.\d+)+-\d+|\d+)．（(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%)·卡壳看答案)?）$')
TIAOMU = re.compile(r'^(\d+(?:\.\d+)+-\d+|\d+)．〔')

print('==== 腿1：题号头形态普查（每件：WJ归一后） ====')
for code, fn in FILES.items():
    ps = paras(os.path.join(BASE, fn))
    n_qstart = sum(1 for _, _, t in ps if QSTART_RAW.match(t.replace(WJ, '')))
    n_kuo = sum(1 for _, _, t in ps if KUOHAO.match(t.replace(WJ, '')))
    n_tiao = sum(1 for _, _, t in ps if TIAOMU.match(t.replace(WJ, '')))
    n_wj_head = sum(1 for _, _, t in ps if WJ in t and QSTART_RAW.match(t))
    # 样本
    kuo_samples, tiao_samples = [], []
    for _, _, t in ps:
        tn = t.replace(WJ, '')
        if KUOHAO.match(tn) and len(kuo_samples) < 2:
            kuo_samples.append(vis(t)[:60])
        if TIAOMU.match(tn) and len(tiao_samples) < 2:
            tiao_samples.append(vis(t)[:60])
    print('%-3s qstart裸匹配=%-4d 括注形=%-4d 条目〔形=%-3d 含WJ且qstart可匹配=%d' %
          (code, n_qstart, n_kuo, n_tiao, n_wj_head))
    print('    括注样本: %s' % (kuo_samples if kuo_samples else '无'))
    print('    条目样本: %s' % (tiao_samples if tiao_samples else '无'))

print()
print('==== 腿2：X2 kind/块结构（题号头→标签行间隔逐段列出，前2题+末题） ====')
ps = paras(os.path.join(BASE, FILES['X2']))
# 题号头（归一后）body 序号
heads = [i for i, _, t in ps if QSTART_RAW.match(t.replace(WJ, ''))]
ans_lines = [i for i, _, t in ps if t.replace(WJ, '').startswith('【答案】')]
print('X2 题号头 body序号: %s' % heads)
print('X2 【答案】行 body序号: %s' % ans_lines)
# 前两题全量段落
def dump_range(ps, a, b, title):
    print('--- %s（body %d..%d） ---' % (title, a, b))
    for i, el, t in ps:
        if a <= i <= b:
            print('  [%d] %s' % (i, vis(t)[:90]))
if len(heads) >= 2:
    dump_range(ps, heads[0], min(heads[1], ans_lines[0] if ans_lines else heads[1]) + 2, 'X2 第1题区至第2题号头后2段')
if ans_lines:
    dump_range(ps, ans_lines[0] - 2, ans_lines[0] + 6, 'X2 首个【答案】行前后')
    dump_range(ps, ans_lines[-1] - 3, ans_lines[-1] + 4, 'X2 末个【答案】行前后')

print()
print('==== 腿3：B 首题号头前后 + 详解区定位 ====')
ps = paras(os.path.join(BASE, FILES['B']))
heads = [i for i, _, t in ps if QSTART_RAW.match(t.replace(WJ, ''))]
ans_lines = [i for i, _, t in ps if t.replace(WJ, '').startswith('【答案】')]
print('B 题号头数=%d 首=%s 末=%s' % (len(heads), heads[:5], heads[-3:]))
print('B 【答案】行数=%d 首=%s 末=%s' % (len(ans_lines), ans_lines[:5], ans_lines[-3:]))
if heads and ans_lines:
    dump_range(ps, heads[0] - 1, heads[0] + 4, 'B 第1题号头前后')
    a0 = ans_lines[0]
    dump_range(ps, a0 - 6, a0 + 4, 'B 首个【答案】行前后6段')
# B 的【答案】行前后是否有题号头（详解区是否重复题号头）
print('B 每个【答案】行向前3段内是否出现题号头：')
cnt = 0
for a in ans_lines[:8]:
    win = [t.replace(WJ, '') for i, _, t in ps if a - 3 <= i < a]
    has = any(QSTART_RAW.match(w) for w in win)
    cnt += has
    print('  ans@%d 前3段=%s 命中题号头=%s' % (a, [vis(w)[:28] for w in win], has))
print('  （前8个中命中 %d）' % cnt)

print()
print('==== 腿4：SM 图例演示段题号头形态 ====')
ps = paras(os.path.join(BASE, FILES['SM']))
for i, el, t in ps:
    tn = t.replace(WJ, '')
    if QSTART_RAW.match(tn) or '【答案】' in tn:
        print('  [%d] %s' % (i, vis(t)[:80]))
