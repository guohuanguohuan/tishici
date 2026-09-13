# -*- coding: utf-8 -*-
r"""红项①抽验器（只读）：逐页页脚实印串＋⑤奇偶交替门判据复算。

窗口/判据逐字承袭 工作区/_tmpS7双断言跑门0913/S7双断言跑门.py 的 D 族 ④⑤ 门
（margin 17.2mm／top 19.6mm／bot 20mm／colsep 7.6mm／双栏；页脚块色 221；
奇＝块贴右＋件名在场；偶＝块贴左＋「人教B」串在场）。

用法：python 抽页脚.py <main.pdf> [页码表 逗号分隔]
"""
import io, sys, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

PT = 72 / 25.4
CFG = dict(margin=17.2 * PT, top=19.6 * PT, bot=20 * PT, colsep=7.6 * PT, ncols=2,
           page=(595.276, 842.0))


def col_lefts(cfg, pw):
    m, cs = cfg['margin'], cfg['colsep']
    cw = (pw - 2 * m - cs * (cfg['ncols'] - 1)) / cfg['ncols']
    return [m + i * (cw + cs) for i in range(cfg['ncols'])], cw


def rgb255(c):
    return tuple(round(x * 255) for x in c)


def main(pdfp, pages_want, jianming):
    cfg = CFG
    doc = pymupdf.open(pdfp)
    n_pdf = doc.page_count
    pw, ph = cfg['page']
    cls, colw = col_lefts(cfg, pw)
    TOP, BOT = cfg['top'], cfg['bot']
    BODY_BOT = ph - BOT
    print(f'文件 {os.path.abspath(pdfp)}')
    print(f'页数 pdf={n_pdf}　纸宽×高={pw:.1f}×{ph:.1f}　版心底 y={BODY_BOT:.1f}'
          f'　栏左={["%.1f" % c for c in cls]} 栏宽={colw:.1f}')
    rows = []
    alt_ok, alt_bad = True, []
    for pno, page in enumerate(doc, 1):
        blk_rect = None
        for d in page.get_drawings():
            r, f = d['rect'], d.get('fill')
            if not f or r.y0 <= BODY_BOT - 10:
                continue
            if rgb255(f) == (221, 221, 221):
                blk_rect = r
        foot_txts = []
        for blk in page.get_text('dict')['blocks']:
            for ln in blk.get('lines', []):
                t = ''.join(sp['text'] for sp in ln['spans']).strip()
                if not t:
                    continue
                bb = ln['bbox']
                if bb[1] > BODY_BOT - 2:
                    foot_txts.append(t)
        ft = ''.join(foot_txts).replace(' ', '')
        odd = pno % 2 == 1
        # ⑤ 门判据（D 族）
        if blk_rect is None:
            okp = False
            why = '缺块'
        elif odd:
            okp = blk_rect.x1 >= max(cls) + colw - 1.5 and (jianming in ft or jianming == '')
            why = ('块贴右✓' if blk_rect.x1 >= max(cls) + colw - 1.5 else '块贴右✗') \
                  + ('＋件名✓' if jianming in ft else '＋件名✗')
        else:
            okp = blk_rect.x0 <= min(cls) + 1.5 and ('人教B' in ft)
            why = ('块贴左✓' if blk_rect.x0 <= min(cls) + 1.5 else '块贴左✗') \
                  + ('＋人教B✓' if '人教B' in ft else '＋人教B✗')
        if not okp:
            alt_ok = False
            alt_bad.append(f'p{pno}{"奇" if odd else "偶"}')
        rows.append(dict(p=pno, odd='奇' if odd else '偶',
                         blk=('无' if blk_rect is None else
                              f'x0={blk_rect.x0:.1f} x1={blk_rect.x1:.1f}'),
                         A=('人教A' in ft), B=('人教B' in ft),
                         jian=(jianming in ft), foot=ft, ok=okp, why=why))
    for r in rows:
        mark = '✓' if r['ok'] else '✗'
        star = ' ★' if (pages_want is None or r['p'] in pages_want) else ''
        print(f"p{r['p']}（{r['odd']}）{mark} {r['why']}　块{r['blk']}　"
              f"A版串={r['A']} B版串={r['B']} 件名={r['jian']}{star}")
        print(f"    页脚实印：{r['foot']}")
    print(f"⑤奇偶交替（件名={jianming}）：{'全绿 ✓' if alt_ok else '✗' + ','.join(alt_bad)}")
    doc.close()
    return alt_ok


if __name__ == '__main__':
    pdfp = sys.argv[1]
    pgs = None
    if len(sys.argv) > 2 and sys.argv[2]:
        pgs = {int(x) for x in sys.argv[2].split(',')}
    jm = sys.argv[3] if len(sys.argv) > 3 else '导学件'
    main(pdfp, pgs, jm)
