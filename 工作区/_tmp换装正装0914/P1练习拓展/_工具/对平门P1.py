# -*- coding: utf-8 -*-
"""对平门P1.py — P1 换装正装波4b 首道：键账对平门（练习 4 件 62 键＋拓展 1 件 46 键＝108 键）。

腿口径：域级三源（册 body.tex `% pair:` 全账 ↔ 值快照 208 键 ↔ check_pairs.collect_expected()
  外账 208，--slice 练,拓 切域；预期无浮键，出浮键即查、悬空停门）＋逐件 5×三源
  （册切丁 ↔ 快照切丁 ↔ 源件实题 \\tihao{n}＋--keyfmt 逐件字面传——{dir} 不可用，目录名是中文件名）。
读数落 _门谱读数/_对平门-*.txt；外账键表与切丁落 _键表/。全 PASS 才进批插。
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # P1练习拓展
PROJ = 'C:/提示词'
GATE = os.path.join(PROJ, '工具', '键账对平门.py')
OUT = os.path.join(HERE, '_门谱读数')
KEYS = os.path.join(HERE, '_键表')
ANS = os.path.join(PROJ, '工作区', 'P1-必修3第9章量产0912', '成卷', '答案册')
BOOK = os.path.join(ANS, 'body.tex')
SNAP = os.path.join(ANS, '值快照.json')
CJ = os.path.join(PROJ, '工作区', 'P1-必修3第9章量产0912', '成卷')
# (件目录, 前缀, keyfmt, 拓切丁判别正则或None)
PIECES = [
    ('9.1电荷', '练-课时91', '练-课时91-{n}', None),
    ('9.2库仑定律', '练-课时92', '练-课时92-{n}', None),
    ('9.3电场电场强度', '练-课时93', '练-课时93-{n}', None),
    ('9.4静电的防止与利用', '练-课时94', '练-课时94-{n}', None),
    ('拓展册', '拓', '拓-{n:03d}', re.compile(r'^拓-\d{3}$')),
]


def run(tag, args):
    r = subprocess.run([sys.executable, GATE] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    txt = (r.stdout or '') + (r.stderr or '')
    with io.open(os.path.join(OUT, '_对平门-%s.txt' % tag), 'w', encoding='utf-8') as f:
        f.write(txt)
    tail = [l for l in txt.splitlines() if ('[PASS]' in l or '[FAIL]' in l)]
    print('[%s] 退出码 %d｜%s' % (tag, r.returncode, (tail[-1] if tail else '无判语')[:100]))
    return r.returncode


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(KEYS, exist_ok=True)
    rc = 0
    # 0) 门自检（负测真拦·正测真放行）
    rc |= run('selftest', ['--selftest'])
    # 1) 外账 208 键表（check_pairs.collect_expected()，只读 import）
    expect = os.path.join(KEYS, 'p1_expect208.txt')
    sys.path.insert(0, ANS)
    import check_pairs                                                    # noqa: E402
    ks = sorted(check_pairs.collect_expected())
    io.open(expect, 'w', encoding='utf-8').write('\n'.join(ks))
    assert len(ks) == len(set(ks)) == 208, '外账键数≠208：%d' % len(ks)
    print('[expect] 四本侧键表 %d 键（练+拓应 108，余导/测侧域外）' % len(ks))
    # 2) 域级全量三源（册↔快照↔外账，--slice 练,拓；预期无浮键）
    rc |= run('域级全量', ['--book', '册原=' + BOOK, '--ledger', '快照=' + SNAP,
                        '--expect', '外账208=' + expect, '--slice', '练,拓'])
    # 3) 逐件 5×三源（册切丁 ↔ 快照切丁 ↔ 源件实题）
    body = io.open(BOOK, encoding='utf-8').read()
    book_keys = re.findall(r'^% pair:(\S+)', body, re.M)
    svals = json.load(io.open(SNAP, encoding='utf-8'))
    for piece, pfx, fmt, rex in PIECES:
        sel = (lambda k: rex.match(k)) if rex is not None else (lambda k: k.startswith(pfx))
        bk = sorted(k for k in book_keys if sel(k))
        sv = sorted(k for k in svals if sel(k))
        assert bk and len(bk) == len(set(bk)) and len(sv) == len(set(sv)), '%s 切丁异常' % piece
        assert len(bk) == len(sv), '%s 册↔快照切丁计数差 %d↔%d（悬空停门）' % (piece, len(bk), len(sv))
        f1 = os.path.join(KEYS, '丁册-%s.txt' % pfx)
        io.open(f1, 'w', encoding='utf-8').write('\n'.join(bk))
        f2 = os.path.join(KEYS, '丁区-%s.json' % pfx)
        json.dump({'keys': len(sv), 'vals': {k: svals[k] for k in sv}},
                  io.open(f2, 'w', encoding='utf-8'), ensure_ascii=False)
        rc |= run('件-' + piece, ['--expect', '册丁=' + f1, '--ledger', '快照丁=' + f2,
                               '--piece', '源件=%s' % os.path.join(CJ, '练习件', piece, 'main.tex')
                                          if pfx.startswith('练') else '源件=%s' % os.path.join(CJ, '拓展册', 'main.tex'),
                               '--keyfmt', fmt])
    print('==== 对平门首道总判（P1 波4b 5 件 108 键）：%s（退出码合计位 %d）===='
          % ('全绿' if rc == 0 else '有红', rc))
    return rc


if __name__ == '__main__':
    sys.exit(main())
