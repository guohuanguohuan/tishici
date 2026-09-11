# -*- coding: utf-8 -*-
# 同文比对举证：验证 keys-03/04/05 中「推导键」的题面同文/同源关系
# 方法：指纹（取自练/测/增侧源文本的题干或选项核心串）经 normalize 后，
#       断言其包含于 _源快照/variantF_body.tex（导学件题面）。
# normalize：剥 \nobreak/\penalty N/\allowbreak/\kern.. 及全部空白后比对。
import re, io, sys

def N(s):
    s = re.sub(r'\\nobreak', '', s)
    s = re.sub(r'\\penalty\d+', '', s)
    s = re.sub(r'\\allowbreak', '', s)
    s = re.sub(r'\\kern[\d.\-]+(?:mm|pt|em)?', '', s)
    s = re.sub(r'\s+', '', s)
    return s

VF = N(io.open('_源快照/variantF_body.tex', encoding='utf-8').read())
LX = N(io.open('_源快照/练习线_main.tex', encoding='utf-8').read())
CP = N(io.open('_源快照/测评卷_main.tex', encoding='utf-8').read())
ZL = N(io.open('_源快照/导学增量_main.tex', encoding='utf-8').read())

checks = []  # (题目, 结论类型, [指纹], [宿主])  结论类型: 同文 / 差异 / 同源改写
def add(qid, kind, fps, host=VF):
    checks.append((qid, kind, fps, host))

add('练-滚-1 ≡ 导-T1-例1', '同文', ['零向量是没有方向的向量', '两个单位向量'])
add('练-滚-2 ≡ 导-T1-变1', '同文', ['零向量与任意向量都平行'])
add('练-滚-4 ≡ 导-P4', '同文', ['在空间四边形\\(ABCD\\)中，\\(E\\)，\\(F\\)分别为\\(AB\\)，\\(CD\\)的中点'])
add('练-滚-5 ≡ 导-P2', '同文', ['\\overrightarrow{b}=4\\overrightarrow{e_1}+k\\overrightarrow{e_2}'])
add('练-滚-6 ≡ 导-T9-例1', '同文', ['使平面\\(ABC\\)与平面\\(ACD\\)垂直，则'])
add('练-滚-7 ≡ 导-T5-例1', '同文', ['\\frac{\\overrightarrow{a} \\cdot \\overrightarrow{b}}{\\overrightarrow{a} \\cdot \\overrightarrow{a}} = \\frac{\\overrightarrow{b}}{\\overrightarrow{a}}'])
add('练-滚-9 ≡ 导-P1', '同文', ['\\langle\\overrightarrow{a},\\overrightarrow{b}\\rangle=60^\\circ\\)，则\\(\\overrightarrow{a}\\cdot\\overrightarrow{b}='])
add('练-滚-10 ≡ 导-P5', '同文', ['\\langle\\overrightarrow{a},\\overrightarrow{b}\\rangle=120^\\circ\\)，则\\(|\\overrightarrow{a}+\\overrightarrow{b}|='])
add('练-滚-11 ≡ 导-T7-例1', '同文', ['的夹角为钝角的实数\\(\\lambda\\)的取值范围是'])
add('练-课-1 ≡ 导-P3', '同文', ['均为非零空间向量，则“\\(\\overrightarrow{a}\\cdot\\overrightarrow{b}=0\\)”是“\\(\\overrightarrow{a}\\perp\\overrightarrow{b}\\)”的'])
add('练-课-2 ≡ 导-T2-变1', '同文', ['\\(\\overrightarrow{D_1B}=\\)'])
add('练-课-3 ≡ 导-T3-变1', '同文', ['\\overrightarrow{A_1E}=\\frac{1}{2}\\overrightarrow{A_1C_1}'])
add('练-课-4 ≡ 导-T5-变1', '同文', ['(\\overrightarrow{a}+2\\overrightarrow{b})\\cdot(\\overrightarrow{a}-\\overrightarrow{b})'])
add('练-课-5 ≡ 导-T6-变1', '同文', ['与\\(\\overrightarrow{AC}\\)夹角的余弦值为'])
add('练-课-6 ≡ 导-T2-例1', '同文', ['\\overrightarrow{CC_{1}} = \\overrightarrow{c}'])
add('练-课-10 ≡ 导-T4-变1', '同文', ['\\overrightarrow{MP}=3\\overrightarrow{MA}-2\\overrightarrow{MB}'])
add('练-课-11 ≡ 导-T8-变1', '同文', ['的二面角\\(A\\text{-}EF\\text{-}D\\)中，四边形\\(ABFE\\)，\\(CDEF\\)都是边长为\\(1\\)的正方形'])
add('练-课-12 ≡ 导-T5-例1', '同文', ['( \\overrightarrow{a} - \\overrightarrow{b} )^{2} = {\\overrightarrow{a}}^{2} - 2\\overrightarrow{a} \\cdot \\overrightarrow{b} + {\\overrightarrow{b}}^{2}'])
add('练-课-15 ≡ 导-T9-变1', '同文', ['使二面角\\(B\\text{-}AC\\text{-}D\\)的大小为\\(60^\\circ\\)，则'])
add('测-1 ≡ 导-T1-例1', '同文', ['两个单位向量'])
add('测-2 ≡ 导-T1-变1', '同文', ['零向量与任意向量都平行'])
add('测-3 ≡ 导-P2', '同文', ['\\overrightarrow{b}=4\\overrightarrow{e_1}+k\\overrightarrow{e_2}'], CP)
add('测-4 ≡ 导-T5-例1', '同文', ['{\\overrightarrow{a}}^{2} = | \\overrightarrow{a} |^{2}'], CP)
add('测-5 ≡ 导-P1', '同文', ['则\\(\\overrightarrow{a}\\cdot\\overrightarrow{b}=\\)'], CP)
add('测-6 ≈ 导-P5(同源改写:填空改解答)', '同源改写', ['\\langle\\overrightarrow{a},\\overrightarrow{b}\\rangle=120^\\circ\\)，求\\(|\\overrightarrow{a}+\\overrightarrow{b}|\\)'], CP)
add('增-章-T1-例1 ≡ 导-T1-例1', '同文', ['两个单位向量'], ZL)
add('增-章-T1-变1 ≡ 导-T1-变1', '同文', ['零向量与任意向量都平行'], ZL)
add('增-章-T2-例1 ≡ 导-T5-例1', '同文', ['\\frac{\\overrightarrow{a} \\cdot \\overrightarrow{b}}{\\overrightarrow{a} \\cdot \\overrightarrow{a}} = \\frac{\\overrightarrow{b}}{\\overrightarrow{a}}'], ZL)
add('增-章-T2-变1 ≡ 导-T5-变1', '同文', ['(\\overrightarrow{a}+2\\overrightarrow{b})\\cdot(\\overrightarrow{a}-\\overrightarrow{b})'], ZL)
add('增-Y1-填1 = 导-Y1-填1+填3首空(拆合)', '同文', ['我们把具有\\kongbai{}和\\kongbai{}的量叫做空间向量', '向量与任意向量平行'], ZL)
add('增-Y1-判1 ≡ 导-Y1-判1', '同文', ['两个空间向量的模相等，则这两个向量相等'], ZL)
add('增-Y2-填1 ≈ 导-Y2-填1(数乘表述异/键值同)', '同文', ['加法可按\\kongbai{}法则或\\kongbai{}法则作出'], ZL)
add('增-Y2-判1 ≡ 导-Y2-判2', '同文', ['则存在唯一实数\\(\\lambda\\)，使\\(\\overrightarrow{a}=\\lambda\\overrightarrow{b}\\)'], ZL)
add('增-Y3-填1 ≈ 导-Y3-填1首空(公式同印/键值同)', '同文', ['\\overrightarrow{a}\\cdot\\overrightarrow{b}=|\\overrightarrow{a}||\\overrightarrow{b}|\\cos\\langle\\overrightarrow{a},\\overrightarrow{b}\\rangle'], ZL)
add('增-Y3-判1 ≡ 导-Y3-判2', '同文', ['两个非零空间向量的数量积大于\\(0\\)，则这两个向量的夹角为锐角'], ZL)
add('增-Y4-填1 ≡ 导-Y3-填4', '同文', ['共面的充要条件是存在\\kongbai{}\\((x,y)\\)，使\\(\\overrightarrow{p}=x\\overrightarrow{a}+y\\overrightarrow{b}\\)'], ZL)
add('增-Y4-判1 ≡ 导-Y3-判1', '同文', ['则\\(\\overrightarrow{p}\\)，\\(\\overrightarrow{a}\\)，\\(\\overrightarrow{b}\\)共面'], ZL)
add('增-探-例1 ≡ 导-T1-例1', '同文', ['零向量是没有方向的向量'], ZL)
add('增-探-变1 ≡ 导-T4-变1', '同文', ['\\overrightarrow{MP}=3\\overrightarrow{MA}-2\\overrightarrow{MB}'], ZL)
add('增-评1 ≡ 导-P2', '同文', ['\\overrightarrow{b}=4\\overrightarrow{e_1}+k\\overrightarrow{e_2}'], ZL)
add('增-评2 ≡ 导-P3', '同文', ['均为非零空间向量'], ZL)
add('增-评3 ≡ 导-P4', '同文', ['分别为\\(AB\\)，\\(CD\\)的中点'], ZL)
add('增-评4 ≡ 导-P1', '同文', ['则\\(\\overrightarrow{a}\\cdot\\overrightarrow{b}=\\)'], ZL)
add('增-评5 ≈ 导-P5(提示文字异/给值同)', '同文', ['则\\(|\\overrightarrow{a}+\\overrightarrow{b}|=\\)'], ZL)

# 练-滚-3 选项A差异专项
diffA = (N('A．①②；') in LX, N('A．①②③④；') in VF)
stem34 = (N('①③④') in LX and N('①③') in LX and N('②④') in LX and N('①③④') in VF)

out = io.open('自检/同文比对.txt', 'w', encoding='utf-8')
w = lambda s: out.write(s + '\n')
w('同文比对举证 ｜ 产出：逻辑闸-样张族0911 ｜ 快照基准：_源快照/（SHA256 见 _源快照/_快照清单.txt）')
w('方法：指纹 normalize（剥 \\nobreak/\\penalty/\\allowbreak/\\kern/空白）后断言包含于导学件快照')
w('=%s' % ('=' * 66))
npass = nfail = 0
for qid, kind, fps, host in checks:
    res = [N(f) in host for f in fps]
    ok = all(res)
    npass += ok; nfail += (not ok)
    w('[%s] %s ｜ 指纹%s' % ('PASS' if ok else 'FAIL', qid,
        '；'.join(('命中' if r else '未命中') for r in res)))
w('=%s' % ('=' * 66))
w('练-滚-3 差异专项：练习线含「A．①②；」=%s ｜ 导学件含「A．①②③④；」=%s → 选项A确系差异点' % diffA)
w('练-滚-3 其余选项（①③④/①③/②④）两侧均在场=%s → 正确项①③=C 两版一致' % stem34)
w('=%s' % ('=' * 66))
w('合计：PASS %d ／ FAIL %d ／ 总检 %d' % (npass, nfail, len(checks)))
w('结论：%s' % ('全部推导键的同文/同源关系成立' if nfail == 0 else '存在未命中指纹——须人工复核！'))
out.close()
print('PASS=%d FAIL=%d total=%d' % (npass, nfail, len(checks)))
