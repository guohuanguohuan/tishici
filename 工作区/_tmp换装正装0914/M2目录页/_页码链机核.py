# -*- coding: utf-8 -*-
"""M2 目录页改版臂·页码链机核（2026-09-14）
义务＝义务总表 §一.4：删「本四 答案本/BOOK FOUR」章带＋\\tocans 行；
页码链以换装件实测页数（印本档 PDF 实数）机核回填：行页码＝跨本连续累计起页、
合计＝Σ件页数；本数口径四本→三本。禁手编：全部数字由脚本从 PDF 实数计算写入。
红线：零 git；M2 正件只读；写入仅 M2目录页/ 树内（前缀断言）。
读入＝main.src.tex（原面快照）；写出＝main.tex（改版件）＋_页码链断言.txt＋_diff登记.txt。
"""
import re
import sys
import difflib
from pathlib import Path

import fitz  # pymupdf

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent
TREE = BASE.parent          # _tmp换装正装0914
SRC_TEX = BASE / 'main.src.tex'
DST_TEX = BASE / 'main.tex'
OUT_ASSERT = BASE / '_页码链断言.txt'
OUT_DIFF = BASE / '_diff登记.txt'

# ---- 写前核 mode：写路径必须全部落在允许根内 ----
ALLOWED = [str(BASE.resolve())]
for p in (DST_TEX, OUT_ASSERT, OUT_DIFF):
    rp = str(p.resolve())
    assert any(rp.startswith(a) for a in ALLOWED), f'写路径越界：{rp}'

# ---- 件账清单：顺序＝目录行序＝装配序；exp＝报告在账页数（机核交叉用） ----
# (本, 件, true档PDF相对TREE路径, 报告在账页数, 行宏, 行首参精确值, 行题名精确值)
MANIFEST = [
    # 本一 导学本（12 件；波1 件账 true 列）
    ('导学本', '课时01',      'M2导学本/课时01/main-true.pdf',      4, 'toclink',  '第1课时', '空间向量的概念及线性运算（含1.1.1前衔接）'),
    ('导学本', '课时02',      'M2导学本/课时02/main-true.pdf',      3, 'toclesson', '2', '空间向量的数量积'),
    ('导学本', '课时03',      'M2导学本/课时03/main-true.pdf',      3, 'toclesson', '3', '空间向量基本定理'),
    ('导学本', '课时04',      'M2导学本/课时04/main-true.pdf',      4, 'toclesson', '4', '空间直角坐标系与空间向量的坐标'),
    ('导学本', '课时05',      'M2导学本/课时05/main-true.pdf',      4, 'toclesson', '5', '空间向量运算的坐标表示'),
    ('导学本', '衔接节-1.2.1前', 'M2导学本/衔接节-1.2.1前/main-true.pdf', 5, 'toclink', '衔\\,\\,接', '初等几何必会（1.2.1前）'),
    ('导学本', '课时06',      'M2导学本/课时06/main-true.pdf',      4, 'toclesson', '6', '空间中的点、直线与空间向量'),
    ('导学本', '课时07',      'M2导学本/课时07/main-true.pdf',      4, 'toclesson', '7', '空间中的平面与空间向量'),
    ('导学本', '课时08',      'M2导学本/课时08/main-true.pdf',      4, 'toclesson', '8', '直线与平面的夹角'),
    ('导学本', '课时09',      'M2导学本/课时09/main-true.pdf',      4, 'toclesson', '9', '二面角'),
    ('导学本', '课时10',      'M2导学本/课时10/main-true.pdf',      4, 'toclesson', '10', '空间中的距离'),
    ('导学本', '章末-本章总结提升', 'M2导学本/章末-本章总结提升/main-true.pdf', 8, 'toczong', '本章总结提升', ''),
    # 本二 练习本（12 件；波2 报告 页数行 true 列）
    ('练习本', '课时01', 'M2练习本/课时01/main-true.pdf', 3, 'toclesson', '1', '配套练习'),
    ('练习本', '课时02', 'M2练习本/课时02/main-true.pdf', 2, 'toclesson', '2', '配套练习'),
    ('练习本', '课时03', 'M2练习本/课时03/main-true.pdf', 3, 'toclesson', '3', '配套练习'),
    ('练习本', '课时04', 'M2练习本/课时04/main-true.pdf', 3, 'toclesson', '4', '配套练习'),
    ('练习本', '课时05', 'M2练习本/课时05/main-true.pdf', 3, 'toclesson', '5', '配套练习'),
    ('练习本', '课时06', 'M2练习本/课时06/main-true.pdf', 3, 'toclesson', '6', '配套练习'),
    ('练习本', '课时07', 'M2练习本/课时07/main-true.pdf', 3, 'toclesson', '7', '配套练习'),
    ('练习本', '课时08', 'M2练习本/课时08/main-true.pdf', 3, 'toclesson', '8', '配套练习'),
    ('练习本', '课时09', 'M2练习本/课时09/main-true.pdf', 3, 'toclesson', '9', '配套练习'),
    ('练习本', '课时10', 'M2练习本/课时10/main-true.pdf', 3, 'toclesson', '10', '配套练习'),
    ('练习本', '上册', 'M2练习本/上册/main-true.pdf', 6, 'toclink', '拓展册', '上册'),
    ('练习本', '下册', 'M2练习本/下册/main-true.pdf', 15, 'toclink', '拓展册', '下册'),
    # 本三 测评本（3 件；波3 案B 印本档 main.pdf）
    ('测评本', '测评卷', 'M2测评滚动/测评卷/main.pdf', 4, 'toclink', '测评卷', '单元素养测评卷（一）·第一章'),
    ('测评本', '滚动卷A', 'M2测评滚动/滚动卷A/main.pdf', 3, 'toclink', '滚动卷', 'A\\quad 第一章（1.1.1～1.1.3）'),
    ('测评本', '滚动卷B', 'M2测评滚动/滚动卷B/main.pdf', 3, 'toclink', '滚动卷', 'B\\quad 第一章（全章）'),
]

ROW_RE = re.compile(r'^\\toc(link|lesson)\{([^{}]*)\}\{([^{}]*)\}\{(\d+)\}$')
ZONG_RE = re.compile(r'^\\toczong\{([^{}]*)\}\{(\d+)\}$')  # \toczong 为两参宏（件标＋页码）
log = []

def parse_row(s):
    """行 → (macro, a1, a2, 页码)；zong 归一为 a2=''。宏名统一带 toc 前缀。"""
    m = ROW_RE.match(s)
    if m:
        return ('toc' + m.group(1), m.group(2), m.group(3), int(m.group(4)))
    m = ZONG_RE.match(s)
    if m:
        return ('toczong', m.group(1), '', int(m.group(2)))
    return None

def build_row(macro, a1, a2, page):
    if macro == 'toczong':
        return '\\toczong{' + a1 + '}{' + str(page) + '}'
    return '\\' + macro + '{' + a1 + '}{' + a2 + '}{' + str(page) + '}'

def say(s=''):
    print(s)
    log.append(s)

# ============ ① 实测页数（PDF 实数）＋与报告在账交叉断言 ============
say('== ① 换装件实测页数（印本档 PDF 实数·pymupdf）与报告在账交叉断言 ==')
pages = []
fail = 0
for book, piece, rel, exp, macro, a1, a2 in MANIFEST:
    pdf = TREE / rel
    if not pdf.exists():
        say(f'[FAIL] 缺 PDF：{pdf}')
        fail += 1
        continue
    n = fitz.open(pdf).page_count
    ok = 'PASS' if n == exp else 'FAIL'
    if n != exp:
        fail += 1
    say(f'[{ok}] {book}/{piece} PDF实数={n} 报告在账={exp}  ({rel})')
    pages.append(n)
assert fail == 0, f'页数断言失败 {fail} 件（实数≠在账或缺件），禁手编终止'
assert len(pages) == 27

BOOKS = ['导学本', '练习本', '测评本']
book_sum = {b: sum(n for n, (b2, *_ ) in zip(pages, MANIFEST) if b2 == b) for b in BOOKS}
total = sum(pages)
say(f'本合计：导学 {book_sum["导学本"]}／练习 {book_sum["练习本"]}／测评 {book_sum["测评本"]}，Σ件页数＝{total}')

# ============ ② 源面 27 行定位＋签名逐件断言（对集合不对数口径） ============
say('')
say('== ② 源面目录行签名逐件断言（27 行·序＝件账序） ==')
src_lines = SRC_TEX.read_text(encoding='utf-8').splitlines()
rows_src = []  # (macro, a1, a2, 旧页码)
for ln in src_lines:
    r = parse_row(ln.strip())
    if r:
        rows_src.append(r)
assert len(rows_src) == 27, f'源面目录行数 {len(rows_src)} ≠ 27'
sig_fail = 0
for (macro, a1, a2, old), (book, piece, rel, exp, emacro, ea1, ea2) in zip(rows_src, MANIFEST):
    if not ((macro == emacro) and (a1 == ea1) and (a2 == ea2)):
        sig_fail += 1
        say(f'[FAIL] 行签名不匹配：面=({macro},{a1},{a2}) 账=({emacro},{ea1},{ea2})')
if sig_fail == 0:
    say('[PASS] 27/27 行签名逐件精确匹配（宏名＋首参＋题名全等，序＝件账装配序）')
else:
    raise SystemExit(f'签名断言失败 {sig_fail} 行')

# ============ ③ 跨本连续累计起页（行页码＝跨本累计起页） ============
say('')
say('== ③ 跨本连续累计起页（行页码＝累计起页；合计＝Σ件页数） ==')
starts, cum = [], 1
book_start = {}
for n, (book, *_ ) in zip(pages, MANIFEST):
    if book not in book_start:
        book_start[book] = cum
    starts.append(cum)
    cum += n
book_end = {b: book_start[b] + book_sum[b] - 1 for b in BOOKS}
for b in BOOKS:
    say(f'{b}：{book_start[b]}-{book_end[b]}（{book_sum[b]} 页）→ 次本起页 {book_end[b] + 1}')
say(f'合计 {total} 页（末件末页 {starts[-1] + pages[-1] - 1}）')
assert book_start['练习本'] == book_sum['导学本'] + 1
assert book_start['测评本'] == book_sum['导学本'] + book_sum['练习本'] + 1
assert starts[-1] + pages[-1] - 1 == total
assert starts[0] == 1

# ============ ④ 删答案本章带＋tocans 行（含死宏，一次定位·降序删） ============
say('')
say('== ④ 删「本四 答案本/BOOK FOUR」章带＋\\tocans 行 ==')
new_lines = list(src_lines)
del_idx = []
for i, ln in enumerate(new_lines):
    if '\\tocchapter{04}' in ln or re.match(r'^\\tocans\{', ln.strip()):
        del_idx.append(i)
assert len(del_idx) == 2, f'章带/tocans 行定位数 {len(del_idx)} ≠ 2'
band, tocans_i = del_idx
assert tocans_i == band + 2, 'tocans 行与章带不邻接'
assert new_lines[band - 1].strip() == '\\vspace{6.60mm}' and new_lines[band + 1].strip() == '\\vspace{-3.29mm}', '章带块上下文不符'
mac_i = next(i for i, ln in enumerate(new_lines) if ln.startswith('\\newcommand{\\tocans}'))
for i in sorted([mac_i, band - 1, band, band + 1, tocans_i], reverse=True):
    say(f'[删行] 原{i+1}: {new_lines[i].strip()[:76]}')
    del new_lines[i]
say('[删行·义务外附带清理] \\tocans 宏定义死代码 1 行（上列首条）')
assert not any('\\tocans{' in ln for ln in new_lines), 'tocans 用法/定义残留'

# ============ ⑤ 行页码回填（27 行·机核写入，重扫定址防漂移） ============
say('')
say('== ⑤ 行页码回填（27 行，禁手编·脚本写入） ==')
rows_new = []
for i, ln in enumerate(new_lines):
    r = parse_row(ln.strip())
    if r:
        rows_new.append((i,) + r)
assert len(rows_new) == 27
assert [(a, b, c, d) for _, a, b, c, d in rows_new] == rows_src, '删带后行集/序/旧页码漂移'
for k, (i, macro, a1, a2, old) in enumerate(rows_new):
    new_ln = build_row(macro, a1, a2, starts[k])
    assert parse_row(new_ln) == (macro, a1, a2, starts[k]), f'回填行自洽断言失败 行{i+1}'
    say(f'[改行] {macro} {a1}｜{a2[:16]}｜页码 {old} → {starts[k]}')
    new_lines[i] = new_ln

# ============ ⑥ 头部注释改行（页码链合计行＋三本口径）＋改版横幅 ============
say('')
say('== ⑥ 头部注释改行（页码链合计行＋三本口径）＋改版横幅 ==')
old_chain_a = '% 页码链：导学本 1-44／练习本 45-82（练习 45-64＋拓展上 65-69＋拓展下 70-82）／'
old_chain_b = '%         测评本 83-89／答案本 90-103，合计 103 页。'
i_a = new_lines.index(old_chain_a)
assert new_lines[i_a + 1] == old_chain_b, '页码链注释第二行不符'
new_chain_a = f'% 页码链（2026-09-14 改版机核回填·印本档实测）：导学本 {book_start["导学本"]}-{book_end["导学本"]}／练习本 {book_start["练习本"]}-{book_end["练习本"]}／'
new_chain_b = (f'%         测评本 {book_start["测评本"]}-{book_end["测评本"]}（测评卷 {starts[24]}-{starts[24]+pages[24]-1}＋滚动卷A {starts[25]}-{starts[25]+pages[25]-1}'
               f'＋滚动卷B {starts[26]}-{starts[26]+pages[26]-1}），合计 {total} 页（三本，Σ件页数）。')
say(f'[改行] 原{i_a+1} 页码链行1（导学/练习段）→ 新链')
say(f'[改行] 原{i_a+2} 页码链行2（测评/答案段·合计）→ 新链（合计 {total}）')
new_lines[i_a:i_a + 2] = [new_chain_a, new_chain_b]

old4_a = '%   ①页眉小字「导学案」→「套装目录」；②分节单元＝四本（本一导学本／本二练习本／本三测评本／'
old4_b = '%   本四答案本），复用 \\tocchapter 章带（01~04＋BOOK ONE~FOUR）；'
i4 = new_lines.index(old4_a)
assert new_lines[i4 + 1] == old4_b, '四本口径注释第二行不符'
new4_a = '%   ①页眉小字「导学案」→「套装目录」；②分节单元＝三本（本一导学本／本二练习本／本三测评本，'
new4_b = '%   2026-09-14 改版删本四答案本带），复用 \\tocchapter 章带（01~03＋BOOK ONE~THREE）；'
say(f'[改行] 原{i4+1} 四本口径行1 → 三本口径')
say(f'[改行] 原{i4+2} 四本口径行2 → 三本口径（01~03）')
new_lines[i4:i4 + 2] = [new4_a, new4_b]

for i, ln in enumerate(new_lines):
    if '第 2 页：本三 测评本＋本四 答案本' in ln:
        new_lines[i] = ln.replace('第 2 页：本三 测评本＋本四 答案本（4 行＋2 带）',
                                  '第 2 页：本三 测评本（3 行＋1 带；本四答案本带 2026-09-14 改版删除）')
        say(f'[改行] 原{i+1} 页2段注 → 三本口径')

banner = [
    '% ============================================================',
    '% M2 第1章 套装册目录页·改版件（2026-09-14，换装轮目录页改版臂·四本→三本收官）',
    '% 义务＝义务总表 §一.4：删「本四 答案本/BOOK FOUR」章带＋\\tocans 行；页码链以换装件',
    '%   实测页数机核回填（行页码＝跨本连续累计起页、合计＝Σ件页数，脚本 _页码链机核.py）。',
    '% 原面快照＝main.src.tex；断言读数＝_页码链断言.txt；删行/改行逐条＝_diff登记.txt。',
    '% ============================================================',
]
new_lines = banner + new_lines
say(f'[增行] 改版横幅 {len(banner)} 行（注释层注记）')

# ============ ⑦ 生成面后断言 ============
say('')
say('== ⑦ 生成面后断言 ==')
txt = '\n'.join(new_lines) + '\n'
body_txt = '\n'.join(new_lines[len(banner):])   # 残留断言只对正文（横幅＝义务注记引述，不计）
strip_note = body_txt.replace('本四答案本带 2026-09-14 改版删除', '').replace('改版删本四答案本带', '')
assert 'BOOK FOUR' not in body_txt, 'BOOK FOUR 残留'
assert '本四' not in strip_note, '本四 残留（注记白名单外）'
assert '\\tocans{' not in body_txt and '参考答案册' not in body_txt, 'tocans/参考答案册 残留'
n_band = txt.count('\\tocchapter{0')
assert n_band == 3, f'章带数 {n_band} ≠ 3'
for tag in ('01', '02', '03'):
    assert ('\\tocchapter{' + tag + '}') in txt, f'缺章带 {tag}'
rows2 = [r for r in (parse_row(l.strip()) for l in new_lines) if r]
assert len(rows2) == 27
got = [r[3] for r in rows2]
assert got == starts, f'回填页码序列不符：{got} ≠ {starts}'
say(f'[PASS] 章带 01-03 三本；目录行 27；页码序列＝累计起页序列（{starts[0]}…{starts[-1]}）；答案本残留 0')
t_src = [r[2] for r in rows_src]
t_new = [r[2] for r in rows2]
assert t_src == t_new, '行题名漂移'
say('[PASS] 27 行题名对原快照逐条全等（零漂移·仅页码列变更）')

# ============ ⑧ 写出（前缀断言后） ============
DST_TEX.write_text(txt, encoding='utf-8', newline='\n')
OUT_ASSERT.write_text('\n'.join(log) + '\n', encoding='utf-8', newline='\n')

# ============ ⑨ diff 登记（删行/改行逐条） ============
d = []
d.append('# _diff登记.txt — M2 目录页改版 vs 原面快照（机核生成 2026-09-14）')
d.append('')
d.append('原面＝main.src.tex（正件逐字节拷贝）；改版＝main.tex（行号含头部 6 行横幅）。分类：[删行]/[改行]/[增行]（增行仅注释横幅）。')
d.append('')
body = new_lines[len(banner):]
sm = difflib.SequenceMatcher(None, src_lines, body, autojunk=False)
n_del = n_chg = n_add = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        continue
    if tag == 'delete':
        for k in range(i1, i2):
            d.append(f'[删行] 原{k+1}: {src_lines[k]}')
            n_del += 1
    elif tag == 'replace':
        for k in range(max(i2 - i1, j2 - j1)):
            if i1 + k < i2 and j1 + k < j2:
                d.append(f'[改行] 原{i1+k+1} → 新{j1+k+1+len(banner)}')
                d.append(f'  - {src_lines[i1 + k]}')
                d.append(f'  + {body[j1 + k]}')
                n_chg += 1
            elif i1 + k < i2:
                d.append(f'[删行] 原{i1+k+1}: {src_lines[i1 + k]}')
                n_del += 1
            else:
                d.append(f'[增行] 新{j1+k+1+len(banner)}: {body[j1 + k]}')
                n_add += 1
    elif tag == 'insert':
        for k in range(j1, j2):
            d.append(f'[增行] 新{k+1+len(banner)}: {body[k]}')
            n_add += 1
d.append('')
d.append(f'合计：删 {n_del} 行（含义务外附带 \\tocans 死宏 1 行）／改 {n_chg} 行／增 {n_add} 行（注释横幅）。')
OUT_DIFF.write_text('\n'.join(d) + '\n', encoding='utf-8', newline='\n')
say('')
say(f'== 写出完成：main.tex（{len(new_lines)}行）／_页码链断言.txt／_diff登记.txt（删{n_del} 改{n_chg} 增{n_add}） ==')
