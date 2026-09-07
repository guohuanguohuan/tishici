# LaTeX 轨可行性实验报告（样张v2-latex）

日期：2026-09-06　｜　轨位：并行双轨实验之 LaTeX 轨（docx 轨另有人做，未动 `样张v2/`）
源节：人教B版选必1 第1章（上）·讲练件 §章首＋1.1＋1.1.1 全节

## 一、环境

- pandoc 3.10（已有）；TinyTeX TL2026 XeLaTeX（已有，`~/AppData/Roaming/TinyTeX`）
- tlmgr 补装：fancyhdr、indentfirst、tcolorbox、environ、trimspaces、multirow、booktabs（etoolbox/calc 已在）
- 坑：Git Bash 不能直接跑 `tlmgr.bat`，需 `cmd //c tlmgr.bat`；`inspect.py` 命名会遮蔽标准库致 lxml 循环导入

## 二、源节抽取

- 截断点：首个「样式 Heading3 且文本以 1.1.2 起首」段（#167），删至文末、保留 sectPr；另删其前紧邻的 1.1.2 隐藏节名锚（1pt 白字段，不属于任务枚举的保留范围）
- 产出 `1.1.1-源节.docx`：166 段、6 表、9 图引用
- 与任务预估差异：实为 6 表 9 图（任务预估 5 表 6 图）——第 6 表是章首统计表；9 图 = 讲部 4 图＋题图 5。如实保留全部

## 三、pandoc 转换与公式保真（生死关）

转换：`pandoc 1.1.1-源节.docx -o sec.tex --extract-media=media`，OMML→LaTeX 共 **282 条**公式，顺序一一对应（282=282）。

方法：自写 OMML 语义提取器（omml_dump.py）把每条公式还原成"真值"伪 TeX（m:f/m:sSup/m:acc/m:d/m:rad/m:eqArr 全覆盖），与 pandoc 输出逐条对齐；先归一化粗检（257/282 字符级一致），25 条差异逐一人工复核，全部为等价转换（`cos`→`\cos`、`∠`→`\angle`、`⇔`→`\Leftrightarrow`、`{A}'`→`A'`、`\left[`→`\lbrack`）。

### 20 条精选判定（刻意覆盖六类＋全节均匀抽样）

| # | 序号 | 类别 | 源语义 | pandoc TeX（归一化前） | 判定 |
|---|------|------|--------|------------------------|------|
| 1 | 000 | 向量箭头 | a⃗,b⃗,c⃗,⋯ | `\overset{⃑}{a},…` | 保真* |
| 2 | 003 | 模 | \|a⃗\| | `\left\| \overset{⃑}{a} \right\|` | 保真 |
| 3 | 009 | 零向量平行 | 0⃗∥a⃗ | `\overset{⃑}{0} \parallel \overset{⃑}{a}` | 保真 |
| 4 | 040 | 夹角边界 | 0≤⟨a,b⟩≤（跨公式） | `\leq \langle…\rangle \leq` | 保真 |
| 5 | 041 | π 带箭头 | 源本身误加箭头 | `\overset{⃑}{\pi}` | 保真（源缺陷照搬） |
| 6 | 043 | 分数 | π/2 | `\frac{\pi}{2}` | 保真 |
| 7 | 067 | 投影复合式 | \|a\|cos⟨a,b⟩·b⃗/\|b\| | 完整还原 | 保真 |
| 8 | 076 | 撇号上标 | A′ | `A'` | 保真 |
| 9 | 085 | 点对区间 | (x,y) | `(x,y)` | 保真 |
| 10 | 087 | 空基座箭头 | 源中箭头基座为空＋x | `\overrightarrow{}x` | 保真（源缺陷照搬） |
| 11 | 097 | 下标柱体 | ABC−A₁B₁C₁ | `ABC - A_{1}B_{1}C_{1}` | 保真 |
| 12 | 098 | ⃗系箭头等式 | CA⃗=a⃗,… | `\overrightarrow{CA} = \overrightarrow{a},…` | 保真 |
| 13 | 160 | 平方＝模平方 | a⃗²=\|a⃗\|² | 完整还原 | 保真 |
| 14 | 161 | 分式套点积 | a⃗·b⃗/a⃗·a⃗ | `\frac{…}{…}` | 保真 |
| 15 | 188 | 夹角区间 | ⟨BC₁,AC⟩∈[0,π] | `\lbrack 0,\pi\rbrack` | 保真（不伸缩定界符，此处渲染等价） |
| 16 | 199 | 开区间根式 | (−1−√3,−1+√3) | `\left( - 1 - \sqrt{3}, … \right)` | 保真 |
| 17 | 206 | 方程组 | {kλ=1, λ=−2k | `\left\{ \begin{array}{r} … \end{array} \right.\ ` | 保真（尾随空距无视觉影响） |
| 18 | 244 | 嵌套根式 | √(3−√2) | `\sqrt{3 - \sqrt{2}}` | 保真 |
| 19 | 258 | 根式分数 | √10/2 | `\frac{\sqrt{10}}{2}` | 保真 |
| 20 | 280 | 混合展开 | 分式＋括号平方＋× | `\times`/`\left(\right)` | 保真 |

**判定汇总：20/20 保真，0 轻微变形，0 错误；全量 282 条错误率 0。**

注*：源文档用了两种箭头重音字符（U+20D7⃗ 与 U+20D5⃑），pandoc 分别映射为 `\overrightarrow{}` 与 `\overset{⃑}{}`（忠实）；后者字形 Latin Modern 缺失，模板侧归一化为 `\overrightarrow{}`（共 437 处，语义等价）。

## 四、全品式模板复刻度（12 版式点）

| # | 版式点 | 结果 | 说明 |
|---|--------|------|------|
| 1 | XeLaTeX＋ctex，宋体 SimSun＋Times New Roman | 成功 | fontset=none 手工指定；加粗映射 SimHei 免伪粗告警 |
| 2 | A4 四边 15mm＋twocolumn＋columnsep 7.5mm＋0.14mm 浅灰栏线 | 成功 | 栏线颜色需 etoolbox 补丁 `\@outputdblcol`（内核无 \columnseprulecolor） |
| 3 | 正文 10.5pt / baselineskip 18pt | 成功 | `\renewcommand\normalsize` |
| 4 | 章标题 22pt 黑体居中＋通栏 0.4pt 横线 | 成功 | `\twocolumn[\zhangtitle{…}]` 通栏参数 |
| 5 | 节标题 18pt 黑体居中 | 成功 | `\jietitle` |
| 6 | 小节 15pt 黑体居中 | 成功 | `\xiaojietitle` |
| 7 | 题型组 12pt 宋体加粗＋左 2.25pt 黑竖条 | 成功 | `\zutit`，\raisebox\rule，无底纹 |
| 8 | 题号悬挂 7mm | 成功 | `\timu`：\hangindent=7mm \hangafter=1，题号顶格 |
| 9 | 答案行一行式＋【】黑体＋答案值 C7C7C7 灰底 | 成功 | 后处理合并 10 处；\colorbox 内数学正常 |
| 10 | 图三档 30/45/86mm | 成功（含登记偏差） | 独立图 6 幅按原图宽就近分档（45/45/86/86/45/86→实际 45,45,86,86,45 及 86）；表内 3 图改 width=\linewidth 防单元格溢出 |
| 11 | 挖空 \underline{\hspace*{15mm}} | 成功 | 5 处长下划线串替换为 \kongbai |
| 12 | 页眉 9pt 灰字节名／页脚 6.5pt 灰字＋31×7.8mm DDDDDD 灰块页码 | 成功 | fancyhdr 奇偶同式；页脚 tabular[b]＋footskip 6mm 对齐 |
| + | 题块间距 6pt | 成功 | \timu 前 \addvspace{6pt} |
| + | 表格 10.5pt 左对齐 | 近似 | 字号对齐达成；线型为 booktabs 三线，未复刻全品全框线（可后处理加网格线，未做） |

编译：xelatex 两遍零错误；缺字形 0；Overfull \vbox 0（Overfull \hbox 15 处，均为数学长式不换行的装饰性微溢出）。最终 **7 页**（任务预估 4~6 页；因 18pt 行距＋讲部 5 表＋9 图，如实）。

表格断栏难题（LaTeX 轨最大结构性短板）：tabular 不可跨栏断行，大表在栏首溢出会压页脚（LaTeX 不移动栏首大盒子）。解法：正文 5 表转 `table[!t]` 浮动贴栏顶＋\raggedbottom＋浮动参数放宽，版面效果与全品"表格居栏顶"一致；代价是表与正文可能有半栏错位。

## 五、与 docx 轨工程量主观对比

- LaTeX 轨一次性投入：truncate/omml_dump/fidelity/postproc 共约 500 行 Python＋main.tex 约 100 行；转换全自动，模板参数化程度高（字号梯子/间距/栏线一处定义），公式保真是 pandoc 白送的
- 调试轮次：4 轮编译错误（\real 缺 calc、longtable 不支持双栏、LTcaptype 括号残留、栏线颜色）＋2 轮版式迭代（列宽归一化、浮动策略）
- docx 轨：样式映射碎（底纹/边框/页眉域逐个处理）但所见即所得、表格跨页断行天然支持；LaTeX 轨版式一致性和批量化潜力更大，短板集中在表格断栏
- 总耗时：全程约 45 分钟（文件时间戳 20:53→21:38）

## 六、坑清单

1. longtable 在 twocolumn 直接报错 → 转 tabular＋规则线规范化
2. pandoc 列宽 `\real{}` 需 calc 包；占比按 docx 表宽计，双栏内需按合计归一化
3. 内核无 `\columnseprulecolor` → etoolbox 补丁 `\@outputdblcol`
4. `\overset{⃑}` 组合箭头字形缺失 → 归一化 `\overrightarrow`
5. ①②③④∴△ 在 Times 无字形 → `\xeCJKDeclareCharClass` 路由宋体
6. 不可分页大表栏首溢出 → table[!t] 浮动＋\raggedbottom
7. 页脚双行对齐 → tabular[b]＋footskip 6mm
8. pandoc 把 1pt 白字"节名锚"段当正文 → 按渲染语义删除并登记
9. tlmgr 需 `cmd //c tlmgr.bat`；脚本勿命名 inspect.py

## 七、输出路径清单（均在 `工作区/全品结构提取/数学选必一/样张v2-latex/`）

- `1.1.1-源节.docx`（截断后源节）｜`truncate.py`｜`probe_docx.py`/`probe2.py`（结构探查）
- `sec.tex`（pandoc 原始输出）｜`media/media/*.png`（9 图）
- `formulas.json`（282 条真值+pandoc 对照）｜`omml_dump.py`｜`fidelity.py`
- `postproc.py`＋`postproc_log.txt`（变换登记）｜`chapterhead.tex`｜`body.tex`
- `main.tex`（全品式模板）｜`main.pdf`（7 页）｜`png/p01.png…p07.png`（150dpi）

## 八、结论

**建议：LaTeX 轨可以担 v2 主后端（有条件）。**
依据：① 生死关（OMML→TeX 保真）以 0/282 错误通过，含向量箭头、分数、上下标、绝对值、区间、方程组全类目，连源文档的箭头瑕疵都原样保真；② 12 个版式点 11 成功 1 近似（表格线型），页码灰块、栏线、悬挂、三档图等硬指标全部达成；③ 版式全参数化，批量套章可行。
条件：接受"正文大表格浮动栏顶放置"这一排版策略（或后续引入 supertabular 做真断栏）；表格全框线如为硬需求需在模板层补网格线规则。若 v2 把"表格严格随文＋跨栏断行"列为不可妥协项，则该单项 docx 轨占优，可考虑混合：正文与公式走 LaTeX、大表走 docx——不建议，双后端维护成本更高。
