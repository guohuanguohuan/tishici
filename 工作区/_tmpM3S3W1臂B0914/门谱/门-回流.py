# -*- coding: utf-8 -*-
r"""门-回流.py — M3 S3 W1 臂B 练习件（课时04＋05）·回流门（零强制跳页）＋件型纪律断言。
承母版 工作区/_tmpM3S3母版0914/门谱/门-回流.py 复刻：PIECE/MANIFEST 参数化；
件型读数按片头标槽型实录：04＝解答8（liubai 8：16/16/24/24/32/32/32/24 按小问数）＋kongda 2
（E4/E14 填空印答位）；05＝解答4（16/32/16/24）＋kongda 3（E11/E19/E20）；多选数＝manifest 期望值（两片均0）。
用法: python 门-回流.py 课时04|课时05    退出码: 0＝全过；1＝有红。
"""
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
PIECES = {
    '课时04': (ROOT + '/成卷/练习件/课时04-点斜式与斜截式',
               ROOT + '/成卷/题面库/manifest/课时04.manifest.json',
               8, ['16mm', '16mm', '24mm', '24mm', '32mm', '32mm', '32mm', '24mm'], 2),
    '课时05': (ROOT + '/成卷/练习件/课时05-两点式与一般式',
               ROOT + '/成卷/题面库/manifest/课时05.manifest.json',
               4, ['16mm', '32mm', '16mm', '24mm'], 3),
}
BAD = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
       '\\ketangboxed', '\\columnbreak', '\\eject', '\\vfill']

tag_sel = sys.argv[1] if len(sys.argv) > 1 else ''
if tag_sel not in PIECES:
    print('用法: python 门-回流.py 课时04|课时05'); sys.exit(2)
PIECE, MANIFEST, EXP_LIUBAI, EXP_LIUBAI_H, EXP_KONGDA = PIECES[tag_sel]

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

print(f'== {tag_sel} ==')
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

n_jieda = sum(1 for k in manifest['键序'] if k.startswith('2章-练-'))
n_liubai = len(re.findall(r'\\liubai(?![a-zA-Z])', body))
liubai_h = re.findall(r'\\liubai\[([0-9.]+mm)\]', body)
check(f'\\liubai 计数＝解答题数 {EXP_LIUBAI}（头标槽型实录）', n_liubai == EXP_LIUBAI, f'{n_liubai}')
check(f'\\liubai 逐题高度按小问数默认梯（16/24/32mm 带，cap 40mm 内；本片 {EXP_LIUBAI_H}）',
      liubai_h == EXP_LIUBAI_H, f'{liubai_h}')

n_kongda = len(re.findall(r'\\kongda(?![a-zA-Z])', body))
check(f'\\kongda 计数＝{EXP_KONGDA}（填空印答位）', n_kongda == EXP_KONGDA, f'{n_kongda}')

print()
print('回流门：', '全绿（零强制跳页＋件型纪律合规）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
