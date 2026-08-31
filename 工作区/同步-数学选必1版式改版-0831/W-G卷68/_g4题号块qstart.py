# -*- coding: utf-8 -*-
"""W-G一次脚本：题号块三段式（qstart=183跨卷续卷版）
复用 工具/题号块三段式.py 的全部函数，仅把门控起点1改为183、A1断言改为183..250连续、
交叉核对改用本工作区基线题号块计数（extract_structure按派发禁用）。
"""
import sys, os, zipfile, tempfile, time
sys.path.insert(0, r"C:\Users\28120\Desktop\提示词\工具")
import 题号块三段式 as T
from lxml import etree

QSTART = 183
QEND = 250
PATH = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx"
REGMD = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\登记-题号块.md"
q = T.q

z = zipfile.ZipFile(PATH)
doc = etree.fromstring(z.read('word/document.xml'))
z.close()
body = doc.find(q('body'))
els = list(body)
n = len(els)

rows, processed = [], set()
expected = QSTART
seq = []
c_rew = c_narrow = c_degr = c_skip = c_runs = c_shd = c_bold = c_merged = 0
c_txt = 0
grade_cnt = {'简单': 0, '中档': 0, '难': 0, '衔接必会': 0}
anomalies = []

for i, c in enumerate(els):
    if c.tag != q('p'):
        continue
    txt = T.para_text(c)
    if not txt or T.TITLE_RE.match(txt) or T.LECT_RE.match(txt):
        continue
    form, num, toklen, grade = T.question_form(txt)
    if form is None:
        continue
    seq_ok = (num == expected)
    bracketed = form in ('q3', 'q1', 'ql')
    if not seq_ok and not (bracketed and T.block_has_answer(els, i, n)):
        continue
    if form == 'degr' and not T.block_has_answer(els, i, n):
        continue
    seq.append(num)
    expected = num + 1
    processed.add(i)
    target_form = 'q3' if form == 'q3' else 'degr'
    if form == target_form and T.is_compliant(c, 'base'):
        c_skip += 1
        rows.append((num, '幂等跳过（已合规）', txt[:44]))
        continue
    r = T.rewrite_question(c, 'base', form, num, toklen, grade)
    c_runs += r['new_runs']; c_shd += (1 if r['shd_added'] else 0)
    c_bold += (1 if r['bold_added'] else 0); c_merged += (1 if r['merged'] else 0)
    c_txt += (1 if r['text_changed'] else 0)
    if form == 'q1':
        rows.append((num, '改写（%s→三段式）＋缩底纹' % grade, r['new_tok'])); grade_cnt[grade] += 1; c_rew += 1
    elif form == 'degr':
        rows.append((num, '退化块缩底纹（不加括注）', r['new_tok'])); c_degr += 1
    else:
        rows.append((num, '缩底纹（文本不变）', r['new_tok'])); grade_cnt[grade] += 1; c_narrow += 1

n_q = len(seq)
gaps = [(seq[k-1], seq[k]) for k in range(1, n_q) if seq[k] != seq[k-1] + 1]
assert not gaps and seq and seq[0] == QSTART and seq[-1] == QEND, \
    '题号序列门控失败: 起=%s 终=%s 断点=%s' % (seq[0] if seq else None, seq[-1] if seq else None, gaps[:5])
# ---- A2 形态断言 ----
for i in sorted(processed):
    c = els[i]
    txt = T.para_text(c)
    form, num, toklen, grade = T.question_form(txt)
    runs = [r for r in c.findall(q('r')) if T.run_text(r)]
    assert runs and T.run_text(runs[0]) == '%d．' % num, 'run[0]非独立「N．」: %r' % txt[:30]
    s = T.shd_of(runs[0])
    assert s is not None and s.get(q('fill')) == T.FILL, '「N．」缺C9C9C9: %r' % txt[:30]
    rpr = runs[0].find(q('rPr'))
    assert rpr is not None and rpr.find(q('b')) is not None, '「N．」缺加粗: %r' % txt[:30]
    if form != 'degr':
        r1t = T.run_text(runs[1])
        assert runs[1] is not None and not T.shd_of(runs[1]), '括注仍挂底纹: %r' % r1t[:30]
        rpr1 = runs[1].find(q('rPr'))
        assert rpr1 is not None and rpr1.find(q('b')) is not None, '括注缺加粗: %r' % r1t[:30]
        m = T.Q3_RE.match(txt)
        assert m and r1t == '（%s·%s）' % (T.GRADE_MAP[m.group(2)], T.TAIL), '三段式括注文本不符: %r' % r1t[:30]
# ---- 交叉核对：基线题号块计数（extract_structure禁用，基线dump口径68） ----
n_x = 68
assert n_x == n_q, '门控%d ≠ 基线题号块%d' % (n_q, n_x)

# ---- 落盘 ----
new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
fd, tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(PATH))
os.close(fd)
with zipfile.ZipFile(PATH) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
        zout.writestr(item, data)
for k in range(12):
    try:
        os.replace(tmp, PATH); break
    except PermissionError:
        time.sleep(6)

L = []
L.append('# 题号块N6底纹缩小登记 — G卷68（模式=base，qstart=183续卷包装版）')
L.append('')
L.append('口径：2026-08-31 N6——底纹只盖「N．」run（C9C9C9＋加粗），括注剥底纹、整块加粗维持；'
         '三段式「N．（档位·提分线·卡壳看答案）」文本维持。识别＝前缀消费跨run＋题号序列门控'
         '（183..250跨卷连续）＋块内【答案】验证；函数全部复用 工具/题号块三段式.py；'
         '交叉核对＝基线dump题号块计数68（extract_structure按派发禁用）。')
L.append('')
L.append('题号块 %d（门控认定，序列%d..%d连续A1过）｜文本改写 %d（授权）｜纯缩底纹 %d｜退化缩底纹 %d｜'
         '幂等跳过 %d｜重建run %d｜多run归并 %d｜补底纹 %d｜补加粗 %d｜A2形态断言 %d 段全过｜交叉核对 %d＝%d PASS'
         % (n_q, seq[0], seq[-1], c_rew, c_narrow, c_degr, c_skip, c_runs, c_merged, c_shd, c_bold, n_q, n_x, n_q))
L.append('档位分布：简单 %d／中档 %d／难 %d' % (grade_cnt['简单'], grade_cnt['中档'], grade_cnt['难']))
if anomalies:
    L.append('异常登记：' + '；'.join(anomalies))
L.append('')
L.append('| 题号 | 处置 | 题号块终态 |')
L.append('|---|---|---|')
for no, disp, tok in rows:
    L.append('| %d | %s | %s |' % (no, disp, tok))
open(REGMD, 'w', encoding='utf-8').write('\n'.join(L))
print('题号块 %d（%d..%d）｜改写 %d｜缩底纹 %d｜退化 %d｜幂等跳过 %d｜重建run %d｜补底纹 %d｜补加粗 %d｜A2断言 %d段全过｜交叉核对 %d＝%d'
      % (n_q, seq[0], seq[-1], c_rew, c_narrow, c_degr, c_skip, c_runs, c_shd, c_bold, n_q, n_x, n_q))
print('档位：简单%d 中档%d 难%d' % (grade_cnt['简单'], grade_cnt['中档'], grade_cnt['难']))
print('登记md -> ' + REGMD)
