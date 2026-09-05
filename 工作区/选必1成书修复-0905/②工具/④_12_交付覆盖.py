# -*- coding: utf-8 -*-
"""④轮步骤8b：成书交付 原位覆盖（12 件新导出 PDF）＋样章包重出前置留档。
①全件PDF：④轮 12 件 PDF 原位覆盖（改前件先 MD5 入 报告/④_交付MD5.json 的 before 段，
  覆盖后 MD5＝②工具 PDF对比/④轮PDF 同名件——字节等值断言）；未动 7 配页件不碰。
②整册/分本：④轮合册 产物（整册、本1..6、大分本×3、补白登记 json/md）原位覆盖同名件。
③样章：旧样章包/选页账/目检PNG → *_⑤留档 后由 ⑤_03_样章包.py 重出（步骤8c 独立跑）。
落盘 报告/④_交付MD5.json（before/after 全量）。"""
import io, sys, os, json, shutil, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
PDFO = os.path.join(BASE, 'PDF对比', '④轮PDF')
HE = os.path.join(BASE, 'PDF对比', '④轮合册')
DELIV = r'C:\提示词\工作区\选必1成书修复-0905\成书交付'
FULL = os.path.join(DELIV, '全件PDF')
ZC = os.path.join(DELIV, '整册')
FB = os.path.join(DELIV, '分本')
YANG = os.path.join(DELIV, '样章')
REP = os.path.join(BASE, '报告')
MD5LEDGER = os.path.join(REP, '④_交付MD5.json')
TWELVE = ['人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.pdf',
          '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.pdf',
          '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.pdf',
          '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.pdf',
          '人教B版选必1 第2章 平面解析几何·知识清单（完成）.pdf',
          '人教B版选必1 第2章 平面解析几何·衔接件（13题）.pdf',
          '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.pdf',
          '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.pdf',
          '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.pdf',
          '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.pdf',
          '人教B版选必1·使用说明.pdf',
          '人教B版选必1·册目录页.pdf']

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

ledger = json.load(open(MD5LEDGER, encoding='utf-8')) if os.path.exists(MD5LEDGER) else {}
ledger.setdefault('before', {})
ledger.setdefault('after', {})

# —— ①全件PDF 12 件原位覆盖 ——
for f in TWELVE:
    dst = os.path.join(FULL, f)
    ledger['before'][f] = md5(dst)
    shutil.copyfile(os.path.join(PDFO, f), dst)
    m_new = md5(dst)
    m_src = md5(os.path.join(PDFO, f))
    assert m_new == m_src, '%s 覆盖后 MD5 ≠ ④轮源' % f
    ledger['after'][f] = m_new
    print('全件PDF 覆盖 %-52s %s' % (f[:52], m_new[:12]))
print('全件PDF 12/12 原位覆盖＋MD5 等值', flush=True)

# —— ②整册/分本 原位覆盖 ——
MERGE_OUT = ['人教B版选必1·整册.pdf']
for i in range(1, 7):
    MERGE_OUT.append('人教B版选必1·本%d.pdf' % i)
MERGE_OUT += ['人教B版选必1·大分本-衔接本.pdf', '人教B版选必1·大分本-清单本.pdf',
              '人教B版选必1·大分本-讲练本.pdf', '人教B版选必1·合册补白登记.json',
              '人教B版选必1·合册补白登记.md']
for f in MERGE_OUT:
    src = os.path.join(HE, f)
    assert os.path.exists(src), '缺合册产物 %s' % f
    dst = os.path.join(FB if '整册' not in f else ZC, f)
    if os.path.exists(dst):
        ledger['before'].setdefault(f, md5(dst))
    shutil.copyfile(src, dst)
    ledger['after'][f] = md5(dst)
    print('覆盖 %-46s → %s' % (f[:46], '整册' if '整册' in f else '分本'))
print('整册/分本 %d 件原位覆盖' % len(MERGE_OUT), flush=True)

# —— ③样章留档（重出由 ⑤_03_样章包.py 在 ④_12 后单独跑） ——
moved = []
for name, arc in [('人教B版选必1·样章包.pdf', '人教B版选必1·样章包_⑤留档.pdf')]:
    src = os.path.join(YANG, name)
    dst = os.path.join(YANG, arc)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.move(src, dst)
        moved.append(arc)
src_json = os.path.join(DELIV, '_工作', '⑤_03_样章选页.json')
arc_json = os.path.join(DELIV, '_工作', '⑤_03_样章选页_⑤留档.json')
if os.path.exists(src_json) and not os.path.exists(arc_json):
    shutil.copyfile(src_json, arc_json)
    moved.append('⑤_03_样章选页_⑤留档.json')
png = os.path.join(YANG, '目检PNG')
png_arc = os.path.join(YANG, '目检PNG_⑤留档')
if os.path.isdir(png) and not os.path.isdir(png_arc):
    shutil.move(png, png_arc)
    moved.append('目检PNG_⑤留档/')
print('样章留档：%s' % (moved or '（已留档）'))

with open(MD5LEDGER, 'w', encoding='utf-8') as f:
    json.dump(ledger, f, ensure_ascii=False, indent=1)
print('④_12 交付覆盖完成；MD5 账本＝%s' % MD5LEDGER)
