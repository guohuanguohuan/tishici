# -*- coding: utf-8 -*-
"""片H2 探针测量 v2：锁定末三行标记行（测甲…测乙/测丙）逐结构量化。
输出：cap(中位)/sub(中位)/分式总高/减号宽与邻隙/行距序列。"""
import json
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
import fitz

OUT = r'C:/提示词/工作区/_tmp取证0909c/片H2/探针'


def render(tag):
    pdf = f'{OUT}/probe_{tag}.pdf'
    png = f'{OUT}/probe_{tag}.png'
    doc = fitz.open(pdf)
    pix = doc[0].get_pixmap(dpi=360)
    pix.save(png)
    return png


def ink_of(png):
    return np.asarray(Image.open(png).convert('L')).astype(np.uint8) < 170


def bands(ik, x0, x1, min_ink=3, min_h=8, merge_gap=4):
    sub = ik[:, x0:x1]
    row = sub.sum(axis=1)
    on = row > min_ink
    runs = []
    s = None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            runs.append([s, i])
            s = None
    if s is not None:
        runs.append([s, len(on)])
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= merge_gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [(a, b) for a, b in merged if b - a >= min_h]


def comps(ik, x0, x1, y0, y1, min_h=2, min_w=2):
    sub = ik[y0:y1, x0:x1]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lab)
    out = []
    for sl in objs:
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        if h < min_h or w < min_w:
            continue
        out.append(dict(x0=int(xs.start + x0), x1=int(xs.stop + x0),
                        y0=int(ys.start + y0), y1=int(ys.stop + y0), w=int(w), h=int(h)))
    out.sort(key=lambda c: c['x0'])
    return out


def frac_stats(ik, bar, xlo, xhi, up=55, dn=60):
    """分式：bar 上下的墨范围（限定 x 于 bar 邻域 ±6px）。"""
    xa, xb = max(xlo, bar['x0'] - 6), min(xhi, bar['x1'] + 6)
    ya, yb = bar['y0'], bar['y1']
    ups = ik[max(0, ya - up):ya, xa:xb]
    dns = ik[yb:yb + dn, xa:xb]
    def ext(m, base, top):
        if not m.any():
            return None
        rows = np.where(m.sum(axis=1) > 0)[0]
        return int(base + rows.min()) if top else int(base + rows.max())
    top = ext(ups, ya, True)
    bot = ext(dns, yb, False)
    return dict(bar=(bar['x0'], bar['x1'], bar['y0'], bar['y1']),
                top=top, bot=bot, total=(bot - top) if (top is not None and bot is not None) else None)


def line_gaps(ik, y0, y1, x0, x1):
    """行内 ink 组成（x 区间列表）→ 用于减号邻隙。"""
    sub = ik[y0:y1, x0:x1]
    col = sub.sum(axis=0)
    on = col > 0
    runs = []
    s = None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            runs.append((s + x0, i + x0))
            s = None
    if s is not None:
        runs.append((s + x0, len(on) + x0))
    return runs


def measure(tag):
    png = render(tag)
    ik = ink_of(png)
    H, W = ik.shape
    x0, x1 = 150, W - 150
    lines = bands(ik, x0, x1)
    bases = []
    for (a, b) in lines:
        cs0 = comps(ik, x0, x1, a, b)
        cjkb = [c['y1'] for c in cs0 if 40 <= c['h'] <= 52 and 34 <= c['w'] <= 55]
        bases.append(max(cjkb) if cjkb else None)
    pitches = [round(bases[i + 1] - bases[i], 1) for i in range(len(bases) - 1)
               if bases[i] is not None and bases[i + 1] is not None and bases[i + 1] > bases[i]]
    res = dict(tag=tag, n_lines=len(lines), pitches=pitches, line_bands=lines, bases=bases)
    # 末三行 = 标记行（甲/乙/丙）
    marks = lines[-3:]
    names = ['ABCD行', '分式行', '减号行']
    res['marks'] = {}
    for nm, (a, b) in zip(names, marks):
        cs = comps(ik, x0, x1, a, b)
        letters = [c['h'] for c in cs if 28 <= c['h'] <= 46 and 18 <= c['w'] <= 55]
        subs = [c['h'] for c in cs if 14 <= c['h'] <= 27 and 5 <= c['w'] <= 34]
        bars = [c for c in cs if 2 <= c['h'] <= 8 and 12 <= c['w'] <= 95]
        # '=' 排除：与另一横杠在 6-18px 内同 x → 双杠
        def is_eq(b):
            for c2 in bars:
                if c2 is b:
                    continue
                if 5 <= abs(c2['y0'] - b['y0']) <= 18 and abs(c2['x0'] - b['x0']) < 8 and abs(c2['w'] - b['w']) < 6:
                    return True
            return False
        bars = [c for c in bars if not is_eq(c)]
        # 分式杠候选：更薄（h<=4）
        frac_bars = [c for c in bars if c['h'] <= 4]
        fs = []
        for bar in frac_bars:
            # 分式判据：杠正上方/正下方各有 '厚' 块（h>=10）且水平居中
            ncs = comps(ik, x0, x1, max(0, bar['y0'] - 60), bar['y1'] + 62)
            up_blk = [c for c in ncs if c['y1'] <= bar['y0'] + 1 and c['y1'] >= bar['y0'] - 45
                      and c['h'] >= 10 and c['x0'] >= bar['x0'] - 18 and c['x1'] <= bar['x1'] + 18
                      and (min(c['x1'], bar['x1']) - max(c['x0'], bar['x0'])) > 0.4 * min(c['w'], bar['w'])]
            dn_blk = [c for c in ncs if c['y0'] >= bar['y1'] - 1 and c['y0'] <= bar['y1'] + 50
                      and c['h'] >= 10 and c['x0'] >= bar['x0'] - 18 and c['x1'] <= bar['x1'] + 18
                      and (min(c['x1'], bar['x1']) - max(c['x0'], bar['x0'])) > 0.4 * min(c['w'], bar['w'])]
            if up_blk and dn_blk:
                top = min(c['y0'] for c in up_blk)
                bot = max(c['y1'] for c in dn_blk)
                fs.append(dict(wbar=bar['w'], bar_y=bar['y0'], total=bot - top,
                               numer_h=max(c['h'] for c in up_blk), denom_h=max(c['h'] for c in dn_blk)))
        res['marks'][nm] = dict(
            y=(a, b), h=b - a,
            letter_h=sorted(letters), letter_med=float(np.median(letters)) if letters else None,
            sub_h=sorted(subs), sub_med=float(np.median(subs)) if subs else None,
            bars=[[c['x0'], c['x1'], c['y0'], c['y1']] for c in bars],
            fracs=fs)
        if nm == '减号行':
            # 取最左 w>=20 的横杠作为减号
            cand = [c for c in bars if c['w'] >= 18]
            if cand:
                mb = cand[0]
                runs = line_gaps(ik, mb['y0'] - 14, mb['y1'] + 14, x0, x1)
                # 找减号在 runs 中的位置
                for i, (ra, rb) in enumerate(runs):
                    if ra <= mb['x0'] and rb >= mb['x1']:
                        gl = mb['x0'] - runs[i - 1][1] if i > 0 else None
                        gr = runs[i + 1][0] - mb['x1'] if i + 1 < len(runs) else None
                        res['marks'][nm]['minus'] = dict(w=mb['w'], x0=mb['x0'], x1=mb['x1'],
                                                         gap_l=gl, gap_r=gr)
                        break
    # ABCD 行的短横（w<18 的横杠）
    ab = res['marks']['ABCD行']
    ab['dash_small'] = [b for b in ab['bars'] if b[1] - b[0] < 18]
    if ab['bars']:
        mb = ab['bars'][0]
        runs = line_gaps(ik, mb[2] - 14, mb[3] + 14, x0, x1)
        for i, (ra, rb) in enumerate(runs):
            if ra <= mb[0] and rb >= mb[1]:
                gl = mb[0] - runs[i - 1][1] if i > 0 else None
                gr = runs[i + 1][0] - mb[1] if i + 1 < len(runs) else None
                ab['abs_minus'] = dict(w=mb[1] - mb[0], gap_l=gl, gap_r=gr)
                break
    return res


if __name__ == '__main__':
    tags = sys.argv[1:] or ['t0']
    alld = {}
    for t in tags:
        r = measure(t)
        alld[t] = r
        m = r['marks']
        print(f"== {t} pitches={r['pitches']}")
        for nm in ('ABCD行', '分式行', '减号行'):
            d = m[nm]
            fr = [(f['wbar'], f['total'], f['numer_h'], f['denom_h']) for f in d['fracs']]
            print(f"  {nm} y{d['y']} h{d['h']} cap_med={d['letter_med']} sub_med={d['sub_med']} "
                  f"fracs(w,total,nh,dh)={fr}")
            if 'minus' in d:
                print(f"     minus={d['minus']}")
            if nm == 'ABCD行':
                print(f"     dash_small={d.get('dash_small')} abs_minus={d.get('abs_minus')}")
    json.dump(alld, open(f'{OUT}/probe_metrics.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
