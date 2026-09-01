# -*- coding: utf-8 -*-
"""omml_sz_strip.py — A'改制轮E2一次性脚本（规格书§6裁决1）：
m:oMath 子树内显式 w:sz/w:szCs 一律剥除（18/21历史杂值交docDefaults继承24半点）；
公式字体Cambria Math与公式内容不碰、文字零改动。
断言：w:t/m:t 字符流前后恒等；仅word/*.xml部件被改写；剥除计数落盘JSON。
用法: python omml_sz_strip.py <in.docx> <out.docx> <计数.json>
幂等：二跑剥除计数=0。"""
import sys, os, json, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)

def text_flow(doc):
    out = []
    for el in doc.iter():
        ln = etree.QName(el).localname if isinstance(el.tag, str) else '?'
        if ln in ('t',):
            ns = etree.QName(el).namespace
            out.append((ns, el.text or ''))
    return out

def main(inp, outp, jp):
    zin = zipfile.ZipFile(inp)
    members = zin.namelist()
    parts = {n: zin.read(n) for n in members}
    zin.close()
    counts = {}
    changed = {}
    for name in members:
        if not (name.startswith('word/') and name.endswith('.xml')):
            continue
        try:
            doc = etree.fromstring(parts[name])
        except Exception:
            continue
        ns_strip = {'stripped_sz': 0, 'stripped_szCs': 0, 'empty_rpr_removed': 0, 'omath_count': 0}
        # 仅处理含 m:oMath / m:oMathPara 的部件
        roots = list(doc.iter(mq('oMath'))) + list(doc.iter(mq('oMathPara')))
        if not roots:
            continue
        # oMathPara 子树含 oMath；去重收集子树节点集合
        seen = set()
        subtree_nodes = []
        for r in roots:
            for node in r.iter():
                if id(node) not in seen:
                    seen.add(id(node))
                    subtree_nodes.append(node)
        ns_strip['omath_count'] = len(list(doc.iter(mq('oMath'))))
        for node in subtree_nodes:
            ln = etree.QName(node).localname if isinstance(node.tag, str) else '?'
            if ln == 'rPr':  # w:rPr（m:r 内与 m:ctrlPr 内）
                for tag in ('sz', 'szCs'):
                    for ch in node.findall(q(tag)):
                        node.remove(ch)
                        ns_strip['stripped_' + ('sz' if tag == 'sz' else 'szCs')] += 1
                if len(node) == 0 and not (node.text or '').strip():
                    par = node.getparent()
                    if par is not None:
                        par.remove(node)
                        ns_strip['empty_rpr_removed'] += 1
        # 字符流恒等断言（对照剥除前）
        before = text_flow(etree.fromstring(parts[name]))
        after = text_flow(doc)
        assert before == after, '字符流漂移: %s' % name
        if ns_strip['stripped_sz'] or ns_strip['stripped_szCs'] or ns_strip['empty_rpr_removed']:
            parts[name] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
            changed[name] = dict(ns_strip)
        counts[name] = dict(ns_strip)
    # 落盘（其余成员逐字节保留）
    with zipfile.ZipFile(outp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in members:
            zout.writestr(n, parts[n])
    total = sum(c['stripped_sz'] + c['stripped_szCs'] for c in counts.values())
    summary = {'输入': os.path.basename(inp), '总剥除sz+szCs': total,
               '分部件': counts, 'oMath块数': sum(c['omath_count'] for c in counts.values())}
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
