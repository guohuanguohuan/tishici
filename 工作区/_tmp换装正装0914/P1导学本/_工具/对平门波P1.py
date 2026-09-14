# -*- coding: utf-8 -*-
r"""对平门波P1.py — 波4a 件级对平（承 M2 对平门波 切丁制）：每件三源＝
①快照丁（值快照按件键切）②册丁（body.tex 契约键按件键切）③件面锚/编译锚（main.tex）。
用法: python 对平门波P1.py   # 5 件全量，读数落 ../_门谱读数/_对平门-件-<件名>.txt
"""
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import 迁移P1导学 as MG

TREE = MG.TREE
PROJ = r'C:/提示词'
GATE = os.path.join(PROJ, '工具', '键账对平门.py')
OUT = os.path.join(TREE, '_门谱读数')
KS = os.path.join(TREE, '_键表')
BODY, SNAP = MG.BODY, MG.SNAP
PIECES = MG.DAOXUE + [MG.ZM]


def piece_keys(piece):
    if piece == MG.ZM:
        return ['导-章末-%d' % n for n in range(1, 6)]
    return MG.expect_keys_ks(MG.DAOXUE.index(piece) + 1)


def run(tag, args):
    r = subprocess.run([sys.executable, GATE] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    txt = (r.stdout or '') + (r.stderr or '')
    io.open(os.path.join(OUT, '_对平门-件-%s.txt' % tag), 'w', encoding='utf-8').write(txt)
    tail = [l for l in txt.splitlines() if l.startswith(('[PASS]', '[FAIL]'))]
    print('[%s] 退出码 %d｜%s' % (tag, r.returncode, (tail[-1] if tail else txt.strip().splitlines()[-1])[:80]))
    return r.returncode


def main():
    os.makedirs(OUT, exist_ok=True)
    body = io.open(BODY, encoding='utf-8').read()
    snap = json.load(io.open(SNAP, encoding='utf-8'))
    book_keys = re.findall(r'^%[ \t]*pair:(\S+)', body, re.M)
    rc = 0
    for piece in PIECES:
        ks = piece_keys(piece)
        io.open(os.path.join(KS, '丁册-件-%s.txt' % piece), 'w', encoding='utf-8', newline='\n').write(
            '\n'.join(k for k in book_keys if k in set(ks)) + '\n')
        io.open(os.path.join(KS, '丁快照-件-%s.json' % piece), 'w', encoding='utf-8', newline='\n').write(
            json.dumps({k: snap[k] for k in ks}, ensure_ascii=False, indent=1))
        rc |= run(piece, ['--ledger', '快照丁=' + os.path.join(KS, '丁快照-件-%s.json' % piece),
                          '--expect', '册丁=' + os.path.join(KS, '丁册-件-%s.txt' % piece),
                          '--piece', '迁件=' + os.path.join(TREE, piece, 'main.tex')])
    print('[对平门波P1 %s]' % ('全过' if rc == 0 else '有红'))
    return rc


if __name__ == '__main__':
    sys.exit(main())
