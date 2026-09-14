# -*- coding: utf-8 -*-
"""A1 辅证：各片 zsd/tjdnr 分册头＋练习件台账注记（口径权威源判定）。只读。"""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
ORDER = ['衔接节'] + ['课时%02d' % i for i in range(1, 20)] + ['课时06B']


def pdir(tree, pid):
    base = os.path.join(CJ, tree)
    for d in os.listdir(base):
        if d == pid or d.startswith(pid + '-'):
            return os.path.join(base, d)
    raise SystemExit(pid)


for pid in ORDER:
    src = open(os.path.join(pdir('导学件', pid), 'main.tex'), encoding='utf-8').read()
    zsd = re.findall(r'\\zsd\{([一二三四五六])\}\{([^}]*)\}', src)
    tj = []
    for m in re.finditer(r'\\tjdnr\{([一二三四五六])\}\{([^}]*)\}', src):
        if (m.group(1), m.group(2)) not in tj:
            tj.append((m.group(1), m.group(2)))
    pdirp = pdir('练习件', pid)
    led = [f for f in os.listdir(pdirp) if f.startswith('值台账') and f.endswith('.json')]
    kj = json.load(open(os.path.join(pdirp, led[0]), encoding='utf-8')) if led else {}
    note = kj.get('知识点预排注记', '') or kj.get('知识点口径', '') or ''
    print('%-5s zsd=%s' % (pid, '；'.join(a + '=' + b for a, b in zsd) or '无'))
    print('       tjdnr=%s' % ('；'.join(a + '=' + b for a, b in tj) or '无'))
    print('       台账注记=%s' % note[:200])
