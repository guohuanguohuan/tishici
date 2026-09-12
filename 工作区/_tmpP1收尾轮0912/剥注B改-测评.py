# -*- coding: utf-8 -*-
r"""剥注B改-测评.py —— 收尾轮A·测评卷 main.tex 一次性改动执行器（断言闸，照处理轮「剥注-答案值.py」纪律）。

三组改动，全部先验后写（任一断言不符即中止不写盘）：
  甲＝题10 B 项「拉力不变」→「拉力（矢量）不变」（分支乙·源裁＝矢量口径/CD）；
  乙＝题10 C 项补「（指大小）」——与拓展册拓-17 双印同题对齐（处理轮已在拓展册落，本卷未同步）；
  丙＝剥 14 条题槽行注「｜答案 X」键值段（保留题号/源号/分值/难度注记）
      ＋件头 6 行改写去「答案」字（信息零丢失：卷名形制、速查登记、唯一依据句全部在位）。
断言改后：含「答案」行集＝{2,18,158,163}（件头级 2＋\dabiao 印面宏体 2＝设计内保留）；
总行数不变；\dabiao 宏体两行逐字未动。
"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\提示词\工作区\P1-必修3第9章量产0912\成卷\测评卷\main.tex'
lines = open(P, encoding='utf-8').read().split('\n')
n0 = len(lines)
errs = []


def chk(lineno, old_sub):
    """1 基行号，该行必须整行等于 old_sub。"""
    cur = lines[lineno - 1]
    if cur != old_sub:
        errs.append(f'行{lineno} 旧文不符:\n  期望={old_sub!r}\n  实得={cur!r}')
        return False
    return True


# ---------- 甲：B 项（矢量） ----------
OLD_B = r'  \optline{\optII{A．$B$ 球的电荷量不变；}{B．轻绳对 $B$ 球的拉力不变；}}'
NEW_B = r'  \optline{\optII{A．$B$ 球的电荷量不变；}{B．轻绳对 $B$ 球的拉力（矢量）不变；}}'
if chk(242, OLD_B):
    lines[241] = NEW_B

# ---------- 乙：C 项（指大小）双印同步 ----------
OLD_C = r'  \optline{\optII{C．$A$、$B$ 两球间库仑力增大；}{D．$A$、$B$ 两球间距离增大}}'
NEW_C = r'  \optline{\optII{C．$A$、$B$ 两球间库仑力增大（指大小）；}{D．$A$、$B$ 两球间距离增大}}'
if chk(243, OLD_C):
    lines[242] = NEW_C

# ---------- 丙-1：14 条题槽行注剥「｜答案 X」 ----------
SLOT = [175, 182, 188, 194, 199, 204, 212, 218, 229, 239, 244, 255, 259, 268]
stripped = 0
for ln in SLOT:
    cur = lines[ln - 1]
    m = re.match(r'^(\s*%\s*题\d+｜.*?｜(?:单选|多选|填空|解答) \d+ 分)｜答案 .+$', cur)
    if not m:
        errs.append(f'行{ln} 非预期槽注形: {cur!r}')
        continue
    lines[ln - 1] = m.group(1)
    stripped += 1

# ---------- 丙-2：件头 6 行改写（去「答案」字、信息不丢） ----------
HEAD = {
    8:  (r'%   \setlength{\headwidth}{\textwidth}（骨架 README §四-C 坑规）。卷末「答案速查」承 M2 数学测评卷先例',
         r'%   \setlength{\headwidth}{\textwidth}（骨架 README §四-C 坑规）。卷末速查表（「××速查」印面题名见宏体）承 M2 数学测评卷先例'),
    9:  (r'%   （看板八十三⑤登记项），本件因 12~14 题答案含长单位式与三空，19 列单表必 Overfull →',
         r'%   （看板八十三⑤登记项），本件因 12~14 题取值含长单位式与三空，19 列单表必 Overfull →'),
    16: (r'%   卷面零答案零标签、题侧标不印）、3 题照抄 成卷/拓展册 成品（拓43→测8、拓17→测10、拓40→测13）；',
         r'%   卷面零键值零标签、题侧标不印）、3 题照抄 成卷/拓展册 成品（拓43→测8、拓17→测10、拓40→测13）；'),
    17: (r'%   16＋3＝19 题闭合；全部答案值以各批值台账为唯一依据。',
         r'%   16＋3＝19 题闭合；全部取值以各批值台账为唯一依据。'),
    155: (r'% 卷末答案速查（承 M2 数学测评卷先例＝全品式登记项；式＝选择题 1~11 列单表＋填空/解答流水行，见头注）',
          r'% 卷末速查表（承 M2 数学测评卷先例＝全品式登记项；式＝选择题 1~11 列单表＋填空/解答流水行，见头注）'),
    281: (r'% ===================== 第 3 页（栏1 题17；栏2 题18；栏3 题19＋答案速查） =====================',
          r'% ===================== 第 3 页（栏1 题17；栏2 题18；栏3 题19＋卷末速查） ====================='),
}
for ln, (old, new) in HEAD.items():
    if chk(ln, old):
        lines[ln - 1] = new

# ---------- 改后终态断言 ----------
if not errs:
    hit = sorted(i + 1 for i, l in enumerate(lines) if '答案' in l)
    if hit != [2, 18, 158, 163]:
        errs.append(f'改后含「答案」行集 {hit} ≠ [2,18,158,163]')
    if len(lines) != n0:
        errs.append(f'行数 {len(lines)} ≠ {n0}')
    if '答案速查}' not in lines[157] or not lines[162].startswith(r'  答案 & B & A & C & D & C & D & B & D & AC & CD & AC'):
        errs.append('\\dabiao 印面宏体两行（158/163）被误动')
    for i, l in enumerate(lines):
        if re.match(r'^\s*%\s*题\d+｜.*｜答案', l):
            errs.append(f'行{i+1} 槽注键值残留: {l!r}')

if errs:
    print('中止，未写盘。断言不符：')
    for e in errs:
        print(' -', e)
    sys.exit(1)

open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print(f'写盘完成：行数 {n0} 不变；剥槽注 {stripped} 条；件头改写 {len(HEAD)} 行；B/C 项 2 行。')
print('含「答案」终态行集＝', hit, '（件头级 2/18＋\\dabiao 印面 158/163）')
