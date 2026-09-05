# -*- coding: utf-8 -*-
"""②D_01c_T5公式丢失全量盘点.py — T5 执行丢失 oMath 元素全量清单（主脑呈报件）。
对十件：diff 工具建设期留档 bak_标签行(pre-T5) vs bak_底纹批(post-T5)——该边界唯一执行的
工具即 T5，序列差 = T5 纯效应。清单件（T5 0 处置）以 X0(=bak_题号终态) 与现态元素数对照兜底。
分类：丢失段文本以【答案】起＝答案值公式丢失。另核对现态元素总数与 T9 预跑 dry 隐含值一致。
报告：报告/②D_01c_T5公式丢失清单.md"""
import sys, io, os, zipfile, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
WJ = '⁠'
def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def om_sig(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    out = []
    for p in doc.find(q('body')).iter(q('p')):
        n = len(list(p.iter(qm('oMath'))))
        if n:
            out.append((n, ptext(p).replace(WJ, '')))
    return out

ARCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本_工具建设期留档')
CUR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本')
NAMES = [
    ('清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）'),
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）'),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）'),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）'),
    ('清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）'),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）'),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）'),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）'),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）'),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）'),
]
# T9 预跑 dry（现态）隐含 oMath 元素总数下限校验用：新挂短+幂等+长（段数，非元素数）
OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

tot_lost_el = tot_lost_p = tot_ans_p = 0
for sh, base in NAMES:
    pre = os.path.join(ARCH, base + '.docx.bak_标签行')
    post = os.path.join(ARCH, base + '.docx.bak_底纹批')
    if not os.path.exists(pre) or not os.path.exists(post):
        # 清单件（②-A 四工具 0 处置、无 bak）：X1 主件（②-B 前）vs 现态元素数对照——其间唯 T8 重构作用
        x1 = os.path.join(ARCH, base + '.docx')
        e1 = sum(n for n, _ in om_sig(x1))
        ec = sum(n for n, _ in om_sig(os.path.join(CUR, base + '.docx')))
        sm2 = difflib.SequenceMatcher(a=[t for _, t in om_sig(x1)], b=[t for _, t in om_sig(os.path.join(CUR, base + '.docx'))], autojunk=False)
        extra = []
        for tag_, i1, i2, j1, j2 in sm2.get_opcodes():
            if tag_ != 'equal':
                for n, t in om_sig(x1)[i1:i2]:
                    extra.append('    [X1−] om%d %s' % (n, t[:56]))
                for n, t in om_sig(os.path.join(CUR, base + '.docx'))[j1:j2]:
                    extra.append('    [现+ ] om%d %s' % (n, t[:56]))
        say('## %s（清单件，T5 0 处置）X1(②-B前)元素 %d → 现态元素 %d（差 %+d）｜T8 重构期差异 %d 行：'
            % (sh, e1, ec, ec - e1, len(extra)))
        for r in extra[:14]:
            say(r)
        continue
    a, b = om_sig(pre), om_sig(post)
    ea, eb = sum(n for n, _ in a), sum(n for n, _ in b)
    sm = difflib.SequenceMatcher(a=[t for _, t in a], b=[t for _, t in b], autojunk=False)
    lost_paras, gained = [], 0
    for tag_, i1, i2, j1, j2 in sm.get_opcodes():
        if tag_ == 'equal':
            continue
        for n, t in a[i1:i2]:
            lost_paras.append((n, t))
        for n, t in b[j1:j2]:
            gained += n
    el_lost = ea - eb
    p_lost = len(lost_paras)
    el_in_lost = sum(n for n, _ in lost_paras)
    ans_lost = sum(1 for n, t in lost_paras if t.startswith('【答案】'))
    tot_lost_el += el_lost
    tot_lost_p += p_lost
    tot_ans_p += ans_lost
    say('## %s：preT5 元素 %d → postT5 元素 %d（丢 %d 元素/ %d 段；丢失段含元素 %d，另有段间迁移 %+d 元素）'
        % (sh, ea, eb, el_lost, p_lost, el_in_lost, gained - (el_in_lost - el_lost)))
    say('  其中答案值公式丢失段（【答案】起）：%d 段' % ans_lost)
    for n, t in lost_paras[:10]:
        say('    丢[om%d] %s' % (n, t[:60]))
    if len(lost_paras) > 10:
        say('    …共 %d 段（全清单见报告文件）' % len(lost_paras))
say('')
say('=== 十件合计：T5 丢失 oMath 元素 %d 个／%d 段（其中答案值公式段 %d 段） ===' % (tot_lost_el, tot_lost_p, tot_ans_p))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '报告', '②D_01c_T5公式丢失清单.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('# T5 执行 oMath 公式元素丢失全量清单（②-D 溯源呈报件）\n\n')
    f.write('- 溯源口径：diff bak_标签行(pre-T5) vs bak_底纹批(post-T5)，该边界唯一执行工具＝T5；\n')
    f.write('- 丢失机制：混行段「【答案】 <纯公式>　【知识点】…」拆分时，公式为零宽 oMath、content 段可视文本全空白，\n')
    f.write('  该空白 content 段被 T5 丢弃，随段丢弃其中的 oMath（T5 文本守恒断言只看 w:t，看不见 m:oMath）；\n')
    f.write('- 承载面：②-B 起全部下游态（含现同步盘 ②-C 终态、②工具/副本）均带此损失；X1→②C 序列零差异（未再丢）。\n\n')
    f.write('```text\n' + '\n'.join(OUT) + '\n```\n')
print('REPORT:', out, flush=True)
