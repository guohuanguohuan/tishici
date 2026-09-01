# -*- coding: utf-8 -*-
# 一次性人工对照抽验（任务测试①：抽两类各10处，独立lxml清点，不用工具代码路径）：
#   A类＝题号难度块（B讲练件，10处）：题号段首连续灰底run串接应恰为「N．」且加粗；
#   B类＝条目第一子层（I1清单件，10处，含修复的3处179/186/189）：lead灰底串接应匹配（N）（可带芯片）且不加粗；
#   附加＝⑦解析块边界人工过目（变体_全量，题块5整段逐段列出清点∈?/浅底∈?）。
import zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

def load(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    return list(doc.find(q('body')))

def shd_fill(rpr):
    s = rpr.find(q('shd')) if rpr is not None else None
    return s.get(q('fill')) if s is not None else None

def eff_bold(r):
    rpr = r.find(q('rPr'))
    if rpr is not None:
        b = rpr.find(q('b'))
        if b is not None:
            return b.get(q('val')) not in ('0', 'false', 'off', 'none')
    return False   # 无显式b且无样式链解析时按False（抽验B类另有样式链另查）

def lead_info(p, fill):
    txt = ''; runs = []
    for r in p.iter(q('r')):
        t = ''.join(x.text or '' for x in r.findall(q('t')))
        if t == '':
            continue
        if shd_fill(r.find(q('rPr'))) == fill:
            txt += t; runs.append(r)
        else:
            break
    return txt, runs

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

print('===== A类：B讲练件 题号难度块 10处（灰底C9C9C9 lead 应恰为 N． 且加粗）=====')
els = load(r'副本\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx')
QB = re.compile(r'^\d+．（')
picks = [i for i, el in enumerate(els) if el.tag == q('p') and QB.match(ptext(el))]
step = max(1, len(picks) // 10)
for i in [picks[k * step] for k in range(10)]:
    txt, runs = lead_info(els[i], 'C9C9C9')
    bold = all(eff_bold(r) for r in runs) if runs else False
    ok = (re.fullmatch(r'\d+．', txt) is not None) and bold
    print('body[%d] lead=%r bold=%s -> %s | 段首: %s' % (i, txt, bold, 'OK' if ok else 'FAIL', ptext(els[i])[:28]))

print()
print('===== B类：I1清单件 条目第一子层 10处（含修复3处179/186/189）=====')
els = load(r'副本\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx')
targets = [179, 186, 189]      # 修复涉及的三处
subs = [i for i, el in enumerate(els)
        if el.tag == q('p') and re.match(r'^（\d+）', ptext(el)) and i not in targets]
step = max(1, len(subs) // 7)
targets += [subs[k * step] for k in range(7)]
for i in sorted(targets):
    txt, runs = lead_info(els[i], 'C9C9C9')
    bold = any(eff_bold(r) for r in runs) if runs else False
    ok = (re.fullmatch(r'（\d+）(?:【[^】]{1,16}】)*', txt) is not None) and not bold and bool(runs)
    print('body[%d] lead=%r 灰底run数=%d bold违规=%s -> %s | 段首: %s'
          % (i, txt, len(runs), bold, 'OK' if ok else 'FAIL', ptext(els[i])[:30]))

print()
print('===== 附加：⑦解析块边界人工过目（变体_挂浅底全量，题块5前后逐段）=====')
els = load(r'副本\变体_挂浅底全量.docx')
QB2 = re.compile(r'^\d+．（')
qstarts = [i for i, el in enumerate(els) if el.tag == q('p') and QB2.match(ptext(el))]
s5 = qstarts[4]; s6 = qstarts[5]
def para_fill(p):
    ppr = p.find(q('pPr'))
    if ppr is not None:
        s = ppr.find(q('shd'))
        if s is not None:
            return s.get(q('fill'))
    return None
print('（题块5 = body[%d] 起，至下一题块 body[%d] 前）' % (s5, s6))
for i in range(s5 - 2, s6 + 2):
    el = els[i]
    if el.tag != q('p'):
        print('body[%d] <非段落元素>' % i); continue
    f = para_fill(el)
    t = ptext(el)
    print('body[%d] 浅底=%s | %s' % (i, f if f else '白', t[:44]))
