# -*- coding: utf-8 -*-
"""fixture_build.py — T2一次性脚本：构造新三色板演示 docx（六类底纹计数/灰度三值校验/灰底改色 验收载体）。
形态＝2026-08-31 N4/N5/N6 新口径：章·节段级#ADC2DA（节走「标题3」样式继承底纹）、讲部·题型段级#C6D4E3、
题号块底纹只盖「N．」、块标签芯片、条目号/第一子层、答案值/需背、并行解法标记、OMML挂点、导航表头 tcPr。
--dirty：同款再注入 A6A6A6 run＋D9D9D9 tcPr（灰底改色迁移链用）。"""
import sys, zipfile, os

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def rn(t, ns=W): return '{%s}%s' % (ns, t)

SHD = lambda f: ('<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % f) if f else ''
def r(text, shd=None, bold=False, sz=None):
    rpr = ''
    if shd or bold or sz:
        rpr = '<w:rPr>%s%s%s</w:rPr>' % (
            '<w:b/>' if bold else '', ('<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz)) if sz else '', SHD(shd) if shd else '')
    t = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, t)
def p(runs, ppr='', style=None, shd=None, keep=False):
    inner = ''
    if style or shd:
        inner = ('<w:pStyle w:val="%s"/>' % style) if style else ''
        inner += SHD(shd) if shd else ''
    ppr_full = '<w:pPr>%s</w:pPr>' % inner if (inner or not keep) else ''
    return '<w:p>%s%s</w:p>' % (ppr_full if inner else ppr, ''.join(runs))

OMML = ('<m:oMath><m:r><w:rPr>%s</w:rPr><m:t>a</m:t></m:r></m:oMath>' % SHD('C9C9C9'))

body = []
# 章/文内开头标题：直挂段级 #ADC2DA ＋ 32半点加粗
body.append(p([r('测试版式 第1章 演示·讲练件（3题）', bold=True, sz=32)], shd='ADC2DA'))
# 章首导航表（表头 tcPr C9C9C9；表头 run 加粗灰底→登记不入六类）
cell = lambda txt, tcshd, rshd, bold: (
    '<w:tc><w:tcPr><w:tcW w:w="4250" w:type="dxa"/>%s</w:tcPr>%s</w:tc>'
    % (SHD(tcshd) if tcshd else '', p([r(txt, shd=rshd, bold=bold)])))
body.append('<w:tbl><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="auto"/>'
            '<w:left w:val="single" w:sz="4" w:color="auto"/><w:bottom w:val="single" w:sz="4" w:color="auto"/>'
            '<w:right w:val="single" w:sz="4" w:color="auto"/></w:tblBorders></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="4250"/><w:gridCol w:w="4250"/></w:tblGrid>'
            '<w:tr>' + cell('教材节', 'C9C9C9', 'C9C9C9', True) + cell('题量', 'C9C9C9', None, True) +
            '</w:tr><w:tr>' + cell('1.1 演示节', None, None, False) + cell('3', None, None, False) +
            '</w:tr></w:tbl>')
# 节标题：挂「标题3」样式（底纹在 styles.xml 样式定义内——样式继承解析路）＋N11合并统计段（含「：」防误判题型）
body.append(p([r('1.1 演示节（第1—3题）　本节3题：简单1｜中档1｜难1', bold=True, sz=28)], style='Heading3'))
# 讲部标题：直挂段级 #C6D4E3 ＋ 24半点加粗
body.append(p([r('1.1.1 方法讲解｜演示讲部（大招1·演示）', bold=True, sz=24)], shd='C6D4E3'))
# 讲部条目：条目号「1．」灰底不加粗＋需背词灰底
body.append(p([r('1．', shd='C9C9C9'), r('演示条目名：核心概念与'),
               r('必背结论甲', shd='C9C9C9'), r('的运用。')]))
# 条目第一子层（N）灰底＋需背词；第二子层①不挂
body.append(p([r('（1）', shd='C9C9C9'), r('第一子层：步骤要点与'), r('关键术语乙', shd='C9C9C9'), r('。')]))
body.append(p([r('①第二子层：不挂底纹的深层要点。')]))
# 题型标题：直挂段级 #C6D4E3
body.append(p([r('1.1.1.1 演示节：演示题型（大招1）', bold=True, sz=24)], shd='C6D4E3'))
body.append(p([r('【编注】', shd='C9C9C9'), r('题型通式：识别信号＋通法步骤（解析档18半点示例）。', sz=18)]))
# Q1 简单
body.append(p([r('1．', shd='C9C9C9', bold=True), r('（简单·保60%·卡壳看答案）', bold=True),
               r('演示题干一：下列说法正确的是（　）')]))
body.append(p([r('A．甲　', sz=24), r('B．乙', sz=24), r('；C．丙；D．丁', sz=24)]))
body.append(p([r('【答案】', shd='C9C9C9'), r(' B', shd='C9C9C9'), r('　'),
               r('【知识点】', shd='C9C9C9'), r('1.1 演示节', sz=18)], keep=True))
body.append(p([r('【分析】', shd='C9C9C9'), r('按定义直接判断。', sz=18)]))
body.append(p([r('【详解】', shd='C9C9C9'), r('演示详解文字一。', sz=18)]))
body.append(p([r('方法一', shd='C9C9C9'), r('：由定义直接得，故选 B。', sz=18)]))
# Q2 中档（答案值多 run 各盖各的）
body.append(p([r('2．', shd='C9C9C9', bold=True), r('（中档·保80%·卡壳看答案）', bold=True),
               r('演示题干二：填空与多选混合。')]))
body.append(p([r('【答案】', shd='C9C9C9'), r(' ①甲', shd='C9C9C9'), r('；', shd='C9C9C9'),
               r('②乙', shd='C9C9C9'), r('　'), r('【知识点】', shd='C9C9C9'), r('1.1 演示节', sz=18)], keep=True))
body.append(p([r('【详解】', shd='C9C9C9'), r('演示详解文字二，含公式 ', sz=18),
               '<m:oMath><m:r><w:rPr>%s</w:rPr><m:t>＝1</m:t></m:r></m:oMath>' % SHD('C9C9C9'),
               r('。', sz=18)]))
# Q3 难（OMML 挂点）
body.append(p([r('3．', shd='C9C9C9', bold=True), r('（难·冲100%·卡壳看答案）', bold=True),
               r('演示题干三：综合论证。')]))
body.append(p([r('【答案】', shd='C9C9C9'), r(' 见详解', shd='C9C9C9'), r('　'),
               r('【知识点】', shd='C9C9C9'), r('1.1 演示节', sz=18)], keep=True))
body.append(p([r('【详解】', shd='C9C9C9'), r('演示详解文字三：设 ', sz=18), OMML, r('，代入即得。', sz=18)]))

dirty = '--dirty' in sys.argv
if dirty:  # 注入旧灰（A6A6A6 run＋D9D9D9 tcPr）——灰底改色迁移链用
    body.insert(2, p([r('旧灰残留行（A6A6A6）', shd='A6A6A6')]))
    body.append(p([r('表内注入前占位', shd='D9D9D9')]))

sectpr = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
          '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" '
          'w:header="283" w:footer="850" w:gutter="0"/></w:sectPr>')
document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="%s" xmlns:m="%s"><w:body>%s%s</w:body></w:document>'
            % (W, M, ''.join(body), sectpr))

styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<w:styles xmlns:w="%s">'
          '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
          '<w:pPr><w:spacing w:before="0" w:after="0" w:line="280" w:lineRule="atLeast"/></w:pPr>'
          '<w:rPr><w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="24"/></w:rPr></w:style>'
          '<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/>'
          '<w:basedOn w:val="Normal"/><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="ADC2DA"/></w:pPr>'
          '<w:rPr><w:b/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:style>'
          '</w:styles>' % W)

ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types '
      'xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
      '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
      '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
      '</Types>')
rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships '
        'xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>')
drels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships '
         'xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
         '</Relationships>')
core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties '
        'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>测试版式 第1章 演示·讲练件（3题）</dc:title>'
        '<dc:creator></dc:creator></cp:coreProperties>')
app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties '
       'xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"/>')

name = '测试版式 第1章 演示·讲练件（3题）%s.docx' % ('·脏灰' if dirty else '')
with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct)
    z.writestr('_rels/.rels', rels)
    z.writestr('word/document.xml', document)
    z.writestr('word/styles.xml', styles)
    z.writestr('word/_rels/document.xml.rels', drels)
    z.writestr('docProps/core.xml', core)
    z.writestr('docProps/app.xml', app)
print('written', name, os.path.getsize(name), 'bytes')
