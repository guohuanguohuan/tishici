# -*- coding: utf-8 -*-
import re, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/'
RE_CMT = re.compile(r'(?<!\\)%.*$')
for pid in ('课时16-2.7.2抛物线性质', '课时17-2.8①压轴综合一', '课时18-2.8②压轴综合二', '课时19-章末总结与复习'):
    n = 0
    for l in open(BASE + pid + '/main.tex', encoding='utf-8'):
        code = RE_CMT.sub('', l)
        n += len(re.findall(r'\\ding\{51\}', code))
    print(pid.split('-')[0], '正文ding51:', n)
j = json.load(open(BASE + '衔接节/件manifest.json', encoding='utf-8'))
ks = j['冻结manifest键序']
from collections import Counter
print('衔接节27键构成:', dict(Counter(k.split('-')[1] for k in ks)))
