# -*- coding: utf-8 -*-
r"""值守恒门.py — 正装波1 件面值守恒检查（钉值门件侧延伸：迁移只挪位置，值一个不许漂）。

口径：迁移器对 kmap（册解析 parse_book）逐键渲染 block()；本门把每件 main.tex 的
ansblock 区逐块抠出，与「按同 kmap 重新渲染的 block()」逐字比对——
  ①件内 ansblock 总数＝该件键数渲染总数（多＝幻影块，少＝丢块）；
  ②每块体（剥 % ans: 源锚行后）与重渲染块逐字相等（值/标签/附行零漂移）；
  ③块键集合＝键账集合（对集合不对数）。
链路闭合：对平门波（册切丁↔值快照，已绿）＋本门（快照同源 kmap↔件面）＝值零漂移。
用法: python 值守恒门.py   # 全 12 件
退出码: 0＝全过；1＝有红。红线：只读件面，报告落 stdout。
"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from 册解析 import parse_book                                        # noqa: E402
from 迁移引擎 import TREE, KS, qpm3_defs, preamble_swap, block, ensure_ov  # noqa: E402
from 迁移件型 import migrate_keshi, migrate_xianjie, migrate_zhangmo, load_body_extra  # noqa: E402
import 迁移件型 as JT                                                 # noqa: E402


def tex_blocks(tex):
    """[(键, 块体)] —— 抠 \begin{ansblock}[键]…\end{ansblock}，体剥 % ans: 行。"""
    out = []
    for m in re.finditer(r'\\begin\{ansblock\}\[([^\]]+)\]\n(.*?)\\end\{ansblock\}', tex, re.S):
        body = '\n'.join(l for l in m.group(2).split('\n') if not l.startswith('% ans:'))
        out.append((m.group(1), body))
    return out


def main():
    groups, kmap = parse_book()
    m3names, m3bodies = qpm3_defs()
    JT.BODY_EXTRA = load_body_extra()
    bad = 0
    for piece in KS:
        d = os.path.join(TREE, piece)
        tex = io.open(os.path.join(d, 'main.tex'), encoding='utf-8').read()

        def _zmkey(k):
            m = re.match(r'(.+?)(\d+)$', k.rsplit('-', 1)[-1])
            return ({'例': 0, '变式': 1}.get(m.group(1), 2), int(m.group(2)))

        if piece.startswith('课时'):
            keys2 = sorted(k for k in kmap if k.startswith('导-' + piece))
            rtex, _ = migrate_keshi(piece, keys2, kmap, m3names, m3bodies)
        elif piece.startswith('衔接节'):
            keys2 = sorted((k for k in kmap if k.startswith('导-衔接')), key=lambda k: int(k.rsplit('-', 1)[-1]))
            rtex, _ = migrate_xianjie(piece, keys2, kmap, m3names, m3bodies)
        else:
            keys2 = sorted((k for k in kmap if k.startswith('导-章末')), key=_zmkey)
            rtex, _ = migrate_zhangmo(piece, keys2, kmap, m3names, m3bodies)
        rtex = ensure_ov(rtex, [])
        rb = tex_blocks(rtex)
        ab = tex_blocks(tex)
        rk, ak = [k for k, _ in rb], [k for k, _ in ab]
        reds = []
        if len(ab) != len(rb):
            reds.append('块数 %d≠重放 %d' % (len(ab), len(rb)))
        if sorted(ak) != sorted(rk):
            reds.append('键集合 diff：%s' % sorted(set(ak) ^ set(rk)))
        amap = {}
        for k2, body in ab:
            amap.setdefault(k2, []).append(body)
        rmap = {}
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
    print('值守恒门：%s' % ('FAIL %d 件红' % bad if bad else '全过 12 件'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
