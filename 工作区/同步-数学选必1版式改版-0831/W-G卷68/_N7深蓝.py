# -*- coding: utf-8 -*-
"""N7 深蓝字：答案值/挖空答案 run（灰底C9C9C9保留）→ w:color 1F4E79
   块标签芯片（【×】/方法N/［方法N］）、条目号/题号块、导航表 不变黑字"""
import zipfile, re, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

BLUE = '1F4E79'
PARALLEL = re.compile(r'^(［?(方法[一二三四五六七八九十]|解法[一二三四五六七八九十]|另解|法[一二三四五六七八九十])］?)[：:]?$')
ANS_START = re.compile(r'^(【答案】|\(\d\)|（[ⅠⅡⅢⅣⅤ\d]+）)')

def rtext(r):
    return ''.join(t.text or '' for t in r.iter() if t.tag in (w('t'), m('t')))

def get_rPr(r, create=True):
    rPr = r.find(w('rPr'))
    if rPr is None and create:
        rPr = etree.SubElement(r, w('rPr'))
        r.insert(0, rPr)
    return rPr

def set_color(rPr):
    c = rPr.find(w('color'))
    if c is None:
        c = etree.SubElement(rPr, w('color'))
    c.set(w('val'), BLUE)

def in_table(p):
    par = p.getparent()
    while par is not None:
        if par.tag == w('tbl'): return True
        par = par.getparent()
    return False

def main(path):
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(w('body'))
    cnt = {'答案值': 0, '挖空答案': 0, 'OMML答案': 0, '跳过芯片': 0, '跳过表内': 0, '已有蓝': 0}
    for p in body.iter(w('p')):
        tbl = in_table(p)
        rs = p.findall('.//' + w('r'))
        ptxt = ''.join(rtext(x) for x in rs)
        is_ans = bool(ANS_START.match(ptxt))
        for r in rs:
            rPr = r.find(w('rPr'))
            if rPr is None: continue
            s = rPr.find(w('shd'))
            if s is None or s.get(w('fill')) != 'C9C9C9': continue
            t = rtext(r)
            if tbl:
                cnt['跳过表内'] += 1; continue
            if re.fullmatch(r'\d+．', t) or re.fullmatch(r'【[^】]*】', t.strip()) or re.fullmatch(r'（\d+）', t):
                continue  # 题号/条目号/芯片——黑字
            if PARALLEL.match(t.strip()):
                cnt['跳过芯片'] += 1; continue
            col = rPr.find(w('color'))
            if col is not None and col.get(w('val')) == BLUE:
                cnt['已有蓝'] += 1; continue
            set_color(rPr)
            cnt['答案值' if is_ans else '挖空答案'] += 1
    # OMML：凡带 C9C9C9 灰的 m:r/w:rPr 与 ctrlPr/w:rPr → 深蓝（仅答案值与讲部挖空处存在）
    for p in body.iter(w('p')):
        for holder in p.findall('.//' + m('r')) + p.findall('.//' + m('ctrlPr')):
            rPr = holder.find(w('rPr'))
            if rPr is None: continue
            s = rPr.find(w('shd'))
            if s is None or s.get(w('fill')) != 'C9C9C9': continue
            col = rPr.find(w('color'))
            if col is not None and col.get(w('val')) == BLUE: continue
            set_color(rPr)
            cnt['OMML答案'] += 1
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.n7tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n, b in parts.items():
            zo.writestr(n, b)
    for i in range(12):
        try:
            os.replace(tmp, path); break
        except PermissionError:
            time.sleep(5)
    print(json.dumps(cnt, ensure_ascii=False))
    print('深蓝run合计(文字):', cnt['答案值'] + cnt['挖空答案'])

if __name__ == '__main__':
    main(sys.argv[1])
