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
