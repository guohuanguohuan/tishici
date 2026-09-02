# -*- coding: utf-8 -*-
"""RF修复轮 扫描：PDF侧全部页图片bbox（底边>阈值=侵入）＋图-图交叠＋页文本快照（供锚匹配）。
用法：python rf2_scan.py <tag>   （tag=base/fix1/fix2/fix3）
输出 JSON 到 输出\scan_<tag>.json 与控制台摘要。"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
import fitz

PDFDIR = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\PDF'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\输出'
CODES = ['X1','B','C','I2','E','F','G','H']
BODY_BOTTOM = 799.5   # 正文区底界（842-42.5）
TARGET = 797.0        # 修复目标（留2.5pt缓冲）
tag = sys.argv[1] if len(sys.argv) > 1 else 'base'

result = {}
for code in CODES:
    doc = fitz.open(os.path.join(PDFDIR, '%s_%s.pdf' % (code, tag)))
    pages = []
    intrude = []
    imgimg = []
    for pi in range(doc.page_count):
        page = doc[pi]
        # 页文本（去空白，供锚段文本匹配）
        txt = page.get_text().replace('\n', '')
        rects = []
        for img in page.get_images(full=True):
            for R in page.get_image_rects(img[0]):
                rects.append(R)
        # 图-图交叠
        for i in range(len(rects)):
            for j in range(i+1, len(rects)):
                inter = rects[i] & rects[j]
                if not inter.is_empty and inter.get_area() > 1:
                    imgimg.append((pi+1, round(inter.get_area(), 1),
                                   tuple(round(v, 1) for v in rects[i]), tuple(round(v, 1) for v in rects[j])))
        for R in rects:
            r = (round(R.x0, 1), round(R.y0, 1), round(R.x1, 1), round(R.y1, 1))
            pages.append({'p': pi+1, 'rect': r, 'txt': txt if not any(x['p'] == pi+1 and 'txt' in x for x in pages) else None})
            if R.y1 > BODY_BOTTOM:
                intrude.append({'p': pi+1, 'rect': r, 'bottom': round(R.y1, 1),
                                'w': round(R.width, 1), 'h': round(R.height, 1),
                                'shift': round(R.y1 - TARGET, 1)})
    result[code] = {'n_pages': doc.page_count, 'intrude': intrude, 'imgimg_overlap': imgimg,
                    'page_txt': {rec['p']: rec['txt'] for rec in pages if rec['txt'] is not None}}
    doc.close()

with open(os.path.join(OUT, 'scan_%s.json' % tag), 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
# 摘要
for code in CODES:
    r = result[code]
    print('=== %s 页数=%d 侵入图(bbox底>%.1f)=%d处 图图交叠=%d处' % (code, r['n_pages'], BODY_BOTTOM, len(r['intrude']), len(r['imgimg_overlap'])))
    for it in r['intrude']:
        print('   p%-3d rect=%s 底=%.1f 尺寸=%.1fx%.1f 需上移=%.1fpt' % (it['p'], it['rect'], it['bottom'], it['w'], it['h'], it['shift']))
print('DONE')
