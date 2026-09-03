# -*- coding: utf-8 -*-
r"""sectPr抽验_子步2.py（子步2代跑②一次性脚本）——六件文末sectPr w:type=continuous在位XML抽验。
断言面：
 A. 六件：文末（body级）sectPr 含 <w:type w:val="continuous"/> 且落 schema 位（pgSz 之前）；
    头部节（段落级）sectPr type=continuous＋cols=1；正文节 cols num=2 space=425 sep=1。
 B. X2/B 深查：body 子元素序列落点——
    X2：文内标题段（idx0，含段落级sectPr＝头部节承载）→ 正文元素；文末sectPr子元素序。
    B ：文内标题段 → 全件统计行 → 导航表（tbl，头部单栏区内）→ 零字符承载段（段落级sectPr，
        spacing line=20 exact＋sz=2，零文本）→ 正文元素；导航表必须在头部节分节符之前。
 另核：段落级sectPr全局仅1处（头部节）；文档末sectPr＝最后一body子元素。
"""
import sys, io, os, zipfile, json
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def nospc(s):
    import re
    return re.sub(r'[\s　]+', '', s or '')

BASE = r'C:\提示词\高中数学\高中数学同步'
FILES = {
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
}

def sect_info(sp):
    kids = [tag(c) for c in sp]
    tp = sp.find(q('type'))
    cols = sp.find(q('cols'))
    pgSz = sp.find(q('pgSz'))
    return {
        'child_order': kids,
        'type': tp.get(q('val')) if tp is not None else None,
        'type_pos_ok': (tp is not None and pgSz is not None and kids.index('type') < kids.index('pgSz')),
        'cols_num': cols.get(q('num')) if cols is not None else None,
        'cols_space': cols.get(q('space')) if cols is not None else None,
        'cols_sep': cols.get(q('sep')) if cols is not None else None,
        'hdr': len(sp.findall(q('headerReference'))),
        'ftr': len(sp.findall(q('footerReference'))),
        'start': (sp.find(q('pgNumType')).get(q('start'))
                  if sp.find(q('pgNumType')) is not None else None),
    }

def probe(code, path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = root.find(q('body'))
    kids = list(body)
    # 段落级 sectPr 定位
    para_sect = [i for i, el in enumerate(kids)
                 if tag(el) == 'p' and el.find(q('pPr')) is not None
                 and el.find(q('pPr')).find(q('sectPr')) is not None]
    body_sect = body.findall(q('sectPr'))
    res = {'n_para_sect': len(para_sect), 'para_sect_idx': para_sect,
           'n_body_sect': len(body_sect), 'last_child_is_sectPr': tag(kids[-1]) == 'sectPr'}
    if len(body_sect) != 1:
        res['FAIL'] = 'body级sectPr数=%d（期望1）' % len(body_sect)
        return res
    sp = body_sect[0]
    res['body_sect'] = sect_info(sp)
    if para_sect:
        hp = kids[para_sect[0]]
        res['head_sect'] = sect_info(hp.find(q('pPr')).find(q('sectPr')))
        res['head_carrier_idx'] = para_sect[0]
        res['head_carrier_text'] = ptext(hp)[:40]
        ppr = hp.find(q('pPr'))
        spc = ppr.find(q('spacing'))
        rpr = ppr.find(q('rPr'))
        sz = rpr.find(q('sz')) if rpr is not None else None
        res['head_carrier_spacing'] = (spc.get(q('line')), spc.get(q('lineRule'))) if spc is not None else None
        res['head_carrier_sz'] = sz.get(q('val')) if sz is not None else None
        res['head_carrier_zero_text'] = (ptext(hp) == '')
    # X2/B 深查：头部区子元素序列
    deep = {}
    if code in ('X2', 'B') and para_sect:
        brk = para_sect[0]
        seq = []
        for i, el in enumerate(kids[:brk + 2]):
            ln = tag(el)
            if ln == 'p':
                t = ptext(el)
                seq.append((i, 'p', t[:30] if t.strip() else '(零字符段)'))
            else:
                cells = []
                if ln == 'tbl':
                    tr = el.find(q('tr'))
                    if tr is not None:
                        cells = [nospc(ptext(tc)) for tc in tr.findall(q('tc'))]
                seq.append((i, ln, cells[:6]))
        deep['head_seq'] = seq
        # 导航表落区：须 < brk（头部单栏区内）
        nav_idx = None
        for i, el in enumerate(kids):
            if tag(el) != 'tbl':
                continue
            tr = el.find(q('tr'))
            if tr is None:
                continue
            cells = [nospc(ptext(tc)) for tc in tr.findall(q('tc'))]
            if any('节名' in c for c in cells) and any('题量' in c for c in cells):
                nav_idx = i
                break
        deep['nav_idx'] = nav_idx
        deep['nav_in_header'] = (nav_idx is not None and nav_idx < brk) if brk is not None else None
        # B：承载段须在导航表之后
        if code == 'B':
            deep['carrier_after_nav'] = (nav_idx is not None and brk == nav_idx + 1)
            deep['carrier_zero'] = res.get('head_carrier_zero_text')
    res['deep'] = deep
    # 汇总断言
    ok = (res['n_body_sect'] == 1 and res['last_child_is_sectPr']
          and res['body_sect']['type'] == 'continuous' and res['body_sect']['type_pos_ok']
          and res['body_sect']['cols_num'] == '2' and res['body_sect']['cols_space'] == '425'
          and res['body_sect']['cols_sep'] == '1'
          and len(para_sect) == 1
          and res.get('head_sect', {}).get('type') == 'continuous'
          and res.get('head_sect', {}).get('cols_num') in (None, '1'))
    if code in ('X2', 'B'):
        if code == 'B':
            ok = ok and deep.get('nav_in_header') and deep.get('carrier_after_nav') and deep.get('carrier_zero')
        else:
            ok = ok and (deep.get('nav_idx') is None)
    res['verdict'] = 'PASS' if ok else 'CHECK'
    return res

if __name__ == '__main__':
    out = {}
    for code, fn in FILES.items():
        out[code] = probe(code, os.path.join(BASE, fn))
        r = out[code]
        bs = r.get('body_sect', {})
        print('[%s] %s | 文末sectPr type=%s(位ok=%s) cols=%s/%s/%s｜段落级sectPr %d处@%s｜末子元素=sectPr:%s'
              % (code, r['verdict'], bs.get('type'), bs.get('type_pos_ok'),
                 bs.get('cols_num'), bs.get('cols_space'), bs.get('cols_sep'),
                 r['n_para_sect'], r['para_sect_idx'], r['last_child_is_sectPr']))
        if r.get('deep'):
            print('   深查:', json.dumps(r['deep'], ensure_ascii=False)[:400])
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sectPr抽验结果.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('落盘:', dst)
