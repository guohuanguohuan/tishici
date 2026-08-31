# -*- coding: utf-8 -*-
"""N15 挖空双标记复扫：删「＿＿」空线（答案已嵌原位）；悬空＿＿无答案＝红旗"""
import zipfile, re, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

def lin(el):
    out = []
    for sub in el.iter():
        if not isinstance(sub.tag, str): continue
        if sub.tag in (w('t'), m('t')): out.append(sub.text or '')
    return ''.join(out)

def main(path):
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(w('body'))
    removed_runs = 0
    removed_chars = 0
    red_flags = []
    for p in body.iter(w('p')):
        rs = p.findall('.//' + w('r'))
        # 逐run判断：run文本去空白后全为＿ → 空线run候选
        to_del = []
        for r in rs:
            t = ''.join(tt.text or '' for tt in r.iter() if tt.tag == w('t'))
            if t and '＿' in t and re.fullmatch(r'＿+', t.strip()):
                to_del.append((r, t))
        if not to_del: continue
        # 红旗核验：删后段落内必须仍有灰底内容（文字或OMML）作为答案
        grey_left = any(
            (rr.find(w('rPr')) is not None and rr.find(w('rPr')).find(w('shd')) is not None)
            for rr in rs if rr not in [x[0] for x in to_del]
        ) or any(
            h.find(w('rPr')) is not None and h.find(w('rPr')).find(w('shd')) is not None
            for h in p.findall('.//' + m('r')) + p.findall('.//' + m('ctrlPr'))
        )
        if not grey_left:
            red_flags.append(lin(p)[:80])
        for r, t in to_del:
            removed_chars += len(re.sub(r'\s', '', t))
            r.getparent().remove(r)
            removed_runs += 1
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.n15tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n, b in parts.items():
            zo.writestr(n, b)
    for i in range(12):
        try:
            os.replace(tmp, path); break
        except PermissionError:
            time.sleep(5)
    print(json.dumps({'删空线run数': removed_runs, '删空线字符数': removed_chars, '红旗段数': len(red_flags)}, ensure_ascii=False))
    for f in red_flags:
        print('RED_FLAG:', f)
    # 复扫清零断言
    with zipfile.ZipFile(path) as z:
        doc2 = etree.fromstring(z.read('word/document.xml'))
    remain = 0
    for p in doc2.iter(w('p')):
        remain += len(re.findall(r'＿', lin(p)))
    print('复扫残余＿字符:', remain)

if __name__ == '__main__':
    main(sys.argv[1])
