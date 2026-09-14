# -*- coding: utf-8 -*-
"""S4 印前处置·插桩/改号后 复编译三零扫描（双档连编两遍，cwd＝片目录）。
对象：练习件 01/02/06/07/08/12/13/15/18/19 ＋ 导学件 02/12/13/15/17/18/19。
写入：片目录 in-place aux/log/pdf（刷新在位件）＋本目录 复编读数S4.json。零 git。
"""
import io, json, os, re, subprocess, sys, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz

CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
XETEX = r'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex'
HERE = r'C:/提示词/工作区/_tmpM3印前处置0914'

PRACTICE = ['课时01', '课时02', '课时06', '课时07', '课时08', '课时12', '课时13', '课时15', '课时18', '课时19']
GUIDE = ['课时02', '课时12', '课时13', '课时15', '课时17', '课时18', '课时19']


def pdir(tree, pid):
    base = os.path.join(CJ, tree)
    for d in os.listdir(base):
        if d == pid or d.startswith(pid + '-'):
            return os.path.join(base, d)
    raise SystemExit(pid)


rows = []
t0 = time.time()
for tree, pids in (('练习件', PRACTICE), ('导学件', GUIDE)):
    for pid in pids:
        d = pdir(tree, pid)
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
        rows.append(dict(树=tree, 片=pid, 三零=three0, exit全零=kt['exit0'] and kf['exit0'],
                         true读=[kt['err'], kt['over'], kt['under'], kt['miss']],
                         false读=[kf['err'], kf['over'], kf['under'], kf['miss']],
                         true页=kt['pages'], false页=kf['pages'],
                         ANSKEY=[kt['anskey'], kf['anskey']], figs=kt['figs']))
        print('%s-%s 三零=%s T=%s F=%s 页%d/%d ANSKEY%d/%d figs=%d %.0fs' % (
            tree, pid, three0, rows[-1]['true读'], rows[-1]['false读'],
            kt['pages'], kf['pages'], kt['anskey'], kf['anskey'], kt['figs'], time.time() - t0), flush=True)

json.dump(rows, open(os.path.join(HERE, '复编读数S4.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
bad = [r for r in rows if not (r['三零'] and r['exit全零'] and r['false页'] <= r['true页'] and r['ANSKEY'][0] == r['ANSKEY'][1])]
print('\n异常片：%s' % ([r['树'] + r['片'] for r in bad] or '无'))
