# -*- coding: utf-8 -*-
"""导航表表头单行化：列分配下限补「表头单元格全宽」（表头不折行），外框 tblW=10206 不变。"""
import sys, io, os, json, zipfile, shutil, hashlib
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
sys.path.insert(0, r'C:\提示词\工具')
from 表格重排工具 import (q, measure_table, allocate, apply_table, plan_table, zones_of,
                        is_navtbl, text_stream, cell_margins, para_width_em, SZ_NORMAL, SLACK)

SRC = r'C:\提示词\高中数学\高中数学同步'
NAV_FILES = {
 'B': os.path.join(SRC, '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
 'E': os.path.join(SRC, '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
}
res = {}
for code, path in NAV_FILES.items():
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = root.find(q('body'))
    ts0 = text_stream(root)
    kids, brk, zp = zones_of(body)
    tbl = None
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'tbl' and is_navtbl(el):
            tbl = el
            break
    assert tbl is not None
    plan = plan_table(tbl, 'header', zp)
    marL, marR = cell_margins(tbl)
    # 表头全宽下限
    rows = tbl.findall(q('tr'))
    mins2 = list(plan['mins'])
    em_tw = (SZ_NORMAL / 2.0) * 20.0
    ci = 0
    for tc in rows[0].findall(q('tc')):
        wmax = 0.0
        for p in tc.findall(q('p')):
            tw_em, _ = para_width_em(p)
            wmax = max(wmax, tw_em * em_tw)
        if ci < len(mins2):
            mins2[ci] = max(mins2[ci], wmax + marL + marR + SLACK)
        ci += 1
    content, _, ncols, _ = measure_table(tbl, SZ_NORMAL)
    alloc = allocate(content, mins2, plan['limit'])
    assert alloc is not None, '表头单行化分配不可行'
    plan['alloc'] = alloc
    chg = apply_table(tbl, plan)
    ok = (ts0 == text_stream(root))
    new_raw = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    sha_b = hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]
    tmp = path + '.tmp_rewrite'
    zin = zipfile.ZipFile(path, 'r')
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            data = new_raw
        zout.writestr(item, data)
    zin.close()
    zout.close()
    shutil.move(tmp, path)
    res[code] = {'alloc': alloc, 'mins2': mins2, 'changes': chg, 'text_equal': ok,
                 'sha_before': sha_b, 'sha_after': hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]}
    print('[%s] 表头单行化 alloc=%s 文字流等=%s sha %s→%s' % (code, alloc, ok, sha_b, res[code]['sha_after']))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '表头单行化_子步6.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
