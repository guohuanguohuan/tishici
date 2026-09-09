# 片D 报告（0909c 修复轮 · 变式标签双字重 · 意见#33）

交付件：`工作区/字替对照-0909/variantF/main.pdf`（7 页，未变）。改动全落源码层，`body.tex` 未手改（postproc 重跑后与基线**逐字节一致**，0 diff）。

## 一、改动文件清单（行号）

| 文件 | 行号 | 内容 |
|---|---|---|
| `variantF/qp-fonts.tex` | :19-22 | 文件头新增「F 片D 0909c」⑥ 段（双字重依据） |
| | :92-93 | `\libian` w400 注释改「退役备查」 |
| | :101-110 | 新族挂载区：`libianb`＝FY-w700BEVL100、`libians`＝FY-w450BEVL100、`\libianslat`＝FY-w450（西文/数字） |
| | :131-133 | 访问宏 `\libianb` / `\libians` |
| `variantF/qp-blocks.tex` | :120 | 注释更新（例N 维持 \li；变式走 \liB 双字重） |
| | :125-130 | `\liB` 拆两段：`\def\liBsplit#1#2\liBstop{{\libianb #1}{\libians\libianslat #2}}`＋`\liB` 新形 |
| `variantF/postproc_daoxue.py` | :714 | 发射注释更新（不改编排逻辑，emission 字面不变） |
| | :1060 | 第 8 步日志文案更新（w400→双字重） |
| `variantF/_测v4断言.py` | :56-59 | 文件头「F 片D 0909c 适配」块（旧→新登记） |
| | :661-663 | ⑲ `li_ok` 锁新宏形＋`\def\liBsplit` |
| | :701-705 | ⑲ reg 文案 |
| | :1151-1189 | ① 密度拆双集（变/式）＋check 新窗＋两条 reg |
| `variantF/fonts/FY-w700BEVL100.ttf` | 新 | 字体实例（gitignore 已挡） |
| `variantF/fonts/FY-w450BEVL100.ttf` | 新 | 字体实例 |
| `variantF/fonts/FY-w500BEVL100.ttf` | 新 | 标定候选（w450 胜出，未挂载，保留备查） |

## 二、字体实例化参数与 MD5

源：`fonts/候选字体/AlimamaFangYuanTi-VF.ttf`（fvar：wght 200–700，default 700；BEVL 1–100，default 100）。
命令（fontTools 4.63.0）：`python -m fontTools.varLib.instancer <VF> wght=<W> BEVL=100 -o <out>`。

| 文件 | 参数 | 产物核验 | 大小 | MD5 |
|---|---|---|---|---|
| FY-w700BEVL100.ttf | wght=700 BEVL=100 | fvar=False，usWeightClass=700 | 2,616,096 B | `5188da55f7ec4148f4b418000d8cbea8` |
| FY-w450BEVL100.ttf | wght=450 BEVL=100 | fvar=False，usWeightClass=450 | 2,631,732 B | `d841d05a5f6b8f687cb68acfb95becb0` |
| FY-w500BEVL100.ttf | wght=500 BEVL=100 | fvar=False，usWeightClass=500 | 2,628,684 B | `ca8babf56870753525364166bb39b60d` |

PDF 内嵌核验（extract_font→OS/2）：`usWeightClass=700`（变）／`450`（式+数字）／`600`（例N \lihei，未动）三档同时在嵌。
日志字体轨迹（main.log:1318 等 9 处）：`\TU/FY-w700BEVL100…变 \TU/FY-w450BEVL100(1)…式 \TU/FY-w450BEVL100(0)/b/n…1`——数字 `\textbf` 的 b/n 未定义回落同族 m/n（w450），与改前 w400 机制同。

## 三、三 0 对比（xelatex 两遍）与页数

| 指标 | 基线 | 改后 |
|---|---|---|
| error `^! ` | 0 | 0 |
| Overfull | 0 | 0 |
| Missing character | 0 | 0 |
| Underfull（登记项） | 31 | 31 |
| LaTeX Font Warning / Font shape undefined | 3 / 2 | 3 / 2 |
| 页数 | 7 | **7（不变）** |

## 四、断言适配登记（旧→新）

| 断言 | 旧 | 新 | 实测 |
|---|---|---|---|
| ⑲ `li_ok` | 锁 `\noindent{\fontsize{12.03pt}{15pt}\selectfont\libian\libianlat #1}%` | 锁 `\noindent{…\liBsplit#1\liBstop}%`＋`\def\liBsplit#1#2\liBstop{{\libianb #1}{\libians\libianslat #2}}` | 在 |
| ① 变式密度 | 单集 `var_ratio ≤1.75`（w400「常规反向」） | 双集：变（特黑）`2.2–3.2`／式（中黑）`≤1.75` | 变 2.68（n=9）／式 1.33（n=9） |
| ⑲ reg、① 两条 reg、文件头适配块、postproc 日志文案 | 提及 w400 | 同步改双字重 | — |

未受影响（维持绿）：⑥ 计数 变式1 9/9、⑲ 字号档 12pt 标签 例9/变9、⑪ 隙距 2.7/2.2、⑫ \zhenti6/\jiexi14 等。
**双绿**：`_测v4断言.py` 全部通过（rc=0）；`断言顶格.py` 通过（rc=0，签名行 127/违规 0）。

## 五、「变/式」笔画实测（360dpi＝14.1732px/mm 页图尺，二值众数＋AA积分中位；n=9 标签中位）

| 字 | 改前 | 改后 | 全品 p06 左 | 全品 p06 右 | 目标 | 判定 |
|---|---|---|---|---|---|---|
| **变** | 3.86px（mode 4，0.064em） | **7.08px（mode 8，0.118em）** | 8.73px（0.145em） | 9.34px（0.155em） | 7.5±1px | ✓ 窗内（Δ−1.65 vs 左） |
| **式** | 3.85px（mode 4） | **4.39px（mode 5，0.073em）** | 4.50px（0.075em） | 4.51px | 4.5±0.5px | ✓（Δ−0.11） |
| 1（数字） | 4.21px | 4.86px（mode 5） | —（p06 标签为「变式」＋后随(1)，无粘连数字） | — | — | 登记 |

600dpi 高倍：变 11.78px（→360 口径 7.07）／式 7.29px（→360 口径 4.37）／1 8.10px。
墨色：标签 span color=#000000，墨 min_gray=0（纯黑，改前亦纯黑）。
位置/基线：x0=310.75/49.82、origin.y 逐条与改前一致（≤0.01pt）；标签 advance 32.41→32.48pt（+0.07pt），后随 span x 同步 +0.07pt。
间隙：标签 span 右缘→题侧 span 左缘＝**2.700mm 恒定**（\hspace 未动）；墨级隙 3.556→3.598mm（+0.04mm，数字墨形微差）。

## 六、裁片（均落 `_tmp取证0909c/片D/`）

- `片D_变式双字重_同尺对比板.png`——全品 p06 左/右 真迹＋我方改前/改后，360dpi 同尺 ×3，逐格标注笔画值。
- `片D_变式双字重_600dpi高倍.png`——我方改后 600dpi vs 全品 p06 左 ×1.67 同尺。
- `片D_变式双字重_笔画标注_600dpi.png`——逐字墨框＋竖笔实测标注。
- `片D_p3_标签上下文_150dpi.png`——p3 标签在版面上文上下文。
- 数据/日志：`verify_result.json`、`verify.log`、`probe_result.json`、`probe.log`、`inst.log`、`board.log`。
- 基线快照：`基线_body.tex / 基线_main.log / 基线_main.pdf / 基线_postproc_daoxue.py / 基线_qp-*.tex / 基线__测v4断言.py / 基线_断言顶格.py`。
- 脚本：`inst.py`（实例化）、`probe.py`（标定探针）、`verify.py`（同尺实测）、`board.py`（裁片）。

## 七、遗留风险

1. 「变」7.08px 落在主目标 7.5±1px 窗内，但低于任务注记 0.13–0.16em 下沿（0.118em）——根因 VF wght 上限 700 已封顶；对全品 8.7px 差 −1.65px（较例N −1px 略大，登记）。再贴 0.145em 需换族（NSC-w850，失圆角）或 FakeBold（E 轮已否决形变）。
2. 数字「1」4.86px 略重于「式」——字形固有（1 的竖笔/字宽比大）；任务口径「式＋数字」同升 w450–500 已按令执行；全品 p06 无同构样本可比（其标签为「变式」＋后随 (1)），登记不设门。
3. FY-w500BEVL100.ttf 未挂载（w450 实测 4.39px 贴 4.5px 胜出，w500 4.91px）；保留备查。
4. `\libian/\libianlat`（w400）挂载保留、\liB 不再引用（退役备查，断言⑲已锁新形）。
5. 未碰：`交付报告F.md`、附则、总控、看板、git。字体二进制不入 git（沿 F 轮纪律）。
