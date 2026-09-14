# -*- coding: utf-8 -*-
"""盘点：拓展册键集 vs 课时片键集 交集（键↔号语义确认＋同键并存登记用）。只读。"""
import glob
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
RE_B = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]')


def keys(p):
    t = open(p, encoding='utf-8').read()
    return RE_B.findall(t)


ku = keys(CJ + '/拓展册/上册/main.tex')
kd = keys(CJ + '/拓展册/下册/main.tex')
print('拓展上', len(ku), '拓展下', len(kd), '和', len(ku) + len(kd),
      '并集', len(set(ku + kd)))
kj, kl = [], []
for p in glob.glob(CJ + '/导学件/*/main.tex'):
    kj += keys(p)
for p in glob.glob(CJ + '/练习件/*/main.tex'):
    kl += keys(p)
print('导学键', len(kj), '练习键', len(kl), '导学∩练习', len(set(kj) & set(kl)))
sx = sorted(set(ku + kd) & set(kj))
sxl = sorted(set(ku + kd) & set(kl))
print('拓展∩导学', len(sx), sx[:8])
print('拓展∩练习', len(sxl), sxl[:8])
both = sorted(set(sx) & set(sxl))
print('三面同键', len(both), both[:8])
