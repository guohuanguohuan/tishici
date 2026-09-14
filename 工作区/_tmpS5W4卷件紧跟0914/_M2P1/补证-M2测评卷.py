# -*- coding: utf-8 -*-
r"""补证-M2测评卷.py — 证据文件专名化修复：
P1 与 M2 测评卷 basename 同为「测评卷」，举证文件互覆。本件以 .bak_w4（案B 底本）对现件
按重产-回流制.py 同款 question_flow 口径重生成 M2 测评卷举证（专名 M2测评卷），并把 P1 举证改专名。
"""
import importlib.util
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
OUTDIR = r'C:/提示词/工作区/_tmpS5W4卷件紧跟0914/_M2P1'
spec = importlib.util.spec_from_file_location(
    'ch', os.path.join(OUTDIR, '重产-回流制.py'))
ch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch)

B = r'C:/提示词/工作区/_tmp换装正装0914'
old_p = os.path.join(B, 'M2测评滚动/测评卷/main.tex.bak_w4')
new_p = os.path.join(B, 'M2测评滚动/测评卷/main.tex')
lines = ch.read_lines(old_p)
body_l = next(i for i, l in enumerate(lines) if l.rstrip('\r\n') == '\\begin{document}')
app_l = next(i for i, l in enumerate(lines) if '卷末附卷' in l)
newlines = ch.read_lines(new_p)
nb = next(i for i, l in enumerate(newlines) if l.rstrip('\r\n') == '\\begin{document}')

RE_TI = ch.RE_TI
RE_PRELINE = ch.RE_PRELINE
RE_PKG = ch.RE_PKG

# 同重产脚本 question_flow（原样抄录，保证口径一致）
def question_flow(ls, side):
    res, skip_ans = [], False
    for ln in ''.join(ls).splitlines(keepends=True):
        s = ln.rstrip('\r\n')
        st = s.strip()
        if side == 'old' and '卷末附卷' in s:
            break
        if ch.RE_BANNER.match(st):
            continue
        if side == 'new' and '题-答-解析同流（S5-W4 回流制）' in st:
            continue
        if st in ('\\begin{juancols}', '\\end{juancols}', '\\jphead', '\\jplead', '\\newpage',
                  '\\begin{document}', '\\end{document}'):
            continue
        if ch.RE_OPENER.match(st) or ch.RE_GROUP2.match(st) or ch.RE_BARE.match(st):
            continue
        if (re.match(r'^\\ifshowans\\dabiao\\fi', st) or re.match(r'^\\ifshowans\\else', st)
                or '\\anskey{' in st or st == '\\fi'):
            continue
        if st.startswith('\\begin{ansblock}'):
            skip_ans = True
            continue
        if st.startswith('\\end{ansblock}'):
            skip_ans = False
            continue
        if skip_ans:
            continue
        res.append(ln)
    return res

old_flow = question_flow(lines[body_l + 1:app_l], 'old')
new_flow = question_flow(newlines[nb + 1:], 'new')
same = old_flow == new_flow
name = 'M2测评卷'
ev = os.path.join(OUTDIR, '题面零改举证-%s.txt' % name)
with io.open(ev, 'w', encoding='utf-8', newline='') as f:
    f.write('题面零改举证｜%s｜S5-W4 阶段二 回流制重产 2026-09-14（补证：专名化重生成，口径同重产脚本）\r\n' % name)
    f.write('口径：双侧同剔结构件（\\jpthree 三器/\\newpage/页横幅/壳行）＋退役件（速查挂载/\\anskey 补偿）\r\n')
    f.write('＋ansblock（旧附卷块/新内联块整块剔）＋导言宏区；余行逐行比对。底本＝main.tex.bak_w4。\r\n')
    f.write('旧件题流 %d 行 vs 新件题流 %d 行 → %s\r\n\r\n' % (
        len(old_flow), len(new_flow), '逐行一致（零改）' if same else '存在差异！'))
    f.write('—— 旧件题流全文 ——\r\n')
    f.writelines(old_flow)
    f.write('\r\n—— 新件题流全文 ——\r\n')
    f.writelines(new_flow)
print('M2测评卷 举证重生成：%s，一致=%s' % (os.path.basename(ev), same))
assert same

# P1 举证改专名
p1_old = os.path.join(OUTDIR, '题面零改举证-测评卷.txt')
p1_new = os.path.join(OUTDIR, '题面零改举证-P1测评卷.txt')
if os.path.exists(p1_old):
    t = io.open(p1_old, encoding='utf-8', newline='').read()
    assert t.startswith('题面零改举证｜测评卷'), '疑似非 P1 举证（首行异常）'
    t = t.replace('题面零改举证｜测评卷｜', '题面零改举证-P1测评卷｜原文件名互覆修复｜', 1)
    io.open(p1_new, 'w', encoding='utf-8', newline='').write(t)
    os.remove(p1_old)
    print('P1 举证改专名：%s' % os.path.basename(p1_new))
