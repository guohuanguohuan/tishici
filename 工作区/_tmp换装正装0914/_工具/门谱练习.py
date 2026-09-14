# -*- coding: utf-8 -*-
r"""门谱练习.py — 波2 槽宽门＋[D]＋ANSKEY 恒发 驱动（练习本 12 件；读数落 _门谱读数/）。

  槽宽门 zero-fp：迁后 main.tex 逐件；有旗件加跑 main.src.tex 对照（同读数＝义务总表既有点位随迁，
    迁移零新旗——波1 §一 同证法）。
  [D] 静默溢出审计 --grade zero-fp：main-true.tex／main-pure.tex 逐件双档（log/pdf 同目录自动发现）。
  ANSKEY 恒发：双档 log M3-ANSKEY 键集合互等且＝键账切丁（对号门两档可跑判据②）。
用法: python 门谱练习.py   # 退出码 0/1
"""
import io
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ = r'C:/提示词'
OUT = os.path.join(HERE, '_门谱读数')
KEYS = os.path.join(HERE, '_键表')
TREE = os.path.join(HERE, 'M2练习本')
CAO = os.path.join(PROJ, '工具', 'makebox槽宽门.py')
AUD = os.path.join(PROJ, '工具', '静默溢出审计.py')
PIECES = [('课时%02d' % i, '练-课时%02d' % i, None) for i in range(1, 11)]
PIECES += [('上册', '拓上', (1, 58)), ('下册', '拓下', (59, 160))]


def run_py(script, args, tag):
    r = subprocess.run([sys.executable, script] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', cwd=os.path.dirname(args[0] if args else '.'))
    txt = (r.stdout or '') + (r.stderr or '')
    with io.open(os.path.join(OUT, tag), 'w', encoding='utf-8') as f:
        f.write(txt)
    return r.returncode, txt


def main():
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for piece, pfx, rng in PIECES:
        d = os.path.join(TREE, piece)
        # 槽宽门 zero-fp（迁后件面）
        rc, txt = run_py(CAO, [os.path.join(d, 'main.tex'), '--mode', 'zero-fp'],
                         '_槽宽-%s.txt' % piece)
        nflag = len(re.findall(r'^\[旗', txt, re.M)) or (1 if rc == 1 else 0)
        if rc == 1:
            rc2, txt2 = run_py(CAO, [os.path.join(d, 'main.src.tex'), '--mode', 'zero-fp'],
                               '_槽宽-%s-src对照.txt' % piece)
            same = txt2.count('旗') >= 1 and rc2 == 1
            print('[槽宽] %s：旗 %d（src 对照 %s）' % (piece, nflag, '同读数＝既有随迁' if same else 'DIFF——须核'))
            bad += (not same)
        else:
            print('[槽宽] %s：0 旗 PASS' % piece)
            bad += (rc not in (0,))
        # [D] 双档 zero-fp
        for mode in ('true', 'pure'):
            rc, txt = run_py(AUD, [os.path.join(d, 'main-%s.tex' % mode), '--grade', 'zero-fp'],
                             '_D-%s-%s.txt' % (piece, mode))
            verdict = [l for l in txt.splitlines() if '[FAIL]' in l or '[PASS]' in l or '[WARN]' in l]
            tail = verdict[-1] if verdict else txt.strip().splitlines()[-1][:90]
            print('[D-%s] %s：退出码 %d｜%s' % (mode, piece, rc, tail[:96]))
            bad += (rc not in (0,))
        # ANSKEY 恒发（双档 log ↔ 键账切丁）
        want = [l.strip() for l in io.open(os.path.join(KEYS, '丁册-%s.txt' % pfx), encoding='utf-8')]
        got = {}
        for mode in ('true', 'pure'):
            log = io.open(os.path.join(d, 'main-%s.log' % mode), encoding='utf-8', errors='replace').read()
            got[mode] = re.findall(r'M3-ANSKEY: (\S+)', log)
        ok = sorted(got['true']) == sorted(want) and sorted(got['pure']) == sorted(want)
        print('[ANSKEY] %s：true %d｜pure %d｜键账 %d → %s'
              % (piece, len(got['true']), len(got['pure']), len(want), '恒发 PASS' if ok else 'FAIL'))
        if not ok:
            bad += 1
            print('   diff true：%s' % sorted(set(got['true']) ^ set(want))[:12])
    print('==== 门谱练习（槽宽＋[D]＋ANSKEY）总判：%s ====' % ('全绿' if bad == 0 else '有红 %d' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
