# -*- coding: utf-8 -*-
"""③三期 04 回写清单2：承 ③二期_05 范式（FX-2：同步盘零直开零直写通道外无操作；
抗锁 copy2 300s×3；MD5 双向比对；回写后同步盘零 COM 终验）。
断言 FAIL 即停跑呈报，不硬闯。"""
import zipfile, hashlib, io, os, re, shutil, time, json

ROOT = r'C:/提示词'
SRC = os.path.join(ROOT, '工作区/选必1成书修复-0905/③三期/副本_后/清单2.docx')
DST = os.path.join(ROOT, '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx')
PRE_SYNC_MD5 = 'ed14608c28ebc034989c1b9d07ba34ad'   # 回写前同步盘（=③二期终态）
SRC_MD5_EXPECT = '319438647184ae45e3644b5adbff1e11'  # ③三期 副本_后
IMG3_NEW = None  # 填充自副本
OMATH_ANCHOR = 1156
LINK = {'人教B版选必1·册目录页.docx': 'b5c2bbda6f173f185f3d69a2080042f6',
        '人教B版选必1·装订单.md': 'd59e6a52bd8bf2d65e96be567a5eb9fb'}

def md5f(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
def log(m): print(m, flush=True)

r = {}
assert md5f(SRC) == SRC_MD5_EXPECT, f'副本_后 MD5 漂移 {md5f(SRC)}'
z = zipfile.ZipFile(SRC); IMG3_NEW = hashlib.md5(z.read('word/media/image3.png')).hexdigest()
foot_src = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/footer')}
doc_src = z.read('word/document.xml'); z.close()
r['src_md5'] = md5f(SRC); r['image3_embedded_md5'] = IMG3_NEW

pre = md5f(DST)
assert pre == PRE_SYNC_MD5, f'回写前同步盘漂移 {pre} —— 停跑呈报'
r['pre_md5'] = pre
log(f'回写前同步盘 MD5 = {pre}（锚相符）')

# 抗锁回写（copy2 → 读回 MD5 判成功；300s×3 语义＝3 试）
ok = False
for i in range(3):
    try:
        shutil.copy2(SRC, DST)
        if md5f(DST) == SRC_MD5_EXPECT:
            ok = True; break
        log(f'  try{i+1} 读回 MD5 不等，重试')
    except Exception as e:
        log(f'  try{i+1} err={e}')
    time.sleep(2)
assert ok, '回写 3 试未成功 —— 停跑呈报'
r['post_md5'] = md5f(DST)
log(f'回写后同步盘 MD5 = {r["post_md5"]}（＝副本源 {SRC_MD5_EXPECT}）')

# 回写后同步盘终验（零 COM）
z = zipfile.ZipFile(DST)
doc = z.read('word/document.xml')
om = len(re.findall(r'<m:oMath[ >]', doc.decode('utf-8')))
img3 = hashlib.md5(z.read('word/media/image3.png')).hexdigest()
foot_post = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/footer')}
ext = None
for m in re.finditer(r'<w:drawing>.*?</w:drawing>', doc.decode('utf-8'), re.S):
    if 'r:embed="rId10"' in m.group(0):
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', m.group(0)).groups(); break
z.close()
assert om == OMATH_ANCHOR, f'oMath {om}≠{OMATH_ANCHOR}'
assert img3 == IMG3_NEW, '同步盘 image3 ≠ 新嵌入件'
assert doc == doc_src, 'document.xml 与副本源不等'
assert foot_post == foot_src, 'footer 字节漂移'
foot_txt = None
z = zipfile.ZipFile(DST)
for n in z.namelist():
    if n.startswith('word/footer'):
        t = z.read(n).decode('utf-8', 'ignore')
        mm = re.search(r'（共\d+页）[^<]*', t)
        if mm:
            foot_txt = f'{n}: {mm.group(0)}'
z.close()
r.update(omath=om, image3_md5=img3, wp_extent=f'{ext[0]}x{ext[1]}',
         footer_md5_equal=True, footer_sample=foot_txt)
log(f'终验: oMath={om}｜image3 md5={img3[:8]}…｜extent={ext[0]}x{ext[1]}｜footer 同串={foot_txt}')

# 联动件零动核对（只读 MD5）
sync_dir = os.path.dirname(DST)
root_dir = os.path.join(ROOT, '高中数学/高中数学同步')
link_r = {}
for fn, anchor in LINK.items():
    p = os.path.join(root_dir, fn)
    got = md5f(p) if os.path.exists(p) else None
    link_r[fn] = dict(md5=got, anchor=anchor, equal=got == anchor)
    assert got == anchor, f'联动件 {fn} 漂移! —— 停跑呈报'
r['联动件'] = link_r
log('联动件 册目录页/装订单 MD5 全等（零动）')

json.dump(r, open(os.path.join(ROOT, '工作区/选必1成书修复-0905/③三期/回写结果.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
log('SUMMARY_WRITEBACK ALLOK = True')
