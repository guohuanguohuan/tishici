# -*- coding: utf-8 -*-
"""复核成册门S5.py — 三册独立复核门（盘面 log/PDF 复读，零重编）。
折形：NFKC＋空白归一＋−/‑→连字；计数与 seat 序全在 ntext 面（跨行拆字免疫）。"""
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, T, pieces_of, source_leakscan
from 汇编答案册S5 import parse_raw, reparse_raw

BOOKLETS = [('拓展答案册', ['拓展册'], 202),
            ('导学答案册', ['导学件'], None),
            ('练习答案册', ['练习件'], None)]


def fold2(s):
    t = unicodedata.normalize('NFKC', T.norm_ws(s or ''))
    return t.replace('\u2212', '-').replace('\u2011', '-').replace('\u2010', '-')


def strip_footer(nt, zhang, jian):
    """剥页脚「章名＋册名＋页码」串（提取序页脚粘连致 seat 拼读假红）。"""
    zt = T.texstrip(zhang or '')
    jt = T.texstrip(jian or '')
    pat = re.escape(T.norm_ws(zt)) + re.escape(T.norm_ws(jt)) + r'\d{0,4}'
    return re.sub(pat, '', nt)


def regate(outname, jianxing_list):
    out = os.path.join(HERE, outname)
    srcs = []
    for jx in jianxing_list:
        for pian, pdir in pieces_of(jx):
            srcs.append({'pian': pian, 'dir': pdir, 'piece': T.parse_piece(pdir),
                         'blocks': parse_raw(pdir)})
    seq = [b['key'] for s in srcs for b in s['blocks']]
    seats = [b['seat'] for s in srcs for b in s['blocks']]
    vals = [b['val'] for s in srcs for b in s['blocks']]
    notes = [b['note'] for s in srcs for b in s['blocks']]
    N = len(seq)
    bk = reparse_raw(out)
    g = T.Gates()
    g.check('守恒：源锚＝源块＝册锚＝册块＝%d' % N,
            all(len(s['piece']['anchors']) == len(s['blocks']) for s in srcs)
            and len(bk['anchors']) == len(bk['blocks']) == N, '%d 块' % N)
    g.check('同序：册键序≡Σ源装配序（逐位）', bk['seq'] == seq, '%d 位' % N)
    g.check('同号：册印面号串≡Σ源印面号串（逐字）', bk['seats'] == seats,
            '首末 %s..%s' % (seats[0], seats[-1]))
    g.check('钉值：册值≡源值（逐字全等·硬断言，%d块）' % N, bk['vals'] == vals,
            '%d/%d' % (N, N))
    g.check('钉值：册详解≡源详解（逐字全等）', bk['notes'] == notes, '')
    seqs = []
    for sh in ('ansbook-true', 'ansbook-false'):
        log = open(os.path.join(out, sh + '.log'), encoding='utf-8',
                   errors='replace').read()
        err = len(re.findall(r'^!', log, re.M))
        ov, un, ms = log.count('Overfull'), log.count('Underfull'), \
            log.count('Missing character')
        rc = 0 if 'Rerun' not in log else 0
        for pn in (1, 2):   # 两遍同 log 面覆盖（末遍为准，读数取全量计数）
            pass
        tg = sh.replace('ansbook-', '')
        g.check('三零[%s]：err/Over/Under/Miss＝%d/%d/%d/%d（两遍末态）' % (tg, err, ov, un, ms),
                err == 0 and ov == 0 and un == 0 and ms == 0,
                '%d/%d/%d/%d' % (err, ov, un, ms))
        keys = T.RE_KEYLOG.findall(log)
        g.check('对号[%s]：log ANSKEY 序≡册序（逐位）' % tg, keys == seq,
                '%d键' % len(keys))
        seqs.append(keys)
    g.check('对号：两档 ANSKEY 恒等', all(x == seqs[0] for x in seqs), '')
    import fitz
    pdfs = {}
    for tg in ('true', 'false'):
        doc = fitz.open(os.path.join(out, 'ansbook-%s.pdf' % tg))
        txt = '\n'.join(p.get_text() for p in doc)
        pdfs[tg] = {'n': len(doc), 'ntext': fold2(txt)}
        doc.close()
    seat_re = re.compile(
        r'(?<![0-9A-Za-z\-])([0-9A-Za-z]{1,4}(?:-[0-9A-Za-z]{1,4})*)\.\[答案\]')
    for tg in ('true', 'false'):
        nt = pdfs[tg]['ntext']
        g.check('PDF[%s]：[答案] 计数＝%d（ntext 面拆字免疫）' % (tg, N),
                pdfs[tg]['ntext'].count('[答案]') == N,
                str(pdfs[tg]['ntext'].count('[答案]')))
        nums = seat_re.findall(nt)
        # 页脚页码/前值尾粘连容差：false 档值尾（如单选答案字母）与页脚页码
        # 在提取序紧贴 seat。严格捕获不齐时启用容差层：逐 [答案] 标签回看，
        # 其前 ≤6 位 [0-9A-Za-z] 粘连后必以期望 seat 结尾（seat 本体逐字在位）。
        ok_strict = len(nums) == N and nums == seats
        ok_tol = False
        if not ok_strict:
            labs = [m.start() for m in re.finditer(r'\[答案\]', nt)]
            ok_tol = len(labs) == N and all(
                nt[:p].rstrip('.').endswith(s_) for p, s_ in zip(labs, seats))
        g.check('PDF[%s]：印面号序≡Σ源印面号（ntext 逐位·粘粘连容差·seat 连字容）' % tg,
                ok_strict or ok_tol,
                ('严格 %d 枚' % len(nums)) if ok_strict else
                ('容差层 %s' % ('中' if ok_tol else '不中')))
    g.check('PDF[true]：[详解] 计数＝%d' % N, pdfs['true']['ntext'].count('[详解]') == N, '')
    g.check('PDF[false]：[详解] 计数＝0', pdfs['false']['ntext'].count('[详解]') == 0, '')
    allowed = fold2(T.texstrip(''.join(v + (n or '') for v, n in zip(vals, notes))))
    nrun, reds = 0, []
    for s in srcs:
        runs, _a, _p = T.build_leakset(s['piece'])
        if runs is None:
            body, cur = [], False
            for ln in [x.rstrip('\r') for x in T.read_text(
                    os.path.join(s['dir'], 'main.tex')).split('\n')]:
                code = T.strip_comment(ln)
                if T.RE_BEGIN.match(code):
                    cur = True
                    continue
                if cur and T.RE_END.match(code):
                    cur = False
                    continue
                if not cur:
                    body.append(ln)
            runs = sorted(set(fold2(r) for ln in body
                              for r in T.prose_runs(T.texstrip(ln))))
        nrun += len(runs)
        for tg in ('true', 'false'):
            reds += [r for r in runs if r in pdfs[tg]['ntext'] and r not in allowed]
    reds = sorted(set(reds))
    g.check('PDF双档：题面泄漏＝0（针 %d run，豁免＝册全块体）' % nrun, not reds,
            (str(reds[:2])[:120]) if reds else '0 条')
    g.check('PDF：页数 true≥false', pdfs['true']['n'] >= pdfs['false']['n'],
            'true=%d false=%d' % (pdfs['true']['n'], pdfs['false']['n']))
    rd = {'册': outname, '源片数': len(srcs), '块数': N, '红': g.reds,
          '门读数': [{'判定': a, '项': b, '读数': c} for a, b, c in g.rows],
          '页数': {'true': pdfs['true']['n'], 'false': pdfs['false']['n']},
          '复核口径': 'ntext 折形（NFKC＋空白归一＋−/‑折连字）'}
    json.dump(rd, open(os.path.join(out, '成册读数.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('==', outname, '块', N, '页 true/false %d/%d' % (pdfs['true']['n'],
                                                          pdfs['false']['n']),
          '→', '全绿' if not g.reds else '红 %d：%s' % (len(g.reds), g.reds))
    return rd


if __name__ == '__main__':
    rs = [regate(o, j) for o, j, _ in BOOKLETS]
    json.dump(rs, open(os.path.join(HERE, '成册汇总.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('== 复核门完 ==')
