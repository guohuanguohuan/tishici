# -*- coding: utf-8 -*-
"""③三期 02 image3 修复重嵌：完全承 ③二期_01 范式（zip 级媒体替换＋零 COM）。
输入＝③三期\\副本_起\\清单2.docx（=③二期终态，MD5 锚 ed14608c28ebc034989c1b9d07ba34ad）；
新图＝③三期\\I2_image3_fix.png（重出自验已过）。
处置＝mode replace（清单2 image3 无 srcRect/rot，wp:extent 1095375×857250 原值零回流，
r:embed=rId10 原值）；画布比失配>1.5% 白边 letterbox 加画布（预期同 ③二期 → 437×342）。
六道硬断言：a)oMath=1156 对锚；b)w:t 4007 段零差；c)白名单外零 diff（本轮白名单仅 word/media/image3.png，
document.xml 与全部 rels 必须字节全等）；d)引用无悬空无孤儿；e)嵌入媒体灰阶+300dpi+等比；
f)wp:extent/rId 原值。输出＝③三期\\副本_后\\清单2.docx。FAIL 即停跑呈报。"""
import zipfile, hashlib, io, os, re, json
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(HERE, '副本_起/清单2.docx')
OUT = os.path.join(HERE, '副本_后/清单2.docx')
NEWPNG = os.path.join(HERE, 'I2_image3_fix.png')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

PRE_MD5_ANCHOR = 'ed14608c28ebc034989c1b9d07ba34ad'
OMATH_ANCHOR = 1156
TARGET = 'image3.png'
RID = 'rId10'
PAD_T = 0.015

def md5(b): return hashlib.md5(b).hexdigest()
def log(m): print(m, flush=True)

pre_bytes = open(PRE, 'rb').read()
assert md5(pre_bytes) == PRE_MD5_ANCHOR, f'副本起点 MD5 漂移 {md5(pre_bytes)}'
zin = zipfile.ZipFile(io.BytesIO(pre_bytes))
names = zin.namelist()
data = {n: zin.read(n) for n in names}
compress = {i.filename: i.compress_type for i in zin.infolist()}
doc_xml = data['word/document.xml']
rels_xml = data['word/_rels/document.xml.rels']

# 目标定位
blk = None
for m in re.finditer(r'<w:drawing>.*?</w:drawing>', doc_xml.decode('utf-8'), re.S):
    if f'r:embed="{RID}"' in m.group(0):
        blk = m.group(0); break
assert blk, 'image3 drawing 块未找到'
ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', blk).groups()
assert re.search(r'<a:srcRect[^>]*/>', blk) is None, '意外 srcRect'
assert 'rot=' not in blk and 'flip' not in blk, '意外 rot/flip'
paint_ratio = int(ext[0]) / int(ext[1])
log(f'wp:extent={ext[0]}x{ext[1]} paint_ratio={paint_ratio:.5f} srcRect=None rot/flip=无')

# 新图＋letterbox（承 ③二期 等比处置）
img_bytes = open(NEWPNG, 'rb').read()
delivered_md5 = md5(img_bytes)
im = Image.open(io.BytesIO(img_bytes))
dpi = im.info.get('dpi'); cw, ch = im.size
img_ratio = cw / ch
dev = abs(img_ratio - paint_ratio) / paint_ratio
padded = False
if dev > PAD_T:
    if img_ratio > paint_ratio:
        ncw, nch = cw, round(cw / paint_ratio)
    else:
        ncw, nch = round(ch * paint_ratio), ch
    canvas = Image.new(im.mode, (ncw, nch), (255, 255, 255))
    canvas.paste(im, ((ncw - cw) // 2, (nch - ch) // 2))
    buf = io.BytesIO(); canvas.save(buf, format='PNG', dpi=dpi)
    img_bytes = buf.getvalue(); padded = True
imf = Image.open(io.BytesIO(img_bytes))
ok_gray = None
a = np.array(imf).astype(int)
ok_gray = (imf.mode in ('L',) or (a[..., 3].min() == 255 and (a[..., :3].max(2) - a[..., :3].min(2)).max() == 0))
assert ok_gray, '嵌入媒体非灰阶'
dpi2 = imf.info.get('dpi'); assert dpi2 and abs(dpi2[0] - 300) < 1.5, f'dpi 异常 {dpi2}'
log(f'新图 {cw}x{ch} dev={dev*100:.2f}% padded={padded} → 嵌入 {imf.size[0]}x{imf.size[1]} dpi={dpi2}')

# 纯媒体替换（document.xml / rels 零改动）
expected_changed = {f'word/media/{TARGET}'}
data[f'word/media/{TARGET}'] = img_bytes

# 重组 zip（承 ③二期：原成员序/时间戳/压缩方式）
dt = {i.filename: i.date_time for i in zin.infolist()}
buf = io.BytesIO()
zout = zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED)
for n in names:
    zi = zipfile.ZipInfo(n, date_time=dt.get(n, (1980, 1, 1, 0, 0, 0)))
    zi.compress_type = compress.get(n, zipfile.ZIP_DEFLATED)
    zout.writestr(zi, data[n])
zout.close()
open(OUT, 'wb').write(buf.getvalue())

# ---- 六道断言（重开输出独立验证）----
zchk = zipfile.ZipFile(OUT)
chk = {n: zchk.read(n) for n in zchk.namelist()}
post_doc = chk['word/document.xml'].decode('utf-8')
# a) oMath 对锚
om = len(re.findall(r'<m:oMath[ >]', post_doc))
assert om == OMATH_ANCHOR == len(re.findall(r'<m:oMath[ >]', doc_xml.decode('utf-8'))), f'oMath {om}≠{OMATH_ANCHOR}'
# b) w:t 零差
wt_pre = re.findall(r'<w:t[^>]*>(.*?)</w:t>', doc_xml.decode('utf-8'), re.S)
wt_post = re.findall(r'<w:t[^>]*>(.*?)</w:t>', post_doc, re.S)
assert wt_pre == wt_post and len(wt_post) == 4007, 'w:t 差异!'
# c) 白名单外零 diff（document.xml/rels 必须字节全等）
pre_all = {n: md5(zin.read(n)) for n in names}
post_all = {n: md5(b) for n, b in chk.items()}
assert set(pre_all) == set(post_all), '成员增删!'
changed = {n for n in pre_all if pre_all[n] != post_all[n]}
assert changed == expected_changed, f'变更越界: {changed}'
assert chk['word/document.xml'] == doc_xml and chk['word/_rels/document.xml.rels'] == rels_xml, 'XML 非字节全等!'
# d) 引用无悬空无孤儿
rmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', chk['word/_rels/document.xml.rels'].decode('utf-8')))
media_members = {n.split('/')[-1] for n in chk if n.startswith('word/media/')}
rels_targets = {v.split('/')[-1] for v in rmap.values() if 'media/' in v}
assert not (rels_targets - media_members) and not (media_members - rels_targets), '孤儿/缺媒体!'
# e) 嵌入媒体复核（已上方 assert）＋ 与 ③二期嵌入件对照
z2 = zipfile.ZipFile(os.path.join(HERE, '../②工具/副本_③/清单2.docx'))
old_media = z2.read(f'word/media/{TARGET}'); z2.close()
assert md5(old_media) == 'bfb3ca951889622dac65b4cd83c298cc', '③二期嵌入件 md5 意外'
assert md5(img_bytes) != md5(old_media), '嵌入字节与 ③二期 相同（未生效?）'
# f) extent/rId 原值
blk3 = None
for m in re.finditer(r'<w:drawing>.*?</w:drawing>', post_doc, re.S):
    if f'r:embed="{RID}"' in m.group(0):
        blk3 = m.group(0); break
ext3 = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', blk3).groups()
assert f'{ext3[0]}x{ext3[1]}' == f'{ext[0]}x{ext[1]}', 'wp:extent 变动!'
ET.fromstring(chk['word/document.xml']); ET.fromstring(chk['word/_rels/document.xml.rels'])
zchk.close()

r = dict(pre_md5=PRE_MD5_ANCHOR, out_md5=md5(open(OUT, 'rb').read()),
         target=TARGET, rid=RID, wp_extent=f'{ext[0]}x{ext[1]}',
         delivered_md5=delivered_md5, delivered_px=f'{cw}x{ch}',
         embedded_md5=md5(img_bytes), embedded_px=f'{imf.size[0]}x{imf.size[1]}',
         padded=padded, dev_pct=round(dev * 100, 2), dpi=str(dpi2),
         omath=om, wt_count=len(wt_post), changed_members=sorted(changed))
r['old_embedded_md5_3二期'] = 'bfb3ca951889622dac65b4cd83c298cc'
json.dump(r, open(os.path.join(HERE, '嵌回结果.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
log(f"六道断言全 PASS: oMath={om} w:t={len(wt_post)} changed={sorted(changed)}")
log(f"副本后 MD5 = {r['out_md5']}")
log('SUMMARY_EMBED OK')
