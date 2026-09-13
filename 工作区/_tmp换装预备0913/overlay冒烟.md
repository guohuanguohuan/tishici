# qp-m3p-overlay 冒烟记录（0913 深夜，换装预备轮）

- 依据：`换装方案草案.md` §1.4（P1 toolchain 变体——overlay 未过冒烟不得批插）＋`_tmpM3toolchain0913/qp-m3.sty` v0.1（抽段回源）＋P1 成卷件骨架只读判读
- 产物：`qp-m3p-overlay.sty`（overlay 适配层）＋`dummy-p1.tex`（单源）＋`dummy-p1-true/false.tex`（双壳）＋双 PDF/log/aux＋`png-true/`、`png-false/` 目验图——全部在本目录
- 编译器：TinyTeX xelatex（`C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex`），每档连编两遍取稳态，均 exit=0
- 红线核查：零 git；写入仅限本目录；P1 成卷件（P1-必修3第9章量产0912/）、物理样张0911/骨架、qp-m3.sty 只读未动（骨架 render.py 只读调用，png 落本目录）

## 一、P1 骨架 vs qp-m3 宏族差异面（研判定案）

| 面 | P1 骨架（物理样张0911 七模块） | qp-m3.sty | overlay 处置 |
| --- | --- | --- | --- |
| 装载形制 | \input 七模块绝对路径（fonts/layout/parts/headfoot〔内联 phy-params〕/titles/blocks/figs），无包机制 | 单一 .sty＋包选项 | overlay 以 \usepackage 挂七模块后；开装载卫兵（缺 \glueguard/\huaxing/\numboldjian 即 PackageError 拦早挂） |
| 答案制 | 答案制A：\ansline/\jiexi/\kongda/\zhenti/\xiaojie 恒印，正文 0 答案宏，判断走 \zhentib 空括号 | \ifshowans 开关族 | 存量五宏 \renewcommand 换开关体，签名逐一同原件，件内调用零改动 |
| 版面/字号 | qp-layout＝数学 L1 零参数继承（10.09pt/18pt、margin 17.2mm、栏距 7.6mm） | 同档＋ansbg/ansrule 色＋\multicolundershoot=8pt | 内件字号基准零改（正文同源）；补两色＋容差计数器（卫兵式，multicol 缺计数器则跳过） |
| P1 独有件 | qp-figs（\qpfig/\unit）、qp-phy-params（\qpbuce/页脚三形制）、件型层宏在件 main.tex 内（\pingtou/\liubai/\tihao 单参/\lxopt/\xiexwei/\dangbadge…） | \tihao[可选]双参等收编件 | 零收编件型层宏名（防件内后置 \newcommand 撞名炸）；ketang 组头内嵌自有形，不依赖 \pingtou |
| 名占用 | 四制名（showans/ansblock/anskey/ketang/tailfill）正文件骨架零占用；\ansitem/\qpind/\anshang 仅答案册 qp-answ-* 模块占用 | 全量自备 | 本件禁挂答案册件（迁移轮答案册降级只读迁移源不编译，无冲突面）；ketangboxed 不收录（草案 §1.3.1 禁用） |

## 二、overlay 四制读数

| 制 | 落位 | 冒烟实证 |
| --- | --- | --- |
| ① \showans 开关 | 开关本体＋[pure] 包选项＋\mthreepure 壳开关；存量 \ansline/\jiexi/\kongda/\zhenti/\xiaojie 开关化 | false 档答案/解析/小结全隐、\kongda 退 15mm 空线、\zhenti 退 \zhentib 空括号（(3) 行尾空括号目验在） |
| ② ansblock 锚点 | [键]可选参＋\anskey 双锚（log 发射 M3-ANSKEY 两档恒发射）；灰底（lrbox+colorbox）/括线双模；\ansitem/\anssub/\ansnote 内件 | true 档灰底块（题号 11.4pt \heihao\numboldjian＋[答案]条＋(1)(2) 二档悬挂＋[详解]）与括线长块（上下 hairline）渲染正常；3 发射两档恒等 |
| ③ 课堂评价回流 | ketang 环境＝\huaxing＋内嵌组头（\glueguard 软绑定顺排可跨栏） | true/false 双档组头＋2 题顺排正常，无 \vbox 右栏空病灶；迁移后不另手写 \huaxing（dummy 初版双花形已修） |
| ④ 尾页填充块 | \tailfill[高度]（无参吃尾空）＋\iftailfillused 布尔 | 无参档 true 版独占 p2 吃满、false 版贴 p1 栏尾；两档尾块均在 |

## 三、双档机械读数（修正后终检，各连编两遍）

| 项 | dummy-p1-true | dummy-p1-false |
| --- | --- | --- |
| Error | 0 | 0 |
| Overfull | 0 | 0 |
| Underfull | 0 | 0 |
| Missing character | 0 | 0 |
| 页数 | 2 | 1（≤true 档，断言③过） |
| M3-ANSKEY 发射 | 3 | 3（YX-01/YX-02/KT-01 键清单两档 diff=0，对号门两档可跑） |

- log 要点摘录（两档同构）：`Output written on dummy-p1-*.pdf (N pages)`；grep 计数 `^!`=0、`Overfull`=0、`Underfull`=0、`Missing character`=0、`M3-ANSKEY:`=3。
- 目验（png-true/2 页、png-false/1 页，150dpi）：true 版灰底块 F0F0F0、括线块 hairline、\kongda 印答、判断带答案形（×）＋[解析]、[答案]A、素养小结、ketang 组头、尾块全在；false 版答案全隐、判断全空括号、15mm 空线、题面行两档逐行同位（版面等形）、ketang 头与尾块在；页脚物理档（第9章…P1冒烟件＋页码灰块）正常。

## 四、遗留与登记

1. 首编一错＝dummy 正文误写未定义名 `\showans`（学习目标行），修正措辞后双档三零——非 overlay 缺陷，登记防复发；批插脚本禁在题面层写裸 `\showans`。
2. dummy 初版课堂评价位双花形＝调用侧手写 \huaxing＋ketang 内嵌重复，已修；迁移脚本以 `\begin{ketang}` 整体替换「\huaxing＋\vbox」组合，不得再手写花形。
3. 灰底块不可跨栏断（M3 冒烟遗留1 同源）：P1 测评/滚动三栏件一律括线模；长详解判据沿草案 §1.2.5，换装轮与 M3 S2 收口同常数。
4. \multicolundershoot=8pt 为卫兵式设置（旧版 multicol 缺计数器自动跳过），语义与 qp-m3 同。
5. false 档 p1 尾块下方留白较大＝dummy 正文量少＋无参吃尾空档行为，真件 multicols 满栏则尾块贴栏尾，非缺陷。
6. overlay 禁挂答案册件（\ansitem/\qpind/\anshang 与 qp-answ-blocks 撞名）——已在 sty 头部红线注明。
7. 批量前置条件已满足：overlay 冒烟双档通过，换装轮可按草案 §6 顺序进入「迁移脚本＋P1 批插」。
