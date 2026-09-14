# -*- coding: utf-8 -*-
"""压缩 05 片探究点三/四 的 ③收束（自撰行）以消 p3 左栏 Overfull \\vbox。
用法: python 压05小结.py <on|off>
"""
import io
import sys

BS, LF = chr(92), chr(10)
P = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时05-两点式与一般式/main.tex'
LONG3 = BS + 'bindp {' + BS + 'kaishu ③收束：截距式丢过原点与平行于轴的直线，须补检验；源卷结果与题面数据互斥时按“源错必改”回代双向验证并留注记.}'
SHORT3 = BS + 'bindp {' + BS + 'kaishu ③收束：截距式丢过原点与平行于轴的直线，须补检验；源卷结果与题面互斥时按“源错必改”回代验．}'
LONG4 = BS + 'bindp {' + BS + 'kaishu ③收束：包络型问题须辨“过定点”与“与定圆相切”两类直线系，二者命题结论完全不同；多解情形（内切、外切两型）逐一取面积，勿漏第二值.}'
SHORT4 = BS + 'bindp {' + BS + 'kaishu ③收束：包络型须辨“过定点”与“与定圆相切”两类直线系，结论完全不同；多解（内切、外切）逐一取面积，勿漏第二值.}'

mode = sys.argv[1] if len(sys.argv) > 1 else 'on'
lines = io.open(P, encoding='utf-8', newline='').read().split(LF)
n = 0
for i, l in enumerate(lines):
    if mode == 'on' and l == LONG3:
        lines[i] = SHORT3; n += 1
    elif mode == 'on' and l == LONG4:
        lines[i] = SHORT4; n += 1
    elif mode == 'off' and l == SHORT3:
        lines[i] = LONG3; n += 1
    elif mode == 'off' and l == SHORT4:
        lines[i] = LONG4; n += 1
assert n == 2, f'命中 {n} 处（应为2），mode={mode}'
io.open(P, 'w', encoding='utf-8', newline='').write(LF.join(lines))
print(f'{mode} 压缩 {n} 行完成')
