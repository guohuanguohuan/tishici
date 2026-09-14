# -*- coding: utf-8 -*-
"""P1 目录页改版臂·编译后 PDF 文本层断言＋PNG 目验件（2026-09-14）
断言＝改版件 main.pdf（1 页）文本层：四本带在印、答案本族零残留、11 行起页序列逐行在印、
学史切片行与段注 1~54 在印。原印面 main-原印面.pdf 同法提层对照（旧值在原、新值在新）。
PNG＝150dpi 渲染 png/main-1.png（改版）＋png/原印面-1.png（对照）。
红线：写前核 mode（仅 P1目录页/ 树内）；零 git。
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding='utf-8')
BASE = Path(__file__).resolve().parent
NEW = BASE / 'main.pdf'
OLD = BASE / 'main-原印面.pdf'
PNGDIR = BASE / 'png'
ALLOWED = str(BASE.resolve())
for p in (PNGDIR,):
    assert str(p.resolve()).startswith(ALLOWED), f'写路径越界：{p}'

log = []
def say(s=''):
    print(s)
    log.append(s)

doc = pymupdf.open(NEW)
assert doc.page_count == 1, f'改版件页数 {doc.page_count} ≠ 1'
txt = doc[0].get_text('text')
flat = re.sub(r'\s+', '', txt)   # 去空白规范层（跨 span/空格拼接）
lines = [l.strip() for l in txt.splitlines() if l.strip()]

say('== P1 目录页改版件·PDF 文本层断言 ==')
say(f'页数＝{doc.page_count}（1 页，与原印面同构）')

# ---- ① 四本带在印＋答案本族零残留 ----
ok = True
for i, name in ((1, 'BOOKONE'), (2, 'BOOKTWO'), (3, 'BOOKTHREE'), (4, 'BOOKFOUR')):
    hit = name in flat and f'本{"一二三四"[i-1]}' in flat
    say(f'[{"PASS" if hit else "FAIL"}] 本{"一二三四"[i-1]}带＋{name} 在印')
    ok &= hit
for tok in ('BOOKFIVE', '本五', '答案本', '参考答案册', '208键'):
    hit = tok not in flat
    say(f'[{"PASS" if hit else "FAIL"}] 「{tok}」零残留')
    ok &= hit
assert ok

# ---- ② 11 行起页序列逐行在印（文本层行＝节号/题名/页码独立行；序贯扫描＝行序断言） ----
# 文本层形制（实测）：题名行（可拆多行）后随纯数字页码行；\tocpart 学史切片页列为「P1」非数字。
ROWS = [  # (行题名检索串, 链值起页)
    ('电荷', 1), ('库仑定律', 5), ('电场', 9), ('静电的防止与利用', 13), ('本章易错过关', 17),
    ('配套练习', 20), ('配套练习', 26), ('配套练习', 31), ('配套练习', 35),
    ('静电场拓展', 40), ('单元素养测评卷', 51),
]
ptr, seq_fail = 0, 0
for t, exp in ROWS:
    j = ptr
    while j < len(lines) and t not in lines[j]:
        j += 1
    if j >= len(lines):
        say(f'[FAIL] 行「{t}」题名未在印（自行{ptr}起扫描）')
        seq_fail += 1
        continue
    k = j + 1
    while k < len(lines) and not re.fullmatch(r'\d+', lines[k]):
        k += 1
    if k >= len(lines):
        say(f'[FAIL] 行「{t}」行尾页码未在印')
        seq_fail += 1
        continue
    got = int(lines[k])
    good = got == exp
    if not good:
        seq_fail += 1
    say(f'[{"PASS" if good else "FAIL"}] 行「{t}」页码行 {got}（链值 {exp}）')
    ptr = k + 1
assert seq_fail == 0, f'起页序列断言失败 {seq_fail} 行'
say('[PASS] 11 行起页序列逐行在印＝机核链值（1/5/9/13/17｜20/26/31/35｜40｜51），序＝装配序')

# ---- ③ 学史切片行＋段注链尾在印（注：~ 连字符文本层不落字，按空白折叠正则） ----
collapsed = re.sub(r'\s+', ' ', txt)
assert '物理学史切片' in flat, '学史切片行缺失'
assert '自成页码制起1' in collapsed, '学史切片小注缺失'
assert re.search(r'不入1\s*54\s*跨本链', collapsed), '学史切片小注链尾未更新为 1~54'
assert re.search(r'四本一串1\s*54', collapsed), '页码段注未更新为 1~54'
assert not re.search(r'五本一串1\s*48', collapsed), '旧段注「五本一串 1~48」残留'
assert not re.search(r'合计\s*48\s*页', collapsed), '旧合计 48 残留'
say('[PASS] 学史切片行在印零触碰；段注「四本一串 1~54」在印；旧「五本一串 1~48／合计 48 页」零残留')

# ---- ④ 原印面对照（旧答案本族在原、新页码仅在改版件） ----
old_doc = pymupdf.open(OLD)
assert old_doc.page_count == 1, '原印面页数≠1'
old_txt = old_doc[0].get_text('text')
old_flat = re.sub(r'\s+', '', old_txt)
old_collapsed = re.sub(r'\s+', ' ', old_txt)
assert '答案本' in old_flat and '参考答案册' in old_flat, '原印面应含答案本族（对照基线自检）'
assert '答案本' not in flat, '改版件答案本残留（与原印面对照）'
assert re.search(r'五本一串1\s*48', old_collapsed), '原印面段注应含 1~48（对照基线自检）'
say('[PASS] 原印面对照：答案本族/1~48 在原、零在改版件（对照基线自检双过）')

# ---- ⑤ PNG 目验件 ----
PNGDIR.mkdir(exist_ok=True)
doc[0].get_pixmap(dpi=150).save(PNGDIR / 'main-1.png')
old_doc[0].get_pixmap(dpi=150).save(PNGDIR / '原印面-1.png')
say('')
say(f'== 写出：png/main-1.png（改版）／png/原印面-1.png（对照），150dpi ==')

(BASE / '_PDF文本层断言.txt').write_text('\n'.join(log) + '\n', encoding='utf-8', newline='\n')
say('== 全部断言 PASS，读数入 _PDF文本层断言.txt ==')
