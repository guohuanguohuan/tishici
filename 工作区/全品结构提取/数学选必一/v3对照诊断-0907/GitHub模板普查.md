# GitHub 模板普查：全品版式参数公开源 + 中文试卷/教辅 LaTeX 模板

- 查证日期：2026-09-07。全部结论附来源 URL；stars/日期来源统一标注为〔搜索 API〕（GitHub REST 搜索 API `pushed_at`/`stargazers_count`）、〔仓库页〕（github.com 仓库页 HTML 星标计数）、〔commits.atom〕（GitHub 提交 feed）、〔CTAN〕（ctan.org 包页）。
- 方法备注：本机未装 `gh` CLI；WebSearch 服务本次故障（HTTP 500），检索全部改走 GitHub REST 搜索 API（未登录）＋仓库页/raw README/commits.atom 抓取，CTAN 页核版本与维护状态。CTAN 与 GitHub 页均为实时抓取。

---

## ① 全品学练考版式参数公开源结论

**结论：未找到。** GitHub 上不存在任何公开的全品学练考（Canpoint）版式参数、高仿模板或复刻样式仓库；同类教辅（必刷题/五三/教材帮/一遍过）也没有出现专设的复刻/高仿排版仓库。

证据（GitHub 搜索 API，2026-09-07 实测）：

| 搜索词 | 结果数 | 判定 |
|---|---|---|
| 全品学练考 | 19 | 全部为 README 含词的无关仓库（funNLP、书单收藏等），无排版类 |
| 全品 latex | 0 | 无 |
| canpoint | 7 | 均无关（租车网站、支付宝组件、班级管理等） |
| canpoint latex | 0 | 无 |
| 学练考 | 578 | 命中的是在线考试系统（sg-exam 等），非排版模板 |
| 教辅 latex / 练习册 latex / 导学案 latex / 讲义模板 latex / exercise book latex chinese | 0 | 无 |
| 双栏 latex | 12 | 全是中文期刊论文双栏模板，无教辅 |

要点：连「练习册 latex」「导学案 latex」这类泛词都是 0 结果，说明 GitHub 中文圈根本没有人把教辅版式做成开源模板——全品参数更不可能有公开源。**版式参数只能靠纸样实测/扫描测量反推，联网查证此路不通。**（本次未扩展普查全品官网 canpoint.cn 与电商详情页，任务范围以 GitHub 为主。）

---

## ② 模板候选登记表（按与本项目需求的匹配度排序）

需求基准：a) 中文数学公式（XeLaTeX/ctex）；b) 双栏/多栏紧凑训练册形态；c) 题答分离；d) 悬挂题号/题号列；e) 黑白灰可定制（非彩色锁死）；f) 可局部借宏（如选项自动排版）不必整体套用。

### 第一梯队（值得动手借）

**1. BHCexam — 匹配度最高（b/c/d/e/f 全中）**
- URL：https://github.com/mathedu4all/bhcexam ｜ stars 98〔仓库页〕｜ 最近提交 2025-05-29〔commits.atom〕｜ 维护中（被 Mathcrowd 题库用于生成试卷 PDF，附 Overleaf 模板页）
- 核心特性（README 实测）：**支持多栏排版开关**；答案显隐开关；选项长度自动网格对齐；题目留白宽度可调；有中文文档（README-zh.md）与 https://lab.mathcrowd.cn/bhcexam/docs
- 匹配：a✓（中文试卷类天生 ctex 系） b✓（唯一明确支持多栏的中文试卷类） c✓ d✓ e✓（黑白试卷样式） f✓
- 短评：与「双栏紧凑训练册」最接近的现成中文试卷类；即使不整体套用，其多栏题号与选项对齐实现也值得抄。

**2. exam-zh — 局部借宏价值最高（f 满分）**
- URL：https://github.com/xkwxdyy/exam-zh ｜ stars 41〔搜索 API〕｜ 最近推送 2026-08-21〔搜索 API〕｜ LPPL 1.3c
- 维护状态（两说并存，如实记录）：README 顶部有 2024-04-26 起「无限期停止维护」告示；但 CTAN 包页显示 **v0.3.6，2026-08-01 仍在发版**（https://ctan.org/pkg/exam-zh ），仓库 2026-08 仍有推送——至少 2026 年仍有版本活动，依赖风险中等。
- 核心特性（README/CTAN 实测）：样式与内容分离；**选择题选项自动排版成合适列数**；密封线参数化定制（姓名/准考证号/考场/座位号栏）；answer control（答案控制）、draft mode；XeLaTeX＋expl3；**模块化——exam-zh-question.sty、exam-zh-choices.sty 等可单独使用**
- 匹配：a✓ c✓ d✓ e✓ b✗（A4 单栏试卷形态，非双栏训练册） f✓✓（模块可单借）
- 短评：它把「选项自动分列」做成了独立 sty，正好是 v3 需要的部件，不必接受它的整卷版式。

**3. xsim — 题答分离引擎备选**
- URL：https://github.com/cgnieder/xsim ｜ stars 81〔搜索 API〕｜ v0.21a（2022-02-12，仓库 README 元信息）、仓库推送 2024-07-20〔搜索 API〕｜ LPPL，维护状态 maintained
- 核心特性：习题-答案分离与收集（就地打印/文末收集/按节/按 ID 选择性打印）、题库分班分主题选择性抽取（collections）、随机出题、多选题型；自带 50+ 示例（含 multiplechoice）
- 匹配：a✓（配 ctex 使用无障碍） b—（无版式，自己配 multicol） c✓✓（最成熟的题答分离机制） d— e✓（无样式锁死） f✓（纯宏包，不带走版式）
- **exsheets 不要用**：CTAN 官方声明 2017-05 起被 xsim 取代、已过时（obsolete），v0.21k 2019-09-30 后无新特性（https://ctan.org/pkg/exsheets ）。GitHub 上仅存个人模板仓（maxnoe/exsheets_template，2 stars，2016 年停更）。

### 第二梯队（高校/地区试卷类，部件级参考）

| 候选 | URL | stars | 最近更新 | 要点 |
|---|---|---|---|---|
| exam-cau | https://github.com/tigertooth4/exam-cau | 9 | 2026-06-10〔搜索 API〕 | LaTeX3；`\problem` 自动中文大题号（一、二、）、得分表动态生成、**一份源出试卷+答案双版**、智能分值标记；中国农大卷风格 |
| hnu_exam | https://github.com/wvqusrai/hnu_exam | 19 | 2026-01-26〔搜索 API〕 | XeLaTeX；基于 exam 类封装 `\makepart`；评分标准设计注明参考 jnuexam；左侧学生信息表 |
| USTBExam | https://github.com/htharoldht/USTBExam | 81 | 2022-11-04〔commits.atom，已停更〕 | `\options{}{}{}{}` 自动排版（仅四选项）、大题计分表/小题题号自动、答案隐藏开关 |
| GEEexam（gaokao_exam） | https://github.com/shaodongtang/gaokao_exam | 88 | 2019-05-01〔搜索 API，停更〕 | 高考卷样式；GEEexam.sty（带分栏线）/NEMT.sty（无分栏线）双样式；README 极简 |
| CMC | https://github.com/shaodongtang/CMC | 28 | 2021-04-19〔搜索 API，停更〕 | 中国大学生数学竞赛卷样式 |
| DANexam | https://github.com/sd44/DANexam | 3 | 2018-12-09〔commits.atom，停更〕 | XeLaTeX/LuaLaTeX 试卷包，参考 exam/BHCexam/GEEexam |
| simplexam | https://github.com/hushidong/simplexam | 20 | 2022-11-11〔搜索 API〕 | 「A simple class for chinese exam paper」；仓库 README 抓取 404，特性未能核实 |
| shmeea | https://github.com/ttyS0/shmeea-exam-paper-latex | 7 | 2026-07-18〔搜索 API〕 | 上海考试院卷样式，基于 exam 类；依赖专用字体集 ctex-fontset-shmeea.def＋华文字体，移植成本高 |
| jnuexam | CTAN：https://ctan.org/pkg/jnuexam ；官方主页 lvjr.bitbucket.io/jnuexam.html（本次网络环境拦截，未读成） | — | 2024F，2024-07-09〔CTAN〕 | **GitHub 无官方仓库**（仅发行版打包镜像 OpenMandrivaAssociation/texlive-jnuexam）；暨大试卷类，含评分栏/登分表（第三方 hnu_exam 引用佐证） |

### 第三梯队（书籍模板：登记备查，彩色/单栏，不合双栏黑白需求）

| 候选 | URL | stars | 最近更新 | 要点 |
|---|---|---|---|---|
| ElegantBook | https://github.com/ElegantLaTeX/ElegantBook | 2,593 | 2026-05-02〔搜索 API〕 | 最流行的中文书籍模板，彩色主题＋单栏章体；只可借章节标题/定理框样式 |
| Beautybook | https://github.com/BeautyLaTeX/Beautybook | 167 | 2026-01-06〔搜索 API〕 | 大型彩色书籍模板，同上不合用 |
| VividBooK | https://github.com/Azure1210/VividBooK | 102 | 2025-08-18〔搜索 API〕 | ElegantBook 魔改（Legrand Orange Book 移植），彩色 |

### 其他登记

- **ezexam** https://github.com/gbchu/ezexam ｜ 38 stars ｜ 2026-08-05 ｜ **Typst 而非 LaTeX**：exam/handout 双模式、A3、choices/fillin、分值；文档 https://ezexam.pages.dev 。不做 LaTeX 引入，仅作「试卷+讲义一体」设计思路参考。
- **讲义成品类**（是排好的讲义不是模板）：Shichien/SeniorMath（https://github.com/Shichien/SeniorMath ，12 stars，2026-06-28，适配国内高中数学体系，**CC BY-NC-SA 4.0 明令禁商用**，只可看样式不可搬内容）；Onion12138/math（https://github.com/Onion12138/math ，30 stars，2021，上海初中数学总复习讲义，基于 ECNUThesis 类 LaTeX3 重构）；lihugang/math-jb-latex（https://github.com/lihugang/math-jb-latex ，7 stars，2024-11，上海《高中数学精编》重排：题间距可调留草稿、按章出 PDF、TikZ 重绘插图——思路与 v3 相关）。
- 试卷自动生成/题库系统（软件，非模板）：JudgePeach/math-question-bank（211 stars）、JinLingxi 题库助手（120 stars）等，与本次版式需求关系弱，不展开。
- 恒定候选之外的发现：Furinar/studyforge-latex-template（https://github.com/Furinar/studyforge-latex-template ，0 stars，2026-07，ctexart＋tcolorbox「复习资料/试卷」双模式、`\HideAnswers` 答案开关、questions/choices 环境——形态接近本项目但彩色框、个人玩具仓，只可看接口设计）；constant-e/latex-math-exam-template（2 stars，2025-08，北京高考样式）；Frigus27/cnexam-math（9 stars，2019）。

---

## ③ 建议（借什么、怎么装）

**总判断：没有任何现成模板能整体满足 a–f（特别是「双栏紧凑＋黑白灰＋可局部借宏」三者并存的不存在），v3 自研骨架应保留，做「部件级借入」而不是换模板。**

1. **选项自动分列 ← exam-zh**（最优先）。两条路：
   - 直接借包：TeX Live/MiKTeX 已收录 exam-zh〔CTAN 包页〕，`exam-zh-choices.sty` 按其文档可脱离主类单独 `\usepackage{exam-zh-choices}` 使用；先在 v3 样张里做兼容性冒烟测试（ctexart＋multicol 双栏下是否冲突）。
   - 若不引包：抄其自动分列判定逻辑（选项累计宽度→自动 2/4 列）自实现，规避其停维风险（README 停维告示 vs CTAN 2026-08 发版并存，长期依赖需谨慎）。
2. **双栏训练册形态 ← BHCexam**。它是唯一明确支持多栏排版的中文试卷类（98 stars、2025-05 仍在动、有 Mathcrowd 生产使用背书）。建议：不整体套用其类，但把它的多栏题号处理、选项网格对齐、留白控制当作 v3 双栏样张的对标实现，逐项核对 v3 的行为是否等效。
3. **题答分离引擎 ← xsim 作为备选**。若 v3 现有「练习件/测评卷答案卷末收集」机制将来不够用（按 ID/按节选择性打印、题库抽取），xsim 是最成熟的方案且不绑定任何版式；**不要碰 exsheets（官方已宣布 obsolete）**。
4. **暂不建议引入**：shmeea（专用字体集绑定）、ElegantBook/Beautybook/VividBooK（彩色单栏，与黑白灰双栏需求相反）、ezexam（Typst 体系）、SeniorMath（NC 协议禁商用，且是成品不是模板）。
5. **全品版式参数**：网查无果（见①），放弃「网上找到现成参数」的路线，改走纸样实测。

---

## ④ 已查清单

**搜索词**（GitHub REST 搜索 API，2026-09-07；加粗者 0 结果）：
全品学练考、**全品 latex**、canpoint、**canpoint latex**、学练考、**教辅 latex**、**练习册 latex**、导学案、**导学案 latex**、讲义 latex、试卷 latex、高中数学 latex、高考 latex、试卷模板、**讲义模板 latex**、exam latex chinese、exam-zh、jnuexam、xsim latex、exsheets、ElegantBook、Beautybook、数学讲义 latex、培优、handout latex、**习题 latex template**、双栏 latex、全品、**exercise book latex chinese**

**实际访问的 URL**：
- 搜索接口：https://api.github.com/search/repositories?q=… （上列各词）
- 仓库页/raw README：https://github.com/xkwxdyy/exam-zh 及其 raw README；https://github.com/shaodongtang/gaokao_exam ；https://github.com/hushidong/simplexam ；https://github.com/ttyS0/shmeea-exam-paper-latex ；https://github.com/constant-e/latex-math-exam-template ；https://github.com/wvqusrai/hnu_exam ；https://github.com/tigertooth4/exam-cau ；https://github.com/Shichien/SeniorMath ；https://github.com/Onion12138/math ；https://github.com/lihugang/math-jb-latex ；https://github.com/Furinar/studyforge-latex-template ；https://github.com/ElegantLaTeX/ElegantBook ；https://github.com/BeautyLaTeX/Beautybook ；https://github.com/Azure1210/VividBooK ；https://github.com/cgnieder/xsim ；https://github.com/gbchu/ezexam ；https://github.com/Frigus27/cnexam-math ；https://github.com/mathedu4all/bhcexam ；https://github.com/htharoldht/USTBExam ；https://github.com/sd44/DANexam
- commits.atom：mathedu4all/bhcexam、htharoldht/USTBExam、sd44/DANexam、shaodongtang/CMC
- CTAN：https://ctan.org/pkg/exam-zh ；https://ctan.org/pkg/jnuexam ；https://ctan.org/pkg/exsheets ；https://mirrors.ctan.org/macros/latex/contrib/jnuexam/README
- 访问失败（如实记录）：https://lvjr.bitbucket.io/jnuexam.html （本地网络策略拒绝，DNS 解析到私有地址）——jnuexam 特性细节未能从官方主页核实，以 CTAN 条目＋第三方引用为准
