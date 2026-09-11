# 物理样张骨架 0911 —— 使用说明（供 6 个试点件并行代理零猜测引用）

产出轮＝2026-09-11 物理样张线·骨架搭建。骨架目录＝`工作区/物理样张0911/骨架/`。
继承基准＝数学 L1（M1 样式冻结，进度看板 L54；源族＝`工作区/字替对照-0909/variantF/` ＋
`工作区/字替对照-0909/靠齐样张-0910/{测评卷,练习线,答案册}/`）；样式口径＝`附则/全品基准总表.md`
（§一总表＋§三 答案制拍板A／答案册件条款／品牌位）；试点依据＝`工作区/物理样张0911/立项盘点.md` §三。

## 一、文件清单与继承关系

| 文件 | 性质 | 来源/口径 |
|---|---|---|
| `qp-fonts.tex` | 零参数继承 | 源＝靠齐样张-0910/测评卷 同名件（源 md5 a2e5cfd1…，字体绝对路径版）；字体二进制仍指 variantF/fonts/，不复制 |
| `qp-layout.tex` | 零参数继承 | 源＝数学 L1 同名件（源 md5 77766069…，三向一致）；A4 双栏版心全参数（下表） |
| `qp-parts.tex` | 继承＋尾增段 | 源＝数学 L1 同名件（源 md5 ca28db7d…）＋尾部新增 **TW-RD 读数刻度图显示宽档**（已拍板：下限 50mm、不足放宽通栏 84mm——2026-09-11 用户批，已升《全品零件库》TW-RD） |
| `qp-titles.tex` | 零参数继承 | 源＝数学 L1 同名件（源 md5 edf1c99c…）；字号梯子 章20.67/节16.88/小节15.1/课时13.0pt |
| `qp-blocks.tex` | 零参数继承 | 源＝variantF 同名件（源 md5 3279de92…，含 0911 全品对齐 \zhentib，比靠齐样张拷贝新 10 行） |
| `qp-figs.tex` | **物理新设** | 图族＝源位图引用宏包（\qpfig/\qpfigpair/\qpfigtrio/\qpfigrd/\qpfigopt）＋硬闸＋单位正体/矢量小挂（C4） |
| `qp-phy-params.tex` | **物理新设** | 件型参数单点件（学科/册名/版权标/件型词/章名/卷名/品牌/开关），由两族 headfoot 自动装载 |
| `qp-headfoot.tex` | **物理化重写** | 页脚机制 100% 承数学 L1（md5 b19b7191…），字串物理化＋三形制切换宏（见 §四） |
| `qp-answ-fonts/layout/blocks.tex` | 零参数继承 | 源＝靠齐样张-0910/答案册 同名件（源 md5 13967113…/64837512…/c6025f1b…） |
| `qp-answ-headfoot.tex` | 物理化改件 | 几何/裁5 页码块（31.0mm 出血）零改动；参数改走 qp-phy-params，件名固定「参考答案」 |
| `render.py` | 工具 | pdf→png；默认 300dpi（数学 L1 各件 render 为 150dpi，物理样张线按任务书提档） |
| `figs/` | 试样素材 | 光路-彩色源图.png／光路-灰度化版.png／读数-刻度图.png（自 docx 源位图提取，出处见 试样/main.tex 头注） |
| `smoke/` `smoke-answ/` `试样/` | 验证页 | 各自 main.tex＋png/ 成品；三 0 读数见 §六 |

**版心全参数（继承冻结，件侧勿改）**：左右 margin 17.2mm、top 19.6mm、bottom 20mm、twoside、
无页眉；栏宽 84.0mm、栏距 7.6mm、栏线 0.4pt black!26（答案册族）/black!40（正文族，随 variantF 现档）；
正文 10.09pt/18.0pt、字内距 CJKglue 0.10em plus 0.05em、PunctStyle=banjiao；数学＝unicode-math
Termes Math Scale=1.02、脚本比 54/45、\frac→\dfrac；顶格制 \parindent=0pt；页脚灰块 DDDDDD＋
纯黑 \numpnum 10.7pt 数字、块底距页底 11.2mm、出血到纸边。

## 二、装载序（二族二选一，勿混编）

正文族（讲练/实验卷/知识清单/学史切片/测评卷）：

```latex
\documentclass[fontset=none]{ctexart}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-fonts.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-layout.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-parts.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-headfoot.tex}   % 自动装载 qp-phy-params.tex
\input{C:/提示词/工作区/物理样张0911/骨架/qp-titles.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-blocks.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-figs.tex}
```

答案册族（答案制A 的「另册」侧）：

```latex
\documentclass[fontset=none]{ctexart}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-answ-fonts.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-answ-layout.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-parts.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-answ-headfoot.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-answ-blocks.tex}
\input{C:/提示词/工作区/物理样张0911/骨架/qp-figs.tex}
```

- 模块一律**绝对路径** \input（任意 cwd 可编；Path= 值内禁宏纪律同源）。
- 件目录约定：件 main.tex 旁建 `figs/` 放源位图，导言加
  `\graphicspath{{figs/}}`（qp-figs 已含此默认，件图放件目录即可）；跨件共用素材再追加路径。
- 两族宏名重叠（\zhangtitle/\qpzhangming/\anlabel…），一份 main 只装一族。

## 三、件型参数宏（qp-phy-params.tex 单点供给；件侧 `\renewcommand` 覆盖，勿改默认件）

| 宏 | 默认值 | 件侧动作 |
|---|---|---|
| `\qpyxueke` | 高中物理 | 不动 |
| `\qpbuce` | 必修第三册 | **每件必换**（必修第一～三册/选择性必修第一～三册） |
| `\qpbbiao`／`\qpbbiaoS` | 人教版／RJ | 短标 RJ＝物理新默认（数学先例 RJB），总标待拍板，件侧可覆盖 |
| `\qpzhangming` | 第11章 电路及其应用 | **每件必换**（页脚奇页章名串） |
| `\qpjianming` | 讲练 | **按件型换**，枚举＝讲练／实验卷／学史切片／知识清单／测评卷（答案册族固定「参考答案」） |
| `\juanname` | 单元素养测评卷（一） | 测评卷件换卷名（YJ-02 页脚前段） |
| `\qppinpai` | 羿郭工作室 | 不动（《全品基准总表》§三品牌位行） |
| `\ifqpbrand` | false（素面） | 测评卷件与封面件 `\qpbrandtrue`；其余件保持 false |

## 四、页脚三形制（qp-headfoot.tex；默认＝形制 A，导言末尾换形制）

| 形制 | 宏 | 用件 | 机制 |
|---|---|---|---|
| A 灰块·导学档 | `\qpFooterBlockDX`（默认已生效） | 章讲练/实验卷/知识清单/学史切片 | 26.2×7.8mm 块出血到纸边；奇页＝章名＋件型词（＋品牌若开）＋块；偶页＝块＋册名 |
| B 灰块·练习册档 | `\qpFooterBlockLX` | 需要 31.0mm 宽块的正文件（默认给答案册族用） | 31.0×7.8mm 块·裁5 裁决出血档，其余同 A |
| C 文字行·测评卷档 | `\qpFootTextRow` | 测评卷（对齐全品 YJ-02，无灰块） | 奇页＝卷名＋件型词＋「卷」＋页码14pt；偶页＝页码＋「卷」＋**品牌位 羿郭工作室**＋学科＋册名＋RJ |

- 形制 C 走 8 开横放三栏时，件 main.tex 二次 `\geometry` 后**必须** `\setlength{\headwidth}{\textwidth}`
  （fancyhdr 首置不随换页型回改——数学测评卷 main 同款坑注）。
- 答案册族页脚由 `qp-answ-headfoot.tex` 自带（形制 B 几何＋「参考答案」件名），不随 §三 `\qpjianming` 换。

## 五、可用宏清单（件侧只列名与用途；细节看各件头注）

**标题（qp-titles，通栏区用）**：`\zhangtitle{章名}` `\jietitle{节名}` `\xiaojietitle{小节名}`
`\keshi{第N课时}` `\mubiaoline`＋`\mubiaomu{序号}{内容}`（【学习目标】块）。
物理映射：章＝册章大标题；节＝「11.3 实验：导体电阻率的测量」；小节＝三级讲标题；课时＝练习分层。

**正文块（qp-blocks，栏内用）**：`\zsd{N}{名}`（◆知识点N）`\tiaomu{N}{内容}`（条目号 2.7×）
`\tiaomuz/\tiaomutail`（拆段条目）`\tjdnr{点序}{名}{例N标签}{题侧}{题干}` `\li{标签}{题侧}{前}{后}`
`\liB{变式N…}` `\duoxuan` `\tieside{}` `\kongbai`（15mm 挖空）`\kongda{值}` `\kongwei`（6.8mm 空档）
`\zhenti{(N)}{题干}{答案}{解析}`（旧制）`\zhentib{(N)}{题干}`（**答案制A 正文形**——行尾只挂空括号（　），
不印答案解析）`\ansline/\jiexi`（**仅答案册/内部稿用，成品正文禁**）`\bindopt/\bindp` `\bindopt` 选项绑定、
`\glueguard{N}` 防孤悬、`\gou`（√）`\cha`（×）`\huaxing{四}{字}{说}{明}{右灰词}`（花形栏目行，物理件型可借用）。
选项行排法随件（数学测评卷 \optline/\optII/\optIV 为件型层宏，试点件按需在 main 自建并登记）。

**图族（qp-figs，两族共用；红线＝源位图 only）**：

| 宏 | 形制 | 档位 |
|---|---|---|
| `\qpfig{file}`／`\qpfig[宽mm]{file}` | 题下居中独立段（默认 32mm） | TW-02 27.7–36mm；上距 2.8/下距 2.2mm |
| `\qpfigpair{甲图}{乙图}`／`[每张宽]` | 并排双图＋(甲)(乙) 子标（默认每张 22mm） | TW-03 18–24mm |
| `\qpfigtrio[每张宽]{甲}{乙}{丙}` | 并排三图（默认 18mm） | TW-03 |
| `\qpfigrd{file}`／`[宽mm]` | **读数刻度图**（默认走 TW-RD `\qpRDWdef`＝50mm 拍板终值；低于下限编译告警；不足放宽通栏84mm） | 30/40/50 候选见试样页 |
| `\qpfigopt{宽mm}{file}` | 选项行内小图（行内直排） | TW-04 9–13mm |
| `\qpfigsetw{mm}` | 宽度硬闸检查（>84.0mm 出 QP-FIGS 告警） | 硬闸 |

子标 (甲)(乙)＝宋体 7.5pt 级居中图下（物理新设 v1，试点目验后定档）；题干引用「如图甲」与子标
对账属件侧文案纪律。**图名可带连字符与中文**；`\graphicspath` 命中即可省扩展名。

**物理量小挂（qp-figs 尾段，C4）**：`\unit{V}`（单位正体，数学模式）、`\vect{F}`（矢量箭头）、
`\powten{-3}`（×10ⁿ）。**坑规**：单位里希腊字母走直立族 `\unit{1.0\upOmega}`、`\unit{\upmu m}`——
unicode-math 下裸 `\Omega` 发 \symbb（U+1D6FA 缺字，smoke 实证）。

**答案册块（qp-answ-blocks）**：`\qufen{组名}{说明}` `\kdhead{标题}{说明}`（知识点居中式）
`\ansitem{题号}{答案值}` `\ansline{标签}{内容}`（[分析]/[详解]/[点睛]）`\ansfig{内容}`（题下居中挂）。
层级缩进 5.0mm（\qpind）与对号断言口径随《全品基准总表》§三答案册件条款。

## 六、编译与目验（每件标准工序）

```bash
cd 件目录
xelatex -interaction=nonstopmode main.tex   # 第 1 遍
xelatex -interaction=nonstopmode main.tex   # 第 2 遍（页脚/引用稳定）
# 三 0 判据（全 0 才过门）：
grep -c '^!' main.log                        # error＝0
grep -c 'Overfull' main.log                  # overfull＝0
grep -c 'Missing character' main.log         # 缺字＝0
# 目验渲染（300dpi）：
python C:/提示词/工作区/物理样张0911/骨架/render.py . main 300   # → png/pageN.png
```

- 三 0 口径＝《全品基准总表》§断言禁则「编译三 0」行；`Missing character` 行是 xelatex 缺字唯一出口。
- 图族告警看 `QP-FIGS`（log 与终端都出）：出现即回档缩宽或登记例外，不得带告警交付。
- 多页件双跑后若页码引用未稳，可三跑（三跑仍三 0）。

**本轮骨架自验读数（2026-09-11，双跑）**：

| 页 | error | overfull | 缺字 | 成品 |
|---|---|---|---|---|
| `smoke/`（正文族） | 0 | 0 | 0 | `smoke/png/page1.png`（300dpi） |
| `smoke-answ/`（答案册族） | 0 | 0 | 0 | `smoke-answ/png/page1.png`（300dpi） |
| `试样/`（拍板页） | 0 | 0 | 0 | `试样/png/page1.png`（300dpi） |

## 七、六个试点件 → 骨架用法映射（立项盘点 §三）

| # | 试点件 | 族/形制 | 关键宏与注意 |
|---|---|---|---|
| 1 | 章讲练件切片（2.1 楞次定律）＋答案册对应切片 | 正文族形制 A（`\qpjianming`＝讲练）；切片＝答案册族 | 三级标题 `\xiaojietitle`；图题双栏回流＝图一律 ≤栏宽 84mm（`\qpfig` 族）；标签行随源件清洗；正文用 `\zhentib` 空括号形（答案制A）；答案切片 `\ansitem/\ansline` 同号对账 |
| 2 | 实验卷切片（11.3 导体电阻率的测量） | 正文族形制 A（`\qpjianming`＝实验卷） | 读数刻度图 `\qpfigrd`（TW-RD 50mm 拍板终值、不足放宽通栏 84mm（2026-09-11 已批））；电路图/实物图＝源位图 `\qpfig`；条目组置首＝`\tiaomu` 序列按源号；数据记录表（B2）＝tabular 骨架继承《表格规范》，空格行高按 BG-03 档 |
| 3 | 知识清单切片（11.4 串并联） | 正文族形制 A（`\qpjianming`＝知识清单） | 灰底填空＝旧制「需背处」灰底 A6A6A6（立项盘点 §1.2）——与答案制A 的关系**未拍板**：试点暂按源制保留印答形制（灰底 A6A6A6：`\definecolor{huidiA6}{gray}{0.651}`＋`\colorbox{huidiA6}{…}`；注意 xcolor 的 gray 模型只收单值，禁写三值式），交付时列待拍板⑤随件上报；对比表 B1＝表骨架＋表内嵌图（单元格 \includegraphics 宽≤列宽） |
| 4 | 物理学史切片件（必修三） | 正文族形制 A（`\qpjianming`＝学史切片） | 五类标签＝`\biaoqian{【必记】}` 系（1.3× 底纹机制借块标签）；灰底标记点同上 `\colorbox`；总览表 B3 继承；全件 0 图——qp-figs 可不装 |
| 5 | 测评卷切片（11 章简单卷题 1-4＋卷首） | 正文族形制 C（`\qpFootTextRow`＋`\qpbrandtrue`） | 卷头 JT-01～06 零件＝照抄数学测评卷 main 件型层（`工作区/字替对照-0909/靠齐样张-0910/测评卷/main.tex` 为模板，丝带角饰「数学」改「物理」、字内距 0.04em 件型档随带）；8 开横放必补 `\setlength{\headwidth}{\textwidth}` |
| 6 | 配页件 1 套（册目录页＋部分封面） | 正文族形制 A/B 按需 | 册目录页承数学 靠齐样张-0910/册目录页 模板＋增「学史切片/实验集训」行型（总控任务 E）；封面品牌＝羿郭工作室（公共规则§11 配页件条款，随成书链封面落） |

## 八、红线与待拍板（骨架级纪律）

1. **图族红线**：一律源位图 `\includegraphics` 引用；**禁矢量化重绘**（TikZ 复刻源图不立项，补绘＝逐图例外登记另批）、**禁 AI 三维图**（三维装置/立体磁场＝源位图，公共规则三维禁重绘令覆盖）。全库 1010png+21jpg 零矢量存量（立项盘点 §5.2-8）。
2. **答案制A**：正文件不印答案/解析（`\ansline/\jiexi/\kongda` 印答形制禁入正文件，判断题走 `\zhentib`）；答案侧＝答案册族另册，同构同号＋对号断言（《全品基准总表》§三）。
3. **品牌位**：默认素面（`\ifqpbrand` false）；只测评卷页脚品牌位＋封面/部分封面落「羿郭工作室」；余件勿开。
4. **禁 git**；改骨架＝回本 README 登记；数学侧 L1 后续改动**不随动**（M1 冻结快照口径）。
5. **待拍板（用户/主脑）**：①A3 彩色源位图是否灰度化——`试样/png/page1.png` 上半对照；②A2 读数图显示宽下限＝**已拍板 50mm、不足放宽通栏 84mm**（2026-09-11 用户批，已回填 `qp-parts.tex` 并升《全品零件库》TW-RD）；①A3 彩色源位图＝**已批原样保留**（纯灰断言豁免入公共规则§7）；③物理版权短标 RJ（默认）/RJA/其他；④(甲)(乙) 子标 7.5pt 档目验定档；⑤知识清单灰底填空与答案制A 的关系（骨架不擅自豁免也不擅自去答，试点按源制保留＋上报，见 §七-3）。
6. **已踩坑登记（件侧勿复发）**：`\unit{…\Omega}` 缺字→`\upOmega`（§五）；`\hbox` 内 `\vtop` 的 `\centerline` 按外层 `\hsize` 铺盒→`\vtop` 内局部 `\hsize`（qp-figs 已修，件侧自建并排盒同法）；fancyhdr `\headwidth` 不随二次 `\geometry`（§四-C）；`\qpYJbNumSize` 等零件宏已在 qp-parts 注册，件侧/模块侧勿重复 `\newcommand`。

## 九、素材与探针出处（可复验）

- `figs/光路-彩色源图.png`＝`高中物理/高中物理同步/人教版选必1 第4章 光·中档卷（20题）.docx`→`word/media/image4.png`（1945×892，甲=球体折射照片·乙=光路图带蓝色虚线）。
- `figs/光路-灰度化版.png`＝同图 PIL `convert("L")`（ITU-R 601 亮度）回 RGB，仅判据试样副本。
- `figs/读数-刻度图.png`＝`人教版必修3 第11章 电路及其应用·实验卷（14题3条）.docx`→`word/media/image32.png`（1601×455，20/50分度游标卡尺＋螺旋测微器，题1-2 读数图）。
- 提取脚本与中间探针＝`_probe/`（本轮生成，可删可复跑）。
