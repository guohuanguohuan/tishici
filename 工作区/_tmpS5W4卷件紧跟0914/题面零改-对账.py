# -*- coding: utf-8 -*-
r"""题面零改-对账.py — S5-W4 阶段二硬门①：卷件重产「题面字符零改」逐字节对账。
对每卷：bak_w4（旧案B）vs main.tex（新回流制）
  A. 题面流＝\ti/\optline/\qpart/\zuhang/\vgt/\jphead 行，按序逐字节比对（LF 规范一致）；
  B. 答案块＝每键 \begin{ansblock}[键]…\end{ansblock} 全文逐字节比对（原缩进含）；
  C. 退役项盘点：bak 有而新无＝\anskey{、\dabiao、附卷 \ifshowans…参考答案、\jpthree/\jpcol。
exit 0＝全卷零改＋退役落位；否则 exit 1。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
VOLS = {'测评卷': 19, os.path.join('滚动卷', '滚A'): 16, os.path.join('滚动卷', '滚B'): 16}
QRE = re.compile(r'^\\(ti|optline|qpart|zuhang|vgt)\{|^\\jphead$')


def body_zone(tex, endmark):
    i0 = tex.index('\\begin{document}') + len('\\begin{document}')
    i1 = tex.index(endmark) if endmark in tex else tex.index('\\end{document}')
    return tex[i0:i1]


def qstream(tex, endmark):
    out = []
    for ln in body_zone(tex, endmark).split('\n'):
        if QRE.match(ln.strip()):
            out.append(ln)
    return out


def blocks(tex):
    d = {}
    for m in re.finditer(r'\\begin\{ansblock\}\[([^\]]+)\].*?\\end\{ansblock\}', tex, re.S):
        d[m.group(1)] = m.group(0)
    return d


def main():
    bad = 0
    for vol, nkeys in VOLS.items():
        d = os.path.join(BASE, vol)
        bak = io.open(os.path.join(d, 'main.tex.bak_w4'), encoding='utf-8', newline='').read()
        new = io.open(os.path.join(d, 'main.tex'), encoding='utf-8', newline='').read()
        qb, qn = qstream(bak, '% ===================== 卷末附卷'), qstream(new, '\\end{juancols}')
        if qb != qn:
            bad += 1
            diff = [i for i, (a, b) in enumerate(zip(qb, qn)) if a != b]
            print('红｜[%s] 题面流失恒：bak %d 行 vs 新 %d 行，首异位 %s' % (vol, len(qb), len(qn), diff[:3]))
            continue
        bb, bn = blocks(bak), blocks(new)
        if set(bb) != set(bn) or any(bb[k] != bn[k] for k in bb):
            bad += 1
            print('红｜[%s] 答案块非逐字节恒等' % vol)
            continue
        # C. 退役落位
        gone = {
            '\\anskey 补偿': ('\\anskey{' in new, bak.count('\\anskey{')),
            '\\dabiao 定义/调用': ('\\dabiao' in new, bak.count('\\dabiao')),
            '\\jpthree/\\jpcol 零高栏': (('\\jpthree' in new or '\\jpcol{' in new), bak.count('\\jpthree')),
            '卷末附卷参考答案': ('参考答案' in new, bak.count('参考答案')),
            '\\ifshowans\\dabiao\\fi 行': (bool(re.search(r'^\\ifshowans\\dabiao\\fi', new, re.M)), 1),
        }
        left = [k for k, (still, _) in gone.items() if still]
        print('[%s] 题面流 %d 行逐字节恒等｜答案块 %d/%d 键逐字节恒等｜退役残留：%s' % (
            vol, len(qn), len(bn), nkeys, left if left else '无（五项全撤）'))
        if left:
            bad += 1
    if bad:
        sys.exit(1)
    print('对账全绿：三卷题面零改＋答案块逐字节恒等＋退役五项落位')


if __name__ == '__main__':
    main()
