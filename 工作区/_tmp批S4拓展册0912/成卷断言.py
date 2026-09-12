# -*- coding: utf-8 -*-
"""S4 拓展册成卷断言：题号连续／口径零命中／图位闭合／六宏 md5。"""
import io, sys, re, os, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(r'C:/提示词/工作区/M2-第1章量产0911/成卷/拓展册')
ok = True
def chk(name, cond, detail=''):
    global ok
    print(('PASS' if cond else 'FAIL'), name, detail)
    if not cond:
        ok = False

TIHAO = re.compile(r'\\tihao\{(\d+)\}')
TU = re.compile(r'\\tu\{([^}]+)\}\{')

allt = []
for vol, lo, hi, exp in [('上册', 1, 58, 58), ('下册', 59, 160, 102)]:
    txt = open(os.path.join(vol, 'main.tex'), encoding='utf-8').read()
    nums = [int(n) for n in TIHAO.findall(txt)]
    chk('%s \\tihao 计数=%d' % (vol, len(nums)), len(nums) == exp, '期望%d' % exp)
    chk('%s 拓号连续 %03d..%03d' % (vol, lo, hi), nums == list(range(lo, hi + 1)))
    allt += nums
    for w in ['叉乘', '行列式', '导数', '外积']:
        c = txt.count(w)
        chk('%s 题面「%s」零命中' % (vol, w), c == 0, '命中%d' % c)
    figs_ref = set(TU.findall(txt))
    figs_dir = set(os.listdir(os.path.join(vol, 'figs')))
    chk('%s \\tu 引用均在 figs/' % vol, figs_ref <= figs_dir, '缺%s' % (figs_ref - figs_dir))
    unused = figs_dir - figs_ref
    chk('%s figs/ 无冗余图' % vol, not unused, '冗余%s' % unused)

chk('全卷题号合计 160 且连续', len(allt) == 160 and sorted(allt) == list(range(1, 161)))

SRC = r'C:/提示词/工作区/字替对照-0909/靠齐样张-0910/练习线'
macros = ['qp-blocks.tex', 'qp-fonts.tex', 'qp-headfoot.tex', 'qp-layout.tex', 'qp-parts.tex', 'qp-titles.tex']
for vol in ['上册', '下册']:
    bad = []
    for mf in macros:
        h1 = hashlib.md5(open(os.path.join(vol, mf), 'rb').read()).hexdigest()
        h2 = hashlib.md5(open(os.path.join(SRC, mf), 'rb').read()).hexdigest()
        if h1 != h2:
            bad.append(mf)
    chk('%s 六宏 md5 与练习线源一致' % vol, not bad, '不一致:%s' % bad if bad else '')

print('=== 断言总结:', '全部通过' if ok else '存在失败项', '===')
sys.exit(0 if ok else 1)
