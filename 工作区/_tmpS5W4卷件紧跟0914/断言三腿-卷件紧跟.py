# -*- coding: utf-8 -*-
r"""断言三腿-卷件紧跟.py — S5-W4 阶段一③：卷件「题后紧跟答案」三腿断言草案（可跑）
适用前提：件用 multicols 三栏回流制（\juancols），题后紧跟 ansblock；双壳 main.tex／main-pure.tex。

腿1 锚连含序：tex 流内 \ti{N} 与 \begin{ansblock}[键] 严格交错（每块落在本题号与下一题号之间），
    键尾序号＝题号、全卷升序＝源键序（键账序）。
腿2 块数恒等·双档零泄答：ansblock 块数＝题数；双档 log M3-ANSKEY 键集恒等且＝块数；
    true 印面「[答案]」计数＝块数、「[解析]」计数＝\ansnote 数；false 印面「答案／解析」零出现。
腿3 每栏底实测＜纸边：双档全页按三栏切片（text spans＋drawings 解析量测，页脚签名豁免），
    逐栏墨底硬判 ＜267.6mm（设计线 266.6＋1.0 容差；[D] 家族脚带线 277.0 同时满足）。

用法：
  python 断言三腿-卷件紧跟.py <件目录> [--keys N] [--skip-compile] [--selftest]
  无 pdf 时自动 xelatex ×2×双档（--xelatex 指定可执行文件路径）。
退出码 0＝三腿全绿；--selftest 反装双档应判红（断言可拦性自证）。读数全落 stdout。
"""
import argparse
import io
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

MM2PT = 72.0 / 25.4
XELATEX_DEF = r'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex.exe'
# 8 开横放三栏切片（mm）：left 8.9＋3×120＋2×11＝382 全幅（件型层 A 冻结值）
COLS_MM = [(8.9, 128.9), (139.9, 259.9), (270.9, 390.9)]
BOTTOM_LIMIT = 267.6          # 设计线＝text block 底 266.6＋1.0 容差
FOOT_TOP_MM = 268.3           # 页脚签名带起点（页脚行 y0 实测 ≥268；fancy 页脚 7.5pt/14pt 号码）
FOOT_RE = re.compile(r'羿郭工作室|测评卷|单元素养测评卷|选择性必修|RJB|^卷\s*\d+$|^卷$|^\d{1,3}$')
# 体墨溢出仍必拦：ansblock 括线为 drawings（不豁免），120mm 发丝线越 267.6 即红。
FOOT_REGAP = 1.0              # 量测容差


def shp(msg):
    print(msg)


def fail(msg):
    print('红｜' + msg)
    sys.exit(1)


def compile_if_needed(d, xelatex, skip):
    for shell in ('main', 'main-pure'):
        if not os.path.isfile(os.path.join(d, shell + '.tex')):
            fail('缺 %s.tex（双壳纪律）' % shell)
        if skip or os.path.isfile(os.path.join(d, shell + '.pdf')):
            continue
        for p in (1, 2):
            r = subprocess.run([xelatex, '-interaction=nonstopmode', '-halt-on-error',
                                shell + '.tex'], cwd=d, capture_output=True)
            if r.returncode != 0:
                fail('%s 第%d遍编译 exit=%d' % (shell, p, r.returncode))
        shp('编译：%s ×2 exit=0' % shell)


def parse_tex(path):
    """返回 (题号位表 [(pos,N)], 键位表 [(pos,键)], ansnote 数)。"""
    s = io.open(path, encoding='utf-8').read()
    tis = [(m.start(), int(m.group(1))) for m in re.finditer(r'\\ti\{(\d+)\}\{', s)]
    keys = [(m.start(), m.group(1).strip())
            for m in re.finditer(r'\\begin\{ansblock\}\[([^\]]+)\]', s)]
    nnotes = len(re.findall(r'\\ansnote\{解析\}', s))
    return tis, keys, nnotes, s


def leg1(tis, keys):
    shp('—— 腿1 锚连含序 ——')
    if len(tis) != len(keys):
        fail('腿1：题数 %d ≠ 块数 %d' % (len(tis), len(keys)))
    nums = [n for _, n in tis]
    if nums != sorted(nums) or len(set(nums)) != len(nums):
        fail('腿1：题号非严格升序 %s' % nums)
    for i, (pos_k, key) in enumerate(keys):
        pos_t, n = tis[i]
        nxt = tis[i + 1][0] if i + 1 < len(tis) else float('inf')
        if not (pos_t < pos_k < nxt):
            fail('腿1：键 %s 未落在题 %d 与下一题之间（锚连断裂）' % (key, n))
        m = re.search(r'(\d+)$', key)
        if not m or int(m.group(1)) != n:
            fail('腿1：键 %s 尾序 ≠ 题号 %d' % (key, n))
    shp('腿1 PASS：%d 题逐键紧跟（%s … %s），键序＝源键序' % (
        len(keys), keys[0][1], keys[-1][1]))


def leg2(d, tis, keys, nnotes, true_txt, false_txt, true_log, false_log):
    shp('—— 腿2 块数恒等·双档零泄答 ——')
    if len(keys) != len(tis):
        fail('腿2：块数 %d ≠ 题数 %d' % (len(keys), len(tis)))
    want = set(k for _, k in keys)
    ltrue = set(re.findall(r'M3-ANSKEY: (\S+)', io.open(true_log, encoding='utf-8', errors='ignore').read()))
    lfalse = set(re.findall(r'M3-ANSKEY: (\S+)', io.open(false_log, encoding='utf-8', errors='ignore').read()))
    if ltrue != want or lfalse != want:
        fail('腿2：log 键集失恒等 tex=%d true=%d false=%d' % (len(want), len(ltrue), len(lfalse)))
    a_true = true_txt.count('[答案]')
    j_true = true_txt.count('[解析]')
    if a_true != len(keys):
        fail('腿2：true 印面 [答案]×%d ≠ 块数 %d' % (a_true, len(keys)))
    if j_true != nnotes:
        fail('腿2：true 印面 [解析]×%d ≠ \\ansnote×%d' % (j_true, nnotes))
    leak = [w for w in ('答案', '解析') if w in false_txt]
    if leak:
        fail('腿2：false 印面泄答：%s' % '／'.join(leak))
    shp('腿2 PASS：块数恒等 %d｜双档 log 键集恒等｜true [答案]×%d [解析]×%d｜false 印面零泄答' % (
        len(keys), a_true, j_true))


def page_body_bottoms(pdf):
    """逐页逐栏返回体墨底 mm（页脚签名豁免）。返回 [(页, {栏: mm})]。"""
    doc = pymupdf.open(pdf)
    out = []
    for pno, pg in enumerate(doc, 1):
        ph = pg.rect.height / MM2PT
        pw = pg.rect.width / MM2PT
        if abs(pw - 399.8) > 1.0:
            fail('腿3：p%d 纸宽 %.1fmm 非 8 开横放' % (pno, pw))
        col_bot = {c: 0.0 for c in range(1, len(COLS_MM) + 1)}
        items = []
        for b in pg.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                for sp in ln['spans']:
                    items.append((sp['bbox'], sp.get('text', '')))
        for dr in pg.get_drawings():
            r = dr['rect']
            if (r.y1 - r.y0) * 1.0 / MM2PT <= 40.0:      # 细线/角饰；页高剪裁盒弃
                items.append((tuple(r), ''))
        for bbox, txt in items:
            x0, y0, x1, y1 = [v / MM2PT for v in bbox]
            if y0 > FOOT_TOP_MM and txt and FOOT_RE.search(txt.strip()):
                continue                                  # 页脚签名带豁免
            cx = (x0 + x1) / 2.0
            for c, (a, b2) in enumerate(COLS_MM, 1):
                if a - FOOT_REGAP <= cx <= b2 + FOOT_REGAP:
                    col_bot[c] = max(col_bot[c], y1)
                    break
        out.append((pno, col_bot))
    doc.close()
    return out


def leg3(tag, pdf):
    shp('—— 腿3 每栏底＜纸边（%s）——' % tag)
    worst = 0.0
    for pno, col_bot in page_body_bottoms(pdf):
        for c, y in sorted(col_bot.items()):
            if y > BOTTOM_LIMIT:
                fail('腿3：p%d 栏%d 底 %.1fmm ＞ %.1fmm（出栏出纸）' % (pno, c, y, BOTTOM_LIMIT))
            worst = max(worst, y)
        shp('  p%d 栏底 %s mm' % (pno, ' '.join('栏%d:%.1f' % (c, y) for c, y in sorted(col_bot.items()))))
    shp('腿3 PASS（%s）：全栏墨底峰 %.1fmm ＜ %.1f（设计线，兼＜277 脚带线）' % (tag, worst, BOTTOM_LIMIT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('piece')
    ap.add_argument('--keys', type=int, default=0, help='期望块数（缺省由 tex 自证）')
    ap.add_argument('--skip-compile', action='store_true')
    ap.add_argument('--selftest', action='store_true', help='反装双档应判红（可拦性自证）')
    ap.add_argument('--xelatex', default=XELATEX_DEF)
    a = ap.parse_args()
    d = os.path.normpath(a.piece)
    compile_if_needed(d, a.xelatex, a.skip_compile)
    tis, keys, nnotes, _ = parse_tex(os.path.join(d, 'main.tex'))
    if a.keys and len(keys) != a.keys:
        fail('块数 %d ≠ --keys %d' % (len(keys), a.keys))
    leg1(tis, keys)
    true_txt = pymupdf.open(os.path.join(d, 'main.pdf'))[0].get_text()
    false_txt = pymupdf.open(os.path.join(d, 'main-pure.pdf'))[0].get_text()
    for pg in range(1, len(pymupdf.open(os.path.join(d, 'main.pdf')))):
        true_txt += pymupdf.open(os.path.join(d, 'main.pdf'))[pg].get_text()
        false_txt += pymupdf.open(os.path.join(d, 'main-pure.pdf'))[pg].get_text()
    if a.selftest:
        try:
            leg2(d, tis, keys, nnotes, false_txt, true_txt,
                 os.path.join(d, 'main-pure.log'), os.path.join(d, 'main.log'))
        except SystemExit:
            shp('selftest PASS：反装双档被腿2拦截（断言可拦）')
            return
        fail('selftest：反装双档未被拦截（断言失效）')
    leg2(d, tis, keys, nnotes, true_txt, false_txt,
         os.path.join(d, 'main.log'), os.path.join(d, 'main-pure.log'))
    leg3('true', os.path.join(d, 'main.pdf'))
    leg3('false', os.path.join(d, 'main-pure.pdf'))
    shp('三腿全绿：%s' % d)


if __name__ == '__main__':
    main()
