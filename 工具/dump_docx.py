# -*- coding: utf-8 -*-
"""dump_docx.py — docx 全文转储（按文档顺序，OMML 线性化保留结构分隔符）
用法: python dump_docx.py <docx路径> [输出txt路径]
可复用工具：数学物理单元同步（题目台账/亲算用）"""
import sys, re
from docx import Document
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WC, MC = '{'+W+'}', '{'+M+'}'

def tagof(el):
    return el.tag.split('}')[-1]

def omml_text(el):
    """递归线性化 OMML，保留 m:d 分隔符 / m:rad 根号 / m:f 分数 / 上下标"""
    t = tagof(el)
    if t == 't':
        return el.text or ''
    if t == 'f':  # 分数
        num = el.find(MC+'num'); den = el.find(MC+'den')
        return '(' + ''.join(omml_text(c) for c in num) + ')/(' + ''.join(omml_text(c) for c in den) + ')'
    if t == 'rad':
        deg = None; e = el.find(MC+'e')
        d = el.find(MC+'deg')
        if d is not None:
            dt = ''.join(omml_text(c) for c in d)
            deg = dt.strip()
        inner = ''.join(omml_text(c) for c in e) if e is not None else ''
        return ('root[' + deg + '](' if deg else '√(') + inner + ')'
    if t == 'sSup':
        e = el.find(MC+'e'); sup = el.find(MC+'sup')
        return ''.join(omml_text(c) for c in e) + '^(' + ''.join(omml_text(c) for c in sup) + ')'
    if t == 'sSub':
        e = el.find(MC+'e'); sub = el.find(MC+'sub')
        return ''.join(omml_text(c) for c in e) + '_(' + ''.join(omml_text(c) for c in sub) + ')'
    if t == 'sPre':
        sub = el.find(MC+'sub'); sup = el.find(MC+'sup'); e = el.find(MC+'e')
        return '_(' + (''.join(omml_text(c) for c in sub) if sub is not None else '') + ')^(' + \
               (''.join(omml_text(c) for c in sup) if sup is not None else '') + ')' + \
               (''.join(omml_text(c) for c in e) if e is not None else '')
    if t == 'd':  # 括号/绝对值等定界符
        fPr = el.find(MC+'dPr')
        beg, end = '(', ')'
        if fPr is not None:
            b = fPr.find(MC+'begChr'); e2 = fPr.find(MC+'endChr')
            if b is not None: beg = b.get(MC+'val') or ''
            if e2 is not None: end = e2.get(MC+'val') or ''
            if b is None: beg = '('
            if e2 is None: end = ')'
        inner = ''
        for e3 in el.findall(MC+'e'):
            inner += ''.join(omml_text(c) for c in e3) + ','
        return beg + inner.rstrip(',') + end
    if t == 'nary':  # 求和/乘积
        sub = el.find(MC+'sub'); sup = el.find(MC+'sup'); e = el.find(MC+'e')
        chrEl = el.find(MC+'naryPr')
        op = '∑'
        if chrEl is not None:
            c = chrEl.find(MC+'chr')
            if c is not None and c.get(MC+'val'): op = c.get(MC+'val')
        return op + '_(' + (''.join(omml_text(c) for c in sub) if sub is not None else '') + ')^(' + \
               (''.join(omml_text(c) for c in sup) if sup is not None else '') + ')' + \
               (''.join(omml_text(c) for c in e) if e is not None else '')
    if t == 'func':
        fname = el.find(MC+'fName'); e = el.find(MC+'e')
        return (''.join(omml_text(c) for c in fname) if fname is not None else '') + \
               ('(' + ''.join(omml_text(c) for c in e) + ')' if e is not None else '')
    if t in ('r',):
        txt = ''
        for c in el:
            ct = tagof(c)
            if ct == 't': txt += c.text or ''
        return txt
    if t == 'eqArr':
        parts = []
        for e4 in el.findall(MC+'e'):
            parts.append(''.join(omml_text(c) for c in e4))
        return ' ‖ '.join(parts)
    # 其余容器：递归
    out = ''
    for c in el:
        ct = tagof(c)
        if ct.endswith('Pr'): continue
        out += omml_text(c)
    return out

def para_text(p_el):
    """段落全文（w:t + m:t 按文档顺序）"""
    parts = []
    def walk(el):
        for c in el:
            ct = tagof(c)
            if ct == 't' and c.tag.startswith(WC):
                parts.append(c.text or '')
            elif ct == 'oMath':
                parts.append('⟦' + omml_text(c) + '⟧')
            elif ct == 'oMathPara':
                for om in c.findall(MC+'oMath'):
                    parts.append('⟦' + omml_text(om) + '⟧')
            elif ct in ('drawing', 'pict', 'object'):
                parts.append('【图】')
            elif ct == 'br':
                parts.append('⏎')
            elif ct == 'tab':
                parts.append('\t')
            else:
                walk(c)
    walk(p_el)
    return ''.join(parts)

def main():
    src, dst = sys.argv[1], sys.argv[2]
    doc = Document(src)
    body = doc.element.body
    lines = []
    tbl_i = 0
    for child in body.iterchildren():
        ct = tagof(child)
        if ct == 'p':
            t = para_text(child)
            lines.append(t)
        elif ct == 'tbl':
            tbl_i += 1
            lines.append(f'───表格{tbl_i}───')
            for tr in child.findall(WC+'tr'):
                cells = []
                for tc in tr.findall(WC+'tc'):
                    ctxt = ' '.join(para_text(p) for p in tc.findall('.//'+WC+'p'))
                    cells.append(ctxt.strip())
                lines.append(' | '.join(cells))
            lines.append(f'───表格{tbl_i}结束───')
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    n = len([l for l in lines if l.strip()])
    print(f'OK {src} -> {dst}  非空行数={n} 表格数={tbl_i}')

if __name__ == '__main__':
    main()
