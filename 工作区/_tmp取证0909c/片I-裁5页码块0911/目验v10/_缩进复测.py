# -*- coding: utf-8 -*-
r"""缩进复测（v10-B 证据脚本）：逐页逐视觉行量「行首墨左缘」，按栏折算缩进量＋居中复核。

口径＝300dpi 灰度像素墨缘（灰阈<128；卷四证据等级：像素测量），与 _判行检测.py 同族。
版心事实：A4 210mm，左右 margin 17.2mm，columnsep 7.6mm → 栏宽 84.0mm；
  左栏左缘 17.2mm，右栏左缘 108.8mm。
分档（Δ＝行首墨左缘−本栏左缘；含首字左侧向，宋体≈0.4mm、黑体/楷体≈0.5–0.7mm）：
  顶格  Δ<=0.90mm
  一档  4.50mm<=Δ<=6.00mm（\qpind=5.0mm＋侧向）
  居中  Δ>6.00mm 且 左空与右空差<=1.20mm（知识点标题行＝整行居中于栏）
  其他  逐条列行首文本供人工归类（页眉页脚/通栏标题/公式行/悬挂段等）
用法：python _缩进复测.py <标签> <pdf路径> <页码表,逗号分隔>
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
COLS = [MARGIN, MARGIN + COLW + COLSEP]
LABELS = ('[答案]', '[解析]', '[分析]', '[详解]', '[点睛]', '[题型总结]')


def ink_span(page, y0, y1, cl):
    """行带 [cl, cl+COLW] 内最左/最右墨像素 x（pt）；无墨返回 (None, None)。"""
    clip = pymupdf.Rect(cl - 1.0, y0 - 0.5, cl + COLW, y1 + 0.5)
    pix = page.get_pixmap(dpi=DPI, clip=clip, colorspace=pymupdf.csGRAY)
    w, h, s = pix.width, pix.height, pix.samples
    lo = hi = None
    for x in range(w):
        if any(s[r_ * w + x] < 128 for r_ in range(h)):
            lo = clip.x0 + x / SC
            break
    if lo is None:
        return None, None
    for x in range(w - 1, -1, -1):
        if any(s[r_ * w + x] < 128 for r_ in range(h)):
            hi = clip.x0 + (x + 1) / SC - 1.0 / SC
            break
    return lo, hi


def run(tag, pdf, pages):
    doc = pymupdf.open(pdf)
    print('=' * 84)
    print(f'[{tag}] {pdf}  页表={pages}')
    print('=' * 84)
    rows = []
    for pno in pages:
        page = doc[pno - 1]
        bycol = {}
        for blk_ in page.get_text('dict')['blocks']:
            for ln in blk_.get('lines', []):
                t = ''.join(sp['text'] for sp in ln['spans']).strip()
                if not t:
                    continue
                bb = pymupdf.Rect(ln['bbox'])
                base = ln['spans'][0]['origin'][1]
                cl = COLS[0] if bb.x0 < MID else COLS[1]
                bycol.setdefault((cl, round(base * 2)), []).append((t, bb, base))
        vis = []
        for (cl, _kb), frs in bycol.items():
            frs.sort(key=lambda r: r[1].x0)
            vis.append((cl, ''.join(r[0] for r in frs),
                        min(r[1].y0 for r in frs), max(r[1].y1 for r in frs),
                        min(r[2] for r in frs)))
        vis.sort(key=lambda r: (r[0], r[4]))
        for cl, t, y0, y1, base in vis:
            il, ir = ink_span(page, y0, y1, cl)
            if il is None:
                continue
            d = (il - cl) / PT
            dr = ((cl + COLW) - ir) / PT
            if d <= 0.90:
                cls = '顶格'
            elif 4.50 <= d <= 6.00:
                cls = '一档'
            elif d > 6.00 and abs(d - dr) <= 1.20:
                cls = '居中'
            else:
                cls = '其他'
            rows.append((pno, 'L' if cl == COLS[0] else 'R', round(base / PT, 2),
                         round(d, 2), round(dr, 2), cls, t.replace('\n', '')[:22]))
    doc.close()
    n = len(rows)
    print(f'{"页":>3} {"栏":>2} {"基线mm":>7} {"Δ左mm":>6} {"Δ右mm":>6} {"档":>4}  行首')
    for r in rows:
        print(f'{r[0]:>3} {r[1]:>2} {r[2]:>7.2f} {r[3]:>6.2f} {r[4]:>6.2f} {r[5]:>4}  {r[6]}')
    print('--- 汇总 ---')
    for k in ('顶格', '一档', '居中', '其他'):
        sub = [r for r in rows if r[5] == k]
        ds = sorted(r[3] for r in sub)
        rng = f'Δ{ds[0]:.2f}–{ds[-1]:.2f}mm 中位{ds[len(ds)//2]:.2f}' if ds else '—'
        print(f'  {k}: {len(sub)}/{n}  {rng}')
    print('  — 顶格样本（标签行/条目行）—')
    for r in [x for x in rows if x[5] == '顶格'][:6]:
        print(f'    p{r[0]}{r[1]} Δ{r[3]}mm 「{r[6]}」')
    print('  — 一档样本（内容/续行）—')
    for r in [x for x in rows if x[5] == '一档'][:6]:
        print(f'    p{r[0]}{r[1]} Δ{r[3]}mm 「{r[6]}」')
    print('  — 居中样本（知识点标题行）—')
    for r in [x for x in rows if x[5] == '居中']:
        print(f'    p{r[0]}{r[1]} Δ左{r[3]}mm Δ右{r[4]}mm 「{r[6]}」')
    print('  — 其他明细（逐条人工归类）—')
    for r in [x for x in rows if x[5] == '其他']:
        print(f'    p{r[0]}{r[1]} 基线{r[2]}mm Δ左{r[3]}mm Δ右{r[4]}mm 「{r[6]}」')
    # 结构核对：按行首文本判定「应顶格／应一档」两类硬指标
    print('  — 结构核对 —')
    lab = [r for r in rows if r[6].startswith(LABELS)]
    lab_ok = [r for r in lab if r[3] <= 0.90]
    print(f'    标签行（[答案]/[解析]/[题型总结]…起行）共{len(lab)}，其中顶格{len(lab_ok)}，'
          f'非顶格{[ (r[0],r[1],r[3],r[6][:10]) for r in lab if r[3] > 0.90 ][:6]}')
    tx = [r for r in rows if r[6].startswith('题型：')]
    print(f'    题型行共{len(tx)}，Δ左分布{sorted(set(r[3] for r in tx))}')
    kd = [r for r in rows if re.match(r'^知识点[一二三四五六七八九十]', r[6])]
    print(f'    知识点行共{len(kd)}，档别{[(r[0],r[1],r[3],r[4],r[5]) for r in kd]}')
    return rows


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) >= 3:
        run(a[0], a[1], [int(x) for x in a[2].split(',')])
    else:
        V9 = r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\靠齐样张包-v9-21页0911.pdf'
        run('v9册v1(包p7-10)', V9, [7, 8, 9, 10])
        run('v10册v1现件(p1-4)', r'C:\提示词\工作区\字替对照-0909\导学件答案册-v1\main.pdf', [1, 2, 3, 4])
        run('v9样张(包p13-14)', V9, [13, 14])
        run('v10样张现件(p1-2)', r'C:\提示词\工作区\字替对照-0909\靠齐样张-0910\答案册\main.pdf', [1, 2])
