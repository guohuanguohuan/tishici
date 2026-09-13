# -*- coding: utf-8 -*-
# OMML 按对象读：解析 m:f(分式)/m:rad(根式)/m:sSub 等，还原分式与根式结构
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn

M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def omml_to_text(el):
    """递归解析 OMML 元素为可读文本（分式 A/B、根式 √()、上下标）"""
    tag = el.tag
    if tag == M + 't':
        return el.text or ''
    if tag == M + 'f':  # 分式
        num = den = ''
        for ch in el:
            if ch.tag == M + 'num': num = omml_to_text(ch)
            if ch.tag == M + 'den': den = omml_to_text(ch)
        return f"〔{num}／{den}〕"
    if tag == M + 'rad':  # 根式
        deg = ''
        e = ''
        for ch in el:
            if ch.tag == M + 'deg': deg = omml_to_text(ch)
            if ch.tag == M + 'e': e = omml_to_text(ch)
        return f"√({e})" if not deg else f"({e})^(1/({deg}))"
    if tag == M + 'sSub':
        base = sub = ''
        for ch in el:
            if ch.tag == M + 'e': base = omml_to_text(ch)
            if ch.tag == M + 'sub': sub = omml_to_text(ch)
        return f"{base}_{sub}"
    if tag == M + 'sSup':
        base = sup = ''
        for ch in el:
            if ch.tag == M + 'e': base = omml_to_text(ch)
            if ch.tag == M + 'sup': sup = omml_to_text(ch)
        return f"{base}^({sup})"
    if tag == M + 'd':  # 括号组
        inner = ''.join(omml_to_text(ch) for ch in el.findall(M + 'e'))
        return f"({inner})"
    if tag == M + 'func':
        name = val = ''
        for ch in el:
            if ch.tag == M + 'fName': name = omml_to_text(ch)
            if ch.tag == M + 'e': val = omml_to_text(ch)
        return name + val
    if tag == W + 't':
        return el.text or ''
    if tag == W + 'br':
        return ' ⏎ '
    return ''.join(omml_to_text(ch) for ch in el)

def para_render(p):
    return ''.join(omml_to_text(ch) for ch in p._p.iter() if ch.tag in (M+'oMath', M+'oMathPara') or ch.tag == W+'r')

ROOT = r"C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第2章 直线与圆的方程/"
FILES = {
    "件4": (ROOT + "4 直线的方程综合（共23题）.docx", 96, 107),
    "件2": (ROOT + "2 直线的倾斜角与斜率（共49题）.docx", 423, 432),
    "件5": (ROOT + "5 直线的交点坐标与距离公式（共43题）.docx", 246, 257),
}
from docx.text.paragraph import Paragraph
for name, (path, lo, hi) in FILES.items():
    doc = Document(path)
    plist = [Paragraph(p, doc) for p in doc.element.body.iter(qn('w:p'))]
    print(f"===== {name} 段{lo}~{hi} OMML对象层渲染 =====")
    for i in range(lo, min(hi + 1, len(plist))):
        print(f"[{i}] {para_render(plist[i])}")
    print()
