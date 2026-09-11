# -*- coding: utf-8 -*-
r"""句末标点0910 前置取证：body.tex 全件 U+FF0E「．」逐处分类扫描。
分类口径（用户 2026-09-10 拍板A）：
  K1 检测题号「{\numboldjian N}．」＝序号位 → 留
  K2 选项标号「A．/B．/C．/D．」（字母处开括／空格后＝标签位）＝序号位 → 留
  K3 方法标号「方法N．」＝序号位 → 留
  K4 数学式内（行内 \( … \) 域内）→ 留
  T  其余＝句末（陈述/题干/答案句收口，后接 }、\zhuzhu、\par、行末或下一句起头）→ 转「.」
"""
import io, re, sys, os

BODY = sys.argv[1] if len(sys.argv) > 1 else \
    r'C:\提示词\工作区\字替对照-0909\variantF\body.tex'

lines = io.open(BODY, encoding='utf-8').read().split('\n')


def math_ranges(line):
    """行内 math 域（body.tex 无 $、无 display 环境；\\[ 均为表格 \\\\[..] 行距）。"""
    out, i = [], 0
    while True:
        a = line.find('\\(', i)
        if a < 0:
            break
        b = line.find('\\)', a + 2)
        if b < 0:
            break
        out.append((a, b))
        i = b + 2
    return out


RE_OPT = re.compile(r'(?:^|[{( \t])[A-D]$')     # 标签位选项字母（前为开括/空白/行首）
RE_NUM = re.compile(r'\\numboldjian\s*\d\}$')    # 检测题号
RE_FFA = re.compile(r'方法\d$')                  # 方法标号


def classify(line, j):
    pre = line[max(0, j - 24):j]
    for a, b in math_ranges(line):
        if a + 2 <= j < b:
            return 'K4', '数学式内'
    if RE_NUM.search(pre):
        return 'K1', '检测题号序位'
    if RE_OPT.search(pre):
        return 'K2', '选项标号序位'
    if RE_FFA.search(pre):
        return 'K3', '方法标号序位'
    return 'T', '句末'


rows = []
for i, l in enumerate(lines):
    for j, ch in enumerate(l):
        if ch == '．':
            k, why = classify(l, j)
            rows.append((k, why, i + 1, j, l[max(0, j - 12):j], l[j + 1:j + 13]))

cnt = {}
for r in rows:
    cnt[r[0]] = cnt.get(r[0], 0) + 1
n_t = cnt.get('T', 0)
print('body.tex 总行数 %d｜U+FF0E 总处数 %d｜句末转(T) %d｜保留 %d（K1 %s／K2 %s／K3 %s／K4 %s）'
      % (len(lines), len(rows), n_t, len(rows) - n_t,
         cnt.get('K1', 0), cnt.get('K2', 0), cnt.get('K3', 0), cnt.get('K4', 0)))
print()
for r in sorted(rows, key=lambda x: (x[2], x[3])):
    print('%-3s L%-4d col%-4d %-12s | ...%s[．]%s...' % (r[0], r[2], r[3], r[1], r[4], r[5]))
