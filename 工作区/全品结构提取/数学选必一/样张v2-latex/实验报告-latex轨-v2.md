# LaTeX 轨 v2 实验报告（样张v2-latex · main_v2）

日期：2026-09-07　｜　前置：`实验报告-latex轨.md`（v1 报告，未改动；环境/源节抽取/公式保真 282 条 0 错误等结论在 v2 全部继承）
本轮为 v2 收尾：p5 空栏页修复 ＋ 两条精修要求（题号列恒空、表头白底黑体加粗）＋ 终版全量验证。

## 一、v2 相对 v1 的总变更（背景，上轮已完成）

1. twocolumn → multicol：节/小节标题、统计行、章首导航表通栏（multicol 外），仅正文双栏；栏线用 multicol 原生 `\columnseprulecolor`
2. 表格弃 booktabs 三线制 → 全框 0.4pt `\hline` 网格；列宽弃 `\real` 占比改定长；`\tabcolsep` 3pt
3. 图内容感知分档 30/45mm（86mm 档禁用）
4. 结构增补：`\zhishi` 知识点块、`\zutit` 探究点挂号、T0 章首导航表
5. 逻辑绑定：`\penalty10000` 题干→选项/①链/尾句；`\clubpenalty=\widowpenalty` 10000；xeCJK CheckSingle

## 二、p5 空栏页：根因实证链与定案（本轮核心）

**症状**（9 页初版）：1.1.1.3-2 的【详解】＋image1＋「故答案为」整块放不进 p4 剩余 74pt，整体推到 p5；p5 仅左栏 ~197pt 材料、右栏全空，探究点三跳 p6。

**tracingpages 铁证**：multicol 按**整页** 1575.68pt（goal height）收集材料（非按栏 787pt）；p5 采纳的断点是 `t=197.61 plus 1.0fil b=0 p=-10000`——正是 needspace 的 `\vfil`＋`\break` 路径。

**机制**：needspace 的断点无论 starred（`\pagebreak`）还是 unstarred（第二栏直接 `\vfil\break`），本质都是 `\penalty-10000`；在 multicol 的整页收集机制下它是**页级断点**——把整页提前收断、跳过第二栏 → 空栏页。starred↔unstarred 互换无效（两者都含强制断点）。

**单变量实验（定罪）**：仅删 `\zutit` 的 `\Needspace{6\baselineskip}`、其余不动 → 编译一次 **9→8 页**、p5 双栏满（overfull 仍 0）→ 根因确认。

**定案**：multicol 内禁用一切含 `\break`/`\pagebreak` 的 `\Needspace`。
- `\zhishi`/`\zutit`/`\timu` 前置换 `\glueguard{N}`＝`\vskip 0pt plus N\baselineskip\penalty-100\vskip 0pt plus -N\baselineskip`（无 `\break` 的软断点：剩余够时不触发，不够时整块顺移；正负伸缩自闭合）。N 取 4/6/4。**防孤悬由强制保证降级为 best effort，登记在案**；
- `\jietitle`/`\xiaojietitle` 在 multicols 外，保留 `\Needspace*`；
- 终版构建因表格列宽收缩（见下）内容回排为 9 页；tracingpages 复核：全篇**无任何被采纳的 p=-10000 断点**（仅 p=-100 软候选出现 3 处，均未被采纳为页断），无空栏页复发。

## 三、题号列恒空（精修要求①）

**规则**：悬挂题号 7mm 窄列内禁放任何内容；**图/表/答案行**一律从题号右缘（栏左＋7mm）起排，逐页核验出数字。范围仅此三类（选项/①段不在范围，保持顶格对齐全品）；T0 章首导航表在 multicols 外通栏、无题号语境，不适用并登记豁免。

**实现**（postproc_v2.py）：
- step 12 独立图：`\penalty10000\noindent\hspace*{7mm}\makebox[\dimexpr\linewidth-7mm\relax][c]{IMG}\par\penalty10000`；**image5 由行内改独立**（行内图行首落位不定、x0 无法断言；改置计数登记于 log 12）
- step 14 正文表：`\noindent\hspace*{7mm}`＋tabular＋`\par`（弃 center 环境包裹）
- step 10 答案行：`\noindent\hangindent=7mm\hangafter=0\biaoqian{【答案】}…`（hangafter=0＝全行缩进）

**连锁列宽收缩**（表从栏左＋7mm 起排后必须 ≤79.25mm）：正文 5 表内容宽度收缩（T1 13/27/32、T2 22/52、T3 15/26/31、T4 18/56、T5 16/58，单位 mm），n=3 合计 78.91mm、n=2 合计 78.65mm，＋7mm 后 ≤85.91 ≤ 栏宽 86.25mm，逐表算术登记于 log 5-N。T0 通栏表 166mm 不缩。

**断言**（新增 `断言题号列.py`，PyMuPDF）：
- 口径：栏左 42.52pt，阈值 x0 ≥ 61.86pt（栏左＋7mm−0.5pt，登记口径 61.9）；右栏同理 +265.75pt；
- 登记排除项（探针实证，均不在三类范围）：multicol 栏线（stroke 中心＝栏中缝 297.64pt）、`\zutit` 探究点黑条 `\rule{2.25pt}{13pt}`（顶格，组标题元素）、T0 最左竖线 ×21（通栏豁免）；
- **答案行墨迹口径**：SimHei 的【左半空、xeCJK 行首压缩后 char origin 比 ink 左偏 0.56em（origin/bbox 均伪报 56.48pt）；600dpi 像素实测墨迹左缘 62.44pt ≥ 阈 62.36pt → 锚定行按 300dpi 像素墨迹左缘认定；续行由 `\hangafter=0` 结构保证（p4 实测 62.36pt）；
- **终版出数：逐页「图/表线/答案行检查数」全过、违规数=0；合计图 9/9、表线 112（T0 豁免 21）、答案行 10/10，违规 0**。

## 四、表头白底黑体加粗（精修要求②）

- postproc step 5：表头行去掉 `\rowcolor{thbg}` 前缀 → **白底**；`\multicolumn{1}{|>{\centering\arraybackslash}p{Wmm}|}` 定宽居中保留（修 T1 col2 撑宽的方案不变）；黑体加粗不变；全框 0.4pt 横竖线不变；T3/T4/T5 无表头行、首列黑体不变；
- `colortbl` 宏包与 `thbg` 色定义随之从 main_v2.tex 移除（唯一用户是 `\rowcolor`）；
- log 5-1/5-2/5-3 改记「白底黑体加粗＋\multicolumn 定宽」。

## 五、v2 结构增补登记（上轮定案，集中列表）

**图档位表（9 张）**：

| 图 | 档位 | 放置 |
|----|------|------|
| sub3_B_1.png / sub3_B_2.png | 30mm | T3 加法表内（multirow 格） |
| sub3_B_3.png | 45mm | T5 图示表内（multirow 格） |
| sub3_B_4.png | 45mm | 独立（投影三联图①②③） |
| image1.png～image4.png | 30mm | 独立（直三棱柱/正方体AE/正方体BC₁AC/二面角） |
| image5.png | 30mm | 独立（折叠矩形；v2.1 行内→独立） |

**知识点 3 块**（讲部 9 条目聚类，块内条目源序不动）：◆知识点一 空间向量的概念←条目1～3；◆知识点二 空间向量的线性运算←条目4～5；◆知识点三 空间向量的夹角、数量积与共面←条目6～9。

**探究点九组**（题部题型组挂号，演示性改动）：探究点一～九 ← 1.1.1.2～1.1.1.10；讲部组 1.1.1.1 保持原名。

**multirow {=} 源码结论**：`{=}` 路径展开为 `\strut#6\strut\par`——格内外包 `{\centering…\par}` 会多出一空行 → Overfull \vbox；水平居中由 `\multirowsetup{\centering}` 承担；垂直修正 `MROW_VMOVE='0pt'`（scan_vmove.py 实测定值：0pt 时 Overfull \vbox=0 且图顶低于顶线 4.4/3.8pt；6/8pt 图上浮越线 1.6/3.6pt 弃）。scan_vmove.py 为一次性定值工具（会重写 postproc_v2.py），定值已并入 postproc，不再运行。

**详解C 溯源链**（1.1.1.6-5）：multicol 进入时把 `\emergencystretch` 重置为默认 8pt（`\typeout` 实测）→ 巨型行内公式在 `\left\right` 密集嵌套处无自动断点（\tracingparagraphs 实证全式仅 2 个候选）→ 首行 29.68pt overfull 且与 tolerance/emergencystretch 取值无关 → 修复＝postproc 11b 在顶层 `=`、· 后注入 `\allowbreak` ×26（纯惩罚点零字形增删）＋ multicols 内重设 `\emergencystretch=8em` → 松行替代 overfull，Overfull 清零。

**表格随行放置**：`table[!t]` 浮动在 multicol 下被无限推迟、全篇丢失（实测废弃）→ 5 张正文表全部随行放置；T0 通栏不浮动。

## 六、终版构建与验证数字

- 链：`python postproc_v2.py`（log 43 行）→ `xelatex main_v2.tex` ×2 → 统计 → `python render_v2.py` → 逐页目验 9 页 → `python 断言题号列.py`
- **errors=0；Overfull=0；Underfull=6（badness 10000×3、6364、6078、10000，数学长式松行，行号 116/190/243×2/245/301）；Missing character=0；9 页**；fancyhdr footskip 告警 1 条（无害，v1 已知）
- 断言：**图 9/9、表线 112（T0 豁免 21）、答案行 10/10、违规 0**
- 逐页目验（终版 PNG 全 9 页）：p1 章标题/统计行/T0 白底表头/节小节标题/本节统计；p2 T1/T2；p3 T3/运算律/T5＋表内图；p4～p8 正文双栏满排、答案行/独立图 7mm 起排；p9 末页双栏平衡收尾。p5 双栏满、探究点三顺排，空栏页未复发。

## 七、可再迭代项（如实登记）

1. `\glueguard` 为 best effort：-100 软断点不保证组标题/题号在任何内容分布下都不孤悬（当前 9 页无实例；若未来章出现，可加大 N 或回退逐案处理）
2. 答案行断言必须用**墨迹口径**：换 bbox/origin 口径会因 SimHei【＋xeCJK 行首压缩伪报 -5.88pt（断言脚本已内置登记）
3. 表格仍不可跨栏断（tabular 天性）；列宽收缩后 T1 col1 四字标签（研究范围等）换行仍在（对齐全品原状，接受）
4. p5 左栏底 ~180pt 留白：题块完整性绑定（1.1.1.4-2 整块移右栏）所致，与全品行为一致，未强排
5. image5 行内→独立后，【详解】标签独占一行（源文该图紧随标签）；如不接受可回改行内，但该图 x0 即不可断言
6. Underfull 6 处为数学长式松行（详解C 链的伴生代价），已登记，不影响验收

## 八、输出路径清单（均在 `工作区/全品结构提取/数学选必一/样张v2-latex/`）

- `postproc_v2.py`＋`postproc_v2_log.txt`（43 行变换登记）→ `chapterhead_v2.tex`/`body_v2.tex`
- `main_v2.tex`（v2 模板：multicol＋\glueguard＋白底表头注释链）→ `main_v2.pdf`（9 页）
- `断言题号列.py`（题号列恒空逐页断言）｜`render_v2.py`→`png_v2/p01…p09.png`（150dpi）
- `main_v2.log`（终版权威统计来源）｜v1 全套文件未动

## 九、结论

**v2 收尾三项全部落地并出数**：p5 空栏页根因（needspace 强制断点 × multicol 整页收集＝页级跳栏）单变量实验定罪并以 `\glueguard` 定案；题号列恒空（图/表/答案行 7mm 起排）逐页断言违规 0；表头白底黑体加粗全表生效。终版 9 页、0 错误、0 overfull、缺字 0。LaTeX 轨 v2 可作为 v2 主后端候选提交主会话核验。
