# -*- coding: utf-8 -*-
"""dxml.py — 实验卷装配与docx手术共享库（本轮自用，收尾随中间文件删除）"""
import zipfile, re, os, hashlib
from docx import Document
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
V = 'urn:schemas-microsoft-com:vml'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WC, RC, AC, VC, MC = '{%s}' % W, '{%s}' % R, '{%s}' % A, '{%s}' % V, '{%s}' % M

def qn(t):
    p, l = t.split(':')
    return {'w': WC, 'r': RC, 'a': AC, 'v': VC, 'm': MC}[p] + l

def el_text(el):
    """段落/表格全部 w:t 文本"""
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))

def body_children(doc_path):
    """返回 [(idx, element, text)] — body 直接子元素（段+表），排除 sectPr"""
    doc = Document(doc_path)
    body = doc.element.body
    out = []
    for i, ch in enumerate(body):
        tag = etree.QName(ch).localname
        if tag == 'sectPr':
            continue
        out.append((len(out), ch, el_text(ch)))
    return doc, out

SEC_TITLE = re.compile(r'^\d+\.\d+(?:\.\d+)?\s+\S')
TYPE_TITLE = re.compile(r'^\d+(?:\.\d+){1,2}\s+\S{1,30}[：:]')
QNUM = re.compile(r'^(\d{1,3})[．.](?!\d)')

def classify(text):
    ts = text.strip()
    if TYPE_TITLE.match(ts):
        return 'type'
    if SEC_TITLE.match(ts):
        return 'sec'
    if QNUM.match(ts):
        return 'q'
    return 'x'

def find_question_block(children, qnum, start_after=0):
    """从 children 定位题号 qnum 的块：起始段到下一 分类边界 前。返回 (start_idx, end_idx_exclusive)"""
    for i in range(start_after, len(children)):
        idx, el, t = children[i]
        m = QNUM.match(t.strip())
        if m and int(m.group(1)) == qnum:
            j = i + 1
            while j < len(children):
                ts = children[j][2].strip()
                if classify(ts) in ('q', 'type', 'sec'):
                    break
                j += 1
            return i, j
    return None, None

def blk_rids(el):
    """收集块内全部 rId 引用（blip embed / imagedata id）"""
    rids = set()
    for blip in el.iter(qn('a:blip')):
        v = blip.get(qn('r:embed')) or blip.get(qn('r:link'))
        if v: rids.add(v)
    for im in el.iter(qn('v:imagedata')):
        v = im.get(qn('r:id'))
        if v: rids.add(v)
    return rids

def rid_target(rels, rid):
    for rel in rels:
        if rel.rId == rid:
            return rel
    return None

def add_image_to(dest_doc, blob, ext):
    """把图片 blob 加入 dest 包，返回新 rId。emf/wmf 走手动 part 兜底。"""
    from docx.image.image import Image as DocxImage
    from io import BytesIO
    part = dest_doc.part
    try:
        image_part, rId = part.get_or_add_image_part(BytesIO(blob))
        return rId
    except Exception:
        # 手动兜底：新建唯一 partname
        from docx.opc.part import Part
        from docx.opc.packuri import PackURI
        ct = {'emf': 'image/x-emf', 'wmf': 'image/x-wmf'}.get(ext, 'application/octet-stream')
        existing = [p.partname for p in part.package.iter_parts()]
        n = 1
        while ('/word/media/expimg%d.%s' % (n, ext)) in [str(e) for e in existing]:
            n += 1
        pn = PackURI('/word/media/expimg%d.%s' % (n, ext))
        newpart = Part(pn, ct, blob, part.package)
        return part.relate_to(newpart, RT_IMAGE)

RT_IMAGE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'

def remap_block_els(els, src_doc, dest_doc, rid_map):
    """deepcopy 块并重映射图片 rId（双路 blip/imagedata）。返回新元素列表。"""
    out = []
    for el in els:
        ne = etree.fromstring(etree.tostring(el))
        src_rels = src_doc.part.rels
        for blip in ne.iter(qn('a:blip')):
            old = blip.get(qn('r:embed')) or blip.get(qn('r:link'))
            if not old: continue
            if old not in rid_map:
                rel = rid_target(src_rels.values(), old)
                if rel is None: continue
                blob = rel.target_part.blob
                ext = str(rel.target_part.partname).rsplit('.', 1)[-1]
                rid_map[old] = add_image_to(dest_doc, blob, ext)
            blip.set(qn('r:embed'), rid_map[old])
            if blip.get(qn('r:link')) is not None:
                del blip.attrib[qn('r:link')]
        for im in ne.iter(qn('v:imagedata')):
            old = im.get(qn('r:id'))
            if not old: continue
            if old not in rid_map:
                rel = rid_target(src_rels.values(), old)
                if rel is None: continue
                blob = rel.target_part.blob
                ext = str(rel.target_part.partname).rsplit('.', 1)[-1]
                rid_map[old] = add_image_to(dest_doc, blob, ext)
            im.set(qn('r:id'), rid_map[old])
        out.append(ne)
    return out

def set_first_number(el, num):
    """把段首题号改为 num（只替换数字，保留全角分隔点「．」）"""
    for t in el.iter(qn('w:t')):
        if t.text and QNUM.match(t.text):
            m = QNUM.match(t.text)
            t.text = str(num) + t.text[m.end(1):]
            return True
    # 跨 run：首 t 纯数字，次 t 以．开头
    ts = list(el.iter(qn('w:t')))
    for k, t in enumerate(ts):
        if t.text and t.text.strip().isdigit():
            t.text = str(num)
            return True
    return False

def new_title_para(model_title_el, text, bold=True):
    """以现有标题段为模板 deepcopy，替换文字为 text"""
    ne = etree.fromstring(etree.tostring(model_title_el))
    ts = [t for t in ne.iter(qn('w:t'))]
    if not ts:
        return None
    # 保留首 run 字体，其余文字 run 删除
    first = ts[0]
    first.text = text
    # 删除 first 所在 run 之后的兄弟 run
    run = first.getparent()
    while run.getnext() is not None:
        if etree.QName(run.getnext()).localname in ('r', 'hyperlink', 'bookmarkStart', 'bookmarkEnd'):
            run.getparent().remove(run.getnext())
        else:
            break
    # 段内其余 run（首个 run 之前的）也删
    p = run.getparent()
    for prev in list(p):
        if prev is run: break
        if etree.QName(prev).localname == 'r':
            p.remove(prev)
    return ne

def md5(b):
    return hashlib.md5(b).hexdigest()
