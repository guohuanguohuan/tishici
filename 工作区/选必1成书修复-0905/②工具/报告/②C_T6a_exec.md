# ②C T6a 正式执行报告 — E0E0E0→F2F2F2（pPr 级）

- 时点：2026-09-05 18:32:52
- 工具：`工具\底纹批量器.py --only a`（执行态自动留 `.bak_底纹批`）
- 对象：`②工具\副本\` 十件（从同步盘 ②-B 回写终态重新复制，MD5 见 `②C_副本重置_MD5.md`）
- 基线：`②工具对账.md` §二 T6a 行＝0／38／131／123／0／18／161／164／118／138 处（全 pPr 级）
- 前置互斥证据：T3/T4 dry 十件 0 改写已复核（`②C_T3T4dry_前置复核.md`，20/20 PASS）

## 一、四道关逐件结果

| 件 | 基线 | 实得 | 计数断言 | 层级 | 幂等 dry | 文本守恒 strict/norm | E0E0E0 前→后 | 残留断言 | 判定 |
|---|---|---|---|---|---|---|---|---|---|
| 清单1 | 0 | 0 | PASS | 无 | 0 PASS | True／True | 0→0 | PASS | PASS |
| 衔接1(29) | 38 | 38 | PASS | pPr×38 | 0 PASS | True／True | 38→0 | PASS | PASS |
| 上(61) | 131 | 131 | PASS | pPr×131 | 0 PASS | True／True | 131→0 | PASS | PASS |
| 下(79) | 123 | 123 | PASS | pPr×123 | 0 PASS | True／True | 123→0 | PASS | PASS |
| 清单2 | 0 | 0 | PASS | 无 | 0 PASS | True／True | 0→0 | PASS | PASS |
| 衔接2(13) | 18 | 18 | PASS | pPr×18 | 0 PASS | True／True | 18→0 | PASS | PASS |
| 92 | 161 | 161 | PASS | pPr×161 | 0 PASS | True／True | 161→0 | PASS | PASS |
| 90 | 164 | 164 | PASS | pPr×164 | 0 PASS | True／True | 164→0 | PASS | PASS |
| 68 | 118 | 118 | PASS | pPr×118 | 0 PASS | True／True | 118→0 | PASS | PASS |
| 89 | 138 | 138 | PASS | pPr×138 | 0 PASS | True／True | 138→0 | PASS | PASS |

- 文本守恒口径：strict＝body 文档序逐段 w:t 串接字面全等；norm＝去空白（含全角空格/nbsp/零宽）归一化逐段零差异；另断非 `word/document.xml` 部件 MD5 全等（T6 只应改 document.xml）。
- 残留断言：exec 后十件 `w:shd fill=E0E0E0` 计数＝0；exec 前计数＝基线（证副本起点＝②-B 回写态、底纹未被 ②-B 触动）。

## 二、逐件工具原始输出

## T6 底纹批量器（a）— 人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx
fill 分布：pPr/ADC2DA×11；rPr/C9C9C9×1353
a) E0E0E0→F2F2F2：0 处（无）
## T6 底纹批量器（a）— 人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx
fill 分布：pPr/ADC2DA×3；pPr/C6D4E3×5；pPr/E0E0E0×38；rPr/C9C9C9×302
a) E0E0E0→F2F2F2：38 处（pPr×38）
## T6 底纹批量器（a）— 人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx
fill 分布：pPr/ADC2DA×10；pPr/C6D4E3×59；pPr/E0E0E0×131；rPr/C9C9C9×876；tcPr/C9C9C9×4
a) E0E0E0→F2F2F2：131 处（pPr×131）
## T6 底纹批量器（a）— 人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx
fill 分布：pPr/ADC2DA×1；pPr/C6D4E3×76；pPr/E0E0E0×123；rPr/C9C9C9×466
a) E0E0E0→F2F2F2：123 处（pPr×123）
## T6 底纹批量器（a）— 人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx
fill 分布：pPr/ADC2DA×21；pPr/auto×123；rPr/C9C9C9×1085；tcPr/F2F5F9×3；tcPr/FAFAFA×6；tcPr/FAFBFC×7
a) E0E0E0→F2F2F2：0 处（无）
## T6 底纹批量器（a）— 人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx
fill 分布：pPr/ADC2DA×2；pPr/C6D4E3×8；pPr/E0E0E0×18；rPr/C9C9C9×743
a) E0E0E0→F2F2F2：18 处（pPr×18）
## T6 底纹批量器（a）— 人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx
fill 分布：pPr/ADC2DA×11；pPr/C6D4E3×76；pPr/E0E0E0×161；pPr/auto×31；rPr/C9C9C9×350；tcPr/C9C9C9×4
a) E0E0E0→F2F2F2：161 处（pPr×161）
## T6 底纹批量器（a）— 人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx
fill 分布：pPr/ADC2DA×5；pPr/C6D4E3×73；pPr/E0E0E0×164；pPr/auto×28；rPr/C9C9C9×340
a) E0E0E0→F2F2F2：164 处（pPr×164）
## T6 底纹批量器（a）— 人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx
fill 分布：pPr/ADC2DA×6；pPr/C6D4E3×56；pPr/E0E0E0×118；pPr/auto×31；rPr/C9C9C9×347；tcPr/F2F5F9×3；tcPr/FAFAFA×6；tcPr/FAFBFC×7
a) E0E0E0→F2F2F2：118 处（pPr×118）
## T6 底纹批量器（a）— 人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx
fill 分布：pPr/ADC2DA×1；pPr/C6D4E3×74；pPr/E0E0E0×138；pPr/auto×84；rPr/C9C9C9×67；tcPr/F2F5F8×3
a) E0E0E0→F2F2F2：138 处（pPr×138）

## 三、结论

**十件全绿**：计数逐件恰等基线、幂等 dry 二跑全 0、文本守恒（strict＋norm）逐件零差异、E0E0E0 残留 0、非 document.xml 部件零扰动。T6a 通过，可进 T6b。
