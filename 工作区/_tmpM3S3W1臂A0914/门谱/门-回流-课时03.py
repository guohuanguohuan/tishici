# -*- coding: utf-8 -*-
r"""门-回流.py — M3 S3 W1臂A 课时03 练习件·回流门（零强制跳页）＋件型纪律断言。
（照抄母版门谱 工作区/_tmpM3S3母版0914/门谱/门-回流.py，PIECE/MANIFEST 常量换片；
逐片期望值：\duoxuan＝manifest 多选数 0（本片无多选）；\liubai＝解答题数 12
（E2~E11＋E14/E15，文件序 24mm×7＋16mm×5，逐题 16~40mm 带内）；\kongda＝4
（E1 双空两印答位＋E13＋E16 填空印答位）。）

断言面：main.tex 剔注释后：
  ①强制版面原子零出现：\newpage \clearpage \pagebreak \vbox \vtop \ketangboxed
    \columnbreak \eject \vfill。
  ②练习件件型纪律：\begin{ketang} ×0；\tailfill 恰 1（置 \end{multicols} 前）；
    \duoxuan 计数＝manifest 期望值多选数（本片 0，≤4 合规）；
    \liubai 计数＝片内解答题数 12 且逐题高度 16~40mm 带内
    （24mm×7＋16mm×5，文件序 E2~E11＋E14/E15）；
    \kongda 计数＝4（填空印答位，两档等形开关宏）。
用法: python 门-回流-课时03.py     退出码: 0＝全过；1＝有红。
"""
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时03-方向向量与法向量'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时03.manifest.json'
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
check('\\liubai 计数＝解答题数 12（E2~E11＋E14/E15，题面侧头标实录）', n_liubai == 12, f'{n_liubai}')
inband = all(16.0 <= float(h[:-2]) <= 40.0 for h in liubai_h)
check('\\liubai 逐题高度 16~40mm 带内（24mm×7＋16mm×5 文件序）',
      inband and liubai_h == ['24mm', '16mm', '24mm', '16mm', '24mm', '24mm',
                              '16mm', '24mm', '24mm', '16mm', '24mm', '16mm'],
      f'{liubai_h}')

n_kongda = len(re.findall(r'\\kongda(?![a-zA-Z])', body))
check('\\kongda 计数＝4（E1 双空＋E13＋E16 填空印答位）', n_kongda == 4, f'{n_kongda}')

print()
print('回流门：', '全绿（零强制跳页＋件型纪律合规）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
