# -*- coding: utf-8 -*-
"""对平门波练习.py — M2 练习本 12 件批插首道：键账对平门全量（正装波2·对集合不对数）。

依据：对平门波.py（波1 同制）；义务总表 §一.2（319 键＝练 160＋拓 159）；试迁报告-练习本 §六.2
     （键账对平前置，悬空即停门）。读数落 _门谱读数/；切丁件落 _键表/。
腿口径：逐件三源＝册切丁 ↔ 值快照切丁 ↔ 源件实题（\\tihao{n}＋--keyfmt 练-{dir}-{n}／拓-{n:03d}）；
     迁移前源件无 % ans: 锚（首道即批插前门），实题腿即件面锚侧。
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ = r'C:/提示词'
GATE = os.path.join(PROJ, '工具', '键账对平门.py')
OUT = os.path.join(HERE, '_门谱读数')
KEYS = os.path.join(HERE, '_键表')
BOOK = os.path.join(PROJ, '工作区', 'M2-第1章量产0911', '成卷', '答案册', 'body.tex')
SNAP = os.path.join(PROJ, '工作区', 'M2-第1章量产0911', '成卷', '答案册', '值快照.json')
SRC_LX = os.path.join(PROJ, '工作区', 'M2-第1章量产0911', '成卷', '练习件')
SRC_TUO = os.path.join(PROJ, '工作区', 'M2-第1章量产0911', '成卷', '拓展册')
WAIVE_FULL = ['--waive', '拓-057@四本160档']

KS = [('课时%02d' % i, '练-课时%02d' % i, None) for i in range(1, 11)]
KS += [('上册', '拓上', (1, 58)), ('下册', '拓下', (59, 160))]


def run(tag, args):
    r = subprocess.run([sys.executable, GATE] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    txt = (r.stdout or '') + (r.stderr or '')
    with io.open(os.path.join(OUT, '_对平门-%s.txt' % tag), 'w', encoding='utf-8') as f:
        f.write(txt)
    tail = [l for l in txt.splitlines() if l.startswith(('[PASS]', '[FAIL]')) or 'FAIL' in l]
    print('[%s] 退出码 %d｜%s' % (tag, r.returncode, (tail[-1] if tail else txt.strip().splitlines()[-1])[:96]))
    return r.returncode


def main():
    os.makedirs(OUT, exist_ok=True)
    rc = 0
    # 0) 门自检（负测真拦·正测真放行）
    rc |= run('selftest', ['--selftest'])
    # 1) 外账 632 档键表（check_pairs.collect_expected()，只读 import；波1 同源）
    expect = os.path.join(KEYS, 'm2_expect632.txt')
    code = ("import sys,io;sys.path.insert(0,r'%s');"
            "import check_pairs;io.open(r'%s','w',encoding='utf-8').write("
            "'\\n'.join(sorted(check_pairs.collect_expected())))"
            % (os.path.dirname(BOOK), expect))
    r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    assert r.returncode == 0, 'expect 键表生成失败：%s' % r.stderr[-400:]
    n = len(io.open(expect, encoding='utf-8').read().split())
    print('[expect] 四本160档键表 %d 键' % n)
    # 2) 练习本域全量三源（册↔快照↔外账，--slice 练,拓 切域；拓-057 外账浮键挂哨）
    rc |= run('练习域全量', ['--book', '册原=' + BOOK, '--ledger', '快照=' + SNAP,
                          '--expect', '四本160档=' + expect,
                          '--slice', '练,拓'] + WAIVE_FULL)
    # 3) 逐件 12×（三源：册切丁 ↔ 快照切丁 ↔ 源件实题）
    body = io.open(BOOK, encoding='utf-8').read()
    book_keys = re.findall(r'^% pair:(\S+)', body, re.M)
    snap = json.load(io.open(SNAP, encoding='utf-8'))
    svals = snap.get('vals', snap)
    for piece, pfx, rng in KS:
        srcdir = os.path.join(SRC_LX if pfx.startswith('练') else SRC_TUO, piece)
        fmt = '练-{dir}-{n}' if pfx.startswith('练') else '拓-{n:03d}'
        bk = sorted(k for k in book_keys if k.startswith(pfx)) if rng is None else \
            sorted(k for k in book_keys
                   if re.match(r'^拓-\d{3}$', k) and rng[0] <= int(k.split('-')[1]) <= rng[1])
        sv = sorted(k for k in svals if k.startswith(pfx)) if rng is None else \
            sorted(k for k in svals
                   if re.match(r'^拓-\d{3}$', k) and rng[0] <= int(k.split('-')[1]) <= rng[1])
        assert len(bk) == len(set(bk)) and len(sv) == len(set(sv)) and sv, '%s 切丁异常' % piece
        assert len(bk) == len(sv), '%s 册↔快照切丁计数差 %d↔%d（悬空停门）' % (piece, len(bk), len(sv))
        f1 = os.path.join(KEYS, '丁册-%s.txt' % pfx)
        io.open(f1, 'w', encoding='utf-8').write('\n'.join(bk))
        f2 = os.path.join(KEYS, '丁区-%s.json' % pfx)
        json.dump({'keys': len(sv), 'vals': {k: svals[k] for k in sv}},
                  io.open(f2, 'w', encoding='utf-8'), ensure_ascii=False)
        rc |= run('件-' + piece, ['--expect', '册丁=' + f1, '--ledger', '快照丁=' + f2,
                                '--piece', '源件=%s' % os.path.join(srcdir, 'main.tex'),
                                '--keyfmt', fmt])
    print('==== 对平门首道总判（练习本 12 件）：%s（退出码合计位 %d）====' % ('全绿' if rc == 0 else '有红', rc))
    return rc


if __name__ == '__main__':
    sys.exit(main())
