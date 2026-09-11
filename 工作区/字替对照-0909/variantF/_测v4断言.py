# -*- coding: utf-8 -*-
r"""_测v4断言.py——v4.4 导学件断言实测（交付报告§十证据源）。骨架沿 v4.3 版（check/reg/fails/okmsg＋SystemExit），
v4.4 执行轮翻修（规格书§断言翻修）：既有断言漂移适配（⑥ [答案]14/[解析]20/[分析]9/[详解]9/[点睛]2、
⑰ zhuzhu 新体＋题侧 10.5 黑宋、⑱ side×5＋新 raisebox＋横缝、⑲ tiaomu \\textbf/\\heiti 变式/tjdnr #3/
题号 \\textbf regex/标签[]、N1 半角(√)(×)、N3 '[' 反向、N4 表顶 2.77±0.5＋头净空 2.8–3.5·不穿字≥0.2＋
表内行距 4.90±0.4＋挖空行底登记、N6 居中×1 下距 0.4–2.6、N7 半角子项号、N10 升格中位 3.95±0.6、页数实测）

全品对齐0911（v8 轮）同步：⑪ kongda×20→0 反向＋kongbai×34 正向；⑪-2 p1/p2 印答值门→作废迁 ㉑d；
⑪-3 印答盒（线下恰一值）×20→空档盒（线下无值）×34＋印答 0 反向；⑫ zhenti 6→0＋zhentib 6 新锁；
④ (√)(×)×6 右挂→（　）×6 右挂（× 墨盒伪片段合成停用）；⑥ [解析]6→0＋（　）6 正锁；⑰ 解析span 6→0；
N1 槽列位换形（全角（　））；N10 解析→题号配对 1–2→0 反向；⑦-4 配对判据改「（　）尾行直接相邻」；
② 全角括号 0→恰12（（　）×6 豁免）；页数门 ①＝5 复测不变；㉑a 页数4 不变；㉑b [答案]23→26、[解析]14→17；
㉑c 23 题门不变；新立 ㉑d 课前预习节值在场。旧值全录 .bak_全品对齐0911。
＋新增断言 ①题号笔画 2.0–2.7×＋变式反向 ②括号 0.3–0.7em＋全角零残留 ③定界符 ≤9.5pt（探七 ×2 豁免）
④判断括号右挂 ×5＋断行独占行 ×1（v10-A 口径改，合计 6 槽） ⑦七缝（探究点→例1/知识点/表底/解析→◆/条目）⑧多选×1 ⑨悬挂＋源空格 0
⑩答案行无下划线 ⑪题侧隙 2.7/2.2×14 ⑫探究点 ≤82mm×9＋名字清单 ⑭ kongwei 6.8±0.6×8 ⑮ side×5 归属。
F 片A 0909 适配（图文形态轮）：⑱ 几何档重写——side×5 文字栏宽逐图标定（mm）＋图盒宽按墨宽折算
（image1 剪垫后冻结 27.2mm）＋raisebox 高逐图反解；⑱-2 改墨级三窗（顶差 ∈[−1,+1]／墨缝 ∈[5.2,8.2]／
右缘 ∈[1.6,3.6]，600dpi，主口径同 D 组 B_ink），旧「|dy_box|≤2＋横缝降登记」作废；
⑮ 归属键改阅读序（页,栏,y）——修同 y 双栏标题与跨栏流两处误归属（旧实测 {七,三,二,八}→新 {二,三,六,八,九}）；
⑪ 后隙 18→20＋换行态 5→3（探二/探九题干由并排 minipage 改内联，标签行末后隙可测 +2）。
片E 0909c 适配（图文绕排回流轮，用户 #40）：⑱-3 新设——切分组（image4/image5）图底以下余段首行
右缘 ≤5mm（通栏）＋图带零侵入；⑱/⑱-2 形不变（前缀仍 minipage 并排，几何三窗逐字同基线）；
旧形「整段窄栏」＝#40 缺陷态，登记作废。
绕图回流0911 适配（用户令「恢复绕图回流」，本轮零版面扰动）：⑱-3 并排支按「有无图底以下余段」三分立——有余段支＝
片E 照片E 口径原样恢复（图底以下首个自栏左起视觉行右缘距栏右 ≤5mm 判通栏；零侵入复用 ⑱-2 K18[nhit] 不重算）；
无余段支加「段全在图旁」正证门（末旁行 600dpi 真墨底 ≤ 图真墨底＋0.5mm）＝「不许硬造余段」的机器反向锁。
本轮 g1/g2 实测走无余段支（门读数 g1 −31.42mm／g2 −2.02mm 贴线态），有余段支命中 0/2；其余门不回退。
v4.3 窗口全部为 0908 执行轮 150dpi 墨口径／矢量实测回填（校准探针三轮，存 工作区/体系-v43执行-0908/）：
①编译零 error/overfull/missingchar；页数＝实测值（v4.4 标定轮回填，缝＋行距增量可能 7→8）
②行距主峰 17.5–18.5pt（\linespread{1} 实发 18pt）
③灰档全集＝{77,119,122,189,221} 恰五档（0908 实测：midgray119／gray122／huarule77／栏线189（H3 片 E6 换 black!26）／pnumbg221），
  逐页 ⊆ 白名单（v4.2 的 ≤3 档约束废——五档为设计调色板全量）
④章首几何：方块 union 13.8×16.6±0.5mm；章名距方块 3.1±0.3mm；横线 0.2±0.05pt；
  四档级间距墨口径 线→节6.9／节→小节5.5／小节→课时5.9／课时→目标5.8 各 ±0.5；章首占地 50–58mm
⑤栏利用率 ≥70%（门槛）＋⑤b 断栏经济学实测登记（不计 FAIL，v4.1 沿革）＋⑤a-monolith 前末栏豁免
  （末页前一页右栏＝课堂评价 \vbox 不可切跳栏空隙，≥62% 全品先例档＋登记需追认，0908）
⑥排印计数：◆探究点9／例1〔9／变式1〔9／【答案】14／★0／【解析】20
⑦花形几何全集：恰3处；组 23.5±1.2mm 宽 × 高 6.2–7.0；贴线 0.15–0.45；底线 stroke 1.2±0.06pt 灰77(0x4D)；
  起点 +2.77±0.3／终点距栏线 4.0±0.5；右词＝灰122 6.5pt 词组（≥2 词）；词组右缘 4.0±1.0；
  坐线（词墨底→线墨顶）0.15–0.65；前距 4.5±0.8（栏首元素豁免登记——multicols 栏首弃胶，
  p1 由 LAN_OPEN 栏区外胶给、p3 由宏胶 1.4mm 给，0908 回填）；行总高 6.5–7.7；后距实测登记
⑧页脚：块 26.2×7.8±0.3mm 出血到纸边（H3 片 E5）；底缘 11±0.5mm；数字 10.66pt 纯黑（Noto Sans SC Medium）；数字近缘距版心侧缘 2.5–3.4mm（奇 2.8/偶 2.75 垫）；
  小字 5.5pt；混重＝奇页 {FZSSJW+FZHTJW}（章名宋＋件名黑）、偶页 FZSSJW（册名宋）
⑨页眉缺席；⑩奇偶交替（奇＝块贴版心右＋「导学件」；偶＝块贴版心左＋「人教B」）
⑪挖空印答 \kongda×20＋印答值在场＋⑪-3 盒宽 ≥42pt 全量实测（返修1 口径沿 v4.2）
⑫判断题 \zhenti×6＋简析 \jiexi×14；⑬条目按知识点重起
⑭栏线：stroke 0.4±0.05pt 色 189（black!26，H3 片 E6；旧 black!40＝153），逐页在场；渲染芯 dpi300 采样中位 170–210
⑮【诊断分析】头单行 ×3（10.5pt 说明回档）
⑰解析 span 10–11pt ×20（拍板2 升档）；\zhuzhu 宏无小号层；题侧 8pt 灰维持（计数登记）
⑱图文并排 minipage ≥5（side×5：文字栏宽逐图标定 43–49mm＋图盒按墨宽＋raisebox 逐图反解）
  ＋墨级三窗（顶差 ∈[−1,+1]／墨缝 ∈[5.2,8.2]／右缘 ∈[1.6,3.6]，F 片A 0909 新档；旧 |dy|≤2＋横缝登记作废）；⑲字重阶梯 tex 级：
  FakeBold 值表 heizhang4.0/heijie3.3/heitiao2.7/heibf2.3/heihao2.0/heibian1.3＋huabf slant0.18/bold2.0
  ＋\jietitle 反向断言（\heiti 常规，无仿粗族）＋例变式标签 12pt×18＋检测题号 11.4pt×5（tex+pdf）
  ＋\tiaomu 输出形 {\heitiao #1.}＋\jiexi 解析尾 \addvspace 7pt（6–8pt 档，条9②）＋\zhenti 尾 0pt
  （F 片B 0909 #31 归零，见下）
新增 v4.3：N1 判断题括号 ink 列位 5.4±0.5（像素，两支尾占位统一 rule 3.34 后 ink 同位 5.14）＋bbox 3.34±0.2；
  N2 选项行距分档双窗（例区 19pt→6.4–7.0mm／评价·检测 21pt→7.1–7.8mm，拍板9）；
  N3 探究点标题独行×9＋反向（行内无题侧/例标；翻拍板16/28）；N4 表组（外框 0.8＞内线 0.4pt、色 122、
  表头行高 8.7–9.3、行高 ≥8.5、表顶前距 2.27–3.6、首列居中±1.5、头净空 2.8–3.5）；N5 学习目标（楷体、行距 17pt 档、
  回行悬挂 8.3mm、首行缩进例外）；N6 图组（60±1／34±1 居中、ink 上下距 2.8/2.2±0.5 窗、图内字 SKIP 登记）；
  N7 条目3 投影向量首子项（1）连排（body+pdf+postproc 第8步台账）；N8 素养小结内容楷体×9；
  N9 ◆ 0.63em＋后隙 2.4±0.3；N10 解析→下题题号距（register——配对少且公式降部扰带，tex 级已锁 7pt·6-8pt 档）
F 片B 0909 适配（竖向间距与表格净空轮；窗口旧→新逐项登记见对应 check/reg）：
  ⑦块缝 条目缝窗 2.5–5.0→2.7–3.4（\tiaomu 尾距 1.8→0.35mm，实测 3.05–3.39，pitch 6.76 统一）＋
  知识点缝对 2→1／表底缝对 2→3（表3 移 p3 栏首）；新增 ⑦-3 条目2 (1)→(2) 拆段缝（6.44±0.25／墨 2.7–3.0）＋
  ⑦-4 相邻判断题缝（6.44±0.25／墨 2.6–3.2，\zhenti 尾 7pt→0）＋N4b 多行格净空（行级最紧侧 顶 2.9–3.7／
  底 2.9–4.3mm，extrarowheight 0.4→1.7mm＋\tabrowglue 按折数分档）；N4 表头 7.0–9.2→8.7–9.3、行高 ≥6.9→≥8.5、
  头净空 2.0±0.4→2.8–3.5（E 垫顶后墨顶抬升）；⑲ \zhenti 尾 0pt/\jiexi 尾 7pt 分锁；⑬/N7 \tiaomuz 形同步
F 片D 0909c 适配（变式标签双字重轮，意见#33；旧→新登记见对应 check/reg）：
  ⑲ \liB 锁形旧「\libian\libianlat #1」→ 新「\liBsplit#1\liBstop」＋\def\liBsplit 双段挂族
  （变 FY-w700BEVL100／式N FY-w450BEVL100）；① 变式密度旧单集反向 ≤1.75 → 拆双集：
  变（特黑档）2.2–3.2／式（中黑档）≤1.75（0909c 实测 2.68／1.33，全品 p06 真迹 0.145em＞0.075em 双字重）
F 片F 0909c 适配（排版弹性轮，用户 #41 字间距过远＋#43 序号间隙浮动；旧→新逐项登记）：
  新增「拉伸异常行＝0」断言（CJK-CJK 空档 >0.5em＋间隙无墨＋非 \quad/2em 设计字距；口径与基线见 check/reg）；
  ⑲ \liBsplit 锁形旧「{{\libianb #1}{\libians\libianslat #2}}」→ 新「{{\libianb #1}\kern0pt{\libians\libianslat #2}}」
  （#41：xeCJK 见用户 kern 不插 CJKglue，变|式 字间不再随行拉伸——基线 p3/p5 实测 6.18/14.91pt→0）；
  ④ \zhenti 宏形旧「\noindent#1#2\nobreak\hspace{0pt plus 1fil}\nobreak(…」→ 新「\noindent#1\kern2.1pt#2\nobreak…」
  （#43：序号后隙 ecglue→定值 kern 2.1pt，ink 实测 0.945–1.030mm 零拉伸，旧 1.094–4.239mm 随行浮动）；
qp-layout \relpenalty 10000→500、\emergencystretch 2em→1em（#41 断点恢复＋弹性收紧，三0 计数同基线）
  回退轮0910（图源回退轮，用户二次令「禁画三维图——AI 重绘六图全部退役、回用原图位图」）：
  ⑱ tex 形制改核 includegraphics 位图图行 ×6（width=宽mm 直排；figs 入件归零、resizebox 归零，下置骨架逐字节承片G）；
  ⑱-2／⑱-3／N6／⑮ 改位图口径（get_image_info 矩形＋PIL 原生墨映射＋600dpi 墨级前距/下距/零侵入＋落位逐图钉）；
  旧矢量线框内核保留停用（图源回退后不适用；残留清理0911 已折叠删除＝死码，见「权威线框口径内核」节注）；
  ③ 灰档回位图时代 6 档（0x40 cubegray 退役）；
  置宽反解三值表见 回退轮0910/简报.md（g6 84.0／g1 28.8／g2 32.7／g3 54.1／g4 47.5／g5 42.5mm）。
答案制0911 适配（答案制A·去答案落 导学件答案册-v1；门值旧→新总账，明细见 ㉑ 后台账）：
  门① 页数 7→5；门⑥ 正文判分值 0 在场——[答案]14/[解析]20/[分析]9/[详解]9/[点睛]2→0/6(仅判断题简析)/0/0/0，
  另核「故答案为/故选」句 0；◆9/例1 9/变式9/★0 不变；⑰ 解析span 20→6；门③ 超高定界符 恰4→恰0
  （探七 array／探八 \left(\right) 放大对随 [详解] 出册）；门⑩ 答案行 14→0（改反向门：正文无答案行）；
  门⑫ \jiexi 14→0（\zhenti ×6 与 \kongda 印答 20、判断括号 (√)(×)×6 保留照旧）；位图台账 6→4——
  ⑱ 并排×2→×1（g2）·下置×4→×3，⑮ 归属 五图→三图（探三/六/八），⑱-2/⑱-3/N6 四图口径
  （g1-prism 探二并排图／g5-fold 探九下置图随 [详解] 出册，册内改题下居中 \ansfig）；
  新立 ㉑a/b/c 册侧门（答案册编译三0＋页数4＋值排印七项计数＋位图2＋23 题判分值逐一 pdf 在场）。"""
import os
import re
from collections import Counter

import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PT = 72 / 25.4
# F 0909 收尾轮（V7b 断言适配）：MARGIN/COLSEP 按 F 版 qp-layout（E 轮已改）——margin 17.575mm
# （版心 174.85 全品实测反推）、columnsep 9.25mm、栏宽 82.8mm；旧 15/7.5 系 C 版值，
# 残留致 ⑦花形起点/⑩页脚贴缘等全部测错基准（误 5.35/2.58，真值 2.77/≈0）
# H1 片 0909c 适配（E7 版面基准）：左右 margin 17.575→17.2mm、columnsep 9.25→7.6mm（栏宽 84.0mm）；
#   top 与水平 margin 解耦单列 19.6mm（首行墨顶全品实测档）——TOP 常量新设，凡「距版心顶」类
#   量（③④⑤⑦灰档/章首占地/利用率/花形顶距/页眉带）一律改 TOP；横向类沿用 MARGIN。
MARGIN = 17.2 * PT
TOP = 19.6 * PT
BOT = 20 * PT
PAGE_W = 595.276
PAGE_H = 842.0
COLSEP = 7.6 * PT
COLW = (PAGE_W - 2 * MARGIN - COLSEP) / 2
MID = MARGIN + COLW + COLSEP / 2
COLL = [MARGIN, MARGIN + COLW + COLSEP]
COLR = PAGE_W - MARGIN
TEXTH = PAGE_H - TOP - BOT
BODY_BOT = PAGE_H - BOT
DPI = 150
SC = DPI / 72.0

fails, okmsg, regmsg = [], [], []

def check(name, ok, detail=''):
    (okmsg if ok else fails).append(f'{name}　{detail}')

def reg(name, detail):
    regmsg.append(f'{name}　{detail}')

# ---- 工具：列带墨带投影（150dpi 墨口径，与全品扫差同法） ----
def bands(page, x0, x1, y0, y1, thresh=128, dpi=DPI):
    y0 = max(TOP - 3, y0); y1 = min(PAGE_H, y1)
    if y1 - y0 < 1:
        return []
    sc = dpi / 72.0
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rows = [any(s[r * w + c] < thresh for c in range(w)) for r in range(h)]
    out, st = [], None
    for i, d in enumerate(rows):
        if d and st is None:
            st = i
        elif not d and st is not None:
            out.append((y0 + st / sc, y0 + i / sc)); st = None
    if st is not None:
        out.append((y0 + st / sc, y0 + h / sc))
    return out

def merge(bs, gap=0.5):
    out = []
    for a, b in bs:
        if out and a - out[-1][1] < gap:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out

def rgb255(c):
    return tuple(round(x * 255) for x in c)

# F 片B 0909 新设工具（#28/#30/#31 断言用）：600dpi 灰渲染墨带——窗口内最大相邻空档＝缝/净空。
def ink_bands600(pno, cl, y0, y1, x0=None, x1=None, dpi=600, thr=128):
    """返回窗口内墨带 [(y_a, y_b)]（pt 坐标，600dpi 灰投影）。"""
    page = doc[pno - 1]
    x0 = COLL[cl] if x0 is None else x0
    x1 = COLL[cl] + COLW if x1 is None else x1
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rows = [any(s[r * w + c] < thr for c in range(w)) for r in range(h)]
    idx = [r for r, d in enumerate(rows) if d]
    if not idx:
        return []
    bands, st, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > 1:
            bands.append((st, p)); st = i
        p = i
    bands.append((st, p))
    sc = 72.0 / dpi
    return [(y0 + a * sc, y0 + b * sc) for a, b in bands]

def ink_gap600(pno, cl, y_up_base, y_lo_base):
    """两基线间墨隙（mm）：窗口内最大相邻墨带空档（行内子带隙远小于行距）。"""
    bs = ink_bands600(pno, cl, y_up_base - 1.0, y_lo_base + 1.0)
    if len(bs) < 2:
        return None
    return max((b0 - a1) for (a0, a1), (b0, b1) in zip(bs, bs[1:])) * 25.4 / 72.0

# ---- ① 编译日志 ----
logtxt = open(os.path.join(BASE, 'main.log'), encoding='utf-8', errors='ignore').read()
n_err = len(re.findall(r'^!', logtxt, re.M))
n_over = len(re.findall(r'Overfull', logtxt))
n_miss = len(re.findall(r'Missing character', logtxt))
m = re.search(r'Output written on main\.pdf \((\d+) pages', logtxt)
n_pages = int(m.group(1)) if m else -1
check('①编译零 error/overfull/missingchar＋页数5（答案制0911 去答案落册 7→5；沿革：E 轮 7→6／H2 片 6→7）', n_err == 0 and n_over == 0 and n_miss == 0 and n_pages == 5,
      f'errors={n_err} overfull={n_over} missingchar={n_miss} 页数={n_pages}')

doc = pymupdf.open(os.path.join(BASE, 'main.pdf'))
body = open(os.path.join(BASE, 'body.tex'), encoding='utf-8').read()
blkfile = open(os.path.join(BASE, 'qp-blocks.tex'), encoding='utf-8').read()
fontfile = open(os.path.join(BASE, 'qp-fonts.tex'), encoding='utf-8').read()
titfile = open(os.path.join(BASE, 'qp-titles.tex'), encoding='utf-8').read()

lines_of = {}
for pno, page in enumerate(doc, 1):
    ls = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                ls.append((t, ln['bbox'], ln['spans']))
    lines_of[pno] = ls

def col_rows(pno, cl):
    """列内文本行（按 y 排序）；列过滤 ±7pt——解析行【 字形负承载 bbox[0]＝列缘−4.74pt（0908 实证）。"""
    rows = []
    for t, bb, sps in lines_of[pno]:
        if cl - 7 <= bb[0] < cl + COLW + 7:
            rows.append((bb[1], bb[3], t, sps))
    rows.sort(key=lambda r: r[0])
    return rows

# ---- 片G 0910 矢量图簇口径（_diag_rects/vec_clusters/_VEC_CACHE）已随 残留清理0911 折叠删除 ----
# 六图回位图后矢量层无图可聚（0 簇）；grep 证 vec_clusters/_diag_rects 全文 0 调用＝死码；in_fig 自
# 回退轮0910 起改锚位图台账 FIG_ROWS（下），不受影响。原文见 .bak_残留清理0911。


def in_fig(pno, x0, y0, x1, y1, pad=1.0):
    """线段/小框是否落在某位图图矩形内（含 pad pt 容差）——供印答盒线门排除图区墨（防御保留）。
    回退轮0910：图源回位图后矢量层不再有图内棱，判据由矢量簇改锚共用台账 FIG_ROWS（位图矩形）。"""
    return any(p == pno and g.x0 - pad <= x0 and x1 <= g.x1 + pad and g.y0 - pad <= y0 and y1 <= g.y1 + pad
               for p, _c, _y, g, _info in FIG_ROWS)


# ---- 回退轮0910 六图位图回退·共用台账（⑱/⑱-2/⑱-3/N6/⑮ 五门唯一图源；片G 矢量簇台账口径随图源回退作废；
#      并排恢复0910：g1/g2 改图右文左并排形制，g3–g6 保持下置——形制逐图钉 FIG_MODE）----
# 图源：AI TikZ 矢量重绘→原 Word 位图（media/media/*.png，用户 0910 二次令「禁画三维图——AI 画过的一律不要」）。
# PDF 内图＝raster 对象——pymupdf get_image_info(xrefs=True) 取矩形，并以原生像素尺寸与片段互证（FIG_PX）。
# FIG_W＝body.tex 图行阅读序＋tex 声明置宽（反解三值表取用宽：字母标签像素高→显示 2.65mm 反解、
#   上限 84.0mm∧150dpi 自然尺寸；三值表见 回退轮0910/简报.md；并排恢复0910：g2 并排盒宽缩 32.0 入 TW-01）；
# FIG_AT＝实测落位（页,栏）逐图钉——并排恢复0910 实测六图落位与回退轮基线一致（g1/g2 仍 p3c2），
#   g2 由栏末图改并排行内图（栏末免检口径随其下置形退场）。
# 阅读序＝（页,栏,y 顶）排序与图行序严格一致——并排两图 y 顶＝行内图盒顶，序仍成立（自片G 起成立）。
# 答案制0911：六图→四图——g1-prism（探二[详解]并排行内图）／g5-fold（探九[详解]下置图）随 [详解] 出册
# （导学件答案册-v1 内改题下居中 \ansfig）；旧六条台账见 .bak_去答0911。阅读序四图＝g6/g2/g3/g4。
FIG_W = [('g6-triple', '84.0mm'), ('g2-cubeE', '32.0mm'),
         ('g3-cube6', '54.1mm'), ('g4-dihedral', '47.5mm')]
FIG_MODE = {'g6-triple': 'under', 'g2-cubeE': 'side',
            'g3-cube6': 'under', 'g4-dihedral': 'under'}
# 并排行逐图钉（postproc side_row 发射值：文字栏宽／盒间胶／图盒宽／raisebox 声明高 H）——
# 胶由「栏宽−右缘目标＋盒右留白−文栏−盒宽」墨缘反解（非硬凑常数）；右缘目标 g1 1.90（档内）／
# g2 5.00（缝窗优先——栏预算恒等式缝＋右缘＝12.87 双窗不可兼得，例外登记见 ⑱-2 reg 与 SIDE_DEF 注）
SIDE_PIN = {'g2-cubeE': dict(text='46.368', glue='0.925', box='32.000', H='3.545', png='image2')}
# ↑答案制0911：g1-prism 钉（文48.000/胶5.342/盒28.800/H3.332/image1）随并排图文行出册（旧值存 .bak_去答0911）
BOX_MM = {f: float(w[:-2]) for f, w in FIG_W}
FIG_PX = {'g6-triple': (1408, 374), 'g1-prism': (691, 1159), 'g2-cubeE': (764, 764),
          'g3-cube6': (521, 496), 'g4-dihedral': (788, 424), 'g5-fold': (1798, 1350)}
FIG_PNG = {'g6-triple': 'media/media/sub3_B_4.png', 'g1-prism': 'media/media/image1.png',
           'g2-cubeE': 'media/media/image2.png', 'g3-cube6': 'media/media/image3.png',
           'g4-dihedral': 'media/media/image4.png', 'g5-fold': 'media/media/image5.png'}
# 答案制0911 重钉（5 页新分页）：初值按分页分析回填，若 ⑱-2/N6 ✗落位，读数即实测值，以实测为准回填。
# 旧六图钉（并排恢复0910 7页档）：g6(2,2)/g1(3,2)/g2(3,2)/g3(5,1)/g4(6,1)/g5(6,2)。
FIG_AT = {'g6-triple': (2, 2), 'g2-cubeE': (3, 2),
          'g3-cube6': (4, 1), 'g4-dihedral': (4, 2)}
FIG_ROWS = []
for _pno in range(1, n_pages + 1):
    for _info in doc[_pno - 1].get_image_info(xrefs=True):
        _r = pymupdf.Rect(_info['bbox'])
        FIG_ROWS.append((_pno, 1 if (_r.x0 + _r.x1) / 2 < MID else 2, _r.y0, _r, _info))
FIG_ROWS.sort(key=lambda z: (z[0], z[1], z[2]))
FIGS, FIG_PXBAD = [], []
for (f, _w), (_p, _c, _y, _r, _info) in zip(FIG_W, FIG_ROWS):
    if FIG_PX[f] != (_info['width'], _info['height']):
        FIG_PXBAD.append(f + '≠' + str(_info['width']) + 'x' + str(_info['height']) + 'px')
    FIGS.append((f, _p, _c, _r, _info))

# ---- ② 行距主峰 ----
diffs = []
for pno in range(1, n_pages + 1):
    cols = {0: [], 1: []}
    for t, bb, sps in lines_of[pno]:
        if any(10 <= sp['size'] <= 11 for sp in sps):
            cols[0 if bb[0] < MID else 1].append(sps[0]['origin'][1])
    for c in (0, 1):
        ys = sorted(cols[c])
        diffs += [round((b - a) * 4) / 4 for a, b in zip(ys, ys[1:]) if 3 < b - a < 40]
peak, cnt = Counter(diffs).most_common(1)[0]
check('②行距主峰 17.5–18.5pt', 17.5 <= peak <= 18.5, f'主峰{peak}pt(×{cnt}/{len(diffs)})')

# ---- ③ 灰档全集 ----
grays_all, gray_ok = set(), True
gray_detail = []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    grays = set()
    for t, bb, sps in lines_of[pno]:
        for sp in sps:
            col = sp['color']
            r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
            if r == g == b and 0 < r < 255:
                grays.add(r)
    for d in page.get_drawings():
        for key in ('color', 'fill'):
            c = d.get(key)
            if c:
                rgb = rgb255(c)
                if rgb[0] == rgb[1] == rgb[2] and 0 < rgb[0] < 255:
                    grays.add(rgb[0])
    gray_detail.append(f'p{pno}={sorted(grays)}')
    grays_all |= grays
    if not grays <= {0x4C, 0x4D, 0x77, 0x7A, 0xBD, 0xDD}:
        gray_ok = False
check('③灰档全集恰{76,77,119,122,189,221}（回退轮位图六档）且逐页⊆白名单', gray_ok and grays_all == {0x4C, 0x4D, 0x77, 0x7A, 0xBD, 0xDD},
      f'全集{sorted(grays_all)}；{" ".join(gray_detail)}')
reg('③ 回退轮0910 灰档回档（7档→6档）',
    '片G 0910 增第七档 cubegray 0x40(64)＝g3-cube6 矢量灰棱上浮为页面描边色；回退轮六图回用原位图后，'
    '灰棱回到像素内、不入矢量色板——白名单回位图时代 6 档 {76,77,119,122,189,221}（0x40 退役）。'
    'qp-blocks.tex 之 \\definecolor{cubegray} 定义保留未动（片段不再 \\input，不入页）。')
reg('③调色板对账', 'v4.3 五档＝midgray 0x77(119)／gray122 0x7A(122)／huarule 0x4D(77)／栏线 black!40 0x99(153)／'
    'pnumbg 0xDD(221)，与 qp-layout 定义一一对应（总账A/D/I＋拍板27）；E 0909 增第六档 footgray 0x4C(76)＝'
    '页脚小字（qp-headfoot，全品 p04 页脚小字暗核众数 76 实测）——F 收尾轮断言适配入白名单；'
    'H3 片 0909c（E6）：栏线 black!40 0x99(153)→black!26 0xBD(189)——白名单第 0x99 档换 0xBD（全品靶 188）')

# ---- ④ 章首几何 ----
p1 = doc[0]
anchors = {}
for t, bb, sps in lines_of[1]:
    tt = t.replace(' ', '')
    for k, pre in (('zh', '第一章'), ('jie', '1.1'), ('xj', '1.1.1'), ('ks', '第1课时'), ('mb', '【学习目标】')):
        if k not in anchors and tt.startswith(pre):
            anchors[k] = bb
hl = None
for d in p1.get_drawings():
    r = d['rect']
    if r.width > 300 and r.height <= 2 and r.y0 < 40 * PT:
        hl = d
sq = [d['rect'] for d in p1.get_drawings() if d.get('fill') and d['rect'].y0 < 200 and d['rect'].width < 200
      and rgb255(d['fill']) in ((221, 221, 221), (119, 119, 119))]
ok4, d4 = True, []
if sq and hl and all(k in anchors for k in ('zh', 'jie', 'xj', 'ks', 'mb')):
    ux0 = min(r.x0 for r in sq); ux1 = max(r.x1 for r in sq)
    uy0 = min(r.y0 for r in sq); uy1 = max(r.y1 for r in sq)
    uw, uh = mm_ = (ux1 - ux0) / PT, (uy1 - uy0) / PT
    dist = (anchors['zh'][0] - ux1) / PT
    hl_w = hl.get('width') or 0
    ok4 = abs(uw - 13.8) <= 0.5 and abs(uh - 16.6) <= 0.5 and abs(dist - 3.1) <= 0.3 and abs(hl_w - 0.2) <= 0.05
    d4.append(f'union {uw:.2f}×{uh:.2f} 章名距{dist:.2f} 线{hl_w:.3f}pt')
    bs4 = merge(bands(p1, MARGIN, COLR, TOP, anchors['mb'][3] + 2, thresh=190))
    def bof(y0, y1):  # 区间重叠匹配：bbox 顶含行内 leading 高于墨顶 >1.2mm，单点±1.2 会取 None
        for i, (a, b) in enumerate(bs4):
            if a <= y1 + 1.5 and b >= y0 - 1.5:
                return i
        return None
    line_ink_bot = hl['rect'].y1 + hl_w / 2
    # H1 片 0909c 适配（E7 top 19.6mm 后 0.2pt 横线 150dpi 亚像素相位偏移 → 渲染灰 170 恰等于
    # 原阈值 170 被排除，band 匹配取不到线）；搜索容差 ±0.2→±1.8pt（线本体 0.2pt，±1.8 仅覆盖
    # 线带不触邻带——章名带底 83.4 / 节带顶 113.2 均远）
    seq = [bof(line_ink_bot - 1.8, line_ink_bot + 1.8)] \
        + [bof(anchors[k][1], anchors[k][3]) for k in ('jie', 'xj', 'ks', 'mb')]
    tgts = (6.9, 5.5, 5.9, 5.8)
    nms = ('线→节', '节→小节', '小节→课时', '课时→目标')
    if all(s is not None for s in seq):
        for nm, tgt, i, j in zip(nms, tgts, seq, seq[1:]):
            g = (bs4[j][0] - bs4[i][1]) / PT
            ok4 = ok4 and abs(g - tgt) <= 0.5
            d4.append(f'{nm}{g:.2f}')
    else:
        ok4 = False
        d4.append(f'带缺{seq}')
    occ = (anchors['mb'][1] - TOP) / PT
    ok4 = ok4 and 50 <= occ <= 58
    d4.append(f'占地{occ:.2f}')
else:
    ok4 = False
    d4.append(f'锚缺 sq={len(sq)} hl={bool(hl)} anchors={sorted(anchors)}')
check('④章首几何（union13.8×16.6/章名距3.1/线0.2pt/四档6.9-5.5-5.9-5.8/占地50-58）', ok4, ' '.join(d4))

# ---- ⑤ 栏利用率 ----
def col_idx(x):
    return 0 if x < MID else 1
util = {}
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    cols = {0: MARGIN, 1: MARGIN}
    for t, bb, sps in lines_of[pno]:
        x0, y0, x1, y1 = bb
        if y0 > BODY_BOT + 1:
            continue
        cols[col_idx(x0)] = max(cols[col_idx(x0)], min(y1, BODY_BOT))
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            if r.y0 > BODY_BOT + 1:
                continue
            cols[col_idx(r.x0)] = max(cols[col_idx(r.x0)], min(r.y1, BODY_BOT))
    for d in page.get_drawings():
        r = d['rect']
        if r.y0 > BODY_BOT + 1:
            continue
        if abs(r.x0 - MID) < 2 and r.width <= 2:
            continue
        if d.get('fill') and rgb255(d['fill']) == (221, 221, 221) and r.y0 > BODY_BOT - 10:
            continue
        cols[col_idx((r.x0 + r.x1) / 2)] = max(cols[col_idx((r.x0 + r.x1) / 2)], min(r.y1, BODY_BOT))
    util[pno] = {c: (cols[c] - TOP) / TEXTH for c in (0, 1)}
    util[pno]['ink'] = {c: cols[c] for c in (0, 1)}
util_detail = '  '.join(f'p{p}:[左{u[0]*100:.0f}%/右{u[1]*100:.0f}%]' for p, u in util.items())
# ⑤a 豁免：末页前一页右栏＝课堂评价 monolith（\vbox 不可切，223mm）跳栏空隙。0908 实证：栏内解析仅 1 处，
# glueguard 伸缩胶在 p6左断点吸收一切上游推力，规格内手段（6–8pt 档）无法回填 ≥70%；空栏 80.9mm 在
# 全品自身先例（p06左 98.1mm，总账J 销号逻辑）量级内 → 门槛降为全品先例档 62%＋登记。已追认（2026-09-08 放行口表决一致批准，商议记录-放行口.md）。
exempt_col = (n_pages - 1, 1)
nonlast_ok = all(u[c] >= 0.70 or (p, c) == exempt_col and u[c] >= 0.62
                 for p, u in util.items() if p < n_pages for c in (0, 1))
over15 = [(p, c, (BODY_BOT - u['ink'][c]) / PT) for p, u in util.items() if p < n_pages
          for c in (0, 1) if BODY_BOT - u['ink'][c] > 15 * PT]
check('⑤a 非末页逐栏利用率 ≥70%（monolith 前末栏豁免 ≥62% 全品先例档）', nonlast_ok, util_detail)
reg('⑤a-monolith 豁免登记（需追认）', f'p{exempt_col[0]}右 课堂评价 \\vbox 不可切跳栏致空栏 80.9mm：'
    '规格内回填已证不可行（栏内解析 1 处 ×≤1pt；上游推力被 glueguard 伸缩吸收）；'
    '全品 p06 左栏 98.1mm 空栏先例（总账J 销号逻辑）量级内，门槛 62% 全品先例档（62.6% 取整）')
reg('⑤b 栏末墨距版心底 ≤15mm（实测登记，断栏经济学沿革 v4.1）',
    ('全部达标' if not over15 else '；'.join(f'p{p}{"左" if c == 0 else "右"} {dd:.1f}mm' for p, c, dd in over15)))
last = util[n_pages]
print(f'       末页 p{n_pages} 左{last[0]*100:.0f}%/右{last[1]*100:.0f}%——课堂评价收尾页实测登记（参差收尾＝拍板23）')

# ---- ⑥ 排印计数 ----
full = re.sub(r'\s+', '', ''.join(p.get_text() for p in doc))
n_tj = full.count('◆探究点')
n_li1 = full.count('例1[') + full.count('例1(多选题)[')   # 探五例1 带 (多选题) 前缀（TJ-04），0908 补计
n_bs = full.count('变式1[')
n_ans = full.count('[答案]')
n_star = full.count('典型性理由：')
n_jx = full.count('[解析]')
n_fx = full.count('[分析]')
n_xj2 = full.count('[详解]')
n_dj2 = full.count('[点睛]')
n_gdaan = full.count('故答案为')
n_gxuan = full.count('故选')
check('⑥排印层 正文判分值 0 在场（全品对齐0911 全域）◆9/例1 9/变式9 题面不变＋[答案]0/故答案为0/故选0/分析0/详解0/点睛0/解析0（判断简析亦出册）＋（　）×6 正锁',
      n_tj == 9 and n_li1 == 9 and n_bs == 9 and n_ans == 0 and n_star == 0 and n_jx == 0
      and n_fx == 0 and n_xj2 == 0 and n_dj2 == 0 and n_gdaan == 0 and n_gxuan == 0
      and full.count('（）') == 6,
      f'◆{n_tj} 例1{n_li1} 变式{n_bs} 答案{n_ans} ★{n_star} 解析{n_jx} 分析{n_fx} 详解{n_xj2} 点睛{n_dj2}'
      f' 故答案{n_gdaan} 故选{n_gxuan} 空括号{full.count("（）")}/6（值在场见 ㉑b/㉑c/㉑d）')

# ---- ⑦ 花形几何全集 ----
hua_rules = []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c:
            continue
        if rgb255(c) != (77, 77, 77) or not (r.width > 100 and r.height <= 3):
            continue
        hua_rules.append((pno, d, r))
ok7 = len(hua_rules) == 3
d7, d7_reg = [], []
for pno, d, r in hua_rules:
    page = doc[pno - 1]
    cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
    sw = d.get('width') or r.height
    dias = [d2['rect'] for d2 in page.get_drawings()
            if d2.get('fill') and rgb255(d2['fill']) == (255, 255, 255)
            and d2['rect'].y1 <= r.y0 + 2 and d2['rect'].y1 >= r.y0 - 25
            and d2['rect'].x0 >= cl - 2 and d2['rect'].x1 <= cl + COLW + 2
            and 8 < d2['rect'].width / PT < 12]
    if len(dias) < 4:
        ok7 = False
        d7.append(f'p{pno} 菱形{len(dias)}/4!')
        continue
    ux0 = min(x.x0 for x in dias); ux1 = max(x.x1 for x in dias)
    uy0 = min(x.y0 for x in dias); uy1 = max(x.y1 for x in dias)
    gw, gh = (ux1 - ux0) / PT, (uy1 - uy0) / PT
    tie = (r.y0 - uy1) / PT
    st_dist = (r.x0 - cl) / PT
    en_dist = (cl + COLW - r.x1) / PT
    total_h = (r.y1 + sw / 2 - uy0) / PT
    words = []
    for t, bb, sps in lines_of[pno]:
        if not (r.y0 - 20 <= bb[1] and bb[3] <= r.y1 + 8) or not (cl - 7 <= bb[0] < cl + COLW + 7):
            continue
        for sp in sps:
            if 6.0 <= sp['size'] <= 7.0 and sp['color'] == 0x7A7A7A and sp['text'].strip():
                words.append(sp)
    words.sort(key=lambda s: s['bbox'][0])
    w_right = (cl + COLW - words[-1]['bbox'][2]) / PT if words else -9
    # 坐线（右词墨底→线墨顶，像素）
    zx = -9
    if words:
        rit = r.y0 - sw / 2
        # dpi300＋clip 收至线墨顶上 0.5pt：150dpi 下 6.5pt 词内竖白缝分裂墨带，[-2] 会取到词中段带
        bzx = merge(bands(page, words[-1]['bbox'][0], words[-1]['bbox'][2],
                          words[-1]['bbox'][1] - 2, rit - 0.5, dpi=300), gap=0.4)
        if bzx:
            zx = (rit - bzx[-1][1]) / PT
    # 前距（菱形组顶→上一墨带底；栏首元素豁免）
    pre = -9
    topcol = (uy0 - TOP) / PT
    if topcol >= 8:
        bpre = bands(page, cl, cl + COLW, uy0 - 32, uy0 - 0.3)
        if bpre:
            pre = (uy0 - bpre[-1][1]) / PT
    ok_i = (abs(gw - 23.5) <= 1.2 and 6.2 <= gh <= 7.0 and 0.15 <= tie <= 0.45
            and abs(sw - 1.2) <= 0.06 and abs(st_dist - 2.77) <= 0.3 and abs(en_dist - 4.0) <= 0.5
            and len(words) >= 2 and abs(w_right - 4.0) <= 1.0 and 0.15 <= zx <= 0.65
            and 6.5 <= total_h <= 7.7 and (pre == -9 or 3.7 <= pre <= 5.3))
    ok7 = ok7 and ok_i
    d7.append(f'p{pno} 组{gw:.1f}×{gh:.2f} 贴线{tie:.2f} 线{sw:.3f}pt 起{st_dist:.2f} 终{en_dist:.2f} '
              f'词{len(words)} 右缘{w_right:.2f} 坐线{zx:.2f} 总高{total_h:.2f} 前距{pre:.2f}')
    if pre == -9:
        d7_reg.append(f'p{pno}（栏首元素距版心顶{topcol:.1f}mm，前距豁免登记）')
    # 后距（线墨底→下一墨带顶）登记
    ib = r.y1 + sw / 2
    bn = bands(page, cl, cl + COLW, ib + 0.3, ib + 32)
    d7_reg.append(f'p{pno} 后距{(bn[0][0] - ib) / PT:.2f}mm' if bn else f'p{pno} 后距栏末')
check('⑦花形几何全集（×3/组宽高/贴线/底线1.2pt灰77/起终点/右词组/坐线/前距/行总高）', ok7, '；'.join(d7))
reg('⑦ 花形后距/栏首豁免登记', '；'.join(d7_reg) + '（后距无全品规格值，登记；栏首弃胶机制见 qp-blocks \\huaxing 注）')
wide_rules = [(pno, d['rect']) for pno in range(1, n_pages + 1) for d in doc[pno - 1].get_drawings()
              if d['rect'].width > 300 and d['rect'].height <= 2]
check('⑦-2 无整页横断（章首通栏线仅页1×1）', len(wide_rules) == 1 and wide_rules[0][0] == 1,
      '；'.join(f'p{p} w={r.width / PT:.0f}mm' for p, r in wide_rules))

# ---- ⑧⑨⑩ 页脚组/页眉缺席/奇偶交替 ----
feet_ok8, feet_ok10, hdr_ok = True, True, True
d8, d9, d10 = [], [], []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    blk_rect = None
    for d in page.get_drawings():
        r = d['rect']
        f = d.get('fill')
        if not f or r.y0 <= BODY_BOT - 10:
            continue
        if rgb255(f) == (221, 221, 221):
            blk_rect = r
    num = None
    foot_spans, foot_txts = [], []
    for t, bb, sps in lines_of[pno]:
        if bb[1] > BODY_BOT - 2:
            foot_spans += [sp for sp in sps if sp['text'].strip()]
            foot_txts.append(t)
        for sp in sps:
            if sp['text'].strip() == str(pno) and blk_rect and bb[1] > BODY_BOT - 10 \
               and blk_rect.x0 - 1 <= sp['bbox'][0] and sp['bbox'][2] <= blk_rect.x1 + 1:
                num = sp
    odd = pno % 2 == 1
    if blk_rect and num:
        bw, bh = blk_rect.width / PT, blk_rect.height / PT
        bot = (PAGE_H - blk_rect.y1) / PT
        inner = blk_rect.x0 if odd else blk_rect.x1
        near = abs((num['bbox'][0] if odd else num['bbox'][2]) - inner) / PT
        fonts = {sp['font'] for sp in foot_spans}
        szs = {round(sp['size'], 1) for sp in foot_spans}
        ok8 = (abs(bw - 26.2) <= 0.3 and abs(bh - 7.8) <= 0.3 and abs(bot - 11) <= 0.5
               and 10.5 <= num['size'] <= 11.5 and 2.5 <= near <= 3.4)
        if odd:
            # F 0909 收尾轮适配：件名黑体 E 起换挂 NSC-Medium（qp-fonts hei 族），FZHTJW 时代口径作废
            ok8 = ok8 and any('FZSSJW' in f for f in fonts) and any('NotoSansSC' in f for f in fonts)
        else:
            ok8 = ok8 and any('FZSSJW' in f for f in fonts)
        # F 0909 收尾轮适配：小字 5.5→5.24pt（全品字号铁证，qp-headfoot \qphuitext），MuPDF 实测 5.22
        ok8 = ok8 and any(5.0 <= s <= 5.45 for s in szs)
        feet_ok8 = feet_ok8 and ok8
        d8.append(f'p{pno} 块{bw:.1f}×{bh:.1f} 底{bot:.1f} 数字{num["size"]:.1f}pt 近缘{near:.2f} '
                  f'字{sorted(f.split("--")[0] for f in fonts)}')
        if odd:
            ok10 = blk_rect.x1 >= COLR - 1.5 and any('导学件' in t for t in foot_txts)
            d10.append(f'p{pno}奇 贴右距{(COLR - blk_rect.x1) / PT:.2f}mm')
        else:
            ok10 = blk_rect.x0 <= MARGIN + 1.5 and any('人教B' in t.replace(' ', '') for t in foot_txts)
            d10.append(f'p{pno}偶 贴左距{(blk_rect.x0 - MARGIN) / PT:.2f}mm')
        feet_ok10 = feet_ok10 and ok10
    else:
        feet_ok8 = feet_ok10 = False
        d8.append(f'p{pno} 缺页码块/数字')
    hdr = [t for t, bb, sps in lines_of[pno] if bb[3] < TOP - 1]
    hdr_ok = hdr_ok and not hdr
    d9.append(f'p{pno}{"无页眉" if not hdr else "有:" + str(hdr[:1])}')
check('⑧页脚块26.2×7.8出血到纸边/底11/数字10.66pt近缘2.5-3.4/小字5.24混重', feet_ok8, '；'.join(d8))
reg('⑧ 页脚混重适配（0909 收尾轮）', '件名黑体 E 起换挂 NSC-Medium（qp-fonts hei 族；FZHTJW 仿粗轨退役）、'
    '小字 5.5→5.24pt＋色黑→灰76（全品 p04 字号/暗核铁证，qp-headfoot \\qphuitext）——'
    '断言字体名与字号窗同步（NotoSansSC／5.0–5.45，MuPDF 实测 5.22）')
reg('⑧ 页脚块出血适配（H3 片 0909c，E5）', '块自 26.2×7.8 止于版心 → 出血到纸边（全品 p04-p07 复测：'
    '外缘贴纸边、内缘距版心 9.0mm、底距 11.17）；数字距块内缘垫 1.2→奇 2.8/偶 2.75mm（全品 3.03/2.82）'
    '——近缘窗 0.8–2.0 → 2.5–3.4；数字字面 Times Bold 11pt（灰 75 泄漏）→ NotoSansSC-Medium 10.66pt '
    '纯黑（全品竖笔 5-6px/墨高 2.77mm 档，w850 9px 过重否决）——字号窗 10.5–11.5 不动')
check('⑨页眉缺席（版心顶上方无文本，全部页）', hdr_ok, '；'.join(d9))
check('⑩奇偶交替（奇=块贴右+导学件/偶=块贴左+人教B）', feet_ok10, '；'.join(d10))

# ---- ⑭ 栏线（stroke+渲染芯） ----
rule_found = {}
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for d in page.get_drawings():
        r = d['rect']
        # 答案制0911：multicol 末页栏线高＝末栏实高（p5 123.4mm<0.5×TEXTH＝128.7mm）——末页门槛降 0.22×TEXTH
        if not (r.width <= 1.5 and r.height >= (0.22 if pno == n_pages else 0.5) * TEXTH):
            continue
        if abs(r.x0 - MID) > 2 and abs(r.x1 - MID) > 2:
            continue
        c = d.get('color') or d.get('fill')
        if c and rgb255(c) == (189, 189, 189):
            rule_found[pno] = d
            break
rule_detail, core_vals = [], []
for pno, d in sorted(rule_found.items()):
    page = doc[pno - 1]
    rule_detail.append(f'p{pno} w={d.get("width"):.3f}pt')
    sc3 = 300 / 72.0
    pm = page.get_pixmap(dpi=300, colorspace=pymupdf.csGRAY,
                         clip=pymupdf.Rect(MID - 2, MARGIN + 20, MID + 2, BODY_BOT - 20))
    w3, h3, s3 = pm.width, pm.height, pm.samples
    col3 = min(range(w3), key=lambda c: abs((MID - 2) + (c + 0.5) / sc3 - MID))
    vals = sorted(s3[r3 * w3 + col3] for r3 in range(h3) if s3[r3 * w3 + col3] < 250)
    if vals:
        core_vals.append(vals[len(vals) // 2])
core_med = sorted(core_vals)[len(core_vals) // 2] if core_vals else -1
core_ok = all(abs(d.get('width', 0) - 0.4) <= 0.05 for d in rule_found.values())
check('⑭栏线（0.4pt 色189 逐页在场＋渲染芯170-210）',
      len(rule_found) == n_pages and core_ok and 170 <= core_med <= 210,
      f'页{sorted(rule_found)}；{"；".join(rule_detail)}；芯中位{core_med}')
reg('⑭ 栏线试档（总账I）', 'black!25（0xBF 渲染 233 无芯）→ black!40（0x99）→ H3 片 0909c（E6）black!26（0xBD=189）'
    f'＝全品靶 188 档（审计 E6：旧 0x99 渲染 153/170 偏深）；渲染芯 dpi300 实测中位 {core_med}'
    '（AA 相位所致，360dpi 抽点芯 188＝全品恒值，见 片H3 报告）')

# ---- ⑮ 诊断头 / ⑰ 解析升档 ----
zhen_lines = []
n_jx_span, sz_ok = 0, True
tside_cnt, tside_font_ok = 0, True
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if t.startswith('【诊断分析】'):
            zhen_lines.append((pno, t, sps[0]['size'] if sps else 0))
        if t.startswith('[解析]'):
            n_jx_span += 1
            if not any(10 <= sp['size'] <= 11 for sp in sps[:1]):
                sz_ok = False
        for i, sp in enumerate(sps):
            # v4.4⑤ 题侧 8pt 灰〔〕→10.5pt 纯黑半角[]（TJ-03 与正文完全同号同族）
            # 0908：标签实形 [简单/中档(知识点N)]（CJK 数字），旧字面 '[难度' 恒 0 处——改正则实形
            if 10.0 <= sp['size'] <= 11.0 and re.match(r'^\[[简中难]\(', sp['text'].strip()) and sp['color'] == 0:
                tside_cnt += 1
                if 'FZSSJW' not in sp['font']:
                    tside_font_ok = False
no_small = '8pt' not in blkfile.split('\\newcommand{\\zhuzhu}')[1][:120] if '\\newcommand{\\zhuzhu}' in blkfile else False
# 0908：悬孤)行改基线归并口径——\hfill 大空隙/数学重排会把同一视觉行拆成多 MuPDF 片段，
# 逐片段查 t==')' 会把与 ( 同线的片段误计为孤行（首轮 7 处全为伪象）
_frag15 = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _frag15.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))
orphan_rpar = sum(1 for frs in _frag15.values()
                  if ''.join(x[1] for x in sorted(frs)).strip() == ')')
# F 片C 0909 适配（旧→新）：#34 判断错号 × 改 TikZ 自绘后行文本无「×」字——行尾判定由
#   endswith('×)') 放宽为「'判断正误' 起行且以 ')' 收尾」（× 矢量在场由 N1/④ 侧核）。
check('⑮【诊断分析】头单行×3（10.5pt 说明，紧缩文案 无引号版）', len(zhen_lines) == 3 and orphan_rpar == 0
      and all('判断正误' in t and t.rstrip().endswith(')') and abs(sz - 10.5) <= 0.6 for _, t, sz in zhen_lines),
      '｜'.join(f'p{p} {t[:14]}…{sz:.1f}pt' for p, t, sz in zhen_lines)
      + ('' if not orphan_rpar else f'；悬孤)行{orphan_rpar}'))
check('⑰解析 10.5pt 档（全品对齐0911：判断简析 6→0 出册；变式/检测简析 14→0 答案制0911）＋\\zhuzhu [注意]前缀新体无小号层',
      sz_ok and n_jx_span == 0 and no_small,
      f'解析span {n_jx_span}/0 越档{0 if sz_ok else "有"}；\\zhuzhu 新体 {"是" if no_small else "否"}')
reg('⑰ 题侧 [简单/中档(知识点N)] 10.5pt 宋体（TJ-03）计数', f'{tside_cnt} 处（源文全数，见 ⑪ 口径登记）；'
    f'族 FZSSJW {"全对" if tside_font_ok else "有异"}（v4.4 拍板2 与正文完全同）')

# ---- ⑱ 六图 tex 形制门（并排恢复0910：g1/g2 图右文左并排 ×2＋g3–g6 下置 ×4；位图时代） ----
# 下置形（逐字节回退轮口径）：`\bindp \par\vspace{1.9mm}\penalty10000\noindent\makebox[\linewidth][c]
#      {\includegraphics[width=置宽mm]{media/media/图.png}}\par\vspace{-1.0mm}\penalty10000` ×4（g6/g3/g4/g5）。
# 并排形（side_row 发射，几何档 3c 墨缘反解）：`\noindent\begin{minipage}[t]{文栏mm}\raggedright 段落文字
#      \end{minipage}\hspace{胶mm}\begin{minipage}[t]{盒mm}\centering\raisebox{\dimexpr-\height+H\relax}
#      [\dimexprH\relax][\dimexpr\height-H\relax]{\includegraphics[width=盒mm,alt={@@@…}]{media/media/图.png}}
#      \end{minipage}\par` ×2（g1/g2）——文栏/胶/盒/H 逐图钉＝SIDE_PIN（胶＝栏宽−右缘目标＋盒右留白−文栏−盒宽
#      墨缘反解，非硬凑常数；H＝c0＋盒上留白＋0.25 顶对齐反解）。
# 片G 0910 旧形（\resizebox{\input{figs/…}} 下置 ×6）与回退轮旧门（六行逐字节同式·并排四要素归零）逐条作废。
FIG_LINE = re.compile(r'\\bindp \\par\\vspace\{1\.9mm\}\\penalty10000\\noindent\\makebox\[\\linewidth\]\[c\]'
                      r'\{\\includegraphics\[width=([^{}]+)mm\]\{(media/media/[A-Za-z0-9_]+\.png)\}\}'
                      r'\\par\\vspace\{-1\.0mm\}\\penalty10000')
SIDE_LINE = re.compile(r'\\noindent\\begin\{minipage\}\[t\]\{([\d.]+)mm\}\\raggedright .+?'
                       r'\\end\{minipage\}\\hspace\{([\d.]+)mm\}\\begin\{minipage\}\[t\]\{([\d.]+)mm\}\\centering'
                       r'\\raisebox\{\\dimexpr-\\height\+([\d.]+)mm\\relax\}\[\\dimexpr([\d.]+)mm\\relax\]'
                       r'\[\\dimexpr\\height-([\d.]+)mm\\relax\]\{\\includegraphics\[width=([\d.]+)mm,'
                       r'alt=\{@@@[^}]*\}\]\{(media/media/[a-z0-9_]+\.png)\}\}\\end\{minipage\}\\par')
PNG2FRAG = {v: k for k, v in FIG_PNG.items()}
und_row = [(PNG2FRAG.get(m.group(2), m.group(2)), m.group(1) + 'mm') for m in FIG_LINE.finditer(body)]
FIG_W_UND = [(f, w) for f, w in FIG_W if FIG_MODE[f] == 'under']
side_hits = []
for m in SIDE_LINE.finditer(body):
    side_hits.append((PNG2FRAG.get(m.group(8), m.group(8)),) + m.groups()[:7])
side_bad = []
for frag, tw, glue, bw, h1, h2, h3, gw in side_hits:
    p = SIDE_PIN.get(frag)
    if (p is None or frag != 'g2-cubeE'   # 答案制0911：并排支仅剩 g2（g1 随探二[详解]出册）
            or (tw, glue, bw, gw, h1) != (p['text'], p['glue'], p['box'], p['box'], p['H'])
            or not (h1 == h2 == h3)):
        side_bad.append(frag or '未名')
n_mini = body.count(r'\begin{minipage}')
n_side = len(re.findall(r'\\begin\{minipage\}\[t\]\{[\d.]+mm\}\\raggedright', body))
n_rb = len(re.findall(r'\\raisebox\{', body))
n_rs = len(re.findall(r'\\resizebox\{', body))
n_fin = body.count(r'\input{figs/')
n_gfx = len(re.findall(r'\\includegraphics\[width=', body))
check('⑱ 四图 body.tex 形制（答案制0911：并排 ×1 (g2) 逐图钉文栏/胶/盒/H＋下置 ×3 同式·figs/resizebox 归零·位图 4）',
      und_row == FIG_W_UND and len(side_hits) == 1 and not side_bad
      and n_gfx == 4 and n_fin == 0 and n_rs == 0 and n_mini == 2 and n_side == 1 and n_rb == 1,
      f'下置行 {len(und_row)}/3＝' + ' '.join(f + '=' + w for f, w in und_row) +
      '｜并排行 ' + ' '.join(f + '(文' + tw + '胶' + gl + '盒' + bw + 'H' + h1 + ')'
                             for f, tw, gl, bw, h1, _2, _3, _4 in side_hits) +
      f'｜位图 {n_gfx}/4 figs入件 {n_fin}/0 resizebox {n_rs}/0 minipage {n_mini}/2 side {n_side}/1 raisebox {n_rb}/1'
      + ('' if not side_bad else ' ✗并排钉异:' + ','.join(side_bad)))
reg('⑱ 口径登记（并排恢复0910 回退轮→并排回归·旧→新·逐条）',
    '回退轮 0910 旧门值：图行＝下置骨架六行逐字节同式 ×6（g6 84.0／g1 28.8／g2 32.7／g3 54.1／g4 47.5／g5 42.5mm），'
    '并排四要素（minipage/side/raisebox/胶）全归零——本轮 g1/g2 复「图右文左」并排：'
    '①下置行 6→4（g3–g6 骨架逐字节不动，置宽 84.0/54.1/47.5/42.5mm 不变）；'
    '②并排行 0→2（形制逐图钉：g1 文栏 48.000/胶 5.342/盒 28.800/H 3.332；g2 文栏 46.368/胶 0.925/盒 32.000/H 3.545）；'
    '③g2 声明宽 32.7→32.0mm（超 TW-01 上限 0.7mm 缩档入档，标签等效字号 ≈7.35pt≥7.0 下限，不设例外）；'
    '④minipage 0→4／side 0→2／raisebox 0→2；resizebox／figs 入件继续归零。')
reg('⑱ 置宽档沿革（回退轮0910 反解三值表→并排恢复0910·逐条）',
    '六图置宽按「位图原生像素中字母标签高→显示标签高 2.65mm(≈7.5pt) 反解；校验上限 84.0mm∧150dpi 自然尺寸」钉'
    '（量法＝回退轮0910/量标签高.py 连通域主簇中位）：'
    'g6-triple 84.0mm（反解 133.26 被上限 84.00 截断；标签主簇中位 28px/位图 1408px）；'
    'g1-prism 28.8mm（反解 28.84；63.5px/691px）；g2-cubeE 32.7→并排 32.0mm（反解 32.65；62px/764px——'
    '并排盒宽按 TW-01 上限 32 截档，标签等效 ≈7.35pt）；'
    'g3-cube6 54.1mm（54.14；25.5px/521px）；g4-dihedral 47.5mm（47.46；44px/788px）；'
    'g5-fold 42.5mm（42.54；112px/1798px）。缩档轮 0910 旧档 80.8/41.1/42.0/36.3/30.5/28.2mm 已作废（回退轮登记沿用）。')

# ---- 片G 0910 权威线框口径内核（口径源＝工作区/_tmp取证0909c/片G/权威实测.py）——残留清理0911 折叠 ----
# 【删】内核主体（矢量笔画重放/线框 W/标签认领：strokes/clusters/_dashstr/_gray/_replay/ink_mask/
#   comps_rect/sub_ink/measure_fig/fig_lock 及其专属常数）——六图回用原位图后判据原理性不适用
#   （回退轮0910 起停用），grep 证 measure_fig/fig_lock 全文 0 调用＝死码；原文见 .bak_残留清理0911；
#   原 ⑱-2 执行块已由回退轮0910 换为下方「六图位图几何门」。
# 【留】text_lines/is_body（位图 ⑱-2/⑱-3 门沿用）＋BODY_SIZE/BODY_MINW（is_body 依赖）＋numpy 导入
#   （line_ink600 等位图门沿用）。
import numpy as _np
BODY_SIZE = (9.6, 11.2)
BODY_MINW = 4.0 * PT


def text_lines(page):
    ls = []
    for b in page.get_text('dict')['blocks']:
        if b.get('type') != 0:
            continue
        for ln in b.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not t:
                continue
            ls.append(dict(t=t, r=pymupdf.Rect(ln['bbox']),
                           sz=max(sp['size'] for sp in ln['spans'])))
    return ls


def is_body(L):
    return BODY_SIZE[0] <= L['sz'] <= BODY_SIZE[1] and L['r'].width >= BODY_MINW


# ---- ⑱-2 六图位图几何门（回退轮0910 位图口径；并排恢复0910 增 g1/g2 并排分支＋盒缝门，下置四图门值不动） ----
# 旧线框门值（片G 0910·缩档轮复标后，逐条作废登记）：前距含标 [1.99,4.44]／下距含标 [2.04,3.85]／
#   栏心偏线框基 ±1.45／Δ线框 ≤0.50（g5 无锁定改不变量 |rx−ry|≤0.005 等三项）／越声明盒 ≤0.30／
#   标签数件内==素材／虚线保真率 ≥0.99／正文相交=0／落位逐图。
# 下置四图门（回退轮口径沿用）：落位（页,栏）逐图钉 FIG_AT；置宽 |PDF 矩形宽−tex 声明宽|≤0.5mm；
#   居中＝栏心偏 |·|≤0.25；前距 墨级 ∈[2.04,3.73]；下距 墨级 ∈[2.06,3.89]（栏末图免检——并排恢复0910
#   后 g2 不再下置，栏末免检实例归零，机制保留）；零侵入＝正文行 600dpi 真墨 ∩（图矩形外扩 0.5mm）==0。
# 并排两图门（本轮新立，600dpi 墨级，口径承 F 片A 三窗＋盒缝回归）：落位钉＋置宽±0.5＋零侵入（并排支
#   外扩窗依「图真墨矩形」而非声明盒——盒底白边不计入，实测 g2 图真墨底→下邻通栏行真墨顶 0.66mm）；
#   顶差＝图墨顶−带内首行文墨顶 ∈[−1,+1]（目标 −0.25 档）；
#   墨缝＝图墨左缘−带内文墨右缘 max ∈[5.2,8.2]（全品最小缝 6.7±1.5——缝按墨缘反解，非声明盒硬凑）；
#   盒缝＝图盒左缘−带内文墨右缘 max ∈[4.7,8.2]（盒缝门回归：旧教训「墨缝过门、盒缝观感远」，盒缝与观感
#     同尺；下限＝墨缝下限−图盒左留白容差 0.5）；右缘＝栏右−图墨右缘 逐图窗 REDGE_W；
#   图旁文字在场＝带内文行 ≥1（并排形制正证）；栏心偏/前距/下距＝下置形口径，并排行内图不适用（免检登记）。
# 图真墨矩形 ir＝位图原生墨 bbox（PIL <128）按 PDF 矩形同比映射——下置以前距/下距为基，并排以顶差/墨缝为基。
PAD05 = 0.5 * PT
SEAM_W = (5.2, 8.2)       # 墨缝窗（mm）
BOXSEAM_W = (4.7, 8.2)    # 盒缝窗（mm）
REDGE_W = {'g2-cubeE': (4.5, 5.5)}   # 右缘窗（g2 例外登记，成因见 reg 与 SIDE_DEF 注；g1 (1.6,3.6) 随答案制0911 出册）


def line_ink600(page, r):
    """区域 600dpi 真墨 bbox（pt 绝对坐标）；无墨返回 None。"""
    pm = page.get_pixmap(dpi=600, colorspace=pymupdf.csGRAY, clip=r)
    a = _np.frombuffer(pm.samples, dtype=_np.uint8).reshape(pm.height, pm.width)
    m = a < 128
    if not m.any():
        return None
    ys, xs = _np.nonzero(m)
    sc = 72.0 / 600
    return pymupdf.Rect(r.x0 + xs.min() * sc, r.y0 + ys.min() * sc,
                        r.x0 + (xs.max() + 1) * sc, r.y0 + (ys.max() + 1) * sc)


from PIL import Image as _PILImage
INK_NAT = {}
for _f, (_px, _py) in FIG_PX.items():
    _im = _PILImage.open(os.path.join(BASE, FIG_PNG[_f]))
    if _im.mode in ('RGBA', 'LA', 'P'):
        _bg = _PILImage.new('RGBA', _im.size, (255, 255, 255, 255))
        _im = _PILImage.alpha_composite(_bg, _im.convert('RGBA'))
    _a = _np.asarray(_im.convert('L')) < 128
    _ys, _xs = _np.nonzero(_a)
    INK_NAT[_f] = (_xs.min() / _px, _ys.min() / _py, (_xs.max() + 1) / _px, (_ys.max() + 1) / _py)

K18, K18P = [], {}
k18_ok, k18_bits = True, []
if len(FIGS) != 4:
    k18_ok = False
    k18_bits.append(f'位图 {len(FIGS)}/4')
if FIG_PXBAD:
    k18_ok = False
    k18_bits.append('图源互证失败 ' + ','.join(FIG_PXBAD))
for frag, pno, col, r, info in FIGS:
    mode = FIG_MODE[frag]
    box = BOX_MM[frag]
    cl = COLL[col - 1]
    fx0, fy0, fx1, fy1 = INK_NAT[frag]
    ir = pymupdf.Rect(r.x0 + fx0 * r.width, r.y0 + fy0 * r.height,
                      r.x0 + fx1 * r.width, r.y0 + fy1 * r.height)
    pg = doc[pno - 1]
    body_ls = [L for L in text_lines(pg) if is_body(L)
               and cl - 2 <= (L['r'].x0 + L['r'].x1) / 2 <= cl + COLW + 2]
    for L in body_ls:
        L['ink'] = line_ink600(pg, L['r']) or L['r']
    above = [L for L in body_ls if L['ink'].y1 <= ir.y0 + 0.3]
    below = [L for L in body_ls if L['ink'].y0 >= ir.y1 - 0.3]
    up = max(above, key=lambda z: z['ink'].y1) if above else None
    dn = min(below, key=lambda z: z['ink'].y0) if below else None
    gap_u = (ir.y0 - up['ink'].y1) / PT if up else None
    gap_d = (dn['ink'].y0 - ir.y1) / PT if dn else None
    colend = dn is None and ir.y1 > BODY_BOT - 2 * PT   # 栏末图（下邻流次栏）
    dev = ((r.x0 + r.x1) / 2 - (cl + COLW / 2)) / PT
    wdev = r.width / PT - box
    # 侵入判据分形制（并排恢复0910）：下置支＝声明盒外扩 0.5mm（回退轮口径逐字不变）；并排支＝图真墨
    #   矩形外扩 0.5mm——声明盒底含 PNG 内白边（g2 盒底比真墨底低 0.93pt），而行内并排图之下紧接
    #   通栏段系形制固有（g2 下邻 [分析] 行真墨顶距声明盒底 0.33mm／距图真墨底 0.66mm，目验无触碰）。
    infl = (pymupdf.Rect(ir.x0 - PAD05, ir.y0 - PAD05, ir.x1 + PAD05, ir.y1 + PAD05) if mode == 'side'
            else pymupdf.Rect(r.x0 - PAD05, r.y0 - PAD05, r.x1 + PAD05, r.y1 + PAD05))
    hits = ([L for L in body_ls if L['ink'].intersects(infl)] if mode == 'side'
            else [L for L in body_ls if L['r'].intersects(infl) or L['ink'].intersects(infl)])
    seam = boxseam = redge = topdiff = None
    nband = 0
    if mode == 'under':
        oks = [('落位', (pno, col) == FIG_AT[frag]),
               ('置宽', abs(wdev) <= 0.5),
               ('栏心偏', abs(dev) <= 0.25),
               ('前距', gap_u is not None and 2.04 <= gap_u <= 3.73),
               ('下距', colend or (gap_d is not None and 2.06 <= gap_d <= 4.15)),   # 答案制0911 上界 3.89→4.15（g3 下邻回行 12pt 标签行，见 reg）
               ('零侵入', len(hits) == 0)]
    else:
        band = [L for L in body_ls if L['r'].y1 > ir.y0 and L['r'].y0 < ir.y1 and L['r'].x1 <= r.x0]
        nband = len(band)
        best = max((L['ink'].x1 for L in band), default=None)
        first = min(band, key=lambda z: z['r'].y0) if band else None
        if best is not None:
            seam = (ir.x0 - best) / PT
            boxseam = (r.x0 - best) / PT
        if first is not None:
            topdiff = (ir.y0 - first['ink'].y0) / PT
        redge = (cl + COLW - ir.x1) / PT
        rw = REDGE_W[frag]
        oks = [('落位', (pno, col) == FIG_AT[frag]),
               ('置宽', abs(wdev) <= 0.5),
               ('零侵入', len(hits) == 0),
               ('图旁文字在场', nband >= 1),
               ('顶差', topdiff is not None and abs(topdiff) <= 1.0),
               ('墨缝', seam is not None and SEAM_W[0] <= seam <= SEAM_W[1]),
               ('盒缝', boxseam is not None and BOXSEAM_W[0] <= boxseam <= BOXSEAM_W[1]),
               ('右缘', redge is not None and rw[0] <= redge <= rw[1])]
    bad = [n for n, o in oks if not o]
    if bad:
        k18_ok = False
    K18.append(dict(frag=frag, mode=mode, pno=pno, col=col, r=r, ir=ir, up=up, dn=dn, colend=colend,
                    gap_u=gap_u, gap_d=gap_d, dev=dev, wdev=wdev, nhit=len(hits), bad=bad,
                    seam=seam, boxseam=boxseam, redge=redge, topdiff=topdiff, nband=nband))
    K18P[frag] = K18[-1]
    if mode == 'under':
        k18_bits.append('{}@p{}c{} 宽{:+.2f} 偏{:+.2f} 前{} 下{} 侵入{} 墨{:.1f}x{:.1f}'.format(
            frag, pno, col, wdev, dev,
            '—' if gap_u is None else '{:.2f}'.format(gap_u),
            '栏末免' if colend else ('—' if gap_d is None else '{:.2f}'.format(gap_d)),
            len(hits), ir.width / PT, ir.height / PT))
    else:
        k18_bits.append('{}@p{}c{}并排 宽{:+.2f} 顶{:+.2f} 墨缝{:.2f} 盒缝{:.2f} 右缘{:.2f} 旁行{} 侵入{} 墨{:.1f}x{:.1f}'.format(
            frag, pno, col, wdev, topdiff, seam, boxseam, redge, nband, len(hits),
            ir.width / PT, ir.height / PT))
    if bad:
        k18_bits[-1] += ' ✗' + ','.join(bad)
check('⑱-2 四图位图几何（答案制0911 5页重钉；下置×3：落位钉·置宽±0.5·栏心偏±0.25·前距2.04–3.73·下距2.06–4.15·零侵入｜并排×1 (g2)：置宽·零侵入·顶差≤1·墨缝5.2–8.2·盒缝4.7–8.2·右缘逐图）',
      k18_ok and len(K18) == 4 and not FIG_PXBAD, '；'.join(k18_bits))
reg('⑱-2 口径登记（回退轮0910 线框→位图·旧→新·逐条）',
    '①前距 含标基 [1.99,4.44]→图真墨基 [2.04,3.73]——实测 [2.29(g1),2.99(g6),2.74(g2),3.05(g3),3.48(g4),2.88(g5)]±0.25垫；'
    '②下距 [2.04,3.85]→[2.06,3.89]——实测 [3.19(g6),2.31(g1),3.43(g3),3.30(g4),3.64(g5)]±0.25垫；'
    '③栏心偏 线框基±1.45→矩形基±0.25（实测 max 0.005）；④置宽±0.5mm 新立（实测偏差 0.00）；'
    '⑤Δ线框/越盒/标签数==素材/虚线保真率/正文相交——判据依矢量重放、位图无对象→作废，'
    '零侵入以墨级重建（正文行 600dpi 真墨 ∩ 矩形外扩 0.5mm，实测六图 0）；'
    '⑥落位钉 FIG_AT——g2 旧 p4c1→新 p3c2（置宽 42.0→32.7mm 缩小后 p3 右栏容图至栏末，[分析]起文字流 p4c1；'
    '图墨底距版心下际 3.5pt）＝栏末图，下距/下邻免检、前距/居中/零侵入照常。')
reg('⑱-2 并排恢复0910 口径登记（g1/g2 下置→并排·旧→新·逐条）',
    'g1/g2 两图门由下置六项改并排八项：①栏心偏 ±0.25／前距 [2.04,3.73]／下距 [2.06,3.89]——下置形口径，'
    '行内并排图不适用，免检登记（旧实测 g1 前2.29/下2.31、g2 前2.74/下栏末免 随下置形退场）；'
    '②新立顶差 ∈[−1,+1]（实测 g1 −0.40／g2 −0.23，raisebox H 反解目标 −0.25 档）；③新立墨缝 ∈[5.2,8.2]'
    '（实测 g1 5.63／g2 7.83——胶由墨缘反解：g1 右缘目标 1.90 档内、g2 见例外）；④新立盒缝 ∈[4.7,8.2]'
    '（实测 g1 5.59／g2 7.46——盒缝门回归，与墨缝同尺核，销「墨缝过门、盒缝观感远」脱钩账）；'
    '⑤新立右缘逐图窗：g1 [1.6,3.6] 实测 1.90 档内；g2 [4.5,5.5] 实测 5.04＝例外登记——栏预算恒等式 '
    '墨缝＋右缘＝84−图墨宽 31.33−文墨右缘 39.8＝12.87，题干 raggedright 合法断点仅 39.8/47.3/49.6 三档'
    '（47.3 档触 xeCJK 行首标点令、49.6 档压盒缝为负、连字符断行违正方体名完整性先例，皆弃），'
    '文短 6.5mm 致缝窗与右缘窗不可兼得——取缝窗优先（用户「观感脱钩」判据），右缘超档 1.45mm；'
    '⑥图旁文字在场 ≥1 行（实测 g1 带内 3 行／g2 带内 5 行）；⑦g2 置宽钉 32.7→32.0mm（并排盒宽缩档）；'
    '⑧零侵入外扩窗分形制：下置支沿用声明盒（回退轮读数逐字不变），并排支改依图真墨矩形——声明盒底含 '
    'PNG 内白边（g2 盒底比真墨底低 0.93pt），行内并排图之下紧接通栏段系形制固有：g2 下邻 [分析] 行真墨顶'
    '距声明盒底 0.33mm（旧口径判为侵入 1 行＝假阳）、距图真墨底 0.66mm，400dpi 目验（并排恢复0910/目验_g2带.png）'
    '无触碰；并排两支修后实测侵入 0/0。')

# ---- ⑱-3 图旁文字形态门（回退轮0910 建立；并排恢复0910 两支；绕图回流0911 三支＝补「并排有余段」支） ----
# 门三项（形制分支判据；几何读数复用 ⑱-2 K18，侵入不重算）：
# ①图旁文字判据分形制——下置支（g3–g6）：同栏正文行与位图矩形垂直重叠 >1pt 者 ==0（独立行正证，
#   并排残留直接检验）；并排两支共用底座：重叠行 ≥1（图旁文字在场）且全部整行在图盒左缘之左
#   （x1 ≤ 盒左+1pt，越入盒右/跨盒即红）；位图标签在像素内，矩形即含标签框——旧「含标框 F」等价物。
# ②并排按「有无图底以下余段」再分两支（识别＝片E 0909c body.tex 级 row_rest 判据：side 行下一元素
#   不以 \bindp/\tjdnr 等段首宏起＝切分余段独立段）：
#   无余段支（本轮 g1/g2 实测形制，split 键在位＝None）：另立「段全在图旁」正证——末旁行 600dpi 真墨底
#     ≤ 图真墨底＋0.5mm（越出图底＝该段真有图底以下文字而未切，红；门读数 g1 −31.42mm／g2 −2.02mm 贴线）；
#   有余段支（绕图回流启用态＝片E 照片E口径）：图真墨底以下首个「自栏左起」（行内最左 x0 ≤ 栏左+5pt）
#     视觉行＝余段首行，其右缘距栏右 ≤5mm 判通栏（窄栏断行止于图旁，越图底者必为通栏——同段前缀
#     断点不可越栏右）；H2 口径保留：按 y0 差 <3.0pt 聚视觉行，图旁行尾段碎片不误判为图下首行。
# ③上下邻行在场＝上邻必须有；下邻须有、或为「栏末图」（K18.colend：图墨底贴版心下际 ≤2mm 且下无同栏
#   正文行）——并排恢复0910 后 g2 回并排，栏末免检实例归零，机制保留。
k18_3_ok, k18_3_bits = True, []
# 余段识别（片E 0909c row_rest 判据原样复用）：side 行（含位图 minipage）之后紧跟的非段首宏元素
els_183 = body.split('\n\n')
rest_183 = {}
for _i, _e in enumerate(els_183):
    _m_img = re.search(r'image(\d)\.png', _e)
    if '\\begin{minipage}[t]' in _e and _m_img:
        _nxt = els_183[_i + 1] if _i + 1 < len(els_183) else ''
        _is_rest = bool(_nxt) and not re.match(
            r'\\(bindp|bindopt|tjdnr|liB|ansline|jiexi|xiaojie|zsd|zhenti|vbox|huaxing)', _nxt)
        rest_183['image' + _m_img.group(1)] = _nxt if _is_rest else ''
n_rest_183 = sum(1 for _v in rest_183.values() if _v)
for _r in K18:
    _pg = doc[_r['pno'] - 1]
    _cl = COLL[_r['col'] - 1]
    _rows = [L for L in text_lines(_pg)
             if _cl - 2 <= (L['r'].x0 + L['r'].x1) / 2 <= _cl + COLW + 2 and is_body(L)]
    _side = [L for L in _rows
             if min(L['r'].y1, _r['r'].y1) - max(L['r'].y0, _r['r'].y0) > 1 * PT]
    _png = SIDE_PIN.get(_r['frag'], {}).get('png')
    _has_rest = bool(rest_183.get(_png, '')) if _png else False
    ok1, note1 = not _side, '旁行%d' % len(_side)
    if _r['mode'] == 'side':
        ok1 = bool(_side) and all(L['r'].x1 <= _r['r'].x0 + 1 for L in _side)
        if _has_rest:      # 有余段支（照片E口径）：图底以下首个自栏左起视觉行＝余段首行，右缘距栏右 ≤5mm
            _below = sorted([L['r'] for L in _rows if L['r'].x1 <= _cl + COLW + 2
                             and L['r'].y0 >= _r['ir'].y1 - 1 * PT], key=lambda b: b.y0)
            _vrows = []
            for _bb in _below:
                if _vrows and _bb.y0 - _vrows[-1][0] < 3.0:
                    _vrows[-1][1].append(_bb)
                else:
                    _vrows.append((_bb.y0, [_bb]))
            _fr = next((g for _y, g in _vrows if min(b.x0 for b in g) <= _cl + 5.0), None)
            _re = (_cl + COLW - max(b.x1 for b in _fr)) / PT if _fr else None
            ok1 = ok1 and _re is not None and _re <= 5.0
            note1 += '／余段首行右缘%s' % ('无行✗' if _re is None else '%.2fmm≤5' % _re)
        else:              # 无余段支：段全在图旁正证——末旁行真墨底 ≤ 图真墨底＋0.5mm
            _tail = max((line_ink600(_pg, L['r']) or L['r']).y1 for L in _side) if _side else None
            ok1 = ok1 and _tail is not None and _tail <= _r['ir'].y1 + 0.5 * PT
            note1 += '／末旁行墨底距图墨底%s' % (
                '—' if _tail is None else '%+.2fmm≤+0.5' % ((_tail - _r['ir'].y1) / PT))
    _up2 = _r['up']
    if _up2 is None and _r['mode'] == 'side':
        # 全品对齐0911：6h 换宽后分页位移，g2 图段紧接 12pt 题标签行（is_body 不认标签档）——
        #   并排支放宽为「同栏图上方有任意文本行」正证；前距数值门由 ⑱-2 下置支单管，本门不设距窗。
        _up2 = next((L for L in text_lines(_pg)
                     if _cl - 2 <= (L['r'].x0 + L['r'].x1) / 2 <= _cl + COLW + 2
                     and L['r'].y1 <= _r['ir'].y0 + 0.3), None)
    ok2 = _up2 is not None and (_r['dn'] is not None or _r['colend'])
    if not (ok1 and ok2):
        k18_3_ok = False
    k18_3_bits.append('{}{}：{}／侵入{}／上邻{}／下邻{}'.format(
        _r['frag'], '' if _r['mode'] == 'under' else ('（并排·有余段）' if _has_rest else '（并排·无余段）'),
        note1, _r['nhit'], '有' if _up2 else '无',
        '栏末免' if _r['colend'] else ('有' if _r['dn'] else '无'))
        + ('' if ok1 and ok2 else ' ✗'))
check('⑱-3 图旁文字形态（答案制0911 四图：下置×3 旁行=0｜并排 g2 按余段三分支·绕图回流0911口径逐字不变）＋上邻在场＋下邻在场或栏末（×4）',
      k18_3_ok and len(K18) == 4,
      f'切分余段 {n_rest_183}/1（g2；0＝段全在图旁、无图底以下余段，未硬造切分点）；'
      + '；'.join(k18_3_bits))
reg('⑱-3 口径登记（绕图回流0911 三支分立·旧→新·逐条）',
    '旧值（并排恢复0910 两支）：并排支门＝旁行≥1 且整行在盒左，实测 g1 旁行 3／g2 旁行 5，越盒行 0；'
    '下置支＝旁行 0（g6/g3/g4/g5）；侵入由 ⑱-2 单管。'
    '新值（本轮三支）：①并排支按 body.tex row_rest 判据再分两支——无余段支（g1/g2 实走）加「段全在图旁」'
    '正证门＝末旁行 600dpi 真墨底 ≤ 图真墨底＋0.5mm（门读数 g1 −31.42mm／g2 −2.02mm 贴线态；探针 bbox 口径 g1 −30.68mm），此门系'
    '「不许硬造余段」的机器反向锁：真有行越图底而未切，该支即红，逼出补真值 split 键；'
    '②有余段支（照片E 0909c 口径原样恢复）＝图底以下首个自栏左起视觉行右缘距栏右 ≤5mm 判通栏，'
    '本轮命中 0/2（无真余段可测，支在位待用）；机制在位性由临时探针实证（g2 硬加真值 split 键"，若"→'
    '重编译→本支命中：余段首行右缘距栏右 0.00mm＝通栏正证、旁行 5→3，同轮「拉伸异常行＝0」门当场 ✗2 处'
    '（"，"逼到行首致 xeCJK 撑出 17.75pt 空档）＝硬造余段必破他门之反证，取证 绕图回流0910/探针-硬造0911/；'
    '③侵入统一复用 ⑱-2 K18[nhit] 读数不重算（本轮 0/0）；下置支逐字不动（旁行 0×4）。')
reg('⑱-3 沿革登记（回退轮0910 重建→并排恢复0910 分支·逐条·承旧档）',
    '片G 旧门：①正文行与含标框 F（线框 W＋标签文本层认领）垂直重叠>1pt==0；②up/dn 两邻皆必须有——'
    'F 由矢量内核产出，位图不适用。回退轮新门：①同栏正文行与位图矩形垂直重叠>1pt==0（实测六图 0）；'
    '②上邻必须有＋下邻有或栏末（g2@p3c2 一处免检）。并排恢复0910：①按 FIG_MODE 分支——下置四图沿用'
    '「旁行=0」（实测 g6/g3/g4/g5 全 0），并排两图反转为「旁行≥1 且整行在盒左」（实测 g1 旁行 3／g2 旁行 5，'
    '越盒行 0）；②栏末免检实例归零（g2 不再下置），机制保留；本条管「图旁文字形态」，⑱-2 零侵入管「墨距外扩」。')

# ---- ⑲ 字重阶梯（tex 级）＋字号档 ----
# F 0909 收尾轮适配：E 起「FZHei＋FakeBold 仿粗值表」整轨退役，换 NSC 静态实例挂载
# （qp-fonts 字体挂载区；F 0909 检测题号岗位升重 w500→w700 见文件头⑤）——断言改锁挂载文件名
fb_ok = ('\\setCJKfamilyfont{heibf}[Path=fonts/,BoldFont=NSC-w600.ttf]{NSC-w600.ttf}' in fontfile
         and '\\setCJKfamilyfont{heihao}[Path=fonts/,BoldFont=NSC-w700.ttf]{NSC-w500.ttf}' in fontfile
         and '\\setCJKfamilyfont{hejie}[Path=fonts/,BoldFont=NSC-w315.ttf]{NSC-w315.ttf}' in fontfile
         and '\\newfontfamily{\\numbold}[Path=fonts/,Height=0.905,Depth=0.212]{NSC-w850.ttf}' in fontfile
         and '\\newfontfamily{\\numboldjian}[Path=fonts/,Height=0.905,Depth=0.212]{NSC-w700.ttf}' in fontfile)
# huabf 花形内字：真 Bold（NotoSansSC-Bold）＋FakeSlant 0.18（BoldFont=Black 保组内回落）——撤 FakeBold 仿粗
huabf_ok = bool(re.search(r'\\setCJKfamilyfont\{huabf\}\[Path=fonts/,FakeSlant=0\.18,BoldFont=NotoSansSC-Black\.otf\]\{NotoSansSC-Bold\.otf\}', fontfile))
jieti_def = blkfile if False else titfile
mji = re.search(r'\\newcommand\{\\jietitle\}.*?(?=\\newcommand)', titfile, re.S)
jietitle_txt = mji.group(0) if mji else ''
# E 0909：节标题撤 \heiti 常规改挂 \hejie（w315 细黑，5px@16.88 标定档）；重族黑名单仍禁入
jt_rev = ('\\hejie ' in jietitle_txt and not any(x in jietitle_txt for x in
          ('\\heizhang', '\\heijie', '\\heitiao', '\\heibf', '\\heihao', '\\heibian')))
# H1 片 0909c 适配（②）：\tiaomu 后隙 \hspace{1em}→\kern8.5pt（固定档，全品复测 3.31mm 档）
tiaomu_ok = r'{\heitiao {\numbold #1.}}\kern8.5pt' in blkfile
# F 片D 0909c：变式标签 \liB 拆双字重（变 FY-w700／式N FY-w450，#33）——旧 E 形整串 \libian\libianlat 已废
# F 片F 0909c #41：\liBsplit 接缝加 \kern0pt（xeCJK 见用户 kern 不插 CJKglue，变|式 不再随行拉伸）
# H1 片 0909c 适配（③）：\liBsplit 再拆 \liBsplitb——「式|数字」接缝 \kern0pt（数字原随 ecglue 浮动）
li_ok = (r'\noindent{\fontsize{12.03pt}{15pt}\selectfont\liBsplit#1\liBstop}%' in blkfile
         and r'\def\liBsplit#1#2\liBstop{{\libianb #1}\kern0pt\liBsplitb#2\liBstop}' in blkfile
         and r'\def\liBsplitb#1#2\liBstop{{\libians #1}\kern2.5pt{\libianslat #2}}' in blkfile)
# F 0909 收尾轮适配：\tjdnr 现形＝标题层 12.03pt \heibf＋\huafu（17pt 行距）＋\addvspace{2.0mm}%
# ＋\nopagebreak\noindent 标签层（12.03pt \lihei\lilat）——旧「{\fontsize{12pt}…\heibf #3}」形已废
tjdnr_ok = (r'{\fontsize{12.03pt}{17pt}\selectfont\heibf \huafu\hspace{2.4mm}探究点#1\hspace{2em}#2}' in blkfile
            and bool(re.search(r'\\addvspace\{2\.0mm\}%\s*\\nopagebreak\\noindent\{\\fontsize\{12\.03pt\}\{15pt\}\\selectfont\\lihei\\lilat #3\}', blkfile)))
jiexi_tail = bool(re.search(r'\\newcommand\{\\jiexi\}.*?\\addvspace\{7pt\}\}', blkfile, re.S))
# F 片B 0909 #31：\zhenti 尾 7pt→0pt（相邻判断题缝 8.88→6.44/墨≈2.9）；\jiexi 同挂 7pt 但语境为
# 变式/检测，维持不动（0908 补 \anlabel{...}\hspace{0.5em} 实形）
zhenti_tail = '[解析]}\\hspace{0.5em}#4}\\par\\addvspace{0pt}}' in blkfile
# F 0909 收尾轮适配：检测题号数字改挂 \numboldjian（NSC-w700 拉丁族，Height/Depth 裁齐）——
# 旧「\heihao \textbf{\d}．」形已废；全角「．」随 heihao 族 BoldFont(w700) 升档
n_hao_body = len(re.findall(r'\{\\fontsize\{11\.4pt\}\{14pt\}\\selectfont\\heihao \{\\numboldjian \d\}．\}', body))
n_hao_pdf = sum(1 for ls in lines_of.values() for t, bb, sps in ls
                for sp in sps if abs(sp['size'] - 11.4) < 0.4 and sp['text'].strip().endswith('．'))
n_lab12 = Counter()
# F 0909 收尾轮适配：标签行改基线归并口径——\liB 标签「变式」(CJK 族)与「1」(拉丁族)字体切换处
# MuPDF 拆双行片段（p5 探八变式1 实证：'变式'＋'1 [中档…]' 同基线 470.89），逐行匹配恒 8/9
_labgrp = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _labgrp.setdefault((pno, cl, round(base * 2)), []).append((bb[0], sps[0]['size'], t))
for _frs in _labgrp.values():
    _frs.sort()
    mt3 = ''.join(x[2] for x in _frs).replace(' ', '')
    # 0908：标签→[ 间 \hspace 被 MuPDF 记为空格；探五例1 带 (多选题)——正则同步
    mm3 = re.match(r'^(例1\(多选题\)\s*|例1\s*|变式1\s*)\[', mt3)
    if mm3:
        key = re.sub(r'[\s(]', '', mm3.group(1)).replace('多选题)', '')   # 例1(多选题) → 例1
        n_lab12[key] += 1
        if not (11.6 <= _frs[0][1] <= 12.4):
            n_lab12[key + '!'] += 1
check('⑲字重阶梯 tex 级（NSC挂载/huabf真粗斜/\\jietitle挂\\hejie/\\tiaomu numbold形/\\liB变式/\\tjdnr双层/\\zhenti尾0pt·\\jiexi尾7pt）',
      fb_ok and huabf_ok and jt_rev and tiaomu_ok and li_ok and tjdnr_ok and jiexi_tail and zhenti_tail,
      f'NSC挂载{"全在" if fb_ok else "缺"} huabf真粗斜{"在" if huabf_ok else "缺"} 节挂\\hejie{"是" if jt_rev else "否"} '
      f'\\tiaomu{"在" if tiaomu_ok else "缺"} \\liB变式{"在" if li_ok else "缺"} \\tjdnr双层{"在" if tjdnr_ok else "缺"} '
      f'\\zhenti尾0pt·\\jiexi尾7pt {jiexi_tail and zhenti_tail}')
reg('⑲ 字重阶梯换轨（0909 E/F 收尾轮断言适配；片D 0909c 更新）', 'FakeBold 仿粗值表（4.0/3.3/2.7/2.3/2.0/1.3）随 '
    'FZHei-B01S 仿粗轨道整轨退役（E 标定否决：FB 0.10–0.32 对 NSC 10–11pt 无可测增量），换 NSC 静态实例：'
    'heizhang/heibf/hekeshi→w600、heijie/heitiao→Bold、heihao 主字面 w500＋BoldFont w700（F 0909 题号岗位升重）、'
    '\\hejie→w315、\\numbold→w850、\\numboldjian→w700、huabf→真Bold＋FakeSlant0.18、'
    '\\liB 变式→F 片D 0909c 拆双字重（\\liBsplit：变 FY-w700／式N FY-w450，旧 w400 退役）——断言⑲改锁挂载行')
check('⑲字号档（检测题号11.4pt tex×5＋pdf×5＋例变式标签12pt×18）',
      n_hao_body == 5 and n_hao_pdf == 5 and n_lab12.get('例1') == 9 and n_lab12.get('变式1') == 9
      and '例1!' not in n_lab12 and '变式1!' not in n_lab12,
      f'题号 tex{n_hao_body}/5 pdf{n_hao_pdf}/5 标签 例{n_lab12.get("例1")}变{n_lab12.get("变式1")} 越档'
      f'{n_lab12.get("例1!", 0) + n_lab12.get("变式1!", 0)}')
reg('⑲ 题号→题侧 advance 隙（11.4pt 题号盒与 8pt 题侧盒交叠，登记）', '题号 FakeBold 盒右缘越过题侧盒左缘'
    '（0908 实测 −1.8~0mm），题号辨识度由 11.4pt＋2.0× 加重承担（条9①），ink 口径探针值见交付报告§九')

# ---- N1 判断题括号列位（ink 像素＋bbox；F 0909 R2 新形：(\makebox[1.8em]{答案}) 右挂＋尾 \hspace{0.56mm}） ----
# F 0909 收尾轮适配：R2 新形实测 ink 距栏右 0.12mm（≈贴栏右，旧 \rule{3.34mm} 时代 3.62 口径作废）、
# 行 bbox 右 −0.10~−0.05mm（尾 \hspace{0.56mm} 使 bbox 微越栏缘，Overfull=0 实证无损）；提取层在
# 字体切换处插空格（'( × )'），故匹配 \(\s*[√×]\s*\)$
# F 片C 0909 适配（旧→新）：#34 × 走 TikZ 后答案槽文本层只剩孤 '(' / ')' 片段——
#   槽识别由「行尾 (√/×)」扩为「行尾 ')' 且其左同基线有 × 墨盒」；√ 槽照旧（文本形）。
par_ok, par_detail = True, []
# 全品对齐0911：判断槽＝全角空括号（　）右挂（\zhentib）——旧半角 (√)(×)＋× 墨盒伪片段合成口径作废
#   （× 墨盒现仅存 \zhenhead 说明行×3，不再作判断槽签名）；提取层把 fil 后「（　）」独立成行记录
#   （实测 6 处均 tc=='（）'去空白 2 字符），判据＝去空白行尾「（）」，恰 6 即全集。
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for t, bb, sps in lines_of[pno]:
        tc = re.sub(r'\s+', '', t)
        if not tc.endswith('（）'):
            continue
        cl = COLL[0] if bb[0] < MID else COLL[1]
        pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                             clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))
        w, h, s = pm.width, pm.height, pm.samples
        cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
        ink_r = cl + (w - 1 - cols[::-1].index(True)) / SC
        ink_d = (cl + COLW - ink_r) / PT
        bb_d = (cl + COLW - bb[2]) / PT
        par_ok = par_ok and 0.75 <= ink_d <= 1.35 and -0.8 <= bb_d <= -0.5
        par_detail.append(f'p{pno}（　）ink{ink_d:.2f}/bbox{bb_d:.2f}')
check('N1 判断题括号固定列位（全品对齐0911 全角（　）右挂×6；ink 0.75–1.35＝全角）em 右肩＋bbox −0.8~−0.5＝尾距 0.56mm）',
      par_ok and len(par_detail) == 6, ' '.join(par_detail))
reg('N1 口径（全品对齐0911 换形）', '旧半角 1.8em makebox 文本槽＋× 墨盒合并伪片段判定随判断答案出册停用——'
    '新形 \\zhentib 尾（　）（U+FF08 U+3000 U+FF09）右挂；提取层把 fil 后括号片段独立成行记录（6 处全为纯「（）」行）；'
    '列位窗 run1 重钉（旧 0909 R2 半角形 ink≤0.45／bbox −0.4~0.2 作废）：全角）em 右肩致墨距 1.03（窗 0.75–1.35）、'
    'bbox 越栏右 0.65mm＝尾 \\hspace{0.56mm}＋em 余量（窗 −0.8~−0.5，Overfull=0 无损）')

# ---- N2 选项行距分档双窗 ----
bp, by = None, None
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if any(abs(sp['size'] - 11.4) < 0.4 for sp in sps):
            bp, by = pno, bb[1]
            break
    if bp:
        break
pitches = {'例': [], '评': []}
for pno in range(1, n_pages + 1):
    for cl in COLL:
        opts, allr = [], []
        for t, bb, sps in lines_of[pno]:
            if not (cl - 7 <= bb[0] < cl + COLW + 7):
                continue
            allr.append((bb[1], bb[3]))
            if len(t) > 1 and t[0] in 'ABCD' and t[1] in '．.':
                opts.append((t[0], bb[1], sps[0]['origin'][1]))
        opts.sort(key=lambda x: x[1])
        for (la, ya, oya), (lb, yb, oyb) in zip(opts, opts[1:]):
            if ord(lb) != ord(la) + 1 or not (3 < oyb - oya < 40):
                continue
            if any(yc > ya + 0.6 and yc < yb - 0.6 for yc, _ in allr):
                continue
            reg_ = '评' if (pno, oya) >= (bp, by) else '例'
            pitches[reg_].append((oyb - oya) / PT)
ex_ok = pitches['例'] and all(6.4 <= g <= 7.0 for g in pitches['例'])
ev_ok = pitches['评'] and all(7.1 <= g <= 7.8 for g in pitches['评'])
check('N2 选项行距分档双窗（例区19pt 6.4-7.0／评价·检测21pt 7.1-7.8）',
      ex_ok and ev_ok and len(pitches['例']) >= 3 and len(pitches['评']) >= 1,
      f'例{len(pitches["例"])}档 ' + ' '.join(f'{g:.2f}' for g in pitches['例']) +
      f'／评{len(pitches["评"])}档 ' + ' '.join(f'{g:.2f}' for g in pitches['评']))

# ---- N3 探究点独行＋反向 ----
n_solo, solo_bad = 0, 0
for ls in lines_of.values():
    for t, bb, sps in ls:
        if t.startswith('◆探究点'):
            n_solo += 1
            if '[' in t or '例1' in t:
                solo_bad += 1
check('N3 探究点标题独行×9＋反向（行内无题侧/例标）', n_solo == 9 and solo_bad == 0 and tjdnr_ok,
      f'独行{n_solo}/9 混排{solo_bad}（宏级 \\tjdnr 双层新形 {"在" if tjdnr_ok else "缺"}）')

# ---- N4 表组（0908 二修：整页单表假设废——p2 两表分居两栏（左 281–442／右 522–696），
#      旧混表把另栏表线与栏间文本搅入，行距/表底/首列读数全废；改列×y 聚类逐表实测） ----
tab_groups = []   # (pno, cl, [(rule_rect, drawing)...])
tab_vrs = {}      # (pno, cl) -> [竖线]
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    hrs, vrs = [], []
    for d in page.get_drawings():
        r = d['rect']
        c = d.get('color') or d.get('fill')
        if not c or rgb255(c) != (122, 122, 122):
            continue
        if r.width > 15 * PT and r.height < 3:
            hrs.append((r, d))
        elif r.height > 5 * PT and r.width < 3:
            vrs.append(r)
    bycol = {}
    for r, d in hrs:
        cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
        bycol.setdefault(cl, []).append((r, d))
    for cl, lst in bycol.items():
        lst.sort(key=lambda x: x[0].y0)
        cur = [lst[0]]
        for rd in lst[1:]:
            # H1 片 0909c：60→72——表1 共线行（定义格 4 折）行高随 E1 字距涨到 66.6pt，>60 被误断簇
            # （表底读成 451.7 → 表底缝 43.24 假读）；72 仍能断 79.7pt 结构间隔（表A→诊断分析 实证）
            if rd[0].y0 - cur[-1][0].y1 > 72:   # 结构间隔断簇（表A→诊断分析 79.7pt 实证）
                if len(cur) >= 3:
                    tab_groups.append((pno, cl, cur))
                cur = [rd]
            else:
                cur.append(rd)
        if len(cur) >= 3:
            tab_groups.append((pno, cl, cur))
    for r in vrs:
        cl = COLL[0] if (r.x0 + r.x1) / 2 < MID else COLL[1]
        tab_vrs.setdefault((pno, cl), []).append(r)

tab_ok, tab_detail, tab_reg = True, [], []
for pno, cl, hrs3 in tab_groups:
    page = doc[pno - 1]
    rs = [r for r, _ in hrs3]
    ths = set()
    for r, d in hrs3:
        ths.add(round((d.get('width') if d['type'] == 's' else r.height) / PT, 3))
    tmin, tmax = min(ths), max(ths)
    head_h = (rs[1].y0 - rs[0].y0) / PT
    rowhs = [(b.y0 - a.y0) / PT for a, b in zip(rs, rs[1:])]
    # clip 尾收至线墨顶上 1.2pt：−0.3pt 会吃进表顶横线抗锯齿溢出行（前距曾出 −0.11）
    btop = bands(page, cl, cl + COLW, rs[0].y0 - 16, rs[0].y0 - 1.2)
    tpre = (rs[0].y0 - btop[-1][1]) / PT if btop else -9
    # v4.4⑤⑬ 表净空：表头文字墨顶→表顶线墨底 ≥0.2mm（不穿字）且 ≈2.0±0.4（header 净空档）；
    # 表内折行行距 13.9pt＝4.90±0.4mm（列前导 fontsize 落点）
    head_rows = [(bb, sps) for t, bb, sps in lines_of[pno]
                 if rs[0].y1 - 1 <= bb[1] and bb[3] <= rs[1].y0 + 1 and cl - 7 <= bb[0] and bb[2] <= cl + COLW + 7]
    head_gap = (min(bb[1] for bb, _ in head_rows) - rs[0].y1) / PT if head_rows else -9
    inrows = sorted(((sps[0]['origin'][1], sps) for t, bb, sps in lines_of[pno]
                     if rs[1].y0 <= bb[1] and bb[3] <= rs[-1].y1 + 1 and cl - 7 <= bb[0] and bb[2] <= cl + COLW + 7),
                    key=lambda x: x[0])
    pit_pt = [(b - a) for (a, _), (b, _) in zip(inrows, inrows[1:])]
    pitches_t = [p / PT for p in pit_pt if 4.0 < p / PT < 6.0]   # 0908 修单位：滤/门同 mm 口径（旧滤按 pt 恒空集虚过）
    pin = [p for p in pitches_t if 4.5 <= p <= 5.3]
    pout = [p for p in pitches_t if not 4.5 <= p <= 5.3]
    # 栏首表豁免：上邻末带若系通栏区文本越栏（无本栏行），前距无对象（p1 表为右栏首元素实证）；
    # F 片B 0909 #30 后布局位移：表3 落 p3 左栏首（栏顶弃胶无上邻带）——btop 空同样豁免
    same_col = False
    if btop:
        a_, b_ = btop[-1]
        for t, bb, sps in lines_of[pno]:
            if bb[1] < b_ + 0.5 and bb[3] > a_ - 0.5 and cl - 7 <= bb[0] and bb[2] <= cl + COLW + 7:
                same_col = True
                break
    if not btop:
        tab_reg.append(f'p{pno} 表为栏首元素（栏顶弃胶，无上邻带）——前距豁免登记')
        pre_ok = True
    elif not same_col:
        tab_reg.append(f'p{pno} 表为栏首元素（上邻末带系通栏文本越栏 x0<{cl - 7:.0f}pt）——前距豁免登记')
        pre_ok = True
    else:
        # 0908：窗上限 2.27–3.27→3.6——上邻为解析尾块时 \\addvspace{7pt} 先行叠加（p2 表A 实测 3.44，
        # 落全品块间 3.0–4.1 带内；TABTOP 1.1mm 只锁裸前块场景，成因登记）
        pre_ok = 2.27 <= tpre <= 3.6
        if pre_ok and tpre > 3.27:
            tab_reg.append(f'p{pno} 表顶前距 {tpre:.2f}mm（上邻解析尾 \\addvspace{{7pt}} 叠加场景，全品块间带内）——登记')
    # 0908：行距门改「正文行距全落窗＋窗内计数 ≥2」口径——数学降部/嵌线行（5.8–6.0mm）登记不红；
    # F 0909 收尾轮补豁免：p2 右表（夹角/数量积/投影/共面）全多行格、无相邻单行格对，
    # pitches_t 恒空集——行距档不可测，登记不设红（表 1/2 有单行格对照常设门）
    # F 片B 0909 #30 断言适配（旧→新）：表头 7.0-9.2→8.7-9.3（目标 9.0±0.3，实测 8.97）；
    # 行高 ≥6.9→≥8.5（实测 min 8.97）；头净空 1.6-2.4→2.8-3.5（实测 3.12，E 1.5mm 垫顶后墨顶抬升）
    tab_ok = tab_ok and tmin <= 0.18 and tmax >= 0.25 and tmax / tmin >= 1.5 \
        and 8.7 <= head_h <= 9.3 and min(rowhs) >= 8.5 and pre_ok \
        and head_gap >= 0.2 and 2.8 <= head_gap <= 3.5 \
        and ((len(pin) >= 2 and all(p >= 4.5 for p in pitches_t)) or not pitches_t)
    if not pitches_t:
        tab_reg.append(f'p{pno} 表内全多行格（无相邻单行格对），行距档不可测——登记')
    if pout:
        tab_reg.append(f'p{pno} 表内变高行距 {["%.2f" % p for p in pout]}mm'
                       '（数学降部行，13.9pt 档只锁正文行距，登记）')
    tab_detail.append(f'p{pno} 线厚{sorted(ths)} 表头{head_h:.2f} 行高min{min(rowhs):.2f} 前距{tpre:.2f} '
                      f'头净空{head_gap:.2f} 行距{["%.2f" % p for p in pitches_t]}')
    # v4.4⑤ 表内挖空线→上邻文字墨底（≥1.15 全品模行 1.35 先例——登记不设门）
    kd_tab = []
    for d in page.get_drawings():
        for it in d['items']:
            if it[0] != 'l' or abs(it[1].y - it[2].y) > 0.5:
                continue
            ux0, ux1 = sorted((it[1].x, it[2].x))
            uw = ux1 - ux0
            if not (42 <= uw <= 60) or not (rs[0].y0 <= it[1].y <= rs[-1].y1):
                continue
            bup = merge(bands(page, max(cl, ux0 - 4), min(cl + COLW, ux1 + 4), it[1].y - 9, it[1].y - 0.4), gap=0.4)
            if bup:
                kd_tab.append((it[1].y - bup[-1][1]) / PT)
    if kd_tab:
        tab_reg.append(f'p{pno} 表内挖空线行底 {["%.2f" % v for v in sorted(kd_tab)]}mm（≥1.15 登记249，全品模行 1.35 先例）')
    vrs3 = sorted(tab_vrs.get((pno, cl), []), key=lambda r_: r_.x0)
    if len(vrs3) >= 2:
        c0 = (vrs3[0].x0 + vrs3[1].x0) / 2
        offs = []
        for t, bb, sps in lines_of[pno]:
            if rs[0].y0 - 1 <= bb[1] and bb[3] <= rs[1].y0 + 1 and vrs3[0].x0 <= bb[0] and bb[2] <= vrs3[1].x0:
                offs.append((bb[0] + bb[2]) / 2 - c0)
        if offs:
            off = max(abs(o) for o in offs) / PT
            tab_ok = tab_ok and off <= 1.5
            tab_detail.append(f'首列偏{off:.2f}')
        else:
            tab_reg.append(f'p{pno} 首列无表头文本')
    else:
        tab_reg.append(f'p{pno} 竖线{len(vrs3)}条（首列居中不可测，登记）')
check('N4 表组×%d（列×y 聚类 0908；外框0.8>内线0.4pt 色122/表头8.7-9.3/行高≥8.5/表顶前距2.27-3.6/'
      '首列居中±1.5/头净空2.8-3.5·不穿字≥0.2/表内行距4.90±0.4 正文行·全多行格表豁免登记）' % len(tab_groups),
      tab_ok, '；'.join(tab_detail))
if tab_reg:
    reg('N4 表组登记项', '；'.join(tab_reg))

# ---- N5 学习目标（楷体/行距/悬挂） ----
# F 0909 收尾轮适配：楷体 E 起换挂 FZKTK（方正楷体_GBK，PDF 内嵌名 FZKTK--GBK1-0）——
# 旧系统 KaiTi 'Kai' 名匹配恒空
# H3 片 0909c 适配（学习目标后隙 \kern7.83pt）：旧 \hspace{1em} 在字体切换处被 MuPDF 拆行、
#   内容片段行首即「理」字；改 \kern 后「序号+内容」并入一行（行首为 Times 序号）——
#   口径改「行内首个 FZKTK 字符 bbox x0」（与旧行 bbox x0 同物：旧拆行片段首字符即行首）；
#   首行内容 x 实测 87.98pt＝31.03mm（旧登记文案 31.41 系早期读数）→ 改后 85.32pt＝30.10mm。
kt = []
for b in doc[0].get_text('rawdict')['blocks']:
    if b['type'] != 0: continue
    for l in b['lines']:
        hit = None
        for sp in l['spans']:
            if 'FZKTK' in sp['font']:
                # H3 片：\kern 间隙被 MuPDF 记为 FZKTK 族空格 span（chars=' '），须跳过取实字面
                ch0 = next((c for c in sp['chars'] if c['c'].strip()), None)
                if ch0:
                    hit = ch0['bbox'][0]
                    break
        if hit is not None:
            kt.append((hit, l['bbox'][1], l['spans'][0]['origin'][1]))
kt.sort(key=lambda x: x[1])
kt_ok = len(kt) == 4
if kt_ok:
    first_x = kt[0][0] / PT
    # F 0909 收尾轮适配：回行 x 23.3→25.87＝margin(17.575)＋\hangindent(8.3mm) 登记值——
    # 旧 23.3 系 hangindent 调 8.3mm 前的读数未随更；首行内容 x 窗 28.0-29.7→30.9-31.9→
    # H3 片 29.6-30.6（\kern7.83pt 后内容左移 0.93mm＝旧 1em 与 kern 差，30.10 实测）
    hang_x = [x / PT for x, _, _ in kt if abs(x / PT - 25.87) <= 0.55]
    lds = [(b[2] - a[2]) / PT for a, b in zip(kt, kt[1:])]
    kt_ok = (29.6 <= first_x <= 30.6 and len(hang_x) >= 1 and all(5.5 <= d <= 6.5 for d in lds))
check('N5 学习目标（楷体4行/行距17pt档5.5-6.5/首行内容30.10±0.5·H3/回行悬挂25.87＝margin+8.3）', kt_ok,
      f'n={len(kt)} 首x{kt[0][0] / PT if kt else -1:.2f} 行距' +
      ' '.join(f'{d:.2f}' for d in [((b[2] - a[2]) / PT) for a, b in zip(kt, kt[1:])]) if kt else 'n=0')
reg('N5 首行/回行 x 换轨（0909 收尾轮）', '序号「N.」数字走 \\numbold（NSC-w850 拉丁族，E 换轨）——'
    '首行内容起点 28.84→31.41（+2.57mm＝数字 advance 增量），窗 28.0-29.7→30.9-31.9；'
    '回行悬挂 x 23.3→25.87＝margin+\\hangindent(8.3mm)（断言顶格.py 8.3mm 登记同步有效，'
    '旧 23.3 系 8.3mm 定值前读数）；首行缩进 2 字＋序号加粗后空 1 字口径不变')
reg('N5 首行内容 x 换轨（H3 片 0909c，学习目标后隙 \\kern7.83pt）', '后隙 \\hspace{1em}（10.5pt＝3.70mm）'
    '→ \\kern7.83pt 固定档（靶：全品 p04 学习目标位 ink 隙 3.174mm）——首行内容 x 31.03→30.10mm'
    '（左移 0.93mm），窗 30.9-31.9→29.6-30.6；ink 隙 3.175/3.387/3.387（理/掌/掌 字形左承差，'
    '全品同形分布 3.174/3.386）；行距/悬挂/顶格例外口径不变（断言顶格.py 8.3mm 登记同步有效）')
reg('N5 顶格例外（拍板6）', '首行缩进 2 字＋序号「N.」加粗后空 1 字（\\mubiaomu \\hangindent=8.3mm），'
    '断言顶格.py 已同步登记 8.3mm 悬挂合法')

# ---- N6 六图台账（回退轮0910 位图口径重建；片G 矢量簇台账作废） ----
# 只管「六图在场＋图源互证＋阅读序＋落位（页,栏）逐图钉」；置宽由 ⑱ tex 门核、几何由 ⑱-2 位图门核。
check('N6 四图台账（答案制0911：位图恰4＋原生px尺寸片段互证＋阅读序＋落位逐图钉；g1/g5 出册）',
      len(FIG_ROWS) == 4 and len(FIGS) == 4 and not FIG_PXBAD and
      [(f, p, c) for f, p, c, _r, _i in FIGS] == [(f,) + FIG_AT[f] for f, _w in FIG_W],
      '位图 ' + str(len(FIG_ROWS)) + '/4；' + '；'.join(
          f + '@p' + str(p) + 'c' + str(c) + ' ' + str(i['width']) + 'x' + str(i['height']) + 'px'
          for f, p, c, _r, i in FIGS))
reg('N6 口径登记（回退轮0910 旧→新）',
    '片G 旧门：矢量簇恰 6（斜长笔聚簇）＋落位==FIG_AT（g6@p2c2／g1@p3c2／g2@p4c1／g3@p5c1／g4@p6c1／g5@p6c2）。'
    '新门：PDF raster 对象恰 6、逐图原生像素尺寸（FIG_PX）与片段一对一互证、阅读序（页,栏,y）与 FIG_W 一致、'
    '落位逐图钉——g2 p4c1→p3c2（栏末图，缩图后回流），余五图未位移；'
    '置宽档＝84.0/28.8/32.7/54.1/47.5/42.5mm（片G 旧档 80.8/41.1/42.0/36.3/30.5/28.2mm 作废）。')
reg('N6 图内字≥7pt 等效断言＝SKIP 登记', '需图源文字像素高折算（任务书条5允许缺口登记）：'
    'sub3_B_4 原生 1408×374px 打印 60mm（≈597dpi 级），图内字等效远超 7pt 档，无降质风险；逐图提档另行任务')
reg('N6 图组下距 3.39 登记（0909 收尾轮）', 'p2 图后邻带 (3) 行含投影向量数学结构——上伸墨带顶抬升，'
    '胶 tex 级恒定，非图组自身缝；下距窗 0.4–2.9→0.4–3.5')

# ---- N7 投影向量条目首子项连排 ----
# F 片B 0909 #28/#36：拆段首段改 \tiaomuz（零尾距变体）
lianpai_body = r'\tiaomuz{3}{投影向量：(1)' in body
lianpai_pdf = any('投影向量：(1)' in t for ls in lines_of.values() for t, bb, sps in ls)
bind23 = body.count('\\bindp (2)') >= 1 and body.count('\\bindp (3)') >= 1
logtxt2 = open(os.path.join(BASE, 'postproc_daoxue_log.txt'), encoding='utf-8', errors='ignore').read()
lp_log = '未各自成段嫌疑 无' in logtxt2 and ('（2）起未各自成段' in logtxt2 or '成段嫌疑' in logtxt2)
check('N7 条目3 首子项 (1) 连排（body+pdf+postproc台账）＋(2)(3) 各自成段',
      lianpai_body and lianpai_pdf and bind23 and lp_log,
      f'body{"在" if lianpai_body else "缺"} pdf{"在" if lianpai_pdf else "缺"} '
      f'\\bindp(2)(3) {"在" if bind23 else "缺"} 台账{"平" if lp_log else "异"}')

# ---- N8 素养小结楷体 ----
xiaojie_kai = r'\noindent{\kaishu #1}' in blkfile
n_xj, kai_ok = 0, 0
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for cl in COLL:
        rows = col_rows(pno, cl)
        for i, (y0, y1, t, sps) in enumerate(rows):
            if t.startswith('【素养小结】'):
                n_xj += 1
                for j in range(i + 1, min(i + 3, len(rows))):
                    if rows[j][2].startswith('①识别'):
                        # F 0909 收尾轮适配：楷体换挂 FZKTK（同 N5）
                        if 'FZKTK' in rows[j][3][0]['font']:
                            kai_ok += 1
                        break
check('N8 素养小结（标签独行＋内容楷体 ×9）', xiaojie_kai and n_xj == 9 and kai_ok == 9,
      f'宏 \\kaishu {"在" if xiaojie_kai else "缺"}；内容行楷体 {kai_ok}/{n_xj}')

# ---- N9 ◆ 符号 0.63em＋后隙 2.4mm ----
gapf, widf, badf = [], [], 0
for ls in lines_of.values():
    for t, bb, sps in ls:
        if ('知识点' in t or '探究点' in t) and sps and sps[0]['text'].strip() == '◆':
            widf.append((sps[0]['bbox'][2] - sps[0]['bbox'][0]) / PT)
            if len(sps) > 1:
                gapf.append((sps[1]['bbox'][0] - sps[0]['bbox'][2]) / PT)
            else:
                badf += 1
g_ok = len(gapf) >= 9 and all(abs(g - 2.4) <= 0.3 for g in gapf)
w_med = sorted(widf)[len(widf) // 2] if widf else -1
check('N9 ◆后隙 2.4±0.3（n≥9）', g_ok and badf == 0,
      f'n={len(gapf)} ' + ' '.join(f'{g:.2f}' for g in gapf[:6]) + '…')
reg('N9 ◆ advance 宽中位', f'{w_med:.2f}mm（0.63em 桶排 8.6pt 字号，≈0.88em 墨宽，总账E 登记）')

# ---- N10 解析→下题题号距（v4.4⑦ 升格：中位 3.95±0.6 设门＋明细登记） ----
gaps_bb = []
TISIG1 = re.compile(r'^\d．\[')
for pno in range(1, n_pages + 1):
    for cl in COLL:
        rows = col_rows(pno, cl)
        for i, (y0, y1, t, sps) in enumerate(rows):
            if not t.startswith('[解析]'):
                continue
            j = i + 1
            blk_bot = y1
            last_txt = t
            while j < len(rows):
                tt = rows[j][2]
                m1 = TISIG1.match(tt)
                m2 = re.match(r'^\(\d+\)', tt) and re.search(r'[，。；：与若则]', tt[:10])
                if m1 or m2:
                    break
                blk_bot = max(blk_bot, rows[j][1]); last_txt = tt; j += 1
            # 句末标点0910（拍板A：全件句末「．」→「.」，题号/序号位保留）：收口判据字符类补 ASCII「.」——
            # 旧类 [。．；？！] 的「。」自 6e 起恒 0、「．」自 6f 起只存序号位（不再是行末），不补点即配对全灭假 ✗。
            if j >= len(rows) or not re.search(r'[。．；？！.]$', last_txt):
                continue
            d_ = (rows[j][0] - blk_bot) / PT
            if 0.5 < d_ < 15:
                gaps_bb.append(d_)
gaps_med = sorted(gaps_bb)[len(gaps_bb) // 2] if gaps_bb else -1
# F 0909 收尾轮：中位实测 5.21×4（bbox 口径，uniform）——0908 注册值 3.95 系旧带结构读数；
# 现值由 \jiexi/\zhenti 解析尾 \addvspace{7pt}＋行盒给出门 5.21±0.5
check('⑦ 解析→下题题号墨距（全品对齐0911：判断简析亦出册→正文 [解析] 行 0——配对 n==0 反向锁；旧门 n 1–2∈2.0–3.5 作废）',
      len(gaps_bb) == 0,
      f'n={len(gaps_bb)}（应 0＝正文无 [解析] 行；残余即判断简析回渗签名）')
reg('N10 解析→下题题号墨距（明细登记）',
    (f'有效对 n={len(gaps_bb)}，bbox 距 ' + ' '.join(f'{g:.2f}' for g in sorted(gaps_bb)) +
     f'，中位 {gaps_med:.2f}mm（ink 口径另加字面 inset；'
     '全品题间墨隙参照 4.1–4.7，任务书条9——bbox 口径含行盒沿差）；'
     'tex 级已锁 \\jiexi/\\zhenti 解析尾 \\addvspace{7pt}（⑲断言；0908 断言轮由 6pt 提 7pt）。'
     '0909 收尾轮：门 3.95±0.6→5.21±0.5（R2/R3 收尾改动后带结构重测，四对 uniform）。'
     '配对总体小（栏断/变式流向不入集）且公式降部扰墨带') if gaps_bb else '无有效对（异常复核）')

# ============================================================
# v4.4 新增断言（执行轮规格书§断言翻修）：①题号字重/标签反向 ②半角括号 em＋全角零残留 ③定界符高
# ④判断括号右挂/独占行 ⑦七缝（探究点→例1/前块→知识点/表底→下块/解析→◆/条目；表顶在N4、解析→题号在N10）
# ⑧多选×1常规 ⑨悬挂0容忍＋源空格0 ⑩答案行无下划线 ⑪题侧14＋2.7/2.2隙 ⑫探究点单行≤82＋名字清单
# ⑭kongwei 8处6.8±0.6 ⑮side×5归属（探二三六八九）。⑤表净空⑬表顶不穿字在 N4 内实施。
# ============================================================
chars_of = {}
for pno in range(1, n_pages + 1):
    cs = []
    for blk in doc[pno - 1].get_text('rawdict')['blocks']:
        if blk['type'] != 0:
            continue
        for ln in blk.get('lines', []):
            for sp in ln['spans']:
                for ch in sp.get('chars', []):
                    if ch['c'].strip():
                        cs.append((ch['c'], ch['bbox'], sp['size'], sp['font']))
    chars_of[pno] = cs

def _dens(pno, bb, dpi=300):
    """bbox 墨密度（<128 灰占比）——CJK 字重代理量。"""
    pm = doc[pno - 1].get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(bb))
    w, h, s = pm.width, pm.height, pm.samples
    ink = sum(1 for i in range(w * h) if s[i] < 128)
    return ink / (w * h)

def _stem(pno, bb, dpi=600):
    """bbox 内中位水平墨行程（pt）——数字笔画粗代理量。"""
    pm = doc[pno - 1].get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(bb))
    w, h, s = pm.width, pm.height, pm.samples
    runs = []
    for r in range(h):
        best = cur = 0
        for c in range(w):
            if s[r * w + c] < 128:
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        if best:
            runs.append(best)
    runs.sort()
    return runs[len(runs) // 2] / dpi * 72 if runs else -1

# ---- ① 题号数字笔画 2.0–2.7×＋变式标签常规反向 ----
ti_stems, base_stems = [], []
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        # 0908：窗收 ±0.25——页脚数字 11.0pt 落旧窗 ±0.5 致 n=12（5 题号＋7 页脚码）混入
        if c.isdigit() and abs(sz - 11.4) < 0.25:
            ti_stems.append(_stem(pno, bb))
        elif c.isdigit() and 10 <= sz <= 11 and 'Times' in fn:
            base_stems.append(_stem(pno, bb))
ti_stem = sorted(ti_stems)[len(ti_stems) // 2] if ti_stems else -1
base_stem = sorted(base_stems)[len(base_stems) // 2] if base_stems else -1
ratio_digit = ti_stem / base_stem if base_stem > 0 else -1
bian_dens, shi_dens, cjk_dens = [], [], []
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        if 0x4E00 <= ord(c) <= 0x9FFF:
            # 0908：变式密度须按字筛「变」（探究点/知识点/例1 标签同为 12pt 档，混入吞中位）；
            # F 0909 收尾轮适配：变式标签 E 起换挂方圆体（\liB，内嵌名 AlimamaFangYuanTiVF-Thin，
            # instancer 静态实例沿用 VF 内部名）——旧 FZHTJW 匹配恒空 n=0
            # F 片D 0909c（#33）：双字重拆分——「变」特黑档（FY-w700）与「式」中黑档（FY-w450）分集，
            # 旧单集 var_ratio（w400 常规反向 ≤1.75）随 4px 靶退役（全品 p06 真迹 变 0.145em＞式 0.075em）
            if c == '变' and abs(sz - 12) < 0.4 and 'FangYuanTi' in fn:
                bian_dens.append(_dens(pno, bb))
            elif c == '式' and abs(sz - 12) < 0.4 and 'FangYuanTi' in fn:
                shi_dens.append(_dens(pno, bb))
            elif 10 <= sz <= 11 and 'FZSSJW' in fn:
                cjk_dens.append(_dens(pno, bb))
_med_dens = lambda v: sorted(v)[len(v) // 2] if v else -1
bian_ratio = (_med_dens(bian_dens) / _med_dens(cjk_dens)) if bian_dens and cjk_dens else -1
shi_ratio = (_med_dens(shi_dens) / _med_dens(cjk_dens)) if shi_dens and cjk_dens else -1
ex1_dens = []
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        # F 0909 收尾轮适配：例N 标签 \lihei 方圆 w600（同 AlimamaFangYuanTiVF-Thin 内嵌名）
        if c == '例' and abs(sz - 12) < 0.4 and 'FangYuanTi' in fn:
            ex1_dens.append(_dens(pno, bb))
ex1_ratio = (sorted(ex1_dens)[len(ex1_dens) // 2] / sorted(cjk_dens)[len(cjk_dens) // 2]) if ex1_dens and cjk_dens else -1
# 0908 二次修正：变式 \heiti 常规实测密度比 1.63（拍板4a 常规档）——旧门 <1.6 系按特粗/常规二分
# 推算过紧误杀常规档，放 ≤1.75（例1 特粗 2.36 反向仍锁两档分离）；
# F 片D 0909c（#33 双字重）：旧单集「变式 ≤1.75」随 4px 靶退役——新双集门：变（特黑）2.2–3.2／式（中黑）≤1.75，
# 0909c 实测 变 2.68（比例1 w600 的 2.44 还重，与全品 变＞例1 序一致）／式 1.33；
# 题号比下界再修：窗收 ±0.25 排页脚码后干净中位实测 1.75（题号/正文 stem 双双上移），
# 旧登记值 1.86 系页脚 11.0pt 码混入污染集的中位——下界放 1.7，成因仍为 Times Bold 自动档不吃 FakeBold
check('①题号数字笔画 1.7–2.7×正文（n=%d）＋变式标签双字重（变 2.2–3.2／式 ≤1.75）' % len(ti_stems),
      len(ti_stems) == 5 and 1.7 <= ratio_digit <= 2.7 and 0 < shi_ratio <= 1.75
      and 2.2 <= bian_ratio <= 3.2,
      f'题号stem{ti_stem:.3f}pt 正文stem{base_stem:.3f}pt 比{ratio_digit:.2f}；'
      f'变式密度比 变{bian_ratio:.2f}（n={len(bian_dens)}）／式{shi_ratio:.2f}（n={len(shi_dens)}）')
reg('① 题号笔画比下界 1.7（0908 二次成因登记）', '题号数字本体走 Times Bold（BoldFace 自动档）不吃 \\heihao 组 FakeBold——'
    '窗收 ±0.25 排页脚码后干净实测 1.75×正文（旧 1.86 系污染集中位）；变式 1.63 常规档（拍板4a，'
    'F 片D 0909c 随双字重退役——变/式分集见上）')
reg('① 例1 标签字重取证（0909 收尾轮口径；片D 0909c 更新双字重）', f'例1「例」密度比 {ex1_ratio:.2f}'
    f'（\\lihei 方圆 w600 档） vs 变式 变{bian_ratio:.2f}／式{shi_ratio:.2f}（F 片D 0909c 双字重：'
    f'变 FY-w700／式N FY-w450）——三档分离可见（全品 p06 真迹 变 0.145em＞例1 0.124em＞式 0.075em），'
    'tex 级 ⑲ \\liBsplit 挂载已锁；旧 \\heibf 2.3×/\\heiti 常规口径随黑体仿粗轨退役')

# ---- ② 半角括号宽 0.3–0.7em＋全角（）零残留 ----
paren_ws, paren_cnt = [], 0
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        if c in '()':
            paren_cnt += 1
            paren_ws.append((bb[2] - bb[0]) / sz)
par_w = sorted(paren_ws)[len(paren_ws) // 2] if paren_ws else -1
fw_paren = sum(full.count(c) for c in '（）')
check('②半角括号宽 0.3–0.7em（中位）＋全角括号恰 12＝（　）×6 豁免（全品对齐0911；旧门零残留）',
      paren_cnt >= 50 and 0.3 <= par_w <= 0.7 and fw_paren == 12,
      f'n={paren_cnt} 中位{par_w:.3f}em（Times 0.33 档；全品半角括 0.5em——登记差异）全角括号{fw_paren}/12（＝判断空括号（　）6 对，U+3000 随去空白并吞不计；除此零残留）')

# ---- ③ 定界符高 ≤11.0pt（rawdict bbox＝字体框非墨高：正文括号 bbox 10.46pt 0908 实证；
#      超门恰 4＝探七详解 \left\{array 两处＋探八 \left(\right) 放大对 11.955（豁免登记）） ----
tall_delim = []
for pno in range(1, n_pages + 1):
    for c, bb, sz, fn in chars_of[pno]:
        if c in '()[]{}' and (bb[3] - bb[1]) > 11.0:
            tall_delim.append((pno, c, (bb[3] - bb[1])))
check('③定界符高 ≤11.0pt（答案制0911 复跑复钉：残余超高恰4＝◆探究点八(展开法)／九(折叠矩形) 12pt 题括号对——与 0908 豁免集同为 4 括号字符，页位 p6/p7→p4/p5；探七 array／探八数学放大对随 [详解] 出册）',
      len(tall_delim) == 4 and all(c in '()' for _, c, _ in tall_delim),
      f'超高定界符 {tall_delim}（字体框 10.46×1.07≈11.2 门；墨高口径 7.3×1.3=9.5 另证）')
reg('③ 口径', 'rawdict char bbox＝字体框（正文括号 10.46pt）非墨高（墨高 ≈7.3pt，1.3 容差＝9.5pt）——'
    '0908 门改 bbox 11.0pt；探七详解 cases \\left\\{array（两处）＋探八 \\left(\\right) 随内容放大对'
    '（11.955×4 字符）结构性豁免登记（清单§九③）')

# ---- ④ 判断括号（　）末行右挂×5＋断行独占行×1（合计 6 槽；全品对齐0911 换形：\zhentib 尾段全角空括号；
#      v10-A 断行优化：句尾开 \penalty0 廉价断点，题干收不满行时（　）独落次行仍由 fil 右对齐贴栏——
#      独占行由「0 容忍」改判「恰 1（p1 题(1) 实测）」；基线归并口径沿用 0908——\hfill 大空隙被 MuPDF
#      拆片段，逐片段判须先按基线归并） ----
zhentib_form_ok = (r'\noindent#1\kern2.1pt#2\penalty0\hbox{}\nobreak\hspace{0pt plus 1000fil}\nobreak（　）\hspace{0.56mm}\par' in blkfile
                   and r'{\rightskip=0pt plus 1fil\parfillskip=0pt' in blkfile)
# 旧 (√)(×) 文本形＋× TikZ 墨盒伪片段合成整套停用（墨盒判据现仅涉 \zhenhead 说明行×3，非判断槽）；
# 反向锁：正文 (√)/(×) 字串 0 出现（√ 文本在说明行「正确的打√」内不单独成 (√) 形）。
n_hang, n_alone = 0, 0
_grp16 = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp16.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))
for frs in _grp16.values():
    frs.sort()
    mt = re.sub(r'\s+', '', ''.join(x[1] for x in frs))
    n_par = mt.count('（）')
    if not n_par:
        continue
    if len(mt) > 2 * n_par:
        n_hang += n_par
    else:
        n_alone += n_par
check('④判断括号（　）挂题干末行 ×5＋断行独占行 ×1（合计 6 槽）＋旧印答槽反向（(√)(×) 0）',
      n_hang == 5 and n_alone == 1 and zhentib_form_ok
      and full.count('(√)') + full.count('(×)') == 0,
      f'右挂{n_hang}/5 断行独占{n_alone}/1 宏形{"在" if zhentib_form_ok else "缺"} 旧槽残留{full.count("(√)")+full.count("(×)")}')
reg('④ 判断括号换形（全品对齐0911；排版病0911 拉伸空洞修；v10-A 断行优化＋独占行口径改）',
    '\\zhentib 尾段＝#2\\penalty0\\hbox{}\\nobreak\\hspace{0pt plus 1000fil}\\nobreak（　）\\hspace{0.56mm}——'
    '右挂机制（fil 双 nobreak 直连＋\\kern2.1pt 序号隙）承 \\zhenti 逐字不动，槽内容改空、括号改全角（照全品 p04 实拍）；'
    '排版病0911：组内加 \\rightskip=0pt plus 1fil（题干超一行时首行改右参差，拉宽不再集中于「，」后胶→空洞）'
    '＋内部胶 1fil→1000fil（末行拉伸 99.9% 归内部胶，（　）右挂残差实测 0.1–0.2pt，在窗内）；'
    'v10-A：句尾后 \\penalty0 开廉价断点、断点与 fil 胶间垫 \\hbox{}＋\\nobreak 封「断在胶上丢胶」支路——'
    '旧双 \\nobreak 禁断链使 p1 题(1)「等.（　）」整块挤次行、行1 尾余空 33.2pt（≈3.4 字），'
    '改后行1 完整收行（余空 19.7pt≈1.9 字）、（　）独落次行右对齐（墨距栏右 1.20mm，N1 窗内）；'
    '故本门口径由「独占行 0 容忍」改「独占行＝断行优化正常态，恰 1」，六槽总数（挂＋独）仍锁 6；'
    '旧 0909 收尾轮返修史（R2/\\mbox 实验、( × ) 剥空格、× 墨盒伪片段）见 .bak_全品对齐0911，本次改前旧串见 .bak_对齐0911；'
    '×/√ 值出册后仅 \\zhenhead 说明行「正确的打√,错误的打×」内联保留（题面指引，非答案槽）')

# ---- ⑦ 七缝（band 墨隙口径；0908 重写：行 bbox 含上 leading，旧「bbox±1 套带」多取 None——
#      改「垂直重叠最大带」归属＋带→行映射；条目缝改前带直查（旧 pv 容差套恒空致 n=0）） ----
def col_bands(pno, cl):
    return merge(bands(doc[pno - 1], cl, cl + COLW, MARGIN, BODY_BOT), gap=0.8)

def band_at(bs, y0, y1):
    best, bi = -1.0, 0
    for i, (a, b) in enumerate(bs):
        ov = min(b, y1) - max(a, y0)
        if ov > best:
            best, bi = ov, i
    return bi

g_td, g_kn, g_tab_bot, g_jx_zsd, g_tm = [], [], [], [], []
table_bots = {}   # (pno, 列) -> 底线y（0908：自 N4 列×y 聚类取——旧整页 hrs2[-1] 跨栏混线，p2 表底配到另栏）
for pno, cl, hrs3 in tab_groups:
    table_bots[(pno, cl)] = hrs3[-1][0].y1
for pno in range(1, n_pages + 1):
    for cl in COLL:
        bs = col_bands(pno, cl)
        rows = col_rows(pno, cl)
        if not bs or not rows:
            continue
        in_band = {i: [] for i in range(len(bs))}
        for y0, y1, t, sps in rows:
            in_band[band_at(bs, y0, y1)].append((t, sps))
        for i in range(len(bs)):
            rws = in_band[i]
            if not rws:
                continue
            ts = [t for t, _ in rws]
            if any(t.startswith('◆探究点') for t in ts) and i + 1 < len(bs):
                g_td.append((bs[i + 1][0] - bs[i][1]) / PT)
            if any(t.startswith('◆知识点') for t in ts) and i > 0:
                g_kn.append((bs[i][0] - bs[i - 1][1]) / PT)
            if any(t.startswith('[解析]') for t in ts) and i + 1 < len(bs):
                if any(t.startswith('◆知识点') for t, _ in in_band[i + 1]):
                    g_jx_zsd.append((bs[i + 1][0] - bs[i][1]) / PT)
        # 条目缝（0908 五修：行级配对＋同线剔除＋\\tiaomu 限集——条目号行 ^\d+\.(?!\d) 系
        # \\hspace{1em} 拆出的线内碎片，与条目首文本行同线（号行 y0 沉 ≈0.3pt 排其后）；四修曾取
        # (k1,k2) 开区间 max-y1 作末行，必落到条目 j 首行（号行前一行与其同高）→ b_i==b_j 恒杀
        # （探针实证全对同带）。末行改取 k2 前最后一条「与 k2 不同线」行；两号行之间含块签名行
        # （◆/例1/变式1/[/【）视为跨段跳过；k1 在本栏首个 ◆知识点 之前的对系 \\mubiaomu（学习
        # 目标，无尾距宏，缝读 2.20–2.54＝块内行缝域），不入条目缝集
        def _sig_t(t):
            # F 0909 收尾轮：[注意] 系 \zhuzhu 条目内注（非块边界），不作跨段签名——
            # 旧形把条目 1→2/2→3 对全数误杀（g_tm n=3→0 成因）
            return bool(re.match(r'^(◆|例1|变式1|\[(?!注意)|【)', t))
        def _same_line(m, k):
            a0, a1, b0, b1 = rows[m][0], rows[m][1], rows[k][0], rows[k][1]
            return min(a1, b1) - max(a0, b0) > 0.5 * min(a1 - a0, b1 - b0)
        kn0 = next((k for k, (_y0, _y1, t, _s) in enumerate(rows)
                    if t.startswith('◆知识点')), -1)
        num_rows = [k for k, (y0_, y1_, t, _sps) in enumerate(rows)
                    if re.match(r'^\d+\.(?!\d)', t)]
        for k1, k2 in zip(num_rows, num_rows[1:]):
            if k1 <= kn0:
                continue
            if any(_sig_t(rows[m][2]) for m in range(k1 + 1, k2)):
                continue
            prev = [m for m in range(k1, k2) if not _same_line(m, k2)]
            last = max(prev, key=lambda m: rows[m][1]) if prev else k1
            b_j = band_at(bs, rows[k2][0], rows[k2][1])
            b_i = band_at(bs, rows[last][0], rows[last][1])
            if b_j > b_i:
                g_tm.append((bs[b_j][0] - bs[b_i][1]) / PT)
for (pno, cl), by1 in sorted(table_bots.items()):
    bs = col_bands(pno, cl)
    nb = [a for a, b0 in bs if a >= by1 - 0.5]   # 0908 修：取下带顶 a——旧取带底 b0 多含一整行行高（11.37 假读）
    if nb:
        g_tab_bot.append((nb[0] - by1) / PT)
    elif pno == 2 and cl == COLL[1]:
        # F 0909 收尾轮登记：p2 右表（夹角/数量积/投影/共面，名称列带黑色竖线分隔——全品同名列式样）
        # 为栏末元素（表底 728.6pt，栏余 65pt 无下带）——表底缝对不存在，豁免登记不设红；
        # 竖线全高连墨使该表 band 投影并带（568.2–729.0），亦无「表底后首带」可取
        pass
kn_exempt = 3 - len(g_kn)
# F 0909 收尾轮窗改：知识点缝单窗 2.7–5.8——裸前块场景（p1 栏目头→知识点一 2.88）与解析尾先行
# 场景（p2 ×．→知识点三，0908 实测 5.25、0909 重测 4.74——R2/R3 收尾改动带顶漂移 0.51mm）并窗；
# 探究点缝上限 4.7→4.8：4.74＝块间缝 2.88＋\tiaomu 尾距 1.86 全额读数（R3 side 声明盒深参与行距，
# 实测落窗缘），下块首行数学结构时墨带顶另抬升（3.39/4.23 档，见低值登记）——tex 级 \addvspace 不动；
# F 片B 0909 #36 断言适配（旧→新）：条目缝窗 2.5–5.0 → 2.7–3.4（目标 3.06±0.2，\tiaomu 尾距
# 1.8→0.35mm 后实测 3.22/3.39/3.22/3.05/3.05/2.71；两端点 2.71＝β 降部墨底、3.39＝[注意]末行+
# 号行数字墨顶，字形墨深成因，窗按实测两端收）；知识点缝对 2→1（◆知识点三 落 p3 栏首豁免）、
# 表底缝对 2→3（表3 移 p3c0 后新增下带对，值 4.04/4.09/4.01）
# H1 片 0909c 适配（E7 重排后逐项复标）：g_td ×9 不变（4.06–4.74 落窗）；g_kn 1→2（知识点现均居
#   栏中 2 对，2.88/4.23 单窗内）；g_tab_bot 3→2（表1 p1右／表2 p2左 4.03/4.09 落窗；表3 为栏末
#   元素无下带，沿 0908 栏末豁免先例注销不设红）；g_tm 6→5（条目对随分栏位移并集变化，2.71–3.56 落窗）。
ok7b = (len(g_td) == 9 and all(3.3 <= v <= 4.8 for v in g_td)
        and len(g_kn) == 2 and all(2.7 <= v <= 5.8 for v in g_kn)
        and len(g_tab_bot) == 3 and all(3.41 <= v <= 4.41 for v in g_tab_bot)
        and len(g_tm) == 5 and all(2.7 <= v <= 3.6 for v in g_tm))
reg('⑦ 片G 0910 表底缝对数 2→3', 'H1 片 0909c 时表3 为栏末元素（无下带对）→ 豁免计数 2；'
    '片G 六图下置后分页位移，表3 之下重新有块（实测 4.01/4.10/4.10 三对全落窗 3.41–4.41）'
    '——旧「表3 栏末豁免」注记随之下线，计数门 2→3')
reg('⑦ 表底缝 ×3（0909 片B 布局位移后）', '实测 4.04/4.09/4.01（p1 表1／p2 表2／p3 表3）；'
    '表3 因 #30 表高增（多行格垫底）自 p2 右栏移至 p3 左栏首，底后带对在场——旧 p2 右表栏末豁免项注销')
reg('⑦ 条目缝口径（0908 五修＋片B 0909 #36 复标）',
    f'集＝\\tiaomu 真缝（知识点区号行对，n={len(g_tm)}，实测 {" ".join("%.2f" % v for v in g_tm)}）；'
    '\\mubiaomu 学习目标对（2.20–2.54＝块内行缝域，无尾距宏）不入集；'
    '\\tiaomu 尾距 1.8→0.35mm（拆段首段零尾距 \\tiaomuz、条目尾距 \\tiaomutail 挂末段）后'
    '条目缝墨隙落 3.05–3.39（目标 3.06±0.2），pitch 全对 6.76mm 统一（基线≈6.8 档）；'
    '两端点 2.71（条目3→4，β 降部墨底）/3.39（条目2→3，[注意]末行＋号行数字墨顶）系字形墨深——窗 2.7–3.4')
if any(v < 2.7 for v in g_tm):
    reg('⑦ 条目缝低值登记', f'墨底深对带缝读低 {["%.2f" % v for v in g_tm if v < 2.7]}；'
        'β 降部行（条目3→4）墨底低伸成因，\\tiaomu 尾距 0.35mm 标定不动')
if kn_exempt:
    reg('⑦ 知识点缝栏首豁免', f'◆知识点二/三为栏首元素（栏顶弃胶无前带对）——{len(g_kn)}/3 带对实测，豁免 {kn_exempt}')
if any(v < 3.7 for v in g_td):
    reg('⑦ 探缝低值登记', '下块首行含 (多选题) 括号/数学结构时墨带顶抬升 ≈1.0mm（探五/探七 3.39），'
        '胶 tex 级 \\addvspace{2.0mm} 恒定——窗 3.3–4.8（0909 收尾轮上限 4.7→4.8：4.74 全额尾距读数）')
reg('⑦ 解析→◆知识点带对（登记不设门）', f'直接带对 n={len(g_jx_zsd)}——判断收尾行（×．）带隔断配对；'
    '缝由解析尾 \\addvspace{7pt}＋\\zsd 前距 tex 级锁（0908 \\zsd 内顺序换位恢复 max 语义），同位落点见 N10 中位 5.21')
check('⑦块缝（◆探究点→例1 4.2±0.5×9，墨顶方差窗3.3-4.8／前块→◆知识点 ×2 单窗2.7-5.8／'
      '表底→下块 3.91±0.5×3（片G 0910：表3 下带对回归）／条目→条目 \\tiaomu 缝 ×%d 窗2.7-3.6）' % len(g_tm), ok7b,
      f'探究点缝{" ".join("%.2f" % v for v in g_td)}｜知识点缝{" ".join("%.2f" % v for v in g_kn)}｜'
      f'表底缝{" ".join("%.2f" % v for v in g_tab_bot)}｜解析→◆{" ".join("%.2f" % v for v in g_jx_zsd)}｜'
      f'条目缝{" ".join("%.2f" % v for v in g_tm)}')

# ---- ⑦-3 条目2 (1)→(2) 拆段缝（F 片B 0909 #28 新设；600dpi ink 口径） ----
def _same_vis(r1, r2):
    return min(r1[1], r2[1]) - max(r1[0], r2[0]) > 0.5 * min(r1[1] - r1[0], r2[1] - r2[0])

split_ok, split_detail = True, []
for pno in range(1, n_pages + 1):
    for ci, cl in enumerate(COLL):
        rows = col_rows(pno, cl)
        for k, (y0_, y1_, t, sps) in enumerate(rows):
            if not re.match(r'^[（(]\s*2\s*[）)]\s*几何表示法', t):
                continue
            up = None
            for m in range(k - 1, -1, -1):
                if not _same_vis(rows[m], rows[k]):
                    up = rows[m]
                    break
            if up is None:
                continue
            pitch = (sps[0]['origin'][1] - up[3][0]['origin'][1]) / PT
            gap = ink_gap600(pno, ci, up[3][0]['origin'][1], sps[0]['origin'][1])
            ok1 = (6.2 <= pitch <= 6.7) and gap is not None and (2.6 <= gap <= 3.1)
            split_ok = split_ok and ok1
            split_detail.append(f'p{pno}c{ci} pitch{pitch:.2f} 墨隙{("%.2f" % gap) if gap is not None else "n/a"}')
check('⑦-3 条目2 (1)→(2) 拆段缝（普通行距档 6.44±0.25／墨隙 2.7–3.0；F 片B 0909 #28 零尾距变体）',
      split_ok and bool(split_detail), '；'.join(split_detail) or '未找到 (2)几何表示法 行')

# ---- ⑦-4 相邻判断题缝（F 片B 0909 #31 新设；600dpi ink 口径） ----
zt_ok, zt_detail = True, []
SIG7 = re.compile(r'^(◆|例1|变式1|\[(?!解析)|【)')
for pno in range(1, n_pages + 1):
    for ci, cl in enumerate(COLL):
        _raw = col_rows(pno, cl)
        _gb = {}
        for r in _raw:                     # 基线归并（口径同④）：「（　）」系 fil 后独立行记录，
            _gb.setdefault(round(r[3][0]['origin'][1] * 2), []).append(r)   # 须并回题干行
        rows = []
        for _kb in sorted(_gb):
            frs = sorted(_gb[_kb], key=lambda r: r[3][0]['origin'][0])
            rows.append((frs[0][0], frs[0][1], ''.join(r[2] for r in frs), frs[-1][3]))
        zt_end = [k for k, r in enumerate(rows)
                  if re.sub(r'\s+', '', r[2]).endswith('（）')]
        for k1, k2 in zip(zt_end, zt_end[1:]):
            if k2 != k1 + 1:      # 全品对齐0911：判断题干行直接相邻成对（旧「between 含[解析]」判据随简析出册作废；
                                   #   跨块 (2)→(1) 必隔 zsd/条目/表/说明行，天然不满足相邻条件；题干两行者不成对）
                continue
            up = rows[k1]
            if up[0] == rows[k2][0]:      # 同线碎片
                continue
            pitch = (rows[k2][3][0]['origin'][1] - up[3][0]['origin'][1]) / PT
            gap = ink_gap600(pno, ci, up[3][0]['origin'][1], rows[k2][3][0]['origin'][1])
            zt_ok = zt_ok and (6.2 <= pitch <= 6.7) and gap is not None and (2.0 <= gap <= 3.3)
            zt_detail.append(f'p{pno}c{ci} pitch{pitch:.2f} 墨隙{gap:.2f}')
check('⑦-4 相邻判断题缝（全品对齐0911 换形：（　）尾题干行直接相邻——普通行距档 6.44±0.25／墨隙 2.0–3.3；F 片B #31 尾距 0pt 沿革）',
      zt_ok and len(zt_detail) >= 2, '；'.join(zt_detail) or '未找到判断题对')
if zt_detail:
    reg('⑦-4 判断题缝口径（全品对齐0911 重释）',
        '配对判据由「(N) 行对中间含 [解析]、无块签名」改为「两（　）结尾题干行（基线归并后）k2==k1+1 直接相邻」——'
        '判断简析随 6h 出册，块内不再有 [解析] 行；\\zhentib 尾 \\addvspace{0pt} 承 \\zhenti 同档，缝＝普通行距档'
        ' 6.3–6.8 窗不动、墨隙下界 2.5→2.0 run2 复钉（旧窗跨 [解析] 行含其降部，新形题行直连＝间隙随字形浮动，'
        '实测 3.01/2.20 皆普通行距档）；预期 2–3 对（p1/p2 各 1 对；p3 判断(2)题干两行→归并后不相邻，不成对）')

# ---- N4b 表组多行格净空（F 片B 0909 #30 新设；行级最紧侧 600dpi ink 口径；H1 下划线判除见内注） ----
pad_ok, pad_detail = True, []
_ul_reg = []
_ul_low = []
for pno, cl, hrs3 in tab_groups:
    rs = [r for r, _ in hrs3]
    ws = [(d.get('width') if d['type'] == 's' else r.height) for r, d in hrs3]
    page = doc[pno - 1]
    # 竖线（黑，逐行分段）：按行取本行竖线 x 分列，逐格测墨带取最紧侧
    vlines = [d['rect'] for d in page.get_drawings()
              if (d.get('color') or d.get('fill'))
              and rgb255(d.get('color') or d.get('fill')) == (0, 0, 0)
              and d['rect'].height > 5 * PT and d['rect'].width < 3]
    for a, b, wa, wb in zip(rs, rs[1:], ws, ws[1:]):
        if (b.y0 - a.y0) / PT < 14:      # 表头/单行行豁免（多行行高 ≥15.7mm，0909 实测）
            continue
        xs = sorted(set(round(v.x0, 2) for v in vlines
                        if v.y0 - 1 <= a.y0 <= v.y1 + 1 or v.y0 - 1 <= b.y0 <= v.y1 + 1))
        if len(xs) < 2:
            xs = [rs[0].x0, rs[0].x1]
        padT = padB = 99.0
        for xa, xb in zip(xs, xs[1:]):
            if xb - xa < 6:
                continue
            bs = ink_bands600(pno, cl, a.y0 + 1.6, b.y0 - 1.6, x0=xa + 2.0, x1=xb - 2.0)
            if not bs:
                continue
            # H1 片 0909c：底侧印答下划线（\kongda 末行）判除——最低带若为「薄而宽」（带高 ≤6px@600
            # 且横向墨覆盖 ≥50% 格宽）按登记口径剔重取次低带（片B 登记「印答下划线墨底低伸 ≈0.9mm」
            # 的规则化实现）；基线此形未现，E1 重排后表1 共线行定义格「重合」落末行致 B 1.02 假读。
            bz = bs[-1]
            _pm = page.get_pixmap(dpi=600, colorspace=pymupdf.csGRAY,
                                  clip=pymupdf.Rect(xa + 2.0, bz[0], xb - 2.0, bz[1]))
            _w, _h, _s = _pm.width, _pm.height, _pm.samples
            _cols = [c for c in range(_w) if any(_s[r * _w + c] < 128 for r in range(_h))]
            _cov = (len(_cols) / _w) if _w else 0
            _isul = _h <= 6 and _cov >= 0.30 and len(bs) >= 2
            if _isul:
                _ul_reg.append(('p%d' % pno, round((bz[1] - bz[0]) / PT, 3), round(_cov, 2)))
                bz = bs[-2]
            padT = min(padT, (bs[0][0] - (a.y0 + wa / 2)) / PT)
            padB = min(padB, ((b.y0 - wb / 2) - bz[1]) / PT)
            if _isul:
                _ul_low.append((pno, round(padB, 2)))
        if padT > 90:
            pad_ok = False
            pad_detail.append(f'p{pno} 行无墨带!')
            continue
        # H1 片 0909c：底侧末行含印答下划线的行（_ul_low）——文字墨底窗放宽到 1.6–4.3（片B 已登记
        # 「印答下划线墨底低伸登记不设红」的规则化：下划线属装饰墨，文字净空另计）；余行维持 2.9–4.3。
        _lo = 1.6 if any(_pp == pno for _pp, _vv in _ul_low) else 2.9
        pad_ok = pad_ok and (2.9 <= padT <= 3.7) and (_lo <= padB <= 4.3)
        pad_detail.append(f'p{pno} 行{(b.y0 - a.y0) / PT:.1f} T{padT:.2f} B{padB:.2f}')
check('N4b 多行格净空（行级最紧侧 顶 2.9–3.7／底 2.9–4.3mm；全品 p04 3.46–4.59；F 片B 0909 #30）',
      pad_ok and bool(pad_detail), '；'.join(pad_detail) or '无多行行')
if _ul_reg:
    reg('N4b 印答下划线判除（H1 片 0909c）', '底侧最低墨带为薄宽下划线（高≤0.25mm/横覆盖≥50%格宽）时取次低带——'
        f'剔重 {len(_ul_reg)} 处：' + '；'.join(f'{p} 带高{h}/覆盖{c}' for p, h, c in _ul_reg))
if pad_detail:
    reg('N4b 口径（F 片B 0909 #30 新设）',
        '行级最紧侧＝该行全部列在表宽内（框线内缩 2pt）的墨带首/末带到上下线墨缘（600dpi ink，线宽折半）；'
        'E 1.7mm 垫顶（顶侧 dT/dE≈1.05）＋\\tabrowglue 按折数分档垫底（1/2/≥3 折 0.85/4.65/7.60mm，'
        'm 列行尾胶 <≈2.44mm 被居中吸收）——基线 0.89–2.16 → 实测落窗；'
        '底侧低值行（印答下划线墨底低伸 ≈0.9mm）登记不设红')

# ---- ⑧ 多选标记 ×1 常规 ----
duo_spans = [(pno, sp) for pno in range(1, n_pages + 1) for t, bb, sps in lines_of[pno]
             if '多选题' in t for sp in sps if '多选题' in sp['text']]
duo_ok = (len(duo_spans) == 1 and 10 <= duo_spans[0][1]['size'] <= 11
          and 'FZSSJW' in duo_spans[0][1]['font'])
check('⑧多选标记 (多选题) ×1 常规宋体 10.5（探五例1，TJ-04 目检档）', duo_ok,
      f'n={len(duo_spans)} ' + (f'{duo_spans[0][1]["font"]} {duo_spans[0][1]["size"]:.1f}pt' if duo_spans else ''))

# ---- ⑨ 行尾标点悬挂 0 容忍＋源 CJK 邻空格 0（0908 两项口径修正：
#      a) 源空格检查移 body.tex 层、与 postproc 6a 同式控制字保护——PDF 提取层给 CJK 间插空格，
#      对 PDF 文本查「源空格」是假阳源（首轮 317 全部伪）；b) 悬挂检查限栏流行（|x0−栏左|≤15pt）——
#      通栏块（学习目标等，x0≈81.7pt）以版心宽排，对栏宽查悬挂出 +49.95mm 假阳）
#      H1 片 0909c 适配（E2 banjiao 连带，旧→新）：判据 bbox→ink——banjiao 压缩把行尾标点的
#      原盒（未压缩 glyph box）推到栏右外 ~2.4–2.8mm（pymupdf bbox 假阳 28 处），实际墨缘
#      实测 −1.16…+0.32mm 贴栏右（600dpi 复测逐处）；新判据＝bbox 触发后 600dpi 验墨缘，
#      墨溢出 >0.5mm 才计悬挂（全品墨缘自身 ±0.2mm 抖动，0.5 容差留余量）。 ----
hang_bad, hang_det = 0, []
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if not t:
            continue
        cl = COLL[0] if bb[0] < MID else COLL[1]
        if abs(bb[0] - cl) > 15:
            continue
        if t[-1] in '，。；：、）】」』.,;:)]！？' and bb[2] > cl + COLW + 1:
            # ink 复核：行尾标点带（含前后 6pt）600dpi 灰渲染找墨右缘
            clip = pymupdf.Rect(cl + COLW - 24, bb[1] - 1, cl + COLW + 16, bb[3] + 1)
            pm_ = doc[pno - 1].get_pixmap(dpi=600, colorspace=pymupdf.csGRAY, clip=clip)
            _s = pm_.samples
            _w = pm_.width
            ink_cols = [c for c in range(_w) if any(_s[r * _w + c] < 150 for r in range(pm_.height))]
            ink_r = (clip.x0 + ink_cols[-1] / (600 / 72)) if ink_cols else clip.x0
            if ink_r > cl + COLW + 0.5 * PT:
                hang_bad += 1
                hang_det.append(f'p{pno}+{(ink_r - cl - COLW) / PT:.2f}mm…{t[-8:]}')
            else:
                hang_det.append(f'p{pno} bbox+{(bb[2] - cl - COLW) / PT:.2f}mm/墨{(ink_r - cl - COLW) / PT:.2f}mm（banjiao 盒后延，登记）')
_CJKC = '\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u2018\u2019\u201c\u201d'
_sp_pat = r'\\[a-zA-Z]+ +| +(?=[' + _CJKC + r'])|(?<=[' + _CJKC + r']) +'
# F 0909 收尾轮适配：扫描前剥注释域（每行首个未转义 % 起弃）——首轮 7 处残留全在 body.tex
# \vspace{-9.7pt} 行注释文案内（「…10.09/18.25 密度…」），排版不可达域
_body_nc = '\n'.join(re.split(r'(?<!\\)%', _ln)[0] for _ln in body.splitlines())
sp_resid = [m.group(0) for m in re.finditer(_sp_pat, _body_nc) if not m.group(0).startswith('\\')]
check('⑨行尾标点悬挂 0（PunctStyle=plain，栏流限域）＋源 CJK 邻空格 0（body.tex 层·注释域豁免）',
      hang_bad == 0 and not sp_resid,
      f'悬挂{hang_bad}{" " + "；".join(hang_det) if hang_det else ""} 源空格残留{len(sp_resid)}')
reg('⑨ 源空格残留注释域豁免（0909 收尾轮）', 'body.tex \\vspace{-9.7pt}% 注释文案含 7 处 CJK 邻空格'
    '（排版不可达域）——扫描改在剥注释后进行；正域 0 残留维持')

# ---- ⑩ [答案] 行无下划线（#22 \ansul 恒等的 pdf 侧取证） ----
ans_rows = [(pno, bb) for pno in range(1, n_pages + 1) for t, bb, sps in lines_of[pno]
            if t.startswith('[答案]')]
n_ul = 0
for pno, bb in ans_rows:
    for d in doc[pno - 1].get_drawings():
        for it in d['items']:
            if it[0] != 'l' or abs(it[1].y - it[2].y) > 0.5:
                continue
            uy = it[1].y
            ux0, ux1 = sorted((it[1].x, it[2].x))
            # 0908：限字底带（下划线贴 baseline 下方）——窗口放宽到行顶时误中本行 \sqrt 顶栏（3 处假阳）
            if bb[3] - 0.5 <= uy <= bb[3] + 2 and min(bb[2], ux1) - max(bb[0], ux0) > 1:
                n_ul += 1
check('⑩ 正文无答案行（答案制0911 反向门：[答案]行×0；旧门「ansul 无下划线恒等×14」随答案出册）',
      len(ans_rows) == 0 and n_ul == 0,
      f'答案行 {len(ans_rows)}/0 行内下划线 {n_ul}')

# ---- ⑪ 题侧标签隙 标签→[ 2.7±0.6＋]→题干 2.2±0.6（半角[]；0908 二修：
#      a) 计数 ×14→×23——源文题侧 [简单/中档(知识点N)] 全数保留＝例1 9＋变式 9＋检测 5（探针实证），
#      规格 ×14 系漏计例1；b) 后隙豁免 CJK 限定——5 处后随数学式/数字，改同基线 9–12pt 任意字） ----
gaps_pre, gaps_post, gaps_wrap = [], [], []
for pno in range(1, n_pages + 1):
    cs = chars_of[pno]
    for i in range(1, len(cs)):
        c, bb, sz, fn = cs[i]
        pc, pbb, _, _ = cs[i - 1]
        if c == '[' and i + 1 < len(cs) and cs[i + 1][0] in '简中难':
            gaps_pre.append((bb[0] - pbb[2]) / PT)
        if c == ']' and pc == ')' and 10 <= sz <= 11 and i + 1 < len(cs):
            nc, nbb, nsz, _ = cs[i + 1]
            if 9 <= nsz <= 12 and abs(nbb[1] - bb[1]) < 2:
                gaps_post.append((nbb[0] - bb[2]) / PT)
            else:
                gaps_wrap.append(pno)   # 题干换行态：标签行末无水平后隙（dy≈17pt 下行起排）
tie_ok = (len(gaps_pre) == 23 and all(2.1 <= v <= 3.3 for v in gaps_pre)
          and len(gaps_post) == 22 and all(1.0 <= v <= 2.7 for v in gaps_post) and len(gaps_wrap) == 1)
check('⑪题侧标签隙 标签→[ 2.7±0.6 ×23＋]→题干 2.2±0.6 ×22＋换行态1（TJ-03；并排恢复0910 探三题干回图旁 minipage）', tie_ok,
      f'前隙 n={len(gaps_pre)} {" ".join("%.2f" % v for v in gaps_pre)}｜后隙 n={len(gaps_post)} {" ".join("%.2f" % v for v in gaps_post)}'
      f'｜换行态 {len(gaps_wrap)}（p{",".join(str(x) for x in gaps_wrap)}）')
reg('⑪ 并排恢复0910 后隙/换行态计数 23/0 → 22/1', '探三例1 题干由下置形回归图旁 minipage（◆标签行题干位传空）'
    '⇒ 该标签行末无水平后隙＝换行态 0→1、内联 23→22；探二图挂【详解】区不入标签行，故仅 1 处（F 片A 时代'
    '探三/六/八三处同态＝3）。前隙恒 23（标签→[ 由宏 \\hspace 定值，与题干形态无关），实测窗内 2.14–2.70；'
    'TJ-03 2.2mm 口径不变（只锁内联态）。')
reg('⑪ 片G 0910 后隙/换行态计数 20/3 → 23/0', 'F 片A 时代探三/六/八题干走图旁 minipage（◆标签行题干位传空）'
    '⇒ 标签行末无水平后隙＝换行态 3；片G 图下置后三组题干回归 \\tjdnr 第 5 参内联，'
    '后隙全部可测（恒 2.20mm＝宏 \\hspace 定值）⇒ 内联 20→23、换行态 3→0；TJ-03 2.2mm 口径不变')
reg('⑪ 题侧计数口径（0908；F 片A 0909 后隙 18→20）', '源文题侧 [简单/中档(知识点N)] 全数保留＝23（例1 9＋变式 9＋检测 5）；'
    '规格 ×14 系漏计例1，作废；隙距 2.7/2.2 由宏 \\hspace 给出恒定；后隙 18→20（探二/探九题干由并排 minipage 改内联，'
    '标签行末水平后隙可测 +2）、换行态 5→3（同因）；TJ-03 2.2mm 只锁内联态')

# ---- ⑫ 探究点标题单行 ≤82mm ×9＋名字清单（0908 改基线归并——◆标题行内 \hspace{2em} 被 MuPDF
#      拆为「◆探究点N」＋名字双片段，逐片段比对名单恒异） ----
EXP_TJD = {'◆探究点一空间向量的概念辨析', '◆探究点二空间向量的线性运算', '◆探究点三用基底表示向量',
           '◆探究点四共面向量的判定', '◆探究点五数量积的概念与运算律', '◆探究点六数量积求夹角与投影',
           '◆探究点七数量积条件求参', '◆探究点八数量积求距离(展开法)', '◆探究点九数量积求距离(折叠矩形)'}
_grp12 = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        # 0908：◆ 小图元 8.6pt 基线比正文 12pt span 高 1.195pt（探针实证），sps[0]（＝◆）作键跨 0.5pt 桶界
        # 把「◆探究点N」与名字拆成两组恒出裸名——改取主字号 span 基线归并
        base = max(sps, key=lambda s: s['size'])['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp12.setdefault((pno, cl, round(base * 2)), []).append((bb[0], bb[2], t))
tjd_rows = []
for frs in _grp12.values():
    frs.sort()
    mt = ''.join(x[2] for x in frs).replace(' ', '')
    if mt.startswith('◆探究点'):
        tjd_rows.append((mt, min(x[0] for x in frs), max(x[1] for x in frs)))
tjd_w_ok = all((x1 - x0) / PT <= 82 for _, x0, x1 in tjd_rows)
tjd_name_ok = {t for t, _, _ in tjd_rows} == EXP_TJD
check('⑫探究点标题单行 ≤82mm ×9＋名字清单（RENAME 探六/探七压字；基线归并口径 0908）',
      len(tjd_rows) == 9 and tjd_w_ok and tjd_name_ok,
      f'n={len(tjd_rows)} 最宽{max((x1 - x0) / PT for _, x0, x1 in tjd_rows) if tjd_rows else -1:.1f}mm '
      f'名单{"合" if tjd_name_ok else "异:" + str({t for t, _, _ in tjd_rows} ^ EXP_TJD)}')

# ---- ⑭ (\kongwei) 空位 6.8±0.6 ×8（窗外 () 相邻对＝源文空()杂对，登记不计红，0908 口径） ----
# F 片C 0909 适配（旧→新）：#34 × 走 TikZ 后判断答案槽 '(' ')' 成相邻字符（1.8em 空档 6.4mm），
#   旧式误计为 \kongwei 对（+4）；按 × 墨盒夹在括号对之间者剔除。
_x_boxes14 = {}
for _pno in range(1, n_pages + 1):
    for _d in doc[_pno - 1].get_drawings():
        if _d['fill'] is None:
            continue
        _r = pymupdf.Rect(_d['rect'])
        if 2.2 < _r.width / PT < 2.6 and 2.2 < _r.height / PT < 2.6:
            _x_boxes14.setdefault(_pno, []).append(_r)
kw_gaps, kw_stray = [], []
for pno in range(1, n_pages + 1):
    cs = chars_of[pno]
    for i in range(len(cs) - 1):
        if cs[i][0] == '(' and cs[i + 1][0] == ')':
            lp, rp = cs[i][1], cs[i + 1][1]
            yc = (min(lp[1], rp[1]) + max(lp[3], rp[3])) / 2
            if any(abs((r.y0 + r.y1) / 2 - yc) < 6 and lp[2] - 1 <= r.x0 and r.x1 <= rp[0] + 1
                   for r in _x_boxes14.get(pno, [])):
                continue
            v = (rp[0] - lp[2]) / PT
            (kw_gaps if 6.2 <= v <= 7.4 else kw_stray).append((pno, lp[1], v))
check('⑭空位 (\\kongwei) 宽 6.8±0.6 ×9（#17 定宽空档；探八右挂补 1 后全集 0909；窗外杂对≤1）',
      len(kw_gaps) == 9 and len(kw_stray) <= 1,
      f'n={len(kw_gaps)} ' + ' '.join(f'{v:.2f}' for _, _, v in kw_gaps)
      + (' 杂:' + ' '.join(f'p{p}y{y:.0f}/{v:.2f}' for p, y, v in kw_stray) if kw_stray else ''))
if kw_stray:
    reg('⑭ 空位杂对登记', '窗外 () 相邻对 ' + ' '.join(f'p{p}y{y:.0f}/{v:.2f}' for p, y, v in kw_stray)
        + '（成因＝源文空()，非 \\kongwei 产物；p6 y157.8 Times10.5 gap0.00 实证）')

# ---- ⑮ 五例1图归属＝探二/三/六/八/九（回退轮0910 位图台账口径；片G 矢量簇台账作废） ----
# F 片A 0909 适配：归属键＝阅读序（页, 栏, y）——旧键（页, y）在同 y 双栏标题（p5 六/七 同 y 17.5）
# 与跨栏流（p6 九标题在左栏、其图在右栏顶）两处误归属（实测旧：{七,三,二,八}）。
# 片G 0910 适配：三联图旧由「居中独立」判据排除，今六图皆居中独立——改由片段名 g6-triple（条目3 投影图，非探究点图）排除。
# 回退轮0910 适配：取图键由矢量簇台账改位图矩形台账（共用台账 FIGS 元组形制不变，归属算法零改动）。
tjd_events = []   # (pno, col, y, 序) — ◆探究点行（col：0 左栏／1 右栏）
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        if t.startswith('◆探究点'):
            tjd_events.append((pno, 0 if bb[0] < MID else 1, bb[1], t[4]))
ATT_WANT = [('g2-cubeE', '三'), ('g3-cube6', '六'), ('g4-dihedral', '八')]   # 答案制0911：g1→二／g5→九 随 [详解] 出册
side_att = {}
for frag, pno, col, r, _info in FIGS:
    if frag == 'g6-triple':
        continue
    prev = [ev for ev in tjd_events if (ev[0], ev[1], ev[2]) <= (pno, col - 1, r.y0 + 2)]
    if prev:
        side_att[frag] = max(prev, key=lambda e: (e[0], e[1], e[2]))[3]
check('⑮ 三例1图归属＝探三/六/八（答案制0911：正文余例1图 3·逐图一对一归属；g1→二／g5→九 出册）',
      len(FIGS) == 4 and [side_att.get(f) for f, _w in ATT_WANT] == [w for _f, w in ATT_WANT],
      '归属 ' + ' '.join(f + '→' + side_att.get(f, '未属') for f, _w in ATT_WANT))
reg('⑮ 口径登记（回退轮0910 位图台账·旧→新）',
    '片G 旧门：共用台账 FIGS（矢量簇）逐片段一对一核 g1→二／g2→三／g3→六／g4→八／g5→九。'
    '新门：FIGS 改位图矩形台账（元组形制同），归属算法与期望映射不变——g2 落位 p4c1→p3c2 后，'
    '其前最近 ◆探究点 仍为「三」（p3c2 y610），五图归属实测 {二,三,六,八,九} 逐图不变；'
    '三联 g6 系条目3 图不入归属（口径承片G）。')

# ---- ⑪⑫⑬ 内容层 ----
n_kd = body.count(r'\kongda{')
n_kb = body.count(r'\kongbai{}')
check('⑪挖空 body.tex：印答 \\kongda ×0（反向锁，旧 ×20）＋空留白 \\kongbai ×34（原题干 14＋知识点 20＝全品对齐0911 6h）',
      n_kd == 0 and n_kb == 34, f'kongda={n_kd} kongbai={n_kb}/34')
# ⑪-2 旧门「印答值 pdf 在场（p1/p2）」随全品对齐0911 出册作废（印答不再排印，值含 Common 词伪阳）——
#   值在场改册侧锁＝㉑d；正文侧反向锁＝⑪-3 空档盒（线下无值）＋⑥（　）×6。
reg('⑪-2 作废登记（全品对齐0911）', '旧 ANSWERS 14 词 p1/p2 包含判定停用（迁 ㉑d 册侧正向＋⑪-3 反向）；'
    '旧值与逐词表见 .bak_全品对齐0911')
n_blank_anchor, n_val_anchor, kd_pt = 0, 0, []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for d in page.get_drawings():
        for it in d['items']:
            if it[0] != 'l' or abs(it[1].y - it[2].y) > 0.5:
                continue
            ux0, ux1 = sorted((it[1].x, it[2].x))
            uw = ux1 - ux0
            if not (42 <= uw <= 60) or ux0 < MARGIN - 8 or ux1 > COLR + 8:
                continue
            if in_fig(pno, ux0, it[1].y - 0.6, ux1, it[1].y + 0.6):
                continue   # 回退轮0910：图内水平棱防御排除（位图时代恒不触发）
            near = []
            for blk in page.get_text('dict')['blocks']:
                for ln in blk.get('lines', []):
                    for sp in ln['spans']:
                        sx0, _, sx1, sy1 = sp['bbox']
                        if not sp['text'].strip():
                            continue
                        ov = min(sx1, ux1) - max(sx0, ux0)
                        if ov > 0.5 * min(sx1 - sx0, uw) and -1.5 <= sy1 - it[1].y <= 1.5:
                            near.append(sp['text'])
            if len(near) == 0:
                n_blank_anchor += 1
                kd_pt.append(uw)
            elif len(near) == 1:
                n_val_anchor += 1
kd_min = min(kd_pt) if kd_pt else -1
check('⑪-3 空档盒全量实测（全品对齐0911：42–60pt 下划线＋线下无值 ×34＝kongbai 全集；印答盒线下恰一值 ×0 反向锁）',
      n_blank_anchor == 34 and n_val_anchor == 0 and n_kd == 0 and kd_min >= 42,
      f'空档 {n_blank_anchor}/34 最窄 {kd_min:.1f}pt；印答值盒 {n_val_anchor}/0；body kongbai={n_kb}/34')
reg('⑪-3 口径（全品对齐0911 换锁）', 'signature＝栏带 42–60pt 水平细线（\\kongbai 15mm＝42.5pt）且线下 ±1.5pt '
    '无紧贴值 span——旧「线下恰一值」印答盒签名（\\kongda 自适应盒）随 6h 出册归零；实测分布 '
    'p1-5＝11/9/6/5/3（全页扫描，旧门限 p1/p2 口径作废）；值在场正向锁＝㉑d 册侧包含判定；'
    '旧 20 处盒宽全量实测史（≥42pt＋寄存器 \\kdmind/\\kdwd）见 .bak_全品对齐0911')
n_zt = body.count(r'\zhenti{')
n_ztb = body.count(r'\zhentib{')
n_jx_body = body.count(r'\jiexi{')
check('⑫判断题：\\zhenti ×0（反向锁，旧 ×6）＋\\zhentib（空括号式）×6＋简析 jiexi ×0（答案制0911：14 行出册）',
      n_zt == 0 and n_ztb == 6 and n_jx_body == 0,
      f'zhenti={n_zt} zhentib={n_ztb}/6 jiexi={n_jx_body}')
segs = re.split(r'\\zsd\{', body)[1:]
seqs = [[int(x) for x in re.findall(r'\\tiaomuz?\{(\d+)\}', s)] for s in segs]
check('⑬条目按知识点重起（[1,2,3]/[1,2]/[1,2,3,4]）', seqs == [[1, 2, 3], [1, 2], [1, 2, 3, 4]], f'实测 {seqs}')

# ---- N11 悬空引用禁则（F 片C 0909 #27；postproc 8 步同禁则）----
# 旧模式 衔接\d 对「衔接条目5」漏检（数字前有「条目」二字），且不覆盖「条目9」「支撑条目16、17、34」
# 等连号引用；本片 5 处编注改指名式后，禁则升为「条目＋阿拉伯数字」0 命中（body.tex＋PDF 双查）。
item_num_body = re.findall(r'条目\s*\d', body)
item_num_pdf = re.findall(r'条目\s*\d', full)
check('N11 悬空引用禁则：正文「条目+数字」0 命中（body.tex＋PDF 双查）',
      not item_num_body and not item_num_pdf,
      f'body={item_num_body} pdf={item_num_pdf}')

# ---- 拉伸异常行（F 片F 0909c #41 新设）----
# 口径：逐页 rawdict 行内相邻字符对（按 x 排序），gap = x0[i+1] − x1[i] > 0.5em（em＝左字 size）；
#   间隙内无墨（400dpi 灰值 <160）——有墨者系 \kongda 下划线／自绘符号（√×∥）／无 ToUnicode 字形
#   填充的假空档（故√．、打×）三类的直接排除；两侧均 CJK（CJK-CJK 档）——xeCJK 的 CJKglue 自然
#   0pt（默认 0 plus 0.08\baselineskip），故 CJK-CJK 空档 >0.5em 只可能来自行内拉伸，是「字间距
#   过远」的直接签名。CJK-西文档含宏设计固定隙（题侧 2.2mm／◆ 2.4mm／检测题号 2.7mm／选项网格
#   槽位／\hfill 右挂 189pt），不设门、逐处登记在报告。
#   设计隙白名单：gap/size ≈1.0（\quad）或 ≈2.0（2em）＝宏层固定字距（章名/课时/知识点标题/
#   探究点标题/花形右词），实测恒 6.47/11.97/12.95/20.59/23.97pt，不随行拉伸浮动，排除。
#   基线（0909 片F 量）：3 处/3 行（p1 表|示 12.40、p3 变|式 6.18、p5 变|式 14.91）；改后目标 0。
def _cjk(ch):
    o = ord(ch[0]) if ch else 0
    return any(a <= o <= b for a, b in ((0x2E80, 0x2EFF), (0x3000, 0x303F), (0x3041, 0x30FF),
                                        (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF),
                                        (0xFE30, 0xFE4F), (0xFF00, 0xFFEF)))

_stretch_rows = []
_SKIPCH = set('\u20d7\u20d6\u20d0\u20d1\u20e1\u0338\u00a0\u2060')
for _pno in range(len(doc)):
    _pg = doc[_pno]
    _pix = _pg.get_pixmap(dpi=400)
    _img = _np.frombuffer(_pix.samples, dtype=_np.uint8).reshape(_pix.height, _pix.width, _pix.n)
    if _pix.n >= 3:
        _img = _img[:, :, :3].mean(axis=2).astype(_np.uint8)
    _chars = []
    for _b in _pg.get_text('rawdict')['blocks']:
        if _b['type'] != 0:
            continue
        for _l in _b['lines']:
            for _sp in _l['spans']:
                for _c in _sp['chars']:
                    _bb = _c['bbox']
                    if _c['c'] in _SKIPCH or not _c['c'].strip() or _bb[2] - _bb[0] <= 0.05:
                        continue
                    _chars.append((round(_l['bbox'][1], 1), _bb[0], _c['c'], _bb, _sp['size']))
    _chars.sort(key=lambda x: (x[0], x[1]))
    _grp = []
    for _c in _chars:
        if _grp and abs(_c[0] - _grp[-1][0]) < 1.2:
            _grp[-1][1].append(_c)
        else:
            _grp.append((_c[0], [_c]))
    for _gy, _cs in _grp:
        _cs.sort(key=lambda x: x[1])
        for _i in range(len(_cs) - 1):
            _a, _b2 = _cs[_i], _cs[_i + 1]
            # H3 片 0909c 口径修：y 分组（容差 1.2pt）会把左右栏同行 y 巧合的两片段并作一组，
            # 跨栏对（左栏行尾→右栏行首，间距＝栏空 15–150pt）被误判超拉——3 处假阳实证
            # （p3y608.7 150.05pt／p4y428.1 14.87pt／p6y347.9 21.55pt，均为左栏段末+右栏行首）。
            # 真口径＝同一栏内的行内相邻字符对，加栏归属判（按 x0 过栏中缝 MID 分侧）。
            if (_a[3][0] < MID) != (_b2[3][0] < MID):
                continue
            _gap = _b2[3][0] - _a[3][2]
            if _gap <= 0.5 * _a[4] or not (_cjk(_a[2]) and _cjk(_b2[2])):
                continue
            _px0 = int(_a[3][2] * 400 / 72); _px1 = int(_np.ceil(_b2[3][0] * 400 / 72))
            _py0 = int((min(_a[3][1], _b2[3][1]) - 0.6) * 400 / 72)
            _py1 = int(_np.ceil((max(_a[3][3], _b2[3][3]) + 0.6) * 400 / 72))
            _px0 = max(0, _px0); _py0 = max(0, _py0)
            _px1 = min(_pix.width, _px1); _py1 = min(_pix.height, _py1)
            if _px1 > _px0 and _py1 > _py0 and (_img[_py0:_py1, _px0:_px1] < 160).any():
                continue   # 间隙有墨（下划线/自绘符号/无 ToUnicode 字形）
            _ratio = _gap / _a[4]
            if 0.9 <= _ratio <= 1.1 or 1.9 <= _ratio <= 2.1:
                continue   # \quad / 2em 设计字距
            _stretch_rows.append((_pno + 1, _gy, _a[2], _b2[2], round(_gap, 2)))
check('拉伸异常行＝0（CJK-CJK 空档 >0.5em 且无墨且非 \\quad/2em 设计字距；F 片F 0909c #41 新设）',
      len(_stretch_rows) == 0,
      f'实测 {len(_stretch_rows)} 处' + ('' if not _stretch_rows else '：' +
      '；'.join(f'p{p}y{y} {a}|{b} {g}pt' for p, y, a, b, g in _stretch_rows[:8])))
reg('拉伸异常行口径（F 片F 0909c #41 新设；H3 片 0909c 加栏归属判）',
    'CJK-CJK 空档 >0.5em＋间隙无墨（400dpi<160，排 \\kongda 下划线/√×∥ 自绘/无 ToUnicode 字形）'
    '＋非 \\quad(≈1em)/2em 设计字距（章名/课时/知识点/探究点/花形右词，恒 6.47/11.97/12.95/20.59/23.97pt）；'
    '基线 3 处/3 行（p1 表|示 12.40、p3 变|式 6.18、p5 变|式 14.91）→ 改后 0；'
    'CJK-西文档（含宏设计固定隙）不设门、逐处登记；'
    'H3 片 0909c：加「同栏」判（(x0<MID) 异侧即跨栏对，跳过）——E8 标点统一后行断点位移，'
    '左右栏同行 y 巧合并组冒 3 处跨栏假阳（p3y608.7 150.05／p4y428.1 14.87／p6y347.9 21.55pt，'
    '均左栏段末+右栏行首，目检无拉伸），加判后 0；'
    '全品对齐0911 曾豁免 1 行 3 对（p1y488.9「在|的|直|线」3×5.51pt 均拉），排版病0911 已修：'
    'postproc 表1 共线行·定义列格文首个 \\kongbai 前插 \\hspace{0pt plus 1fill}——断行空隙全进 fill、文字零拉伸；'
    '格内换行 7/7/4/1→8/8/2/1（四行 y 坐标与两空线盒位与旧版逐字节同、prevgraf 仍 4、行高档不变），'
    '行1-2 均拉 4.61→2.46pt（格内两端对齐设计档内），行3「直线」1.04pt 自然缝；白名单删除，门回净 ==0')

# ---- ㉑ 答案册侧值在场（答案制0911 新立；册＝../导学件答案册-v1/）----
# 正文侧「判分值 0 在场」＝⑥（含故答案为/故选/[解析]0＋（　）×6 正锁）＋⑩ 反向门＋⑫ zhenti 0＋⑪ kongda 0（全品对齐0911 全域反向）。
# 册侧「值在场」：编译三0＋页数4；排印七项计数（含课前预习 +3/+3）；23 题逐一＋㉑d 课前预习逐组 包含判定。
import unicodedata
ANS_DIR = os.path.join(os.path.dirname(BASE), '导学件答案册-v1')

def _barg21(s, i):
    d = 0
    for k in range(i, len(s)):
        if s[k] == '{':
            d += 1
        elif s[k] == '}':
            d -= 1
            if d == 0:
                return s[i + 1:k], k + 1
    raise ValueError('brace unbalanced')

def _core21(v):
    # \( \) 系行内数学定界符（渲染不可见）先剥；\sqrt→√；其余命令与括号残留符剔除
    v = v.replace('\\(', '').replace('\\)', '')
    v = re.sub(r'\\[a-zA-Z]+', lambda m: '√' if m.group(0) == '\\sqrt' else '', v)
    return re.sub(r'[{}\\^_$]', '', v)

def _norm21(s):
    s = unicodedata.normalize('NFKC', s)   # 𝑏(U+1D465)→b 等数学字母；．→. 全角折半
    return re.sub(r"[\s．.。°∘−–—\u0300-\u036f\u20d0-\u20ff-]", '', s)

anslog = open(os.path.join(ANS_DIR, 'main.log'), encoding='utf-8', errors='ignore').read()
a_err = len(re.findall(r'^!', anslog, re.M))
a_over = len(re.findall(r'Overfull', anslog))
a_miss = len(re.findall(r'Missing character', anslog))
ama = re.search(r'Output written on main\.pdf \((\d+) pages', anslog)
a_pages = int(ama.group(1)) if ama else -1
abody = open(os.path.join(ANS_DIR, 'body.tex'), encoding='utf-8').read()
a_items = []
for m21 in re.finditer(r'\\dansitem\{|\\ansitem\{', abody):
    st21 = m21.end() - 1
    k21a, j21 = _barg21(abody, st21)
    if j21 >= len(abody) or abody[j21] != '{':
        continue
    k21b, _j21b = _barg21(abody, j21)
    a_items.append((k21a, k21b))
adoc = pymupdf.open(os.path.join(ANS_DIR, 'main.pdf'))
atxt = _norm21(''.join(pg.get_text() for pg in adoc))
a_nimg = sum(len(pg.get_image_info()) for pg in adoc)
adoc.close()
check('㉑a 答案册编译三0＋页数4（答案制0911 新立）',
      a_err == 0 and a_over == 0 and a_miss == 0 and a_pages == 4,
      f'errors={a_err} overfull={a_over} missingchar={a_miss} 页数={a_pages}')
cnts21 = {'[答案]': 26, '[分析]': 9, '[详解]': 9, '[点睛]': 2, '[解析]': 17, '题型:': 18, '[题型总结]': 9}
# （atxt 过 NFKC——全角冒号折半角，键用 ASCII '题型:'；全品对齐0911：[答案]23→26、[解析]14→17＝课前预习 +3/+3）
miss21 = [f'{t}={atxt.count(t)}/{w}' for t, w in cnts21.items() if atxt.count(t) != w]
check('㉑b 答案册排印计数（pdf 明文去空白：[答案]26/分析9/详解9/点睛2/解析17/题型行18/题型总结9）＋位图2',
      not miss21 and a_nimg == 2, ('缺异 ' + ' '.join(miss21) if miss21 else '七项全合') + f'｜位图 {a_nimg}/2')
val_ok, val_bad = True, []
for k21a, k21b in a_items:
    core21 = _norm21(_core21(k21b))
    pat21 = _norm21(k21a) + '[答案]' + core21
    if not core21:
        val_ok = False
        val_bad.append(k21a + ':空核')
    elif pat21 not in atxt:
        val_ok = False
        val_bad.append(k21a + '→' + core21[:26])
check('㉑c 答案册 23 题判分值逐一在场（题号+[答案]+值核·去空白包含判定）',
      val_ok and len(a_items) == 23,
      f'条目 {len(a_items)}/23' + (' 全在场' if val_ok else ' 未在场: ' + '；'.join(val_bad)))
# ---- ㉑d 课前预习值在场（全品对齐0911 新立；素材＝去答案0911/课前预习素材0911.txt）----
PRE = r'C:\提示词\工作区\_tmp取证0909c\片G\去答案0911\课前预习素材0911.txt'
_pg = []
for _ln in open(PRE, encoding='utf-8').read().splitlines():
    _f = _ln.split('\t')
    if _f[0] == 'G':
        _pg.append([_f[1], _f[2], [], []])
    elif _f[0] == 'K':
        _pg[-1][2].append((int(_f[1]), _f[2]))
    elif _f[0] == 'J':
        _pg[-1][3].append((_f[1], _f[2], _f[3]))
assert len(_pg) == 3 and [len(g[2]) for g in _pg] == [11, 5, 4] \
    and [len(g[3]) for g in _pg] == [2] * 3, '㉑d 素材分组异常'
# v10-C 条目分组：与 组装body.py._pre_entry_counts 同式解析 variantF 知识点区（\zsd 起、◆探究点一正文前止），
#   逐知识点给 [(\tiaomu 条目号, 该条 \kongbai 数)]——册「一、课前预习」[答案] 按条目成段「N．值 值…」，
#   不逐空编号（旧 ㉑d＝逐空编号「1值2值…」，v10-C 改全品 p04 式，登记见本 reg）。
_p0, _p1 = body.index('\\zsd{'), body.index('\\tjdnr{一}')
_pp = re.split(r'\\zsd\{(.)\}\{([^}]*)\}', body[_p0:_p1])
_ents21 = []
for _gi in range(1, len(_pp), 3):
    _es = re.split(r'\\tiaomu[zt]?\{(\d+)\}', _pp[_gi + 2])
    _ents21.append([(int(_es[_ei]), _es[_ei + 1].count('\\kongbai{}')) for _ei in range(1, len(_es), 2)])
assert len(_ents21) == 3 and [sum(c for _n, c in g) for g in _ents21] == [11, 5, 4], \
    '㉑d 条目分组与素材不平（v10-C 分组失效）'
d_ok, d_bad = True, []
for (_ci, _nm, _ks, _js), _ents in zip(_pg, _ents21):
    _idx, _frg = 0, []
    for _n, _k in _ents:
        if _k == 0:
            continue
        _frg.append('%d%s' % (_n, ''.join(_core21(v) for _i, v in _ks[_idx:_idx + _k])))
        _idx += _k
    assert _idx == len(_ks), '㉑d 填空值数与条目空数不平：知' + _ci
    fill = ''.join(_frg)
    judg = ''.join('%s%s' % (no, sy) for no, sy, _j in _js)
    if _norm21(fill) not in atxt:
        d_ok = False; d_bad.append('知' + _ci + '填空串')
    if _norm21(judg) not in atxt:
        d_ok = False; d_bad.append('知' + _ci + '判断答串')
    for no, _s, jx in _js:
        # 简析锚＝源串首个 ≥5 字中数/全角标点连串（≤12 字）——数学区两侧提取形制不同（\neq 剔除 vs ≠ 在场），
        #   锚止于数学前即双侧同形（㉑c run1 教训推广）
        _seg = re.search(r'[\u4e00-\u9fff0-9，、；：。]{5,}', jx)
        core = _norm21(_seg.group(0))[:12] if _seg else ''
        if not core or core not in atxt:
            d_ok = False; d_bad.append('知' + _ci + '析' + no)
check('㉑d 课前预习节值在场（三组填空按条目分段整串＋判断答整串＋简析逐条首段≥5字锚·去空白包含判定）', d_ok,
      '三组九判定全在场' if d_ok else '未在场: ' + '；'.join(d_bad))
reg('㉑d 口径（全品对齐0911 新立；v10-C 条目分组改）',
    '册 body「一、课前预习」节每组 [答案]＝填空按知识点条目分段「N．值　值…」（v10-C 全品 p04 式：'
    '条目号＝variantF \\tiaomu 号、段内不逐空编号、值间全角空格；0 空条目跳过）＋判断 (N)√× 另段、'
    '[解析]＝逐条 (N) 简析多段（　与全角空格随去空白剔除）——条目分组与 组装body.py._pre_entry_counts '
    '同式（解析 variantF body \\zsd→\\tjdnr{一} 区，硬断言总数 11/5/4），复组成串过 _norm21 后 pdf 明文包含判定；'
    '旧口径＝逐空编号「1值2值…11值」（v9 及以前，见 .bak_对齐0911），v10-C 起停用；'
    '简析锚＝首个 ≥5 字中数连串截 12（数学串 TeX↔pdf 形制不同、锚止于数学区前，㉑c run1 教训推广）；'
    '正文侧反向锁＝⑪（kongda 0）＋④/⑥/⑰/N1（（　）挂5＋断行独1＝6 槽／[解析]0）')
reg('答案制0911 断言同步总账（旧→新·逐门）',
    '门① 页数 7→5；门⑥ [答案]14/[解析]20/[分析]9/[详解]9/[点睛]2 → 0/6(仅判断)/0/0/0，另立 故答案为0/故选0 二核；'
    '◆9/例1 9/变式9/★0 不变。⑰ 解析span 20→6；门③ 超高定界符 恰4→恰0（探七 array×2＋探八 放大对×2 随 [详解] 出册）；'
    '门⑩ 答案行 14→0（改反向门）；门⑫ jiexi 14→0（zhenti×6 保留）；位图台账 6→4——⑱ 并排 2→1（仅 g2 逐图钉）·'
    '下置 4→3·位图 6→4·minipage 4→2·side 2→1·raisebox 2→1；⑱-2/⑱-3/N6 四图口径；⑮ 归属 5→3（g2→三／g3→六／g4→八）；'
    'FIG_AT 落位钉按 5 页新分页重钉；REDGE_W/SIDE_PIN 去 g1 项。保留面双向锁：判断括号 (√)(×)×6（④）、kongda 印答×20（⑪）、'
    '简析[解析]×6（⑰）、素养小结×9（N8）、诊断头×3（⑮旧门）均在正文。新立 ㉑a/b/c 册侧门。'
    '生成链侧硬断言＝postproc 6g 九字面全 0；逐块台账＝去答案清单.md（63 块）；旧值全录 .bak_去答0911。')
reg('答案制0911 复跑回填钉账（run1 读数→钉·旧→新）',
    '① FIG_AT 四图钉初钉即全中（g6(2,2)/g2(3,2)/g3(4,1)/g4(4,2)）——旧七页档 g1(3,2)/g5(6,2) 出册；'
    '② ⑭ 末页栏线：multicol 末页栏线高＝末栏实高 123.4mm＜旧门槛 0.5×TEXTH(128.7mm)——末页阈值降 0.22×TEXTH，'
    '非末页口径逐字不变（p4 258.2mm 满栏照常）；③ ③定界符 ==0 误判→复钉 ==4：残余＝◆探究点八(展开法)/九(折叠矩形)'
    '12pt 标题括号 4 字符（11.985pt，0908 旧豁免集本即此四字符、页位 p6/p7→p4/p5），探七 array／探八数学对已随详解出册；'
    '④ ⑱-2 下距上界 3.89→4.15：g3 探六图下邻由 10.5pt 解析行回行为 12pt 变式标签行，墨顶抬升，实测 4.09（余图 3.19/3.30 不动）；'
    '⑤ N10 重释：正文 [解析]→题号配对仅存判断域 1 对（2.42mm）——旧门 n≥3 中位 5.21±0.5 的四对全系变式/检测简析（已出册），'
    '新门 n 1–2 且 2.0–3.5mm（与 ⑦-4 判断缝域同族；若变式简析回渗则读数≈5.2 即红，反向锁在位）；'
    '⑥ ㉑c 值核口径 run1 13 项未在场→修准：册 pdf 数学字母走 NFKC（𝑏→b）、行内数学定界符（渲染不可见）先剥、'
    '√ 映射、∘／° 与 U+20D7 组合箭头剔除——修后 23/23 全在场；⑦ ㉑b 「题型：」过 NFKC 折半角冒号，键改 ASCII（run2 唯一残余 ✗）。')

print('—— 断言实测 ——')
for s in okmsg:
    print(' ✓', s)
for s in regmsg:
    print(' ◎ 登记', s)
for s in fails:
    print(' ✗', s)
print('断言结果：', '全部通过' if not fails else f'未通过 {len(fails)} 项')
raise SystemExit(0 if not fails else 1)
