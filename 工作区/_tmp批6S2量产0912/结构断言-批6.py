# -*- coding: utf-8 -*-
"""批6 章末「本章总结提升」结构断言：源级＋PDF级＋与10课时/衔接节导学件的取材互斥断言。
互斥口径＝28题特征串（LaTeX 记号归一后）在章末件自身必须命中、在其余11件源文零命中。"""
import io, os, re, sys
import fitz  # pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
JIAN = os.path.normpath(os.path.join(BASE, '..', 'M2-第1章量产0911', '成卷', '导学件', '章末-本章总结提升'))
DAOXUE = os.path.normpath(os.path.join(BASE, '..', 'M2-第1章量产0911', '成卷', '导学件'))

src = io.open(os.path.join(JIAN, 'main.tex'), encoding='utf-8').read()
src_body = '\n'.join(l for l in src.split('\n') if not l.lstrip().startswith('%'))
doc = fitz.open(os.path.join(JIAN, 'main.pdf'))
pdf = ''.join(p.get_text() for p in doc)
pdfn = re.sub(r'\s+', '', pdf)

fails = []
def chk(name, cond, detail=''):
    print(('PASS' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name)

# ---------- 源级 ----------
chk('lxing 题型块＝12', len(re.findall(r'\\lxing\{', src_body)) == 12)
chk('例＝12', len(re.findall(r'\\li\{例\\textbf\{', src_body)) == 12)
chk('变式＝12', len(re.findall(r'\\liB\{变式\\textbf\{', src_body)) == 12)
chk('总述＝12', len(re.findall(r'\\zongshu\{', src_body)) == 12)
chk('花形＝3（题型归类/高考题组/知识脉络）', len(re.findall(r'\\huaxing\{', src_body)) == 3)
chk('高考标签行＝1', src_body.count(r'\anlabel{[精选高考题]}') == 1)
chk('高考题＝4', len(re.findall(r'\\liB\{高考\\textbf\{', src_body)) == 4)
chk('图＝4（F6 源图 image22/24/33/47）',
    len(re.findall(r'figs/image(22|24|33|47)\.png', src_body)) == 4)
chk('本件不用 \\gaokaowei 空槽（独立板块定案）', r'\gaokaowei' not in src_body)
chk('页脚册名换＝人教A版', r'\renewcommand{\qpceming}{高中数学\quad 选择性必修第一册(人教A版)}' in src_body)
chk('vbox 防拆块＝12', len(re.findall(r'\\vbox\{', src_body)) == 12)
chk('题数合计＝28（12例＋12变式＋4高考）',
    len(re.findall(r'\\li\{例', src_body)) + len(re.findall(r'\\liB\{变式', src_body)) + len(re.findall(r'\\liB\{高考', src_body)) == 28)

# ---------- PDF 级 ----------
chk('PDF 页数＝6', len(doc) == 6, f'({len(doc)})')
chk('PDF 题型一~十二齐全', all(f'题型{zh}' in pdfn for zh in
    ['一','二','三','四','五','六','七','八','九','十','十一','十二']))
chk('PDF [类型总述]×12', pdfn.count('[类型总述]') == 12, f'({pdfn.count("[类型总述]")})')
chk('PDF [精选高考题]×1', pdfn.count('[精选高考题]') == 1)
chk('PDF [知识脉络]×1', pdfn.count('[知识脉络]') == 1)
chk('PDF [方法主线]×1', pdfn.count('[方法主线]') == 1)
chk('PDF 高考1~4 齐全', all(f'高考{n}' in pdfn for n in '1234'))
chk('PDF 无生产注记词', not any(w in pdf for w in ['待源', '不在手', '回填', '台账', '断言', '〔生产', 'G1']))
chk('PDF 无「人教B版」残留（偶页脚随实A版）', '人教B' not in pdfn and '人教A' in pdfn)
chk('PDF「如图」仅高考组3处（有言无图＝0）', pdf.count('如图') == 3, f'({pdf.count("如图")})')
chk('PDF 嵌入图＝4', sum(len(p.get_images()) for p in doc) == 4)

# ---------- 互斥断言（源级归一比对） ----------
SYM = {'\\lambda': 'λ', '\\alpha': 'α', '\\beta': 'β', '\\theta': 'θ', '\\pi': 'π',
       '\\parallel': '∥', '\\perp': '⊥', '\\times': '×', '\\cdot': '·', '\\in': '∈',
       '\\neq': '≠', '\\angle': '∠', '\\triangle': '△', '\\sqrt': '', '\\frac': ''}
def norm(t):
    t = re.sub(r'(?m)%.*$', '', t)
    t = t.replace(r'\(', '').replace(r'\)', '')
    t = re.sub(r'\\penalty\d+', '', t)
    t = re.sub(r'\\text\{([^}]*)\}', r'\1', t)
    t = re.sub(r'\\overrightarrow\s*\{([^}]*)\}', r'\1', t)
    for k, v in SYM.items():
        t = t.replace(k, v)
    t = re.sub(r'\\[a-zA-Z]+\*?', '', t)
    t = re.sub(r'[{}_$\\]', '', t)
    return re.sub(r'\s+', '', t)

# 特征串（AND 组）：章末件自身必命中；11 基准件零命中
FR = [
    ('L02Q1', ['任一向量与它的相反向量都不相等']),
    ('L02Q2', ['运算结果为向量']),
    ('L02Q7', ['写出下列向量夹角的大小']),
    ('L02Q14', ['根据下列各条件分别求']),
    ('L02Q13', ['数量积可以为0']),
    ('L01Q16', ['边长为2的等边三角形', '的最小值']),
    ('L03Q2', ['在以下三个命题中']),
    ('L03Q16', ['不共线的三点', '充要条件']),
    ('L04Q8', ['下列叙述正确的序号有']),
    ('L04Q13', ['体对角线的交点为']),
    ('L05Q8', ['求下列两个空间向量夹角的余弦']),
    ('L05Q11', ['求线段AD的长']),
    ('L05Q6', ['平行，求实数']),
    ('L05Q7', ['则x+y的值为']),
    ('L06Q4', ['若l1∥l2', '则λ等于']),
    ('L06Q16', ['判断满足下列条件的点']),
    ('L07Q3', ['方向向量是', '(3,2,1)', '位置关系是']),
    ('L07Q4', ['下列命题是真命题的有']),
    ('L08Q1', ['求线段AB在平面']),
    ('L08Q6', ['直线A1M与平面AMC1']),
    ('L09Q1', ['二面角P-AB-P']),
    ('L09Q7', ['侧面PAD为边长等于2的正三角形']),
    ('L10Q3', ['到直线BC的距离']),
    ('L10Q12', ['点E,O分别是', '则下列说法正确的是']),
    ('G1', ['点P在侧面']),
    ('G2', ['写出一个正确的命题']),
    ('G3', ['按第一个解答计分']),
    ('G4', ['使二面角M-EC-D']),
]
selfn = norm(src_body)
miss_self = [k for k, fs in FR if not all(f in selfn for f in fs)]
chk('28题特征串在章末件自身全部命中（串未写错）', not miss_self, str(miss_self))

peers = {}
for d in sorted(os.listdir(DAOXUE)):
    mp = os.path.join(DAOXUE, d, 'main.tex')
    if d != os.path.basename(JIAN) and os.path.isfile(mp):
        peers[d] = norm(io.open(mp, encoding='utf-8').read())
chk('互斥基准件＝11（课时01~10＋衔接节）', len(peers) == 11, f'({len(peers)})')
bad = []
for k, fs in FR:
    for oname, otext in peers.items():
        if all(f in otext for f in fs):
            bad.append((k, oname))
chk('28题零同文于11件（入板块题不在练习轴导学件重印）', not bad, str(bad[:6]))

print('\nRESULT:', 'ALL PASS' if not fails else f'{len(fails)} FAIL: {fails}')
sys.exit(1 if fails else 0)
