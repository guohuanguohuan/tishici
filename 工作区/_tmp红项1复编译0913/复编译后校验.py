# -*- coding: utf-8 -*-
r"""红项①复编译后校验（只读）：
A. ④页脚块几何逐页读数（窗口承袭 S7 跑门 D 族：块 26.2×7.8±0.3、底 11±0.5、数字 10.5~11.5、近 2.5~3.4）
B. 新 pdf ↔ 陈旧快照 逐页文本 diff（证正文零位移，仅页脚 A→B）
C. 新 pdf 偶页页脚串 ↔ 装配/导学本.pdf 起39 六页 页脚串 对照
"""
import io, sys, os, re, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

PT = 72 / 25.4
MARGIN, COLSEP, BOT, PAGew, PAGEh = 17.2 * PT, 7.6 * PT, 20 * PT, 595.276, 842.0
CL = [MARGIN, MARGIN + (PAGew - 2 * MARGIN - COLSEP) / 2 + COLSEP]
CW = (PAGew - 2 * MARGIN - COLSEP) / 2
BODY_BOT = PAGEh - BOT


def rgb255(c):
    return tuple(round(x * 255) for x in c)


def foot_geom(doc, label, start=0):
    print(f'--- ④页脚块几何读数（{label}）---')
    out = []
    for i, page in enumerate(doc, 1):
        pno = i + start
        blk = None
        for d in page.get_drawings():
            r, f = d['rect'], d.get('fill')
            if f and r.y0 > BODY_BOT - 10 and rgb255(f) == (221, 221, 221):
                blk = r
        spans, txts = [], []
        for b in page.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                s = ln['spans']
                t = ''.join(sp['text'] for sp in s).strip()
                if not t:
                    continue
                bb = ln['bbox']
                if bb[1] > BODY_BOT - 2:
                    spans += [sp for sp in s if sp['text'].strip()]
                    txts.append(t)
        num = None
        for b in page.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                for sp in ln['spans']:
                    if sp['text'].strip() in (str(pno), '%02d' % pno) and blk \
                       and ln['bbox'][1] > BODY_BOT - 10 \
                       and blk.x0 - 1 <= sp['bbox'][0] and sp['bbox'][2] <= blk.x1 + 1:
                        num = sp
        if not blk or not num:
            out.append(f'p{pno} 缺块/缺数字')
            continue
        bw, bh = blk.width / PT, blk.height / PT
        bot = (PAGEh - blk.y1) / PT
        near = abs(((num['bbox'][0] if pno % 2 else num['bbox'][2])
                    - (blk.x0 if pno % 2 else blk.x1))) / PT
        szs = sorted({round(sp['size'], 2) for sp in spans})
        ok = (abs(bw - 26.2) <= 0.3 and abs(bh - 7.8) <= 0.3 and abs(bot - 11) <= 0.5
              and 10.5 <= num['size'] <= 11.5 and 2.5 <= near <= 3.4
              and any(5.0 <= s <= 5.45 for s in szs))
        fonts = {sp['font'] for sp in spans}
        okf = any('FZSSJW' in f for f in fonts) and (
            any('NotoSansSC' in f for f in fonts) if pno % 2 else True)
        out.append(f'p{pno}{"奇" if pno % 2 else "偶"} {bw:.1f}×{bh:.1f} 底{bot:.1f} '
                   f'数字{num["size"]:.1f} 近{near:.2f} 小字{szs} '
                   f'{"✓" if ok and okf else "✗" + ("" if ok else " 窗") + ("" if okf else " 字")}')
    print('；'.join(out))
    return out


def page_texts(pdfp, pages=None):
    doc = pymupdf.open(pdfp)
    d = {}
    for i, page in enumerate(doc, 1):
        if pages and i not in pages:
            continue
        d[i] = page.get_text('text')
    doc.close()
    return d


new = r"C:\提示词\工作区\M2-第1章量产0911\成卷\导学件\章末-本章总结提升\main.pdf"
old = r"C:\提示词\工作区\_tmp红项1复编译0913\陈旧快照-main.pdf"
asm = r"C:\提示词\工作区\M2-第1章量产0911\成卷\装配\导学本.pdf"

dn = pymupdf.open(new); do = pymupdf.open(old)
print('页数：新 pdf=%d　陈旧快照 pdf=%d' % (dn.page_count, do.page_count))
foot_geom(dn, '新 pdf')
foot_geom(do, '陈旧快照 pdf（复编译前）', start=0)
dn.close(); do.close()

print('\n--- B. 逐页文本 diff（陈旧 → 新）---')
tn, to = page_texts(old), page_texts(new)
for p in sorted(tn):
    if tn[p] == to[p]:
        print(f'p{p}：零差异')
        continue
    diff = [l for l in difflib.unified_diff(tn[p].splitlines(), to[p].splitlines(), lineterm='', n=0)
            if l[:1] in '+-' and l[1:2] not in ('+', '-')]
    print(f'p{p}：差异 {len(diff)} 行 -> ' + ' | '.join(x.strip() for x in diff))

if os.path.exists(asm):
    print('\n--- C. 装配/导学本.pdf 起39 六页页脚对照（只读）---')
    da = pymupdf.open(asm)
    print('导学本页数=%d' % da.page_count)
    for p in range(39, 45):
        page = da[p - 1]
        ts = []
        for b in page.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                t = ''.join(sp['text'] for sp in ln['spans']).strip()
                if t and ln['bbox'][1] > BODY_BOT - 2:
                    ts.append(t)
        ft = ''.join(ts).replace(' ', '')
        print(f'导学本 p{p}（{"奇" if p % 2 else "偶"}）页脚：{ft}')
    da.close()
else:
    print('\n(未找到装配/导学本.pdf，跳过 C)')
