# -*- coding: utf-8 -*-
"""刷台账.py — M3 S2 波1 补位臂3·09/14 片目录台账指纹刷新（复跑验证后同步）。
重编（双档各两遍）后 PDF md5 必变（内嵌时间戳）；items/渲染注记/口径全fields承原账零改动，
仅刷：指纹两 PDF md5＋双档读数＋门谱 gen 戳；件manifest.件指纹 同步。
写前核：main.tex.md5 必须与原账一致（源零改动才许刷）；不一致即中止零写。
唯一写域：两片目录的 值台账-课时NN.json ＋ 件manifest.json。
"""
import hashlib
import io
import json
import os
import sys

import fitz

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DAO = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件'
JOBS = {
    '09': ('课时09-圆与圆的位置关系', 21, 'true 0错0溢0under0缺字 ANSKEY=21 5页；false 同 3页'),
    '14': ('课时14-2.6.2双曲线性质', 71, 'true 0错0溢0under0缺字 ANSKEY=71 18页；false 同 8页'),
}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

for k, (dirn, nkey, reads) in JOBS.items():
    piece = os.path.join(DAO, dirn)
    led_path = os.path.join(piece, f'值台账-课时{k}.json')
    man_path = os.path.join(piece, '件manifest.json')
    led = json.load(open(led_path, encoding='utf-8'))
    man = json.load(open(man_path, encoding='utf-8'))
    cur_tex = md5(os.path.join(piece, 'main.tex'))
    if led['指纹']['main.tex.md5'] != cur_tex:
        print(f'[ABORT] 课时{k} main.tex md5 漂移，源有改动，零写回')
        sys.exit(1)
    led['指纹']['main-true.pdf.md5'] = md5(os.path.join(piece, 'main-true.pdf'))
    led['指纹']['main-false.pdf.md5'] = md5(os.path.join(piece, 'main-false.pdf'))
    led['指纹']['双档读数'] = reads
    led['门谱'] = [s + '（补位臂3 2026-09-14 复跑全绿）' if '（全绿）' in s else s for s in led['门谱']]
    led['gen'] = (led['gen'] + '；补位臂3 2026-09-14 门谱全项复跑验证＋指纹刷新（items 零改动承原账）')
    man['件指纹'] = dict(led['指纹'])
    json.dump(led, open(led_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(man, open(man_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'[OK] 课时{k} 指纹刷新：true {led["指纹"]["main-true.pdf.md5"][:12]}… '
          f'false {led["指纹"]["main-false.pdf.md5"][:12]}…；items {len(led["items"])} 键零改动')
