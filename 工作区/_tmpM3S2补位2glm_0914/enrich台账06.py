# -*- coding: utf-8 -*-
"""enrich台账06.py — 值台账-课时06.json items/指纹/门谱回填（写件＝值台账-课时06.json 本体）。"""
import io, json, hashlib, sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时06-两条直线的位置关系'
GATES = 'C:/提示词/工作区/_tmpM3S2补位2glm_0914/门谱'

led = json.load(open(PIECE + '/值台账-课时06.json', encoding='utf-8'))
draft = json.load(open(GATES + '/值台账底稿-06.json', encoding='utf-8'))
draft_items = draft['items'] if isinstance(draft, dict) else draft

def md5f(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

RULED = {'T14', 'T8', 'T10', 'G5'}
items = []
for it in draft_items:
    tag = it['键'].rsplit('-', 1)[-1]
    est = it.get('估高行数', 0)
    mo = '括线' if tag in RULED else '灰底'
    note = ('括线模（估高%d行＞8，上下 hairline 可跨栏断）' % est) if tag in RULED else \
           ('灰底；值行含 −U+2212 照直排' if '−' in (it.get('值tex') or '') else '灰底；逐字照录')
    items.append({'键': it['键'], '印面号': it['印面号'], '键型': it.get('键型', '值'),
                  '值tex': it.get('值tex'), '值源': it.get('值源'),
                  '值快照': '逐字全等' if it.get('值tex') == it.get('值源') else '漂！',
                  '估高行数': est, '判模': mo, '渲染注记': note,
                  '清洗注记': '逐字照录，零清洗' if tag not in ('T13', 'T16') else 'T13/T16 需选学提示行印面照录；T16 式段 ½·x_B 以数学模印出（字体缺字规避），在 main.tex 头注登记'})
led['items'] = items

def readout(log):
    import re
    t = open(PIECE + '/' + log, encoding='utf-8', errors='ignore').read()
    def c(p):
        return len(re.findall(p, t))
    return 'errors=%d missing=%d Overfull=%d Underfull=%d' % (c(r'^!'), c('Missing character'), c('Overfull'), c('Underfull'))

import fitz
d1 = fitz.open(PIECE + '/main-true.pdf')
d2 = fitz.open(PIECE + '/main-false.pdf')
led['指纹'] = {
    'main.tex.md5': md5f(PIECE + '/main.tex'),
    'main-true.pdf.md5': md5f(PIECE + '/main-true.pdf'),
    'main-false.pdf.md5': md5f(PIECE + '/main-false.pdf'),
    '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
    '双档读数': {
        'main-true': readout('main-true.log') + ' ANSKEY=21 %d页' % d1.page_count,
        'main-false': readout('main-false.log') + ' ANSKEY=21 %d页' % d2.page_count,
    },
}
json.dump(led, open(PIECE + '/值台账-课时06.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('台账 enrich 完成：items=%d' % len(items))
