# -*- coding: utf-8 -*-
"""标点专项：行内标点识别（底部小墨块）→ 占宽/前后空档/挤压证据。
可对参考 PNG 或我方渲染 PNG 运行。"""
import numpy as np, sys, json
import ref_tools as R

PXMM = 14.176

def punct_scan(path, x0, x1, y0, y1, tag, thr=170, max_h_ratio=0.45):
    gray = R.load_gray(path)
    ik = R.ink(gray, thr)
    lines = [(a, b) for a, b in R.find_lines(ik, x0, x1) if b > y0 and a < y1]
    out = []
    for (a, b) in lines:
        segs = R.segment_chars(ik, a, b, x0, x1)
        if len(segs) < 3:
            continue
        hts = [s[3] - s[2] for s in segs]
        medh = float(np.median(hts))
        # 行内相对坐标 → 页面坐标
        segs = [(s[0] + x0, s[1] + x0, s[2], s[3]) for s in segs]
        pitches = [segs[i + 1][0] + segs[i + 1][1] - segs[i][0] - segs[i][1] for i in range(len(segs) - 1)]
        for i, s in enumerate(segs):
            h = s[3] - s[2]; w = s[1] - s[0]
            # 标点：墨高明显矮（底部）或细高（冒号/分号）
            bottom = s[3]
            line_bottom = max(x[3] for x in segs)
            is_p = (h < max_h_ratio * medh) or (w < 0.35 * medh and h < 0.7 * medh)
            if not is_p:
                continue
            rec = dict(line=(int(a), int(b)), i=i, w=int(w), h=int(h),
                       x=(int(s[0]), int(s[1])), bottom_gap=int(line_bottom - bottom),
                       medh=round(medh, 1))
            if i > 0:
                rec['gap_before'] = int(s[0] - segs[i - 1][1])
                rec['pitch_before'] = round(pitches[i - 1], 1)
                rec['prev_w'] = int(segs[i - 1][1] - segs[i - 1][0])
            if i < len(segs) - 1:
                rec['gap_after'] = int(segs[i + 1][0] - s[1])
                rec['pitch_after'] = round(pitches[i], 1)
                rec['next_w'] = int(segs[i + 1][1] - segs[i + 1][0])
            out.append(rec)
    print(f'== {tag}: 标点候选 {len(out)} 个（行 {len(lines)}）==')
    for r in out[:40]:
        print('  ', r)
    return out

def pitch_hist(path, x0, x1, y0, y1, tag, thr=170):
    gray = R.load_gray(path)
    ik = R.ink(gray, thr)
    lines = [(a, b) for a, b in R.find_lines(ik, x0, x1) if b > y0 and a < y1]
    allp = []
    perline = []
    for (a, b) in lines:
        segs = R.segment_chars(ik, a, b, x0, x1)
        if len(segs) < 5:
            continue
        cts = [(s[0] + s[1]) / 2 for s in segs]
        ws = [s[1] - s[0] for s in segs]
        medw = np.median(ws)
        ps = [cts[i + 1] - cts[i] for i in range(len(cts) - 1)
              if ws[i] > 0.75 * medw and ws[i + 1] > 0.75 * medw]
        if ps:
            perline.append((a, len(segs), round(float(np.median(ps)), 1), round(float(np.std(ps)), 2)))
            allp += ps
    allp = np.array(allp)
    print(f'== {tag}: 全角字心距 n={len(allp)} ==')
    for q in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        print(f'  p{q}: {np.percentile(allp,q):.1f}px = {np.percentile(allp,q)/PXMM:.3f}mm')
    print('  行内 pitch 中位/标准差（前25行）:')
    for r in perline[:25]:
        print('   ', r)
    return allp, perline

if __name__ == '__main__':
    p = r'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p05.png'
    # 纯文字段（前 800px 附近为知识点四/五正文）
    punct_scan(p, 243, 1433, 1200, 2600, 'ref-p05-L-正文段')
