# -*- coding: utf-8 -*-
"""任务B：人教B版选必1·使用说明.docx 改版重建（§11三要素·现行版式N1~N23图例区与实物同构）。"""
import zipfile, os
from xml.sax.saxutils import escape

WS = r"C:/Users/28120/Desktop/提示词/工作区/同步-数学选必1版式改版-0831/M3-配页"
OUT = os.path.join(WS, "人教B版选必1·使用说明.docx")
TITLE = "人教B版选必1·使用说明"

FONTS = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/>'

def rpr(sz=None, b=False, color=None, shd=None):
    s = '<w:rPr>' + FONTS
    if b: s += '<w:b/><w:bCs/>'
    if color: s += f'<w:color w:val="{color}"/>'
    if sz: s += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    if shd: s += f'<w:shd w:val="clear" w:color="auto" w:fill="{shd}"/>'
    return s + '</w:rPr>'

def run(text, sz=None, b=False, color=None, shd=None):
    return f'<w:r>{rpr(sz,b,color,shd)}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'

def para(runs_xml, line='280', shd=None, pbdr=None, rule='atLeast'):
    p = '<w:p><w:pPr>'
    if pbdr: p += pbdr
    if shd: p += f'<w:shd w:val="clear" w:color="auto" w:fill="{shd}"/>'
    p += f'<w:spacing w:before="0" w:after="0" w:line="{line}" w:lineRule="{rule}"/><w:jc w:val="left"/></w:pPr>{runs_xml}</w:p>'
    return p

TITLE_BDR = '<w:pBdr><w:bottom w:val="single" w:sz="4" w:space="1" w:color="auto"/></w:pBdr>'
BOX_BDR = ('<w:pBdr><w:top w:val="single" w:sz="4" w:space="4" w:color="auto"/>'
           '<w:left w:val="single" w:sz="4" w:space="4" w:color="auto"/>'
           '<w:bottom w:val="single" w:sz="4" w:space="4" w:color="auto"/>'
           '<w:right w:val="single" w:sz="4" w:space="4" w:color="auto"/></w:pBdr>')

P = []
# ===== 标题（章标题式样：三号加粗＋ADC2DA整行底＋底边框——与内容件文内开头标题同构） =====
P.append(para(run(TITLE, sz='32', b=True), line='410', shd='ADC2DA', pbdr=TITLE_BDR))
# ===== 一、视觉锚图例 =====
P.append(para(run('视觉锚图例（式样＝本册现行版式真实呈现）', sz='18', b=True)))
# L1 题号块（N6：底纹只盖N．、括注不挂底纹、整块加粗）
P.append(para(
    run('1．', sz='24', b=True, shd='C9C9C9') +
    run('（简单·保60%·卡壳看答案）', sz='24', b=True) +
    run('　题号块（N6）：底纹只盖「N．」本身、括注不挂底纹、整块加粗；题与题之间不留空行，靠它分隔。衔接件不区分难度、全部必会——两段式「N．（衔接必会·卡壳看答案）」。', sz='18'),
    line='410'))
# L2 章/节标题整行底纹 ADC2DA（N4/N5）
P.append(para(
    run('1.1 空间向量及其运算', sz='28', b=True) +
    run('　章标题与节标题：整行铺底#ADC2DA＋加粗＋顶格（章三号／节四号），章标题另加底边框通栏细线（N4/N5）。', sz='18'),
    line='410', shd='ADC2DA'))
# L3 讲部/题型标题整行底纹 C6D4E3（N4/N5）
P.append(para(
    run('1.1.1.1 节名：题型名', sz='24', b=True) +
    run('　讲部标题与题型标题：整行铺底#C6D4E3＋加粗＋顶格（均小四，层级靠父链续层序号与底纹色表达）（N4/N5）。', sz='18'),
    line='410', shd='C6D4E3'))
# L4 答案值标记（N7）＋块标签芯片
P.append(para(
    run('【答案】', sz='18', shd='C9C9C9') + run(' ', sz='18') +
    run('C', sz='18', color='1F4E79', shd='C9C9C9') +
    run('　', sz='18') +
    run('【知识点】', sz='18', shd='C9C9C9') + run(' ', sz='18') +
    run('1.1.1 空间向量的概念', sz='18') +
    run('　答案值标记（N7）：【答案】后的值挂灰底＋深蓝#1F4E79字；需背内容同款灰底＋深蓝。块标签芯片（【答案】【知识点】等）只盖【×】、不加粗、黑字。', sz='18')))
# L5 定理框（N23）＋框内需背式样
P.append(para(
    run('定理框（N23）：定理/公式级需背条目整段加细框（本段即式样），框内需背内容挂灰底＋深蓝——如「', sz='18') +
    run('充要条件', sz='18', color='1F4E79', shd='C9C9C9') +
    run('」与「', sz='18') +
    run('存在唯一', sz='18', color='1F4E79', shd='C9C9C9') +
    run('」二词式样；普通需背词只挂灰底不加框。', sz='18'),
    pbdr=BOX_BDR))
# L6 块标签芯片枚举
chips = ['【答案】', '【知识点】', '【分析】', '【详解】', '【点睛】', '【编注】', '【大招指引】', '【题后反思】', '【温馨提醒】']
rx = ''
for c in chips:
    rx += run(c, sz='18', shd='C9C9C9') + run(' ', sz='18')
rx += run('块标签芯片：凡行内【×】栏目标签挂同款灰底、不加粗、只盖标签本身；【编注】开头＝编者补写的思路提示或通法，不是素材原文。', sz='18')
P.append(para(rx))
# L7 条目号与条目第一子层灰块（＋〔基〕/〔进〕不挂底纹）
P.append(para(
    run('1．', sz='24', shd='C9C9C9') +
    run('〔基〕条目题名', sz='24') +
    run('　', sz='24') +
    run('（1）', sz='24', shd='C9C9C9') +
    run('第一子层内容', sz='24') +
    run('　条目号与条目第一子层：条目号「N．」与第一子层「（N）」同款灰底、不加粗、只盖序号本身；〔基〕/〔进〕分类标记不挂底纹；第二子层①②③不挂。', sz='18'),
    line='410'))
# L8 〔基〕/〔进〕图例句（N16 逐字照抄）
P.append(para(
    run('〔基〕/〔进〕图例句（知识清单件文内开头标题正下方，逐字照抄——N16）：', sz='18') +
    run('〔基〕＝基础必会：必须学完本条目，才能做本章题目｜〔进〕＝进阶汇总：本章各题型常识/结论的汇总，方便复习，必须先做题再回看', sz='18')))
# L9 双档字号示意（N1）
P.append(para(
    run('正档案例试字：题干与选项等学生精读内容＝小4号12pt；', sz='24') +
    run('解析案例试字：【答案】【详解】【编注】等＝小5号9pt——字号双档制（N1，本图例区按§11豁免双档硬约束真实呈现式样）。', sz='18'),
    line='410'))
# ===== 二、难度三档与建议学习路径（在位，照原文） =====
P.append(para(run('难度三档与建议学习路径', sz='18', b=True)))
P.append(para(run('简单：单一知识点直接套用、一两步即可完成；简单档具备本章高考约60%分数目标所需的基本能力。', sz='18')))
P.append(para(run('中档：常规解法需多步转化，或跨一两个知识点的常规组合；简单＋中档合计具备本章高考约80%分数目标所需的能力。', sz='18')))
P.append(para(run('难：只收特别难的题（含原卷压轴），具备本章冲击满分所需的全部能力；名难实易的题一律放简单或中档。', sz='18')))
P.append(para(run('提分线三形态：简单·保60%／中档·保80%／难·冲100%。', sz='18')))
P.append(para(run('建议学习路径：知识清单 → 衔接件 → 讲练件。先用知识清单过一遍本章知识、背下灰底必背内容；有衔接件的章先刷衔接件补齐初中铺垫；再用讲练件按节推进，先读讲部分再做题，组内由易到难。', sz='18')))
# ===== 三、答案用法（关键句底纹维持） =====
P.append(para(run('答案用法', sz='18', b=True)))
P.append(para(run('每题先独立读题动手，卡壳超过10分钟立即看答案学方法、不死磕；看懂后遮住答案重做一遍，隔天重做仍错的题记入错题记录表。', sz='18', shd='C9C9C9')))
# ===== 四、本册件型用法 =====
P.append(para(run('本册件型用法', sz='18', b=True)))
P.append(para(run('衔接件（仅与初中有映照的章配备）：不区分难度、全部必会——题号块「N．（衔接必会·卡壳看答案）」；只考「初中已学＋本章以前」的铺垫题，学本章之前先自测，卡壳处回补后再进本章。', sz='18')))
P.append(para(run('知识清单：本章全部知识条目按教材节归类，条目逐条标〔基〕/〔进〕——基＝教材正文必会，必须先学完才能做本章题；进＝本章各题型常识/结论汇总，先做题再回看。件开头有章知识结构图，先看图定位、再逐条过。', sz='18')))
P.append(para(run('讲练件（每章一件，分卷题号连续）：本册核心件；讲部分（知识讲解＋例题）排在对应题型组之前，题目按教材节×题型分组、组内由易到难，题号后即难度档位；节标题行内附题量统计，章首有导航表与全件统计行。', sz='18')))
P.append(para(run('错题记录件（每章一件，装订在该章讲练本末尾）：三列空行自填表「题号｜错因｜重做日期」，题号由自己填写，错因可参考示例行「知识不会／方法没想到／计算错／审题错」，重做日期用于跟踪回炉；错题多者复印加页。', sz='18')))
P.append(para(run('部分封面件：每个部分（同章同类型件的全部文件）一张，随该部分首件装订，封面上的统计与导读即该部分的总账。装订组合方案（N10）：方案A＝整册装订（配页三件＋各部分各带部分封面）；方案B＝按件型抽订（如全部知识清单、全部讲练）；方案C＝错题集抽订（各章错题记录件按章序）。', sz='18')))
P.append(para(run('分本用法：本册按「每部分一个物理本」分本装订（本划分见装订单「本」列，与页码体系无关）；单本实测超400页时沿件边界二次拆分、不另配封面与册目录页，靠页眉页脚件标识识别。', sz='18')))

sectpr = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
          '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="850" w:footer="850" w:gutter="0"/>'
          '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>')

document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body>' + ''.join(P) + sectpr + '</w:body></w:document>')

styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
 '<w:docDefaults><w:rPrDefault><w:rPr>' + FONTS + '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:rPrDefault>'
 '<w:pPrDefault><w:pPr><w:spacing w:before="0" w:after="0" w:line="280" w:lineRule="atLeast"/><w:jc w:val="left"/></w:pPr></w:pPrDefault></w:docDefaults>'
 '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
 '<w:pPr><w:spacing w:before="0" w:after="0" w:line="280" w:lineRule="atLeast"/><w:jc w:val="left"/></w:pPr>'
 '<w:rPr>' + FONTS + '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:style></w:styles>')

settings = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
 '<w:updateFields w:val="true"/><w:zoom w:percent="100"/>'
 '<w:defaultTabStop w:val="420"/><w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
 '</w:settings>')

content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
 '<Default Extension="xml" ContentType="application/xml"/>'
 '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
 '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
 '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
 '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
 '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
 '</Types>')

rels_root = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
 '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
 '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
 '</Relationships>')

rels_doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
 '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
 '</Relationships>')

core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
 'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
 f'<dc:title>{escape(TITLE)}</dc:title><dc:creator></dc:creator><cp:lastModifiedBy></cp:lastModifiedBy>'
 '<dcterms:created xsi:type="dcterms:W3CDTF">2026-08-31T00:00:00Z</dcterms:created>'
 '<dcterms:modified xsi:type="dcterms:W3CDTF">2026-08-31T00:00:00Z</dcterms:modified></cp:coreProperties>')

app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
 'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docProps/vnd.openxmlformats-officedocument.vml">'
 '<Application>Microsoft Office Word</Application></Properties>')

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', content_types)
    z.writestr('_rels/.rels', rels_root)
    z.writestr('word/document.xml', document)
    z.writestr('word/styles.xml', styles)
    z.writestr('word/settings.xml', settings)
    z.writestr('word/_rels/document.xml.rels', rels_doc)
    z.writestr('docProps/core.xml', core)
    z.writestr('docProps/app.xml', app)

print("built:", OUT, os.path.getsize(OUT), "bytes")
