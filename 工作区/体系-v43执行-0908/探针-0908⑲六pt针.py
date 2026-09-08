# -*- coding: utf-8 -*-
"""一次性探针：单测 _测v4断言.py ⑲ 的三个 tex 级 needle 表达式（⑲ 解析尾6pt / N3 探究点独行宏）。
背景：首跑⑲报「解析尾6pt False」「探究点独行宏缺」。qp-blocks.tex :114/:116 均为 \\par\\addvspace{6pt}}，
但 needle 未命中——需定位是 needle 写错还是目标文本形态不同。"""
import re

P = r'C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\qp-blocks.tex'
blkfile = open(P, encoding='utf-8').read()

# --- 现 script 里的原表达式 ---
zhenti_old = '】#4}\\par\\addvspace{6pt}}' in blkfile.replace('【解析】', '】')
jiexi_old = bool(re.search(r'\\newcommand\{\\jiexi\}.*\\addvspace\{6pt\}\}', blkfile, re.S))
tjdnr_old = r'{\fontsize{12pt}{15pt}\selectfont\heibf #2}' in blkfile and '\\par\nopagebreak\\noindent' in blkfile
print('OLD zhenti needle(】#4}…):', zhenti_old)
print('OLD jiexi regex(greedy .*6pt}}):', jiexi_old)
print('OLD tjdnr(\\par\\nopagebreak\\noindent):', tjdnr_old)

# --- 候选新表达式 ---
zhenti_new = '【解析】}#4}\\par\\addvspace{6pt}}' in blkfile
jiexi_lazy = bool(re.search(r'\\newcommand\{\\jiexi\}.*?\\addvspace\{6pt\}\}\}', blkfile, re.S))
jiexi_greedy2 = bool(re.search(r'\\newcommand\{\\jiexi\}.*\\addvspace\{6pt\}\}\}', blkfile, re.S))
tj_p1 = '探究点#1}\\par' in blkfile
tj_p2 = '\\nopagebreak\\noindent{' in blkfile
print('NEW zhenti needle(【解析】}#4}\\par\\addvspace{6pt}}):', zhenti_new)
print('NEW jiexi lazy .*?6pt}}):', jiexi_lazy)
print('NEW jiexi greedy .*6pt}}):', jiexi_greedy2)
print('NEW tjdnr two-part:', tj_p1, tj_p2)

# --- 实文形态取证 ---
for name in ('\\zhenti', '\\jiexi', '\\tjdnr'):
    k = blkfile.find('newcommand{' + name)
    print(f'--- {name} 定义尾部 ---')
    print(repr(blkfile[k:k + 420][-150:]))
