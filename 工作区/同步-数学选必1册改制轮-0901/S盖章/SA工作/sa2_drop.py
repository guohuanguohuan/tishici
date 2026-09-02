# -*- coding: utf-8 -*-
"""SA任务1落成品：基线X1(fix7)/C(fix7) → 产出文件夹同名覆盖。
前置：①逐件hash记录（产出fix6态md5留链）；②C「零联动」预验——基线fix7与产出fix6全zip成员
      逐字节比对，预期仅document.xml不同（rf8_inline只改document.xml，页眉/页脚/settings未触碰）；
      ③覆盖后md5回读断言＝基线。"""
import hashlib, os, shutil, zipfile, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\基线'
OUT = r'C:\提示词\高中数学\高中数学同步'
HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = [
    ('X1', os.path.join(BASE, 'X1.docx'),
     os.path.join(OUT, '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx')),
    ('C', os.path.join(BASE, 'C.docx'),
     os.path.join(OUT, '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx')),
]

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

log = {'pre': {}, 'post': {}, 'member_diff': {}}
for code, src, dst in PAIRS:
    assert os.path.isfile(src) and os.path.isfile(dst)
    log['pre'][code] = md5(dst)
    # 成员级预验：基线fix7 vs 产出fix6+章
    with zipfile.ZipFile(src) as za, zipfile.ZipFile(dst) as zb:
        na, nb = za.namelist(), zb.namelist()
        assert na == nb, '%s 成员清单不同: %r vs %r' % (code, set(na) ^ set(nb))
        diff = [n for n in na if za.read(n) != zb.read(n)]
    log['member_diff'][code] = diff
    print('%s 覆盖前：产出md5=%s | 与基线fix7逐成员差异=%r' % (code, log['pre'][code], diff))
    assert diff == ['word/document.xml'], '%s 预验失败：差异成员=%r（预期仅document.xml）' % (code, diff)

for code, src, dst in PAIRS:
    shutil.copy2(src, dst)
    log['post'][code] = md5(dst)
    log['post'][code + '_基线'] = md5(src)
    print('%s 已覆盖 -> %s | 落盘md5=%s（=基线 %s）'
          % (code, os.path.basename(dst), log['post'][code], log['post'][code + '_基线']))
    assert log['post'][code] == log['post'][code + '_基线'], '%s 落盘md5≠基线' % code

json.dump(log, open(os.path.join(HERE, '落成品md5链.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('saved 落成品md5链.json')
