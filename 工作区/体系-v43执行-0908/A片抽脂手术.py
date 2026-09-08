# -*- coding: utf-8 -*-
# A片手术：公共规则.md 行内抽脂（体系瘦身0908）
# 约束：行数227不变；只行内替换；②类（历史/沿革/留痕/废止旧口径/解释性注记）全文抽走；
# 抽走处留「〔沿革→留痕档案L{N}〕」；档案逐字存真；重组恒等断言逐行全量。
import subprocess, sys, re, json

ROOT = r"C:\提示词"
SRC = ROOT + r"\公共规则.md"
ARC = ROOT + r"\附则\留痕档案-公共规则.md"
DATE = "2026-09-08"

raw = open(SRC, "rb").read()
text = raw.decode("utf-8")
lines = text.split("\r\n")
assert lines[-1] == "", "文件应以CRLF结尾"
body = lines[:-1]
assert len(body) == 227, f"行数断言失败: {len(body)}"

# 基线断言：盘上文本 ≡ git a6ee541（仓库 blob 存 LF、工作区 CRLF，规范化行尾后比较）
base = subprocess.run(["git", "show", "a6ee541:公共规则.md"], cwd=ROOT,
                      capture_output=True).stdout.decode("utf-8")
assert base.replace("\r\n", "\n") == text.replace("\r\n", "\n"), "盘上文本与基线 a6ee541 不一致，中止"

def L(n):  # 1-based
    return body[n-1]

# 抽走清单：(源行号, 定性, 定位方式)
# exact=逐字跨度；marks=(起标, 止标) 含两端
PLAN = [
    (12, "拍板日期出处注记（用户令日期）", ("exact", "2026-09-06 用户令：")),
    (12, "▽留痕（CLI时代退役与调用核验法去向）", ("marks", "▽留痕：qwen CLI", "K1 留痕；")),
    (12, "沿革注记（现行绑定实例值＋2026-09-05切换实证）", ("marks", "现行绑定 zhipu", "降级切换实证，")),
    (14, "沿革过渡注记（行内追加终止线）", ("marks", "终止线：本批为行内", "改按条款ID承载。")),
    (20, "拍板日期与沿革注记（索引精读制出处）", ("exact", "2026-09-06 用户拍板⑩轮改默认索引精读制；")),
    (20, "▽留痕（外部CLI退役与附属纪律去向，规则本体已驻附则《多脑调用登记》K1）", ("marks", "；▽留痕：2026-09-06 用户令：外部 CLI", "《多脑调用登记》K1 留痕")),
    (21, "拍板日期出处注记（通读举证门增设）", ("exact", "（2026-09-06 用户拍板⑩轮增设）")),
    (22, "拍板日期出处注记（阅读制改默认）", ("exact", "（2026-09-06 用户拍板⑩轮改默认）")),
    (22, "解释性注记（代理粒度溢出症状说明）", ("exact", "（子代理上下文溢出症状＝漏项与幻觉数字）")),
    (50, "拍板日期出处注记（外移降预算）", ("exact", "（2026-09-06 用户拍板外移降预算）")),
    (51, "拍板日期出处注记（外移降预算）", ("exact", "（2026-09-06 用户拍板外移降预算）")),
    (80, "▽留痕（锚定机制废止）", ("marks", "，▽留痕：posOffset", "锚定机制废止")),
    (100, "▽留痕拍板注记（全品首子项连排——细则全式驻附则《全品样张细节清单》§六漏洞①）", ("marks", "（▽留痕：2026-09-08 v4.3 拍板3——", "§六漏洞①留痕）")),
    (105, "拍板日期出处注记（外移降预算）", ("exact", "（2026-09-06 用户拍板外移降预算）")),
    (106, "拍板沿革与v2方向预留注记（0906三连拍板：居中/全品规格/撤销底纹与页眉页脚同串）", ("marks", "**▽2026-09-06 全品对照轮用户拍板（v2 方向预留）**：", "附则《页面与页码细则》届时修订。")),
    (108, "▽留痕（讲练件四类底纹废止——细则驻附则《讲练件底纹减法》）", ("marks", "（▽留痕：讲练件四类底纹废止——", "题块分隔锚改由题干底纹首段承担）")),
    (110, "▽留痕（深蓝字废止——纯灰断言由§7色系总则承载）", ("marks", "**▽留痕：深蓝字", "全体系不再使用**")),
    (111, "色值更正沿革注记（2026-09-06 dated）", ("exact", "2026-09-06 色值更正：22%灰真值＝C7C7C7≈199，")),
    (111, "拍板日期出处注记（色系总则立条出处）", ("exact", "——2026-09-06 全品对照轮用户点名立")),
    (111, "v2改版轮预留处置注记（#ADC2DA届时废止——拍板注记）", ("marks", "，▽至 v2 改版轮处置——", "（若留则一律归纯灰阶）")),
    (154, "解释性沿革注记（syncall旧根说明）", ("exact", "旧提示词根所在同步盘，现已不是任何现行根目录；")),
    (175, "解释性注记（§12标题目的说明）", ("exact", "（防 Word 卡顿、大文件装配缺陷与 GitHub 拒收）")),
    (190, "拍板沿革与▽留痕（复审计不限模型族＋「恒异族」废止——已落注附则《跨脑复审计制》）", ("marks", "；2026-09-06 用户拍板：", "（外移文本已落注）")),
    (199, "拍板日期出处注记（外移降预算）", ("exact", "（2026-09-06 用户拍板外移降预算）")),
]

blocks = []   # (id, srcline, qual, span)
newlines = list(body)
for i, (ln, qual, how) in enumerate(PLAN, start=1):
    line = newlines[ln-1]
    if how[0] == "exact":
        span = how[1]
    else:
        s = line.find(how[1]); assert s >= 0, f"L{ln} 起标未命中: {how[1]}"
        e = line.find(how[2], s); assert e > s, f"L{ln} 止标未命中: {how[2]}"
        span = line[s:e+len(how[2])]
    assert line.count(span) == 1, f"L{ln} 跨度非唯一命中"
    ptr = f"〔沿革→留痕档案L{i}〕"
    newlines[ln-1] = line.replace(span, ptr, 1)
    blocks.append((i, ln, qual, span))

# 判据示例/检测签名保护断言（归①，一字不动）
assert L(63) == newlines[62], "L63 难度判定例被误动"
assert L(71) == newlines[70], "L71 检测签名例被误动"

new_text = "\r\n".join(newlines) + "\r\n"
assert len(newlines) == 227, "行数不变断言失败"

# 档案落盘（逐字存真；原文行单独成行，供重组解析）
arc_lines = [
    "# 留痕档案——公共规则.md（体系瘦身0908·A片行内抽脂）",
    "",
    "- 源文件：公共规则.md（基线 git a6ee541，227 行）",
    f"- 建档日期：{DATE}",
    "- 性质：本档逐字收存 A 片行内抽脂自《公共规则.md》抽离之②类内容（历史沿革／▽留痕／已废止旧口径／拍板日期出处注记／解释性注记）。只搬不改、一字未删；现行有效规范句（①类）一字不动留原行；判据示例与检测签名（L63/L71 等）按规格归①未动。",
    "- 重组法：正文各抽离处留短指针「〔沿革→留痕档案L{N}〕」，按下块「原文（逐字）」回插即可逐字重组基线原行（重组恒等断言脚本全量执行通过）。",
    "- 块头格式：留痕档案L{N}｜来源行｜抽离日期｜定性。",
    "",
]
for i, ln, qual, span in blocks:
    arc_lines.append(f"## 留痕档案L{i}｜来源：公共规则.md L{ln}｜抽离：{DATE}｜定性：{qual}")
    arc_lines.append("原文（逐字）：")
    arc_lines.append(span)
    arc_lines.append("")
arc_text = "\r\n".join(arc_lines)

# 重组恒等断言（机械全量）：现行行＋指针回插 ≡ 基线原行
arc_map = {f"〔沿革→留痕档案L{i}〕": span for i, ln, q, span in blocks}
pat = re.compile("〔沿革→留痕档案L\\d+〕")
bad = []
for idx in range(227):
    cur, orig = newlines[idx], body[idx]
    if cur == orig:
        continue
    recon, pos = [], 0
    for m in pat.finditer(cur):
        recon.append(cur[pos:m.start()])
        recon.append(arc_map[m.group(0)])
        pos = m.end()
    recon.append(cur[pos:])
    if "".join(recon) != orig:
        bad.append(idx+1)
assert not bad, f"重组恒等断言失败行: {bad}"

open(SRC, "wb").write(new_text.encode("utf-8"))
open(ARC, "wb").write(arc_text.encode("utf-8"))

# 实测数字
before_chars = len(text)
after_chars = len(new_text)
before_lines = len(body)
after_lines = len(newlines)
stats = {
    "before": {"lines": before_lines, "chars_incl_newlines": before_chars},
    "after": {"lines": after_lines, "chars_incl_newlines": after_chars},
    "delta_chars": after_chars - before_chars,
    "archive_chars": len(arc_text),
    "blocks": [{"id": f"L{i}", "src": f"L{ln}", "chars": len(sp), "qual": q} for i, ln, q, sp in blocks],
    "recompose": "PASS(227/227)",
}
print(json.dumps(stats, ensure_ascii=False, indent=1))
