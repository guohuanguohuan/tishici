# -*- coding: utf-8 -*-
"""调试 01 片键联行。"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:/提示词/工作区/_tmpM3印前处置0914')
import importlib.util
spec = importlib.util.spec_from_file_location('a1', r'C:/提示词/工作区/_tmpM3印前处置0914/A1键联扫描.py')
# 手工复制核心函数，避免整跑
CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'


def pdir(tree, pid):
    base = os.path.join(CJ, tree)
    for d in os.listdir(base):
        if d == pid or d.startswith(pid + '-'):
            return os.path.join(base, d)


prac = open(os.path.join(pdir('练习件', '课时01'), 'main.tex'), encoding='utf-8').read()
guide = open(os.path.join(pdir('导学件', '课时01'), 'main.tex'), encoding='utf-8').read()
for m in re.finditer(r'\\tieside\{([^}]*)\}', prac):
    pass
rows = []
positions = [(m.start(), m.group(1)) for m in re.finditer(r'\\tihao\{(\d+)\}', prac)]
for k, (pos, num) in enumerate(positions):
    end = positions[k + 1][0] if k + 1 < len(positions) else len(prac)
    seg = prac[pos:end]
    mt = re.search(r'\\tieside\{([^}]*)\}', seg)
    mk = re.search(r'\\begin\{ansblock\}\[([^\]]+)\]', prac[pos:end])
    if num in ('10', '13'):
        print('练题%s label=%r key=%r' % (num, mt.group(1) if mt else None, mk.group(1) if mk else None))
gm = re.search(r'\\liB\{变式\\textbf\{13\}\}[^{]*\{([^}]*)\}', guide)
print('导 变式13 label=%r' % (gm.group(1) if gm else None,))
i = guide.find('变式\\textbf{13}')
seg2 = guide[i - 10:i + 400]
print('导 变式13 原文片段=%r' % seg2[:160])
