# -*- coding: utf-8 -*-
"""P1 目录页改版臂·页码链机核（2026-09-14）
义务＝义务总表 §二.6：删「本五 答案本/BOOK FIVE」章带＋\\tocans 行；
页码链以换装件实测页数（印本档 PDF 实数）机核回填：行页码＝跨本连续累计起页、
合计＝Σ件页数；本数口径五本→四本。禁手编：全部数字由脚本从 PDF 实数计算写入。
红线：零 git；P1 正件（P1-必修3第9章量产0912/、物理样张骨架）只读；
写入仅 P1目录页/ 树内（前缀断言，越界即断言失败）。
读入＝main.src.tex（正件逐字节快照）；写出＝main.tex（改版件）＋_页码链断言.txt＋_diff登记.txt。
同制先例＝M2目录页/_页码链机核.py（含两参宏双解析、正文层残留断言、difflib 逐条登记）。
"""
import re
import sys
import difflib
from pathlib import Path

import pymupdf  # PDF 页数实数

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

# ---- 件账清单：顺序＝目录行序＝装配序；exp＝波报告在账页数（PDF 实数交叉断言用） ----
# (本, 件, 印本档PDF相对TREE路径, 报告在账页数, 行宏, 行首参精确值, 行题名精确值)
MANIFEST = [
    # 本一 导学本（5 件；波4a《_进度-波4a.md》件账 true 列）
    ('导学本', '9.1电荷',            'P1导学本/9.1电荷/main-true.pdf',            4, 'tocjie',  '9.1', '电荷'),
    ('导学本', '9.2库仑定律',        'P1导学本/9.2库仑定律/main-true.pdf',        4, 'tocjie',  '9.2', '库仑定律'),
    ('导学本', '9.3电场电场强度',    'P1导学本/9.3电场电场强度/main-true.pdf',    4, 'tocjie',  '9.3', '电场\\quad 电场强度'),
    ('导学本', '9.4静电的防止与利用', 'P1导学本/9.4静电的防止与利用/main-true.pdf', 4, 'tocjie',  '9.4', '静电的防止与利用'),
    ('导学本', '章末-本章易错过关',  'P1导学本/章末-本章易错过关/main-true.pdf',  3, 'toczong', '本章易错过关（章末）', ''),
    # 本二 练习本（4 件；波4b 报告 §二 页数行 true 列）
    ('练习本', '9.1电荷',            'P1练习拓展/9.1电荷/main-true.pdf',            6, 'tocjie', '9.1', '配套练习'),
    ('练习本', '9.2库仑定律',        'P1练习拓展/9.2库仑定律/main-true.pdf',        5, 'tocjie', '9.2', '配套练习'),
    ('练习本', '9.3电场电场强度',    'P1练习拓展/9.3电场电场强度/main-true.pdf',    4, 'tocjie', '9.3', '配套练习'),
    ('练习本', '9.4静电的防止与利用', 'P1练习拓展/9.4静电的防止与利用/main-true.pdf', 5, 'tocjie', '9.4', '配套练习'),
    # 本三 拓展本（1 件；波4b）
    ('拓展本', '拓展册', 'P1练习拓展/拓展册/main-true.pdf', 11, 'toclink', '拓展册', '静电场拓展（46 题·题号与答案册同册对号）'),
    # 本四 测评本（1 件；波5 案B 印本档 main.pdf，附卷制 3→4）
    ('测评本', '测评卷', 'P1测评本/测评卷/main.pdf', 4, 'toclink', '测评卷', '单元素养测评卷（一）·第9章（19 题·100 分·90 分钟）'),
]

BOOKS = ['导学本', '练习本', '拓展本', '测评本']

# ---- 行宏解析：jie/link 三参族＋zong 两参宏（M2 教训：不得按族统写）----
# 注意：\tocpart（学史切片行）不入跨本链，不匹配、不改写。
ROW_RE = re.compile(r'^\\toc(jie|link)\{([^{}]*)\}\{([^{}]*)\}\{(\d+)\}$')
ZONG_RE = re.compile(r'^\\toczong\{([^{}]*)\}\{(\d+)\}$')
log = []

def parse_row(s):
    """行 → (macro, a1, a2, 页码)；zong 归一为 a2=''。宏名统一带 toc 前缀；tocpart 返回 None。"""
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

# ============ ① 实测页数（PDF 实数）＋与波报告在账交叉断言 ============
say('== ① 换装件实测页数（印本档 PDF 实数·pymupdf）与波4a/4b/5 报告在账交叉断言 ==')
pages = []
fail = 0
for book, piece, rel, exp, macro, a1, a2 in MANIFEST:
    pdf = TREE / rel
    if not pdf.exists():
        say(f'[FAIL] 缺 PDF：{pdf}')
        fail += 1
        continue
    n = pymupdf.open(pdf).page_count
    ok = 'PASS' if n == exp else 'FAIL'
    if n != exp:
        fail += 1
    say(f'[{ok}] {book}/{piece} PDF实数={n} 报告在账={exp}  ({rel})')
    pages.append(n)
assert fail == 0, f'页数断言失败 {fail} 件（实数≠在账或缺件），禁手编终止'
assert len(pages) == 11

book_sum = {b: sum(n for n, (b2, *_ ) in zip(pages, MANIFEST) if b2 == b) for b in BOOKS}
total = sum(pages)
say(f'本合计：导学 {book_sum["导学本"]}／练习 {book_sum["练习本"]}／拓展 {book_sum["拓展本"]}／测评 {book_sum["测评本"]}，Σ件页数＝{total}')

# ============ ② 源面 11 行定位＋签名逐件断言（对集合不对数口径） ============
say('')
say('== ② 源面目录行签名逐件断言（11 行·序＝件账序） ==')
raw = SRC_TEX.read_bytes()
assert b'\r\n' not in raw, '源面为 CRLF，需改行尾处理后再跑'
src_lines = raw.decode('utf-8').splitlines()
rows_src = []  # (macro, a1, a2, 旧页码)
for ln in src_lines:
    r = parse_row(ln.strip())
    if r:
        rows_src.append(r)
assert len(rows_src) == 11, f'源面目录行数 {len(rows_src)} ≠ 11'
assert sum(1 for ln in src_lines if ln.strip().startswith('\\tocpart{')) == 1, 'tocpart 用法行数≠1'
sig_fail = 0
for (macro, a1, a2, old), (book, piece, rel, exp, emacro, ea1, ea2) in zip(rows_src, MANIFEST):
    if not ((macro == emacro) and (a1 == ea1) and (a2 == ea2)):
        sig_fail += 1
        say(f'[FAIL] 行签名不匹配：面=({macro},{a1},{a2}) 账=({emacro},{ea1},{ea2})')
if sig_fail == 0:
    say('[PASS] 11/11 行签名逐件精确匹配（宏名＋首参＋题名全等，序＝件账装配序；\\tocpart 学史切片行不入链不匹配）')
else:
    raise SystemExit(f'签名断言失败 {sig_fail} 行')

# ============ ③ 跨本连续累计起页（行页码＝跨本累计起页；合计＝Σ件页数） ============
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
assert starts[0] == 1
assert book_start['练习本'] == book_sum['导学本'] + 1
assert book_start['拓展本'] == book_sum['导学本'] + book_sum['练习本'] + 1
assert book_start['测评本'] == book_sum['导学本'] + book_sum['练习本'] + book_sum['拓展本'] + 1
assert starts[-1] + pages[-1] - 1 == total

# ============ ④ 删答案本章带＋tocans 行（含死宏，一次定位·降序删） ============
say('')
say('== ④ 删「本五 答案本/BOOK FIVE」章带＋\\tocans 行 ==')
new_lines = list(src_lines)
del_idx = []
for i, ln in enumerate(new_lines):
    if '\\tocchapter{05}' in ln or re.match(r'^\\tocans\{', ln.strip()):
        del_idx.append(i)
assert len(del_idx) == 2, f'章带/tocans 行定位数 {len(del_idx)} ≠ 2'
band, tocans_i = del_idx
assert tocans_i == band + 2, 'tocans 行与章带不邻接'
assert new_lines[band - 1].strip() == '\\vspace{4.8mm}' and new_lines[band + 1].strip() == '\\vspace{-3.29mm}', '章带块上下文不符'
mac_i = next(i for i, ln in enumerate(new_lines) if ln.startswith('\\newcommand{\\tocans}'))
for i in sorted([mac_i, band - 1, band, band + 1, tocans_i], reverse=True):
    say(f'[删行] 原{i+1}: {new_lines[i].strip()[:76]}')
    del new_lines[i]
say('[删行·义务外附带清理] \\tocans 宏定义死代码 1 行（上列首条）')
assert not any('\\tocans{' in ln for ln in new_lines), 'tocans 用法/定义残留'

# ============ ⑤ 行页码回填（11 行·机核写入，重扫定址防漂移） ============
say('')
say('== ⑤ 行页码回填（11 行，禁手编·脚本写入） ==')
rows_new = []
for i, ln in enumerate(new_lines):
    r = parse_row(ln.strip())
    if r:
        rows_new.append((i,) + r)
assert len(rows_new) == 11
assert [(a, b, c, d) for _, a, b, c, d in rows_new] == rows_src, '删带后行集/序/旧页码漂移'
for k, (i, macro, a1, a2, old) in enumerate(rows_new):
    new_ln = build_row(macro, a1, a2, starts[k])
    assert parse_row(new_ln) == (macro, a1, a2, starts[k]), f'回填行自洽断言失败 行{i+1}'
    say(f'[改行] {macro} {a1}｜{a2[:16]}｜页码 {old} → {starts[k]}')
    new_lines[i] = new_ln

# ============ ⑥ 头部注释＋段注改行（五本→四本口径、页码链、学史切片链尾）＋改版横幅 ============
say('')
say('== ⑥ 头部注释/段注改行（五本→四本口径＋页码链）＋改版横幅 ==')

def sub_once(old, new):
    hits = [i for i, ln in enumerate(new_lines) if old in ln]
    assert len(hits) == 1, f'替换锚「{old[:24]}…」命中 {len(hits)} 处 ≠ 1'
    i = hits[0]
    new_lines[i] = new_lines[i].replace(old, new)
    say(f'[改行] 原{i+1}: {old[:38]}… → {new[:38]}…')

def sub_line(old_full, new_full):
    hits = [i for i, ln in enumerate(new_lines) if ln == old_full]
    assert len(hits) == 1, f'整行替换锚命中 {len(hits)} 处 ≠ 1'
    i = hits[0]
    new_lines[i] = new_full
    say(f'[改行] 原{i+1} → {new_full.strip()[:52]}…')

sub_once('物理线五本制适配：', '物理线五本制适配（2026-09-14 换装轮改版→四本制，见文末改版横幅）：')
sub_line('%   ①分节单元＝五本（本一导学本／本二练习本／本三拓展本〔拍板增设〕／本四测评本／本五答案本），',
         '%   ①分节单元＝四本（本一导学本／本二练习本／本三拓展本／本四测评本；本五答案本带 2026-09-14 改版删除），')
sub_line('%     \\tocchapter 章带扩至 01~05（BOOK ONE~FIVE）；',
         '%     \\tocchapter 章带 01~04（BOOK ONE~FOUR；本五 BOOK FIVE 带 2026-09-14 改版删除）；')
sub_once('本件 13 行＋5 带单页可容', '本件 12 行＋4 带单页可容（改版后口径）')
sub_line('%     \\toczong/\\tocans 照 M2 原样拷入；',
         '%     \\toczong 照 M2 原样拷入（\\tocans 宏 2026-09-14 改版随答案本带撤销）；')
i_chain = next(i for i, ln in enumerate(new_lines) if ln.startswith('% 页码链：'))
new_chain = (f'% 页码链（2026-09-14 改版机核回填·印本档实测）：导学本 {book_start["导学本"]}-{book_end["导学本"]}'
             f'（9.1 起 {starts[0]}／9.2 起 {starts[1]}／9.3 起 {starts[2]}／9.4 起 {starts[3]}／章末 起 {starts[4]}）'
             f'／练习本 {book_start["练习本"]}-{book_end["练习本"]}／拓展本 {book_start["拓展本"]}-{book_end["拓展本"]}'
             f'／测评本 {book_start["测评本"]}-{book_end["测评本"]}，合计 {total} 页（四本，Σ件页数；学史切片自成页码制不入链）。')
say(f'[改行] 原{i_chain+1} 页码链行 → 新链（合计 {total}）')
new_lines[i_chain] = new_chain
sub_once('13 行＋5 带本可回', '12 行＋4 带本可回')
sub_once('五本一串 1~48', f'四本一串 1~{total}')
sub_once('不入 1~48 跨本链', f'不入 1~{total} 跨本链')

banner = [
    '% ============================================================',
    '% P1 第9章 套装册目录页·改版件（2026-09-14，换装轮目录页改版臂·五本→四本收官）',
    '% 义务＝义务总表 §二.6：删「本五 答案本/BOOK FIVE」章带＋\\tocans 行；页码链以换装件',
    '%   实测页数（波4a/4b/5 印本档）机核回填：行页码＝跨本连续累计起页、合计＝Σ件页数，',
    '%   脚本 _页码链机核.py 禁手编。原面快照＝main.src.tex；断言读数＝_页码链断言.txt；',
    '%   删行/改行逐条＝_diff登记.txt。',
    '% ============================================================',
]
new_lines = banner + new_lines
say(f'[增行] 改版横幅 {len(banner)} 行（注释层注记）')

# ============ ⑦ 生成面后断言（残留只对正文层＋注释层白名单strip后全卷） ============
say('')
say('== ⑦ 生成面后断言 ==')
txt = '\n'.join(new_lines) + '\n'
body_lines = new_lines[len(banner):]
WHITELIST = ['本五答案本带 2026-09-14 改版删除', '本五 BOOK FIVE 带 2026-09-14 改版删除',
             '\\tocans 宏 2026-09-14 改版随答案本带撤销']
stripped = []
for l in body_lines:
    for w in WHITELIST:
        l = l.replace(w, '')
    stripped.append(l)
joined = '\n'.join(stripped)
for tok in ('BOOK FIVE', '本五', '\\tocans', '参考答案册', '1~48', '合计 48 页'):
    assert tok not in joined, f'「{tok}」残留（白名单外）'
n_band = txt.count('\\tocchapter{0')
assert n_band == 4, f'章带数 {n_band} ≠ 4'
for tag in ('01', '02', '03', '04'):
    assert ('\\tocchapter{' + tag + '}') in txt, f'缺章带 {tag}'
assert '\\tocchapter{05}' not in txt, '章带 05 残留'
rows2 = [r for r in (parse_row(l.strip()) for l in new_lines) if r]
assert len(rows2) == 11
got = [r[3] for r in rows2]
assert got == starts, f'回填页码序列不符：{got} ≠ {starts}'
say(f'[PASS] 章带 01-04 四本；目录行 11；页码序列＝累计起页序列（{starts[0]}…{starts[-1]}）；答案本/tocans/1~48 残留 0')
t_src = [(r[0], r[1], r[2]) for r in rows_src]
t_new = [(r[0], r[1], r[2]) for r in rows2]
assert t_src == t_new, '行题名漂移'
say('[PASS] 11 行题名对原快照逐条全等（零漂移·仅页码列变更）')
part_line = next(l for l in new_lines if l.strip().startswith('\\tocpart{'))
assert part_line.strip() == '\\tocpart{物理学史切片}{P1}', 'tocpart 学史切片行被改（应零触碰）'
say('[PASS] \\tocpart 学史切片行零触碰（独立薄本自成页码制，不入跨本链）')

# ============ ⑧ 写出（前缀断言后） ============
DST_TEX.write_text(txt, encoding='utf-8', newline='\n')
OUT_ASSERT.write_text('\n'.join(log) + '\n', encoding='utf-8', newline='\n')

# ============ ⑨ diff 登记（删行/改行逐条） ============
d = []
d.append('# _diff登记.txt — P1 目录页改版 vs 原面快照（机核生成 2026-09-14）')
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
