# -*- coding: utf-8 -*-
"""探针：直接原样复跑旧脚本（片G实测.py）口径，验证能否复现历史 Δ（g3 -3.51/-4.33 等）。"""
import sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
def load(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
lg = load('lg', '片G实测.py')
dm = lg.measure_doc(lg.MAIN)
assert len(dm) == 6, len(dm)
sm = {}
for (tag, sn, wbox, frag) in lg.MAP:
    sm[tag] = lg.measure_src(sn, wbox)
print('片段        旧件内线框        旧素材线框×k      旧Δ            旧件内全墨        旧Δ全墨')
for (tag, sn, wbox, frag), d in zip(lg.MAP, dm):
    m = sm[tag]; k = m['k']
    print('%-9s %6.2f×%6.2f  %6.2f×%6.2f  %+5.2f/%+5.2f  |  %6.2f×%6.2f  %+5.2f/%+5.2f' % (
        tag, d['ww'], d['wh'], m['ww']*k, m['wh']*k, d['ww']-m['ww']*k, d['wh']-m['wh']*k,
        d['fw'], d['fh'], d['fw']-m['fw']*k, d['fh']-m['fh']*k))
