# -*- coding: utf-8 -*-
r"""迁移P1练习拓展.py — P1 换装正装波4b 批插（练习 4 件 62 键＋拓展 1 件 46 键＝108 键）。

依据：换装方案草案 §1.2＋试迁报告-P1练习（承重墙：估高>8 行→括线强制；\xiexwei 后插书写位不废；
     SHANG10 块内局部）＋试迁报告-P1拓展（拓区边界前插、拓-046 括线壳、压测 ABC）＋波2 改判
     （尾块插最后 \end{multicols} 之后·\end{document} 之前）＋J1 裁（拓件 SHANG10 照 body.tex L469 加，
     拓-010 起双位档——与试迁拓臂差异面，报告登记）＋断点件②取证（注记 8 处／命制详解 12 处／窄栏 4 处）。
红线：零 git；P1 正件（成卷/答案册/命制）只读；写入仅 工作区/_tmp换装正装0914/P1练习拓展/；
     main.src.tex＝预迁移快照，main.tex＝换装件；拓-31 窄栏改制只落迁后 main.tex。
判模（断点③.2 钉）：est＝ceil(去宏字符/23)+1 对（值＋详解）合计，>8 行→括线强制（承重墙）；
     钉账：91-8/9/10/14/15/16＋拓-046 必括线，9.1 账≡试迁（10 灰/6 括）、拓≡试迁（45 灰/拓-046 括）。
"""
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # P1练习拓展
PROJ = 'C:/提示词'
TREE = HERE
ANS = os.path.join(PROJ, '工作区', 'P1-必修3第9章量产0912', '成卷', '答案册')
BODY = os.path.join(ANS, 'body.tex')
CJ = os.path.join(PROJ, '工作区', 'P1-必修3第9章量产0912', '成卷')
MZ = os.path.join(PROJ, '工作区', 'P1-必修3第9章量产0912', '命制')
STY_SRC = os.path.join(PROJ, '工作区', '_tmp换装预备0913', 'qp-m3p-overlay.sty')
STY_MD5 = 'da54d841927284052336cf9709ff6fb2'

PIECES_LX = [('9.1电荷', '练-课时91', list(range(1, 17))),
             ('9.2库仑定律', '练-课时92', [1] + list(range(3, 17))),
             ('9.3电场电场强度', '练-课时93', [1] + list(range(3, 17))),
             ('9.4静电的防止与利用', '练-课时94', list(range(1, 17)))]
PIECE_TUO = ('拓展册', '拓', list(range(1, 47)))
LINE_UNITS = 23          # 84mm 栏 ≈23 全角字/行（断点③.2 钉公式）
RULED_LINES = 8          # 承重墙判据：est >8 行 → 括线强制
SHANG10 = '\\setlength{\\anshang}{7.6mm}'
RESIDUE = ['Python', '✓', '⇒', '÷', '≈', '±', '＜', '＞', '－',
           '⁻', '⁰', '¹', '²', '³', '⁴', '⁹', 'ₑ', '₁', '₂']

# ========== ① 册载键账＋注记（body.tex 现场解析，逐字零转写——坑·探查截断勿用） ==========
SEG_HEADS = [('练-课时91', r'\jietitle{9.1\quad 电荷(练习件答案)}', r'\jietitle{9.2'),
             ('练-课时92', r'\jietitle{9.2\quad 库仑定律(练习件答案)}', r'\jietitle{9.3'),
             ('练-课时93', r'\jietitle{9.3\quad 电场 电场强度(练习件答案)}', r'\jietitle{9.4'),
             ('练-课时94', r'\jietitle{9.4\quad 静电的防止与利用(练习件答案)}', r'\jietitle{拓展册(答案)}'),
             ('拓', r'\jietitle{拓展册(答案)}', r'\jietitle{单元素养测评卷')]
NOTE_KEYS = {'练-课时92-13', '练-课时92-16', '练-课时93-11', '练-课时93-16',
             '练-课时94-1', '练-课时94-11', '拓-001', '拓-046'}
RE_PAIR = re.compile(r'^% pair:(\S+)\s*$')
RE_ITEM = re.compile(r'^\\ansitem\{(.+?)\}\{(.*)\}\s*$')
RE_LINE = re.compile(r'^\\ansline\{(.+?)\}\{(.*)\}\s*$')


def parse_book():
    body = io.open(BODY, encoding='utf-8').read()
    kmap, notes, n_shuoming = {}, {}, 0
    for pfx, h, t in SEG_HEADS:
        seg = body.split(h, 1)[1].split(t, 1)[0]
        pending, last = [], None
        for ln in seg.splitlines():
            s = ln.strip()
            m = RE_PAIR.match(s)
            if m:
                assert not pending, '%s 悬空组 %s' % (pfx, pending)
                pending.append(m.group(1))
                continue
            m = RE_ITEM.match(s)
            if m and pending:
                k = pending.pop(0)
                assert k not in kmap, '重键 %s' % k
                kmap[k] = (m.group(1), m.group(2))
                last = k
                continue
            m = RE_LINE.match(s)
            if m and last:
                if m.group(1) == '解析':
                    assert last not in notes, '重注记 %s' % last
                    notes[last] = m.group(2)
                else:
                    assert m.group(1) == '说明', '未知注记型 %s' % m.group(1)
                    n_shuoming += 1
        assert not pending, '%s 缺值键 %s（悬空停门）' % (pfx, pending)
    assert set(notes) == NOTE_KEYS, '册载注记键账≠8 处：%s' % sorted(set(notes) ^ NOTE_KEYS)
    assert n_shuoming == 2, '说明行 %d≠2（92/93 略位注记）' % n_shuoming
    return kmap, notes


# ========== ② 命制详解 18 处（9.1 六处＝试迁 R1–R3 已适配逐字复用；余 12 处本轮适配） ==========
DETAIL = {}
DETAIL_SRC = {}
# ---- 9.1（试迁脚本-P1练习.py DETAIL/DETAIL_SRC 字典逐字复用） ----
DETAIL["练-课时91-8"] = r"摩擦起电的实质是电子从一个物体转移到另一个物体——原子核里的质子和中子被紧密束缚、原子核结构稳定，摩擦中不动的只是核外束缚较弱的电子（教材第3页）；得到电子的物体因多余电子带负电，失去电子的物体因缺少电子带正电。玻璃棒带正电，说明它在摩擦中\textbf{失去}电子，这些电子转移到丝绸上，丝绸因得到电子而带负电——A对。B把转移方向说反，且“得到电子而带正电”与教材第3页结论自相矛盾——B错。橡胶棒带负电是它从毛皮\textbf{得到}电子的结果，电荷只是发生转移、总量不变，摩擦并不创造电荷（教材第4页电荷守恒定律：电荷既不会创生也不会消灭，只能从一个物体转移到另一个物体）——C错。玻璃棒靠近铝箔小球时小球被吸引，是静电感应：小球中的自由电子被玻璃棒上的正电荷吸引、向靠近玻璃棒的一端移动，近端带异号电荷故相吸；二者并未接触，没有电荷从玻璃棒转移到小球上，也没有电荷从小球转移到玻璃棒上（教材第4页：感应起电中导体中的自由电荷只是从导体的一部分转移到另一部分）——D错（把“吸引现象”与“接触起电/电荷转移”混为一谈）。故选A。"
DETAIL["练-课时91-9"] = r"比荷＝电荷量与质量之比，故用 $e$ 除以 $m_{\text{e}}$：$\dfrac{e}{m_{\text{e}}}=\dfrac{1.60\times10^{-19}\,\unit{C}}{9.11\times10^{-31}\,\unit{kg}}=0.175\,6\times10^{12}\,\unit{C/kg}=1.756\times10^{11}\,\unit{C/kg}\approx\mathbf{1.76\times10^{11}\,\unit{C/kg}}$（与教材第5页正文所给电子比荷值一致；指数部分 $10^{-19}\div10^{-31}=10^{12}$）。\par B把指数算成 $10^{-11}$（$-19-31$ 之误），数量级错；C的数值 $5.69\times10^{-12}$ 是把比“荷”与“质”倒过来算 $m_{\text{e}}/e$ 的结果（$9.11\times10^{-31}\div1.60\times10^{-19}=5.69\times10^{-12}$，单位 $\unit{kg/C}$）——数值与单位虽配套，但那是“质量与电荷量之比”，不是比荷；D既取倒数又弄错数量级（$10^{12}$）与单位配套关系。故选A。"
DETAIL["练-课时91-10"] = r"两球完全相同，接触后电荷重新分配并均分；分配总量由电荷守恒定律给出——接触前后系统电荷的\textbf{代数和}不变。\par 接触前总量 $=(+3.0\times10^{-9}\,\unit{C})+(-5.0\times10^{-9}\,\unit{C})=-2.0\times10^{-9}\,\unit{C}$（即先有 $3.0\times10^{-9}\,\unit{C}$ 的正、负电荷发生中和，剩余 $-2.0\times10^{-9}\,\unit{C}$ 的净电荷由两球平分）。\par 分开后每球 $=\dfrac{-2.0\times10^{-9}\,\unit{C}}{2}=\mathbf{-1.0\times10^{-9}\,\unit{C}}$，A、B带同种电荷（均为负）。\par B（$-4.0\times10^{-9}\,\unit{C}$）是把两电荷量的绝对值直接取平均（$\dfrac{3.0+5.0}{2}$）而丢掉“异号先抵消”这一步；C（$+1.0\times10^{-9}\,\unit{C}$）是抵消对了、绝对值 $2.0\times10^{-9}$ 平分得 $1.0\times10^{-9}$ 但把符号配反（净电荷为负）；D把“一正一负接触”直接当成“全部抵消、电荷消失”——抵消只发生在等量异号时，且即便完全抵消也只是代数和为零，电荷并没有消失（教材第4页中和表述）。故选A。"
DETAIL["练-课时91-14"] = r"\textbf{（1）}丙原来不带电，与甲接触后两者完全相同、电荷平分，故分开后甲、丙各带 $+2.5\times10^{-9}\,\unit{C}$。由此\textbf{逆推}甲在与丙接触前（即甲、乙刚分开瞬间）所带的电荷量 $q_{1}$：$q_{1}=2\times(+2.5\times10^{-9}\,\unit{C})=\mathbf{+5.0\times10^{-9}\,\unit{C}}$（甲带正电）。甲、乙起初相互接触且都不带电，系统电荷的代数和为零；感应分离过程中电荷只是在两球之间转移，没有电荷逸出到球外（教材第4页电荷守恒定律），故分开后二者必带\textbf{等量异号}电荷，乙的电荷量 $q_{2}=-q_{1}=\mathbf{-5.0\times10^{-9}\,\unit{C}}$。校验：$q_{1}+q_{2}=+5.0\times10^{-9}\,\unit{C}-5.0\times10^{-9}\,\unit{C}=0$，与分开前的总电荷一致。\par \textbf{（2）}P带\textbf{负电}。理由：甲是靠近P的一端（近端），由（1）知甲带正电；教材第3页——导体靠近带电体的一端带\textbf{异种}电荷、远离的一端带\textbf{同种}电荷，近端电性与施带电体相反，故P带负电。微观上：P上多余的电子排斥金属球中的自由电子，自由电子被推离P的一侧，使远端（乙）积有多余电子而带负电、近端（甲）缺少电子而带正电，与（1）所得“甲正、乙负”完全一致（两问互证）。"
DETAIL["练-课时91-15"] = r"\textbf{（1）}玻璃棒带正电。分开前甲、乙中的自由电子受到玻璃棒上正电荷的作用，\textbf{向靠近玻璃棒的一端（甲）移动}；保持玻璃棒不动把甲、乙分开，甲因有多余电子而带\textbf{负电}，乙因缺少电子而带\textbf{正电}。甲、乙起初整体电中性、电荷代数和为零，感应只是把电荷从导体的一部分转移到另一部分（教材第4页），没有电荷离开两球，故二者所带电荷量\textbf{大小相等、电性相反}，即 $q_{1}=q_{2}$；记 $q_{1}=q_{2}=q$，则分开瞬间甲 $=-q$、乙 $=+q$。\par \textbf{（2）}按两次接触逐步记电荷量（完全相同金属球接触后各得两球接触前电荷量代数和的一半）：第一步，乙（$+q$）与不带电的丙接触后分开：乙＝丙＝$+\dfrac{q}{2}$；第二步，甲（$-q$）与此时带 $+\dfrac{q}{2}$ 的丙接触后分开：甲＝丙＝$\dfrac{-q+\dfrac{q}{2}}{2}=\mathbf{-\dfrac{q}{4}}$。由题给丙的最终电荷量 $-1.0\times10^{-9}\,\unit{C}$：$-\dfrac{q}{4}=-1.0\times10^{-9}\,\unit{C}$，即 $q=\mathbf{4.0\times10^{-9}\,\unit{C}}$（$q_{1}=4.0\times10^{-9}\,\unit{C}$）。于是操作结束后的末态为：甲 $=-\dfrac{q}{4}=\mathbf{-1.0\times10^{-9}\,\unit{C}}$，丙 $=\mathbf{-1.0\times10^{-9}\,\unit{C}}$，乙 $=\dfrac{q}{2}=\mathbf{+2.0\times10^{-9}\,\unit{C}}$。守恒校验：甲＋乙＋丙 $=(-1.0+2.0-1.0)\times10^{-9}\,\unit{C}=0$，与分开瞬间（以及最初不带电）的总电荷一致。\par \textbf{（3）分类讨论：仍能唯一确定。}丙的最终电荷量并非可正可负——它由物理链锁定：甲与丙接触前，二者总电荷 $=-q+\dfrac{q}{2}=-\dfrac{q}{2}<0$，均分后丙必带\textbf{负}电，即丙末 $=-\dfrac{q}{4}$ 恒为负值。所以“丙所带电荷量的大小为 $1.0\times10^{-9}\,\unit{C}$”这一读数只能对应丙末 $=-1.0\times10^{-9}\,\unit{C}$，解得 $q_{1}=4.0\times10^{-9}\,\unit{C}$，唯一。反之，若不加论证就把读数写成 $+1.0\times10^{-9}\,\unit{C}$（这是本题的主要失分支），则 $-\dfrac{q}{4}=+1.0\times10^{-9}\,\unit{C}$ 给出 $q=-4.0\times10^{-9}\,\unit{C}$，与 $q$ 表示“电荷量的大小”（正值）矛盾，同时也与（1）中“甲必带负电、乙必带正电”的感应判定相矛盾，\textbf{该支必须舍去}。即：测量只给大小时 $\pm$ 两支在代数上并存，但\textbf{感应链决定了末值的符号}，物理约束使其中一支不成立——本题的难正在这一层“设未知量、按链定符号、据约束取舍”，而不在计算量。"
DETAIL["练-课时91-16"] = r"\textbf{（1）}A、B起初相互接触且都不带电，总电荷的代数和为零；分开瞬间电荷只在两球之间转移，故A、B带\textbf{等量异号}电荷（教材第4页电荷守恒定律）。由A $=+8.0\times10^{-9}\,\unit{C}$ 得 $\mathbf{B=-8.0\times10^{-9}\,\unit{C}}$。电性互证：橡胶棒带负电，它排斥导体中的自由电子，自由电子被推离到远端，故近端A因缺少电子带正电、远端B因多余电子带负电，与A $=+8.0\times10^{-9}\,\unit{C}$ 相符（教材第3页：近端异种、远端同种）。以下记A $=+q$、B $=-q$、C $=0$（$q=8.0\times10^{-9}\,\unit{C}$）。每次接触后两球各得接触前代数和的一半。\par \textbf{（2）}可选的球对有三对：A-C、B-C、A-B；两次操作须取不同的两对，先后有序，共 $3\times2=\mathbf{6}$ 个操作序，逐一计算（数值单位均为 $\times10^{-9}\,\unit{C}$）：\par 序①（先A、C，后A、B）：A、C接触后各 $+4.0$（B $=-8.0$）；再A、B接触：$\dfrac{+4.0-8.0}{2}=-2.0$，末态A $=-2.0$、B $=-2.0$、$\mathbf{C=+4.0}$；\par 序②（先A、C，后B、C）：A＝C＝$+4.0$；再B、C接触：$\dfrac{-8.0+4.0}{2}=-2.0$，末态A $=+4.0$、B $=-2.0$、$\mathbf{C=-2.0}$；\par 序③（先B、C，后A、C）：B、C接触后各 $-4.0$（A $=+8.0$）；再A、C接触：$\dfrac{+8.0-4.0}{2}=+2.0$，末态A $=+2.0$、B $=-4.0$、$\mathbf{C=+2.0}$；\par 序④（先B、C，后A、B）：B＝C＝$-4.0$；再A、B接触：$\dfrac{+8.0-4.0}{2}=+2.0$，末态A $=+2.0$、B $=+2.0$、$\mathbf{C=-4.0}$；\par 序⑤（先A、B，后A、C）：A、B接触后各 $0$（等量异号抵消，代数和仍为零，电荷未消失），C仍为 $0$，末态三球均不带电，$\mathbf{C=0}$；\par 序⑥（先A、B，后B、C）：同序⑤，A、B接触后已全为 $0$，末态三球均不带电，$\mathbf{C=0}$。\par 合计：\textbf{C末值的可能值为 $+4.0\times10^{-9}\,\unit{C}$、$+2.0\times10^{-9}\,\unit{C}$、$0$、$-2.0\times10^{-9}\,\unit{C}$、$-4.0\times10^{-9}\,\unit{C}$ 共五个}（六个序中 $0$ 由序⑤⑥共有）；$|C|$ 最大 $=4.0\times10^{-9}\,\unit{C}$，只在“序①（先A、C后A、B）”取得——其机理是C只与带正电的A接触过、从未与B接触，把A的一半电荷留在自己身上。守恒校验（六序逐一）：末态三球电荷代数和均为 $0$，与总电荷始终为零一致。\par \textbf{（3）不能}（指三球都带同种电荷）。三球构成的系统与外界没有电荷交换，任何一次接触操作前后总电荷的代数和保持不变，本件中该恒量 $=0$（分开瞬间 $+q-q+0=0$）。若三球都带正电，则代数和 $>0$；若都带负电，则代数和 $<0$；两者都与“代数和恒为零”矛盾，故无论按哪种顺序、操作多少次都不可能使三球同时带同种电荷。\par 补充辨别：三球电荷\textbf{完全相同}的情形是存在的，即三球都为 $0$（先让A、B接触中和即可，序⑤⑥），但“都不带电”不等于“都带同种电荷”——题目此处考查的正是守恒这一必要条件与可实现操作序之间的对照：\textbf{懂守恒者一句判定，只背均分结论者须穷举六序仍易漏}。"
for _k, _s in [("练-课时91-8", "命制-P1-9.1-简-1"), ("练-课时91-9", "命制-P1-9.1-简-2"),
               ("练-课时91-10", "命制-P1-9.1-简-3"), ("练-课时91-14", "命制-P1-9.1-中-1"),
               ("练-课时91-15", "命制-P1-9.1-难-1"), ("练-课时91-16", "命制-P1-9.1-难-2")]:
    DETAIL_SRC[_k] = _s
# ---- 9.2/9.3（命制-9.2+9.3-三题-详解.md「详解」栏；R1 去 Python 校核括注／R2 书N→教材第N页／
#      R3 unicode→数学模＋→箭头改词＋＋连接词改、／R4 其余逐字＋\textbf 承粗体＋\par 分段） ----
DETAIL["练-课时92-10"] = r"\textbf{第一步（接触均分，9.1 前序工具）}：A、B 为两个完全相同的金属球，接触后电荷重新分配并均分。接触前两球带\textbf{同种}电荷，不发生中和，总电荷量＝$(+2.0\times10^{-8}\,\unit{C})+(+4.0\times10^{-8}\,\unit{C})=+6.0\times10^{-8}\,\unit{C}$；分开后每球带 $+3.0\times10^{-8}\,\unit{C}$。\par \textbf{第二步（库仑定律两次代入取比，教材第8页）}：放回原处，间距仍为 $r$，故接触前 $F=kq_{1}q_{2}/r^{2}=k\times(2.0\times10^{-8})\times(4.0\times10^{-8})/r^{2}=k\times8.0\times10^{-16}/r^{2}$；接触后 $F'=kq'^{2}/r^{2}=k\times(3.0\times10^{-8})^{2}/r^{2}=k\times9.0\times10^{-16}/r^{2}$。\par $k$、$r$ 均不变，故 $\mathbf{F':F=9.0:8.0=9:8}$——接触均分不改变电荷\textbf{总量}（$+6.0\times10^{-8}\,\unit{C}$ 不变），但把两球电荷量的\textbf{乘积}从 8.0 个（$10^{-8}\,\unit{C}$）$^{2}$ 变为 9.0 个（$10^{-8}\,\unit{C}$）$^{2}$，静电力变大。\par 逐项判伪：A（$8:9$）把比值取反（算成 $F:F'$）；B（$1:1$）落入「接触只使电荷总量不变、误以为电荷量乘积也不变因而力不变」的迷思——总量守恒与乘积守恒是两回事；D（$9:4$）把接触前的力误取为只与小球 A 的电荷量比较（$3^{2}/2^{2}$），漏掉了乘积 $q_{1}q_{2}$ 中的 $q_{2}$。故选 C。"
DETAIL_SRC["练-课时92-10"] = "命制-P1-9.2-简-1"
DETAIL["练-课时93-9"] = r"真空中点电荷周围各点场强由点电荷场强公式（教材第13~14页）给出：$E=\dfrac{kQ}{r^{2}}=(9.0\times10^{9}\,\unit{N\cdot m^{2}/C^{2}})\times(1.0\times10^{-8}\,\unit{C})/(0.30\,\unit{m})^{2}=90/0.09\,\unit{N/C}=\mathbf{1.0\times10^{3}\,\unit{N/C}}$。\par 方向：场强方向规定为该点正电荷所受静电力的方向；正点电荷的电场沿连线由 Q 指向四周（辐射状），故 P 点场强\textbf{沿 QP 连线由 Q 指向 P}。\par 逐项判伪：B（$3.0\times10^{2}$）漏掉 $r$ 的平方（把 $r^{2}$ 当成 $r$：$90/0.30=300$）；C 大小对而方向反（「由 P 指向 Q」指向场源，是负点电荷电场的形态）；D 两处皆错——$9.0\times10^{3}=90/0.01$ 系把 $r$ 误读为 $0.10\,\unit{m}$ 的读数错、且方向反。故选 A。"
DETAIL_SRC["练-课时93-9"] = "命制-P1-9.3-简-1"
DETAIL["练-课时93-10"] = r"电场强度定义式（教材第11~12页）：$E=F/q$。代入：$E=6.0\times10^{-4}\,\unit{N}/2.0\times10^{-8}\,\unit{C}=\mathbf{3.0\times10^{4}\,\unit{N/C}}$。\par 方向：\textbf{正}试探电荷在该点所受静电力方向即该点场强方向，A 项方向表述正确。\par B 项前半句数值对、后半句错——电场强度由\textbf{电场本身}（场源与位置）决定，与是否放入试探电荷、放入电荷量的多少无关；改放 $4.0\times10^{-8}\,\unit{C}$ 的正试探电荷，它受的静电力加倍为 $1.2\times10^{-3}\,\unit{N}$，但 $F/q$ 比值不变，P 点场强仍为 $3.0\times10^{4}\,\unit{N/C}$。\par C 项把定义式倒置（$q/F=2.0\times10^{-8}/6.0\times10^{-4}=3.3\times10^{-5}$），且方向错（正试探电荷受力方向与场强方向相同，不是相反）。\par D 项错——移走试探电荷只是不再有「受力的显示」，场源仍在，P 点场强不变（场是客观存在，试探电荷只是检测工具，定义式本身即以「放入试探电荷测 F、再除以 q」为操作，除出的 E 属于电场不属于试探电荷）。\par 故选 A。"
DETAIL_SRC["练-课时93-10"] = "命制-P1-9.3-简-2"
# ---- 9.4（命制-9.4-九题.md「详解」栏；简1/2/5~8 纯文字 R2/R4，简3/4 填空同制，难-1 R3 逐项转换） ----
DETAIL["练-课时94-3"] = r"导体放入电场后，自由电子受电场力定向逆场移动，在两端积累感应电荷，感应电荷的附加电场与原外电场在导体内部叠加；平衡的标志正是导体内自由电荷不再定向移动，即导体内部各点合场强处处为零（不是仅中心为零，D 误；方向向左或向右都存在残余场强，则电荷仍会移动，B、C 误）。故选 A。"
DETAIL_SRC["练-课时94-3"] = "命制-P1-9.4-简-1"
DETAIL["练-课时94-4"] = r"静电平衡导体内部场强处处为零，在导体内部取高斯面可知其内无净电荷，故净电荷只能分布在外表面；空腔内无其他电荷，内表面不会出现感应电荷（若有异号电荷贴在内表面，就会在内表面内侧存在电场线终点，与「内表面无源荷」矛盾）。故电荷全部在外表面，A（体内分布）、C（内表面带电）、D（集中于中心）皆误。选 B。"
DETAIL_SRC["练-课时94-4"] = "命制-P1-9.4-简-2"
DETAIL["练-课时94-5"] = r"静电平衡导体表面是「电荷不再沿表面移动」的状态。若表面外侧场强有切向（沿表面）分量，表面自由电荷将沿表面定向移动，平衡即被破坏；故平衡时表面外侧电场线只能处处与导体表面垂直，填「垂直」；第二空即矛盾所在，填「沿导体表面（定向）移动」。"
DETAIL_SRC["练-课时94-5"] = "命制-P1-9.4-简-3"
DETAIL["练-课时94-6"] = r"空腔导体处于外场中，壳壁内合场强为零，腔内无源电荷、腔内亦无电场线穿入，故空腔内部场强处处为零——这就是静电屏蔽；由于屏蔽只依赖「闭合导体壳」，导体壳上的感应电荷把外电场「挡住」（外场与感应场在壳内叠加归零），与壳是否接地无关，故\textbf{不接地}也能屏蔽外场。金属网罩孔洞不改变「闭合导体包围空区」的本质，罩内场强同样处处为零，与球壳结论相同。"
DETAIL_SRC["练-课时94-6"] = "命制-P1-9.4-简-4"
DETAIL["练-课时94-7"] = r"腔内 $+q$ 使内表面感应出负电荷；球壳原不带电，由电荷守恒外表面必带等量正电，外表面电荷在壳外空间激发电场——即「内场可出外（不接地时）」，A 误、B 对。接地时只是把外表面的电荷导入大地，使外表面不带电、壳外不再有 $+q$ 引起的电场，但\textbf{内表面的感应负电荷因 $+q$ 束缚仍在}，C 说「内外表面都无电荷」误。D 把壳的作用抹掉，违背屏蔽机理，误。故选 B。"
DETAIL_SRC["练-课时94-7"] = "命制-P1-9.4-简-5"
DETAIL["练-课时94-8"] = r"导体表面越尖（曲率半径越小）的地方电荷越密集、附近场强越强，越容易使空气电离放电。A（点火器尖电极）、C（除尘细金属丝电晕放电）、D（避雷针以尖端引雷入地）都是\textbf{主动利用}尖端放电；只有 B 把高压设备金属表面做成光滑球形、增大曲率半径、削弱表面场强，防止不必要的尖端放电漏电，属「防止」。故选 B。"
DETAIL_SRC["练-课时94-8"] = "命制-P1-9.4-简-6"
DETAIL["练-课时94-9"] = r"秋冬干燥时，人体与衣物摩擦起电、电荷难以散失，积累到一定程度击穿空气产生火花放电。保持湿度后，空气与物体表面吸附水膜使静电随时导走、不易积累，A 合理。B（快速用力摩擦）加剧起电、D（涂易积累电荷的绝缘粉）加剧积累，均使危害增大。C 的说法错误：接触墙壁（尤其接地墙体）能把身体所带电荷导走，是有效做法，「没有任何道理」判误。故选 A。"
DETAIL_SRC["练-课时94-9"] = "命制-P1-9.4-简-7"
DETAIL["练-课时94-10"] = r"复印原理的落点＝带相反电荷的墨粉在静电作用下被吸附到「字迹暗区」的带电鼓面上（异号相吸），故 B 对；重力、万有引力、空气浮力都不随「明暗电荷图形」变化，不能形成按字迹的分布，A、C、D 误。故选 B。"
DETAIL_SRC["练-课时94-10"] = "命制-P1-9.4-简-8"
DETAIL["练-课时94-16"] = r"\textbf{（1）}$q_{1}$ 使内表面感应出异号电荷，高面包住腔内电荷，故内表面总量为 $\mathbf{-q_{1}=-3.0\times10^{-9}\,\unit{C}}$；球壳原不带电，内表面每得 $-q_{1}$，外表面必等量异号补足（电荷守恒），故外表面总量为 $\mathbf{+q_{1}=+3.0\times10^{-9}\,\unit{C}}$。分布均匀性：内表面因 $q_{1}$ 恰在腔\textbf{心}、几何对称，电荷\textbf{均匀}分布；外表面本应均匀，但受壳外 $q_{2}$ 的排斥，正电荷被推离 $q_{2}$ 一侧，故外表面\textbf{不均匀}（背离 $q_{2}$ 的一侧更密）。（外表面总量 $+q_{1}$ 由守恒锁定，与 $q_{2}$ 大小位置无关。）\par \textbf{（2）}B 在金属壁内，静电平衡导体内部合场强处处为零，故 $\mathbf{E_{B}=0}$。A 在空腔内，场强只由 $q_{1}$ 与内表面电荷共同决定：内表面 $-q_{1}$ 均匀分布（＝均匀带电球面）在腔内不产生场（叠加为零），壳外 $q_{2}$ 与外表面的场又被壳屏蔽、进不了腔，故 A 点场强＝$q_{1}$ 单独所生，$E_{A}=\dfrac{kq_{1}}{r^{2}}=(9.0\times10^{9}\times3.0\times10^{-9})/0.3^{2}\,\unit{m^{2}}=27/0.09=\mathbf{300\,\unit{N/C}}$，方向沿 $q_{1}$ 与 A 的连线、由 $q_{1}$ 指向 A（$q_{1}$ 为正，场强背离之）。\par \textbf{（3）分类讨论}：这是本题分类核心，落在「外表面电荷随接地与否改变」上：\par \textbf{①S 闭合}：球壳与大地连成一个导体，$q_{1}$ 靠内表面束缚住 $-q_{1}$，而外表面那份 $+q_{1}$ 失去束缚、经地线\textbf{流入大地}，外表面电荷量由 $+q_{1}$ 变为约 $\mathbf{0}$；于是「内场经外表面传出」的通道被切断——球壳外部空间（$q_{2}$ 侧）\textbf{不再有由 $q_{1}$ 引起的电场}（该侧电场只剩 $q_{2}$ 自己产生）。\par \textbf{②S 先闭合再断开}：闭合时外表面已归零，断开地线后这「零」被锁定，球壳净带电变为 $-q_{1}$（全在内表面）；外表面电荷仍为约 $\mathbf{0}$，外部同样\textbf{无由 $q_{1}$ 引起的电场}。即无论「正在接地」还是「接了又断」，只要外表面被放空过，$q_{1}$ 就不再影响壳外——\textbf{这就是「屏蔽内场必须接地」的机理}。\par \textbf{对照 S 一直断开（第（1）问）}：外表面带 $+q_{1}$，壳外 $q_{2}$ 侧\textbf{存在}由 $q_{1}$（经外表面）引起的电场。三支对比：接地与否决定「内场出不出得来」，而「外场进不进得来」（A、B 点）无论接地与否都进不来——屏蔽的\textbf{方向性}在本题两支对照中同时立起。"
DETAIL_SRC["练-课时94-16"] = "命制-P1-9.4-难-1"

# 适配保真抽断言（源文指纹逐字保留证据）＋命制源节存在性
FPRINT = {
    "练-课时91-8": ["近端带异号电荷故相吸", "混为一谈", "摩擦并不创造电荷"],
    "练-课时91-9": ["不是比荷", "指数部分", "单位配套关系"],
    "练-课时91-10": ["异号先抵消", "电荷并没有消失", "净电荷由两球平分"],
    "练-课时91-14": ["两问互证", "没有电荷逸出到球外", "近端电性与施带电体相反"],
    "练-课时91-15": ["该支必须舍去", "大小相等、电性相反", "而不在计算量"],
    "练-课时91-16": ["懂守恒者一句判定", "把A的一半电荷留在自己身上", "与总电荷始终为零一致"],
    "练-课时92-10": ["总量守恒与乘积守恒是两回事", "把比值取反", "静电力变大"],
    "练-课时93-9": ["辐射状", "指向场源", "的平方"],
    "练-课时93-10": ["除出的 E 属于电场不属于试探电荷", "受力的显示", "静电力加倍"],
    "练-课时94-3": ["平衡的标志", "合场强处处为零", "残余场强"],
    "练-课时94-4": ["高斯面", "电场线终点", "皆误"],
    "练-课时94-5": ["切向（沿表面）分量", "平衡即被破坏", "第二空即矛盾所在"],
    "练-课时94-6": ["静电屏蔽", "叠加归零", "闭合导体包围空区"],
    "练-课时94-7": ["内场可出外", "导入大地", "违背屏蔽机理"],
    "练-课时94-8": ["电离放电", "主动利用", "增大曲率半径"],
    "练-课时94-9": ["击穿空气产生火花放电", "吸附水膜", "均使危害增大"],
    "练-课时94-10": ["异号相吸", "明暗电荷图形", "不能形成按字迹的分布"],
    "练-课时94-16": ["高面包住腔内电荷", "流入大地", "方向性"],
}
for _k, _fps in FPRINT.items():
    for _fp in _fps:
        assert _fp in DETAIL[_k], '适配丢失源文指纹 %r (%s)' % (_fp, _k)
for _k, _s in DETAIL_SRC.items():
    _f = os.path.join(MZ, '命制-9.1-六题-详解.md' if _s.startswith('命制-P1-9.1')
                      else ('命制-9.2+9.3-三题-详解.md' if _s.startswith('命制-P1-9.2') or _s.startswith('命制-P1-9.3')
                            else '命制-9.4-九题.md'))
    assert ('### ' + _s) in io.open(_f, encoding='utf-8').read(), '命制源缺节: %s' % _s
for _k, _d in DETAIL.items():
    for _r in RESIDUE:
        assert _r not in _d, '工作流残留/险字形 %r in %s' % (_r, _k)


def est_lines(tex):
    plain = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})*', '', tex)
    plain = re.sub(r'[${}]', '', plain)
    return math.ceil(len(plain) / LINE_UNITS) + 1


# ========== ③ 副本树就位（cp 快照/figs/原印面＋overlay 本地挂载 md5 断言） ==========
def setup_tree():
    h = hashlib.md5(io.open(STY_SRC, 'rb').read()).hexdigest()
    assert h == STY_MD5, 'overlay sty md5 断言破：%s' % h
    n = 0
    for piece, pfx, nums in PIECES_LX + [PIECE_TUO]:
        srcdir = os.path.join(CJ, '练习件', piece) if pfx.startswith('练') else os.path.join(CJ, '拓展册')
        d = os.path.join(TREE, piece)
        os.makedirs(d, exist_ok=True)
        shutil.copyfile(os.path.join(srcdir, 'main.tex'), os.path.join(d, 'main.src.tex'))
        shutil.copyfile(os.path.join(srcdir, 'main.tex'), os.path.join(d, 'main.tex'))
        shutil.copyfile(os.path.join(srcdir, 'main.pdf'), os.path.join(d, 'main-原印面.pdf'))
        shutil.copyfile(STY_SRC, os.path.join(d, 'qp-m3p-overlay.sty'))
        fsrc, fdst = os.path.join(srcdir, 'figs'), os.path.join(d, 'figs')
        if os.path.isdir(fsrc) and not os.path.isdir(fdst):
            shutil.copytree(fsrc, fdst)
        n += 1
    return n


# ========== ④ 批插 ==========
HOOK = ['', '% —— 换装 overlay 挂接（换装正装波4b；七模块后、\\begin{document} 前；sty 本地挂载 md5 ' + STY_MD5[:8] + '）——',
        '\\usepackage{qp-m3p-overlay}']


def ansblock_lines(key, label, value, detail, shang, shang_note, ruled, est):
    ls = []
    if ruled:
        ls.append('\\ansblockgrayfalse %% 括线模：长详解块（判据 草案§1.2.5，估高 %d 行）' % est)
    ls.append('\\begin{ansblock}[%s]' % key)
    ls.append('%% ans:%s' % key)
    if shang:
        ls.append(SHANG10 + '%% %s' % shang_note)
    item = '\\ansitem{%s}{%s}' % (label, value)
    if detail:
        item += '\\ansnote{详解}{%s}' % detail
    ls.append(item)
    ls.append('\\end{ansblock}')
    if ruled:
        ls.append('\\ansblockgraytrue %% ─ 括线模束')
    return ls


def insert_lines(lines, at, blk):
    lines[at:at] = [b + '\n' for b in blk]


def pure_insert_assert(out, src, extra_changed=b''):
    new_lines, orig = out.splitlines(), src.splitlines()
    it = iter(new_lines)
    for ol in orig:
        for nl in it:
            if nl == ol:
                break
        else:
            sys.exit('原件行被删改: %r' % ol[:60])
    return len(new_lines) - len(orig)


def migrate_lian(piece, pfx, nums, kmap, notes):
    d = os.path.join(TREE, piece)
    src = io.open(os.path.join(d, 'main.src.tex'), encoding='utf-8').read()
    lines = src.splitlines(keepends=True)
    log = []
    figs_i = [i for i, l in enumerate(lines) if 'qp-figs.tex' in l]
    assert len(figs_i) == 1, '%s qp-figs 钩点不唯一' % piece
    insert_lines(lines, figs_i[0] + 1, HOOK)
    starts = [i for i, l in enumerate(lines) if re.match(r'^\\tihao\{(\d+)\}', l)]
    assert len(starts) == len(nums), '%s 题号数 %d≠%d' % (piece, len(starts), len(nums))
    cuts = sorted(starts
                  + [i for i, l in enumerate(lines) if l.startswith('\\dangbadge')]
                  + [i for i, l in enumerate(lines) if '\\end{multicols}' in l]
                  + [i for i, l in enumerate(lines) if l.startswith('\\tielue')])
    bounds, calcset = {}, set()
    for i in starts:
        n = int(re.match(r'^\\tihao\{(\d+)\}', lines[i]).group(1))
        j = next(k for k in cuts if k > i)
        tail = max(k for k in range(i, j) if lines[k].strip() and not lines[k].lstrip().startswith('%'))
        assert n not in bounds
        bounds[n] = tail
        if re.match(r'^\\tihao\{%d\}\\tieside\{[^}]*?(计算题|解答题)' % n, lines[i]):
            calcset.add(n)
    for n in sorted(calcset):
        assert '\\xiexwei' in lines[bounds[n]], '%s 题%d 计算块尾非书写位行' % (piece, n)
    log.append(('计算/解答书写位', '、'.join('\\tihao{%d}' % n for n in sorted(calcset)) or '无',
                '块尾＝\\xiexwei 行后（书写位不废）'))
    blk_lines = 0
    modes, ests = {}, {}
    for n in reversed(nums):
        key = '%s-%d' % (pfx, n)
        label, value = kmap[key]
        detail = DETAIL.get(key) or notes.get(key, '')
        est = est_lines(value + detail)
        ests[key] = est
        ruled = est > RULED_LINES
        modes[key] = '括线' if ruled else '灰底'
        if key in DETAIL or key in notes:
            log.append((key, '估高 %d 行 → %s%s' % (est, modes[key],
                        '（承重墙判据强制，超断点预钉「其余全灰底」面）' if ruled and key not in DETAIL else ''),
                        (DETAIL_SRC.get(key, '册载注记') + ('＋册载注记' if key in DETAIL and key in notes else ''))))
        blk = ansblock_lines(key, label, value, detail, n >= 10, '题%d 起双位档（body.tex 册载同值，块内局部）' % n,
                             ruled, est)
        blk_lines += len(blk)
        insert_lines(lines, bounds[n] + 1, blk)
    out = ''.join(lines)
    assert out.count('\\end{multicols}') == 1, '%s multicols 计数异常' % piece
    out = out.replace('\\end{multicols}', '\\tailfill\n\n\\end{multicols}')
    log.append(('尾块', '\\tailfill 于 \\end{multicols} 后·\\end{document} 前（波2 改判：试迁栏内贴尾课时10 Overfull 27.99pt 案销项）', ''))
    added = pure_insert_assert(out, src)
    assert added == len(HOOK) + blk_lines + 2, '%s 插入行数异常 %d' % (piece, added)
    assert out.count('\\begin{ansblock}[%s-' % pfx) == len(nums)
    assert len(re.findall(r'^%% ans:(%s-\d+)$' % re.escape(pfx), out, re.M)) == len(nums)
    return out, log, modes, ests


def migrate_tuo(kmap, notes):
    piece, pfx, nums = PIECE_TUO
    d = os.path.join(TREE, piece)
    src = io.open(os.path.join(d, 'main.src.tex'), encoding='utf-8').read()
    out_lines = src.splitlines(keepends=True)
    log = []
    figs_i = [i for i, l in enumerate(out_lines) if 'qp-figs.tex' in l]
    assert len(figs_i) == 1
    insert_lines(out_lines, figs_i[0] + 1, HOOK)

    def is_boundary(st):
        return st.startswith(('\\tihao{', '\\zu{', '\\columnbreak', '\\end{multicols}'))
    blk_lines, modes, ests = 0, {}, {}
    for n in nums:
        key = '拓-%03d' % n
        label, value = kmap[key]
        assert int(label) == n, '拓 label 错位 %s' % key
        detail = DETAIL.get(key) or notes.get(key, '')
        est = est_lines(value + detail)
        ests[key] = est
        ruled = est > RULED_LINES
        modes[key] = '括线' if ruled else '灰底'
        tag = '\\tihao{%d}' % n
        hits = [i for i, l in enumerate(out_lines) if l.strip().startswith(tag)]
        assert len(hits) == 1, '题锚不唯一(%d): %s' % (len(hits), key)
        i = hits[0]
        b = next(j for j in range(i + 1, len(out_lines)) if is_boundary(out_lines[j].strip()))
        blk = ['\\begingroup\\ansblockgrayfalse %% 括线模：长详解块（估高 %d 行）' % est] \
            if ruled else []
        blk += ansblock_lines(key, label, value, detail, n >= 10,
                              '拓-三位号＝双位档（body.tex L469 口径·J1 裁照册加，试迁拓臂未加）' if n >= 10 else '', False, est)
        if ruled:
            blk.append('\\endgroup')
        if key in DETAIL or key in notes:
            log.append((key, '\\tihao{%d} 块界前插·估高 %d 行 → %s' % (n, est, modes[key]),
                        DETAIL_SRC.get(key, '册载注记')))
        blk_lines += len(blk)
        out_lines = out_lines[:b] + [x + '\n' for x in blk] + out_lines[b:]
    out = ''.join(out_lines)
    assert out.count('\\end{multicols}') == 4, '拓 multicols 计数异常'
    j = out.rfind('\\end{multicols}')
    out = out[:j] + '\\tailfill\n\n' + out[j:]
    log.append(('尾块', '\\tailfill 于最后 \\end{multicols} 后·\\end{document} 前（波2 改判）', ''))
    log.append(('J1 双位档', '拓-010~046 照 body.tex L469 加 SHANG10 块内局部（试迁拓臂未加＝本波差异面，报告登记）', '40 块'))
    added = pure_insert_assert(out, src)
    assert added == len(HOOK) + blk_lines + 2, '拓 插入行数异常 %d' % added
    assert out.count('\\begin{ansblock}[拓-') == 46
    assert len(re.findall(r'^% ans:(拓-\d{3})$', out, re.M)) == 46
    return out, log, modes, ests


# ========== ⑤ 拓-31 窄栏改制 4 处（仅迁后 main.tex；main.src.tex 保持原样） ==========
RE_Z31 = re.compile(r'^\\lxopt\{[A-D]．\$E=\\left\|')
# 断点原方＝负号后插 \allowbreak；首跑实证：\left|…\right| 系 inner atom 不可断（压测 Overfull 29.1~71.4pt 四行原样）。
# v2＝\right.-\allowbreak\left. 中裂式；二跑实证：空定界符各吃 \nulldelimiterspace 1.2pt → 84mm 面 X 向 +1.2/+2.4pt 漂。
# v3（终）＝行内 $ 后局部 \nulldelimiterspace=0pt ＋中裂式：真 bin 断点（窄栏得断）＋空定界零宽（印面零漂，
#   像素门机械证）。定界符尺寸两半＝整式同高（结构对称），Y 向实证零漂（负号 y 坐标逐字相同）。
Z31_PRE = None
# v5（终）＝v2 中裂式＋两枚 \kern-1.2pt 对冲空定界符垫宽（\nulldelimiterspace 默认 1.2pt，
#   骨架未改；本引擎对 \left/\right 逐定界符垫付）：frac1 [右界:垫+1.2][kern−1.2] −（bin 断点）
#   [kern−1.2][左界:垫+1.2] frac2 —— 逐 junction 代数抵消＝84mm 印面零漂；窄栏负号后真断点消 Overfull。
Z31_OLD, Z31_NEW = '}-\\frac', '}\\right.\\kern-1.2pt-\\allowbreak\\kern-1.2pt\\left.\\frac'


def reform_z31(out):
    lines = out.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if RE_Z31.match(l)]
    assert len(hits) == 4, '拓-31 选项行 %d≠4' % len(hits)
    reg = []
    for i in hits:
        old = lines[i]
        assert old.count(Z31_OLD) == 1, '拓-31 行 %d 锚位≠1' % (i + 1)
        lines[i] = old.replace(Z31_OLD, Z31_NEW, 1)
        reg.append((i + 1, old.strip(), lines[i].strip()))
    out2 = ''.join(lines)
    assert out2.replace(Z31_NEW, Z31_OLD) == out, '改制不可逆核验失败'
    return out2, reg


# ========== ⑥ 双壳＋拓压测 ==========
SHELL_T = ('% ============================================================\n'
           '% _P_ 换装正装波4b·P1练习拓展·含详解印本（\\showans true＝默认档）→ main-true.pdf\n'
           '% 编译：xelatex main-true.tex（两遍）\n'
           '% ============================================================\n'
           '\\def\\mthreepure{0}\n'
           '\\input{main.tex}\n')
SHELL_P = ('% ============================================================\n'
           '% _P_ 换装正装波4b·P1练习拓展·纯题版（\\mthreepure=1 → overlay [pure] 等效）→ main-pure.pdf\n'
           '% 编译：xelatex main-pure.tex（两遍）\n'
           '% ============================================================\n'
           '\\def\\mthreepure{1}\n'
           '\\input{main.tex}\n')


def strip_t046_wrapper(t):
    ls = t.splitlines(keepends=True)
    i = next(i for i, l in enumerate(ls) if l.startswith('\\begin{ansblock}[拓-046]'))
    assert ls[i - 1].startswith('\\begingroup\\ansblockgrayfalse'), '拓-046 壳头未命中'
    j = next(j for j in range(i, len(ls)) if ls[j].startswith('\\end{ansblock}'))
    assert j + 1 < len(ls) and ls[j + 1].startswith('\\endgroup'), '拓-046 壳尾未命中'
    t2 = ''.join(ls[:i - 1] + ls[i:j + 1] + ls[j + 2:])
    assert t2 != t and '\\ansblockgrayfalse' not in t2, '拓-046 括线壳剥离失败'
    return t2


def to3col(t):
    assert t.count('\\begin{multicols}{2}') == 4
    return t.replace('\\begin{multicols}{2}', '\\begin{multicols}{3}')


def add_global_rule(t):
    return t.replace('\\usepackage{qp-m3p-overlay}',
                     '\\usepackage{qp-m3p-overlay}\n\\ansblockgrayfalse   % 压测：全件括线模（三栏口径拟态）', 1)


def main(argv):
    only = argv[1:]
    if not only or 'setup' in only:
        print('[树] 就位 %d 件（overlay md5 %s 断言过）' % (setup_tree(), STY_MD5[:8]))
    kmap, notes = parse_book()
    want = [16, 15, 15, 16, 46]
    got = [len([k for k in kmap if k.startswith(pfx + '-')]) for _, pfx, _ in PIECES_LX] + \
          [len([k for k in kmap if re.match(r'^拓-\d{3}$', k)])]
    assert got == want, '键账域计数 %s≠%s' % (got, want)
    print('[册] 键 %d（91=16／92=15 无-2／93=15 无-2／94=16／拓=46）｜注记 %d 处' % (len(kmap), len(notes)))
    todo = [p for p in [x[0] for x in PIECES_LX] + [PIECE_TUO[0]]
            if not only or any(t in p for t in only if t != 'setup')]
    for piece in todo:
        if piece == PIECE_TUO[0]:
            out, log, modes, ests = migrate_tuo(kmap, notes)
        else:
            p, pfx, nums = next(x for x in PIECES_LX if x[0] == piece)
            out, log, modes, ests = migrate_lian(piece, pfx, nums, kmap, notes)
        # 拓-31 改制（纯插入断言之后施加，可逆核验）
        zreg = []
        if piece == PIECE_TUO[0]:
            out, zreg = reform_z31(out)
            for ln, old, new in zreg:
                log.append(('拓-31窄栏改制', 'L%d（53.5mm 三栏压测探针 4 Overfull 位）\\right.-\\allowbreak\\left. 中裂式'
                            '（断点原方 \\allowbreak inner atom 不可断·首跑实证升级，见件头注）' % ln,
                            old[:56] + ' ⇒ ' + new[:80]))
        d = os.path.join(TREE, piece)
        with io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('% —— 换装正装波4b 件（由 main.src.tex 机器迁移生成；正件只读对照；拓-31 改制仅本件）——\n' + out)
        for name, head in (('main-true.tex', SHELL_T), ('main-pure.tex', SHELL_P)):
            with io.open(os.path.join(d, name), 'w', encoding='utf-8', newline='\n') as f:
                f.write(head.replace('_P_', piece))
        if piece == PIECE_TUO[0]:
            var = {'压测A-三栏灰底': to3col(strip_t046_wrapper(out)),
                   '压测B-两栏括线': add_global_rule(out),
                   '压测C-三栏括线': to3col(add_global_rule(out))}
            for name, text in var.items():
                with io.open(os.path.join(d, name + '.tex'), 'w', encoding='utf-8', newline='\n') as f:
                    f.write('%% —— 压测变体（换装件派生·含拓-31 改制；只作版面压测，非印本候选勿入重发清单）——\n' + text)
                with io.open(os.path.join(d, name + '-true.tex'), 'w', encoding='utf-8', newline='\n') as f:
                    f.write('%% 压测双壳（\\mthreepure=0）→ %s-true.pdf\n\\def\\mthreepure{0}\n\\input{%s.tex}\n'
                            % (name, name))
        # 险字形终检（剥注释后的代码面——正件头注 ✓/² 系旧批注不排印、只读不改；试迁口径承 emitted 面）
        code_face = '\n'.join(re.sub(r'(?<!\\)%.*$', '', l) for l in out.splitlines())
        for r in RESIDUE:
            assert r not in code_face, '险字形 %r 混入 emitted 代码面 %s' % (r, piece)
        # 模式账钉（断点④）：9.1 六括线键＋拓-046 必括线；9.1≡试迁 10 灰/6 括、拓≡试迁 45 灰/1 括
        if piece == '9.1电荷':
            assert {k for k, v in modes.items() if v == '括线'} == \
                {'练-课时91-%d' % n for n in (8, 9, 10, 14, 15, 16)}, '9.1 模式账≠试迁'
        if piece == PIECE_TUO[0]:
            assert [k for k, v in modes.items() if v == '括线'] == ['拓-046'], '拓 模式账≠试迁'
        nblk = out.count('\\begin{ansblock}')
        nruled = sum(1 for v in modes.values() if v == '括线')
        with io.open(os.path.join(d, '_迁移日志.md'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('# %s 换装迁移日志（正装波4b·P1练习拓展·2026-09-14）\n\n| 键/项 | 锚点/判据 | 值/源 |\n|---|---|---|\n' % piece)
            for row in log:
                a, b, c = (row + ('',))[:3]
                f.write('| %s | %s | %s |\n' % (a, b, str(c).replace('|', '\\|')[:150]))
            f.write('\nansblock %d｜括线 %d／灰底 %d｜tailfill 1｜overlay 钩 1｜拓-31 改制 %d 处\n'
                    % (nblk, nruled, nblk - nruled, len(zreg)))
        print('[迁] %s：ansblock %d（括线 %d）｜日志 %d 行%s'
              % (piece, nblk, nruled, len(log), '｜改制 4 处' if zreg else ''))
        yield_key = (piece, modes, ests)
        ALL.setdefault(piece, yield_key)
    man = {'件账': {p: {'模式': m, '估高': e} for p, (p, m, e) in ALL.items()},
           '键数合计': sum(len(m) for _, (p, m, e) in ALL.items()),
           '括线键': {p: sorted([k for k, v in m.items() if v == '括线']) for p, (p, m, e) in ALL.items()},
           '详解账': {p: sorted([k for k in m if k in DETAIL]) for p, (p, m, e) in ALL.items()},
           'J1': '拓-010~046 SHANG10 照册加（试迁拓臂未加＝差异面）',
           '改制': '拓-31 A~D 四条 \\lxopt 负号后 \\allowbreak（仅迁后 main.tex；84mm 不不断行零漂、53.5mm 得断点）'}
    with io.open(os.path.join(HERE, '_键账-波4b.json'), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    print('==== 批插总读数：ansblock %d／键 %d（括线键数 %d）===='
          % (sum(len(m) for _, (p, m, e) in ALL.items()),
             sum(len(m) for _, (p, m, e) in ALL.items()),
             sum(len(v) for v in man['括线键'].values())))


ALL = {}
if __name__ == '__main__':
    main(sys.argv)
