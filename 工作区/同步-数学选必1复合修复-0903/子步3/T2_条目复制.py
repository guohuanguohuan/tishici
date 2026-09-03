# -*- coding: utf-8 -*-
"""子步3 T2：条目复制（I1/I2 权威源 → B/C/E/F/G/H 讲练件，讲部「知识讲解」块补挂）
口径：任务书T2（条目号/〔基〕〔进〕/灰底/填空化/图/编注说明句照抄；媒体rels双路重映射；
     源段号→目标段号登记＋归一化diff=0）。fail-closed：任一断言不过即拒写。
输出：子步3/补挂态/<原文件名>.docx（不写回产出文件夹——dry-run2确认点后随全链子步收尾写回）
"""
import sys, io, re, zipfile, json, copy, hashlib, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
V = 'urn:schemas-microsoft-com:vml'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def qr(t): return '{%s}%s' % (R, t)
def qwp(t): return '{%s}%s' % (WP, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

BASE = r'C:\提示词\高中数学\高中数学同步'
OUT = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3\补挂态'
SRC = {
    'I1': BASE + r'\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'I2': BASE + r'\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
}
TGT = {
    'B': ('I1', BASE + r'\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
    'C': ('I1', BASE + r'\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
    'E': ('I2', BASE + r'\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
    'F': ('I2', BASE + r'\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
    'G': ('I2', BASE + r'\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
    'H': ('I2', BASE + r'\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
}
VOL_SECS = {
    'B': ['1.1.1', '1.1.2', '1.1.3', '1.2.1', '1.2.2', '1.2.3', '1.2.4'],
    'C': ['1.2.5'],
    'E': ['2.1', '2.2.1', '2.2.2', '2.2.3', '2.2.4', '2.3.1', '2.3.2', '2.3.3'],
    'F': ['2.3.4', '2.4', '2.5.1', '2.5.2'],
    'G': ['2.6.1', '2.6.2', '2.7.1', '2.7.2'],
    'H': ['2.8'],
}
ENT_RE = re.compile(r'^(\d+(?:\.\d+)*)-(\d+)．')
SEC_TITLE_RE = re.compile(r'^(\d+(?:\.\d+)+)\s+(.+?)　本节(\d+)题')

def para_shd_fill(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return None
    shd = ppr.find(q('shd'))
    return shd.get(q('fill')) if shd is not None else None

def para_style(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return None
    st = ppr.find(q('pStyle'))
    return st.get(q('val')) if st is not None else None

def extract_entries(code):
    """源清单：{节号: [(start_idx, [elements])]} 文档序"""
    z = zipfile.ZipFile(SRC[code])
    root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(q('body'))
    children = list(body)
    bounds = []
    for i, el in enumerate(children):
        if tag(el) != 'p': continue
        t = ptext(el)
        if not t.strip(): continue
        m = ENT_RE.match(t)
        if m:
            bounds.append((i, m.group(1)))
        elif para_style(el) == 'JieMingMao' or para_shd_fill(el) == 'ADC2DA':
            bounds.append((i, None))
    marks = [(i, sec) for i, sec in bounds if sec]
    entries = {}
    for i, sec in marks:
        j = len(children)
        for bi, _ in bounds:
            if bi > i:
                j = bi
                break
        entries.setdefault(sec, []).append((i, children[i:j]))
    return entries, z

DOCPr_ASSIGNED = set()

def norm_serialize(el, rid_map, docpr_map, numid_map):
    """递归规范化序列（免疫跨文档根级命名空间声明差异）＋合法重映射属性占位化"""
    def canon(e):
        docpr_mask = set(docpr_map) | set(docpr_map.values()) | DOCPr_ASSIGNED
        numid_mask = set(numid_map) | set(numid_map.values())
        qn = etree.QName(e).namespace if isinstance(e.tag, str) else ''
        head = '<%s[%s]' % (etree.QName(e).localname, (qn or '').rsplit('/', 2)[-1]) if isinstance(e.tag, str) else '<'
        out = [head]
        for k in sorted(e.attrib):
            v = e.attrib[k]
            kl = etree.QName(k).localname
            if k.startswith('{%s}' % R):
                v = '@@RID@@'
            if kl == 'id' and v in docpr_mask:
                v = '@@DOCPr@@'
            if kl == 'val' and v in numid_mask:
                v = '@@NUM@@'
            out.append(' %s="%s"' % (kl, v))
        out.append('>')
        if e.text:
            out.append(e.text)
        for c in e:
            out.append(canon(c))
            if c.tail:
                out.append(c.tail)
        out.append('</>')
        return ''.join(out)
    return canon(el)

def sha1(b): return hashlib.sha1(b).hexdigest()

def process_volume(vol, src_code, src_entries, src_zip):
    src_path = SRC[src_code]
    tgt_path = TGT[vol][1]
    zin = zipfile.ZipFile(tgt_path)
    names = zin.namelist()
    doc = etree.fromstring(zin.read('word/document.xml'))
    body = doc.find(q('body'))
    rels = etree.fromstring(zin.read('word/_rels/document.xml.rels'))
    RELNS = 'http://schemas.openxmlformats.org/package/2006/relationships'
    rel_map = {rel.get('Id'): rel for rel in rels}
    max_rid = max(int(r[3:]) for r in rel_map if r.startswith('rId') and r[3:].isdigit())
    used_docpr = {int(d.get('id')) for d in doc.iter(qwp('docPr')) if d.get('id') and d.get('id').isdigit()}
    next_docpr = max(used_docpr) + 1
    # 源 rels 映射
    src_rels = etree.fromstring(src_zip.read('word/_rels/document.xml.rels'))
    src_rel_map = {rel.get('Id'): rel for rel in src_rels}
    existing_media = {n for n in names if n.startswith('word/media/')}
    # numbering 处理（仅当目标含 numbering.xml 且复制内容含 numPr）
    has_numbering = 'word/numbering.xml' in names
    numbering = etree.fromstring(zin.read('word/numbering.xml')) if has_numbering else None
    src_numbering = etree.fromstring(src_zip.read('word/numbering.xml')) if 'word/numbering.xml' in src_zip.namelist() else None
    tgt_numids = {n.get(q('numId')) for n in numbering.findall(q('num'))} if numbering is not None else set()
    tgt_absids = [int(a.get(q('abstractNumId'))) for a in numbering.findall(q('abstractNum'))] if numbering is not None else []
    numid_map = {}   # 源numId -> 目标numId
    new_media = []   # (arcname, bytes)
    new_rels = []    # lxml Relationship elements
    media_counter = 0

    def remap_image(old_rid):
        nonlocal max_rid, media_counter
        if old_rid in remap_image.cache:
            return remap_image.cache[old_rid]
        srel = src_rel_map[old_rid]
        target_name = srel.get('Target')           # 如 media/image5.png
        src_part = 'word/' + target_name if not target_name.startswith('word/') else target_name
        data = src_zip.read(src_part)
        ext = src_part.rsplit('.', 1)[-1].lower()
        while True:
            media_counter += 1
            new_part = 'word/media/sub3_%s_%d.%s' % (vol, media_counter, ext)
            if new_part not in existing_media:
                break
        existing_media.add(new_part)
        new_media.append((new_part, data, sha1(data), src_part))
        max_rid += 1
        new_rid = 'rId%d' % max_rid
        rel = etree.SubElement(rels, '{%s}Relationship' % RELNS)
        rel.set('Id', new_rid)
        rel.set('Type', srel.get('Type'))
        rel.set('Target', 'media/sub3_%s_%d.%s' % (vol, media_counter, ext))
        new_rels.append(rel)
        remap_image.cache[old_rid] = new_rid
        return new_rid
    remap_image.cache = {}

    def remap_numid(old_nid):
        if old_nid in numid_map:
            return numid_map[old_nid]
        # 源定义
        snum = None
        for n in src_numbering.findall(q('num')):
            if n.get(q('numId')) == old_nid:
                snum = n
                break
        if snum is None:
            # 悬空引用：源端无定义。若目标亦无此 numId → 保持悬空（渲染一致为零编号）；
            # 若目标恰有定义 → 迁移到目标也不存在的新 numId 保持悬空。
            if old_nid not in tgt_numids:
                numid_map[old_nid] = old_nid
                return old_nid
            new_nid = str(max([int(x) for x in tgt_numids] + [0]) + 1000)
            numid_map[old_nid] = new_nid
            return new_nid
        # 有定义：整体搬迁 abstractNum＋num 到目标（新 id）
        old_abs = snum.find(q('abstractNumId')).get(q('val'))
        new_abs = str(max(tgt_absids + [-1]) + 1)
        tgt_absids.append(int(new_abs))
        for a in src_numbering.findall(q('abstractNum')):
            if a.get(q('abstractNumId')) == old_abs:
                na = copy.deepcopy(a)
                na.set(q('abstractNumId'), new_abs)
                # OOXML 序：abstractNum 须全部位于 num 之前——插到首个 num 前
                first_num = numbering.find(q('num'))
                if first_num is not None:
                    first_num.addprevious(na)
                else:
                    numbering.append(na)
                break
        new_nid = str(max([int(x) for x in tgt_numids] + [0]) + 1)
        tgt_numids.add(new_nid)
        nn = etree.SubElement(numbering, q('num'))
        nn.set(q('numId'), new_nid)
        na2 = etree.SubElement(nn, q('abstractNumId'))
        na2.set(q('val'), new_abs)
        numid_map[old_nid] = new_nid
        return new_nid

    old_children = list(body)
    old_ids = [id(el) for el in old_children]
    old_text_stream = ''.join(
        (t.text or '') for el in old_children for t in el.iter() if tag(t) in ('t',) or t.tag == qm('t'))
    inserted_ids = []
    mapping = []
    cnt = {'讲部标题': 0, '条目块': 0, 'w:p': 0, 'w:tbl': 0, 'w:drawing': 0, '图': 0}

    secs = VOL_SECS[vol]
    # 逐节定位节标题段（段级ADC2DA 且含「本节N题」）
    sec_title_els = []
    for el in body:
        if tag(el) != 'p': continue
        t = ptext(el)
        m = SEC_TITLE_RE.match(t)
        if m and para_shd_fill(el) == 'ADC2DA':
            sec_title_els.append((m.group(1), m.group(2), el))
    found_secs = [s for s, _, _ in sec_title_els]
    assert found_secs == secs, '%s 节标题序列与归属表不符: %r vs %r' % (vol, found_secs, secs)

    rid_map_all, docpr_map_all = {}, {}
    docpr_assigned = set()   # 全部已分配新 docPr id（含被覆盖的旧id重复出现）——归一化掩码用
    block_pairs = []   # (源元素, 复制元素) 逐块归一化diff用
    numid_map_pairs = {}  # 源numId->目标numId（本卷实际发生值变化者）
    for sec_no, sec_name, sec_el in sec_title_els:
        # 克隆模板：本节其后首个 段级C6D4E3 段（讲部/题型标题）
        tmpl = None
        for el in sec_el.itersiblings():
            if tag(el) == 'p' and para_shd_fill(el) == 'C6D4E3':
                tmpl = el
                break
            if tag(el) == 'p' and para_shd_fill(el) == 'ADC2DA':
                break
        assert tmpl is not None, '%s 节 %s 无标题模板段' % (vol, sec_no)
        # 讲部标题段
        hp = etree.Element(q('p'), nsmap=None)
        hp.append(copy.deepcopy(tmpl.find(q('pPr'))))
        base_run = None
        for r in tmpl.findall(q('r')):
            if ''.join(t.text or '' for t in r.findall(q('t'))).strip():
                base_run = r
                break
        assert base_run is not None
        nr = etree.SubElement(hp, q('r'))
        rpr = base_run.find(q('rPr'))
        if rpr is not None:
            nr.append(copy.deepcopy(rpr))
        nt = etree.SubElement(nr, q('t'))
        title_txt = '%s.1 知识讲解｜%s' % (sec_no, sec_name)
        nt.text = title_txt
        nt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        sec_el.addnext(hp)
        anchor = hp
        inserted_ids.append(id(hp))
        cnt['讲部标题'] += 1
        # 条目块
        ent_list = src_entries.get(sec_no, [])
        assert ent_list, '%s 节 %s 源条目为空（覆盖断言失败）' % (vol, sec_no)
        for src_start, block in ent_list:
            tgt_start = list(body).index(anchor) + 1
            for el in block:
                ne = copy.deepcopy(el)
                # 图 rId 重映射
                for b in ne.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
                    e = b.get(qr('embed'))
                    if e:
                        new_rid = remap_image(e)
                        rid_map_all[e] = new_rid
                        b.set(qr('embed'), new_rid)
                    assert b.get(qr('link')) is None, '外链图不支持'
                for vd in ne.iter('{%s}imagedata' % V):
                    assert vd.get(qr('id')) is None, 'VML图引用不支持（未预期）'
                # docPr id 重映射
                for d in ne.iter(qwp('docPr')):
                    old_id = d.get('id')
                    if old_id and old_id.isdigit():
                        d.set('id', str(next_docpr))
                        docpr_map_all[old_id] = str(next_docpr)
                        docpr_assigned.add(str(next_docpr))
                        next_docpr += 1
                # numPr 重映射
                for np in ne.iter(q('numId')):
                    old_nid = np.get(q('val'))
                    if old_nid is not None:
                        new_nid = remap_numid(old_nid)
                        if new_nid != old_nid:
                            np.set(q('val'), new_nid)
                            numid_map_pairs[old_nid] = new_nid
                # 其余 R 命名空间属性必须已全部处理
                for x in ne.iter():
                    for attr in x.attrib:
                        if attr.startswith('{%s}' % R):
                            assert attr == qr('embed'), '未处理的R属性: %s' % attr
                anchor.addnext(ne)
                anchor = ne
                inserted_ids.append(id(ne))
                block_pairs.append((el, ne))
                cnt['条目块元素'] = cnt.get('条目块元素', 0) + 1
                if tag(ne) == 'p': cnt['w:p'] += 1
                if tag(ne) == 'tbl': cnt['w:tbl'] += 1
                cnt['w:drawing'] += len(list(ne.iter(q('drawing'))))
                cnt['图'] += len(list(ne.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')))
            mapping.append({'卷': vol, '节': sec_no, '源': src_code, '源段区间': [src_start, src_start + len(block) - 1],
                            '目标段区间': [tgt_start, tgt_start + len(block) - 1], '元素数': len(block)})
            cnt['条目块'] += 1

    # ===== 断言 =====
    # A1 覆盖断言：本卷条目数合计
    expect_total = sum(len(src_entries[s]) for s in secs)
    assert cnt['条目块'] == expect_total, '%s 覆盖断言失败: %d != %d' % (vol, cnt['条目块'], expect_total)
    # A2 归一化diff=0：逐块比对（源元素 vs 复制元素，合法重映射属性归一化）
    for src_el, new_el in block_pairs:
        DOCPr_ASSIGNED.clear(); DOCPr_ASSIGNED.update(docpr_assigned)
        s_src = norm_serialize(src_el, rid_map_all, docpr_map_all, numid_map_pairs)
        s_new = norm_serialize(new_el, rid_map_all, docpr_map_all, numid_map_pairs)
        if s_src != s_new:
            pos = next((k for k, (x, y) in enumerate(zip(s_src, s_new)) if x != y), min(len(s_src), len(s_new)))
            print('!! %s 归一化diff≠0 @%d len %d/%d' % (vol, pos, len(s_src), len(s_new)))
            print('   SRC: %r' % s_src[max(0, pos - 80):pos + 160])
            print('   NEW: %r' % s_new[max(0, pos - 80):pos + 160])
            print('   docpr_map_all=%r' % docpr_map_all)
            print('   rid_map_all=%r' % rid_map_all)
            raise AssertionError('%s 归一化diff≠0' % vol)
    # A3 原文零改动：旧元素顺序与文字流不变
    new_children = list(body)
    kept = [el for el in new_children if id(el) in set(old_ids)]
    assert [id(el) for el in kept] == old_ids, '%s 旧元素顺序被扰动' % vol
    new_text_kept = ''.join(
        (t.text or '') for el in kept for t in el.iter() if tag(t) == 't' or t.tag == qm('t'))
    assert new_text_kept == old_text_stream, '%s 原文文字流被改动' % vol
    # A4 图守恒：媒体字节哈希
    for new_part, data, h, src_part in new_media:
        assert sha1(src_zip.read(src_part)) == h == sha1(data), '%s 图字节不一致: %s' % (vol, new_part)
    # A5 全部 embed 可解析
    inserted_set = set(inserted_ids)
    for el in new_children:
        if id(el) in inserted_set:
            for b in el.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
                assert b.get(qr('embed')) in rel_map or any(r.get('Id') == b.get(qr('embed')) for r in new_rels)

    # ===== 落盘 =====
    # [Content_Types].xml 扩展名兜底
    ct = etree.fromstring(zin.read('[Content_Types].xml'))
    defaults = {d.get('Extension').lower() for d in ct.findall('{%s}Default' % CT)}
    ct_changed = False
    for new_part, data, h, src_part in new_media:
        ext = new_part.rsplit('.', 1)[-1].lower()
        if ext not in defaults:
            d = etree.SubElement(ct, '{%s}Default' % CT)
            d.set('Extension', ext)
            d.set('ContentType', {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                                  'emf': 'image/x-emf', 'wmf': 'image/x-wmf', 'gif': 'image/gif'}[ext])
            defaults.add(ext)
            ct_changed = True
    os.makedirs(OUT, exist_ok=True)
    out_path = os.path.join(OUT, os.path.basename(tgt_path))
    new_doc = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    new_rels_xml = etree.tostring(rels, xml_declaration=True, encoding='UTF-8', standalone=True)
    new_ct = etree.tostring(ct, xml_declaration=True, encoding='UTF-8', standalone=True)
    new_numbering = etree.tostring(numbering, xml_declaration=True, encoding='UTF-8', standalone=True) if numbering is not None else None
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            fn = item.filename
            if fn == 'word/document.xml':
                zout.writestr(item, new_doc)
            elif fn == 'word/_rels/document.xml.rels':
                zout.writestr(item, new_rels_xml)
            elif fn == '[Content_Types].xml':
                zout.writestr(item, new_ct)
            elif fn == 'word/numbering.xml' and new_numbering is not None and numid_map:
                zout.writestr(item, new_numbering)
            else:
                zout.writestr(item, zin.read(fn))
        for new_part, data, h, src_part in new_media:
            zout.writestr(new_part, data)
    # A6 容器成员核验
    with zipfile.ZipFile(out_path) as z2:
        out_names = z2.namelist()
    assert set(out_names) == set(names) | {p for p, _, _, _ in new_media}, '%s 容器成员异常' % vol
    return {
        '卷': vol, '源': src_code, '计数': cnt, '映射行数': len(mapping),
        '新图': [(p, h[:12], sp) for p, _, h, sp in new_media],
        'numId重映射': numid_map, 'rId重映射数': len(rid_map_all),
        '讲部标题文本': ['%s.1 知识讲解｜%s' % (s, n) for s, n, _ in sec_title_els],
        '输出': out_path,
    }, mapping

def main():
    src_cache = {}
    results, all_mapping = {}, []
    for vol in ('B', 'C', 'E', 'F', 'G', 'H'):
        src_code = TGT[vol][0]
        if src_code not in src_cache:
            entries, z = extract_entries(src_code)
            src_cache[src_code] = (entries, z)
        entries, z = src_cache[src_code]
        res, mapping = process_volume(vol, src_code, entries, z)
        results[vol] = res
        all_mapping.extend(mapping)
        print(vol, 'PASS', json.dumps(res['计数'], ensure_ascii=False),
              '新图', len(res['新图']), 'numId映射', res['numId重映射'])
    # 全局覆盖断言：B+C=47、E+F+G+H=67
    bc = results['B']['计数']['条目块'] + results['C']['计数']['条目块']
    efgh = sum(results[v]['计数']['条目块'] for v in ('E', 'F', 'G', 'H'))
    assert bc == 47 and efgh == 67, '全局覆盖断言失败: B+C=%d E~H=%d' % (bc, efgh)
    with open(r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3\T2_复制结果.json', 'w', encoding='utf-8') as f:
        json.dump({'results': results, 'mapping': all_mapping}, f, ensure_ascii=False, indent=1, default=str)
    print('全局覆盖断言 PASS：B+C=%d（=I1 47）、E+F+G+H=%d（=I2 67）' % (bc, efgh))
    print('映射表 → T2_复制结果.json（%d 行）' % len(all_mapping))

if __name__ == '__main__':
    main()
