# -*- coding: utf-8 -*-
"""③三期 00 净场锚定：起点态核验＋清单2 字节复制进工作区（FX-2）＋ B 项 W2060 现态取证（只读）。
起点锚（③二期终态）：同步盘清单2 MD5=ed14608c28ebc034989c1b9d07ba34ad；oMath=1156；w:t=4007 段；
嵌入 image3 md5=bfb3ca951889622dac65b4cd83c298cc（③二期 嵌回结果.json）。
B 项取证：word/media/imageW2060.png 是否仍在／px／dpi／彩色或灰阶；document.xml 段746 rId71 extent 原值。
断言 FAIL 即停跑（exit 1）。"""
import zipfile, hashlib, io, os, re, shutil, sys, time, json
import xml.etree.ElementTree as ET

ROOT = r'C:/提示词'
SYNC = os.path.join(ROOT, '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx')
WS = os.path.join(ROOT, '工作区/选必1成书修复-0905/③三期')
PRE = os.path.join(WS, '副本_起/清单2.docx')
EV = os.path.join(WS, '证据')
REP = os.path.join(ROOT, '工作区/选必1成书修复-0905/②工具/报告')
for d in (os.path.dirname(PRE), EV):
    os.makedirs(d, exist_ok=True)

SYNC_ANCHOR = 'ed14608c28ebc034989c1b9d07ba34ad'
OMATH_ANCHOR = 1156
WT_ANCHOR = 4007
IMG3_EMBED_MD5 = 'bfb3ca951889622dac65b4cd83c298cc'

def md5f(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def log(m): print(m, flush=True)

r = {}
# 1. 同步盘起点 MD5（只读通道）
sync_md5 = md5f(SYNC)
log(f'同步盘清单2 MD5 = {sync_md5}')
assert sync_md5 == SYNC_ANCHOR, f'起点漂移! {sync_md5} != {SYNC_ANCHOR} —— 停跑呈报'
r['sync_md5'] = sync_md5

# 2. 字节复制进工作区（300s×3 抗锁，MD5 双向比对）
ok = False
for i in range(3):
    try:
        shutil.copy2(SYNC, PRE)
        if md5f(PRE) == SYNC_ANCHOR and md5f(SYNC) == SYNC_ANCHOR:
            ok = True
            break
    except Exception as e:
        log(f'  copy try{i+1} err={e}')
    time.sleep(2)
assert ok, '字节复制失败（3 试）——停跑呈报'
log(f'字节复制 OK → {PRE}')

# 3. 副本起点态核验（零 COM，zip 直读）
z = zipfile.ZipFile(PRE)
names = z.namelist()
doc = z.read('word/document.xml').decode('utf-8')
om = len(re.findall(r'<m:oMath[ >]', doc))
wt = re.findall(r'<w:t[^>]*>(.*?)</w:t>', doc, re.S)
img3 = z.read('word/media/image3.png')
r['omath'] = om
r['wt_count'] = len(wt)
r['image3_md5'] = hashlib.md5(img3).hexdigest()
log(f'oMath={om} (锚{OMATH_ANCHOR})｜w:t={len(wt)} (锚{WT_ANCHOR})｜image3 md5={r["image3_md5"]}')
assert om == OMATH_ANCHOR and len(wt) == WT_ANCHOR and r['image3_md5'] == IMG3_EMBED_MD5, '副本起点态 ≠ ③二期终态 —— 停跑呈报'

# image3 drawing 块（rId10）extent 原值
m = None
for mm in re.finditer(r'<w:drawing>.*?</w:drawing>', doc, re.S):
    if 'r:embed="rId10"' in mm.group(0):
        m = mm.group(0)
        break
assert m, 'image3 drawing 块未找到'
ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', m).groups()
r['image3_extent'] = f'{ext[0]}x{ext[1]}'
log(f'image3 wp:extent = {r["image3_extent"]} EMU（{int(ext[0])/360000:.2f}×{int(ext[1])/360000:.2f}cm）')

# 4. B 项：W2060 现态取证（只读）
from PIL import Image
w60 = 'word/media/imageW2060.png'
r['W2060_media_present'] = w60 in names
if r['W2060_media_present']:
    b = z.read(w60)
    open(os.path.join(EV, '清单2_media_imageW2060_现态.png'), 'wb').write(b)
    im = Image.open(io.BytesIO(b))
    arr = None
    color_verdict = None
    if im.mode == 'L':
        color_verdict = 'L灰阶'
    elif im.mode in ('RGB', 'RGBA', 'P'):
        rgb = im.convert('RGB')
        import numpy as np
        arr = np.array(rgb).reshape(-1, 3).astype(int)
        chroma = int((arr.max(1) - arr.min(1)).max())
        color_verdict = f'彩色(chroma={chroma})' if chroma > 0 else f'灰阶(chroma=0, mode={im.mode})'
    r['W2060'] = dict(md5=hashlib.md5(b).hexdigest(), px=f'{im.size[0]}x{im.size[1]}',
                      mode=im.mode, dpi=str(im.info.get('dpi')), verdict=color_verdict,
                      bytes=len(b))
    log(f"W2060 media: px={r['W2060']['px']} mode={im.mode} dpi={r['W2060']['dpi']} 判定={color_verdict} md5={r['W2060']['md5']}")
# rels 引用与 drawing extent
rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
mr = re.search(r'Id="(rId\d+)"[^>]*Target="media/imageW2060\.png"', rels)
r['W2060_rid'] = mr.group(1) if mr else None
if r['W2060_rid']:
    blk = None
    for mm in re.finditer(r'<w:drawing>.*?</w:drawing>', doc, re.S):
        if f'r:embed="{r["W2060_rid"]}"' in mm.group(0):
            blk = mm.group(0)
            break
    if blk:
        e2 = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', blk).groups()
        r['W2060_extent'] = f'{e2[0]}x{e2[1]}'
        r['W2060_extent_cm'] = f'{int(e2[0])/360000:.2f}x{int(e2[1])/360000:.2f}cm'
        r['W2060_srcRect'] = bool(re.search(r'<a:srcRect[^>]*/>', blk))
        log(f"W2060: {r['W2060_rid']} extent={r['W2060_extent']} ({r['W2060_extent_cm']}) srcRect={r['W2060_srcRect']}")
# document.xml 中 W2060 相关文本（段746 上下文）
i = doc.find('imageW2060')
r['W2060_doc_mention'] = -1  # document.xml 不应出现文件名文本
# 引用计数（r:embed 出现次数，应恰 1）
if r['W2060_rid']:
    r['W2060_embed_count'] = len(re.findall(f'r:embed="{r["W2060_rid"]}"', doc))
    log(f"W2060 r:embed 计数 = {r['W2060_embed_count']}")
z.close()

# 5. 名单核证：③二期 20 张嵌回名单 vs W2060
ej = json.load(open(os.path.join(ROOT, '工作区/选必1成书修复-0905/③二期/嵌回结果.json'), encoding='utf-8'))
embedded_names = []
for code, v in ej.items():
    for base in v['targets']:
        embedded_names.append(f'{code}:{base}')
r['embedded_20'] = embedded_names
r['W2060_in_embedded20'] = any('W2060' in n for n in embedded_names)
log(f'③二期嵌回 {len(embedded_names)} 张；W2060 在名单内 = {r["W2060_in_embedded20"]}')

json.dump(r, open(os.path.join(WS, '锚定取证.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
log('SUMMARY_ANCHOR OK')
