# -*- coding: utf-8 -*-
r"""判行检测（v10-A 证据脚本）：逐页逐栏找（　）尾行，报告
  · 形态：挂（同基线有正文）／独（（　）独占视觉行）
  · 该（　）行右缘墨距（栏右基准）
  · 若形态＝独：上一视觉行的行尾余空（栏右−上行墨右缘）
  · 若形态＝挂：本行行尾余空＝（　）墨右缘距栏右（即右挂残差）
口径＝300dpi 灰度像素墨缘（卷四证据等级：像素测量）。
用法：python _判行检测.py <pdf路径> [页码表,逗号分隔]
"""
import io
import re
import sys

import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PT = 72 / 25.4
MARGIN = 17.2 * PT
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
DPI = 300
SC = DPI / 72.0


def ink_right(page, y0, y1, cl):
    """行带 [cl, cl+COLW] 内最右墨像素 x（pt）；无墨返回 None。"""
    clip = pymupdf.Rect(cl, y0 - 0.5, cl + COLW, y1 + 0.5)
    pix = page.get_pixmap(dpi=DPI, clip=clip, colorspace=pymupdf.csGRAY)
    w, h, s = pix.width, pix.height, pix.samples
    for x in range(w - 1, -1, -1):
        if any(s[r_ * w + x] < 128 for r_ in range(h)):
            return clip.x0 + (x + 1) / SC - 1.0 / SC
    return None


def run(pdf, pages):
    doc = pymupdf.open(pdf)
    for pno in pages:
        page = doc[pno - 1]
        lines = []
        for blk_ in page.get_text('dict')['blocks']:
            for ln in blk_.get('lines', []):
                t = ''.join(sp['text'] for sp in ln['spans']).strip()
                if t:
                    lines.append((t, pymupdf.Rect(ln['bbox']), ln['spans'][0]['origin'][1]))
        # 基线归并（按栏分列：上一行只在同栏找）
        bycol = {}
        for t, bb, base in lines:
            cl = MARGIN if bb.x0 < MID else MARGIN + COLW + COLSEP
            bycol.setdefault((cl, round(base * 2)), []).append((t, bb, base))
        colrows = {}
        for (cl, kb), frs in bycol.items():
            frs.sort(key=lambda r: r[1].x0)
            colrows.setdefault(cl, []).append(
                (''.join(r[0] for r in frs), frs[0][1], frs[0][2]))
        for cl in colrows:
            colrows[cl].sort(key=lambda r: r[2])
        for cl, rws in colrows.items():
            for k, (t, bb, base) in enumerate(rws):
                tc = re.sub(r'\s+', '', t)
                if not tc.endswith('（）'):
                    continue
                alone = tc == '（）'
                ir = ink_right(page, bb.y0, bb.y1, cl)
                note = ''
                if k > 0:
                    pt_, pb_, pbase = rws[k - 1]
                    if abs(pbase - base) > 2.0:      # 同栏上一视觉行
                        pir = ink_right(page, pb_.y0, pb_.y1, cl)
                        if pir:
                            note = f'｜上行余空 {(cl + COLW - pir):.1f}pt＝{(cl + COLW - pir) / PT:.1f}mm（行尾「{pt_[-6:]}」）'
                print(f'p{pno} c{"左" if cl < MID else "右"} {"独" if alone else "挂"} '
                      f'墨距栏右 {(cl + COLW - ir) / PT:.2f}mm {note}｜{t[:26]}')
    doc.close()


if __name__ == '__main__':
    pdf = sys.argv[1]
    pgs = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [1, 2, 3, 4, 5]
    run(pdf, pgs)
