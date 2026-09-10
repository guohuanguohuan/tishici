# -*- coding: utf-8 -*-
r"""片H1 · 全品靶复测（p04–p07，14.176 px/mm 同尺口径）
输出：E7 版面几何（墨缘/栏宽/栏距/行距/首行墨顶）＋E1 字心距/每行字数
＋E2 标点前后墨空档/advance 反解＋②条目号后隙（'.'→内容首字 ink）。
只读参考图；结果 JSON 落 片H1/。"""
import json
import numpy as np
from PIL import Image
from scipy import ndimage

PXMM = 14.176
REF = r'C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/%s.png'


def load_gray(p):
    return np.asarray(Image.open(p).convert('L')).astype(np.uint8)


def ink(gray, thr=170):
    return gray < thr


def find_lines(ik, x0, x1, min_ink=3, min_h=8):
    sub = ik[:, x0:x1]
    row = sub.sum(axis=1)
    on = row > min_ink
    runs = []
    s = None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            runs.append((s, i))
            s = None
    if s is not None:
        runs.append((s, len(on)))
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= 4:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(list(r))
    return [(a, b) for a, b in merged if b - a >= min_h]


def segment_chars(ik, y0, y1, x0, x1, min_w=4):
    sub = ik[y0:y1, x0:x1]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    if n == 0:
        return []
    objs = ndimage.find_objects(lab)
    comps = []
    for sl in objs:
        ys, xs = sl
        comps.append((xs.start, xs.stop, ys.start + y0, ys.stop + y0))
    comps.sort()
    groups = []
    for c in comps:
        placed = False
        for g in groups:
            if not (c[1] + 1 < g[0] or c[0] - 1 > g[1]):
                g[0] = min(g[0], c[0]); g[1] = max(g[1], c[1])
                g[2] = min(g[2], c[2]); g[3] = max(g[3], c[3])
                placed = True
                break
        if not placed:
            groups.append([c[0], c[1], c[2], c[3]])
    changed = True
    while changed:
        changed = False
        out = []
        for g in sorted(groups):
            if out and not (g[0] > out[-1][1] + 1):
                out[-1][0] = min(out[-1][0], g[0]); out[-1][1] = max(out[-1][1], g[1])
                out[-1][2] = min(out[-1][2], g[2]); out[-1][3] = max(out[-1][3], g[3])
                changed = True
            else:
                out.append(g)
        groups = out
    return [g for g in groups if g[1] - g[0] >= min_w]


def line_extent(ik, y0, y1, xlo=0, xhi=None):
    sub = ik[y0:y1, :]
    col = sub.sum(axis=0)
    on = np.where(col > 0)[0]
    if len(on) == 0:
        return None
    return int(on[0]), int(on[-1] + 1)


def column_projection(ik, ytop, ybot):
    sub = ik[ytop:ybot, :]
    col = sub.sum(axis=0)
    return col


# ---------- E7：版面几何 ----------
def e7_geometry(pages=('p04', 'p05', 'p06', 'p07')):
    out = {}
    for tag in pages:
        gray = load_gray(REF % tag)
        ik = ink(gray)
        H, W = ik.shape
        # 通体墨缘（排除页脚页码块区 y>3950？下方 4000 处有页码块，全品出血到纸边——采正文带 y∈[150, 3900]）
        body = ik[150:3900, :]
        cols = body.sum(axis=0)
        on = np.where(cols > 0)[0]
        x_lo, x_hi = int(on[0]), int(on[-1] + 1)
        # 栏分离：找中缝（cols 为 0 的区带，位于页面中部）
        mid_zone = cols[1300:1700]
        zero = np.where(mid_zone == 0)[0]
        if len(zero):
            # 中缝 = 1300..1700 中最长零段
            runs = []
            s = None
            for i, v in enumerate(mid_zone):
                if v == 0 and s is None:
                    s = i
                elif v != 0 and s is not None:
                    runs.append((s, i)); s = None
            if s is not None:
                runs.append((s, len(mid_zone)))
            gaps = [(a, b) for a, b in runs if b - a < 60]
            lg = max(runs, key=lambda r: r[1] - r[0]) if runs else (0, 0)
            gap_c = (1300 + lg[0], 1300 + lg[1])
        else:
            gap_c = None
        # 左栏 ink 右缘：cols 在 gap 左侧最后一个非零；右栏 ink 左缘
        if gap_c:
            gl, gr = gap_c
            left_on = np.where(cols[:gl] > 0)[0]
            right_on = np.where(cols[gr:] > 0)[0]
            left_span = (int(left_on[0]), int(left_on[-1] + 1)) if len(left_on) else None
            right_span = (int(right_on[0] + gr), int(right_on[-1] + 1 + gr)) if len(right_on) else None
        else:
            left_span = right_span = None
        # 行距与首行墨顶：左栏行 band
        lx0 = left_span[0] - 5 if left_span else 243
        lx1 = left_span[1] + 5 if left_span else 1433
        lines = find_lines(ik, lx0, lx1)
        # 正文行（滤掉花形/表格噪声：行高 < 60px）
        text_lines = [(a, b) for a, b in lines if (b - a) < 60]
        ycs = [(a + b) / 2 for a, b in text_lines]
        diffs = [b - a for a, b in zip(ycs, ycs[1:]) if 60 < b - a < 140]
        from collections import Counter
        pitch_mode = Counter([round(d) for d in diffs]).most_common(6)
        out[tag] = dict(
            page=tag, x_ink=(x_lo, x_hi),
            x_ink_mm=(round(x_lo / PXMM, 2), round((W - x_hi) / PXMM, 2)),
            gap_center_px=gap_c,
            left_span=left_span, left_w_mm=round((left_span[1] - left_span[0]) / PXMM, 2) if left_span else None,
            right_span=right_span, right_w_mm=round((right_span[1] - right_span[0]) / PXMM, 2) if right_span else None,
            colgap_mm=round((right_span[0] - left_span[1]) / PXMM, 2) if left_span and right_span else None,
            n_text_lines=len(text_lines),
            pitch_mode_px=pitch_mode,
            pitch_mode_pt=[(round(p * 72 / 25.4 / PXMM, 2), c) for p, c in pitch_mode],
            first_line_top_px=text_lines[0][0] if text_lines else None,
            first_line_top_mm=round(text_lines[0][0] / PXMM, 2) if text_lines else None,
        )
    return out


# ---------- E1：字心距 / 每行字数 ----------
def e1_pitch(pages=('p04', 'p05', 'p06', 'p07')):
    out = {}
    for tag in pages:
        gray = load_gray(REF % tag)
        ik = ink(gray)
        recs = []
        # 左右栏两个 x 带
        for x0, x1, col in ((243, 1433, 'L'), (1540, 2730, 'R')):
            lines = find_lines(ik, x0, x1)
            for (a, b) in lines:
                if (b - a) < 20 or (b - a) > 50:
                    continue
                segs = segment_chars(ik, a, b, x0, x1)
                segs = [s for s in segs if s[1] - s[0] >= 8]
                if len(segs) < 12:
                    continue
                ws = [s[1] - s[0] for s in segs]
                hts = [s[3] - s[2] for s in segs]
                medw = float(np.median(ws))
                medh = float(np.median(hts))
                # 纯 CJK 行：字宽中位 ≈ 全角，且段数 = 行字数近似
                cts = [(s[0] + s[1]) / 2 for s in segs]
                pitches = [cts[i + 1] - cts[i] for i in range(len(cts) - 1)
                           if ws[i] > 0.75 * medw and ws[i + 1] > 0.75 * medw]
                if len(pitches) < 8:
                    continue
                medp = float(np.median(pitches))
                stdp = float(np.std(pitches))
                # 每行字数＝ink 跨长 / 字心距 + 1
                span = segs[-1][1] - segs[0][0]
                nchars = span / medp + 1
                recs.append(dict(page=tag, col=col, y=(a, b), n_seg=len(segs),
                                 medw=round(medw, 1), medh=round(medh, 1),
                                 pitch_med=round(medp, 2), pitch_mm=round(medp / PXMM, 3),
                                 pitch_std=round(stdp, 2),
                                 n_char_est=round(float(nchars), 1),
                                 span_mm=round(span / PXMM, 1)))
        recs.sort(key=lambda r: -r['n_seg'])
        out[tag] = recs[:12]
    return out


# ---------- E2：标点 ----------
def e2_punct(pages=('p04', 'p05', 'p06', 'p07')):
    out = {}
    for tag in pages:
        gray = load_gray(REF % tag)
        ik = ink(gray)
        recs = []
        for x0, x1, col in ((243, 1433, 'L'), (1540, 2730, 'R')):
            lines = find_lines(ik, x0, x1)
            for (a, b) in lines:
                if (b - a) < 20 or (b - a) > 55:
                    continue
                segs = segment_chars(ik, a, b, x0, x1)
                if len(segs) < 4:
                    continue
                hts = [s[3] - s[2] for s in segs]
                ws = [s[1] - s[0] for s in segs]
                medh = float(np.median(hts))
                medw = float(np.median(ws))
                for i, s in enumerate(segs):
                    h = s[3] - s[2]; w = s[1] - s[0]
                    # 句读标点：矮墨块（底部）或点状墨块（顿号/逗号/分号/句点），h<0.45*medh 且 w<0.5*medw
                    if not (h < 0.45 * medh and w < 0.6 * medw):
                        continue
                    if i in (0, len(segs) - 1):
                        continue
                    prev, nxt = segs[i - 1], segs[i + 1]
                    recs.append(dict(page=tag, col=col, y=(a, b), i=i,
                                     w=w, h=h,
                                     gap_before=int(s[0] - prev[1]), gap_after=int(nxt[0] - s[1]),
                                     pitch_before=round((s[0] + s[1]) / 2 - (prev[0] + prev[1]) / 2, 1),
                                     pitch_after=round((nxt[0] + nxt[1]) / 2 - (s[0] + s[1]) / 2, 1),
                                     medh=round(medh, 1), medw=round(medw, 1)))
        out[tag] = recs
    return out


# ---------- ②条目号后隙 ----------
def item_gap(pages=('p04', 'p05')):
    """条目行行首 '数字.' 形态：行首第一段＝数字（窄），第二段＝'.'，量 '.' 右缘→内容首字左缘。"""
    out = {}
    for tag in pages:
        gray = load_gray(REF % tag)
        ik = ink(gray)
        recs = []
        for x0, x1, col in ((243, 1433, 'L'), (1540, 2730, 'R')):
            lines = find_lines(ik, x0, x1)
            for (a, b) in lines:
                if (b - a) < 20 or (b - a) > 55:
                    continue
                segs = segment_chars(ik, a, b, x0, x1)
                if len(segs) < 3:
                    continue
                s0, s1, s2 = segs[0], segs[1], segs[2]
                w0 = s0[1] - s0[0]; w1 = s1[1] - s1[0]
                # 数字：窄（<0.7 中位宽）；'.'：小墨块；且行首段距栏左 < 20px
                ws = [s[1] - s[0] for s in segs]
                medw = float(np.median(ws))
                if s0[0] - x0 > 25:
                    continue
                if not (w0 < 0.75 * medw and 4 <= w0 <= 30):
                    continue
                if not (w1 < 0.4 * medw and s1[3] - s1[2] < 0.5 * (s0[3] - s0[2])):
                    continue
                recs.append(dict(page=tag, col=col, y=(a, b),
                                 num_bbox=[int(v) for v in s0], dot_bbox=[int(v) for v in s1],
                                 body_bbox=[int(v) for v in s2],
                                 gap_dot_body_px=int(s2[0] - s1[1]),
                                 gap_dot_body_mm=round((s2[0] - s1[1]) / PXMM, 3),
                                 num_w=w0, dot_w=w1, medw=round(medw, 1)))
        out[tag] = recs
    return out


if __name__ == '__main__':
    res = {}
    res['E7'] = e7_geometry()
    res['E1'] = e1_pitch()
    res['E2'] = e2_punct()
    res['ITEM'] = item_gap()
    json.dump(res, open(r'C:/提示词/工作区/_tmp取证0909c/片H1/全品靶复测.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('=== E7 ===')
    for tag, r in res['E7'].items():
        print(tag, 'ink mm', r['x_ink_mm'], 'leftW', r['left_w_mm'], 'rightW', r['right_w_mm'],
              'colgap', r['colgap_mm'], 'pitch(pt,cnt)', r['pitch_mode_pt'], 'first_top', r['first_line_top_mm'])
    print('=== E1 前几行 ===')
    for tag, recs in res['E1'].items():
        for r in recs[:4]:
            print(tag, r['col'], r['y'], 'pitch_mm', r['pitch_mm'], 'pitch_std', r['pitch_std'],
                  'nseg', r['n_seg'], 'n_char≈', r['n_char_est'], 'span', r['span_mm'])
    print('=== E2 汇总 ===')
    import statistics as st
    allg = [(r['gap_before'], r['gap_after']) for tag, recs in res['E2'].items() for r in recs]
    if allg:
        gb = sorted(g for g, _ in allg); ga = sorted(g for _, g in allg)
        print('gap_before n=%d med=%s p10=%s p90=%s' % (len(gb), gb[len(gb)//2], gb[len(gb)//10], gb[9*len(gb)//10]))
        print('gap_after  n=%d med=%s p10=%s p90=%s' % (len(ga), ga[len(ga)//2], ga[len(ga)//10], ga[9*len(ga)//10]))
    print('=== 条目号 ===')
    for tag, recs in res['ITEM'].items():
        print(tag, len(recs))
        for r in recs:
            print('   ', r['y'], 'gap_mm', r['gap_dot_body_mm'], 'num_w', r['num_w'], 'medw', r['medw'])
