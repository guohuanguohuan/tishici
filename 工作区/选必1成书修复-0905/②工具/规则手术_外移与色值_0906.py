# -*- coding: utf-8 -*-
"""规则手术（2026-09-06，主脑执行）：
B1 公共规则外移 L49/L50/L101/L180/L189 → 4 件新附则（原位留指针、行数不变 218）；
B3 L180「恒异族」前提随用户拍板废止（外移文本落注改写）；
B2 色值更正 C9C9C9→C7C7C7（22%灰真值）＋灰度签名 201→199（公共规则/摘要/底纹减法/经验档）；
经验档毕业退役制立规＋新经验写入＋字数平压缩。
任一断言失败即整体不写盘（先验后写）。
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(r"C:\提示词")
GG = ROOT / "公共规则.md"
ZY = ROOT / "公共规则·目录摘要.md"
JF = ROOT / "附则" / "讲练件底纹减法.md"
JY = ROOT / "ai自行经验积累.md"

for f in (GG, ZY, JF, JY):
    shutil.copy2(f, f.with_suffix(f.suffix + ".bak_规则手术0906"))

report = []

# ============ 1. 公共规则.md：取行＋断言 ============
data = GG.read_text(encoding="utf-8")
crlf = "\r\n" in data
lines = data.split("\n")
assert len(lines) == 218, f"公共规则行数 {len(lines)}≠218"


def gl(n):
    return lines[n - 1].rstrip("\r")


prefix = {
    49: "- 多会话并行纪律",
    50: "- git 仓库损坏处置",
    101: "- 页面：**页边距上下左右必须是1.5厘米",
    180: "- 独立复审计",
    189: "- 导出方式（主路径）",
}
for n, p in prefix.items():
    assert gl(n).startswith(p), f"L{n} 前缀不符：{gl(n)[:40]}"
src = {n: gl(n)[2:] for n in prefix}  # 去行首 "- "
report.append("外移行字符数：" + "，".join(f"L{n}={len(src[n])}" for n in sorted(src)))
chars_before = len(data)

# ============ 2. L180 改写（B3/B4 拍板落注） ============
t = src[180]
subs180 = [
    ("由未参与原任务的异族审计代理执行", "由未参与原任务的审计代理执行", False),
    ("复审计者与任务执行者不得同模型族",
     "复审计者与任务执行者不为同一代理、模型族不设限〔2026-09-06 用户拍板废止「恒异族」前提〕", False),
    (r"〔qwen3\.8-flash/思考max〕，与执行者kimi族恒异.✓——若执行者族变更为qwen族则无异族臂、fail-closed报用户另案",
     "〔型号随当轮登记——2026-09-06 拍板不限模型种类、升档议作废〕", True),
    ("由未参与且异族代理（复测类权限", "由未参与之代理（复测类权限", False),
]
for old, new, is_re in subs180:
    if is_re:
        t, k = re.subn(old, new, t)
    else:
        k = t.count(old)
        t = t.replace(old, new)
    assert k == 1, f"L180 改写锚不唯一({k})：{old[:30]}"
src[180] = t
report.append("L180 改写 4 处全落地")

# ============ 3. 指针行替换（保持 218 行不变） ============
ptr = {
    49: "- （外移附则）多会话并行纪律①-⑨／工具版本预检（先更后用）／占用预检／工具使用后残留清查——全文外移驻附则《多机协作与工具纪律》，效力不变、本节各引用照旧（2026-09-06 用户拍板外移降预算）。",
    50: "- （外移附则）git 仓库损坏处置——全文外移驻附则《多机协作与工具纪律》，效力不变（2026-09-06 用户拍板外移降预算）。",
    101: "- （外移附则）页面设置（边距1.5cm/A4）／版面分栏双栏制／页脚页码部分独立页码制／页眉与节名锚机制——全文外移驻附则《页面与页码细则》，效力不变、本节各引用照旧（2026-09-06 用户拍板外移降预算）。",
    180: "- （外移附则）独立复审计（跨脑复审计制）——全文外移驻附则《跨脑复审计制》，效力不变、本节各引用照旧；2026-09-06 用户拍板：复审计与商议体不限模型族，原「与执行者恒异族」前提废止（外移文本已落注）。",
    189: "- （外移附则）导出方式（Word 直导主路径＋PDFCreator 打印链备胎）——全文外移驻附则《PDF导出链》，效力不变、本节各引用照旧（2026-09-06 用户拍板外移降预算）。",
}
tail = "\r" if crlf else ""
for n, p in ptr.items():
    lines[n - 1] = p + tail
text = "\n".join(lines)

# ============ 4. 公共规则：色值更正（B2） ============
n_hex = text.count("C9C9C9")
assert n_hex == 14, f"公共规则 C9C9C9 计数 {n_hex}≠14"
text = text.replace("C9C9C9", "C7C7C7")
old104 = "／内容标记族201／题干底纹242"
new104 = ("／内容标记族199〔2026-09-06 色值更正：22%灰真值＝C7C7C7≈199，"
          "C9C9C9/201 降为存量过渡签名值、④轮改色完成后旧件应＝0——CB-4〕／题干底纹242")
assert text.count(old104) == 1
text = text.replace(old104, new104)
old105 = "（C7C7C7≈201）压于242底上"
assert text.count(old105) == 1
text = text.replace(old105, "（C7C7C7≈199）压于242底上")
report.append(f"公共规则 C9→C7 {n_hex} 处＋201→199 两处（L104 含注记）")

GG.write_text(text, encoding="utf-8")
chars_after = len(text)
report.append(f"公共规则字符 {chars_before}→{chars_after}（预算 50,000：{'达标' if chars_after <= 50000 else '仍超 ' + str(chars_after - 50000)}）")

# ============ 5. 四件新附则 ============
annex = {
    "多机协作与工具纪律.md": (
        "# 多机协作与工具纪律（附则；外移自公共规则§4 L49/L50，2026-09-06 用户拍板外移降预算，原文逐字保留）\n\n"
        "> 原语境注记：文中「本节」＝公共规则§4（git、多机与多会话纪律）、「下条」＝本附则 git 仓库损坏处置条；"
        "「§N」内指公共规则照旧。效力与原位相同，公共规则§4 原位留指针。\n\n"
        "## 多会话并行纪律／工具版本预检（先更后用）／占用预检／工具使用后残留清查（原 L49）\n\n"
        + src[49] + "\n\n## git 仓库损坏处置（原 L50）\n\n" + src[50] + "\n"),
    "页面与页码细则.md": (
        "# 页面与页码细则（附则；外移自公共规则§7 L101，2026-09-06 用户拍板外移降预算，原文逐字保留）\n\n"
        "> 原语境注记：文中「§5/§11/§14」等内指公共规则照旧；附则《双栏首页断言》《表格规范》《节标题栏顶规则》引用不变。"
        "效力与原位相同，§7 原位留指针。\n\n"
        + src[101] + "\n"),
    "跨脑复审计制.md": (
        "# 跨脑复审计制（附则；外移自公共规则§13 L180，2026-09-06 用户拍板外移降预算；同拍板两处改写已落注："
        "复审计/商议体不限模型族、「与执行者恒异族」前提废止）\n\n"
        "> 原语境注记：文中「§1/§2/§13」「K1」内指照旧（K1 块驻附则《多脑调用登记》）；"
        "原「公共规则§13 资格门先归因后顺延」等引用改指本附则。公共规则§13 原位留指针。\n\n"
        + src[180] + "\n"),
    "PDF导出链.md": (
        "# PDF 导出链（附则；外移自公共规则§14 L189，2026-09-06 用户拍板外移降预算，原文逐字保留）\n\n"
        "> 原语境注记：文中「附则《故障先修纪律》」等引用照旧；公共规则§14 原位留指针。\n\n"
        + src[189] + "\n"),
}
for name, body in annex.items():
    (ROOT / "附则" / name).write_text(body, encoding="utf-8")
report.append("新附则 4 件已写：" + "、".join(annex))

# ============ 6. 目录摘要刷新 ============
z = ZY.read_text(encoding="utf-8")
zcrlf = "\r\n" in z
zsep = "\r\n" if zcrlf else "\n"
rows49 = ["- L49｜§4｜多会话并行纪律①整体提交｜整体 add 含他人改动，异常先按§10②处理",
          "- L49｜§4｜多会话并行纪律②-⑦｜他人文件不碰/并发预检锁/冲突双边保留/禁全局杀进程/子文件夹命名/损坏急停",
          "- L49｜§4｜工具版本预检（先更后用）｜每轮首用外部软件先更新再验可运行，落盘三段式",
          "- L49｜§4｜占用预检｜资源被占一直等释放（30秒复查），绝不催促禁强杀",
          "- L49｜§4｜工具使用后残留清查⑨｜用完清查进程/临时产物/锁句柄/系统状态四类残留",
          "- L50｜§4｜git 仓库损坏处置｜缺对象回填法优先；浅克隆备用；成品恢复；repack；重建"]
new4950 = ["- L49｜§4｜〔外移〕多会话并行纪律①-⑨/版本预检（先更后用）/占用预检/残留清查｜全文＝附则《多机协作与工具纪律》（2026-09-06 外移降预算、原位留指针）",
           "- L50｜§4｜〔外移〕git 仓库损坏处置｜全文＝附则《多机协作与工具纪律》（缺对象回填/浅克隆/成品恢复/repack/重建）"]
rows101 = ["- L101｜§7｜页面设置＋版面分栏（双栏制）｜边距1.5cm/A4；正文双栏；头部单栏区；节标题栏顶照附则《节标题栏顶规则》",
           "- L101｜§7｜页脚页码规范（部分独立页码制）｜PAGE 复杂域；NUMPAGES 禁用；盖章脚本写死",
           "- L101｜§7｜页眉＋节名锚机制｜页眉页脚同串左对齐；STYLEREF「节名锚」抓节名；域行为口径"]
new101 = ["- L101｜§7｜〔外移〕页面设置/双栏制/部分独立页码制/页眉与节名锚机制｜全文＝附则《页面与页码细则》（2026-09-06 外移降预算、原位留指针）"]
rows180 = ["- L180｜§13｜独立复审计（跨脑复审计制）｜异族代理实测重测；族别判读；臂池 qwen 独存；资格门先归因后顺延",
           "- L180｜§13｜高危清单当场复测＋抽样配方＋同册横向一致性diff｜七类高危当场重测；3项抽样配方；件间差异即缺陷信号"]
new180 = ["- L180｜§13｜〔外移〕独立复审计（跨脑复审计制，含高危当场复测/抽样配方/同册横向diff）｜全文＝附则《跨脑复审计制》；2026-09-06 拍板不限模型族、异族前提废止"]
row189 = "- L189｜§14｜导出方式（主路径 Word 直导）｜直导必开书签（CreateBookmarks）；备胎链＝打印链；spawn前清GS_LIB"
new189 = "- L189｜§14｜〔外移〕导出方式（Word 直导主路径＋PDFCreator 打印链备胎）｜全文＝附则《PDF导出链》（2026-09-06 外移降预算、原位留指针）"
for olds, news in [(rows49, new4950), (rows101, new101), (rows180, new180), ([row189], [new189])]:
    block = zsep.join(olds)
    assert z.count(block) == 1, f"摘要行块未唯一命中：{olds[0][:24]}"
    z = z.replace(block, zsep.join(news))
nz_hex = z.count("C9C9C9")
assert nz_hex == 4, f"摘要 C9C9C9 计数 {nz_hex}≠4"
z = z.replace("C9C9C9", "C7C7C7")
new_bytes = len(text.encode("utf-8"))
old_h = "（147,370 字节，CRLF；218 行"
assert z.count(old_h) == 1
z = z.replace(old_h, f"（{new_bytes:,} 字节，CRLF；218 行")
old_d = "后现行文本逐行重核刷新）"
assert z.count(old_d) == 1
z = z.replace(old_d, "后现行文本逐行重核刷新）；2026-09-06 外移轮刷新（L49/L50/L101/L180/L189 外移附则＋色值更正 C7C7C7≈199）")
ZY.write_text(z, encoding="utf-8")
report.append(f"摘要行块替换 4 组＋C9→C7 {nz_hex} 处＋源文件字节数刷新为 {new_bytes:,}")

# ============ 7. 讲练件底纹减法 ============
j = JF.read_text(encoding="utf-8")
nj = j.count("C9C9C9")
assert nj == 3, f"底纹减法 C9C9C9 计数 {nj}≠3"
j = j.replace("C9C9C9", "C7C7C7")
assert j.count("PDF侧201灰度值") == 1
j = j.replace("PDF侧201灰度值", "PDF侧199灰度值")
JF.write_text(j, encoding="utf-8")
report.append("底纹减法 C9→C7 3 处＋201→199 一处")

# ============ 8. 经验档：毕业退役制＋写入＋字数平 ============
y = JY.read_text(encoding="utf-8")
y_before = len(y)
edits = [
    ("≤200行≤12,000字符；旧体系条目下次收尾压缩为1行。",
     "≤200行≤12,000字符；旧体系条目下次收尾压缩为1行。**毕业退役制（2026-09-06拍板）：固化进规则/附则的条目删正文留指针；低频旧条目外移看板档案冷档；本档只留现役未固化经验**"),
]
for old, new in edits:
    assert y.count(old) == 1, f"经验档锚不唯一：{old[:20]}"
    y = y.replace(old, new)
ny_hex = y.count("C9C9C9")
assert ny_hex >= 5, f"经验档 C9C9C9 计数 {ny_hex}"
y = y.replace("C9C9C9", "C7C7C7")
pairs = [
    ("＝22%灰（201）", "＝22%灰（199）"),
    ("灰度201（旧值A6A6A6=166、D9D9D9=217勿混用）", "灰度199（旧值C9C9C9=201/A6A6A6=166/D9D9D9=217勿混用）"),
    ("大commit推不上分块push", "大commit推不上分块push（0906实测：~500MB/~2分钟掐断→分批≤200MB即推、批后ls-remote核远端）"),
    ("- （注册表旧径存档、现行主路径免全局配置，§14；旧径AutoSave模板+EnsureUniqueFilenames+OpenViewer=0+改后杀进程重启生效）；打印后立即杀保spool；6.3直接出.pdf用GS压缩；Word COM能开中文路径但VBS链路复制ASCII临时名；多件连打卡死、逐个来",
     "- 主路径与备胎链细则＝附则《PDF导出链》（2026-09-06 自§14 L189 外移）；独有增量：打印后立即杀保spool；多件连打卡死逐个来；Word COM能开中文路径但VBS链路复制ASCII临时名"),
    ("；refs/codex坏ref直接rm -rf .git/refs/codex", ""),
    ("COM须Documents.Open大写O、PrintOut前ActivePrinter='PDFCreator'、只传Background；",
     "COM须Documents.Open大写O、PrintOut只传Background（打印链见附则《PDF导出链》）；"),
    ("（跨包大量追加累积发作，与docPr重复/zip重名无关）", "（跨包大量追加累积发作）"),
    ("；判定缺陷必查OMML结构级＋w:drawing元素级双维（公式图片在位而扫描器只扫w:t＋oMath即漏）",
     "；判定缺陷必查OMML结构级＋w:drawing元素级双维（三族守恒总则＝附则YS-1）"),
    ("- [ ] **删除必须精确列文件名逐个删，禁止宽泛批量删除**（余已固化§2/§3）",
     "- [ ] 删除精确列文件名逐个删、禁宽泛批量删（已固化§2/§3）"),
    ("；footer时序=is_linked_to_previous=False须在body.append前", ""),
    ("- 2026-09-02 压缩轮——释出仅期望非配额、释不出实报不判返工；压缩主力＝删重抄公共规则段",
     "- 2026-09-02 压缩轮——释出仅期望非配额、释不出实报不判返工"),
    ("（裸m:f/m:r插段级=Word拒开且OpenAndRepair救不回）", "（裸m:f/m:r插段级=Word拒开）"),
    ("；题目图统计到下一题号行；只查media会漏\"包内在、引用已删\"", "；题目图统计到下一题号行"),
    ("、whitespace-only run非内容字号不计", ""),
]
for old, new in pairs:
    k = y.count(old)
    assert k == 1, f"经验档锚不唯一({k})：{old[:24]}"
    y = y.replace(old, new)
new_entry = ("- 2026-09-06 选必1成书修复②/③/⑤轮——元素守恒/净场/栏顶/跨行三件套已固化（附则YS/LT/FX-6＋总控例外）；"
             "独有教训：断言执行器与注册表判据必须同源（视角分裂致②-E假阴性5/10——--mapping直载注册表绝后患）；"
             "锚点正则伪影（WJ/零宽/数学斜体/拆行）在匹配层归一化、正则本体保持可读前缀；e2e大件复跑用同卷NTFS硬链接零拷贝")
if not y.endswith("\n"):
    y += "\n"
y += new_entry + "\n"
JY.write_text(y, encoding="utf-8")
report.append(f"经验档字符 {y_before}→{len(y)}（预算 12,000：{'达标' if len(y) <= 12000 else '超 ' + str(len(y) - 12000)}；C9→C7 {ny_hex} 处）")

# ============ 9. 残留扫描（规则类文件的 C9C9C9 尚存点） ============
scan = []
for pat, base in [("*.md", ROOT), ("*.md", ROOT / "附则"), ("*.md", ROOT / "素材普查")]:
    for f in sorted(base.glob(pat)):
        try:
            c = f.read_text(encoding="utf-8", errors="ignore").count("C9C9C9")
        except Exception:
            continue
        if c:
            scan.append(f"{f.relative_to(ROOT)}: {c}")
report.append("规则类文件 C9C9C9 残留扫描→ " + ("；".join(scan) if scan else "零"))

print("\n".join(report))
print("SURGERY_OK")
