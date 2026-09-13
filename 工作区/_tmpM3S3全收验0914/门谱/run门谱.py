# -*- coding: utf-8 -*-
"""M3 S3 全收验·门谱全量复跑（对号门strict＋槽宽门双档×21＋键账对平门×21）。
照 S2 收拢验制（工作区/_tmpM3S2收拢验0914/门谱/run门谱.py）改造：对象＝成卷/练习件 21 片。
只读 成卷/题面库 与 成卷/练习件；输出仅落 工作区/_tmpM3S3全收验0914/门谱/。零 git。
"""
import io, json, os, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'C:/提示词'
M3 = os.path.join(ROOT, '工作区', 'M3-第2章量产0913', '成卷')
LXJ = os.path.join(M3, '练习件')
TMUB = os.path.join(M3, '题面库')
MENPU = os.path.join(ROOT, '工作区', '_tmpM3S3全收验0914', '门谱')
KEYTAB = os.path.join(MENPU, '键表')
os.makedirs(KEYTAB, exist_ok=True)

GATE_DUIHAO = os.path.join(TMUB, '对号门.py')
GATE_CEKUAN = os.path.join(ROOT, '工具', 'makebox槽宽门.py')
GATE_DUIPING = os.path.join(ROOT, '工具', '键账对平门.py')

ORDER = ['衔接节'] + ['课时%02d' % i for i in range(1, 20)] + ['课时06B']

def piece_dir(pid):
    for d in os.listdir(LXJ):
        if d == pid or d.startswith(pid + '-'):
            return d
    raise SystemExit('片目录未找到：%s' % pid)

def ledger_of(pdir, pid):
    cands = [f for f in os.listdir(pdir) if f.startswith('值台账') and f.endswith('.json')]
    assert len(cands) == 1, (pid, cands)
    return os.path.join(pdir, cands[0])

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True)
    out = (p.stdout or b'').decode('utf-8', 'replace')
    err = (p.stderr or b'').decode('utf-8', 'replace')
    return p.returncode, out + ('\n[stderr] ' + err if err.strip() else '')

R = []  # 汇总行 (name, rc, tail)

# ---------- ① 对号门 --strict（全 21 片一次，题面库总闸） ----------
rc, out = run([sys.executable, GATE_DUIHAO, '--strict'])
open(os.path.join(MENPU, '对号门-strict-全量.txt'), 'w', encoding='utf-8').write(out)
tail = out.strip().splitlines()[-1] if out.strip() else ''
R.append(('对号门--strict(题面库全量)', rc, tail))
print('① 对号门 --strict exit=%d｜%s' % (rc, tail), flush=True)

# ---------- ② 槽宽门双档 ＋ ③ 键账对平门 逐片 ----------
for pid in ORDER:
    d = piece_dir(pid)
    pdir = os.path.join(LXJ, d)
    mani = json.load(open(os.path.join(TMUB, 'manifest', pid + '.manifest.json'), encoding='utf-8'))
    keyseq = [k for k in mani['键序'] if k.startswith('2章-练-')]
    kt = os.path.join(KEYTAB, '键表-%s-练E16.txt' % pid)
    open(kt, 'w', encoding='utf-8').write('\n'.join(keyseq) + '\n')
    for mode in ('zero-fp', 'strict'):
        rc, out = run([sys.executable, GATE_CEKUAN, pdir, '--mode', mode])
        open(os.path.join(MENPU, '槽宽门-%s-%s.txt' % (mode, pid)), 'w', encoding='utf-8').write(out)
        last = [l for l in out.splitlines() if l.startswith('——') or l.startswith('[PASS') or l.startswith('[FAIL')]
        R.append(('槽宽门-%s｜%s' % (mode, pid), rc, last[-1] if last else ''))
    rc, out = run([sys.executable, GATE_DUIPING,
                   '--ledger', '台账=' + ledger_of(pdir, pid),
                   '--piece', 'true档=' + os.path.join(pdir, 'main-true.tex'),
                   '--piece', 'false档=' + os.path.join(pdir, 'main-false.tex'),
                   '--expect', 'manifest练键序=' + kt])
    open(os.path.join(MENPU, '对平门-%s.txt' % pid), 'w', encoding='utf-8').write(out)
    last = [l for l in out.splitlines() if l.startswith('[PASS') or l.startswith('[FAIL')]
    R.append(('对平门｜%s' % pid, rc, last[-1] if last else ''))
    print('②③ %s 槽宽双档+对平 exit=%d/%d/%d' % (pid,
          R[-3][1], R[-2][1], R[-1][1]), flush=True)

lines = ['＝＝ S3 全收验·门谱复跑汇总 ＝＝']
nbad = 0
for name, rc, tail in R:
    flag = 'PASS' if rc == 0 else 'FAIL'
    if rc != 0:
        nbad += 1
    lines.append('[%s] exit=%d｜%s｜%s' % (flag, rc, name, tail))
lines.append('合计：%d 项门跑，%d 项 exit!=0' % (len(R), nbad))
open(os.path.join(MENPU, '门谱汇总.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
