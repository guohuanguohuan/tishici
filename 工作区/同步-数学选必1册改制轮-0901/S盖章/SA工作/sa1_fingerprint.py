# -*- coding: utf-8 -*-
"""SA任务1前置：核对基线X1/C两件指纹——md5、锚数（fix7后X1=40/C=62）、inline数、fix7 PDF页数。
RF2报告§8无字面md5表，一致性以结构指纹（锚数42→40/64→62、COM页数17/77、fix7 PDF页数）为准。"""
import hashlib, os, zipfile, json, sys
sys.stdout.reconfigure(encoding='utf-8')
import fitz

BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\基线'
PDFD = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\PDF'
HERE = os.path.dirname(os.path.abspath(__file__))

res = {}
for code, exp_anchor in (('X1', 40), ('C', 62)):
    p = os.path.join(BASE, code + '.docx')
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    with zipfile.ZipFile(p) as z:
        doc = z.read('word/document.xml').decode('utf-8')
        n_anchor = doc.count('<wp:anchor')
        n_inline = doc.count('<wp:inline')
        members = z.namelist()
    pdfp = os.path.join(PDFD, code + '_fix7.pdf')
    d = fitz.open(pdfp); n_pdf = d.page_count; d.close()
    ok = n_anchor == exp_anchor
    print('%s: md5=%s | wp:anchor=%d(期%d) | wp:inline=%d | zip成员=%d | fix7PDF页=%d | 锚数指纹%s'
          % (code, h, n_anchor, exp_anchor, n_inline, len(members), n_pdf, '✓' if ok else '✗'))
    assert ok, '%s 锚数≠fix7指纹' % code
    res[code] = {'md5': h, 'anchor': n_anchor, 'inline': n_inline,
                 'fix7_pdf_pages': n_pdf, 'members': len(members)}

json.dump(res, open(os.path.join(HERE, '基线指纹.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('saved 基线指纹.json')
