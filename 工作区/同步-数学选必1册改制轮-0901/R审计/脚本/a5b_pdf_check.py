# -*- coding: utf-8 -*-
"""R1审计——§14 PDF校验v2：空白容忍同串断言＋词典式跑头双断言（抽10页/件）＋span级图文重叠候选＋重叠clip渲染。"""
import sys, os, re, random
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
import fitz

PDFDIR = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\输出\a5b_pdf校验.txt'
STARTS = {'X1':1,'I1':1,'B':1,'C':78,'X2':1,'I2':1,'E':1,'F':54,'G':110,'H':151}
NVAL = {'X1':16,'I1':20,'B':154,'C':154,'X2':5,'I2':39,'E':221,'F':221,'G':221,'H':221}
WS = r'[ \t]*'
out = open(OUT, 'w', encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out)
random.seed(7)

for code in ['X1','I1','B','E','X2','I2','C','F','G','H']:
    doc = fitz.open(os.path.join(PDFDIR, code + '.pdf'))
    n = doc.page_count
    P('='*90)
    P('### %s 页数=%d' % (code, n))
    # 抽样页：优先含锚换节页＋随机页（全件10页/件；5页件全页）
    anchor_pages = []
    all_pages_have = {}
    running = None
    # 先扫锚分布（全页，快速）
    page_anchors = {}
    for pi in range(n):
        d = doc[pi].get_text('dict')
        anch = []
        for blk in d['blocks']:
            if blk['type'] != 0: continue
            for ln in blk['lines']:
                for sp in ln['spans']:
                    if sp['color'] == 0xFFFFFF and sp['size'] < 2.5 and sp['text'].strip():
                        anch.append((sp['bbox'][1], sp['text'].strip()))
        anch.sort()
        page_anchors[pi] = anch
        if anch: anchor_pages.append(pi)
    sample = set(anchor_pages[:4])
    while len(sample) < min(10, n):
        sample.add(random.randrange(n))
    sample = sorted(sample)
    fails = []; ovl = []
    for pi in sample:
        page = doc[pi]
        r = page.rect
        d = page.get_text('dict')
        spans = []
        for blk in d['blocks']:
            if blk['type'] != 0: continue
            for ln in blk['lines']:
                for sp in ln['spans']:
                    if sp['text'].strip(): spans.append(sp)
        anch = page_anchors[pi]
        running = anch[0][1] if anch else running
        h = ''.join(sp['text'] for sp in sorted([s for s in spans if s['bbox'][1] < 60], key=lambda s: s['bbox'][1]))
        f = ''.join(sp['text'] for sp in sorted([s for s in spans if s['bbox'][3] > r.height - 55], key=lambda s: s['bbox'][1]))
        h_cl = re.sub(r'\s+', '', h); f_cl = re.sub(r'\s+', '', f)
        exp_pg = STARTS[code] + pi
        ok_same = ('第%d页' % exp_pg in h_cl) and ('第%d页' % exp_pg in f_cl)
        okN = ('（共%d页）' % NVAL[code] in h_cl) and ('（共%d页）' % NVAL[code] in f_cl)
        m_h = re.search(r'（共\d+页）(.+?)第\d+页', h_cl)
        m_f = re.search(r'（共\d+页）(.+?)第\d+页', f_cl)
        sh = m_h.group(1) if m_h else None
        sf = m_f.group(1) if m_f else None
        run_cl = re.sub(r'\s+', '', running) if running else None
        dbl = (sh is not None and sh == sf == run_cl)
        P('  p%-3d 同串页码=%s N=%s 双断言=%s | 页眉节=%r 页脚节=%r 跑头锚=%r' % (pi+1, ok_same, okN, dbl, sh, sf, run_cl))
        if not (ok_same and okN and dbl):
            fails.append((pi+1, ok_same, okN, dbl, sh, sf, run_cl))
        # span级图文重叠
        for img in page.get_images(full=True):
            try: rects = page.get_image_rects(img[0])
            except Exception: rects = []
            for R in rects:
                for sp in spans:
                    inter = fitz.Rect(sp['bbox']) & R
                    if not inter.is_empty and inter.get_area() > 15:
                        ovl.append((pi+1, tuple(round(v,1) for v in R), tuple(round(v,1) for v in sp['bbox']), round(inter.get_area(),1), sp['text'][:36]))
    P('  断言失败页=%d %s' % (len(fails), fails if fails else '无——全过'))
    P('  span级图文重叠候选=%d' % len(ovl))
    for o in ovl[:14]:
        P('    候选: p%d 图=%s span=%s 交叠%.0fpt² 文本=%r' % o)
    # 渲染前4个真实候选clip供过目
    if ovl:
        for k, o in enumerate(ovl[:4]):
            pi = o[0]-1
            page = doc[pi]
            clip = fitz.Rect(o[1]) & page.rect
            clip = fitz.Rect(max(0,clip.x0-4), max(0,clip.y0-4), min(page.rect.x1,clip.x1+4), min(page.rect.y1,clip.y1+4))
            pix = page.get_pixmap(matrix=fitz.Matrix(2.2, 2.2), clip=clip)
            pix.save(os.path.join(PDFDIR, '%s_ovl_p%d_%d.png' % (code, pi+1, k)))
    doc.close()
out.close()
print('DONE')
