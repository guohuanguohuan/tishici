# -*- coding: utf-8 -*-
"""试迁脚本-P1练习（副本树-P1练习 内；写入仅限本目录）
P1 练习本首件 9.1电荷（练习件型）overlay 换装试迁：
  ① 答案册 body.tex（只读迁移源）→ 练-课时91 键账提取（16 键，义务总表 §二.2①）
  ② 件内锚点插入 ansblock（16 键；短答灰底／长详解括线模——草案 §1.2 练习件行＋§1.2.5 判据）
     ＋命制详解回嵌 6 处（\ansnote{详解}；印面最小适配 R1–R3，逐条登记键账）
  ③ overlay 挂接（七模块后；sty 本地挂载——正装三裁②）＋ \\tailfill（\\end{multicols} 前）
  ④ 断言：键数＝16、锚块结构唯一、原件行零删改（纯插入）、工作流残留零、险字形零
产物：练习件9.1-换装/main-换装.tex ＋ 双壳 true/false ＋ 压测件 main-压测.tex ＋ 试迁键账-9.1练习.json
红线：零 git；P1 成卷正件/骨架/答案册/命制卷只读。
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "练习件9.1-换装")
SRC_MAIN = os.path.join(HERE, "00原样基线", "main.tex")   # 正件 main.tex 的原样拷贝（正件本身只读未触）
BODY = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex"
MINGZHI = r"C:/提示词/工作区/P1-必修3第9章量产0912/命制/命制-9.1-六题-详解.md"

# ---------- ① 键账提取（body.tex 练习件 9.1 段，逐字零转写） ----------
EXPECT_KEYS = ["练-课时91-%d" % i for i in range(1, 17)]

body = open(BODY, encoding="utf-8").read()
seg = body.split("\\jietitle{9.1\\quad 电荷(练习件答案)}", 1)[1].split("\\jietitle{9.2", 1)[0]

keys, pending, ansval = [], [], {}
for line in seg.splitlines():
    s = line.strip()
    m = re.match(r"^% pair:(.+)$", s)
    if m:
        pending.append(m.group(1).strip())
        continue
    m = re.match(r"^\\ansitem\{(.+?)\}\{(.*)\}\s*$", s)
    if m and pending:
        k = pending.pop(0)
        ansval[k] = (m.group(1), m.group(2))
        keys.append(k)
assert not pending, "缺值键（悬空）: %s" % pending
assert keys == EXPECT_KEYS, "键账不齐：got=%s" % keys
assert len(ansval) == 16, "键数≠16: %d" % len(ansval)

# \anshang 双位档（body.tex:226「题 10 起双位档」逐块迁入，块内局部 setlength）
SHANG10 = "\\setlength{\\anshang}{7.6mm}"   # 题10~16

# ---------- ② 命制详解回嵌（源＝命制-9.1-六题-详解.md；印面最小适配 R1–R3） ----------
# R1 去工作流注记：✓ 校验符与「（Python 复算 …）」括注删除（校验句文字部分保留）
# R2 书N → 教材第N页（命制卷§五 页码口径）
# R3 unicode 上下标/全角运算符 → 件面数学 idiom（$…$、\times、\unit、\dfrac）；
#    corpus 无字形者走数学模：±→$\pm$、≈→$\approx$、＜/＞→$<$/>$、⇒→「，即/给出」、÷→\div
# R4 其余措辞逐字保留（\textbf 承 md 原加粗位）
DETAIL = {
    "练-课时91-8": r"摩擦起电的实质是电子从一个物体转移到另一个物体——原子核里的质子和中子被紧密束缚、原子核结构稳定，摩擦中不动的只是核外束缚较弱的电子（教材第3页）；得到电子的物体因多余电子带负电，失去电子的物体因缺少电子带正电。玻璃棒带正电，说明它在摩擦中\textbf{失去}电子，这些电子转移到丝绸上，丝绸因得到电子而带负电——A对。B把转移方向说反，且“得到电子而带正电”与教材第3页结论自相矛盾——B错。橡胶棒带负电是它从毛皮\textbf{得到}电子的结果，电荷只是发生转移、总量不变，摩擦并不创造电荷（教材第4页电荷守恒定律：电荷既不会创生也不会消灭，只能从一个物体转移到另一个物体）——C错。玻璃棒靠近铝箔小球时小球被吸引，是静电感应：小球中的自由电子被玻璃棒上的正电荷吸引、向靠近玻璃棒的一端移动，近端带异号电荷故相吸；二者并未接触，没有电荷从玻璃棒转移到小球上，也没有电荷从小球转移到玻璃棒上（教材第4页：感应起电中导体中的自由电荷只是从导体的一部分转移到另一部分）——D错（把“吸引现象”与“接触起电/电荷转移”混为一谈）。故选A。",
    "练-课时91-9": r"比荷＝电荷量与质量之比，故用 $e$ 除以 $m_{\text{e}}$：$\dfrac{e}{m_{\text{e}}}=\dfrac{1.60\times10^{-19}\,\unit{C}}{9.11\times10^{-31}\,\unit{kg}}=0.175\,6\times10^{12}\,\unit{C/kg}=1.756\times10^{11}\,\unit{C/kg}\approx\mathbf{1.76\times10^{11}\,\unit{C/kg}}$（与教材第5页正文所给电子比荷值一致；指数部分 $10^{-19}\div10^{-31}=10^{12}$）。\par B把指数算成 $10^{-11}$（$-19-31$ 之误），数量级错；C的数值 $5.69\times10^{-12}$ 是把比“荷”与“质”倒过来算 $m_{\text{e}}/e$ 的结果（$9.11\times10^{-31}\div1.60\times10^{-19}=5.69\times10^{-12}$，单位 $\unit{kg/C}$）——数值与单位虽配套，但那是“质量与电荷量之比”，不是比荷；D既取倒数又弄错数量级（$10^{12}$）与单位配套关系。故选A。",
    "练-课时91-10": r"两球完全相同，接触后电荷重新分配并均分；分配总量由电荷守恒定律给出——接触前后系统电荷的\textbf{代数和}不变。\par 接触前总量 $=(+3.0\times10^{-9}\,\unit{C})+(-5.0\times10^{-9}\,\unit{C})=-2.0\times10^{-9}\,\unit{C}$（即先有 $3.0\times10^{-9}\,\unit{C}$ 的正、负电荷发生中和，剩余 $-2.0\times10^{-9}\,\unit{C}$ 的净电荷由两球平分）。\par 分开后每球 $=\dfrac{-2.0\times10^{-9}\,\unit{C}}{2}=\mathbf{-1.0\times10^{-9}\,\unit{C}}$，A、B带同种电荷（均为负）。\par B（$-4.0\times10^{-9}\,\unit{C}$）是把两电荷量的绝对值直接取平均（$\dfrac{3.0+5.0}{2}$）而丢掉“异号先抵消”这一步；C（$+1.0\times10^{-9}\,\unit{C}$）是抵消对了、绝对值 $2.0\times10^{-9}$ 平分得 $1.0\times10^{-9}$ 但把符号配反（净电荷为负）；D把“一正一负接触”直接当成“全部抵消、电荷消失”——抵消只发生在等量异号时，且即便完全抵消也只是代数和为零，电荷并没有消失（教材第4页中和表述）。故选A。",
    "练-课时91-14": r"\textbf{（1）}丙原来不带电，与甲接触后两者完全相同、电荷平分，故分开后甲、丙各带 $+2.5\times10^{-9}\,\unit{C}$。由此\textbf{逆推}甲在与丙接触前（即甲、乙刚分开瞬间）所带的电荷量 $q_{1}$：$q_{1}=2\times(+2.5\times10^{-9}\,\unit{C})=\mathbf{+5.0\times10^{-9}\,\unit{C}}$（甲带正电）。甲、乙起初相互接触且都不带电，系统电荷的代数和为零；感应分离过程中电荷只是在两球之间转移，没有电荷逸出到球外（教材第4页电荷守恒定律），故分开后二者必带\textbf{等量异号}电荷，乙的电荷量 $q_{2}=-q_{1}=\mathbf{-5.0\times10^{-9}\,\unit{C}}$。校验：$q_{1}+q_{2}=+5.0\times10^{-9}\,\unit{C}-5.0\times10^{-9}\,\unit{C}=0$，与分开前的总电荷一致。\par \textbf{（2）}P带\textbf{负电}。理由：甲是靠近P的一端（近端），由（1）知甲带正电；教材第3页——导体靠近带电体的一端带\textbf{异种}电荷、远离的一端带\textbf{同种}电荷，近端电性与施带电体相反，故P带负电。微观上：P上多余的电子排斥金属球中的自由电子，自由电子被推离P的一侧，使远端（乙）积有多余电子而带负电、近端（甲）缺少电子而带正电，与（1）所得“甲正、乙负”完全一致（两问互证）。",
    "练-课时91-15": r"\textbf{（1）}玻璃棒带正电。分开前甲、乙中的自由电子受到玻璃棒上正电荷的作用，\textbf{向靠近玻璃棒的一端（甲）移动}；保持玻璃棒不动把甲、乙分开，甲因有多余电子而带\textbf{负电}，乙因缺少电子而带\textbf{正电}。甲、乙起初整体电中性、电荷代数和为零，感应只是把电荷从导体的一部分转移到另一部分（教材第4页），没有电荷离开两球，故二者所带电荷量\textbf{大小相等、电性相反}，即 $q_{1}=q_{2}$；记 $q_{1}=q_{2}=q$，则分开瞬间甲 $=-q$、乙 $=+q$。\par \textbf{（2）}按两次接触逐步记电荷量（完全相同金属球接触后各得两球接触前电荷量代数和的一半）：第一步，乙（$+q$）与不带电的丙接触后分开：乙＝丙＝$+\dfrac{q}{2}$；第二步，甲（$-q$）与此时带 $+\dfrac{q}{2}$ 的丙接触后分开：甲＝丙＝$\dfrac{-q+\dfrac{q}{2}}{2}=\mathbf{-\dfrac{q}{4}}$。由题给丙的最终电荷量 $-1.0\times10^{-9}\,\unit{C}$：$-\dfrac{q}{4}=-1.0\times10^{-9}\,\unit{C}$，即 $q=\mathbf{4.0\times10^{-9}\,\unit{C}}$（$q_{1}=4.0\times10^{-9}\,\unit{C}$）。于是操作结束后的末态为：甲 $=-\dfrac{q}{4}=\mathbf{-1.0\times10^{-9}\,\unit{C}}$，丙 $=\mathbf{-1.0\times10^{-9}\,\unit{C}}$，乙 $=\dfrac{q}{2}=\mathbf{+2.0\times10^{-9}\,\unit{C}}$。守恒校验：甲＋乙＋丙 $=(-1.0+2.0-1.0)\times10^{-9}\,\unit{C}=0$，与分开瞬间（以及最初不带电）的总电荷一致。\par \textbf{（3）分类讨论：仍能唯一确定。}丙的最终电荷量并非可正可负——它由物理链锁定：甲与丙接触前，二者总电荷 $=-q+\dfrac{q}{2}=-\dfrac{q}{2}<0$，均分后丙必带\textbf{负}电，即丙末 $=-\dfrac{q}{4}$ 恒为负值。所以“丙所带电荷量的大小为 $1.0\times10^{-9}\,\unit{C}$”这一读数只能对应丙末 $=-1.0\times10^{-9}\,\unit{C}$，解得 $q_{1}=4.0\times10^{-9}\,\unit{C}$，唯一。反之，若不加论证就把读数写成 $+1.0\times10^{-9}\,\unit{C}$（这是本题的主要失分支），则 $-\dfrac{q}{4}=+1.0\times10^{-9}\,\unit{C}$ 给出 $q=-4.0\times10^{-9}\,\unit{C}$，与 $q$ 表示“电荷量的大小”（正值）矛盾，同时也与（1）中“甲必带负电、乙必带正电”的感应判定相矛盾，\textbf{该支必须舍去}。即：测量只给大小时 $\pm$ 两支在代数上并存，但\textbf{感应链决定了末值的符号}，物理约束使其中一支不成立——本题的难正在这一层“设未知量、按链定符号、据约束取舍”，而不在计算量。",
    "练-课时91-16": r"\textbf{（1）}A、B起初相互接触且都不带电，总电荷的代数和为零；分开瞬间电荷只在两球之间转移，故A、B带\textbf{等量异号}电荷（教材第4页电荷守恒定律）。由A $=+8.0\times10^{-9}\,\unit{C}$ 得 $\mathbf{B=-8.0\times10^{-9}\,\unit{C}}$。电性互证：橡胶棒带负电，它排斥导体中的自由电子，自由电子被推离到远端，故近端A因缺少电子带正电、远端B因多余电子带负电，与A $=+8.0\times10^{-9}\,\unit{C}$ 相符（教材第3页：近端异种、远端同种）。以下记A $=+q$、B $=-q$、C $=0$（$q=8.0\times10^{-9}\,\unit{C}$）。每次接触后两球各得接触前代数和的一半。\par \textbf{（2）}可选的球对有三对：A-C、B-C、A-B；两次操作须取不同的两对，先后有序，共 $3\times2=\mathbf{6}$ 个操作序，逐一计算（数值单位均为 $\times10^{-9}\,\unit{C}$）：\par 序①（先A、C，后A、B）：A、C接触后各 $+4.0$（B $=-8.0$）；再A、B接触：$\dfrac{+4.0-8.0}{2}=-2.0$，末态A $=-2.0$、B $=-2.0$、$\mathbf{C=+4.0}$；\par 序②（先A、C，后B、C）：A＝C＝$+4.0$；再B、C接触：$\dfrac{-8.0+4.0}{2}=-2.0$，末态A $=+4.0$、B $=-2.0$、$\mathbf{C=-2.0}$；\par 序③（先B、C，后A、C）：B、C接触后各 $-4.0$（A $=+8.0$）；再A、C接触：$\dfrac{+8.0-4.0}{2}=+2.0$，末态A $=+2.0$、B $=-4.0$、$\mathbf{C=+2.0}$；\par 序④（先B、C，后A、B）：B＝C＝$-4.0$；再A、B接触：$\dfrac{+8.0-4.0}{2}=+2.0$，末态A $=+2.0$、B $=+2.0$、$\mathbf{C=-4.0}$；\par 序⑤（先A、B，后A、C）：A、B接触后各 $0$（等量异号抵消，代数和仍为零，电荷未消失），C仍为 $0$，末态三球均不带电，$\mathbf{C=0}$；\par 序⑥（先A、B，后B、C）：同序⑤，A、B接触后已全为 $0$，末态三球均不带电，$\mathbf{C=0}$。\par 合计：\textbf{C末值的可能值为 $+4.0\times10^{-9}\,\unit{C}$、$+2.0\times10^{-9}\,\unit{C}$、$0$、$-2.0\times10^{-9}\,\unit{C}$、$-4.0\times10^{-9}\,\unit{C}$ 共五个}（六个序中 $0$ 由序⑤⑥共有）；$|C|$ 最大 $=4.0\times10^{-9}\,\unit{C}$，只在“序①（先A、C后A、B）”取得——其机理是C只与带正电的A接触过、从未与B接触，把A的一半电荷留在自己身上。守恒校验（六序逐一）：末态三球电荷代数和均为 $0$，与总电荷始终为零一致。\par \textbf{（3）不能}（指三球都带同种电荷）。三球构成的系统与外界没有电荷交换，任何一次接触操作前后总电荷的代数和保持不变，本件中该恒量 $=0$（分开瞬间 $+q-q+0=0$）。若三球都带正电，则代数和 $>0$；若都带负电，则代数和 $<0$；两者都与“代数和恒为零”矛盾，故无论按哪种顺序、操作多少次都不可能使三球同时带同种电荷。\par 补充辨别：三球电荷\textbf{完全相同}的情形是存在的，即三球都为 $0$（先让A、B接触中和即可，序⑤⑥），但“都不带电”不等于“都带同种电荷”——题目此处考查的正是守恒这一必要条件与可实现操作序之间的对照：\textbf{懂守恒者一句判定，只背均分结论者须穷举六序仍易漏}。",
}
DETAIL_SRC = {
    "练-课时91-8": "命制-P1-9.1-简-1", "练-课时91-9": "命制-P1-9.1-简-2",
    "练-课时91-10": "命制-P1-9.1-简-3", "练-课时91-14": "命制-P1-9.1-中-1",
    "练-课时91-15": "命制-P1-9.1-难-1", "练-课时91-16": "命制-P1-9.1-难-2",
}

# 印面适配断言：工作流残留零＋险字形零（corpus 实测无字形者禁止直排）
RESIDUE = ["Python", "✓", "⇒", "÷", "≈", "±", "＜", "＞", "－", "⁻", "⁰", "¹", "²", "³", "⁴", "⁹", "ₑ", "₁", "₂"]
for k, d in DETAIL.items():
    for r in RESIDUE:
        assert r not in d, "工作流残留/险字形 %r in %s" % (r, k)
# 适配保真抽断言：各详解 3 个源文指纹句必须在（措辞逐字保留的证据）
FPRINT = {
    "练-课时91-8": ["近端带异号电荷故相吸", "混为一谈", "摩擦并不创造电荷"],
    "练-课时91-9": ["不是比荷", "指数部分", "单位配套关系"],
    "练-课时91-10": ["异号先抵消", "电荷并没有消失", "净电荷由两球平分"],
    "练-课时91-14": ["两问互证", "没有电荷逸出到球外", "近端电性与施带电体相反"],
    "练-课时91-15": ["该支必须舍去", "大小相等、电性相反", "而不在计算量"],
    "练-课时91-16": ["懂守恒者一句判定", "把A的一半电荷留在自己身上", "与总电荷始终为零一致"],
}
for k, fps in FPRINT.items():
    for fp in fps:
        assert fp in DETAIL[k], "适配丢失源文指纹 %r (%s)" % (fp, k)

# 详解源存在性断言（命制详解卷逐题对应；题↔源映射见件头注 题8/9/10/14/15/16）
_mz = open(MINGZHI, encoding="utf-8").read()
for k, s in DETAIL_SRC.items():
    assert ("### " + s) in _mz, "命制源缺节: %s" % s

# ---------- ③ 模式判据（草案 §1.2.5：估高 >8 行或含 display 环境/表格/图 → 括线模） ----------
def est_lines(tex):
    plain = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})*", "", tex)  # 粗去宏（估读用）
    plain = re.sub(r"[${}]", "", plain)
    return math.ceil(len(plain) / 23) + 1   # 栏宽 84mm ≈23 字/行；＋答案行

MODE = {k: ("括线" if k in DETAIL else "灰底") for k in EXPECT_KEYS}
EST = {}
for k in EXPECT_KEYS:
    n = est_lines(DETAIL.get(k, "")) + 2
    EST[k] = n
    if MODE[k] == "括线":
        assert n > 8, "判据不符（括线块估高≤8行）%s=%d" % (k, n)
    else:
        assert n <= 8, "判据不符（灰底块估高>8行）%s=%d" % (k, n)
# 题11 \dfrac：inline display 式分数（非 display 环境）——承导学件灰底先例，登记键账
assert r"\dfrac" in ansval["练-课时91-11"][1]

# ---------- ④ 件内插入（块尾锚：\tihao{n} 块至次一块界；\xiexwei 后＝书写位不废） ----------
src = open(SRC_MAIN, encoding="utf-8").read()
lines = src.splitlines(keepends=True)

# overlay 挂接（七模块 \input 之后；本地 sty——正装三裁② kpathsea 中文路径禁绝对引用）
figs_i = next(i for i, l in enumerate(lines) if "qp-figs.tex" in l)
HOOK = ["\n", "% —— 换装 overlay 挂接（副本树-P1练习 试迁；七模块后、\\begin{document} 前；sty 本地挂载）——\n",
        "\\usepackage{qp-m3p-overlay}\n"]
lines[figs_i + 1:figs_i + 1] = HOOK

# 划定每题块界（\tihao{n} 起，至下一 \tihao／\dangbadge／\end{multicols}）
bounds = {}
starts = [i for i, l in enumerate(lines) if re.match(r"^\\tihao\{(\d+)\}", l)]
assert len(starts) == 16, "题号数≠16: %d" % len(starts)
cuts = sorted(starts
              + [i for i, l in enumerate(lines) if l.startswith("\\dangbadge")]
              + [k for k, l in enumerate(lines) if "\\end{multicols}" in l])
for i in starts:
    n = int(re.match(r"^\\tihao\{(\d+)\}", lines[i]).group(1))
    j = next(k for k in cuts if k > i)
    # 块尾＝块内最后一条非空、非注释行（计算题块尾即 \xiexwei{16mm} 行——插其后，书写位不废）
    tail = max(k for k in range(i, j)
               if lines[k].strip() and not lines[k].lstrip().startswith("%"))
    assert n not in bounds
    bounds[n] = tail
for n in (11, 14, 15, 16):
    assert "\\xiexwei{16mm}" in lines[bounds[n]], "题%d 块尾非书写位行" % n

blk_lines = 0
for n in range(16, 0, -1):   # 倒序插入防行号漂移
    key = "练-课时91-%d" % n
    label, val = ansval[key]
    body_lines = []
    if n >= 10:
        body_lines.append(SHANG10 + "   %% 题10 起双位档（body.tex:226 口径，块内局部）")
    body_lines.append("%% ans:%s" % key)
    item = "\\ansitem{%s}{%s}" % (label, val)
    if key in DETAIL:
        item += "\\ansnote{详解}{%s}" % DETAIL[key]
    body_lines.append(item)
    blk = ["\\begin{ansblock}[%s]" % key] + body_lines + ["\\end{ansblock}"]
    if MODE[key] == "括线":
        blk = ["\\ansblockgrayfalse %% 括线模：长详解块（判据 草案§1.2.5，估高 %d 行）" % EST[key]] + blk + \
              ["\\ansblockgraytrue % ─ 括线模束"]
    blk_lines += len(blk)
    lines[bounds[n] + 1:bounds[n] + 1] = [b + "\n" for b in blk]

# 尾页填充块（\end{multicols} 前；义务总表 §二.2③ 尾块 4 处之一）
out = "".join(lines)
assert out.count("\\end{multicols}") == 1
out = out.replace("\\end{multicols}", "\\tailfill\n\n\\end{multicols}")

# ---------- ⑤ 断言：原件行零删改（纯插入子序列 diff） ----------
new_lines = out.splitlines()
orig = src.splitlines()
it = iter(new_lines)
for ol in orig:
    for nl in it:
        if nl == ol:
            break
    else:
        sys.exit("原件行被删改: %r" % ol[:60])
added = len(new_lines) - len(orig)
expect_added = len(HOOK) + blk_lines + 2   # ＋overlay 钩行＋tailfill 行＋空行
assert added == expect_added, "插入行数异常: %d ≠ %d" % (added, expect_added)
# M3-ANSKEY 源层锚（可选参）16 个＋% ans: 源锚 16 个
assert out.count("\\begin{ansblock}[练-课时91-") == 16
assert len(re.findall(r"^% ans:(练-课时91-\d+)$", out, re.M)) == 16

with open(os.path.join(PIECE, "main-换装.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% —— 副本树-P1练习 试迁件（由 00原样基线/main.tex 机器迁移生成；正件只读对照）——\n" + out)

with open(os.path.join(PIECE, "main-换装-true.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% 试迁双壳·含详解印本档（\\showans true＝默认）→ main-换装-true.pdf\n\\def\\mthreepure{0}\n\\input{main-换装.tex}\n")
with open(os.path.join(PIECE, "main-换装-false.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% 试迁双壳·纯题档（\\mthreepure=1 → \\showansfalse；括线/灰底全吞体）→ main-换装-false.pdf\n\\def\\mthreepure{1}\n\\input{main-换装.tex}\n")

# 压测件：6 长详解块强制灰底卡栏（冒烟遗留1／草案 §5.1 风险面的最卡配置；非印本候选）
yace_lines = [l for l in out.splitlines(keepends=True)
              if not l.startswith("\\ansblockgrayfalse") and not l.startswith("\\ansblockgraytrue")]
with open(os.path.join(PIECE, "main-压测.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% 专项压测件·长详解灰底卡栏（真件双栏 multicols 最卡配置；判据常数的反证对照）\n"
            "% ＝true 档内容，仅撤 6 块括线模包装→默认灰底；非印本候选，勿入重发清单\n"
            "\\def\\mthreepure{0}\n\\input{main-换装-压测体.tex}\n")
with open(os.path.join(PIECE, "main-换装-压测体.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("".join(yace_lines))

# 险字形终检（全件 emitted 面上零出现——键值承 body.tex 已编件，详解走 R3 转换）
for r in RESIDUE:
    assert r not in out, "险字形 %r 混入 emitted 件" % r

man = {
    "件": "练习件/9.1电荷（练习本 4 件之首件）", "键数": len(ansval),
    "灰底块数": sum(1 for k in MODE if MODE[k] == "灰底"), "括线块数": sum(1 for k in MODE if MODE[k] == "括线"),
    "键值": {k: ansval[k][1] for k in EXPECT_KEYS},
    "模式": MODE, "估高行": EST,
    "详解随键": {k: {"源": DETAIL_SRC[k], "印面适配": "R1 去工作流注记（✓/Python 复算括注）；R2 书N→教材第N页；R3 unicode→件面数学 idiom（±≈＜＞⇒÷ 走数学模/连接词）；R4 其余逐字"} for k in DETAIL},
    "回捞10题详解": "未迁——详解未入答案册/命制卷（源在 docx 原卷切片），批插轮须主脑裁详解来源口径",
    "插入点": {("练-课时91-%d" % n): ("\\xiexwei{16mm} 后" if n in (11, 14, 15, 16) else "块尾（末 \\lxopt/\\qpfig 行后）") for n in range(1, 17)},
    "尾块": "\\tailfill 1 处（\\end{multicols} 前）", "overlay": "\\usepackage{qp-m3p-overlay}（本地 sty，正装三裁②）",
}
with open(os.path.join(HERE, "试迁键账-9.1练习.json"), "w", encoding="utf-8") as f:
    json.dump(man, f, ensure_ascii=False, indent=1)

print("OK 迁移键数=16（灰底 %d／括线 %d；详解回嵌 %d 处）＋\\tailfill 1＋overlay 挂接 1"
      % (man["灰底块数"], man["括线块数"], len(DETAIL)))
for k in EXPECT_KEYS:
    print("  %s [%s·估%d行] = %s" % (k, MODE[k], EST[k], ansval[k][1][:42]))
