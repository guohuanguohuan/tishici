# -*- coding: utf-8 -*-
"""探针：g5 素材 standalone——页宽/整页墨bbox/F_s/W_s 关系，找 56.56 与 55.08 的 1.48mm 差从哪来。"""
import sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
def load(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
aw = load('aw', '权威实测.py')
PT = aw.PT
for name in ('fig-image5-fold.pdf', 'tikz_tan6.pdf', 'img1_tikz.pdf'):
    p = pymupdf.open(aw.SRC + name)[0]
    clip = pymupdf.Rect(p.rect.x0 + .05, p.rect.y0 + .05, p.rect.x1 - .05, p.rect.y1 - .05)
    A = aw.ink_mask(p, clip)
    cs = aw.comps_rect(A, clip.x0, clip.y0, minpix=1, dilate=0)
    U = cs[0]
    for q in cs[1:]:
        U |= q
    print('%-28s 页 %.2f×%.2f  整页墨bbox %.2f×%.2f  域数 %d' % (
        name, p.rect.width / PT, p.rect.height / PT, U.width / PT, U.height / PT, len(cs)))
    stk = aw.strokes(p); cl = aw.clusters(stk)
    r = cl[0][0]
    for c in cl[1:]:
        r |= c[0]
    d = aw.measure_fig(p, stk, (r, sum(c[1] for c in cl), [i for c in cl for i in c[2]]),
                       aw.text_lines(p), labr=aw.LAB_R / (aw.MAP[5][2] / (p.rect.width / PT)), src=True)
    print('   W_s %.2f×%.2f @ x[%.2f,%.2f] y[%.2f,%.2f]' % (d['W'].width/PT, d['W'].height/PT, d['W'].x0/PT, d['W'].x1/PT, d['W'].y0/PT, d['W'].y1/PT))
    print('   F_s %.2f×%.2f @ x[%.2f,%.2f] y[%.2f,%.2f]  标签 %d' % (d['F'].width/PT, d['F'].height/PT, d['F'].x0/PT, d['F'].x1/PT, d['F'].y0/PT, d['F'].y1/PT, d['nlab']))
    for c in sorted(cs, key=lambda z: -z.width*z.height):
        if not d['F'].intersects(c):
            print('     F_s外墨块 mm x[%6.2f,%6.2f] y[%6.2f,%6.2f] w%5.2f h%5.2f' % (c.x0/PT,c.x1/PT,c.y0/PT,c.y1/PT,c.width/PT,c.height/PT))
    for L in d['labs']:
        print('     标签 %-6s bbox x[%6.2f,%6.2f] y[%6.2f,%6.2f] 墨 x[%6.2f,%6.2f] y[%6.2f,%6.2f] sz%.2f' % (
            L['t'][:5].replace('\n',''), L['bbox'].x0/PT, L['bbox'].x1/PT, L['bbox'].y0/PT, L['bbox'].y1/PT,
            L['ink'].x0/PT, L['ink'].x1/PT, L['ink'].y0/PT, L['ink'].y1/PT, L['sz']))
