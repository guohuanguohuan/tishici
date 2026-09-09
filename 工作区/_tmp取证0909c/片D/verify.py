# -*- coding: utf-8 -*-
"""片D 0909c 验证：变式标签双字重「变/式」笔画竖粗实测（我方改前/改后 vs 全品 p06 真迹，同尺同法）。
口径沿 C组 bianshi.py：360dpi(=14.1732px/mm) 二值众数＋AA积分；另出 600dpi 高倍值。"""
import os, json
import numpy as np
import pymupdf
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
OUR_AFTER = r"C:/提示词/工作区/字替对照-0909/variantF/main.pdf"
OUR_BEFORE = OUT + "/基线_main.pdf"
QP6 = r"C:/提示词/工作区/全品结构提取/数学选必一/导学案页图/p06.png"
PX360 = 360 / 25.4
PX600 = 600 / 25.4
EM_MM = 12.03 * 25.4 / 72


def char_boxes(label, gap=3):
    colink = label.any(axis=0)
    xs = np.where(colink)[0]
    if len(xs) == 0:
        return []
    boxes, s, p = [], xs[0], xs[0]
    for v in xs[1:]:
        if v - p > gap:
            boxes.append((s, p)); s = v
        p = v
    boxes.append((s, p))
    out = []
    for x0, x1 in boxes:
        sub = label[:, x0:x1 + 1]
        ys = np.where(sub.any(axis=1))[0]
        out.append((x0, ys.min(), x1, ys.max()))
    return out


def stroke_stats(gray, bbox):
    x0, y0, x1, y1 = bbox
    h, w = y1 - y0 + 1, x1 - x0 + 1
    dark = gray < 128
    runs = []
    for y in range(y0 + int(0.25 * h), y1 - int(0.2 * h)):
        row = dark[y, x0:x1 + 1]
        d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        ss, ee = np.where(d == 1)[0], np.where(d == -1)[0]
        for s, e in zip(ss, ee):
            ln = e - s
            if 2 <= ln <= 0.45 * w:
                runs.append((y, x0 + s, x0 + e, ln))
    rep = {'nrun': len(runs)}
    if runs:
        lens = np.array([r[3] for r in runs])
        mode = int(np.median(lens))
        sel = [r for r in runs if abs(r[3] - mode) <= 1]
        ints = []
        for (y, xs, xe, ln) in sel:
            prof = 1.0 - gray[y, max(0, xs - 3):xe + 3].astype(np.float64) / 255.0
            ints.append(prof.sum())
        rep['mode'] = mode
        rep['int'] = float(np.median(ints))
    core = gray[y0:y1 + 1, x0:x1 + 1]
    rep['min_gray'] = int(core.min())
    rep['dens'] = float(dark[y0:y1 + 1, x0:x1 + 1].mean())
    rep['h'] = h
    return rep


def measure_pdf(path, tag):
    """逐「变式N」标签逐字实测（360dpi 主口径＋600dpi 高倍）"""
    doc = pymupdf.open(path)
    res = []
    for pno in range(len(doc)):
        page = doc[pno]
        spans = []
        for bl in page.get_text('dict')['blocks']:
            for ln in bl.get('lines', []):
                for sp in ln['spans']:
                    if '变' in sp['text'] and 'Fang' in sp['font']:
                        spans.append(sp)
        for sp in spans:
            bb = sp['bbox']
            x0, y0, x1, y1 = bb
            for dpi, key in ((360, 'z360'), (600, 'z600')):
                clip = pymupdf.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2)
                pm = page.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csGRAY)
                g = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width).copy()
                cbs = char_boxes(g < 128)
                scale = dpi / 25.4
                for i, cb in enumerate(cbs):
                    st = stroke_stats(g, cb)
                    st['px5'] = st.get('int', 0) * PX360 / scale
                    st['dpi'] = dpi
                    res.append(dict(page=pno + 1, label=sp['text'], ch=i, **st))
                if dpi == 360:
                    crop = g
            # 密度（300dpi，逐字 bbox 与断言同法）
            pm3 = page.get_pixmap(dpi=300, clip=clip, colorspace=pymupdf.csGRAY)
            g3 = np.frombuffer(pm3.samples, dtype=np.uint8).reshape(pm3.height, pm3.width)
            cbs3 = char_boxes(g3 < 128)
            for i, cb in enumerate(cbs3):
                core = g3[cb[1]:cb[3] + 1, cb[0]:cb[2] + 1]
                res.append(dict(page=pno + 1, label=sp['text'], ch=i, dpi=300,
                                dens=float((core < 128).mean())))
    doc.close()
    return res


def measure_qp():
    qp = np.asarray(Image.open(QP6).convert('L'))
    out = []
    for name, (wx0, wy0, wx1, wy1) in [('左', (200, 230, 480, 360)), ('右', (1480, 230, 1760, 360))]:
        sub = qp[wy0:wy1, wx0:wx1]
        cbs = char_boxes(sub < 128)
        for i, cb in enumerate(cbs[:2]):   # 只取「变式」两字（后随 如/（1） 非标签）
            st = stroke_stats(sub, cb)
            st['px5'] = st.get('int', 0)
            out.append(dict(label=f'qp_{name}', ch=i, dpi=360, **st))
    return out


before = measure_pdf(OUR_BEFORE, 'before')
after = measure_pdf(OUR_AFTER, 'after')
qpres = measure_qp()

def agg(res, dpi, ch):
    vals_m = [r['mode'] for r in res if r.get('dpi') == dpi and r.get('ch') == ch and 'mode' in r]
    vals_i = [r['int'] for r in res if r.get('dpi') == dpi and r.get('ch') == ch and 'int' in r]
    dens = [r['dens'] for r in res if r.get('dpi') == 300 and r.get('ch') == ch]
    med = lambda v: float(np.median(v)) if v else -1
    return dict(mode=med(vals_m), int=med(vals_i), n=len(vals_i),
                dens=med(dens), mgray=med([r['min_gray'] for r in res if r.get('dpi') == dpi and r.get('ch') == ch]))

print('==== 我方（360dpi 主口径；字0=变 字1=式 字2=1） ====')
for tag, res in (('改前', before), ('改后', after)):
    for ch, nm in ((0, '变'), (1, '式'), (2, '1')):
        a = agg(res, 360, ch)
        b = agg(res, 600, ch)
        print(f"  {tag} {nm}: 360dpi mode={a['mode']}px int={a['int']:.2f}px ({a['int']/PX360:.3f}mm="
              f"{a['int']/PX360/EM_MM:.4f}em) dens={a['dens']:.3f} min={a['mgray']} n={a['n']} "
              f"| 600dpi int={b['int']:.2f}px(→360口径{b['int']*PX360/PX600:.2f}px)")

print('==== 全品 p06（360dpi 原生，同法；p06 标签为「变式」＋后随如/（1），无粘连数字——只列变/式） ====')
for lb in ('qp_左', 'qp_右'):
    for ch, nm in ((0, '变'), (1, '式')):
        r = [x for x in qpres if x['label'] == lb and x['ch'] == ch]
        if not r:
            print(f"  {lb} {nm}: 无"); continue
        r = r[0]
        print(f"  {lb} {nm}: mode={r.get('mode')}px int={r.get('int', 0):.2f}px "
              f"({r.get('int', 0)/PX360:.3f}mm={r.get('int', 0)/PX360/EM_MM:.4f}em) "
              f"dens={r['dens']:.3f} min={r['min_gray']}")

json.dump(dict(before=before, after=after, qp=qpres), open(OUT + "/verify_result.json", "w"),
          ensure_ascii=False, indent=1, default=float)
print("saved verify_result.json")
