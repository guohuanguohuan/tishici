# -*- coding: utf-8 -*-
#
# 收编：2026-08-27 选必1整册任务·F2收尾（来源轮次：A4样张首创五杠杆 → C5参数化定稿；此为工具文件夹唯一常驻版，A4/C5桌面scripts副本不再维护）
#
# 用法: python 工具/短行合并候选与决策.py <unpack_dir> <qstart> <out_decisions.json> <out_review.txt>
# 功能: 对已解包docx生成杠杆⑤短行白名单合并候选与逐条决策清单（白名单断点=题间/题干/选项/标签块边界/图形段前后/标题导航行；区域内锚点=LAB/MARK段），人工复核后交 短行合并回退.py 调参与 紧凑化五杠杆改版.py --merge 执行

"""gen_decisions.py — 生成杠杆⑤短行合并候选与逐条决策清单（白名单外独占短行全列；F8/F9参数化）
用法: python gen_decisions.py <unpack_dir> <qstart> <out_json> <out_review_txt>
策略与样张完全一致：白名单断点＝题间/题干｜选项行｜【答案】标签合并行｜【分析】【详解】【点睛】块边界、
图形段前后、结构标题与导航表行；区域内锚点=LAB/MARK段；CONT并入当前锚点。
"""
import sys, io, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from 紧凑化公共库 import *

UNPACK = os.path.abspath(sys.argv[1])
QSTART = int(sys.argv[2])
OUT_JSON = os.path.abspath(sys.argv[3])
OUT_TXT = os.path.abspath(sys.argv[4])

tree, root, body = load(os.path.join(UNPACK, 'word', 'document.xml'))

REMARK_RE = re.compile(r'^(注意|提醒|补充|总结|说明|评注|思考|特点|推论|使用提醒|规律)')
ENTRY_NUM_RE = re.compile(r'^\d{1,3}[\.．]')
SECT_RE = re.compile(r'^\d+\.\d+(\.\d+)?(\s|$|（)')
qpat = re.compile(r'^(\d{1,3})．')

rows = []
exp = [QSTART]
for i, el in enumerate(body):
    tag = etree.QName(el).localname
    if tag == 'sectPr':
        continue
    if tag == 'tbl':
        rows.append((i, 'TABLE', ''))
        continue
    assert tag == 'p', tag
    p = el
    t = para_text(p)
    st = t.strip()
    if not st:
        kind = 'GRAPH' if has_object(p) else 'EMPTY'
        rows.append((i, kind, t)); continue
    m = qpat.match(st)
    if m and int(m.group(1)) == exp[0]:
        exp[0] += 1; rows.append((i, 'QHEAD', t)); continue
    if SECT_RE.match(st):
        rows.append((i, 'SECT', t)); continue
    if st.startswith('本节') or st.startswith('本卷') or st.startswith('全件'):
        rows.append((i, 'STAT', t)); continue
    if st.startswith('题型通式'):
        rows.append((i, 'NAVT', t)); continue
    if i == 0:
        rows.append((i, 'DOCTITLE', t)); continue
    if ENTRY_NUM_RE.match(st):
        rows.append((i, 'ENTRY', t)); continue
    if is_label_start(st):
        rows.append((i, 'LAB', t)); continue
    if is_marker_start(st):
        rows.append((i, 'MARK', t)); continue
    rows.append((i, 'CONT', t))

decisions = []
anchor = None
implicit_armed = False
zone = 'LECT'
for idx, kind, text in rows:
    if kind in ('SECT', 'STAT', 'TABLE', 'QHEAD', 'NAVT', 'DOCTITLE'):
        anchor = None; implicit_armed = False
        zone = 'STEM' if kind == 'QHEAD' else ('LECT' if kind in ('SECT', 'NAVT', 'DOCTITLE') else zone)
        continue
    if kind == 'EMPTY':
        continue
    if kind == 'GRAPH':
        anchor = None
        implicit_armed = (zone == 'ANS')
        continue
    if kind == 'LAB':
        if zone == 'STEM':
            zone = 'ANS'
        anchor = (idx, text); implicit_armed = False
        continue
    if kind == 'MARK':
        if zone == 'STEM':
            decisions.append({'key': 'm%d' % idx, '段索引': idx, 'kind': kind, 'zone': zone,
                              '原文摘要': text[:38], '决策': '保留', '理由': '题干/条件/小问区（白名单：题干与选项行不强制合并）'})
            continue
        anchor = (idx, text); implicit_armed = False
        continue
    if kind == 'ENTRY':
        anchor = None; implicit_armed = False
        decisions.append({'key': 'e%d' % idx, '段索引': idx, 'kind': kind, 'zone': zone,
                          '原文摘要': text[:38], '决策': '保留', '理由': '条目题名行（编号唯一层形，不与正文并排）——含讲部条目N．拒识保护'})
        continue
    # CONT
    if zone == 'STEM':
        decisions.append({'key': 's%d' % idx, '段索引': idx, 'kind': kind, 'zone': zone,
                          '原文摘要': text[:38], '决策': '保留', '理由': '题干区（白名单：题干/选项行保留换行）'})
        continue
    if anchor is None:
        if implicit_armed:
            anchor = (idx, text); implicit_armed = False
            decisions.append({'key': 'i%d' % idx, '段索引': idx, 'kind': kind, 'zone': zone,
                              '原文摘要': text[:38], '决策': '保留(隐式锚)', '理由': '图形/公式段后首行：作为隐式锚承接后续碎片，避免跨图重排'})
            continue
        decisions.append({'key': 'k%d' % idx, '段索引': idx, 'kind': kind, 'zone': zone,
                          '原文摘要': text[:38], '决策': '保留', '理由': '无可并锚点（图形/公式/表格/标题后孤行，保守保留）'})
        continue
    aidx, atext = anchor
    if atext.rstrip().endswith('：'):
        decisions.append({'key': 'r6_%d' % idx, '段索引': idx, 'kind': kind, 'zone': zone,
                          '原文摘要': text[:38], '并入段索引': aidx, '决策': '保留', '理由': 'R6锚点以全角冒号收尾（期待图形/表格内容），不吸并；本行改作新锚承接后续'})
        anchor = (idx, text); implicit_armed = False
        continue
    if REMARK_RE.match(text.strip()):
        decisions.append({'key': 'r5_%d' % idx, '段索引': idx, 'kind': kind, 'zone': zone,
                          '原文摘要': text[:38], '并入段索引': aidx, '决策': '保留', '理由': 'R5注释字头行（注意/补充/推论等），保留换行、自成新锚'})
        anchor = (idx, text)
        continue
    decisions.append({'key': 'g%d' % idx, '段索引': idx, 'kind': kind, 'zone': zone,
                      '原文摘要': text[:38], '并入段索引': aidx, '决策': '合并',
                      '理由': '白名单外独占短行（%s），并入前锚保序零增删' % ('锚后接续' if len(text) < 30 else '中长接续段')})

# br 清单（只列出供人工审；本两件勘测F9存量2处、F8为0，均不授权自动删）
br_items = []
for i, el in enumerate(body):
    if etree.QName(el).localname != 'p':
        continue
    for bi, br in enumerate(el.iter(qn('w:br'))):
        br_items.append({'段索引': i, 'br序': bi, '上下文': para_text(el)[:60],
                         '决策': '保留', '理由': '存量手动换行（讲部演示文本），零字符约束下保守保留'})

out = {'items': decisions, 'items_br': br_items}
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

from collections import Counter
c = Counter(d['决策'] for d in decisions)
print('决策统计:', dict(c))
with open(OUT_TXT, 'w', encoding='utf-8') as f:
    f.write('杠杆⑤短行合并逐条决策清单（%s起门控=%d）\n' % (UNPACK, QSTART))
    f.write('初判自动决策（尚未回退）；铁律=零字符增删，只动段落边界\n\n')
    for d in decisions:
        f.write('%-10s %-5s %-4s %-8s %s\n' % (d['key'], d['kind'], d['zone'], d['决策'], d['原文摘要']))
    for b in br_items:
        f.write('BR       段%d   存量br  保留   %s\n' % (b['段索引'], b['上下文']))
print('decisions.json / review written:', OUT_JSON)
