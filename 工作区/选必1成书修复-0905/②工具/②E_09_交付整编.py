# -*- coding: utf-8 -*-
"""②E_09_交付整编.py — ②-E 全件 PDF 交付整编＋页数对照落账。
①巡检_②E/pdf/<代号>.pdf → PDF对比/②E终/<原文件名>.pdf（19件）；
②fitz 清点全 19 件页数 → 报告/②E_页数对照.md（十件对盖章记录/预期，配页件照实登记）。"""
import sys, io, os, shutil, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, '巡检_②E', 'pdf')
DST = os.path.join(HERE, 'PDF对比', '②E终')
os.makedirs(DST, exist_ok=True)

FILES19 = [
    ('清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）', 15),
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）', 15),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）', 65),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', 62),
    ('清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）', 32),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）', 5),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）', 58),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）', 58),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）', 47),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）', 73),
    ('TOC', '人教B版选必1·册目录页', None),
    ('SM', '人教B版选必1·使用说明', None),
    ('COVER', '人教B版选必1·封面', None),
    ('PF1X', '人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）', None),
    ('PF1Q', '人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）', None),
    ('PF1J', '人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）', None),
    ('PF2X', '人教B版选必1·部分封面（第2章 平面解析几何·衔接）', None),
    ('PF2Q', '人教B版选必1·部分封面（第2章 平面解析几何·清单）', None),
    ('PF2J', '人教B版选必1·部分封面（第2章 平面解析几何·讲练）', None),
]

ok = True
rows = []
for code, real, exp in FILES19:
    src = os.path.join(PDF, code + '.pdf')
    if not os.path.exists(src):
        print('!! 缺 %s.pdf' % code)
        ok = False
        continue
    d = fitz.open(src)
    n = d.page_count
    d.close()
    shutil.copy2(src, os.path.join(DST, real + '.pdf'))
    hit = (exp is None) or (n == exp)
    ok = ok and hit
    rows.append('| %s | %s | %s | %s |' % (code, real, n,
                ('预期%d %s' % (exp, 'PASS' if hit else '!!FAIL')) if exp is not None else '配页件（不计页口径）'))
    print('%-6s -> %d 页' % (code, n))
ten = sum(int(r.split('|')[3]) for r, (c, _f, e) in zip(rows, FILES19) if e is not None)
with open(os.path.join(HERE, '报告', '②E_页数对照.md'), 'w', encoding='utf-8') as f:
    f.write('# ②-E 全件 PDF 页数对照（fitz 清点；导出源＝副本_②E 盖章后态）\n\n'
            '| 代号 | 件 | 页数 | 判定 |\n|---|---|---|---|\n' + '\n'.join(rows)
            + '\n\n十件合计 %d 页（＝②-D 终报 T7 后 430 口径）；配页件 9 件不计页。\n'
              '交付 PDF：②工具\\PDF对比\\②E终\\（原文件名）；巡检工作副本：②工具\\巡检_②E\\pdf\\（代号）。\n' % ten)
print('TEN_SUM=%d  ALLOK=%s' % (ten, ok))
sys.exit(0 if ok and ten == 430 else 2)
