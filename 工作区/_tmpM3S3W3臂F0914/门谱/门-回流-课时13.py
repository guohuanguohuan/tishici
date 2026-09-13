# -*- coding: utf-8 -*-
r"""门-回流-课时13.py — M3 S3 W3臂F 课时13 练习件·回流门（零强制跳页）＋件型纪律断言。
（照抄臂F 课时12 门谱 门-回流-课时12.py，PIECE/MANIFEST 常量换片；
逐片期望值：\duoxuan＝manifest 多选数 0（§十一 0913 置换案：原中5席移拓展册13-拓5，随拓不计）；
\liubai＝解答题数 6（简1/简3/简4/简10/中1/难2，五问32mm×1＝简1＋三问32mm×1＝简3＋
四问32mm×1＝简4＋无编号小问16mm×2＝简10/中1＋两问24mm×1＝难2）；\kongda＝4（填空
简9/中2/中4/难1；解答槽题面尾空位 \kongbai 本片 0）。）
用法: python 门-回流-课时13.py     退出码: 0＝全过；1＝有红。
"""
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时13-2.6.1双曲线的标准方程'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时13.manifest.json'
BAD = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
       '\\ketangboxed', '\\columnbreak', '\\eject', '\\vfill']

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

for w in BAD:
    n = body.count(w)
    check(f'{w} ×0', n == 0, f'{n}')

n_ketang = body.count('\\begin{ketang}')
check('\\begin{ketang} ×0（练习件不设课堂评价）', n_ketang == 0, f'{n_ketang}')
n_tail = len(re.findall(r'\\tailfill(?![a-zA-Z])', body))
check('\\tailfill 恰1（尾块每件恰一处）', n_tail == 1, f'{n_tail}')

manifest = json.load(open(MANIFEST, encoding='utf-8'))
exp_duo = manifest['期望值']['多选数']
n_duo = len(re.findall(r'\\duoxuan(?![a-zA-Z])', body))
check(f'\\duoxuan 计数＝manifest 期望值多选数 {exp_duo}（≤4）', n_duo == exp_duo, f'{n_duo}')

n_liubai = len(re.findall(r'\\liubai(?![a-zA-Z])', body))
liubai_h = re.findall(r'\\liubai\[([0-9.]+mm)\]', body)
check('\\liubai 计数＝解答题数 6（题面侧头标实录：简1/简3/简4/简10/中1/难2）', n_liubai == 6, f'{n_liubai}')
inband = all(16.0 <= float(h[:-2]) <= 40.0 for h in liubai_h)
check('\\liubai 逐题高度 16~40mm 带内（32mm×3 多问＝简1五问/简3三问/简4四问＋16mm×2 无编号小问＝简10/中1＋24mm×1 两问＝难2）',
      inband and liubai_h == ['32mm', '32mm', '32mm', '16mm', '16mm', '24mm'], f'{liubai_h}')

n_kongda = len(re.findall(r'\\kongda(?![a-zA-Z])', body))
check('\\kongda 计数＝4（填空简9/中2/中4/难1；详解版印答、纯题版退定宽空线）', n_kongda == 4, f'{n_kongda}')

n_kongbai = len(re.findall(r'\\kongbai(?![a-zA-Z])', body))
check('\\kongbai 计数＝0（本片解答题面无尾空位）', n_kongbai == 0, f'{n_kongbai}')

print()
print('回流门：', '全绿（零强制跳页＋件型纪律合规）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
