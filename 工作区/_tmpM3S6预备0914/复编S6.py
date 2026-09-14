# -*- coding: utf-8 -*-
"""S6 销案·回冲复编译（导学件 02/03/10/14/16/17 双档×2 遍，cwd＝片目录，in-place 刷新）。
三零＝err/Overfull/Missing character 全零（Underfull 单列读数）。零 git。
"""
import io, json, os, re, subprocess, sys, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
XETEX = r'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex'
HERE = r'C:/提示词/工作区/_tmpM3S6预备0914'
PIECES = ['课时02', '课时03', '课时10', '课时14', '课时16', '课时17']


def pdir(pid):
    base = os.path.join(CJ, '导学件')
    for d in os.listdir(base):
        if d == pid or d.startswith(pid + '-'):
            return os.path.join(base, d)
    raise SystemExit(pid)


rows = []
t0 = time.time()
for pid in PIECES:
    d = pdir(pid)
    tier = {}
    for tag, shell in (('true', 'main-true.tex'), ('false', 'main-false.tex')):
        ok = True
        for _ in range(2):
            p = subprocess.run([XETEX, '-interaction=nonstopmode', shell], cwd=d, capture_output=True)
            if p.returncode != 0:
                ok = False
        log = open(os.path.join(d, shell.replace('.tex', '.log')), encoding='utf-8', errors='replace').read()
        err = len(re.findall(r'^!', log, re.M))
        over = len(re.findall(r'Overfull', log))
        under = len(re.findall(r'Underfull', log))
        miss = len(re.findall(r'Missing character', log))
        keys = re.findall(r'^M3-ANSKEY: (\S+)', log, re.M)
        figs = len(re.findall(r'figs/[^\s)]+', log))
        mp = re.search(r'Output written on .* \((\d+) pages', log)
        pages = int(mp.group(1)) if mp else -1
        tier[tag] = dict(err=err, over=over, under=under, miss=miss, anskey=len(keys), pages=pages, figs=figs, exit0=ok)
    kt, kf = tier['true'], tier['false']
    three0 = all(kt[k] == 0 and kf[k] == 0 for k in ('err', 'over', 'miss'))
    rows.append(dict(树='导学件', 片=pid, 三零=three0, exit全零=kt['exit0'] and kf['exit0'],
                     true读=[kt['err'], kt['over'], kt['under'], kt['miss']],
                     false读=[kf['err'], kf['over'], kf['under'], kf['miss']],
                     true页=kt['pages'], false页=kf['pages'],
                     ANSKEY=[kt['anskey'], kf['anskey']], figs=kt['figs']))
    print('%s 三零=%s T=%s F=%s 页%d/%d ANSKEY%d/%d figs=%d %.0fs' % (
        pid, three0, rows[-1]['true读'], rows[-1]['false读'],
        kt['pages'], kf['pages'], kt['anskey'], kf['anskey'], kt['figs'], time.time() - t0), flush=True)

json.dump(rows, open(os.path.join(HERE, '复编读数S6.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
bad = [r for r in rows if not (r['三零'] and r['exit全零'] and r['false页'] <= r['true页'] and r['ANSKEY'][0] == r['ANSKEY'][1])]
print('\n异常片：%s' % ([r['片'] for r in bad] or '无'))
