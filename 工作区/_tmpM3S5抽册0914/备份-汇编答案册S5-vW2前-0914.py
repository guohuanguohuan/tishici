# -*- coding: utf-8 -*-
"""汇编答案册S5.py — 三件答案册 tex 草案（单源 ansbook.tex＋双壳 true/false）＋成册门谱。
导学/练习＝工具同源装配序逐件拼接；拓展册＝臂侧适配器（seat 制印面号逐字保真）。
写入仅限本目录。"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, CJ, T, pieces_of, fold, source_leakscan

RE_BEGIN, RE_END, RE_ANCH = T.RE_BEGIN, T.RE_END, T.RE_ANCH
RE_ITEM_RAW = re.compile(r'\\ansitem\{([^{}]*)\}\{')
RE_NOTE = T.RE_NOTE
RE_KEYLOG = T.RE_KEYLOG


def parse_raw(piece_dir):
    """适配器解析：同工具锚制，印面号留原串（seat 制兼容，T 块值不丢）。"""
    main_path = os.path.join(piece_dir, 'main.tex')
    src = T.read_text(main_path)
    lines = [ln.rstrip('\r') for ln in src.split('\n')]
    blocks, anchors, cur = [], [], None
    for i, raw in enumerate(lines):
        code = T.strip_comment(raw)
        mb = RE_BEGIN.match(code)
        if mb and cur is None:
            cur = {'key': mb.group(1), 'seat': None, 'val': None, 'note': None}
            continue
        if cur is not None:
            ma = RE_ANCH.match(raw)
            if ma:
                anchors.append(ma.group(1))
                continue
            mi = RE_ITEM_RAW.search(code)
            if mi and cur['val'] is None:
                cur['seat'] = mi.group(1)
                cur['val'], _ = T.extract_arg(lines, i, mi.end() - 1)
                continue
            mn = RE_NOTE.search(code)
            if mn and cur['note'] is None:
                cur['note'], _ = T.extract_arg(lines, i, mn.end() - 1)
                continue
            if RE_END.match(code):
                blocks.append(cur)
                cur = None
    assert cur is None, 'ansblock 未闭合'
    assert len(anchors) == len(blocks), '锚数≠块数'
    return blocks


CJKGLUE = T.CJKGLUE
SHELL = T.SHELL_TMPL


def build_booklet(tag, jianxing_list, outname, jianming_label):
    """tag=导学/练习/拓展；jianxing_list=源件型清单。返回读数 dict。"""
    out = os.path.join(HERE, outname)
    os.makedirs(out, exist_ok=True)
    srcs = []
    for jx in jianxing_list:
        for pian, pdir in pieces_of(jx):
            piece = T.parse_piece(pdir)
            blocks = parse_raw(pdir)
            assert [b['key'] for b in blocks] == [b['key'] for b in piece['blocks']] \
                or jx == '拓展册', '适配器与工具解析键序不一致：%s' % pian
            srcs.append({'jianxing': jx, 'pian': pian, 'dir': pdir, 'piece': piece,
                         'blocks': blocks})
    # 键全局唯一断言
    allk = [b['key'] for s in srcs for b in s['blocks']]
    assert len(allk) == len(set(allk)), '组内键跨片撞车'
    zhang = next(s['piece']['zhangming'] for s in srcs if s['piece']['zhangming'])
    zhangtitle = None
    for s in srcs:
        for t in s['piece']['titles']:
            if t.startswith('\\zhangtitle'):
                zhangtitle = t
                break
        if zhangtitle:
            break
    sty0 = srcs[0]['piece']['sty']
    sty_md5 = T.md5_of(sty0)
    assert sty_md5 == T.STY_MD5_LOCK, 'sty 锁漂'
    N = len(allk)
    zhangtitle = '\\zhangtitle{%s}' % jianming_label  # 汇编册＝册名章头（源件章头为件名，不照抄）

    L = []
    A = L.append
    A('% ' + '=' * 60)
    A('%% %s答案册（S5 试产臂汇编草案）—— 源＝%s 各件 main.tex（只读）；'
      '工具/答案抽册器.py 逐件抽册口径，同序同号逐片保持' % (tag, '＋'.join(jianxing_list)))
    A('%% 源件 md5 见 逐件汇总.json；值/详解逐字照源（钉值硬断言）；题面不重印')
    A('%% 双档：ansbook-true＝详解印本／ansbook-false＝纯值速查本（\\ansbookdetail 件面开关）')
    A('%% 编译：xelatex <壳> ×2，cwd＝本目录；sty＝qp-m3.sty 副本（md5 %s 锁同）' % sty_md5)
    A('% ' + '=' * 60)
    A('\\documentclass[fontset=none]{ctexart}')
    A('\\usepackage{qp-m3}')
    A('% —— 册面补钉：pifont（源件值域含 \\ding{51} 勾形；qp-m3 不供给，'
      '照 ROUTING 承源件同精神挂载，未用件零副作用） ——')
    A('\\usepackage{pifont}')
    L.extend(T.ROUTING)
    A(CJKGLUE)
    A('\\ansblockgrayfalse')
    A('\\newif\\ifansbookdetail')
    A('\\ifdefined\\ansbookdetail')
    A('  \\ifnum\\ansbookdetail=0 \\ansbookdetailfalse\\else\\ansbookdetailtrue\\fi')
    A('\\else')
    A('  \\ansbookdetailtrue')
    A('\\fi')
    A('\\renewcommand{\\qpzhangming}{%s}%%' % zhang)
    A('\\renewcommand{\\qpjianming}{%s}%%' % jianming_label)
    A('')
    A('\\begin{document}')
    if zhangtitle:
        A(zhangtitle)
    A('\\par\\glueguard{1}\\addvspace{2pt}\\noindent\\biaoqian{【纯答案册】}'
      '{\\fangsong 题面不重印\\quad 逐片印面号与正册同号同序}\\par\\addvspace{2pt}')
    A('')
    A('\\begin{multicols}{2}')
    A('\\emergencystretch=1em')
    seq, seats, vals, notes = [], [], [], []
    zux_re = re.compile(r'课时\d+[A-Za-z]*')
    for s in srcs:
        piece = s['piece']
        A('')
        heads = [t for t in piece['titles'] if not t.startswith('\\zhangtitle')]
        if heads:
            L.extend(heads)
        else:
            A('\\par\\Needspace*{3\\baselineskip}\\noindent\\biaoqian{【%s】}\\par'
              % s['pian'])
        if not heads:
            pass
        for b in s['blocks']:
            A('')
            A('\\begin{ansblock}[%s]' % b['key'])
            A('%% ans:%s' % b['key'])
            A('\\ansitem{%s}{%s}' % (b['seat'], b['val']))
            A('\\ifansbookdetail')
            A('\\ansnote{详解}{%s}' % b['note'])
            A('\\fi')
            A('\\end{ansblock}')
            seq.append(b['key'])
            seats.append(b['seat'])
            vals.append(b['val'])
            notes.append(b['note'])
    A('')
    A('\\tailfill[30mm]')
    A('')
    A('\\end{multicols}')
    A('\\end{document}')
    open(os.path.join(out, 'ansbook.tex'), 'w', encoding='utf-8',
         newline='\n').write('\n'.join(L) + '\n')
    open(os.path.join(out, 'ansbook-true.tex'), 'w', encoding='utf-8',
         newline='\n').write(SHELL % ('详解印本', '1', 'ansbook-true', 'ansbook-true', '1'))
    open(os.path.join(out, 'ansbook-false.tex'), 'w', encoding='utf-8',
         newline='\n').write(SHELL % ('纯值速查本', '0', 'ansbook-false', 'ansbook-false', '0'))
    shutil.copyfile(sty0, os.path.join(out, 'qp-m3.sty'))
    assert T.md5_of(os.path.join(out, 'qp-m3.sty')) == T.STY_MD5_LOCK
    print('== %s答案册 落盘：源片 %d，块 %d' % (tag, len(srcs), N))

    # 独立复核面：从落盘 ansbook.tex 复抽（原串 seat）
    bk = reparse_raw(out)
    g = T.Gates()
    g.check('守恒：源锚数＝源块数＝册锚数＝册块数＝%d' % N,
            all(len(s['piece']['anchors']) == len(s['blocks']) for s in srcs)
            and len(bk['anchors']) == len(bk['blocks']) == N,
            '%d 块' % len(bk['blocks']))
    g.check('同序：册键序≡Σ源装配序（逐位）', bk['seq'] == seq, '%d 位' % len(seq))
    g.check('同号：册印面号串≡Σ源印面号串（逐字，seat 制兼容）',
            bk['seats'] == seats, '首末 %s..%s' % (seats[0], seats[-1]))
    g.check('钉值：册值≡源值（逐字全等·硬断言，%d块）' % N,
            bk['vals'] == vals, '%d/%d' % (N, N))
    g.check('钉值：册详解≡源详解（逐字全等，%d块）' % N, bk['notes'] == notes, '')
    # 编译＋log/PDF 门
    stats = {s: T.compile_shell(out, s) for s in ('ansbook-true', 'ansbook-false')}
    seqs = []
    for sh, sts in stats.items():
        for st in sts:
            tg = '%s#%d' % (sh.replace('ansbook-', ''), st['pass'])
            g.check('三零[%s]：err/Over/Under/Miss＝0 且 exit=0' % tg,
                    st['rc'] == 0 and st['error'] == 0 and st['overfull'] == 0
                    and st['underfull'] == 0 and st['missing'] == 0,
                    'rc=%d %d/%d/%d/%d' % (st['rc'], st['error'], st['overfull'],
                                           st['underfull'], st['missing']))
            g.check('对号[%s]：log ANSKEY 序≡册序（逐位）' % tg, st['anskeys'] == seq,
                    '%d键' % len(st['anskeys']))
            seqs.append(st['anskeys'])
    g.check('对号：两档×两遍 ANSKEY 恒等（4编全同）', all(x == seqs[0] for x in seqs), '')
    # PDF 门
    import fitz
    pdfs = {}
    for tg in ('true', 'false'):
        doc = fitz.open(os.path.join(out, 'ansbook-%s.pdf' % tg))
        pdfs[tg] = {'n': len(doc),
                    'text': '\n'.join(p.get_text() for p in doc)}
        pdfs[tg]['ftext'] = fold(pdfs[tg]['text'])
        doc.close()
    for tg in ('true', 'false'):
        t = pdfs[tg]['text']
        nums = re.findall(r'(?<![0-9A-Za-z])([0-9A-Za-z]{1,4})\.\s*\[答案\]', t)
        g.check('PDF[%s]：[答案] 计数＝%d' % (tg, N), t.count('[答案]') == N,
                str(t.count('[答案]')))
        g.check('PDF[%s]：印面号序≡Σ源印面号（逐位＝同序同号印面证）' % tg,
                nums == seats, '%d枚' % len(nums))
    g.check('PDF[true]：[详解] 计数＝%d' % N, pdfs['true']['text'].count('[详解]') == N, '')
    g.check('PDF[false]：[详解] 计数＝0', pdfs['false']['text'].count('[详解]') == 0, '')
    # 泄漏门：针＝Σ各片题面库 run＋拓展源件题面区 run；豁免＝册全块体
    allowed = fold(T.texstrip(''.join(v + (n or '') for v, n in zip(vals, notes))))
    nrun = 0
    reds = []
    for s in srcs:
        runs, _a, _p = T.build_leakset(s['piece'])
        if runs is None:
            body, cur = [], False
            srcl = [ln.rstrip('\r') for ln in T.read_text(
                os.path.join(s['dir'], 'main.tex')).split('\n')]
            for ln in srcl:
                code = T.strip_comment(ln)
                if RE_BEGIN.match(code):
                    cur = True
                    continue
                if cur and RE_END.match(code):
                    cur = False
                    continue
                if not cur:
                    body.append(ln)
            runs = sorted(set(fold(r) for ln in body
                              for r in T.prose_runs(T.texstrip(ln))))
        nrun += len(runs)
        for tg in ('true', 'false'):
            reds += [r for r in runs if r in pdfs[tg]['ftext'] and r not in allowed]
    reds = sorted(set(reds))
    g.check('PDF双档：题面泄漏＝0（针 %d run，豁免＝册全块体）' % nrun, not reds,
            (str(reds[:2])[:120]) if reds else '0 条')
    g.check('PDF：页数 true≥false', pdfs['true']['n'] >= pdfs['false']['n'],
            'true=%d false=%d' % (pdfs['true']['n'], pdfs['false']['n']))
    rd = {'册': outname, '源片数': len(srcs), '块数': N,
          '红': g.reds, '门读数': [{'判定': a, '项': b, '读数': c}
                                   for a, b, c in g.rows],
          '页数': {'true': pdfs['true']['n'], 'false': pdfs['false']['n']},
          '键序': seq}
    json.dump(rd, open(os.path.join(out, '成册读数.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('== %s答案册：' % tag, '全绿' if not g.reds else '红 %d：%s' % (len(g.reds), g.reds))
    return rd


def reparse_raw(out_dir):
    src = T.read_text(os.path.join(out_dir, 'ansbook.tex'))
    lines = [ln.rstrip('\r') for ln in src.split('\n')]
    blocks, anchors, cur = [], [], None
    for i, raw in enumerate(lines):
        code = T.strip_comment(raw)
        mb = RE_BEGIN.match(code)
        if mb and cur is None:
            cur = {'key': mb.group(1), 'seat': None, 'val': None, 'note': None}
            continue
        if cur is not None:
            ma = RE_ANCH.match(raw)
            if ma:
                anchors.append(ma.group(1))
                continue
            mi = RE_ITEM_RAW.search(code)
            if mi and cur['val'] is None:
                cur['seat'] = mi.group(1)
                cur['val'], _ = T.extract_arg(lines, i, mi.end() - 1)
                continue
            mn = RE_NOTE.search(code)
            if mn and cur['note'] is None:
                cur['note'], _ = T.extract_arg(lines, i, mn.end() - 1)
                continue
            if RE_END.match(code):
                blocks.append(cur)
                cur = None
    return {'blocks': blocks, 'anchors': anchors,
            'seq': [b['key'] for b in blocks],
            'seats': [b['seat'] for b in blocks],
            'vals': [b['val'] for b in blocks],
            'notes': [b['note'] for b in blocks]}


if __name__ == '__main__':
    rs = []
    rs.append(build_booklet('拓展', ['拓展册'], '拓展答案册', '拓展答案册'))
    rs.append(build_booklet('导学', ['导学件'], '导学答案册', '导学答案册'))
    rs.append(build_booklet('练习', ['练习件'], '练习答案册', '练习答案册'))
    json.dump(rs, open(os.path.join(HERE, '成册汇总.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('== 三册汇编完 ==')
