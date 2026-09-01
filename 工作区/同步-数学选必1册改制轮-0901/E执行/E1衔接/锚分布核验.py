# -*- coding: utf-8 -*-
# 一次性脚本（E1返工）：只读核验docx锚段分布——枚举wp:anchor宿主段落，统计每段锚数，
# 对同段≥2锚做XML级bbox推算（同段锚posOffset同位=叠放候选），输出分布表。
import sys, io, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

path = sys.argv[1]
z = zipfile.ZipFile(path)
root = etree.fromstring(z.read('word/document.xml'))
z.close()
body = root.find(q('body'))

EMU_CM = 360000.0
rows = []
for i, el in enumerate(body):
    if el.tag != q('p'):
        continue
    anchors = el.findall('.//' + '{%s}anchor' % WP)
    inlines = el.findall('.//' + '{%s}inline' % WP)
    if not anchors and not inlines:
        continue
    txt = ''.join(t.text or '' for t in el.iter(q('t')))
    info = []
    for an in anchors:
        ext = an.find('.//{%s}extent' % WP)
        ph = an.find('.//{%s}positionH//{%s}posOffset' % (WP, WP))
        pv = an.find('.//{%s}positionV//{%s}posOffset' % (WP, WP))
        behind = an.get('behindDoc')
        info.append({
            'extent_cm': [round(int(ext.get('cx')) / EMU_CM, 2), round(int(ext.get('cy')) / EMU_CM, 2)] if ext is not None else None,
            'posH': ph.text if ph is not None else '(align)',
            'posV': pv.text if pv is not None else '(align)',
            'behindDoc': behind,
        })
    rows.append({'body序': i, '锚数': len(anchors), 'inline数': len(inlines),
                 '段首文本': txt[:36], '锚明细': info})

multi = [r for r in rows if r['锚数'] >= 2]
print('含anchor段落数=%d｜含inline段落数=%d｜anchor总数=%d｜inline总数=%d' % (
    sum(1 for r in rows if r['锚数']), sum(1 for r in rows if r['inline数']),
    sum(r['锚数'] for r in rows), sum(r['inline数'] for r in rows)))
print('同段多锚段（≥2）数=%d' % len(multi))
print()
print('== 锚段分布表（body序/锚数/inline数/段首） ==')
for r in rows:
    flag = ' <<<多锚' if r['锚数'] >= 2 else ''
    print('[%d] 锚%d inline%d %s%s' % (r['body序'], r['锚数'], r['inline数'], r['段首文本'], flag))
print()
print('== 同段多锚几何核验（XML级bbox推算） ==')
ovl_total = 0
for r in multi:
    n = r['锚数']
    same_pos = all(x['posH'] == r['锚明细'][0]['posH'] and x['posV'] == r['锚明细'][0]['posV'] for x in r['锚明细'])
    w = [x['extent_cm'][0] for x in r['锚明细'] if x['extent_cm']]
    h = [x['extent_cm'][1] for x in r['锚明细'] if x['extent_cm']]
    inter_w, inter_h = (min(w), min(h)) if w and h else (0, 0)
    area = inter_w * inter_h
    ovl_total += 1
    print('段[%d] 锚%d 同位posOffset=%s 交叠框≈%.1f×%.1fcm（交叠面积%.1f cm²>0即叠放）段首=%r' % (
        r['body序'], n, same_pos, inter_w, inter_h, area, r['段首文本']))
    for x in r['锚明细']:
        print('    extent=%s posH=%s posV=%s behindDoc=%s' % (x['extent_cm'], x['posH'], x['posV'], x['behindDoc']))
print()
print('叠放候选段合计=%d' % ovl_total)
