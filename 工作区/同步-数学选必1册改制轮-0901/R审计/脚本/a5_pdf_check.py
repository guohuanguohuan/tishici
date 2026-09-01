# -*- coding: utf-8 -*-
"""R1审计——§14 PDF校验：页数/A4/边距x0/页眉页脚同串左对齐/节名锚域逐页双断言/
12pt抽样/图文重叠bbox候选。"""
import sys, os, re, json, random
sys.stdout.reconfigure(encoding='utf-8')
import fitz

PDFDIR = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\输出\a5_pdf校验.txt'
EXPECT_PAGES = {'X1':16,'I1':20,'B':77,'E':53}  # 全件；其余为前5页抽查
STARTS = {'X1':1,'I1':1,'B':1,'C':78,'X2':1,'I2':1,'E':1,'F':54,'G':110,'H':151}
NVAL = {'X1':16,'I1':20,'B':154,'C':154,'X2':5,'I2':39,'E':221,'F':221,'G':221,'H':221}

out = open(OUT, 'w', encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out)

SEC_RE = re.compile(r'^\d+(?:\.\d+)+\s*\S')
random.seed(42)

for code in ['X1','I1','B','E','X2','I2','C','F','G','H']:
    path = os.path.join(PDFDIR, code + '.pdf')
    doc = fitz.open(path)
    n = doc.page_count
    P('='*90)
    P('### %s 页数=%d（全件=%s）' % (code, n, '是' if code in EXPECT_PAGES else '否·前5页抽查'))
    okA4 = True; minx0 = 9e9; hdr_fail = []; sz_sampler = Counter = None
    from collections import Counter
    sz_hist = Counter()
    overlap_cand = []
    pages = list(range(n)) if n <= 5 else sorted(set(list(range(n))[:2] + random.sample(range(n), min(10, n))))
    for pi in pages:
        page = doc[pi]
        r = page.rect
        if abs(r.width-595.3) > 3 or abs(r.height-841.9) > 3: okA4 = False
        d = page.get_text('dict')
        # 文本x0最小值（排除页眉？——页眉页脚同在边距内；§14要求内容x0≈43pt，测全部文本min x0）
        anchors = []  # (y, text) 白色1pt锚
        header_txt = []; footer_txt = []
        for blk in d['blocks']:
            if blk['type'] != 0: continue
            for ln in blk['lines']:
                for sp in ln['spans']:
                    txt = sp['text']
                    if not txt.strip(): continue
                    x0 = sp['bbox'][0]
                    if x0 < 60 or x0 > 555:  # 版心外≈边距带
                        pass
                    # 收集
                    if sp['color'] == 0xFFFFFF and sp['size'] < 2.5:
                        anchors.append((sp['bbox'][1], txt.strip()))
                    if sp['bbox'][1] < 60: header_txt.append((sp['bbox'][1], sp['bbox'][0], txt))
                    if sp['bbox'][3] > r.height - 55: footer_txt.append((sp['bbox'][1], sp['bbox'][0], txt))
                    if 60 < sp['bbox'][1] < r.height - 60:
                        minx0 = min(minx0, x0)
                        sz_hist[round(sp['size'],1)] += 1
        anchors.sort()
        h = ''.join(t for _,_,t in sorted(header_txt))
        f = ''.join(t for _,_,t in sorted(footer_txt))
        hx0 = min((x for _,x,_ in header_txt), default=None)
        fx0 = min((x for _,x,_ in footer_txt), default=None)
        # 断言：页眉=页脚（容忍页码数字）、左对齐x0≈43
        exp_pg = '%d' % (STARTS[code] + pi)
        ok_hdr = ('第%s页' % exp_pg) in h and ('第%s页' % exp_pg) in f
        sec_h = re.search(r'（共\d+页）　(.+?)　第\d+页', h)
        sec_f = re.search(r'（共\d+页）　(.+?)　第\d+页', f)
        okN = ('（共%d页）' % NVAL[code]) in h and ('（共%d页）' % NVAL[code]) in f
        exp_anchor = anchors[0][1] if anchors else None
        a_ok = bool(anchors)
        sh = sec_h.group(1).strip() if sec_h else None
        sf = sec_f.group(1).strip() if sec_f else None
        dbl = (sh == sf == exp_anchor) if (sh and sf and exp_anchor) else False
        if pi in pages[:12]:
            P('  p%d: 页眉x0=%s 页脚x0=%s 同串断言=%s N=%s 双断言(页眉=页脚=首锚)=%s | 页眉节=%r 页脚节=%r 首锚=%r 锚数=%d' % (
                pi+1, hx0, fx0, ok_hdr, okN, dbl, sh, sf, exp_anchor, len(anchors)))
        if not (ok_hdr and okN and dbl and a_ok):
            hdr_fail.append((pi+1, ok_hdr, okN, dbl, a_ok, sh, sf, exp_anchor))
        # 图文重叠bbox候选
        for img in page.get_images(full=True):
            try:
                rects = page.get_image_rects(img[0])
            except Exception:
                rects = []
            for R in rects:
                for blk in d['blocks']:
                    if blk['type'] != 0: continue
                    tb = fitz.Rect(blk['bbox'])
                    inter = tb & R
                    if not inter.is_empty and inter.get_area() > 40:
                        txts = ''.join(sp['text'] for ln in blk['lines'] for sp in ln['spans'])[:40]
                        overlap_cand.append((pi+1, tuple(round(v,1) for v in R), round(inter.get_area(),1), txts))
    P('  A4全过=%s | 版心文本min x0=%.1fpt（期望≈43）' % (okA4, minx0))
    P('  页眉页脚/节名锚断言失败页数=%d %s' % (len(hdr_fail), hdr_fail[:6] if hdr_fail else ''))
    top_sz = sz_hist.most_common(8)
    P('  正文span字号直方图(top8)=%s （期望12.0为主，1.0=锚，9.0=页眉页脚，14/16=标题梯子）' % top_sz)
    P('  图文重叠bbox候选=%d %s' % (len(overlap_cand), overlap_cand[:8] if overlap_cand else ''))
    doc.close()
out.close()
print('DONE')
