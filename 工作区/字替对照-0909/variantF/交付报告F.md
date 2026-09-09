# variantF 交付报告（2026-09-09 · 全品一致修复轮）

母体＝variantE 全量复制；编译 xelatex 两遍 error／Overfull／Missing character **三 0**；页数 7（与 E 同，无连锁）。
验证：_测v4断言.py 全绿（含 0909 收尾轮口径登记）；断言顶格.py 违规 0；主会话逐页 PNG 实锤 7/7＋6 处原生分辨率放大复核。
执行链：agent-210（主体，超时熔断）→ agent-211（窄口收尾，验证产物齐、报告未写即熔断）→ 主会话补写本报告（依据 diff／断言输出／PNG 实锤）。

## 一、拍板落地（用户授权口径「通过与全品对照进行选择」）

| 项 | 落点 | 内容 |
|---|---|---|
| P-A 题内标签撤粗 | qp-blocks.tex:41 | \anlabel 恒等化（撤 \heiti/NSC-Medium）；[答案][解析][分析][详解][点睛] 全部题源标式＝半角[]＋正文同号＋常规字重＋纯黑不降灰（全品正文区无灰色注记） |
| P-B 检测题号升重 | qp-fonts.tex:71 等 | \heihao BoldFont NSC-w500→w700、\numboldjian 同升；题号数字达全品实测 2.0× 档（6px→8px@11.4pt）；例N 2.3×／变式 1.3×／条目号 2.7× 不动 |
| P-C [注意] 独立行 | qp-blocks.tex:64 | \zhuzhu 改 \par\nopagebreak\noindent[注意]…\par——顶格独立行（全品先例＝"注："行）；推翻 v4.4 内联拍板，宏级统一生效 |
| P-D √× 归仿宋 | qp-fonts.tex:57-58 | \gou/\cha＝\fangsonglat\symbol{"221A}/{"00D7}；说明行/答案位/裸字符全走宏；编译无 Missing char（FZFSK 有字形） |
| P-E 表格全品式 | postproc kbtable＋qp-layout.tex:73 | m 列垂直居中（墨锚数学轴，探针两轮回填）；表头三格 \makebox 全居中；首列居中、短内容居中、长文本两端对齐；\extrarowheight 1.0mm（dT/dE≈+1 净效≈全品顶 2.0/底 2.1mm 档）；断言登记表底缝 4.08/4.04 |
| P-F 标题超长预案 | 本条 | 探究点标题超 14 字先精简、必折行则二行顶格；本轮无实例不触发 |

## 二、修复落地（规则背书项）

| 项 | 落点 | 内容与验证 |
|---|---|---|
| R1 定界符固定档 | postproc 转换 pass | \left(／\left|／\left\langle／\left\{ 全清零（body.tex grep 0）；p4 探究点五例1 C/D 同式括号大小一致实锤；断言③豁免登记（探七 \left\{array×2、探八生长对，清单§九③） |
| R2 判断括号右挂 | qp-blocks.tex \zhenti | \nobreak 双直连＋\hspace{0pt plus 1fil} 右挂＋括号内 \makebox[1.8em] 定宽（全品 1.8 字）＋尾 \hspace{0.56mm} 真右缘（旧 \rule 3.34mm 系沿传误值）；收尾轮返修（去 \mbox{} 断 penalty 链）五原型全右挂 0 overfull；实锤：p1 诊断(1)「两向量模相等」（×) 折行右挂成列、p3(1)(2)、p6 八例1（ ）右挂 |
| R3 图文重叠清零 | postproc side_row | 声明盒 [height=2.6mm][depth=\height−2.6mm]：盒深参与行距，后续文字推到图底之下；实锤 p3 探三例1、p5 探六例1 零重叠，5 处并排全过 |
| R4 空格三类 | postproc pass＋断言 | 双 ~~／数学内 `\ `／相邻 `\) \(` 源换行空隙清零；源空格断言残留 0（注释域豁免登记）；实锤 p5 方法2 大缝消、p3 孤 y 跨行消 |
| R5 全角＝＋－ | postproc pass 6a 替换表 | 半角化＋断言；body.tex 全角数学符 grep 0 |
| R7 ∥ 侧隙 | 探针比对 | _parF_mine vs _parF_ref（全品 a∥b 裁片）同档，\parallel 定义未改 |
| R8 多选排查 | 全卷答案扫描 | 无多字母组合答案，确认全卷唯一 1 处（探究点五例1 (多选题)）；n_duox 断言维持 1 |
| R9 课堂评价 \vbox | 渲染复核 | 7 页版式下 p7 页脚正常，无压页脚 |
| 附带 | postproc side_row 收尾轮 | 选择题题干以空位括号收尾时改末行右挂（全品 p05/p07 实证同纪律） |

## 三、留痕与欠账

- 熔断 2 次（agent-210/211 均 2h 超时）：产物落盘完整，接力无损；教训→防降智纪律（切片/熔断/双口过门）已备案交接-20260909b §三续。
- png-F/ 整页图 7 张；探针裁片 _tab1E/_tab1F（表格）、_parF_ref/_parF_mine（∥）。
- 字体二进制不入 git（再分发条款未核）；抓取脚本＋条款核验＝v4.5 轮欠账。
- 附则回写（新字重表/判断括号新机制/标签题源标式等）留 v4.5 拍板轮，须用户明示后落库。
