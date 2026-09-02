# -*- coding: utf-8 -*-
"""RF修复轮 锚匹配＋几何勘察：
1) 锚段文本→PDF页定位（在页文本中检索锚段w:t前缀）；
2) 侵入图（底>784全量）按 页＋尺寸 匹配锚；
3) 对每个匹配：输出锚XML几何（relativeFrom/posOffset）＋页面上锚段文本首行bbox＋图rect＋
   图上下方文本线分布（预判上移后锚前正文覆盖风险）。
输出 输出\correlate.json ＋控制台报告。"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
import fitz

PDFDIR = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\PDF'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\输出'
CODES = ['X1','B','C','I2','E','F','G','H']
TARGET_BOTTOM = 784.0   # 实测页脚字形顶786.6（X1为788.9）→ 目标底784留2.6pt

def load(code):
    scans = json.load(open(os.path.join(OUT, 'scan_base.json'), encoding='utf-8'))[code]
    anchors = json.load(open(os.path.join(OUT, 'anchors_%s.json' % code), encoding='utf-8'))
    return scans, anchors

def find_page(ptxt, page_txt, hint_lo, hint_hi, npages):
    """锚段文本定位页：优先在hint窗口内找，找不到扩大。返回页号或None"""
    key = ptxt.strip()[:18]
    if not key: return None
    order = list(range(max(1, hint_lo), min(npages, hint_hi) + 1))
    order += [p for p in range(1, npages + 1) if p not in order]
    for p in order:
        if key in page_txt.get(str(p), ''):
            return p
    return None

for code in CODES:
    scans, anchors = load(code)
    page_txt = {int(k): v for k, v in scans['page_txt'].items()}
    npages = scans['n_pages']
    # 逐锚定页（顺序推进hint窗口）
    pages_of = {}
    lo = 1
    for a in anchors:
        p = find_page(a['para_txt'], page_txt, lo, lo + 2, npages)
        pages_of[a['idx']] = p
        if p: lo = p  # 后续锚在当前页或之后
    # 打开PDF取每页文本行bbox
    doc = fitz.open(os.path.join(PDFDIR, '%s_base.pdf' % code))
    def lines_of(pn):
        page = doc[pn-1]
        out = []
        for blk in page.get_text('dict')['blocks']:
            if blk['type'] != 0: continue
            for ln in blk['lines']:
                t = ''.join(sp['text'] for sp in ln['spans']).strip()
                if t:
                    out.append((round(ln['bbox'][1],1), round(ln['bbox'][3],1),
                                round(ln['bbox'][0],1), round(ln['bbox'][2],1), t[:26]))
        out.sort()
        return out
    def imgs_of(pn):
        page = doc[pn-1]
        rs = []
        for img in page.get_images(full=True):
            for R in page.get_image_rects(img[0]):
                rs.append(R)
        return rs
    # 侵入图（底>784）逐个匹配
    print('======== %s' % code)
    out = []
    for pn in range(1, npages+1):
        rs = imgs_of(pn)
        hits = [R for R in rs if R.y1 > TARGET_BOTTOM]
        if not hits: continue
        lines = lines_of(pn)
        for R in hits:
            w, h = round(R.width,1), round(R.height,1)
            cand = [a for a in anchors if abs(a['w_pt']-w) < 0.6 and abs(a['h_pt']-h) < 0.6
                    and (pages_of.get(a['idx']) in (pn-1, pn, pn+1, None))]
            rec = {'p': pn, 'rect': tuple(round(v,1) for v in R), 'w': w, 'h': h,
                   'bottom': round(R.y1,1), 'need_shift': round(R.y1 - TARGET_BOTTOM, 1),
                   'cands': []}
            for a in cand:
                pv = a['positionV'] or {}
                rec['cands'].append({'idx': a['idx'], 'name': a['docPr_name'], 'page': pages_of.get(a['idx']),
                                     'relV': pv.get('rel'), 'offV': pv.get('offset'),
                                     'para': a['para_txt'][:36]})
            # 页面文本线分布（供几何分析）
            above = [l for l in lines if l[1] <= R.y0 + 1]
            below = [l for l in lines if l[0] >= R.y1 - 1]
            inter = [l for l in lines if not (l[1] <= R.y0 or l[0] >= R.y1)]
            rec['last_line_above'] = above[-1] if above else None
            rec['first_line_below'] = below[0] if below else None
            rec['inter_lines'] = [{'y0': l[0], 'y1': l[1], 'x0': l[2], 'x1': l[3], 't': l[4]} for l in inter[:6]]
            rec['inter_n'] = len(inter)
            out.append(rec)
            print('p%-3d rect=%s 底=%.1f 需移%.1f | 锚候选%d %s' % (
                pn, rec['rect'], rec['bottom'], rec['need_shift'], len(rec['cands']),
                '；'.join('idx%s/%s页/off%s/%s' % (c['idx'], c['page'], c['offV'], c['name'][:8]) for c in rec['cands'])))
            if above: print('      上方末行 y%.1f-%.1f x%.0f-%.0f %r' % above[-1])
            if below: print('      下方首行 y%.1f-%.1f x%.0f-%.0f %r' % below[0])
            for il in rec['inter_lines']:
                print('      图内文本线 y%.1f-%.1f x%.0f-%.0f %r' % (il['y0'], il['y1'], il['x0'], il['x1'], il['t']))
    json.dump(out, open(os.path.join(OUT, 'correlate_%s.json' % code), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    doc.close()
print('DONE')
