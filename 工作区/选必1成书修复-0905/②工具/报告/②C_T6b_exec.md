# ②C T6b 正式执行报告 — 撤 C6D4E3＋挂左竖条（single sz=18 space=3 auto）

- 时点：2026-09-05 18:33:07
- 工具：`工具\底纹批量器.py --only b`
- 对象：`②工具\副本\` 十件（T6a 已执行态；起点＝同步盘 ②-B 回写终态）
- 基线：`②工具对账.md` §二 T6b 行＝0／5／59／76／0／8／76／73／56／74 段
- 互斥纪律（②工具对账.md §四.3）：T3/T4 以 C6D4E3 识别题型标题，必须先于 T6b。②-B 已执行 T3/T4；本阶段执行前以 T3/T4 dry 复核十件 **0 改写**（20/20 PASS，证据 `②C_T3T4dry_前置复核.md`），证明识别口径未受 T6b 影响、无遗留工作面。

## 一、五道关逐件结果

| 件 | C6D4E3 前→后 | 撤＋挂段数（基线） | 计数断言 | 跳过非标题 | ADC2DA 前→后 | ADC2DA 守恒 | 规格左竖条 前→后 | 既有非规格左框 前→后 | 幂等 dry | 文本守恒 strict/norm | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 清单1 | 0→0 | 0（0） | PASS | 0 | 11→11 | PASS（工具内断言 PASS） | 0→0（应＋0）PASS | 45→45 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 衔接1(29) | 5→0 | 5（5） | PASS | 0 | 3→3 | PASS（工具内断言 PASS） | 0→5（应＋5）PASS | 0→0 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 上(61) | 59→0 | 59（59） | PASS | 0 | 10→10 | PASS（工具内断言 PASS） | 0→59（应＋59）PASS | 27→27 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 下(79) | 76→0 | 76（76） | PASS | 0 | 1→1 | PASS（工具内断言 PASS） | 0→76（应＋76）PASS | 18→18 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 清单2 | 0→0 | 0（0） | PASS | 0 | 21→21 | PASS（工具内断言 PASS） | 0→0（应＋0）PASS | 81→81 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 衔接2(13) | 8→0 | 8（8） | PASS | 0 | 2→2 | PASS（工具内断言 PASS） | 0→8（应＋8）PASS | 0→0 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 92 | 76→0 | 76（76） | PASS | 0 | 11→11 | PASS（工具内断言 PASS） | 0→76（应＋76）PASS | 22→22 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 90 | 73→0 | 73（73） | PASS | 0 | 5→5 | PASS（工具内断言 PASS） | 0→73（应＋73）PASS | 8→8 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 68 | 56→0 | 56（56） | PASS | 0 | 6→6 | PASS（工具内断言 PASS） | 0→56（应＋56）PASS | 24→24 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |
| 89 | 74→0 | 74（74） | PASS | 0 | 1→1 | PASS（工具内断言 PASS） | 0→74（应＋74）PASS | 27→27 PASS | 0 段（跳过 0）PASS | True／True PASS | PASS |

### 断言口径说明

- **规格左竖条**＝`w:pPr/w:pBdr/w:left` 四属性恰为 `val=single`、`sz=18`（＝2.25pt）、`space=3`、`color=auto`；断言「后＝前＋本件撤底纹段数」且「C6D4E3 残留＝0」「跳过非标题＝0」。
- **既有非规格左框**＝源件原有的四边框条目段（`w:pBdr` 四边 top/left/bottom/right 全为 `single sz=4 space=4 auto`，清单/讲部条目族），与 T6b 无关；断言口径为「前后计数不变」（T6b 不触），非「＝0」。逐件属性组合分布见下节。
- **ADC2DA 守恒**＝章/节标题整行底纹禁触（②工具对账.md §四.3、附则\讲练件底纹减法.md 保留清单）：本脚本外部计数前＝后，与工具内部 `assert adc_pre == adc_post` 双证。
- **文本守恒**＝strict（body 文档序逐段 `w:t` 串接字面全等）＋norm（去空白含全角空格/nbsp/零宽归一化逐段零差异）＋非 `word/document.xml` 部件 MD5 全等（T6 只应改 document.xml）。
- **docxml 指纹**＝改动件数应恰为「段数＞0」的件数（0 段件不得被重写）。

### 既有非规格左框属性组合分布（逐件，前后一致）

- 清单1：left single/4/4/auto｜同级top+left+bottom+right ×45
- 衔接1(29)：无
- 上(61)：left single/4/4/auto｜同级top+left+bottom+right ×27
- 下(79)：left single/4/4/auto｜同级top+left+bottom+right ×18
- 清单2：left single/4/4/auto｜同级top+left+bottom+right ×81
- 衔接2(13)：无
- 92：left single/4/4/auto｜同级top+left+bottom+right ×22
- 90：left single/4/4/auto｜同级top+left+bottom+right ×8
- 68：left single/4/4/auto｜同级top+left+bottom+right ×24
- 89：left single/4/4/auto｜同级top+left+bottom+right ×27

## 二、逐件工具原始输出

## T6 底纹批量器（b）— 人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx
fill 分布：pPr/ADC2DA×11；rPr/C9C9C9×1353
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：0 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx
fill 分布：pPr/ADC2DA×3；pPr/C6D4E3×5；pPr/F2F2F2×38；rPr/C9C9C9×302
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：5 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx
fill 分布：pPr/ADC2DA×10；pPr/C6D4E3×59；pPr/F2F2F2×131；rPr/C9C9C9×876；tcPr/C9C9C9×4
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：59 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx
fill 分布：pPr/ADC2DA×1；pPr/C6D4E3×76；pPr/F2F2F2×123；rPr/C9C9C9×466
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：76 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx
fill 分布：pPr/ADC2DA×21；pPr/auto×123；rPr/C9C9C9×1085；tcPr/F2F5F9×3；tcPr/FAFAFA×6；tcPr/FAFBFC×7
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：0 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx
fill 分布：pPr/ADC2DA×2；pPr/C6D4E3×8；pPr/F2F2F2×18；rPr/C9C9C9×743
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：8 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx
fill 分布：pPr/ADC2DA×11；pPr/C6D4E3×76；pPr/F2F2F2×161；pPr/auto×31；rPr/C9C9C9×350；tcPr/C9C9C9×4
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：76 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx
fill 分布：pPr/ADC2DA×5；pPr/C6D4E3×73；pPr/F2F2F2×164；pPr/auto×28；rPr/C9C9C9×340
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：73 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx
fill 分布：pPr/ADC2DA×6；pPr/C6D4E3×56；pPr/F2F2F2×118；pPr/auto×31；rPr/C9C9C9×347；tcPr/F2F5F9×3；tcPr/FAFAFA×6；tcPr/FAFBFC×7
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：56 段（跳过非标题 0）；ADC2DA 守恒断言 PASS
## T6 底纹批量器（b）— 人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx
fill 分布：pPr/ADC2DA×1；pPr/C6D4E3×74；pPr/F2F2F2×138；pPr/auto×84；rPr/C9C9C9×67；tcPr/F2F5F8×3
b) 讲部/题型标题撤 C6D4E3＋挂左竖条：74 段（跳过非标题 0）；ADC2DA 守恒断言 PASS

## 三、结论

**十件全绿**：撤＋挂段数逐件恰等基线（C6D4E3 前计数亦逐件恰等基线）、跳过非标题 0、ADC2DA 逐件守恒（内外双证）、规格左竖条数＝前值＋撤底纹段数、C6D4E3 残留 0、既有非规格左框前后不变（零误触）、幂等 dry 二跑全 0 段、文本守恒 strict＋norm 零差异、非 document.xml 部件零扰动。T6b 通过，可进 T6c。
