# -*- coding: utf-8 -*-
"""_假红影像核.py — 残片键影像级人工核：按印面号定位 ansbook-true 页面，
裁「N.[答案] 起值区」渲染 PNG（zoom 2.5），供逐件目验「值确已印出＝假红」。"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '假红证据')
os.makedirs(OUT, exist_ok=True)

# 8 残片键：件｜键 → 值锚（取值内稳健 CJK/数字子串，用于定位 \ansitem 印面号）
KEYS = [
    ('导学件-课时02', '2章-拓-课时02-T2', '倾斜角'),
    ('导学件-课时13', '2章-练-课时13-难2', '被抓'),
    ('导学件-课时14', '2章-拓-课时14-33-7', '双曲线中'),
    ('导学件-课时17', '2章-练-课时17-11', '两个公共点：k∈'),
    ('导学件-课时19', '2章-练-课时19-16', '斜率范围'),
    ('练习件-课时13', '2章-练-课时13-难2', '被抓'),
    ('练习件-课时17', '2章-练-课时17-11', '两个公共点：k∈'),
    ('练习件-课时19', '2章-练-课时19-16', '斜率范围'),
]

RE_ITEM = re.compile(r'\\ansitem\{(\d+)\}\{')

manifest = []
for d, key, anchor in KEYS:
    val = json.load(open(os.path.join(HERE, d, '抽册读数.json'),
                         encoding='utf-8'))['册值快照'][key]
    tex = open(os.path.join(HERE, d, 'ansbook.tex'), encoding='utf-8').read()
    num = None
    for m in RE_ITEM.finditer(tex):
        seg = tex[m.start():tex.find('\\ansnote', m.start())]   # 值域＝ansitem→ansnote
        if anchor in seg:
            num = int(m.group(1))
            break
    assert num, '未定位印面号：%s %s' % (d, key)
    doc = fitz.open(os.path.join(HERE, d, 'ansbook-true.pdf'))
    hit = None
    for pg in doc:
        rs = pg.search_for('%d.[答案]' % num)
        if rs:
            hit = (pg, rs[0])
            break
    assert hit, '未寻 %s 印面 %d' % (d, num)
    pg, r = hit
    clip = fitz.Rect(r.x0 - 6, r.y0 - 4, pg.rect.x1 - 30, r.y1 + 58)
    pix = pg.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), clip=clip)
    png = os.path.join(OUT, '%s_%s_印面%d.png' % (d, key.split('-')[-1], num))
    pix.save(png)
    pageno = pg.number + 1
    doc.close()
    manifest.append({'件': d, '键': key, '印面号': num, '页': pageno,
                     '证据PNG': png.replace('\\', '/')})
    print('%s %s → 印面%d 页%d → %s' % (d, key, num, pageno,
                                        os.path.basename(png)))
json.dump(manifest, open(os.path.join(OUT, '_影像核清单.json'), 'w',
                         encoding='utf-8'), ensure_ascii=False, indent=1)
