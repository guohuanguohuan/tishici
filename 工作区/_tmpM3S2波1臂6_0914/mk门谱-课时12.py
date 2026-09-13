# -*- coding: utf-8 -*-
"""mk门谱-课时12.py — 由 门谱-课时11 三门参数化复制为 门谱-课时12（常量换片＋NUM/多选换账）。
写域仅 工作区/_tmpM3S2波1臂6_0914/门谱-课时12/。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '门谱-课时11')
DST = os.path.join(os.path.dirname(SRC), '门谱-课时12')
os.makedirs(DST, exist_ok=True)

PIECE11 = r'课时11-2.5.1椭圆的标准方程'
PIECE12 = r'课时12-2.5.2椭圆的几何性质'

NUM12 = ("NUM = {'简1': 1, '简2': 2, '简3': 3, '简4': 4, '简5': 5, '简6': 6,\n"
         "       '简7': 7, '简8': 8, '简9': 9, '简10': 10, '中1': 11, '中2': 12, '中3': 13,\n"
         "       '中4': 14, '难1': 15, '难2': 16,\n"
         "       'G1': 17, 'G2': 18, 'G3': 19, 'G4': 20, 'G5': 21}")

for fn in ('门-守恒对号.py', '门-值快照键型判模.py', '门-回流.py'):
    s = open(os.path.join(SRC, fn), encoding='utf-8').read()
    s = s.replace(PIECE11, PIECE12)
    s = s.replace('课时11.manifest.json', '课时12.manifest.json')
    s = s.replace('值台账底稿-课时11.json', '值台账底稿-课时12.json')
    s = s.replace('课时11', '课时12')
    if fn == '门-守恒对号.py':
        s = s.replace(
            "check('多选门：\\\\duoxuan＝1（本片正文多选＝简6，≤4 合规）', duox == 1, f'{duox}')",
            "check('多选门：\\\\duoxuan＝1（本片正文多选＝难2，≤4 合规）', duox == 1, f'{duox}')")
    if fn == '门-值快照键型判模.py':
        s = re.sub(r"# 印面号映射（装配序连号 1–21＝探究1—16＋评价17—21，见 main\.tex 头注；键尾段→号）\nNUM = \{[^}]+\}",
                   '# 印面号映射（装配序连号 1–21＝探究1—16＋评价17—21，见 main.tex 头注；键尾段→号）\n' + NUM12, s)
    open(os.path.join(DST, fn), 'w', encoding='utf-8').write(s)
    print(fn, '→', DST)
print('done')
