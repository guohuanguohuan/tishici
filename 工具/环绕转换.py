# -*- coding: utf-8 -*-
"""
环绕转换.py —— docx阅读性配图 inline→anchor＋wrapSquare（四周型环绕）转换工具
口径：A'改制轮规格书§2工具债①（口径B全参数，源自《公共规则.md》§5图像保真与守恒「锚定形态」条款）

动作：
  - wp:inline → wp:anchor＋wp:wrapSquare：图靠左文字绕右（positionH=column/posOffset=0、
    positionV=paragraph/posOffset=0）、四周间距36000EMU（distT/B/L/R）、锚定于其引用文字段。
  - 锚段归属：图现居独立图段的，锚移至引用段（引用段＝邻近段落中含「如图/图甲/图乙/图丙/图丁/
    图所示/如图所示」者，检索窗口±N段、先前后后按距离、跳过标题段）；图已居引用段的就地转换；
    转换后空图段清删（登记）。
  - 无引用词图段回退规则（本工具定义，逐图登记）：锚定图段前邻最近的非标题非空内容段；
    无可用锚段则维持inline并登记。
  - 同段多锚防重叠护栏（2026-09-01 E2补丁·缺陷修复）：同一目标锚段（引用/回退/就地）承接≥2图时
    整组维持inline独立段——wp:anchor positionV=paragraph/posOffset=0 同段多锚渲染同位叠放
    （I1实测：4图锚同段后PDF bbox完全重叠）；口径B锚定形态以可行者为限，整组维持源布局。
  - 例外三形维持inline：①显示宽＞14cm近满宽大图（维持独立段）；②同段≥2图并排（维持多inline）；
    ③显示高≤1.5cm图标级小图（行内嵌）。表格内图一律跳过不移动；oMath公式内图跳过（公式内容）。
断言（每件）：
  A1 图数恒等（w:drawing元素级，转换前后）；
  A2 media与rels零变化（word/media逐件SHA256、word/_rels/document.xml.rels与[Content_Types].xml逐字节）；
  A3 每图锚定段＝登记的引用段/回退段（执行树按元素恒等核验——源件docPr id存在大量重复，按id匹配不可行；
    引用型另断言锚段含引用词）；
  A4 锚段不落条目/题型/讲部标题段（转换锚逐图断言＋落盘后全文所有wp:anchor宿主段重开复断言）；
  A5 空图段删除数＝登记数（段落计数恒等）。
登记：逐图清单（图序/原形态尺寸/处置或例外类别/锚定段/定位依据/断言结果），--report落盘md。
参数：单件.docx路径或目录（批量＝目录下*.docx非递归、跳过~$临时件）；幂等（已是anchor的跳过）。

用法：
  python 环绕转换.py 单件.docx [--report 报告.md] [--window 3] [--dry-run]
  python 环绕转换.py 目录       [--report 报告.md] [--window 3] [--dry-run]
退出码：0＝全过；2＝断言失败；1＝运行错误。
"""
import argparse
import copy
import hashlib
import os
import re
import sys
import zipfile

from lxml import etree

# ---------- 常量（口径B全参数） ----------
EMU_PER_CM = 360000
LARGE_W_CM = 14.0     # 例外①：显示宽＞14cm（约满宽）
ICON_H_CM = 1.5       # 例外③：显示高≤1.5cm
DIST_EMU = 36000      # 四周间距（≈0.1cm）
WRAP_TEXT = 'bothSides'  # wrapSquare环绕侧（Word真值：wrapText属性，四周型＝bothSides）

WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WPNS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
MNS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'


def W(t):
    return '{%s}%s' % (WNS, t)


def WP(t):
    return '{%s}%s' % (WPNS, t)


def M(t):
    return '{%s}%s' % (MNS, t)


REF_RE = re.compile(r'如图|图[甲乙丙丁]|图所示')
TITLE_FILLS = {'ADC2DA', 'C6D4E3'}   # 章/节、讲部/题型标题整行底纹
ENTRY_SHD_FILL = 'C9C9C9'            # 条目号/题号块run级底纹（条目号非加粗＝条目题名行）


# ---------- 基础函数 ----------
def para_text(p):
    """段落全文本（w:t＋m:t，文档序）。"""
    return ''.join(t.text or '' for t in p.iter() if t.tag in (W('t'), M('t')))


def para_is_title(p):
    """条目/题型/讲部/章/节标题段判定：
    ①pPr整行底纹ADC2DA/C6D4E3；②Heading/标题样式；③条目题名行（条目号run挂C9C9C9、
    非加粗、以数字起——题号块加粗故不误判，块标签【×】以【起故不误判）。"""
    pPr = p.find(W('pPr'))
    if pPr is not None:
        shd = pPr.find(W('shd'))
        if shd is not None and shd.get(W('fill')) in TITLE_FILLS:
            return True
        ps = pPr.find(W('pStyle'))
        if ps is not None:
            v = ps.get(W('val'), '') or ''
            if v.startswith('Heading') or v.startswith('标题'):
                return True
    for r in p.findall(W('r')):
        txt = ''.join(t.text or '' for t in r.findall(W('t')))
        if txt.strip():
            rPr = r.find(W('rPr'))
            if rPr is not None:
                shd = rPr.find(W('shd'))
                b = rPr.find(W('b'))
                if shd is not None and shd.get(W('fill')) == ENTRY_SHD_FILL and b is None:
                    if txt[0].isdigit():
                        return True
            break
    return False


def has_ancestor(el, tag):
    a = el.getparent()
    while a is not None:
        if a.tag == tag:
            return True
        a = a.getparent()
    return False


def nearest_ancestor(el, tag):
    a = el.getparent()
    while a is not None:
        if a.tag == tag:
            return a
        a = a.getparent()
    return None


def para_removable(p):
    """空图段可删判定：段落内除pPr外仅允许「纯空白run」（rPr＋仅空白w:t、无其他任何元素）；
    任何非空白文本/公式/图形/域/书签/分节属性残留均保留（登记）。
    纯空白run属零内容残留，随段清删并在登记basis注明。"""
    pPr = p.find(W('pPr'))
    if pPr is not None and pPr.find(W('sectPr')) is not None:
        return False
    for child in p:
        if child.tag == W('pPr'):
            continue
        if child.tag == W('r'):
            for rc in child:
                if rc.tag == W('rPr'):
                    continue
                if rc.tag == W('t'):
                    if (rc.text or '').strip():
                        return False
                    continue
                return False  # drawing/tab/br/fldChar/pict等任何其他元素
            continue  # 该run仅含rPr与空白w:t
        return False  # 非run子元素（书签/公式/其他）
    return True


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def build_anchor(inline, rel_height):
    """由wp:inline构造wp:anchor（保extent/docPr/cNvGraphicFramePr/a:graphic原样，
    插入simplePos/positionH/positionV/effectExtent/wrapSquare，属性挂四周间距36000EMU）。
    wrapSquare必须用wrapText属性（Word真值实测：wrapNum非schema属性、Word拒开且不可修复）。"""
    a = copy.deepcopy(inline)
    a.tag = WP('anchor')
    for k in list(a.attrib):
        del a.attrib[k]
    a.set('distT', str(DIST_EMU))
    a.set('distB', str(DIST_EMU))
    a.set('distL', str(DIST_EMU))
    a.set('distR', str(DIST_EMU))
    a.set('simplePos', '0')
    a.set('relativeHeight', str(rel_height))
    a.set('behindDoc', '0')
    a.set('locked', '0')
    a.set('layoutInCell', '1')
    a.set('allowOverlap', '0')  # 2026-09-01 SW补丁：置0防跨段锚定浮动图叠放（E1返工§6.2定案；§5锚定形态「结构上不可能压字」）
    sp = etree.Element(WP('simplePos'))
    sp.set('x', '0')
    sp.set('y', '0')
    ph = etree.Element(WP('positionH'))
    ph.set('relativeFrom', 'column')
    etree.SubElement(ph, WP('posOffset')).text = '0'
    pv = etree.Element(WP('positionV'))
    pv.set('relativeFrom', 'paragraph')
    etree.SubElement(pv, WP('posOffset')).text = '0'
    a.insert(0, sp)
    a.insert(1, ph)
    a.insert(2, pv)
    if a.find(WP('effectExtent')) is None:
        ee = etree.Element(WP('effectExtent'))
        for k in ('l', 't', 'r', 'b'):
            ee.set(k, '0')
        ext = a.find(WP('extent'))
        ext.addnext(ee)
    ws = etree.Element(WP('wrapSquare'))
    ws.set('wrapText', WRAP_TEXT)
    docpr = a.find(WP('docPr'))
    if docpr is not None:
        docpr.addprevious(ws)
    else:
        a.append(ws)
    return a


# ---------- 单件处理 ----------
def process_file(path, window, dry_run):
    """返回 (登记行列表[dict], 汇总dict, 断言失败列表)。"""
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        members = [(i.filename, z.read(i.filename)) for i in infos]
    blob = dict(members)
    if 'word/document.xml' not in blob:
        raise RuntimeError('缺少word/document.xml：%s' % path)
    xml_bytes = blob['word/document.xml']
    root = etree.fromstring(xml_bytes)
    body = root.find(W('body'))
    paras = [el for el in body if el.tag == W('p')]
    para_idx = {id(p): i for i, p in enumerate(paras)}
    drawings = [d for d in body.iter(W('drawing'))]  # 持活列表（lxml代理GC防护）

    # ---- 前态记录（A1/A2基线） ----
    pre_drawing = len(drawings)
    pre_anchor = sum(1 for d in drawings if len(d) and d[0].tag == WP('anchor'))
    pre_para = len(paras)
    pre_media = {n: sha256(b) for n, b in members if n.startswith('word/media/')}
    pre_rels = blob.get('word/_rels/document.xml.rels')
    pre_ct = blob.get('[Content_Types].xml')

    # ---- 每段图数统计（同段并排判定） ----
    para_img_count = {}
    for dr in drawings:
        p = nearest_ancestor(dr, W('p'))
        if p is not None:
            para_img_count[id(p)] = para_img_count.get(id(p), 0) + 1

    # ---- 决策 ----
    rows = []
    conversions = []   # 待执行转换：dict
    skipped_deleted = 0
    rh = 1000
    for seq, dr in enumerate(drawings, 1):
        ch = dr[0] if len(dr) else None
        if ch is not None and ch.tag == WP('inline'):
            form = 'inline'
        elif ch is not None and ch.tag == WP('anchor'):
            form = 'anchor'
        else:
            form = 'other'
        p = nearest_ancestor(dr, W('p'))
        row = {
            'seq': seq, 'form': form, 'wcm': None, 'hcm': None,
            'para_idx': para_idx.get(id(p)) if p is not None else None,
            'action': '', 'target_idx': None, 'target_text': '', 'basis': '',
            'assert_note': '',
        }
        if form == 'inline':
            ext = ch.find(WP('extent'))
            if ext is not None:
                row['wcm'] = round(int(ext.get('cx')) / EMU_PER_CM, 2)
                row['hcm'] = round(int(ext.get('cy')) / EMU_PER_CM, 2)
        ptxt = para_text(p).strip() if p is not None else ''

        if p is None:
            row['action'] = '跳过（无宿主段落）'
            rows.append(row)
            continue
        if has_ancestor(dr, W('tbl')):
            row['action'] = '例外·表格内图（跳过不移动）'
            rows.append(row)
            continue
        if has_ancestor(dr, M('oMath')):
            row['action'] = '例外·公式内图（跳过）'
            rows.append(row)
            continue
        if form == 'anchor':
            row['action'] = '跳过（已是anchor，幂等）'
            rows.append(row)
            continue
        if form != 'inline':
            row['action'] = '跳过（非inline/anchor形态）'
            rows.append(row)
            continue

        wcm, hcm = row['wcm'] or 0.0, row['hcm'] or 0.0
        if wcm > LARGE_W_CM:
            row['action'] = '例外①大图＞14cm（维持独立段inline）'
            rows.append(row)
            continue
        if para_img_count.get(id(p), 0) >= 2:
            row['action'] = '例外②同段多图并排（维持多inline）'
            rows.append(row)
            continue
        if hcm <= ICON_H_CM:
            row['action'] = '例外③图标级≤1.5cm（行内嵌维持）'
            rows.append(row)
            continue

        # ---- 阅读性配图：单图、非图标、非大图 ----
        i = para_idx[id(p)]
        if ptxt:
            if REF_RE.search(ptxt):
                cv = dict(row)
                cv.update(kind='inplace', target_p=p, target_idx=i,
                          target_text=ptxt,
                          basis='图居引用段（段文含引用词），就地转换')
                conversions.append(cv)
            else:
                row['action'] = '维持inline（段内嵌图但段文无引用词，无口径B适用锚段）'
                rows.append(row)
            continue

        # 独立图段：检索引用段（窗口±N、按距离、先前后后、跳过标题段与空段）
        cand = None
        for dist in range(1, window + 1):
            for j in (i - dist, i + dist):
                if 0 <= j < len(paras):
                    tp = paras[j]
                    tt = para_text(tp).strip()
                    if tt and REF_RE.search(tt) and not para_is_title(tp):
                        cand = (j, tp, tt, dist, '前' if j < i else '后')
                        break
            if cand:
                break
        if cand:
            j, tp, tt, dist, direction = cand
            cv = dict(row)
            cv.update(kind='ref', target_p=tp, target_idx=j, target_text=tt,
                      basis=f'引用段检索±{window}段：第{j}段（图段{direction}方距{dist}）含引用词、非标题段')
            conversions.append(cv)
            continue

        # 回退：前邻最近非标题非空内容段 → 后邻 → 维持inline
        fb = None
        for j in range(i - 1, -1, -1):
            tp = paras[j]
            tt = para_text(tp).strip()
            if tt and not para_is_title(tp):
                fb = (j, tp, tt)
                break
        if fb is None:
            for j in range(i + 1, len(paras)):
                tp = paras[j]
                tt = para_text(tp).strip()
                if tt and not para_is_title(tp):
                    fb = (j, tp, tt)
                    break
        if fb is None:
            row['action'] = '维持inline（±%d段无引用词且无可用回退锚段）' % window
            rows.append(row)
            continue
        j, tp, tt = fb
        cv = dict(row)
        cv.update(kind='fallback', target_p=tp, target_idx=j, target_text=tt,
                  basis=f'±{window}段无引用词→回退锚定前邻内容段（第{j}段，图属其解题/讲解内容；回退规则登记待主会话裁决）' if j < i
                  else f'±{window}段无引用词且前邻无内容段→回退锚定后邻内容段（第{j}段；回退规则登记待主会话裁决）')
        conversions.append(cv)

    # ---- 同段多锚防重叠护栏（2026-09-01 E2补丁·缺陷修复）----
    # 同一目标锚段承接≥2图→整组维持inline（posOffset同位渲染叠放，见docstring）；逐图登记。
    _tgt_groups = {}
    for _cv in conversions:
        _tgt_groups.setdefault(id(_cv['target_p']), []).append(_cv)
    _drop_keys = {k for k, v in _tgt_groups.items() if len(v) >= 2}
    if _drop_keys:
        _kept = []
        for _cv in conversions:
            if id(_cv['target_p']) in _drop_keys:
                _row = dict(_cv)
                _row['action'] = '护栏·同段多锚整组维持inline（%s目标段承接%d图，同位posOffset必重叠）' % (
                    {'ref': '引用', 'fallback': '回退', 'inplace': '就地'}[_cv['kind']],
                    len(_tgt_groups[id(_cv['target_p'])]))
                _row['assert_note'] = '—（未转换）'
                rows.append(_row)
            else:
                _kept.append(_cv)
        conversions = _kept

    # ---- 执行转换 ----
    deleted_paras = []
    placed = []  # (cv, new_run, host_p) —— 执行树恒等对象
    if not dry_run:
        for cv in conversions:
            dr = drawings[cv['seq'] - 1]
            inline = dr[0]
            rh += 1
            anchor = build_anchor(inline, rh)
            run = nearest_ancestor(dr, W('r'))
            new_run = copy.deepcopy(run)
            dr2 = next(e for e in new_run.iter(W('drawing')))
            dr2.remove(dr2[0])
            dr2.append(anchor)
            cv['target_p'].append(new_run)
            placed.append((cv, new_run, cv['target_p']))
            src_p = nearest_ancestor(run, W('p'))
            run.getparent().remove(run)
            if src_p is not None and src_p is not cv['target_p'] and para_removable(src_p):
                deleted_paras.append(para_idx.get(id(src_p)))
                if src_p.findall(W('r')):
                    cv['basis'] += '；空图段清删（含纯空白run）'
                src_p.getparent().remove(src_p)
            elif src_p is not None and src_p is not cv['target_p']:
                cv['basis'] += '；空图段残留非run元素未删（登记）'
        # A3/A4 逐图核验（执行树元素恒等；序列化对结构无损）
        for cv, new_run, hp in placed:
            if nearest_ancestor(new_run, W('p')) is not hp:
                cv['assert_note'] = '断言失败：锚run不在登记锚定段'
                cv.setdefault('fails', []).append('A3失败：图%d锚run未落登记段' % cv['seq'])
                continue
            ht = para_text(hp).strip()
            if ht != cv['target_text']:
                cv['assert_note'] = '断言失败：锚定段文本不符'
                cv.setdefault('fails', []).append('A3失败：图%d锚定段文本不符（应为第%d段）' % (cv['seq'], cv['target_idx']))
            elif cv['kind'] == 'ref' and not REF_RE.search(ht):
                cv['assert_note'] = '断言失败：引用型锚段无引用词'
                cv.setdefault('fails', []).append('A3失败：图%d引用型锚段无引用词' % cv['seq'])
            elif para_is_title(hp):
                cv['assert_note'] = '断言失败：锚段落标题段'
                cv.setdefault('fails', []).append('A4失败：图%d锚段落标题段' % cv['seq'])
            else:
                cv['assert_note'] = '断言通过'
        out_xml = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.tmp'
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
            for name, data in members:
                if name == 'word/document.xml':
                    zo.writestr(name, out_xml)
                else:
                    zo.writestr(name, data)
        os.replace(tmp, path)

    for cv in conversions:
        cv['action'] = '转换→anchor＋wrapSquare（%s）' % {
            'ref': '锚移至引用段', 'fallback': '锚移至回退内容段', 'inplace': '就地转换'}[cv['kind']]
        rows.append(cv)
    rows.sort(key=lambda r: r['seq'])

    # ---- 断言（落盘后文件重开核验A1/A2/A5＋全局A4；dry_run对内存树、免A3/A5） ----
    fails = []
    if dry_run:
        post_root, post_blob = root, blob
    else:
        with zipfile.ZipFile(path) as z:
            post_blob = {n.filename: z.read(n.filename) for n in z.infolist()}
        post_root = etree.fromstring(post_blob['word/document.xml'])
    post_body = post_root.find(W('body'))
    post_drawings = [d for d in post_body.iter(W('drawing'))]
    post_paras = [el for el in post_body if el.tag == W('p')]

    # A1 图数恒等
    if len(post_drawings) != pre_drawing:
        fails.append('A1图数恒等失败：前%d≠后%d' % (pre_drawing, len(post_drawings)))
    # A2 media与rels零变化
    post_media = {n: sha256(b) for n, b in post_blob.items() if n.startswith('word/media/')}
    if post_media != pre_media:
        fails.append('A2 media变化：%s' % (set(post_media.items()) ^ set(pre_media.items()),))
    if post_blob.get('word/_rels/document.xml.rels') != pre_rels:
        fails.append('A2 rels变化')
    if post_blob.get('[Content_Types].xml') != pre_ct:
        fails.append('A2 [Content_Types].xml变化')
    # 执行期逐图A3/A4结论归集（dry_run无转换、无此组断言）
    if dry_run:
        for cv in conversions:
            cv['assert_note'] = 'dry-run仅判定（A3/A5未验）'
    else:
        for cv in conversions:
            fails.extend(cv.get('fails', []))
    # A4 全局复断言：落盘后全文所有wp:anchor宿主段均非标题段
    n_anchor_post = 0
    for dr in post_drawings:
        ch = dr[0] if len(dr) else None
        if ch is not None and ch.tag == WP('anchor'):
            n_anchor_post += 1
            hp = nearest_ancestor(dr, W('p'))
            if hp is not None and para_is_title(hp):
                fails.append('A4失败：anchor宿主段为标题段（段文「%s…」）' % para_text(hp).strip()[:20])
    if not dry_run and n_anchor_post != pre_anchor + len(conversions):
        fails.append('A3失败：落盘后anchor数%d≠前%d＋转换%d' % (n_anchor_post, pre_anchor, len(conversions)))
    # A5 段落计数恒等（仅实跑；dry_run无删除）
    if not dry_run:
        expect = pre_para - len(deleted_paras)
        if len(post_paras) != expect:
            fails.append('A5失败：段落数前%d−删除%d≠后%d' % (pre_para, len(deleted_paras), len(post_paras)))

    # ---- 汇总 ----
    def count_act(sub):
        return sum(1 for r in rows if sub in r['action'])
    summary = {
        'file': os.path.basename(path),
        'total': len(rows),
        'converted': len(conversions),
        'conv_ref': sum(1 for c in conversions if c['kind'] == 'ref'),
        'conv_fb': sum(1 for c in conversions if c['kind'] == 'fallback'),
        'conv_inplace': sum(1 for c in conversions if c['kind'] == 'inplace'),
        'exc_large': count_act('例外①'),
        'exc_multi': count_act('例外②'),
        'exc_icon': count_act('例外③'),
        'skip_table': count_act('表格内图'),
        'skip_math': count_act('公式内图'),
        'skip_anchor': count_act('已是anchor'),
        'keep_inline_noref': count_act('无引用词，无口径B适用锚段') + count_act('无可用回退锚段'),
        'guard_multi': count_act('护栏·同段多锚整组维持inline'),
        'deleted_paras': deleted_paras,
        'pre_drawing': pre_drawing, 'post_drawing': len(post_drawings),
        'pre_para': pre_para, 'post_para': len(post_paras),
        'fails': fails,
    }
    return rows, summary, fails


# ---------- 报告 ----------
def write_report(report_path, per_file, window, dry_run):
    lines = ['# 环绕转换登记报告（工具/环绕转换.py）', '']
    lines.append('- 生成参数：窗口±%d段；%s' % (window, 'dry-run（未落盘）' if dry_run else '实跑（已落盘）'))
    lines.append('- 口径：A' + "'改制轮规格书§2工具债①（口径B全参数：wrapSquare、图左文右、间距36000EMU、锚定引用段）")
    lines.append('')
    for rows, s in per_file:
        lines.append('## %s' % s['file'])
        lines.append('')
        lines.append('- 图总数（w:drawing元素级）：%d（前）→ %d（后）｜段落数：%d→%d（删除空图段%d个）'
                     % (s['pre_drawing'], s['post_drawing'], s['pre_para'], s['post_para'], len(s['deleted_paras'])))
        lines.append('- 转换%d（引用段锚移%d｜回退锚移%d｜就地%d）｜例外①大图%d｜例外②多图%d｜例外③图标%d｜表格内跳过%d｜公式内跳过%d｜已是anchor跳过%d｜无引用维持inline%d｜护栏同段多锚维持inline%d'
                     % (s['converted'], s['conv_ref'], s['conv_fb'], s['conv_inplace'],
                        s['exc_large'], s['exc_multi'], s['exc_icon'], s['skip_table'],
                        s['skip_math'], s['skip_anchor'], s['keep_inline_noref'], s['guard_multi']))
        lines.append('- 断言：%s' % ('全过（A1图数恒等/A2media与rels零变化/A3锚段归属/A4锚段非标题/A5段落恒等）' if not s['fails'] else '失败：' + '；'.join(s['fails'])))
        if s['deleted_paras']:
            lines.append('- 删除空图段（原段落序）：%s' % s['deleted_paras'])
        lines.append('')
        lines.append('| 图序 | 原段落 | 原形态尺寸(cm) | 处置 | 锚定段 | 定位依据 | 断言 |')
        lines.append('|---|---|---|---|---|---|---|')
        for r in rows:
            size = '%s×%s' % (r['wcm'], r['hcm']) if r['wcm'] is not None else '—'
            tgt = ('第%s段「%s…」' % (r['target_idx'], r['target_text'][:24])) if r.get('target_idx') is not None else '—'
            lines.append('| %s | %s | %s %s | %s | %s | %s | %s |' % (
                r['seq'], r['para_idx'], r['form'], size, r['action'], tgt,
                r['basis'] or '—', r.get('assert_note') or '—'))
        lines.append('')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    ap = argparse.ArgumentParser(description='docx阅读性配图inline→anchor＋wrapSquare环绕转换（口径B）')
    ap.add_argument('target', help='单件.docx路径或目录（批量＝目录下*.docx非递归）')
    ap.add_argument('--report', default=None, help='登记清单落盘md路径')
    ap.add_argument('--window', type=int, default=3, help='引用段检索窗口±N段（默认3）')
    ap.add_argument('--dry-run', action='store_true', help='只判定不落盘（断言对内存树）')
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    if os.path.isdir(args.target):
        files = sorted(os.path.join(args.target, n) for n in os.listdir(args.target)
                       if n.lower().endswith('.docx') and not n.startswith('~$'))
    elif os.path.isfile(args.target):
        files = [args.target]
    else:
        print('路径不存在：%s' % args.target)
        return 1
    if not files:
        print('无待处理docx。')
        return 1

    per_file, all_fail, err = [], [], []
    for fp in files:
        try:
            rows, s, fails = process_file(fp, args.window, args.dry_run)
            per_file.append((rows, s))
            all_fail.extend('%s: %s' % (s['file'], f) for f in fails)
            print('[%s] 图%d→%d｜转换%d（引用%d/回退%d/就地%d）｜例外①%d②%d③%d｜表内%d公式内%d已anchor%d维持inline%d｜护栏多锚%d｜删空图段%d｜断言%s'
                  % (s['file'], s['pre_drawing'], s['post_drawing'], s['converted'],
                     s['conv_ref'], s['conv_fb'], s['conv_inplace'], s['exc_large'],
                     s['exc_multi'], s['exc_icon'], s['skip_table'], s['skip_math'],
                     s['skip_anchor'], s['keep_inline_noref'], s['guard_multi'],
                     len(s['deleted_paras']),
                     '全过' if not fails else '失败'))
            for f in fails:
                print('  !! ' + f)
        except Exception as e:
            err.append('%s: %r' % (fp, e))
            print('[%s] 运行错误：%r' % (fp, e))

    if args.report:
        write_report(args.report, per_file, args.window, args.dry_run)
        print('报告落盘：%s' % args.report)
    if err:
        return 1
    if all_fail:
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
