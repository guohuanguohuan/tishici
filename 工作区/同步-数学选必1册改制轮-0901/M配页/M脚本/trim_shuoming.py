# -*- coding: utf-8 -*-
"""M配页·使用说明图例说明文字收敛（保1页；规则信息不减项、只压表述）。"""
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

T2 = ('　题号块（N6·层级制）：「节号-序号．（档位·提分线·卡壳看答案）」——底纹盖整个「节号-序号．」、'
      '括注不挂底纹、整块加粗；序号＝节内连续。衔接件不区分难度、全部必会——两段式'
      '「节号-序号．（衔接必会·卡壳看答案）」；题间不留空行，靠题号块分隔。')
T5 = ('　答案值分型（N7·A′改制）：【答案】值按形态分型——文字型（如「C」）＝灰底C9C9C9＋深蓝#1F4E79；'
      '公式型（值含公式，如「x²＋y²＝4」）＝不挂灰底、纯深蓝；混合型从公式型；需背内容同款。'
      '块标签芯片只盖【×】、不加粗、黑字。')
T10 = ('解析块浅底（第七类底纹·A′改制）：带题件解析块全部段落（【答案】【知识点】标签行、'
       '【分析】【详解】【点睛】等块、【编注】、题型通式句）整段铺#F2F2F2浅底（本段与上行【答案】行即式样）'
       '——浅底即题干与解析的区分线；题干、选项、讲部讲解白底，知识清单全件白底。'
       '字号行距归一：全件正文与解析一律小4号12pt、行距统一（旧双档制废止）。')

def set_last_run_text(p, txt):
    rs = [r for r in p.findall(qn('r')) if r.find(qn('t')) is not None]
    rs[-1].find(qn('t')).text = txt

assert ptext(paras[2]).startswith('2.4-13．')
assert ptext(paras[5]).startswith('【答案】')
assert ptext(paras[10]).startswith('【详解】')
set_last_run_text(paras[2], T2)
set_last_run_text(paras[5], T5)
set_last_run_text(paras[10], T10)

contents['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = DOC + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.writestr(n, contents[n])
shutil.move(tmp, DOC)
print('说明文字收敛完成')
