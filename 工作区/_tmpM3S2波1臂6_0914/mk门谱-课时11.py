# -*- coding: utf-8 -*-
"""mk门谱-课时11.py — 由 门谱-课时10 三门参数化复制为 门谱-课时11（常量换片＋NUM/多选换账）。
写域仅 工作区/_tmpM3S2波1臂6_0914/门谱-课时11/。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '门谱-课时10')
DST = os.path.join(os.path.dirname(SRC), '门谱-课时11')
os.makedirs(DST, exist_ok=True)

PIECE10 = r'课时10-2.4曲线与方程'
PIECE11 = r'课时11-2.5.1椭圆的标准方程'

NUM11 = ("NUM = {'简7': 1, '简8': 2, '简2': 3, '简3': 4, '简4': 5, '简1': 6,\n"
         "       '简9': 7, '简10': 8, '简5': 9, '简6': 10, '中1': 11, '中2': 12, '中3': 13,\n"
         "       '中4': 14, '难1': 15, '难2': 16,\n"
         "       'G1': 17, 'G2': 18, 'G3': 19, 'G4': 20, 'G5': 21}")

for fn in ('门-守恒对号.py', '门-值快照键型判模.py', '门-回流.py'):
    s = open(os.path.join(SRC, fn), encoding='utf-8').read()
    s = s.replace(PIECE10, PIECE11)
    s = s.replace('课时10.manifest.json', '课时11.manifest.json')
    s = s.replace('值台账底稿-课时10.json', '值台账底稿-课时11.json')
    s = s.replace('课时10', '课时11')
    if fn == '门-守恒对号.py':
        s = s.replace(
            "check('多选门：\\\\duoxuan＝0（本片多选 0 合规）', duox == 0, f'{duox}')",
            "check('多选门：\\\\duoxuan＝1（本片正文多选＝简6，≤4 合规）', duox == 1, f'{duox}')")
        s = s.replace('% 印面号 17—21', '% 印面号 17—21')
    if fn == '门-值快照键型判模.py':
        s = re.sub(r"# 印面号映射（装配序连号 1–21＝探究1—16＋评价17—21，见 main\.tex 头注；键尾段→号）\nNUM = \{[^}]+\}",
                   '# 印面号映射（装配序连号 1–21＝探究1—16＋评价17—21，见 main.tex 头注；键尾段→号）\n' + NUM11, s)
    open(os.path.join(DST, fn), 'w', encoding='utf-8').write(s)
    print(fn, '→', DST)
print('done')
