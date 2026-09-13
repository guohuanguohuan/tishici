# -*- coding: utf-8 -*-
"""对平门波.py — M2 导学本 12 件批插首道：键账对平门全量（军师裁：对集合不对数）。

依据：键账对平首跑.md（三源口径＋拓-057 浮键定位＋三哨核销 R1b 退出码 0）。
读数落 _门谱读数/；键表临时件落本树 _键表/（不落项目树其他处）。
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
TUOSHANG = os.path.join(PROJ, '工作区', 'M2-第1章量产0911', '成卷', '拓展册', '上册', 'main.tex')
TUOXIA = os.path.join(PROJ, '工作区', 'M2-第1章量产0911', '成卷', '拓展册', '下册', 'main.tex')
WAIVES = ['--waive', '拓-057@外账',
          '--waive', '导-课时02-探五变式1@键账',
          '--waive', '导-课时03-探四例1@键账']

KS = [('课时%02d' % i, '导-课时%02d' % i, i in (2, 3)) for i in range(1, 11)]
KS += [('衔接节-1.2.1前', '导-衔接', False), ('章末-本章总结提升', '导-章末', False)]


def run(tag, args):
    r = subprocess.run([sys.executable, GATE] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    txt = (r.stdout or '') + (r.stderr or '')
    with io.open(os.path.join(OUT, '_对平门-%s.txt' % tag), 'w', encoding='utf-8') as f:
        f.write(txt)
    tail = [l for l in txt.splitlines() if l.startswith(('[PASS]', '[FAIL]')) or 'FAIL' in l]
    print('[%s] 退出码 %d｜%s' % (tag, r.returncode, (tail[-1] if tail else txt.strip().splitlines()[-1])[:90]))
    return r.returncode


def main():
    os.makedirs(OUT, exist_ok=True)
    rc = 0
    # 0) 门自检（负测3·正测2·用法错1）
    rc |= run('selftest', ['--selftest'])
    # 1) 外账 632 档键表（check_pairs.collect_expected()，只读 import）
    expect = os.path.join(KEYS, 'm2_expect632.txt')
    code = ("import sys,io;sys.path.insert(0,r'%s');"
            "import check_pairs;io.open(r'%s','w',encoding='utf-8').write("
            "'\\n'.join(sorted(check_pairs.collect_expected())))"
            % (os.path.dirname(BOOK), expect))
    r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    assert r.returncode == 0, 'expect 键表生成失败：%s' % r.stderr[-400:]
    n = len(io.open(expect, encoding='utf-8').read().split())
    print('[expect] 四本160档键表 %d 键（拓-057 在外账·撤题跳空在案）' % n)
    # 2) 全量三源（册 pair 631＋键账 json 633＋外账 632；三哨核销＝首跑 R1b 同口径）
    rc |= run('全量', ['--book', '册原=' + BOOK, '--ledger', '快照=' + SNAP,
                     '--expect', '四本160档=' + expect] + WAIVES)
    # 3) 拓区 159↔159（册拓域 ↔ 拓展册上下册实题并集·--keyfmt 拓-{n:03d}；--slice 拓 切册）
    rc |= run('拓区159', ['--book', '册=' + BOOK,
                        '--piece', '拓上=' + TUOSHANG, '--piece', '拓下=' + TUOXIA,
                        '--keyfmt', '拓-{n:03d}', '--slice', '拓'])
    # 4) 逐件 12×（双腿＝册键表切丁 ↔ 值快照切丁——首跑「册切丁↔外账」同制式；
    #    导键首段无件级前缀，--slice 切不到件，故以切丁文件对平）
    body = io.open(BOOK, encoding='utf-8').read()
    book_keys = re.findall(r'^% pair:(\S+)', body, re.M)
    snap = json.load(io.open(SNAP, encoding='utf-8'))
    svals = snap.get('vals', snap)
    for piece, pfx, alias in KS:
        bk = sorted(k for k in book_keys if k.startswith(pfx))
        sv = sorted(k for k in svals if k.startswith(pfx))
        assert len(bk) == len(set(bk)) and sv, '%s 切丁异常 bk=%d sv=%d' % (piece, len(bk), len(sv))
        f1 = os.path.join(KEYS, '丁册-%s.txt' % pfx)
        io.open(f1, 'w', encoding='utf-8').write('\n'.join(bk))
        f2 = os.path.join(KEYS, '丁区-%s.json' % pfx)
        json.dump({'keys': len(sv), 'vals': {k: svals[k] for k in sv}},
                  io.open(f2, 'w', encoding='utf-8'), ensure_ascii=False)
        w = []
        for akey in ('导-课时02-探五变式1', '导-课时03-探四例1'):
            if akey in sv:
                w += ['--waive', akey + '@快照丁']
        rc |= run('件-' + piece, ['--expect', '册丁=' + f1, '--ledger', '快照丁=' + f2] + w)
    print('==== 对平门首道总判：%s（退出码合计位 %d）====' % ('全绿' if rc == 0 else '有红', rc))
    return rc


if __name__ == '__main__':
    sys.exit(main())
