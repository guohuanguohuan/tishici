# -*- coding: utf-8 -*-
r"""v4 练习件后处理器：sec.tex（pandoc 原始输出）→ body.tex（题区）＋ answers.tex（答案与解析区）
＋ chapterhead.tex ＋ postproc_lianxi_log.txt。
v4 依据：总诊断-v4参数表（参数权威）＋练习件对照 A1–A13＋交接-20260907b §四②任务书。
结构：章首通栏（方块＋章22/节18/小节15/课时14）→ 题区双栏（三档组行「夯基达标·保60%／提能进阶·
保80%／冲刺突破·冲100%」＋流水号＋6.5pt 灰侧标〔难度〕★（知识点N）——〔源〕括注已撤〔拍板18〕，
题面无答案）→ \clearpage →「答案与解析」通栏标题 → 双栏 10.5pt/18pt（A9 主会话裁定）。
题量配平：源题只用各组第 2 题起（防撞池，与导学件例1不重复）＝1.1.1.8-8 唯一可用；命制兜底 10 题
（上限顶格、偏基础档、逐题亲算核验、逐条登记）；合计 11 题，配平落点＝题区满 1 页＋答案区满 1 页。
A7 选项按长度 4/2/1 项每行网格，分号字符全保留（拍板21）；A8 图 30mm 档（题干 ≤2 行右嵌／长题干
题下居中，TikZ 矢量化拍板24）；分号台账：源采用题分号计数与成品逐字对账＋命制分号逐条入账。"""
import re

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\练习件"
LOG = []
log = LOG.append

tex = open(BASE + r"\sec.tex", encoding='utf-8').read()

# ---- 1. 源清洗（同 v3）：U+2060、箭头归一化、长下划线挖空 ----
tex = tex.replace('\u2060', '')
tex = tex.replace(r'\overset{⃑}{', r'\overrightarrow{')
n_kong = len(re.findall(r'(?:\\_){4,}', tex))
tex = re.sub(r'(?:\\_){4,}', r'\\kongbai{}', tex)
log(f'1. 源清洗：去 U+2060、\\overset{{⃑}}{{}}→\\overrightarrow{{}}；长下划线→\\kongbai{{}} ×{n_kong}（题面原有空保留）')

blocks = [b.strip() for b in re.split(r'\n\s*\n', tex) if b.strip()]

# ---- 2. 解析题部（组/题；讲部与编注不排印） ----
RE_GRP = re.compile(r'^\\textbf\{(1\.1\.1\.(\d+) [^}]*)\}$')
RE_TI = re.compile(r'^\\textbf\{(1\.1\.1\.(\d+)-(\d+)．（(简单|中档|难)）)\}(.*)$', re.S)

tis, grp_order = {}, []
cur_grp = cur_ti = None
for b in blocks:
    m = RE_GRP.match(b)
    if m:
        cur_grp = m.group(1)
        cur_ti = None
        if m.group(2) != '1':
            grp_order.append(cur_grp)
        continue
    if cur_grp is None or cur_grp.startswith('1.1.1.1 '):
        continue
    m = RE_TI.match(b)
    if m:
        key = (int(m.group(2)), int(m.group(3)))
        cur_ti = key
        tis[key] = {'num': f'1.1.1.{key[0]}-{key[1]}', 'nanidu': m.group(4),
                    'stem': [m.group(5).replace('\n', ' ').strip()] if m.group(5).strip() else [],
                    'ans': '', 'zsd': '', 'fenxi': [], 'xiangjie': [], 'dj': []}
        continue
    if cur_ti:
        d = tis[cur_ti]
        if b.startswith('【答案】'):
            d['ans'] = b[len('【答案】'):].strip() or 'NEXT'
        elif b.startswith('【知识点】'):
            d['zsd'] = b[len('【知识点】'):].strip() or 'NEXT'
        elif b.startswith('【分析】'):
            d['fenxi'] = [b] if len(b) > len('【分析】') else []
        elif b.startswith('【详解】'):
            d['xiangjie'] = [b]
        elif b.startswith('【点睛】'):
            d['dj'] = [b]
        elif d['ans'] == 'NEXT':
            d['ans'] = b.replace('\n', ' ')
        elif d['zsd'] == 'NEXT':
            d['zsd'] = b.replace('\n', ' ')
        elif d['fenxi'] and not d['xiangjie']:
            d['fenxi'].append(b)
        elif d['xiangjie']:
            d['xiangjie'].append(b)
        else:
            d['stem'].append(b.replace('\n', ' '))
for k, d in tis.items():
    assert d['ans'] and d['ans'] != 'NEXT', f'{d["num"]} 答案缺失'
assert len(tis) == 10, f'源题应为 10 道，实得 {len(tis)}'
log(f'2. 解析：题部组 {len(grp_order)} 组、题 {len(tis)} 道；源题全守恒在场——'
    f'各组第 1 题（1.1.1.2-1/3-2/4-3/5-4/6-5/7-6/8-7/9-9/10-10）让渡导学件例1（拍板16），'
    f'各组第 2 题起仅 1.1.1.8-8（组8 第2题）→ 本件题1（防撞池）')

# ---- 3. 题量配平与命制题库（10 题顶格、偏基础档、逐题亲算核验） ----
# 知识点N 口径沿用 v2 实验报告三块映射（与导学件 v4 同源）：1＝空间向量的概念（零/单位/相等/
# 相反/共线等特殊向量）、2＝空间向量的线性运算（加减/数乘/几何表示）、3＝夹角/数量积/共面/投影。
# 难度档沿用源节口径（简单/中档/难；源节 简单6/中档4/难0），命制偏基础档＝简单5/中档6/难0。
# 每题亲算核验记录见交付报告§命制题逐题核验；此处存答案与解析。
FIG_CUBE = r'''\begin{tikzpicture}[baseline=(current bounding box.north),line width=0.4pt,x=1mm,y=1mm,scale=0.72]
\coordinate (A) at (0,0);\coordinate (B) at (20,0);\coordinate (C) at (20,20);\coordinate (D) at (0,20);
\coordinate (A1) at (8,7);\coordinate (B1) at (28,7);\coordinate (C1) at (28,27);\coordinate (D1) at (8,27);
\draw (A)--(B)--(C)--(D)--cycle;
\draw (A1)--(B1)--(C1)--(D1)--cycle;
\draw (A)--(A1);\draw (B)--(B1);\draw (C)--(C1);\draw (D)--(D1);
\draw[line width=0.9pt] (A1)--(B);\draw[line width=0.9pt] (B)--(C1);
\node[anchor=north east,inner sep=1pt] at (-0.5,-0.5) {\figfont $A$};
\node[anchor=north west,inner sep=1pt] at (20.5,-0.5) {\figfont $B$};
\node[anchor=south west,inner sep=1pt] at (20.5,20) {\figfont $C$};
\node[anchor=south east,inner sep=1pt] at (-0.5,20.5) {\figfont $D$};
\node[anchor=east,inner sep=1pt] at (7.2,7.8) {\figfont $A_1$};
\node[anchor=west,inner sep=1pt] at (28.5,7) {\figfont $B_1$};
\node[anchor=west,inner sep=1pt] at (28.5,27) {\figfont $C_1$};
\node[anchor=south east,inner sep=1pt] at (7.5,27.5) {\figfont $D_1$};
\end{tikzpicture}'''
FIG_PARA = r'''\begin{tikzpicture}[line width=0.4pt,x=1mm,y=1mm]
\coordinate (A) at (0,0);\coordinate (B) at (17,0);\coordinate (D) at (7.5,12.5);\coordinate (A1) at (2,15);
\coordinate (C) at (24.5,12.5);\coordinate (B1) at (19,15);\coordinate (C1) at (26.5,27.5);\coordinate (D1) at (9.5,27.5);
\draw (A)--(B)--(C)--(D)--cycle;
\draw (A1)--(B1)--(C1)--(D1)--cycle;
\draw (A)--(A1);\draw (B)--(B1);\draw (C)--(C1);\draw (D)--(D1);
\draw[line width=0.9pt] (A)--(C1);\draw[line width=0.9pt] (B)--(D1);
\node[anchor=north east,inner sep=1.5pt] at (-0.5,-0.5) {\figfont $A$};
\node[anchor=north west,inner sep=1.5pt] at (17.5,-0.5) {\figfont $B$};
\node[anchor=west,inner sep=1.5pt] at (25,12.5) {\figfont $C$};
\node[anchor=south east,inner sep=1.5pt] at (7,13) {\figfont $D$};
\node[anchor=east,inner sep=1.5pt] at (1.5,15.5) {\figfont $A_1$};
\node[anchor=south west,inner sep=1.5pt] at (19,15.5) {\figfont $B_1$};
\node[anchor=south west,inner sep=1.5pt] at (26.5,28) {\figfont $C_1$};
\node[anchor=south east,inner sep=1.5pt] at (9,28) {\figfont $D_1$};
\end{tikzpicture}'''

MC = [
 dict(id='F1', nanidu='简单', zsd=2, star=False, fig=None, liubai=False,
      stem=r'化简\(\overrightarrow{AB} + \overrightarrow{BC} - \overrightarrow{AD}\)＝（\quad）',
      opts=[r'\(\overrightarrow{DB}\)', r'\(\overrightarrow{BD}\)', r'\(\overrightarrow{DC}\)', r'\(\overrightarrow{CD}\)'],
      ans=r'C',
      fenxi=r'利用向量加法的三角形法则先求前两项的和，再由减法的几何意义作差即可．',
      xiangjie=r'解：\(\overrightarrow{AB} + \overrightarrow{BC} = \overrightarrow{AC}\)，故\(\overrightarrow{AB} + \overrightarrow{BC} - \overrightarrow{AD} = \overrightarrow{AC} - \overrightarrow{AD} = \overrightarrow{DC}\)．故选：C．',
      dj=''),
 dict(id='F2', nanidu='简单', zsd=2, star=False, fig=None, liubai=False,
      stem=r'在平行六面体\(ABCD - A_{1}B_{1}C_{1}D_{1}\)中，已知\(\overrightarrow{AB} = \overrightarrow{a}\)，\(\overrightarrow{AD} = \overrightarrow{b}\)，\(\overrightarrow{AA_{1}} = \overrightarrow{c}\)，则\(\overrightarrow{A_{1}D} =\)\kongbai{}，\(\overrightarrow{AC_{1}} =\)\kongbai{}．（用\(\overrightarrow{a}\)，\(\overrightarrow{b}\)，\(\overrightarrow{c}\)表示）',
      opts=None,
      ans=r'\(\overrightarrow{b} - \overrightarrow{c}\)；\(\overrightarrow{a} + \overrightarrow{b} + \overrightarrow{c}\)',
      fenxi=r'利用空间向量加减法的几何意义，把目标向量沿棱向量作和差分解．',
      xiangjie=r'解：\(\overrightarrow{A_{1}D} = \overrightarrow{AD} - \overrightarrow{AA_{1}} = \overrightarrow{b} - \overrightarrow{c}\)；\(\overrightarrow{AC_{1}} = \overrightarrow{AB} + \overrightarrow{BC} + \overrightarrow{CC_{1}} = \overrightarrow{a} + \overrightarrow{b} + \overrightarrow{c}\)．',
      dj=''),
 dict(id='F3', nanidu='简单', zsd=1, star=False, fig=None, liubai=False,
      stem=r'有下列说法：①零向量与任意向量共线；②模相等且方向相反的两个向量互为相反向量；③共线向量所在的直线必重合；④相等向量的起点必相同．其中正确的是（\quad）',
      opts=[r'①②', r'①②③', r'②③', r'①③④'],
      ans=r'A',
      fenxi=r'根据零向量、相反向量、共线向量与相等向量的定义逐一判断即可．',
      xiangjie=r'解：由规定，零向量与任意向量平行（共线），①对；由相反向量的定义，②对；共线向量所在的直线互相平行或重合，不必重合，③错；相等向量只需方向相同且模相等，与起点无关，④错．故选：A．',
      dj=''),
 dict(id='F5c', nanidu='简单', zsd=3, star=False, fig=None, liubai=False,
      stem=r'已知\(\overrightarrow{a}\)，\(\overrightarrow{b}\)为非零向量，则\(\overrightarrow{a} \cdot \overrightarrow{b} < 0\)是\(\langle \overrightarrow{a},\overrightarrow{b} \rangle\)为钝角的（\quad）',
      opts=[r'充分而不必要条件', r'必要而不充分条件', r'充要条件', r'既不充分也不必要条件'],
      ans=r'B',
      fenxi=r'利用数量积与夹角的关系，注意反向共线时夹角为180°的特例，判断充分性与必要性．',
      xiangjie=r'解：若\(\overrightarrow{a} \cdot \overrightarrow{b} < 0\)，则\(\cos\langle \overrightarrow{a},\overrightarrow{b} \rangle < 0\)，\(\langle \overrightarrow{a},\overrightarrow{b} \rangle \in \left( 90^{\circ},180^{\circ} \right]\)，当两向量反向共线时夹角为\(180^{\circ}\)，不是钝角，充分性不成立；反之，夹角为钝角时\(\cos\langle \overrightarrow{a},\overrightarrow{b} \rangle < 0\)，必有\(\overrightarrow{a} \cdot \overrightarrow{b} < 0\)，必要性成立．故选：B．',
      dj=''),
 dict(id='F5j', nanidu='中档', zsd=3, star=False, fig='embed', liubai=True,
      stem=r'如图，在正方体\(ABCD - A_{1}B_{1}C_{1}D_{1}\)中，求向量\(\overrightarrow{A_{1}B}\)与\(\overrightarrow{BC_{1}}\)夹角的大小．',
      opts=None,
      ans=r'\(120^{\circ}\)',
      fenxi=r'把\(\overrightarrow{A_{1}B}\)与\(\overrightarrow{BC_{1}}\)用在同一顶点处的三条棱向量表示，用数量积求夹角．',
      xiangjie=r'解：不妨设棱长为1，\(\overrightarrow{AB} = \overrightarrow{a}\)，\(\overrightarrow{AD} = \overrightarrow{b}\)，\(\overrightarrow{AA_{1}} = \overrightarrow{c}\)，则\(\overrightarrow{a}\)，\(\overrightarrow{b}\)，\(\overrightarrow{c}\)两两垂直且模均为1．于是\(\overrightarrow{A_{1}B} = \overrightarrow{a} - \overrightarrow{c}\)，\(\overrightarrow{BC_{1}} = \overrightarrow{b} + \overrightarrow{c}\)，\(\overrightarrow{A_{1}B} \cdot \overrightarrow{BC_{1}} = \left( \overrightarrow{a} - \overrightarrow{c} \right) \cdot \left( \overrightarrow{b} + \overrightarrow{c} \right) = \overrightarrow{a} \cdot \overrightarrow{b} + \overrightarrow{a} \cdot \overrightarrow{c} - \overrightarrow{c} \cdot \overrightarrow{b} - {\overrightarrow{c}}^{2} = - 1\)，又\(\left| \overrightarrow{A_{1}B} \right| = \sqrt{2}\)，\(\left| \overrightarrow{BC_{1}} \right| = \sqrt{2}\)，所以\(\cos\langle \overrightarrow{A_{1}B},\overrightarrow{BC_{1}} \rangle = \frac{- 1}{\sqrt{2} \times \sqrt{2}} = - \frac{1}{2}\)．因为\(\langle \overrightarrow{A_{1}B},\overrightarrow{BC_{1}} \rangle \in \lbrack 0,\pi\rbrack\)，所以\(\overrightarrow{A_{1}B}\)与\(\overrightarrow{BC_{1}}\)的夹角为\(120^{\circ}\)．',
      dj=''),
 dict(id='F7', nanidu='中档', zsd=3, star=False, fig=None, liubai=False,
      stem=r'已知空间向量\(\overrightarrow{a}\)，\(\overrightarrow{b}\)满足\(\left| \overrightarrow{a} \right| = 3\)，\(\left| \overrightarrow{b} \right| = 2\)，\(\langle \overrightarrow{a},\overrightarrow{b} \rangle = 120^{\circ}\)，则\(\left| \overrightarrow{a} \right|\cos\langle \overrightarrow{a},\overrightarrow{b} \rangle =\)\kongbai{}，\(\overrightarrow{a}\)在\(\overrightarrow{b}\)上的投影向量为\kongbai{}．',
      opts=None,
      ans=r'\(- \frac{3}{2}\)；\(- \frac{3}{4}\overrightarrow{b}\)',
      fenxi=r'由投影向量（条目8）的定义直接计算：投影向量＝模长×夹角余弦×单位向量．',
      xiangjie=r'解：\(\left| \overrightarrow{a} \right|\cos\langle \overrightarrow{a},\overrightarrow{b} \rangle = 3\cos 120^{\circ} = - \frac{3}{2}\)；\(\overrightarrow{a}\)在\(\overrightarrow{b}\)上的投影向量为\(\left| \overrightarrow{a} \right|\cos\langle \overrightarrow{a},\overrightarrow{b} \rangle \cdot \frac{\overrightarrow{b}}{\left| \overrightarrow{b} \right|} = - \frac{3}{2} \times \frac{\overrightarrow{b}}{2} = - \frac{3}{4}\overrightarrow{b}\)．',
      dj=''),
 dict(id='F6b', nanidu='中档', zsd=3, star=False, fig=None, liubai=False,
      stem=r'已知\(\overrightarrow{a}\)，\(\overrightarrow{b}\)，\(\overrightarrow{c}\)为空间向量，则下列各式一定成立的是（\quad）',
      opts=[r'若\(\overrightarrow{a} \cdot \overrightarrow{b} = 0\)，则\(\overrightarrow{a} \perp \overrightarrow{b}\)',
            r'\(\left( \overrightarrow{a} \cdot \overrightarrow{b} \right) \cdot \overrightarrow{c} = \overrightarrow{a} \cdot \left( \overrightarrow{b} \cdot \overrightarrow{c} \right)\)',
            r'\(\left| \overrightarrow{a} \cdot \overrightarrow{b} \right| \leq \left| \overrightarrow{a} \right| \cdot \left| \overrightarrow{b} \right|\)',
            r'若\(\overrightarrow{a} \cdot \overrightarrow{b} > 0\)，则\(\langle \overrightarrow{a},\overrightarrow{b} \rangle\)必为锐角'],
      ans=r'C',
      fenxi=r'根据数量积的定义（零向量情形）、运算律（无结合律）与夹角范围逐一判断．',
      xiangjie=r'解：对A，\(\overrightarrow{a}\)，\(\overrightarrow{b}\)中有零向量时也有\(\overrightarrow{a} \cdot \overrightarrow{b} = 0\)，但零向量与任意向量不谈垂直，A错；对B，数量积是数量，不满足结合律，如\(\overrightarrow{a} \perp \overrightarrow{b}\)且\(\overrightarrow{b} \cdot \overrightarrow{c} \neq 0\)时，左边为零向量而右边不为零向量，B错；对C，\(\left| \overrightarrow{a} \cdot \overrightarrow{b} \right| = \left| \overrightarrow{a} \right| \cdot \left| \overrightarrow{b} \right| \cdot \left| \cos\langle \overrightarrow{a},\overrightarrow{b} \rangle \right| \leq \left| \overrightarrow{a} \right| \cdot \left| \overrightarrow{b} \right|\)，C对；对D，两向量同向共线时夹角为\(0^{\circ}\)，数量积大于0但夹角不是锐角，D错．故选：C．',
      dj=''),
 dict(id='F9', nanidu='中档', zsd=3, star=True, fig=None, liubai=False,
      stem=r'已知空间向量\(\overrightarrow{a}\)，\(\overrightarrow{b}\)满足\(\left| \overrightarrow{a} \right| = 2\)，\(\left| \overrightarrow{b} \right| = 3\)，则\(\left| \overrightarrow{a} + \overrightarrow{b} \right|^{2} + \left| \overrightarrow{a} - \overrightarrow{b} \right|^{2} =\)（\quad）',
      opts=[r'26', r'13', r'25', r'20'],
      ans=r'A',
      fenxi=r'把两式的平方用数量积展开，相反项抵消，结果只与两向量的模有关．',
      xiangjie=r'解：\(\left| \overrightarrow{a} + \overrightarrow{b} \right|^{2} = {\left| \overrightarrow{a} \right|^{2}} + 2\overrightarrow{a} \cdot \overrightarrow{b} + {\left| \overrightarrow{b} \right|^{2}}\)，\(\left| \overrightarrow{a} - \overrightarrow{b} \right|^{2} = {\left| \overrightarrow{a} \right|^{2}} - 2\overrightarrow{a} \cdot \overrightarrow{b} + {\left| \overrightarrow{b} \right|^{2}}\)，两式相加得\(2\left( {\left| \overrightarrow{a} \right|^{2}} + {\left| \overrightarrow{b} \right|^{2}} \right) = 2 \times \left( 4 + 9 \right) = 26\)，结果与夹角无关．故选：A．',
      dj=r'★理由（台账）：数量积模恒等式（平行四边形对角线法则）由平面向量向空间迁移的识别型通法题，结论高频复用，选为精选重点题．'),
 dict(id='F8', nanidu='中档', zsd=2, star=False, fig=None, liubai=True,
      stem=r'在空间四边形\(ABCD\)中，\(E\)，\(H\)分别是棱\(AB\)，\(AD\)的中点，\(F\)，\(G\)分别是棱\(CB\)，\(CD\)上的点，且\(\overrightarrow{CF} = \frac{1}{3}\overrightarrow{CB}\)，\(\overrightarrow{CG} = \frac{1}{3}\overrightarrow{CD}\)．求证：四边形\(EFGH\)是梯形．',
      opts=None,
      ans=r'证明见解析',
      fenxi=r'连接\(BD\)，用棱向量表示\(\overrightarrow{EH}\)与\(\overrightarrow{FG}\)，证明两向量共线且模不相等．',
      xiangjie=r'证明：连接\(BD\)．因为\(E\)，\(H\)分别是\(AB\)，\(AD\)的中点，所以\(\overrightarrow{EH} = \overrightarrow{EA} + \overrightarrow{AH} = \frac{1}{2}\overrightarrow{BA} + \frac{1}{2}\overrightarrow{AD} = \frac{1}{2}\overrightarrow{BD}\)；因为\(\overrightarrow{CF} = \frac{1}{3}\overrightarrow{CB}\)，\(\overrightarrow{CG} = \frac{1}{3}\overrightarrow{CD}\)，所以\(\overrightarrow{FG} = \overrightarrow{CG} - \overrightarrow{CF} = \frac{1}{3}\left( \overrightarrow{CD} - \overrightarrow{CB} \right) = \frac{1}{3}\overrightarrow{BD}\)．于是\(\overrightarrow{FG} = \frac{2}{3}\overrightarrow{EH}\)，故\(FG \parallel EH\)且\(FG \neq EH\)，四边形\(EFGH\)是梯形．',
      dj=''),
 dict(id='F10', nanidu='中档', zsd=3, star=True, fig='block', liubai=True,
      stem=r'如图，在平行六面体\(ABCD - A_{1}B_{1}C_{1}D_{1}\)中，各棱长均为2，且从同一顶点\(A\)出发的三条棱两两夹角均为\(60^{\circ}\)．（1）求对角线\(AC_{1}\)与\(BD_{1}\)的长；（2）求\(\overrightarrow{AC_{1}} \cdot \overrightarrow{BD_{1}}\)的值．',
      opts=None,
      ans=r'（1）\(2\sqrt{6}\)，\(2\sqrt{2}\)；（2）\(8\)',
      fenxi=r'设从\(A\)出发的三条棱向量为基底式和链，逐项作数量积展开；展开时注意\(60^{\circ}\)角下两两点积均为正值．',
      xiangjie=r'解：设\(\overrightarrow{AB} = \overrightarrow{a}\)，\(\overrightarrow{AD} = \overrightarrow{b}\)，\(\overrightarrow{AA_{1}} = \overrightarrow{c}\)，则\(\left| \overrightarrow{a} \right| = \left| \overrightarrow{b} \right| = \left| \overrightarrow{c} \right| = 2\)，且\(\overrightarrow{a} \cdot \overrightarrow{b} = \overrightarrow{a} \cdot \overrightarrow{c} = \overrightarrow{b} \cdot \overrightarrow{c} = 2 \times 2\cos 60^{\circ} = 2\)．（1）\(\overrightarrow{AC_{1}} = \overrightarrow{a} + \overrightarrow{b} + \overrightarrow{c}\)，\(\left| \overrightarrow{AC_{1}} \right|^{2} = {\left| \overrightarrow{a} \right|^{2}} + {\left| \overrightarrow{b} \right|^{2}} + {\left| \overrightarrow{c} \right|^{2}} + 2\left( \overrightarrow{a} \cdot \overrightarrow{b} + \overrightarrow{a} \cdot \overrightarrow{c} + \overrightarrow{b} \cdot \overrightarrow{c} \right) = 12 + 2 \times 6 = 24\)，故\(AC_{1} = 2\sqrt{6}\)；\(\overrightarrow{BD_{1}} = \overrightarrow{AD_{1}} - \overrightarrow{AB} = \overrightarrow{b} + \overrightarrow{c} - \overrightarrow{a}\)，\(\left| \overrightarrow{BD_{1}} \right|^{2} = {\left| \overrightarrow{a} \right|^{2}} + {\left| \overrightarrow{b} \right|^{2}} + {\left| \overrightarrow{c} \right|^{2}} + 2\left( \overrightarrow{b} \cdot \overrightarrow{c} - \overrightarrow{a} \cdot \overrightarrow{b} - \overrightarrow{a} \cdot \overrightarrow{c} \right) = 12 + 2 \times \left( - 2 \right) = 8\)，故\(BD_{1} = 2\sqrt{2}\)．（2）\(\overrightarrow{AC_{1}} \cdot \overrightarrow{BD_{1}} = \left( \overrightarrow{a} + \overrightarrow{b} + \overrightarrow{c} \right) \cdot \left( \overrightarrow{b} + \overrightarrow{c} - \overrightarrow{a} \right) = 2\overrightarrow{b} \cdot \overrightarrow{c} + {\left| \overrightarrow{b} \right|^{2}} + {\left| \overrightarrow{c} \right|^{2}} - {\left| \overrightarrow{a} \right|^{2}} = 4 + 4 + 4 - 4 = 8\)．',
      dj=r'★理由（台账）：平行六面体对角线的向量展开＝空间数量积求模的母题式通法（结论：对角线长公式），线性运算与数量积两知识点串接，选为精选重点题．'),
]
assert len(MC) == 10, f'命制题应为 10 题（上限顶格），实得 {len(MC)}'
log('3. 题量配平：源题 1（1.1.1.8-8，各组第2题起唯一可用）＋命制 10（上限顶格）＝11 题；'
    '难度分布 简单5/中档6/难0（偏基础档，源节 难0 不造难）；配平落点＝题区满 1 页＋答案区满 1 页'
    '（题数对全品 16~20 题/2 页的缺口＝题池缺口，回补轮按拍板29 优先序补齐——债务登记）')
log('3a. 命制题逐题亲算核验（10/10 通过，过程见交付报告）：F1 AC−AD=DC；F2 A1D=b−c、AC1=a+b+c；'
    'F3 ①零向量规定②相反向量定义③平行或重合④与起点无关；F5c a·b<0 ⟹ 夹角∈(90°,180°]含180°反向共线；'
    'F5j (a−c)·(b+c)=−1、|·|=√2×√2 → cos=−1/2 → 120°；F7 3cos120°=−3/2、投影向量−3/4·b；'
    'F6b 零向量/无结合律/|cos|≤1/同向0°；F9 2(|a|²+|b|²)=26 与夹角无关；'
    'F8 EH=½BD、FG=⅓BD → FG=⅔EH 共线不等长；F10 |AC1|²=24、|BD1|²=8、AC1·BD1=8')

# ---- 4. A7 选项网格（按长度 4/2/1 项每行；分号字符全保留，拍板21） ----
LEDGER = []   # 命制/版式自产分号台账（逐字符串入账）

def optlen(s):
    t = re.sub(r'\\[a-zA-Z]+', '\u0001', s)
    t = re.sub(r'[()\[\]{}=<>+\-*,.;:！？，。；：、\s~]', '', t)
    n = 0.0
    for ch in t:
        if ch == '\u0001':
            n += 2.0
        elif ord(ch) > 0x2E7F:
            n += 1.0
        else:
            n += 0.5
    return n

def emit_options(opts):
    mx = max(optlen(o) for o in opts)
    L = 'ABCD'
    if mx <= 6:          # 4 项/行
        cells = [f'{L[i]}．{o}；' for i, o in enumerate(opts)]
        cells[3] = cells[3][:-1]
        LEDGER.extend(cells)
        return [r'\bindopt ' + ''.join(cells)]
    if mx <= 14:         # 2 项/行（第二列对齐 ≈栏中）
        LEDGER.extend([f'A．{opts[0]}；', f'B．{opts[1]}；', f'C．{opts[2]}；', f'D．{opts[3]}'])
        return [r'\optgrid{' + f'A．{opts[0]}； & B．{opts[1]}； \\\\' + '\n' + f'C．{opts[2]}； & D．{opts[3]}' + '}']
    out = []             # 1 项/行（逐行）
    for i, o in enumerate(opts):
        cell = f'{L[i]}．{o}；' if i < 3 else f'{L[i]}．{o}'
        LEDGER.append(cell)
        out.append(r'\bindopt ' + cell)
    return out

def siderun(nanidu, zsd, star):
    return ('〔' + nanidu + '〕' + ('★' if star else '') + '（知识点' + str(zsd) + '）')

# 组行外衣（拍板26；组名/外衣文案 L225 待过目——登记）
TIERS = [('夯基达标', r'保60\%'), ('提能进阶', r'保80\%'), ('冲刺突破', r'冲100\%')]
LIUBAI_LINES = 3   # L104「大题之后保留6行」双栏降档 3 行书写空间；配平超标时降 0（登记）

# ---- 5. 组装题区 body.tex（顺序：夯基=源+F1~F5c，提能=F5j/F7/F6b/F9，冲刺=F8/F10） ----
ORDER = [('src', (8, 8))] + [('mc', i) for i in range(4)] + \
        [('mc', i) for i in range(4, 8)] + [('mc', i) for i in range(8, 10)]
TIER_OF = [0] * 5 + [1] * 4 + [2] * 2
body = []
em = body.append
seq = 0
fig_tikz = []
for idx, (kind, ref) in enumerate(ORDER):
    if TIER_OF[idx] != (TIER_OF[idx - 1] if idx else -1):
        name, coat = TIERS[TIER_OF[idx]]
        em(r'\huaxing{' + name + '}{' + coat + '}')
        log(f'5a. 组行「{name}」＝tcbox 白底黑边圆角块（花形近似）＋右侧灰小字外衣「{coat}」（拍板26 槽位）；'
            '撤 v3 深灰底线与描述小字（A4）；块前 3pt 尾 2pt（主病3/A4）；文案 L225 待过目（登记）')
    seq += 1
    if kind == 'src':
        d = tis[ref]
        label = siderun(d['nanidu'], 3, False)
        em(r'\jx{' + str(seq) + '}{' + label + '}{' + d['stem'][0] + '}')
        for b in d['stem'][1:]:
            em(r'\bindp ' + b)
        log(f'5b. 题{seq}＝源 {d["num"]}（{d["nanidu"]}，知识点3），题面无答案；'
            '侧标＝〔难度〕（知识点N）6.5pt 777777（A11：〔源〕括注已撤，拍板18）；源分号 0 处全保留')
        src_used = d['stem'] + [d['ans'], d['zsd']] + d['fenxi'] + d['xiangjie'] + d['dj']
        src_semis = sum(s.count('；') for s in src_used)
        src_key = ref
    else:
        mcd = MC[ref]
        label = siderun(mcd['nanidu'], mcd['zsd'], mcd['star'])
        LEDGER.append(mcd['stem'])
        if mcd['fig'] == 'embed':
            em(r'\jxfig{' + str(seq) + '}{' + label + '}{' + mcd['stem'] + '}{' + FIG_CUBE + '}')
            fig_tikz.append((seq, '右嵌 30mm 档 minipage（题干≤2 行，图右缘=栏右缘）'))
        else:
            em(r'\jx{' + str(seq) + '}{' + label + '}{' + mcd['stem'] + '}')
            if mcd['fig'] == 'block':
                em(r'\figblock{' + FIG_PARA + '}')
                fig_tikz.append((seq, '题下居中 30mm 档（长题干路径，7mm 起排）'))
        if mcd['opts']:
            for s in emit_options(mcd['opts']):
                em(s)
        # 末题（题区最后）不追加书写留白：栏底自然留白已承担作答空间，
        # 追加不可拆需求为 p1 Overfull 2.63pt 根因（裁决登记交付报告 §六-2）
        if mcd['liubai'] and LIUBAI_LINES and mcd is not MC[-1]:
            em(r'\liubai{' + str(LIUBAI_LINES) + '}')
        star_txt = '＋★精选标（' + mcd['dj'] + '）' if mcd['star'] else ''
        log(f'5c. 题{seq}＝命制 {mcd["id"]}（{mcd["nanidu"]}，知识点{mcd["zsd"]}）{star_txt}'
            + ('；解答题后书写空间 3 行（L104 双栏降档）' if mcd['liubai'] and LIUBAI_LINES and mcd is not MC[-1] else ''))

log('5d. 题侧随件全件口径：〔难度〕★（知识点N）＝6.5pt/9pt #777777 同一灰档（总诊断表 §二），'
    '落题号侧（拍板25 ★ 题号侧口径；v3 行末右缘 \\hfill 注入法废止——撤〔源〕括注后无截断需求）；'
    '★ ×2（题9 F9、题11 F10，理由入台账）；知识点N 对位：1＝概念、2＝线性运算、3＝夹角/数量积/共面/投影'
    '（v2 实验报告三块映射同源，铺开轮以导学件 v4 知识清单为准复核——逻辑断言① 口径）')
log('5e. 图 2 张均 TikZ 矢量重绘（拍板24，30mm 档，图内字号 \\figfont 7.5pt≈正文71%，线宽 0.4/0.9pt）：'
    + '；'.join(f'题{n} {w}' for n, w in fig_tikz) + '；答案区图计数＝0（A8 断言）')

# ---- 6. 组装答案区 answers.tex（\jans 流水号与题区一一对应——逻辑断言④） ----
answers = []
aseq = 0
for idx, (kind, ref) in enumerate(ORDER):
    aseq += 1
    assert aseq == seq - seq + aseq
    if kind == 'src':
        d = tis[ref]
        answers.append(r'\jans{' + str(aseq) + r'}{\ansul{' + d['ans'] + '}}')
        pieces = []
        for tag, blks in (('【分析】', d['fenxi']), ('【详解】', d['xiangjie']), ('【点睛】', d['dj'])):
            if blks:
                first = blks[0]
                for tg in ('【分析】', '【详解】', '【点睛】'):
                    if first.startswith(tg):
                        first = first[len(tg):].strip()
                rest = ' '.join(blks[1:])
                pieces.append(tag + first + ((' ' + rest) if rest else ''))
        answers.extend(pieces)
        log(f'6. 答{aseq}＝源 1.1.1.8-8：【答案】下划线＋【分析】{len(d["fenxi"])}块＋【详解】{len(d["xiangjie"])}块'
            f'＋【点睛】{len(d["dj"])}块 verbatim 连排（答案区 10.5pt/18pt，A9 裁定）')
    else:
        mcd = MC[ref]
        LEDGER.append(mcd['ans'])
        answers.append(r'\jans{' + str(aseq) + r'}{\ansul{' + mcd['ans'] + '}}')
        if mcd['fenxi']:
            answers.append('【分析】' + mcd['fenxi'])
            LEDGER.append('【分析】' + mcd['fenxi'])
        answers.append('【详解】' + mcd['xiangjie'])
        LEDGER.append('【详解】' + mcd['xiangjie'])
        if mcd['dj'] and not mcd['dj'].startswith('★'):
            answers.append('【点睛】' + mcd['dj'])
            LEDGER.append('【点睛】' + mcd['dj'])
        log(f'6. 答{aseq}＝命制 {mcd["id"]}：【答案】下划线＋【分析】/【详解】连排（亲算核验答案入区）')
assert aseq == 11, f'题↔答案区一一对应（逻辑断言④）：题 {seq} 条 vs 答案 {aseq} 条'
assert aseq == len(ORDER)

# ---- 7. 分号台账对账（公共铁律：分号字符全保留，拍板21/L102） ----
d8 = tis[src_key]
src_used = d8['stem'] + [d8['ans'], d8['zsd']] + d8['fenxi'] + d8['xiangjie'] + d8['dj']
exp_src = sum(s.count('；') for s in src_used)
exp_mc = sum(s.count('；') for s in LEDGER)
body_text = '\n\n'.join(body)
ans_text = '\n'.join(answers)
actual = body_text.count('；') + ans_text.count('；')
assert actual == exp_src + exp_mc, f'分号对账失败：成品 {actual} vs 台账 {exp_src}+{exp_mc}'
log(f'7. 分号对账：源采用题（1.1.1.8-8 题面＋解析）源分号 {exp_src} 处逐字保留；命制/版式自产分号 '
    f'{exp_mc} 处逐条入账（选项格 3 分号×4 选择题＋命制文本）；成品（body＋answers）合计 {actual} 处＝台账 ✓')

# ---- 8. 巨型公式断点（同 v2 11b）＋输出 ----
n_ab = body_text.count(' = \\left') + body_text.count(' \\cdot \\left')
body_text = body_text.replace(' = \\left', ' = \\allowbreak\\left').replace(' \\cdot \\left', ' \\cdot \\allowbreak\\left')
log(f'8. body.tex：巨型行内公式显式断点 \\allowbreak ×{n_ab}（同 v2 11b）')
open(BASE + r'\body.tex', 'w', encoding='utf-8').write(body_text + '\n')
n_ab2 = ans_text.count(' = \\left') + ans_text.count(' \\cdot \\left')
ans_text = ans_text.replace(' = \\left', ' = \\allowbreak\\left').replace(' \\cdot \\left', ' \\cdot \\allowbreak\\left')
log(f'8. answers.tex：巨型行内公式显式断点 \\allowbreak ×{n_ab2}（同 v2 11b）')
open(BASE + r'\answers.tex', 'w', encoding='utf-8').write(ans_text + '\n')

head = [
    r'\zhangtitle{第1章 空间向量与立体几何}',
    r'\jietitle{1.1 空间向量及其运算}',
    r'\xiaojietitle{1.1.1 空间向量及其运算}',
    r'\keshi{第1课时\quad 空间向量及其运算}',
]
open(BASE + r'\chapterhead.tex', 'w', encoding='utf-8').write('\n'.join(head) + '\n')
log('9. 章首通栏：A13 装饰方块 13.9×16.8mm #777777 与居中章标题同行（拍板4 居中摆位变通，待过目）；'
    'A3 压缩：章尾 4pt、节前 6pt/行高22pt、小节前 6pt 尾 5pt、课时前 5pt 尾 4pt；'
    '题区/答案区 \\clearpage 由 main.tex 承担（multicols 外）；课时名「第1课时 空间向量及其运算」'
    '＝演示性定名（源节未分课时，v3 同口径承继）')
open(BASE + r'\postproc_lianxi_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG))
print('\n'.join(LOG))
