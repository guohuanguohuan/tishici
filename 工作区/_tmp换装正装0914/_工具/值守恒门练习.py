# -*- coding: utf-8 -*-
r"""值守恒门练习.py — 波2 件面值守恒（钉值门件侧延伸；波1 值守恒门.py 同制，树＝M2练习本）。

口径：迁移器对 kmap（册解析练习 parse_book_lt）逐键重渲染，与件面 ansblock 逐字比对——
  块数/键集合/块体（剥 % ans: 行）三维全对平＝值零漂移链闭合（册切丁↔快照↔件面）。
用法: python 值守恒门练习.py   # 全 12 件，退出码 0/1
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from 册解析练习 import parse_book_lt                                    # noqa: E402
from 迁移练习件 import TREE, PIECES_LX, PIECES_TUO, migrate_lian, migrate_tuo, qpm3_defs  # noqa: E402


def tex_blocks(tex):
    out = []
    for m in re.finditer(r'\\begin\{ansblock\}\[([^\]]+)\]\n(.*?)\\end\{ansblock\}', tex, re.S):
        body = '\n'.join(l for l in m.group(2).split('\n') if not l.startswith('% ans:'))
        out.append((m.group(1), body))
    return out


def main():
    _, _, kmap = parse_book_lt()
    m3names, m3bodies = qpm3_defs()
    bad = 0
    for piece in PIECES_LX + PIECES_TUO:
        d = os.path.join(TREE, piece)
        tex = io.open(os.path.join(d, 'main.tex'), encoding='utf-8').read()
        if piece in PIECES_LX:
            rtex, _ = migrate_lian(piece, kmap, m3names, m3bodies)
        else:
            rng = (1, 58) if piece == '上册' else (59, 160)
            rtex, _ = migrate_tuo(piece, rng, kmap, m3names, m3bodies)
        rb, ab = tex_blocks(rtex), tex_blocks(tex)
        rk, ak = [k for k, _ in rb], [k for k, _ in ab]
        reds = []
        if len(ab) != len(rb):
            reds.append('块数 %d≠重放 %d' % (len(ab), len(rb)))
        if sorted(ak) != sorted(rk):
            reds.append('键集合 diff：%s' % sorted(set(ak) ^ set(rk)))
        amap, rmap = {}, {}
        for k2, body in ab:
            amap.setdefault(k2, []).append(body)
        for k2, body in rb:
            rmap.setdefault(k2, []).append(body)
        for k2 in sorted(set(ak) & set(rk)):
            if amap[k2] != rmap[k2]:
                reds.append('块体漂移：%s' % k2)
        nre = len(re.findall(r'\\begin\{ansblock\}', tex))
        if nre != len(ab):
            reds.append('begin 计 %d ≠ 成对 %d' % (nre, len(ab)))
        if reds:
            bad += 1
            print('[红] %s：%s' % (piece, '｜'.join(reds)))
        else:
            print('[过] %s：块 %d 键集合＝重放 块体逐字等' % (piece, len(ab)))
    print('值守恒门（练习本）：%s' % ('FAIL %d 件红' % bad if bad else '全过 12 件'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
