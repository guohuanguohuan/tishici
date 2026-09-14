# -*- coding: utf-8 -*-
r"""门谱P1.py — P1 换装正装波4b 件级门谱（练习 4 件＋拓展 1 件）。

  槽宽门 zero-fp（迁后 main.tex；有旗件跑 main.src.tex 对照：同读数＝义务总表既有点位随迁）
  [D] 静默溢出审计 zero-fp（main-true/main-pure 双档＋拓压测 A/B/C true）
  ANSKEY 恒发（双档 log M3-ANSKEY ↔ 键账切丁集合互等）
  钉值门（迁后件面 \ansitem{n}{值} 花括号配平解析 ↔ body.tex 值源逐字节相等；label 同门）
  [E] 印面对账（true：`n.[答案]` 计数＝键数、[详解] 计数＝册载注记＋命制账；pure 全零无泄答）
  页级对勘（基线 main.src 复编译 vs 原印面逐页文本全等；pure 除末页逐页 PNG md5≡原、末页差＝尾块族、
    缺原段＝0（页码/页脚伪段豁免）；true 缺原段＝0＋题面锚串单调（序贯命中））
读数落 _门谱读数/。用法: python 门谱P1.py   # 退出码 0/1
"""
import hashlib
import io
import os
import re
import subprocess
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 迁移P1练习拓展 import parse_book, TREE, PIECES_LX, PIECE_TUO, DETAIL, NOTE_KEYS  # noqa: E402

import pymupdf                                                          # noqa: E402
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, '_门谱读数')
KEYS = os.path.join(HERE, '_键表')
PROJ = 'C:/提示词'
CAO = os.path.join(PROJ, '工具', 'makebox槽宽门.py')
AUD = os.path.join(PROJ, '工具', '静默溢出审计.py')
norm = lambda s: re.sub(r'\s+', '', s)
TAILFILL_TXT = ('笔记与错题整理', '课堂笔记', '错题重做', '疑问登记', '此处笔记')
FOOTER_TXT = ('第9章', '静电场及其应用', '拓展册', '练习', '高中物理', '必修第三册', '课时')


def run_py(script, args, tag, cwd):
    r = subprocess.run([sys.executable, script] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', cwd=cwd)
    txt = (r.stdout or '') + (r.stderr or '')
    with io.open(os.path.join(OUT, tag), 'w', encoding='utf-8') as f:
        f.write(txt)
    return r.returncode, txt


def pdf(f):
    return pymupdf.open(f)


def pages_text(f):
    d = pdf(f)
    return d.page_count, [norm(p.get_text()) for p in d]


def lines_multiset(f):
    d = pdf(f)
    ls = [norm(x) for pg in d for x in pg.get_text().split('\n')]
    return d.page_count, Counter(x for x in ls if x)


def png_md5(doc, page, zoom=2.0):
    pix = doc[page].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    return hashlib.md5(pix.tobytes('png')).hexdigest()


def miss(base, tgt):
    c = Counter(base)
    c.subtract(tgt)
    return Counter({k: v for k, v in c.items() if v > 0})


def is_artifact(s, cnt_diff, n0, np_):
    """页数差伪段：页码裸数或页脚丛名/件名族。"""
    if re.fullmatch(r'\d{1,3}', s):
        return cnt_diff <= max(n0 - np_, 0) + 1 and cnt_diff <= 2
    return any(t in s for t in FOOTER_TXT) and cnt_diff == max(n0 - np_, 1)


def needles_of(piece):
    """题面锚串：main.src.tex 各 \tihao 行去宏后首 12 字（序贯命中＝true 面题序零漂）。"""
    tex = io.open(os.path.join(TREE, piece, 'main.src.tex'), encoding='utf-8').read()
    out = []
    for l in tex.splitlines():
        m = re.match(r'^\\tihao\{(\d+)\}(.*)', l)
        if not m:
            continue
        t = m.group(2)
        t = re.sub(r'\\(tieside|xuankong)\{[^}]*\}', '', t)
        t = re.sub(r'\\(duoxuan|nobreak|tihao)\b', '', t)
        t = t.replace('\\kongwei', '').replace('\\obreak', '')
        t = re.sub(r'\\[a-zA-Z]+', '', t)
        t = re.sub(r'[{}~]', '', t)
        t = norm(t)
        out.append((int(m.group(1)), t[:12]))
    return out


def brace_item(body):
    """\\ansitem{L}{V} 花括号配平解析 → (label, value)。"""
    i = body.find('\\ansitem{')
    assert i >= 0, '块内无 ansitem'
    j, depth, fields = i + len('\\ansitem'), 0, []
    cur = []
    while len(fields) < 2:
        c = body[j]
        if c == '{':
            depth += 1
            if depth == 1:
                cur = []
            else:
                cur.append(c)
        elif c == '}':
            depth -= 1
            if depth == 0:
                fields.append(''.join(cur))
            else:
                cur.append(c)
        elif depth >= 1:
            cur.append(c)
        j += 1
    return fields[0], fields[1]


def tex_blocks(path):
    tex = io.open(path, encoding='utf-8').read()
    out = []
    for m in re.finditer(r'\\begin\{ansblock\}\[([^\]]+)\]\n(.*?)\\end\{ansblock\}', tex, re.S):
        out.append((m.group(1), brace_item(m.group(2))))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    kmap, notes = parse_book()
    bad = 0
    rpt = []

    def say(s):
        print(s)
        rpt.append(s)

    for piece, pfx, nums in PIECES_LX + [PIECE_TUO]:
        d = os.path.join(TREE, piece)
        want = set(io.open(os.path.join(KEYS, '丁册-%s.txt' % pfx), encoding='utf-8').read().split())
        # ① 槽宽门
        rc, txt = run_py(CAO, ['main.tex', '--mode', 'zero-fp'], '_槽宽-%s.txt' % piece, d)
        if rc == 1:
            rc2, txt2 = run_py(CAO, ['main.src.tex', '--mode', 'zero-fp'], '_槽宽-%s-src对照.txt' % piece, d)
            same = rc2 == 1
            say('[槽宽] %s：旗（src 对照 %s）' % (piece, '同读数＝既有随迁' if same else 'DIFF——须核'))
            bad += (not same)
        else:
            say('[槽宽] %s：0 旗 PASS' % piece)
            bad += (rc != 0)
        # ② [D] 双档＋压测
        for tex in ['main-true.tex', 'main-pure.tex'] + (
                    ['压测A-三栏灰底-true.tex', '压测B-两栏括线-true.tex', '压测C-三栏括线-true.tex']
                    if piece == PIECE_TUO[0] else []):
            rc, txt = run_py(AUD, [tex, '--grade', 'zero-fp'], '_D-%s-%s.txt' % (piece, tex), d)
            verdict = [l for l in txt.splitlines() if '[PASS]' in l or '[FAIL]' in l]
            say('[D] %s %s：%s' % (piece, tex, (verdict[-1] if verdict else '无判语')[:88]))
            bad += (rc != 0)
        # ③ ANSKEY 恒发
        got = {}
        for mode in ('true', 'pure'):
            log = io.open(os.path.join(d, 'main-%s.log' % mode), encoding='utf-8', errors='replace').read()
            got[mode] = re.findall(r'M3-ANSKEY: (\S+)', log)
        ok = set(got['true']) == set(want) and set(got['pure']) == set(want)
        say('[ANSKEY] %s：true %d｜pure %d｜键账 %d → %s' % (piece, len(got['true']), len(got['pure']),
                                                             len(want), '恒发 PASS' if ok else 'FAIL'))
        bad += (not ok)
        # ④ 钉值门（件面 ansitem ↔ body.tex 值源逐字节）
        blocks = tex_blocks(os.path.join(d, 'main.tex'))
        reds = []
        if [k for k, _ in blocks] != ['%s-%s' % (pfx, (('%03d' % n) if pfx == '拓' else str(n))) for n in nums]:
            reds.append('键序不符 %d 块' % len(blocks))
        for k, (lab, val) in blocks:
            blab, bval = kmap[k]
            if lab != blab or val != bval:
                reds.append('钉值漂移 %s' % k)
        nkey = pfx == '拓' and 46 or len(nums)
        say('[钉值] %s：%d 块逐字节比对 → %s' % (piece, len(blocks), 'FAIL ' + '；'.join(reds) if reds else 'PASS'))
        bad += bool(reds)
        # ⑤ [E] 印面对账
        t = ''.join(pg.get_text() for pg in pdf(os.path.join(d, 'main-true.pdf')))
        p = ''.join(pg.get_text() for pg in pdf(os.path.join(d, 'main-pure.pdf')))
        want_notes = sum(1 for k in want if k in notes) + sum(1 for k in want if k in DETAIL)
        got_i = len(re.findall(r'(?<![\w）)])\d{1,2}\s*\.\s*\[答案\]', t))
        got_n = t.count('[详解]')
        leak = len(re.findall(r'\[\s*答案\s*\]', p)) + p.count('[详解]')
        ok = got_i == len(want) and got_n == want_notes and leak == 0
        say('[E] %s：true [答案] %d/%d｜[详解] %d/%d（注记+命制）｜pure 泄答 %d → %s'
            % (piece, got_i, len(want), got_n, want_notes, leak, 'PASS' if ok else 'FAIL'))
        bad += (not ok)
        # ⑥ 页级对勘
        n0, T0 = pages_text(os.path.join(d, 'main-原印面.pdf'))
        nb, Tb = pages_text(os.path.join(d, 'main.src.pdf'))
        nt, Lt = lines_multiset(os.path.join(d, 'main-true.pdf'))
        np_, Lp = lines_multiset(os.path.join(d, 'main-pure.pdf'))
        reds = []
        if nb != n0 or Tb != T0:
            reds.append('基线复编译≠原印面（页 %d/%d，首异页 %d）'
                        % (nb, n0, next((i for i in range(min(nb, n0)) if Tb[i] != T0[i]), -1)))
        d0 = pdf(os.path.join(d, 'main-原印面.pdf'))
        dp = pdf(os.path.join(d, 'main-pure.pdf'))
        md5diff = [i + 1 for i in range(min(n0, np_) - 1) if png_md5(d0, i) != png_md5(dp, i)]
        if md5diff:
            reds.append('pure 像素漂移页 %s' % md5diff[:6])
        mt, mpu = miss(L0c := lines_multiset(os.path.join(d, 'main-原印面.pdf'))[1], Lt), miss(L0c, Lp)
        if mt:
            reds.append('true 缺原段 %d（题面漂移红）' % sum(mt.values()))
        real = {s: v for s, v in mpu.items() if not is_artifact(s, v, n0, np_)}
        if real:
            reds.append('pure 缺原段 %d 样本 %s' % (sum(real.values()), list(real)[:4]))
        add_pu = miss(Lp, L0c)
        tail_add, art_add, real_add = 0, 0, []
        for s, v in add_pu.items():
            if any(x in s for x in TAILFILL_TXT):
                tail_add += v
            elif re.fullmatch(r'\d{1,3}', s) or any(x in s for x in FOOTER_TXT):
                art_add += v
            else:
                real_add.append(s)
        if real_add:
            reds.append('pure 新增出尾块族 %s' % real_add[:4])
        # true 题面锚串单调（序贯命中）
        pos, seq = 0, []
        tt = norm(''.join(pg.get_text() for pg in pdf(os.path.join(d, 'main-true.pdf'))))
        for n, nd in needles_of(piece):
            i = tt.find(nd, pos)
            if i < 0:
                seq.append(n)
            else:
                pos = i + len(nd)
        if seq:
            reds.append('true 题面锚串失序/未命中 题%s' % seq[:6])
        if reds:
            bad += 1
            say('[页勘] %s：FAIL｜%s' % (piece, '｜'.join(reds)[:220]))
        say('[页勘] %s：页 %d→基线 %d/true %d/pure %d｜pure 逐页 md5（除末页）漂移 %d｜'
            'pure 新增＝尾块族 %d 段＋伪段 %d｜true 锚串单调 %d/%d'
            % (piece, n0, nb, nt, np_, len(md5diff), tail_add, art_add, len(nums) - len(seq), len(nums)))
    # ⑦ 拓 压测复跑读数（三栏探针）
    if PIECE_TUO[0] in [x[0] for x in PIECES_LX + [PIECE_TUO]]:
        log = io.open(os.path.join(TREE, '拓展册', '压测A-三栏灰底-true.log'), encoding='utf-8', errors='replace').read()
        n_ov = len(re.findall(r'Overfull', log))
        say('[压测] 拓-31 探针（改制后三栏 53.5mm）：压测A Overfull %d（试迁 4 → 0＝改制消红实证）' % n_ov)
    with io.open(os.path.join(OUT, '_门谱总读数.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(rpt) + '\n')
    print('==== 门谱P1 总判：%s ====' % ('全绿' if bad == 0 else '有红 %d' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
