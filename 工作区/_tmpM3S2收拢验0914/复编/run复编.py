# -*- coding: utf-8 -*-
"""M3 S2 波1 收拢验·编译三零复验（双档各连编两遍，沙箱副本）＋渲染面口径复核。
成卷全只读（仅 cp 源件入沙箱）；写入仅 工作区/_tmpM3S2收拢验0914/复编/。零 git。
"""
import io, json, os, re, shutil, subprocess, sys, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz

ROOT = r'C:/提示词'
DJJ = os.path.join(ROOT, '工作区', 'M3-第2章量产0913', '成卷', '导学件')
XETEX = r'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex'
SB = os.path.join(ROOT, '工作区', '_tmpM3S2收拢验0914', '复编')

ORDER = ['衔接节'] + ['课时%02d' % i for i in range(1, 20) if i != 6] + ['课时06B']

def piece_dir(pid):
    return [d for d in os.listdir(DJJ) if d == pid or d.startswith(pid + '-')][0]

rows = []
for pid in ORDER:
    d = piece_dir(pid)
    src = os.path.join(DJJ, d)
    dst = os.path.join(SB, pid)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for f in ('main.tex', 'main-true.tex', 'main-false.tex', 'qp-m3.sty'):
        shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
    # 防外链：体若引用 figs/png 则带上
    body = open(os.path.join(src, 'main.tex'), encoding='utf-8').read()
    if 'includegraphics' in body:
        for sub in ('figs', 'png'):
            if os.path.isdir(os.path.join(src, sub)):
                shutil.copytree(os.path.join(src, sub), os.path.join(dst, sub))
    mani = json.load(open(os.path.join(src, '件manifest.json'), encoding='utf-8'))
    keyseq = mani['冻结manifest键序']
    tier = {}
    ok = True
    for t, shell in (('true', 'main-true.tex'), ('false', 'main-false.tex')):
        for _ in range(2):  # 连编两遍取稳态
            p = subprocess.run([XETEX, '-interaction=nonstopmode', shell],
                               cwd=dst, capture_output=True)
            if p.returncode != 0:
                ok = False
        log = open(os.path.join(dst, shell.replace('.tex', '.log')), encoding='utf-8', errors='replace').read()
        err = len(re.findall(r'^!', log, re.M))
        over = len(re.findall(r'Overfull', log))
        under = len(re.findall(r'Underfull', log))
        miss = len(re.findall(r'Missing character', log))
        keys = re.findall(r'^M3-ANSKEY: (\S+)', log, re.M)
        mp = re.search(r'Output written on .* \((\d+) pages', log)
        pages = int(mp.group(1)) if mp else -1
        tier[t] = dict(err=err, over=over, under=under, miss=miss, keys=keys, pages=pages)
    kt, kf = tier['true'], tier['false']
    seteq = set(kt['keys']) == set(kf['keys'])
    manieq = set(kt['keys']) == set(keyseq)
    pagesok = kf['pages'] <= kt['pages']
    three0 = (kt['err'] == kt['over'] == kt['miss'] == 0 and kf['err'] == kf['over'] == kf['miss'] == 0)
    # 渲染面口径复核（PDF 文本层）
    def text_of(pdf):
        doc = fitz.open(os.path.join(dst, pdf))
        t = '\n'.join(pg.get_text() for pg in doc)
        n = doc.page_count
        doc.close()
        return t, n
    tt, _ = text_of('main-true.pdf')
    tf, fpage = text_of('main-false.pdf')
    tail_true = tt.count('笔记与错题整理')
    tail_false = tf.count('笔记与错题整理')
    ans_true = len(re.findall(r'\d+\.\s*\[答案\]', tt))
    leak = sum(tf.count(w) for w in ('[答案]', '[详解]', '证明见详解'))
    rows.append(dict(片=pid, 目录=d, 三零=three0, true读=[kt['err'], kt['over'], kt['under'], kt['miss']],
                     false读=[kf['err'], kf['over'], kf['under'], kf['miss']],
                     true页=kt['pages'], false页=kf['pages'], 页数false不超true=pagesok,
                     ANSKEY两档集合相等=seteq, ANSKEY键数true=len(kt['keys']), ANSKEY键数false=len(kf['keys']),
                     manifest键数=len(keyseq), ANSKEY等于manifest=manieq,
                     尾块true=tail_true, 尾块false=tail_false, 答案行true=ans_true, 泄答false=leak))
    print('%-8s 三零=%s 读数T=%s F=%s 页%d/%d ANSKEY %d/%d≡manifest%s 尾块%d/%d 答案行%d 泄答%d'
          % (pid, three0, kt and [kt['err'], kt['over'], kt['under'], kt['miss']],
             [kf['err'], kf['over'], kf['under'], kf['miss']], kt['pages'], kf['pages'],
             len(kt['keys']), len(kf['keys']), manieq, tail_true, tail_false, ans_true, leak))

json.dump(rows, open(os.path.join(SB, '复编读数.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
bad = [r for r in rows if not (r['三零'] and r['页数false≤true'] and r['ANSKEY两档集合相等']
                              and r['ANSKEY≡manifest'] and r['尾块true'] == 1 and r['尾块false'] == 1
                              and r['泄答false'] == 0)]
print('\n异常片：%s' % ([r['片'] for r in bad] or '无'))
