# -*- coding: utf-8 -*-
"""M1盖章·自检⑥b（v2）：PyMuPDF逐页断言。v1教训：①页脚行内TNR数字run与CJK run的word bbox y0有微差，
  按y排序会把「页）」排到「第1页」后——改为按tag词定位页脚行、行内词按x0排序拼接；
  ②正文深页词y0也会>750——页脚行以含「·衔接/·清单/·讲练」tag词的y带为准。
断言：整串「件标识（共N页）第X页」（去空白）、X=件内物理页+start−1、行首x0≈43pt左对齐、
  第1页页码=1、跨卷衔接（C/F/G/H首页=79/48/99/135）。落盘 自检PDF输出.txt"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz

BASE = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(BASE, 'PDF')
JOBS = [  # (pdf名, tag, N, 本件start)
    ('P1_X1_p1-5.pdf', '第1章·衔接', 20, 1),
    ('P2_I1_p1-5.pdf', '第1章·清单', 20, 1),
    ('P3_B_p1-5.pdf', '第1章·讲练', 156, 1),
    ('P3_C_p1.pdf', '第1章·讲练', 156, 79),
    ('P4_X2_p1-4.pdf', '第2章·衔接', 4, 1),
    ('P5_I2_p1-5.pdf', '第2章·清单', 40, 1),
    ('P6_E_p1-5.pdf', '第2章·讲练', 197, 1),
    ('P6_F_p1.pdf', '第2章·讲练', 197, 48),
    ('P6_G_p1.pdf', '第2章·讲练', 197, 99),
    ('P6_H_p1.pdf', '第2章·讲练', 197, 135),
]


def footer_line(page, tag):
    """定位含tag的页脚行：找含tag关键段的word（页面下部），取与其y带重叠的全部词按x排序。"""
    words = page.get_text('words')
    key = tag.split('·')[-1]          # 衔接/清单/讲练
    anchors = [w for w in words if w[1] > 700 and key in w[4] and '·' + key in re.sub(r'\s', '', w[4])]
    if not anchors:
        # tag可能被切成多word：退而取页面上部70%以下、含tag章前缀的行
        anchors = [w for w in words if w[1] > 700 and tag.replace('·', '') in re.sub(r'\s|·', '', w[4])]
    if not anchors:
        # 最后兜底：页面上最靠下且x0≈左边距起始的「第X章」词
        anchors = [w for w in words if w[1] > 700 and re.match(r'^第[12]章·', re.sub(r'\s', '', w[4]))]
    assert anchors, '页脚tag词未定位到: %s' % tag
    a = anchors[0]
    ay0, ay1 = a[1], a[3]
    line = [w for w in words if w[3] > ay0 - 2 and w[1] < ay1 + 2]   # y带重叠
    line.sort(key=lambda w: w[0])
    return line


out = []
fail = 0
total = 0
for pdf, tag, N, start in JOBS:
    doc = fitz.open(os.path.join(PDFDIR, pdf))
    for i in range(doc.page_count):
        page = doc[i]
        phys = i + 1                       # 本件内物理页号（导出自主件第1页起）
        exp_num = start + phys - 1
        expect = '%s（共%d页）第%d页' % (tag, N, exp_num)
        line = footer_line(page, tag)
        compact = re.sub(r'\s+', '', ''.join(w[4] for w in line))
        x0 = line[0][0] if line else -1
        # 页脚行必须恰为期望串（允许页眉等无关行不混入——行带以tag锚定）
        ok = compact == expect
        left_ok = x0 < 60
        total += 1
        if not (ok and left_ok):
            fail += 1
        out.append('%s p%d 页脚=%r 预期=%r %s x0=%.1f %s'
                   % (pdf, phys, compact, expect, 'OK' if ok else 'FAIL',
                      x0, '左对齐OK' if left_ok else '左对齐FAIL'))
    doc.close()
out.append('PDF断言页数=%d FAIL=%d -> %s' % (total, fail, '全绿' if fail == 0 else '存在失败'))
open(os.path.join(BASE, '自检PDF输出.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
sys.exit(1 if fail else 0)
