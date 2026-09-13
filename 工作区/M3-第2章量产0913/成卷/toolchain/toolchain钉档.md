# M3 toolchain 迁入钉档（S2 开工预备轮，2026-09-14 凌晨）

- 执行：M3 成卷轮 S2 开工预备代理｜写前核 mode＝auto｜红线执行：零 git（全程未运行任何 git 命令）；写入仅 `成卷/toolchain/`＋`工作区/_tmpM3S2预备0913/`；源目录 `_tmpM3toolchain0913/`、题面库、定稿、命制全程只读。

## 一、迁入记录（换装三裁②本地挂载口径）

| 项 | 值 |
|---|---|
| 源（只读） | `工作区/_tmpM3toolchain0913/qp-m3.sty`（33157 B） |
| 迁入位（正装挂载位） | `工作区/M3-第2章量产0913/成卷/toolchain/qp-m3.sty` |
| md5（源＝迁入） | `c8a5b7e0a7b359d5712e98a1b1a2d2db` 两侧全等 |
| 装载口径 | 件内一律 `\usepackage{qp-m3}` 裸名本地挂载（sty cp 到件目录同层）；**禁绝对路径**——kpathsea 不认中文路径（换装方案草案·正装三裁②） |
| 编译器 | TinyTeX xelatex（`C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex`），每档连编两遍取稳态 |

## 二、冒烟复验读数（迁入位，`toolchain/冒烟0914/`，2026-09-14）

体＝源 `dummy.tex` 单源零改＋双壳（dummy-true.tex＝`\mthreepure{0}`／dummy-false.tex＝`\mthreepure{1}`）；sty 本地挂载进冒烟目录后编译，cwd＝冒烟目录（中文路径实跑通过）。四编（双档×两遍）全 exit=0。

| 项 | dummy-true（含详解印本档） | dummy-false（纯题档） |
|---|---|---|
| Error / Overfull / Underfull / Missing character | 0/0/0/0 | 0/0/0/0 |
| 页数 | **4** | **3**（≤true，纯题开关生效版面实证） |
| M3-ANSKEY 发射 | 27 | 27（两档键清单 diff=0，对号门两档可跑） |

- 与源冒烟报告（`_tmpM3toolchain0913/冒烟报告.md` §二）逐项全同：**迁入零漂移成立**。
- 留证：`冒烟0914/dummy-true.pdf／dummy-false.pdf＋双 log＋aux＋_true*/_false*.out`（四编全程捕获）。

## 三、量产纪律（承接源冒烟报告 §三遗留＋试迁四报告，详见 `工作区/_tmpM3S2预备0913/S2波次方案.md`）

1. 灰底块不可跨栏断：长详解（估高＞8 行）一律括线模（承重墙口径）；`\columnbreak` 是逃生口禁常态。
2. ketang 顺排量产制；ketangboxed 禁用；课堂评价禁 `\vbox` 装栏。
3. `\tailfill` 置 `\end{multicols}` 前；无参在平衡栏呈「内容尾随框」，贴栏底须定高参——挂装配轮裁；`\iftailfillused` 制断言（v0.1 无 M3-TAILFILL typeout，以渲染面证据代，禁改 sty 破 md5）。
4. 括线块跨栏切分＝起线/收线段式自洽（试迁实证 3 处）；anskey 允许重复发射，对号门对集合不对数＋按需去重。

## 四、两钉落盘钉版行（2026-09-14 实修轮，追记）

- 写前核 mode＝auto｜红线执行：零 git；写入仅 qp-m3.sty 三副本＋本钉档＋`冒烟0914/` 常驻探针＋`工作区/_tmpM3两钉实修0914/`；题面库/定稿层/换装正件（M2/P1）全程只读（副本树仅沙箱复编对照，未落一笔）。

| 项 | 值 |
|---|---|
| 钉版 | 两钉落盘版：补丁① `\setlength{\extrarowheight}{1.7mm}` 插 :162 `\arrayrulewidth` 之后；补丁② `\parallel` TikZ 复刻由 :105 `\AtBeginDocument` 改挂 `\AddToHook{begindocument/end}`（:104-108 整块替换）；钉③三栏 linewidth 照补丁方案 §四——主落点＝件面 `\jpcol` 补 `\setlength\linewidth{\jpcolw}` 2 行，sty 侧观望位（`\ansruled*/\ansgrayopen/\tailfill` 改取宽）不采纳、登记待裁，sty 本轮不动 |
| 母本 | `工作区/_tmpM3两钉预研0913/负测/patch/qp-m3.sty`（13 项负测断言全过，`_负测门.py` exit 0） |
| md5（四侧全等） | `7c3930362be8a0a2bdf21bbf8ac16573`（母本＝`成卷/toolchain/`＝`_tmpM3toolchain0913/`＝`成卷/toolchain/冒烟0914/`） |
| 前版 md5 | `c8a5b7e0a7b359d5712e98a1b1a2d2db`（三副本落钉前复核一致，被本版整替） |
| kernel 依赖 | `\AddToHook` 需 LaTeX ≥2020-10-01（TinyTeX xelatex 实测通过）；老发行版回退＝件面导言末 top-level 再注册（补丁方案 §三保底） |
| 出证 | `工作区/_tmpM3两钉实修0914/出战重现报告.md`（旧病复现→钉后病愈双截图/读数＋对照件像素复编） |

## 五、钉后复跑读数（2026-09-14 实修轮，追记）

| 门 | 读数 | 判定 |
|---|---|---|
| 冒烟四编三零（`冒烟0914/`，钉版 sty） | dummy-true/dummy-false 各两遍：error=0／Overfull=0／Missing character=0；页数 4/3（与钉前基线恒等）；M3-ANSKEY 27/27 两档恒等 | 全绿 |
| 常驻探针（新增两件，M2 两案各一） | `探针-速查表.tex`：`M3-EH-VALUE: 4.83694pt`＋`M3-TAB-HT: 27.26637pt`（两遍同）；`探针-平行框.tex`：`M3-PAR-BEGINDOCEND:`／`M3-PAR-BODY:` 两阶段 `\meaning` 均 TikZ（两遍同） | 全绿 |
| 换装硬门（M2 副本树测评本对照件复编，零件面补钉） | 测评卷 3 页＋滚A 2 页＋滚B 2 页＝**7/7 页 0.0000%**（`工具/视觉回归.py` tol=0，钉前病页 0.3552%/0.0743%/0.3046%/0.2875% 全归零） | 达成 |
| 题面库对号门 strict（21 片冻结片内容口径重核） | 21 片 552 键全集断言相等零缺漏，exit 0 | 全绿 |
| 负测门（`_负测门.py`，钉后终检） | 13/13 断言 PASS，exit 0 | 全绿 |
| md5 三副本＋母本 | 四侧全等 `7c3930362be8a0a2bdf21bbf8ac16573`（落钉后复查） | 一致 |

出证全文＝`工作区/_tmpM3两钉实修0914/出战重现报告.md`（§一负测双档读数、§二速查表、§三十框位、§四括线、§五像素门、§六冒烟＋探针、§七对号门；截图三张在其 `截图/`）。
