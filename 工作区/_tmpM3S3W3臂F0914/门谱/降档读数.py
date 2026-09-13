# -*- coding: utf-8 -*-
r"""降档读数.py — 课时02/03 练习件·选项槽位降档梯真算读数（槽宽门同源 ink_em 口径）。
对每道选择题：四连排槽宽 0.25\linewidth−0.25\lxhang＝19.10mm（零误报阈 +2.5mm＝21.60mm），
逐槽墨宽估值（\fontsize 10.5pt 档），＞四连排零误报阈者须降档（两连排 37.28mm／单列）。
读数供 值台账「降档登记」＋回执 引用；只读件面，零写入（stdout 报告）。
用法: python 降档读数.py <piece_dir>
"""
import io
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GATE = 'C:/提示词/工具/makebox槽宽门.py'
sys.path.insert(0, os.path.dirname(GATE))
import importlib.util
spec = importlib.util.spec_from_file_location('slotgate', GATE)
sg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sg)

PIECE = sys.argv[1]
LW, LXHANG = 84.0, 7.6
EMU_PT = 10.5                                   # 选项行 \fontsize{10.5pt}
S4 = 0.25 * LW - 0.25 * LXHANG                  # 19.10mm
S2 = 0.5 * LW - 0.5 * LXHANG - 0.25 * EMU_PT / sg.MM2PT  # 两连排 37.28mm
TOL = 7.11 / sg.MM2PT                           # 零误报容差 2.5mm

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
key_seq = re.findall(r'\\begin\{ansblock\}\[([^\]]+)\]', src)
lines = src.split('\n')
cur_tihao, ti_seq = None, []
rows = []
for ln in lines:
    mt = re.search(r'\\tihao\{(\d+)\}', ln)
    if mt:
        cur_tihao = int(mt.group(1))
        ti_seq.append(cur_tihao)
    for sm in sg.RE_SLOT_POS.finditer(sg.strip_comment(ln)):
        content = sg.read_full_group(ln, sm.end() - 1) if hasattr(sg, 'read_full_group') else None
        if content is None:
            # 自切花括号体
            i = sm.end() - 1
            depth, j = 0, i
            s = ln
            while j < len(s):
                if s[j] == '\\' and j + 1 < len(s):
                    j += 2
                    continue
                if s[j] == '{':
                    depth += 1
                elif s[j] == '}':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            content = s[i + 1:j]
        wmm = sg.parse_dimexpr_mm(sm.group(1), EMU_PT, LW, 13.0, LXHANG)
        est_mm = sg.ink_em(content, False) * EMU_PT / sg.MM2PT
        rows.append((cur_tihao, content, wmm, est_mm))

print(f'片＝{os.path.basename(PIECE)}｜四连排槽宽 {S4:.2f}mm＋容差2.5＝{S4 + TOL:.2f}｜'
      f'两连排槽宽 {S2:.2f}mm｜strict 预警 0.85×槽宽（四连排 {0.85 * S4:.2f}／两连排 {0.85 * S2:.2f}）')
byq = {}
for tihao, content, wmm, est in rows:
    byq.setdefault(tihao, []).append((content, wmm, est))
for idx, (tihao, slots) in enumerate(sorted(byq.items())):
    key = key_seq[ti_seq.index(tihao)] if tihao in ti_seq else '?'
    mx = max(e for _, _, e in slots)
    four_ok = mx <= 0.85 * S4
    pos = ('四连排' if four_ok else
           ('两连排' if mx <= 0.85 * S2 else '单列'))
    det = '；'.join(f'{c[:14]}…={e:.1f}mm' if len(c) > 14 else f'{c}={e:.1f}mm'
                    for c, w, e in slots)
    print(f'题{tihao}({key}) 最宽槽 {mx:.1f}mm｜在槽 {slots[0][1]:.2f}mm｜梯位 {pos}｜{det}')
