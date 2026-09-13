# -*- coding: utf-8 -*-
r"""_qinsuan_dump.py — P2 亲算预备：微专题 50~58 讲全块转储（题面＋答案＋解析），供逐块亲算交叉验算。

源件只读（python-docx 对象读，经 工具/dump_docx.py body_elements）；落盘仅本目录。
块口径承 轮1 _p2_extract.py：N．段起＝块界；有【答案】/【解析】＝真题。
"""
import sys, os
WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(WS, '..', '..', '工具'))
from dump_docx import body_elements

WZT = os.path.join(WS, '..', '..', '高中物理', '参考', '组卷网',
                   '备战高考·107微专题模型精讲精练', '8静电场')
WZT_FILES = {
    50: '第50讲电场中的图像-2023届高三物理高考复习101微专题模型精讲精练.docx',
    51: '第51讲匀强电场中的场强、电势、电势能的定性分析与定量计算-2023届高三物理高考复习101微专题.docx',
    52: '第52讲非匀强电场中的场强、电势、电势能的定性分析与定量计算-2023届高三物理高考复习101微专.docx',
    53: '第53讲单体或多体在电场中的运动之力、电综合问题-2023届高三物理高考复习101微专题模型精讲精.docx',
    54: '第54讲电容器的充电与放电实验-2023届高三物理高考复习101微专题模型精讲精练.docx',
    55: '第55讲电容器的动态分析-2023届高三物理高考复习101微专题模型精讲精练.docx',
    56: '第56讲带电粒子在电场中的直线运动-2023届高三物理高考复习101微专题模型精讲精练.docx',
    57: '第57讲带电粒子在电场中的曲线运动-2023届高三物理高考复习101微专题模型精讲精练.docx',
    58: '第58讲带电粒子在交变电场中的运动-2023届高三物理高考复习101微专题模型精讲精练.docx',
}
QSTART = re_start = __import__('re').compile(r'^(\d{1,3})．')

for lec, fn in sorted(WZT_FILES.items()):
    els = body_elements(os.path.join(WZT, fn))
    lines = [(tg, t) for tg, t in [(tg, t) for i, tg, t in els] if t is not None and tg == 'p']
    lines = [t for tg, t in lines]
    starts = [k for k, t in enumerate(lines) if t.strip() and QSTART.match(t.strip())]
    out = []
    for k_i, k in enumerate(starts):
        no = int(QSTART.match(lines[k].strip()).group(1))
        end = starts[k_i + 1] if k_i + 1 < len(starts) else len(lines)
        block = '\n'.join(t for t in lines[k:end] if t.strip())
        is_ti = '【答案】' in block or '【解析】' in block
        out.append((len(out) + 1, no, is_ti, block))
    fn_out = os.path.join(WS, 'dump-讲%d.md' % lec)
    with open(fn_out, 'w', encoding='utf-8') as f:
        f.write('# 讲%d 全块转储（亲算验算参照；块数=%d 真题=%d）\n' % (
            lec, len(out), sum(1 for _, _, ti, _ in out if ti)))
        for blk, no, ti, text in out:
            f.write('\n===[讲%d-%d|%s]===\n%s\n' % (lec, blk, '真题' if ti else '讲料', text))
    print('讲%d 块=%d 真题=%d -> %s' % (lec, len(out),
          sum(1 for _, _, ti, _ in out if ti), os.path.basename(fn_out)))
print('完毕')
