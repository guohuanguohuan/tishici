# -*- coding: utf-8 -*-
r"""迁移件型.py — 三件型迁移函数＋驱动（M2 导学本 12 件批插·正装波1）。

件型插入规则表（换装方案草案 §1.2，试迁课时01 规约 R1/R2/R3）：
  课时件  预习填空＝第 3 个 \zhenhead 前｜判＝各 \zhentib 行后（标签取册连号）｜
          探＝例块尾（次 \liB 前·书写位后）＋变式块尾（次 \liB/\xiaojie 前）｜
          评＝次 \jiancestem 前／ketang 闭箱前｜ketang 回流＋\tailfill
  衔接节  \xthao 逐题块尾 ansblock（含图随迁）＋升格结构挂位点（注释槽·不印空节）＋\tailfill
  章末    例＝第 N 处 \zhankong{13mm} 后｜变式＝第 N 处 \zhankong{6mm} 后｜高考1–4 块尾锚｜
          题型卡 \vbox×12 保守保留（义务总表待裁2）＋\tailfill
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 册解析 import parse_book, split_group, read, SNAP  # noqa: E402
from 迁移引擎 import (TREE, KS, qpm3_defs, preamble_swap, block, insert_before,  # noqa: E402
                     insert_after_line, find1, kv_of, QP_M3_MD5, ensure_ov)

sys.stdout.reconfigure(encoding='utf-8')
BODY_EXTRA = {}


def load_body_extra():
    """三裁③：衔接填空补键值源＝body.tex \\ansline{衔接填空}（册有印无键）。"""
    body = read(r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册/body.tex")
    out = {}
    for m in re.finditer(r'^\\ansline\{(衔接填空)\}\{(.+)\}$', body, re.M):
        out['导-课时01-衔接填空'] = {'keys': ['导-课时01-衔接填空'], 'label': m.group(1),
                                     'value': m.group(2), 'extra': []}
    assert '导-课时01-衔接填空' in out, 'body.tex 衔接填空行未命中'
    return out


def migrate_keshi(piece, keys, kmap, m3names, m3bodies):
    tex = read(os.path.join(TREE, piece, 'main.src.tex'))
    log = []
    tex = preamble_swap(tex, piece, m3names, m3bodies, log)
    P = '导-' + piece                                  # 课时01 → 导-课时01

    want = (['%s-预习填空' % P] + ['%s-判%d' % (P, i) for i in range(1, 6)]
            + sorted((k for k in keys if '-探' in k),
                     key=lambda k: (int(re.search(r'-探(\d+)-', k).group(1)),
                                    0 if k.endswith('-例1') else int(k.rsplit('变式', 1)[-1])))
            + ['%s-评%d' % (P, i) for i in range(1, 6)])
    missing = [k for k in want if k not in kmap]
    assert not missing, '%s 缺键即停：%s' % (piece, missing)
    assert set(want) == set(keys), '%s 件账≠迁移账：%s' % (piece, sorted(set(keys) ^ set(want)))

    # 课堂评价回流（先开箱，方案§1.3）
    m = re.search(r'\\vbox\{\s*\\huaxing\{课\}\{堂\}\{评\}\{价\}\{知识评价\\quad 素养形成\}'
                  r'\s*\\pingtou\{([^}]*)\}', tex)
    assert m, '%s ketang 开箱锚未命中' % piece
    tex = tex[:m.start()] + '\\begin{ketang}{%s}' % m.group(1) + tex[m.end():]
    log.append(('回流', '\\vbox 整体装栏 → \\begin{ketang}{%s}（右栏空病灶位）' % m.group(1)))
    ket_open = tex.find('\\begin{ketang}')

    # 预习填空（第 3 个 \zhenhead 前＝知识点三判断组头前·R1）
    zh = [mm.start() for mm in re.finditer(r'\\zhenhead\{', tex)]
    assert len(zh) == 3, '%s \\zhenhead 计 %d（须 3）' % (piece, len(zh))
    k = '%s-预习填空' % P
    v, ex = kv_of(k, kmap, P)
    tex = insert_before(tex, zh[2], block(k, '预习填空', v, 'ansnote',
                                          ['\\ansnote{解析}{%s}' % e[1] for e in ex]))
    log.append((k, '第 3 个 \\zhenhead 前（知识点三判断组头前·R1）', v))

    # 判 1–5（各 \zhentib 行后·标签取册连号 R2；6答5键＝末键双值锚随组尾题）
    # 插块推移位：\zhentib 位逐键重测（判 n 插入会使既存判 n+1.. 位失准——课时01 实证）
    ck = ['%s-判%d' % (P, i) for i in range(1, 6)]

    def zhentib_now():
        hz = tex.find('\\huaxing{课}{中}')
        assert hz >= 0, '%s 课中探究组头未命中' % piece
        return list(re.finditer(r'^\\zhentib\{(\(\d+\))\}', tex[:hz], re.M))

    items = zhentib_now()
    if len(items) == len(ck):
        for j, k2 in enumerate(ck):
            v, ex = kv_of(k2, kmap, P)
            items = zhentib_now()
            assert len(items) == len(ck), '%s 判位重测 %d（须 5）' % (piece, len(items))
            tex = insert_after_line(tex, items[j].start(), block(k2, items[j].group(1), v, 'ansitem',
                                      ['\\ansnote{解析}{%s}' % e[1] for e in ex]))
            log.append((k2, '\\zhentib %s 行后' % items[j].group(1), v))
    elif len(items) == len(ck) + 1:
        sp, unc = split_group(kmap[ck[0]], P)
        assert unc is None and sp.get('__双值__'), '%s 判组拆分非双值形态' % piece
        shuang = sp['__双值__']
        for j in range(4):
            k2 = ck[j]
            v, _ = kv_of(k2, kmap, P)
            items = zhentib_now()
            assert len(items) == len(ck) + 1, '%s 判位重测 %d（须 6）' % (piece, len(items))
            tex = insert_after_line(tex, items[j].start(), block(k2, items[j].group(1), v, 'ansitem'))
            log.append((k2, '\\zhentib %s 行后' % items[j].group(1), v))
        k2 = ck[4]
        items = zhentib_now()
        assert len(items) == len(ck) + 1, '%s 判位重测 %d（须 6）' % (piece, len(items))
        b = ('\\begin{ansblock}[%s]\n%% ans:%s\n\\ansitem{%s}{%s}\n\\anssub{%s}{%s}\n\\end{ansblock}'
             % (k2, k2, shuang['labels'][0], shuang['vals'][0], shuang['labels'][1], shuang['vals'][1]))
        tex = insert_after_line(tex, items[5].start(), b)
        log.append((k2, '\\zhentib %s 行后（6答5键·末键双值锚 \\ansitem+%%anssub，快照判5双值口径「%s」）'
                    % (items[5].group(1), sp[k2]),
                    '%s ＋ %s' % (shuang['vals'][0], shuang['vals'][1])))
    else:
        raise AssertionError('%s 判断条 %d（5/6 之外无规约·停）' % (piece, len(items)))

    # 探 例/变（例块尾＝次 \liB 前·书写位后；末变式块尾＝\xiaojie 前·试迁同款）
    tj = [mm.start() for mm in re.finditer(r'\\tjdnr\{', tex)]
    tnums = sorted({int(re.search(r'-探(\d+)-', k2).group(1)) for k2 in keys if '-探' in k2})
    assert len(tj) == len(tnums), '%s \\tjdnr %d ≠ 探点 %d' % (piece, len(tj), len(tnums))
    for i, tno in enumerate(tnums, 1):
        tkeys = sorted((k2 for k2 in keys if k2.startswith('%s-探%d-' % (P, tno))),
                       key=lambda k2: 0 if k2.endswith('-例1') else int(k2.rsplit('变式', 1)[-1]))
        pos = None
        for j, k2 in enumerate(tkeys):
            tj = [mm.start() for mm in re.finditer(r'\\tjdnr\{', tex)]   # 插块推移位，段界逐键重测
            pos = tj[i - 1] if pos is None else pos
            seg1 = tj[i] if i < len(tj) else tex.find('\\begin{ketang}')
            tag = k2.rsplit('-', 1)[-1]
            v, ex = kv_of(k2, kmap, P)
            b = block(k2, tag, v, 'ansnote', ['\\ansnote{解析}{%s}' % e[1] for e in ex])
            if tag == '例1' or j < len(tkeys) - 1:
                idx = find1(tex, '\\liB{', pos, '%s 块尾 \\liB' % k2, stop=seg1)
                anch = '次 \\liB 前（%s 块尾·书写位后）' % tag
            else:
                idx = find1(tex, '\\xiaojie{', pos, '%s 块尾 \\xiaojie' % k2, stop=seg1)
                anch = '\\xiaojie 前（探%d %s 块尾）' % (tno, tag)
            tex = insert_before(tex, idx, b)
            log.append((k2, anch, v))
            pos = idx + len(b) + 2

    # 评 1–5（次 \jiancestem 前；末题 ketang 闭箱前）——位逐键重测（同判：插块推移位）
    for i in range(1, 6):
        k2 = '%s-评%d' % (P, i)
        v, ex = kv_of(k2, kmap, P)
        if i < 5:
            konow = tex.find('\\begin{ketang}')
            js = [mm.start() for mm in re.finditer(r'\\jiancestem\{', tex) if mm.start() > konow]
            assert len(js) == 5, '%s 评价题 %d（须 5）' % (piece, len(js))
            idx, anch = js[i], '次 \\jiancestem 前'
        else:
            m2 = re.search(r'\}\s*\n\n\\end\{multicols\}\n\\end\{document\}\s*$', tex)
            assert m2, '%s ketang 闭箱锚未命中' % piece
            idx, anch = m2.start(), 'ketang 闭箱前'
        tex = insert_before(tex, idx, block(k2, str(i), v, 'ansitem',
                                            ['\\ansnote{解析}{%s}' % e[1] for e in ex]))
        log.append((k2, anch, v))

    # ketang 闭箱＋尾块（§1.3）
    m2 = re.search(r'\}\s*\n\n\\end\{multicols\}\n\\end\{document\}\s*$', tex)
    assert m2, '%s ketang 闭箱＋尾锚未命中' % piece
    tex = tex[:m2.start()] + '\\end{ketang}\n\n\\end{multicols}\n\n\\tailfill\n\\end{document}\n' + tex[m2.end():]
    log.append(('尾块', '\\tailfill 于 \\end{document} 前（\\iftailfillused 装配断言面）'))

    # 三裁③ 衔接填空补键随迁（仅课时01 有衔接位①~⑥·组尾 ansblock）
    xjk = list(re.finditer(r'^\\xjtk\{[①-⑥]\}', tex, re.M))
    if xjk:
        assert len(xjk) == 6, '%s 衔接填空条 %d（须 6）' % (piece, len(xjk))
        bk = '%s-衔接填空' % P
        g = kmap.get(bk) or BODY_EXTRA.get(bk)
        assert g, '%s 衔接填空补键值源缺失' % piece
        tex = insert_after_line(tex, xjk[-1].start(), block(bk, '衔接填空', g['value'], 'ansnote'))
        log.append((bk, '衔接位⑥条后（组尾 ansblock·正装三裁③补键随迁·值＝册 \\ansline{衔接填空} 逐字）',
                    g['value']))
    return tex, log


def migrate_xianjie(piece, keys, kmap, m3names, m3bodies):
    tex = read(os.path.join(TREE, piece, 'main.src.tex'))
    log = []
    tex = preamble_swap(tex, piece, m3names, m3bodies, log)
    P = '导-衔接'
    want = ['%s-%d' % (P, i) for i in range(1, 30)]
    missing = [k for k in want if k not in kmap]
    assert not missing and set(want) == set(keys), '%s 键账不齐：%s' % (piece, missing)
    for n in range(1, 30):
        k = '%s-%d' % (P, n)
        start = find1(tex, '\\xthao{%d}' % n, 0, k)
        nxt = [x for x in (tex.find(p, start + 1) for p in ('\\xthao{', '\\zuhang{', '\\zhublock{'))
               if x > start]
        assert nxt, '%s 题块尾锚未命中' % k
        g = kmap[k]
        assert len(g['keys']) == 1, '%s 非单键组' % k
        ex = ['\\ansnote{解析}{%s}' % e[1] for e in g['extra']]
        tex = insert_before(tex, min(nxt), block(k, str(n), g['value'], 'ansitem', ex))
        log.append((k, '次 \\xthao/\\zuhang/\\zhublock 前（题块尾·含图随迁）', g['value']))

    upgrade = (
        '% ============================================================\n'
        '% 衔接节升格·结构挂位点（换装正装轮0914 立·义务总表§一.1②）\n'
        '%   全制式补＝考点探究（\\huaxing{课}{中}{探}{究}{考点探究\\quad 素养小结}＋\\tjdnr/\\liB 例变骨架）\n'
        '%           ＋课堂评价 G5（\\begin{ketang}{本组共5题，1—3为单选，4—5为填空．}…\\end{ketang}，\n'
        '%             判/选/填 恒5 内构）——补题命制挂后续轮；本轮先立结构不印空节（防空节版面红旗），\n'
        '%             qp-m3 制式宏已就位，命制到件时按课时件批1—6 样板展开即入位。\n'
        '% ============================================================\n')
    m = re.search(r'\\end\{multicols\}\s*\n\\end\{document\}\s*$', tex)
    assert m, '%s 件尾锚未命中' % piece
    tex = tex[:m.start()] + upgrade + '\\end{multicols}\n\n\\tailfill\n\\end{document}\n' + tex[m.end():]
    log.append(('升格槽', '考点探究＋课堂评价 G5 结构挂位点（注释槽·不印空节·待裁清单在案）'))
    log.append(('尾块', '\\tailfill 于 \\end{document} 前'))
    return tex, log


def migrate_zhangmo(piece, keys, kmap, m3names, m3bodies):
    tex = read(os.path.join(TREE, piece, 'main.src.tex'))
    log = []
    tex = preamble_swap(tex, piece, m3names, m3bodies, log)
    P = '导-章末'
    z13 = [mm.start() for mm in re.finditer(r'^\\zhankong\{13mm\}', tex, re.M)]
    z6 = [mm.start() for mm in re.finditer(r'^\\zhankong\{6mm\}', tex, re.M)]
    assert len(z13) == 12, '章末书写位锚 z13=%d（须 12）' % len(z13)
    assert len(z6) == 13, '章末书写位锚 z6=%d（须 13：变式12＋高考3 自带书写位）' % len(z6)
    g3 = tex.find('\\liB{高考\\textbf{3}')
    g4 = tex.find('\\liB{高考\\textbf{4}')
    assert 0 < g3 < z6[12] < g4, '第 13 处 \\zhankong{6mm} 非高考3 自带书写位（禁猜停）'
    for i in range(1, 13):
        for pre, mmx in (('例', '13mm'), ('变式', '6mm')):
            k = '%s-%s%d' % (P, pre, i)
            v, ex = kv_of(k, kmap, P)
            lst = [mm.start() for mm in re.finditer(r'^\\zhankong\{%s\}' % mmx, tex, re.M)]
            assert len(lst) >= i, '%s%s%d 书写位重测不足' % (P, pre, i)
            tex = insert_after_line(tex, lst[i - 1], block(k, '%s%d' % (pre, i), v, 'ansnote',
                                      ['\\ansnote{解析}{%s}' % e[1] for e in ex]))
            log.append((k, '\\zhankong{%s} 第 %d 处行后（%s%d 块尾·书写位后）' % (mmx, i, pre, i), v))
    gk = ['%s-高考%d' % (P, i) for i in range(1, 5)]
    assert tex.count('\\zhankong{8mm}') == 1, '高考1 书写位锚不唯一'
    i8 = find1(tex, '\\zhankong{8mm}', 0, '高考1 块尾')
    v, ex = kv_of(gk[0], kmap, P)
    tex = insert_after_line(tex, i8, block(gk[0], '高考1', v, 'ansnote',
                                           ['\\ansnote{解析}{%s}' % e[1] for e in ex]))
    log.append((gk[0], '\\zhankong{8mm} 行后（高考1 块尾）', v))
    icol = find1(tex, '\\columnbreak', 0, '高考2 块尾')
    v, ex = kv_of(gk[1], kmap, P)
    tex = insert_before(tex, icol, block(gk[1], '高考2', v, 'ansnote',
                                         ['\\ansnote{解析}{%s}' % e[1] for e in ex]))
    log.append((gk[1], '\\columnbreak 前（高考2 块尾）', v))
    i4 = find1(tex, '\\liB{高考\\textbf{4}', 0, '高考3 块尾')
    v, ex = kv_of(gk[2], kmap, P)
    tex = insert_before(tex, i4, block(gk[2], '高考3', v, 'ansnote',
                                       ['\\ansnote{解析}{%s}' % e[1] for e in ex]))
    log.append((gk[2], '\\liB{高考4} 前（高考3 块尾）', v))
    em = [mm.start() for mm in re.finditer(r'\\end\{multicols\}', tex)]
    assert len(em) == 3, '章末 \\end{multicols} 计 %d（须 3）' % len(em)
    v, ex = kv_of(gk[3], kmap, P)
    tex = insert_before(tex, em[1], block(gk[3], '高考4', v, 'ansnote',
                                          ['\\ansnote{解析}{%s}' % e[1] for e in ex]))
    log.append((gk[3], '第二个 \\end{multicols} 前（高考4 块尾）', v))
    m = re.search(r'\\end\{multicols\}\s*\n\\end\{document\}\s*$', tex)
    assert m, '章末件尾锚未命中'
    tex = tex[:m.start()] + '\\end{multicols}\n\n\\tailfill\n\\end{document}\n' + tex[m.end():]
    log.append(('尾块', '\\tailfill 于 \\end{document} 前（题型卡 \\vbox×12 保守保留·待裁2）'))
    return tex, log


def main(argv):
    global BODY_EXTRA
    BODY_EXTRA = load_body_extra()
    only = argv[1:]
    todo = [x for x in KS if not only or any(t in x for t in only)]
    groups, kmap = parse_book()
    m3names, m3bodies = qpm3_defs()
    print('答案册导学区组数 %d｜qp-m3 名集 %d（体 %d）' % (len(groups), len(m3names), len(m3bodies)))
    for piece in todo:
        if piece.startswith('课时'):
            keys = sorted(k for k in kmap if k.startswith('导-' + piece))
            tex, log = migrate_keshi(piece, keys, kmap, m3names, m3bodies)
        elif piece.startswith('衔接节'):
            keys = sorted((k for k in kmap if k.startswith('导-衔接')),
                          key=lambda k: int(k.rsplit('-', 1)[-1]))
            tex, log = migrate_xianjie(piece, keys, kmap, m3names, m3bodies)
        else:
            def _zmkey(k):
                m = re.match(r'(.+?)(\d+)$', k.rsplit('-', 1)[-1])
                pre = m.group(1)
                return ({'例': 0, '变式': 1}.get(pre, 2), int(m.group(2)))
            keys = sorted((k for k in kmap if k.startswith('导-章末')), key=_zmkey)
            tex, log = migrate_zhangmo(piece, keys, kmap, m3names, m3bodies)
        tex = ensure_ov(tex, log)
        d = os.path.join(TREE, piece)
        with io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(tex)
        nblk = tex.count('\\begin{ansblock}')
        nanc = len(re.findall(r'^% ans:(\S+)', tex, re.M))
        with io.open(os.path.join(d, '_迁移日志.md'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('# %s 换装迁移日志（正装波1·2026-09-14）\n\n| 键/项 | 锚点 | 值 |\n|---|---|---|\n' % piece)
            for row in log:
                a, b, c = (row + ('',))[:3] if len(row) == 2 else row
                f.write('| %s | %s | %s |\n' % (a, b, str(c).replace('|', '\\|')[:120]))
            f.write('\nansblock %d｜源层锚 %d｜bindpx %d\n'
                    % (nblk, nanc, len(re.findall(r'\\bindpx\s*[{ ]?\\kaishu', tex))))
        print('[迁] %s：键 %d｜ansblock %d｜源锚 %d｜日志 %d 行' % (piece, len(keys), nblk, nanc, len(log)))


if __name__ == '__main__':
    main(sys.argv)
