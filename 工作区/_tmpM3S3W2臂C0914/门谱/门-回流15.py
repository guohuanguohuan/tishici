# -*- coding: utf-8 -*-
r"""门-回流15.py — M3 S3 课时15 练习件（W2 臂C）·回流门（零强制跳页）＋件型纪律断言。
照 门-回流.py（课时14 版）同制：改 PIECE/MANIFEST 指向课时15；
本片纪律读数：\duoxuan＝manifest 期望值多选数 0；\liubai＝9（解答9题），
高度表 16/16/24/16/16/16/16/24/16mm（出现序 题1,6,7,8,9,10,14,15,16；题7/15 两小问 24mm）；
\kongda＝5（题2/3/4/11/12 填空印答位，题12 双空拆两空）。

用法: python 门-回流15.py     退出码: 0＝全过；1＝有红。
"""
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时15-2.7.1抛物线方程'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时15.manifest.json'
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

n_jieda = sum(1 for k in manifest['键序'] if k.startswith('2章-练-') )
# 本片解答题数：16−单选2−填空5＝9（题面侧头标实录）
exp_liubai = 9
n_liubai = len(re.findall(r'\\liubai(?![a-zA-Z])', body))
liubai_h = re.findall(r'\\liubai\[([0-9.]+mm)\]', body)
check(f'\\liubai 计数＝解答题数 {exp_liubai}（题面侧头标实录；练键共{n_jieda}）', n_liubai == exp_liubai, f'{n_liubai}')
check('\\liubai 逐题高度＝16/16/24/16/16/16/16/24/16mm（出现序题1,6,7,8,9,10,14,15,16；题7/15 两小问24；16~40mm 带内）',
      liubai_h == ['16mm', '16mm', '24mm', '16mm', '16mm', '16mm', '16mm', '24mm', '16mm'], f'{liubai_h}')

n_kongda = len(re.findall(r'\\kongda(?![a-zA-Z])', body))
check('\\kongda 计数＝6（题2/3/4/11/12 共5空位题，题12 双空拆两空：5+1=6 处）', n_kongda == 6, f'{n_kongda}')

print()
print('回流门：', '全绿（零强制跳页＋件型纪律合规）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
