# -*- coding: utf-8 -*-
"""M配页·使用说明二次收敛：[005]撤【知识点】样例run、[002]/[010]再压（保1页）。"""
import io, sys, zipfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def qn(t): return '{%s}%s' % (W, t)

DOC = '使用说明_wip.docx'
with zipfile.ZipFile(DOC) as z:
    names = z.namelist()
    contents = {n: z.read(n) for n in names}
root = etree.fromstring(contents['word/document.xml'])
body = root.find(qn('body'))
paras = body.findall(qn('p'))

def ptext(p): return ''.join(t.text or '' for t in p.iter(qn('t')))
def rtext(r): return ''.join(t.text or '' for t in r.iter(qn('t')))

# [005]：删【知识点】芯片、空格、值三run（保留【答案】两式样＋说明）
p = paras[5]
assert ptext(p).startswith('【答案】')
kills = []
for r in p.findall(qn('r')):
    t = rtext(r)
    if t in ('【知识点】', '2.4 曲线与方程'):
        kills.append(r)
    elif t == ' ' and kills:
        pass  # 保留判断给下面
# 精确：删「【知识点】」run、其后紧邻的「 」run、「2.4 曲线与方程」run
rs = p.findall(qn('r'))
for i, r in enumerate(rs):
    if rtext(r) == '【知识点】':
        kills = [r]
        if i + 1 < len(rs) and rtext(rs[i+1]) == ' ':
            kills.append(rs[i+1])
        if i + 2 < len(rs) and rtext(rs[i+2]) == '2.4 曲线与方程':
            kills.append(rs[i+2])
        break
assert len(kills) == 3, [rtext(k) for k in kills]
for r in kills:
    p.remove(r)
# 说明run改写（去掉「块标签芯片」句已无样例对应关系，但规则句保留——芯片样例在[007]）
for r in p.findall(qn('r')):
    if rtext(r).startswith('　答案值分型'):
        r.find(qn('t')).text = ('　答案值分型（N7·A′改制）：【答案】值按形态分型——文字型（如「C」）＝灰底C9C9C9＋'
                                '深蓝#1F4E79；公式型（值含公式，如「x²＋y²＝4」）＝不挂灰底、纯深蓝；混合型从公式型；'
                                '需背内容同款；【知识点】值黑字不挂灰。芯片（【答案】等）只盖【×】、不加粗、黑字。')
        break

# [002] 再压
p = paras[2]
for r in p.findall(qn('r')):
    if rtext(r).startswith('　题号块'):
        r.find(qn('t')).text = ('　题号块（N6·层级制）：「节号-序号．（档位·提分线·卡壳看答案）」——底纹盖整个'
                                '「节号-序号．」、括注不挂底纹、整块加粗；序号＝节内连续；题间不留空行，靠它分隔。'
                                '衔接件全部必会——两段式「节号-序号．（衔接必会·卡壳看答案）」。')
        break

# [010] 再压
p = paras[10]
for r in p.findall(qn('r')):
    if rtext(r).startswith('解析块浅底'):
        r.find(qn('t')).text = ('解析块浅底（第七类底纹·A′改制）：带题件解析块全部段落（【答案】【知识点】标签行、'
                                '【分析】【详解】【点睛】等块、【编注】、题型通式句）整段铺#F2F2F2浅底（本段与上行即式样）'
                                '——浅底即题干与解析的区分线；题干、选项、讲部讲解白底，知识清单全件白底。'
                                '字号行距归一：全件一律小4号12pt（旧双档制废止）。')
        break

contents['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = DOC + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.writestr(n, contents[n])
shutil.move(tmp, DOC)
print('二次收敛完成')
