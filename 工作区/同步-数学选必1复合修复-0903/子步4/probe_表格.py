# -*- coding: utf-8 -*-
"""子步4摸底：全件表格盘点（只读）。逐表登记落区/tblW/tblInd/cellMar/gridCol/行列/首行文本/上文线索。"""
import sys, io, os, json, zipfile
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

FILES = {
 'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
 'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'C':  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
 'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F':  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G':  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H':  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
 '封面': '人教B版选必1·封面.docx',
 '使用说明': '人教B版选必1·使用说明.docx',
 '册目录页': '人教B版选必1·册目录页.docx',
 '部分封面1衔接': '人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx',
 '部分封面1清单': '人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx',
 '部分封面1讲练': '人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx',
 '部分封面2衔接': '人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx',
 '部分封面2清单': '人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx',
 '部分封面2讲练': '人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx',
}
SRC = r'C:\提示词\高中数学\高中数学同步'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'probe_表格.json')


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def tbl_info(tbl, zone, depth, ctx, idx):
    tblpr = tbl.find(q('tblPr'))
    tw = tblind = None
    cellmar = {}
    layout = None
    if tblpr is not None:
        e = tblpr.find(q('tblW'))
        if e is not None:
            tw = {'w': int(e.get(q('w')) or 0), 'type': e.get(q('type'))}
        e = tblpr.find(q('tblInd'))
        if e is not None:
            tblind = int(e.get(q('w')) or 0)
        e = tblpr.find(q('tblLayout'))
        if e is not None:
            layout = e.get(q('type'))
        e = tblpr.find(q('tblCellMar'))
        if e is not None:
            for side in ('left', 'right', 'top', 'bottom'):
                s = e.find(q(side))
                if s is not None:
                    cellmar[side] = int(s.get(q('w')) or 0)
    grid = tbl.find(q('tblGrid'))
    cols = [int(g.get(q('w')) or 0) for g in grid.findall(q('gridCol'))] if grid is not None else []
    rows = tbl.findall(q('tr'))
    ncells = len(rows[0].findall(q('tc'))) if rows else 0
    first_row_txt = ' | '.join(ptext(tc)[:18] for tc in rows[0].findall(q('tc'))) if rows else ''
    nested = len(tbl.findall('.//' + q('tbl')))
    return {'idx': idx, 'zone': zone, 'depth': depth, 'tblW': tw, 'tblInd': tblind,
            'layout': layout, 'cellMar': cellmar, 'gridCol': cols, 'gridSum': sum(cols),
            'rows': len(rows), 'cols': ncells, 'firstRow': first_row_txt, 'nested': nested,
            'ctx': ctx[-40:]}


def walk_body(body):
    """产出 (kids, header_break_index)。header_break_index＝含sectPr段的下标，无则None。"""
    kids = list(body)
    brk = None
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'p':
            ppr = el.find(q('pPr'))
            if ppr is not None and ppr.find(q('sectPr')) is not None:
                brk = i
                break
    return kids, brk


def sect_cols(sect):
    cols = sect.find(q('cols'))
    if cols is None:
        return {'num': 1, 'space': 425}
    return {'num': int(cols.get(q('num')) or 1), 'space': int(cols.get(q('space')) or 425)}


def probe(path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = root.find(q('body'))
    kids, brk = walk_body(body)
    # 节参数：文末sectPr＋头部节sectPr
    body_sect = body.find(q('sectPr'))
    pgSz, pgMar = body_sect.find(q('pgSz')), body_sect.find(q('pgMar'))
    pgw = int(pgSz.get(q('w')))
    ml, mr = int(pgMar.get(q('left'))), int(pgMar.get(q('right')))
    sects = [{'zone': 'body', **sect_cols(body_sect)}]
    if brk is not None:
        hsect = kids[brk].find(q('pPr')).find(q('sectPr'))
        sects.insert(0, {'zone': 'header', **sect_cols(hsect)})
    tables = []
    ctx = ''
    for i, el in enumerate(kids):
        ln = etree.QName(el).localname
        zone = ('header' if (brk is not None and i <= brk) else 'body') if brk is not None else 'body'
        if ln == 'p':
            t = ptext(el).strip()
            if t:
                ctx = t
        elif ln == 'tbl':
            tables.append(tbl_info(el, zone, 1, ctx, len(tables) + 1))
            # 嵌套表（深度2+，单元格内）
            for ntbl in el.iter(q('tbl')):
                if ntbl is el:
                    continue
                tables.append(tbl_info(ntbl, zone + '/nested', 2, ctx, len(tables) + 1))
    return {'pgw': pgw, 'ml': ml, 'mr': mr, 'sects': sects, 'has_break': brk is not None,
            'content_w': pgw - ml - mr, 'tables': tables}


def main():
    out = {}
    for code, fn in FILES.items():
        p = os.path.join(SRC, fn)
        if not os.path.exists(p):
            out[code] = {'error': 'missing'}
            continue
        out[code] = probe(p)
        t = out[code]
        print('%-14s 表%d 节:%s 内容宽%d缇' % (code, len(t['tables']),
              '/'.join('%s(cols=%d,sp=%d)' % (s['zone'], s['num'], s['space']) for s in t['sects']),
              t['content_w']))
        for tb in t['tables']:
            tw = tb['tblW']
            print('   #%d %-12s tblW=%s ind=%s lay=%s mar=%s grid=%s(Σ%d) %dx%d nest=%d | %s | %s' % (
                tb['idx'], tb['zone'], tw, tb['tblInd'], tb['layout'], tb['cellMar'],
                tb['gridCol'], tb['gridSum'], tb['rows'], tb['cols'], tb['nested'],
                tb['firstRow'][:50], tb['ctx'][:30]))
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('落盘:', OUT)


if __name__ == '__main__':
    main()
