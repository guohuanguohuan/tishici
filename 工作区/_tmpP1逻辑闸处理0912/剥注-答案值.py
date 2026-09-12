# -*- coding: utf-8 -*-
"""剥注-答案值.py —— 件一：拓展册 main.tex 逐槽注释剥答案值（逻辑闸处理轮 2026-09-12）
规则：只动 % 注释行；删「答案 X／印面答案 X」键值段（含仅注解答案值的尾括注）；
保留槽号/源号/难度与其余随行注记；题面正文/组行/图零改动。
断言硬闸：逐行核对旧文、改动行全为注释行、改后 grep 口径 答案 行数＝4（件头 4 行、无键值）。
"""
import io, re, sys

P = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/拓展册/main.tex"

with io.open(P, "r", encoding="utf-8", newline="") as f:
    lines = f.read().split("\n")

# ---- 1) 显式四行（答案字样不在「｜键值段」结构内的，逐对全行替换） ----
EXPLICIT = [
    # L22 件头用题必办⑧：剥「印面答案 D」键值（值在 批5b值台账 §八-1）
    ("%   复真值启用——垂直性错因＋极向增强错因），印面答案 D；⑨中3＝注记位（A-2 式，题面不重收，\\tielue 略题行承批2 第2题略先例）；",
     "%   复真值启用——垂直性错因＋极向增强错因）；⑨中3＝注记位（A-2 式，题面不重收，\\tielue 略题行承批2 第2题略先例）；"),
    # L149 拓-6 随行注：「构型与答案不变」→「构型不变」（值信息在台账 §一 拓6）
    ("% 　[69]~[78] 原文改录为「均匀球壳双力」（万有引力取等、库仑力偏大），题面随件轻改＝措辞与标点规范化，构型与答案不变。",
     "% 　[69]~[78] 原文改录为「均匀球壳双力」（万有引力取等、库仑力偏大），题面随件轻改＝措辞与标点规范化，构型不变。"),
    # L373 拓-28 随行注：「经答案自洽锁定」→「经自洽锁定」（值在台账 §一 拓28）
    ("% 拓-28｜48题13（块15·g48[207]~[222]）｜中档(选择题)｜答案 B｜M/N 侧序经答案自洽锁定（页图目验在册）",
     "% 拓-28｜48题13（块15·g48[207]~[222]）｜中档(选择题)｜M/N 侧序经自洽锁定（页图目验在册）"),
    # L411 拓-33：切分件括注内「从句删后答案 B 不动」＋尾段「｜答案 B」两处一并剥
    ("% 拓-33｜49题11（块14·g49[173]~[186]）◐切分件（各项「电势相同」从句删后答案 B 不动·被删四从句系真命题，剥出留第10章轮）｜中档(选择题)｜答案 B",
     "% 拓-33｜49题11（块14·g49[173]~[186]）◐切分件（各项「电势相同」从句删·被删四从句系真命题，剥出留第10章轮）｜中档(选择题)"),
]
# 显式对的 1 基行号（断言用）
EXPLICIT_LN = [22, 149, 373, 411]

# ---- 2) 其余 45 条槽注释行：删「｜…答案…」整段（段＝两个全角｜之间且含「答案」键值） ----
SEG = re.compile(r"｜[^｜]*答案[^｜]*(?=｜|$)")

hits = []
for i, ln in enumerate(lines):
    n1 = i + 1
    if n1 in EXPLICIT_LN:
        continue
    if ln.startswith("% 拓-") and "答案" in ln:
        new, k = SEG.subn("", ln)
        if k != 1:
            sys.exit("FATAL 槽行 %d 命中段数=%d 非 1：%s" % (n1, k, ln))
        lines[i] = new
        hits.append(n1)

if len(hits) != 44:
    sys.exit("FATAL 槽行剥注数=%d 预期 44：%s" % (len(hits), hits))

for n1, (old, new) in zip(EXPLICIT_LN, EXPLICIT):
    if lines[n1 - 1] != old:
        sys.exit("FATAL 显式行 %d 旧文不符：\n  实=%s\n  期=%s" % (n1, lines[n1 - 1], old))
    lines[n1 - 1] = new

# ---- 3) 硬闸 ----
changed = EXPLICIT_LN + hits
for n1 in changed:
    if not lines[n1 - 1].startswith("%"):
        sys.exit("FATAL 行 %d 非注释行被改：%s" % (n1, lines[n1 - 1]))
remain = [(i + 1, ln) for i, ln in enumerate(lines) if "答案" in ln]
if len(remain) != 4 or [n for n, _ in remain] != [2, 4, 8, 9]:
    sys.exit("FATAL 改后 答案 行数/行号异常：%s" % (remain,))
for n1, ln in remain:
    if re.search(r"答案[\s　]*[A-DＡ-Ｄ<＜]", ln):
        sys.exit("FATAL 件头行 %d 仍含键值：%s" % (n1, ln))

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))

print("OK 剥注完成：显式 4 行 %s＋槽行 44 行；改后 答案 行=%d（行号 2/4/8/9，件头级、无键值）"
      % (EXPLICIT_LN, len(remain)))
print("改动行号清单：", changed)
