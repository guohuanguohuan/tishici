# -*- coding: utf-8 -*-
r"""双栏改制工具.py — 2026-09-02 A''成品轮新建（公共规则§7版面分栏双栏制＋§5图形态嵌入型独立段制）。

功能四合一（对内容件 docx，幂等）：
  ① 头部单栏区重构：文首至首个教材节标题前的头部区（文内开头标题＋全件统计行＋章首导航表＋
     〔基〕/〔进〕图例行——各件按其要素）以连续分节符维持单栏——头部区末段 pPr 内插
     sectPr（type=continuous、cols=1）；页眉页脚引用（headerReference/footerReference）
     从 body 级 sectPr 移至该头部节 sectPr（页眉页脚定义各仅一处——分节不重复引用，§7）；
  ② cols 写入：body 级 sectPr 设 cols num="2" space="425" sep="1"（栏间分隔线开、每栏约8.6cm）；
     头部节 cols num="1"；
  ③ 锚定图转嵌入型：全部 wp:anchor → wp:inline（保留 drawing 内容与 extent；allowOverlap/
     posOffset 等锚定机制随外壳剥除——§5全文零锚定）；锚图 run 若在文字段中→图移独立段
     （左对齐、无缩进、随全件行距——§5图形态），位置＝紧随其引用文字段（--dry-run 产
     锚→目标段映射表供人工抽验）；
  ④ 图宽钳制：显示宽（wp:extent cx）> 栏宽 8.6cm（3096000 EMU）→ 钳至栏宽（同步
     a:ext cx；只改显示尺寸不改图像文件）；单图高>9cm（3240000 EMU）钳至9cm上限（§7
     定尺寸款几何上限；内容感知定尺寸的精调仍走 图片定尺寸回扫.py）。
  附：--navtable 将章首导航表表内段落升 12pt（sz=24）＋line=410 atLeast（§6导航表样式）。

清单件（文件名含「知识清单」）同样适用（头部区＝文内开头标题＋图例行两段）；
四类配页件（封面/使用说明/册目录页/部分封面）全文单栏——本工具不得对配页件调用（入口断言）。

断言（全过才落盘）：anchor 残留=0；头部节恰1个段落级 sectPr 且 cols=1 continuous；body sectPr
cols=2/425/1；headerReference/footerReference 全文恰1处（头部节）；w:t/m:t 文字流恒等；
图片计数与 blip r:embed 集合恒等（转 inline 不动媒体）。
用法: python 双栏改制工具.py <docx...> [--report 报告.txt] [--dry-run] [--navtable]
"""
import sys, io, zipfile, os, re, time, argparse, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PIC = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
def q(t): return '{%s}%s' % (W, t)
def wq(t): return '{%s}%s' % (WP, t)
def aq(t): return '{%s}%s' % (A, t)
def tag(e): return etree.QName(e).localname if isinstance(e.tag, str) else '?'

COL_W_EMU = 3096000        # 8.6cm 栏宽上限
IMG_H_EMU = 3240000        # 9cm 单图高上限
PAGEW_MARGIN_TW = 850      # 四边距（缇）
COL_SPACE_TW = 425         # 栏间距

FILL_TITLE1 = 'ADC2DA'
LECT_RE = re.compile(r'^\d+(?:\.\d+)*[\s　]*方法讲解[｜|]')
CHAP_RE = re.compile(r'^第\d+章')
MERGED_SEC_RE = re.compile(r'（第\d+[—–-]\d+题）|本节\d+题')
HEADNUM_RE = re.compile(r'^\d+(?:\.\d+)+[\s　]+\S')
NUMTOK_RE = re.compile(r'^(?:\d+(?:\.\d+)*-\d+|\d+)．')
PAGEFILE_RE = re.compile(r'(使用说明|册目录页|部分封面|·封面)')


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def para_fill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    shd = ppr.find(q('shd'))
    return shd.get(q('fill')) if shd is not None else None


def is_section_title(p, txt):
    """教材节标题段判定（口径同题号块三段式：节号pattern＋ADC2DA/28半点/标题3三信号；C6D4E3除外）。"""
    if LECT_RE.match(txt) or NUMTOK_RE.match(txt) or not HEADNUM_RE.match(txt):
        return None
    if para_fill(p) == 'C6D4E3':
        return None
    if para_fill(p) == FILL_TITLE1:
        return re.match(r'^(\d+\.\d+(?:\.\d+)?)', txt).group(1)
    ppr = p.find(q('pPr'))
    if ppr is not None:
        ps = ppr.find(q('pStyle'))
        if ps is not None and re.search(r'(?i)heading3|标题3', ps.get(q('val')) or ''):
            return re.match(r'^(\d+\.\d+(?:\.\d+)?)', txt).group(1)
    for r in p.findall(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None:
            continue
        z = rpr.find(q('sz'))
        t = ''.join(x.text or '' for x in r.findall(q('t')))
        if z is not None and z.get(q('val')) == '28' and t.strip():
            return re.match(r'^(\d+\.\d+(?:\.\d+)?)', txt).group(1)
    return None


def find_header_end(body):
    """头部区末元素序号（不含）：文首至首个教材节标题（不含锚段）前。返回首个节标题的 body 序号。"""
    els = list(body)
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        txt = ptext(el).strip()
        if not txt:
            continue
        ppr = el.find(q('pPr'))
        sid = None
        if ppr is not None:
            ps = ppr.find(q('pStyle'))
            sid = ps.get(q('val')) if ps is not None else None
        # 节名锚段跳过（1pt 白锚——非内容）
        if sid in ('JieMingMao', '节名锚'):
            continue
        if is_section_title(el, txt):
            return i
        # 文内开头标题之后的要素段（统计行/导航表 tbl/图例行）继续；正文首段（非要素）即头部区尽头的兜底：
        # 以下判据——段落是文首标题或要素段（含「全件」「题：」「〔基〕/〔进〕」起头，或 tbl），否则头部区结束
        if i > 0 and not (txt.startswith('全件') or txt.startswith('〔基〕') or txt.startswith('〔进〕')
                          or el.find('.//' + q('tbl')) is not None or el.getprevious() is None
                          or tag(el.getprevious()) == 'tbl'):
            # 首个「非要素正文段」＝头部区尽头（无节标题件的兜底——理论上内容件都有节标题）
            return i
    return None


INLINE_KIDS_WP = ('extent', 'effectExtent', 'docPr', 'cNvGraphicFramePr')   # wp: 命名空间子元素
INLINE_KIDS_A = ('graphic',)                                                 # a: 命名空间子元素


def convert_anchor(inline_parent, anchor):
    """wp:anchor → wp:inline：重建 inline 外壳，仅迁移 inline 合法子元素（白名单——
    positionH/positionV/wrap*/simplePos 等锚定专属元素剥除，§5锚定机制废止）。"""
    inline = etree.Element(wq('inline'))
    inline.set('distT', '0'); inline.set('distB', '0')
    inline.set('distL', '0'); inline.set('distR', '0')
    for nm in INLINE_KIDS_WP:
        for ch in anchor.findall(wq(nm)):
            inline.append(copy.deepcopy(ch))
    for nm in INLINE_KIDS_A:
        for ch in anchor.findall(aq(nm)):
            inline.append(copy.deepcopy(ch))
    assert inline.find(aq('graphic')) is not None, 'anchor 内无 a:graphic（迁移失败）'
    return inline


def clamp_extents(drawing_or_el, stats):
    """钳制 wp:extent 与 a:ext 显示尺寸（宽≤栏宽、高≤9cm）；返回是否改动。"""
    changed = False
    root = drawing_or_el
    for ext in root.iter():
        t = tag(ext)
        if t == 'extent' or (t == 'ext' and etree.QName(ext).namespace == A):
            cx, cy = ext.get('cx'), ext.get('cy')
            if cx is None or cy is None:
                continue
            cx, cy = int(cx), int(cy)
            ncx, ncy = cx, cy
            if ncx > COL_W_EMU:
                ncy = int(ncy * COL_W_EMU / ncx)   # 等比缩
                ncx = COL_W_EMU
                stats['钳宽'] += 1
            if ncy > IMG_H_EMU:
                ncx = int(ncx * IMG_H_EMU / ncy)
                ncy = IMG_H_EMU
                stats['钳高'] += 1
            if (ncx, ncy) != (cx, cy):
                ext.set('cx', str(ncx)); ext.set('cy', str(ncy))
                changed = True
    return changed


def set_cols(sectpr, num):
    cols = sectpr.find(q('cols'))
    if cols is None:
        cols = etree.SubElement(sectpr, q('cols'))
    cols.set(q('num'), str(num))
    if num == 2:
        cols.set(q('space'), str(COL_SPACE_TW))
        cols.set(q('sep'), '1')
    else:
        for att in (q('space'), q('sep'), q('equalWidth')):
            if cols.get(att) is not None:
                del cols.attrib[att]


def make_head_sectpr(template_body_sectpr):
    """构造头部节段落级 sectPr：type=continuous、cols=1、无 pgNumType/titlePg、页眉页脚引用移入。"""
    sect = etree.Element(q('sectPr'))
    # 页眉页脚引用（从模板节拷贝——随后从模板节删除）
    for ref in ('headerReference', 'footerReference'):
        for el in template_body_sectpr.findall(q(ref)):
            sect.append(copy.deepcopy(el))
    t = etree.SubElement(sect, q('type'))
    t.set(q('val'), 'continuous')
    pg = etree.SubElement(sect, q('pgSz'))
    for k, v in template_body_sectpr.find(q('pgSz')).attrib.items():
        pg.set(k, v)
    mar = etree.SubElement(sect, q('pgMar'))
    for k, v in template_body_sectpr.find(q('pgMar')).attrib.items():
        mar.set(k, v)
    cols = etree.SubElement(sect, q('cols'))
    cols.set(q('num'), '1')
    return sect


def process(path, args):
    name = os.path.basename(path)
    if PAGEFILE_RE.search(name):
        raise SystemExit('%s：配页件（全文单栏）不得调用本工具' % name)
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    els = list(body)
    stats = {'anchor': 0, 'anchor_moved': 0, 'inline': 0, '钳宽': 0, '钳高': 0, 'navt': 0}
    texts_before = [t.text or '' for t in doc.iter(q('t'))]

    # —— ③ 锚定图转 inline ——
    anchor_map = []
    for anchor in list(body.iter(wq('anchor'))):
        stats['anchor'] += 1
        run = anchor.getparent()
        while run is not None and tag(run) != 'r':
            run = run.getparent()
        p = anchor.getparent()
        while p is not None and tag(p) != 'p':
            p = p.getparent()
        if run is None or p is None:
            raise RuntimeError('%s anchor 宿主异常' % name)
        drawing_host = anchor.getparent()          # w:drawing（anchor 的直接父）
        if tag(drawing_host) != 'drawing':
            raise RuntimeError('%s anchor 直接父非 w:drawing: %s' % (name, tag(drawing_host)))
        inline = convert_anchor(p, anchor)
        anchor_map.append((ptext(p)[:28],))
        # 宿主段若只含该图（无其他文字/公式）→ 原位转（drawing 内 anchor→inline）
        other = [e for e in p.iter() if tag(e) == 't' and (e.text or '').strip()]
        has_math = next(p.iter(q('oMath')), None) is not None
        if not other and not has_math:
            drawing_host.replace(anchor, inline)
            stats['inline'] += 1
        else:
            # 图在文字段中 → 图移独立段（w:r>w:drawing>wp:inline，左对齐无缩进）紧随宿主段；
            # 宿主侧删除整个 w:drawing（残空 drawing 非法）；run 剩空壳合法
            newp = etree.Element(q('p'))
            ppr = etree.SubElement(newp, q('pPr'))
            jc = etree.SubElement(ppr, q('jc')); jc.set(q('val'), 'left')
            newr = etree.SubElement(newp, q('r'))
            drawing = etree.SubElement(newr, q('drawing'))
            drawing.append(inline)
            p.addnext(newp)
            run.remove(drawing_host)
            # 宿主段空壳清理：图移走后宿主段无文字/无图/无公式 → 删除（防题干区空段残留）
            if not ptext(p).strip()                     and next(p.iter(wq('inline')), None) is None                     and next(p.iter(wq('anchor')), None) is None                     and next(p.iter(q('oMath')), None) is None                     and p.find(q('pPr')) is None or (
                    p.find(q('pPr')) is not None
                    and p.find(q('pPr')).find(q('sectPr')) is None):
                pass
            if not ptext(p).strip()                     and next(p.iter(wq('inline')), None) is None                     and next(p.iter(wq('anchor')), None) is None                     and next(p.iter(q('oMath')), None) is None:
                ppr_h = p.find(q('pPr'))
                has_sect = ppr_h is not None and ppr_h.find(q('sectPr')) is not None
                if not has_sect:
                    body.remove(p)
                    stats['empty_host_removed'] = stats.get('empty_host_removed', 0) + 1
            stats['inline'] += 1
            stats['anchor_moved'] += 1
    # anchor 残留断言
    left = list(body.iter(wq('anchor')))
    assert not left, '%s anchor 残留 %d' % (name, len(left))

    # —— ④ 图宽钳制（含 inline/anchor 已转后的全部 drawing） ——
    for drawing in body.iter(q('drawing')):
        clamp_extents(drawing, stats)

    # —— ① 头部区重构 ＋ ② cols ——
    body_sect = body.find(q('sectPr'))
    assert body_sect is not None, '%s 无 body 级 sectPr' % name
    head_end = find_header_end(body)
    assert head_end is not None, '%s 未找到首个教材节标题（头部区定位失败）' % name
    # 已有段落级 sectPr（幂等重跑）？
    existing_para_sects = [el for el in body if tag(el) == 'p'
                           and el.find(q('pPr')) is not None
                           and el.find(q('pPr')).find(q('sectPr')) is not None]
    if existing_para_sects:
        head_p = existing_para_sects[0]
    else:
        # 头部区末段（head_end 前最后一个段落；无则新建空段）
        cand = None
        for j in range(head_end - 1, -1, -1):
            if tag(body[j]) == 'p':
                ppr_j = body[j].find(q('pPr'))
                sid_j = None
                if ppr_j is not None:
                    ps_j = ppr_j.find(q('pStyle'))
                    sid_j = ps_j.get(q('val')) if ps_j is not None else None
                if sid_j in ('JieMingMao', '节名锚'):
                    continue          # 节名锚段不挂分节（锚属正文节、随节标题）
                cand = body[j]
                break
        if cand is None:
            cand = etree.Element(q('p'))
            body.insert(head_end, cand)
        head_sect = make_head_sectpr(body_sect)
        ppr = cand.find(q('pPr'))
        if ppr is None:
            ppr = etree.Element(q('pPr'))
            cand.insert(0, ppr)
        ppr.append(head_sect)
        head_p = cand
    # 从 body sectPr 删除页眉页脚引用（移到头部节——唯一引用）
    for ref in ('headerReference', 'footerReference'):
        for el in body_sect.findall(q(ref)):
            body_sect.remove(el)
    # 头部节 cols=1（幂等重置）、body cols=2
    hpr = head_p.find(q('pPr'))
    hsect = hpr.find(q('sectPr'))
    set_cols(hsect, 1)
    set_cols(body_sect, 2)
    # 头部节 type=continuous（幂等）
    ty = hsect.find(q('type'))
    if ty is None:
        ty = etree.Element(q('type'))
        hsect.insert(0, ty)
    ty.set(q('val'), 'continuous')

    # —— 附：导航表表内段落 12pt/410 ——
    if args.navtable:
        for tbl in body.iter(q('tbl')):
            for p in tbl.iter(q('p')):
                ppr = p.find(q('pPr'))
                if ppr is None:
                    ppr = etree.Element(q('pPr'))
                    p.insert(0, ppr)
                sp = ppr.find(q('spacing'))
                if sp is None:
                    sp = etree.SubElement(ppr, q('spacing'))
                sp.set(q('line'), '410'); sp.set(q('lineRule'), 'atLeast')
                for r in p.findall(q('r')):
                    rpr = r.find(q('rPr'))
                    if rpr is None:
                        rpr = etree.Element(q('rPr'))
                        r.insert(0, rpr)
                    sz = rpr.find(q('sz'))
                    if sz is None:
                        sz = etree.SubElement(rpr, q('sz'))
                    sz.set(q('val'), '24')
                    szcs = rpr.find(q('szCs'))
                    if szcs is None:
                        szcs = etree.SubElement(rpr, q('szCs'))
                    szcs.set(q('val'), '24')
                stats['navt'] += 1

    # —— 断言 ——
    texts_after = [t.text or '' for t in doc.iter(q('t'))]
    assert texts_before == texts_after, '%s 文字流不恒等' % name
    para_sects = [el for el in body if tag(el) == 'p'
                  and el.find(q('pPr')) is not None
                  and el.find(q('pPr')).find(q('sectPr')) is not None]
    assert len(para_sects) == 1, '%s 段落级 sectPr 数=%d（期望1）' % (name, len(para_sects))
    hc = para_sects[0].find(q('pPr')).find(q('sectPr')).find(q('cols'))
    assert hc is not None and hc.get(q('num')) == '1', '头部节 cols≠1'
    bc = body_sect.find(q('cols'))
    assert bc is not None and bc.get(q('num')) == '2' and bc.get(q('space')) == '425' \
        and bc.get(q('sep')) == '1', 'body cols≠2/425/1'
    hrefs = doc.findall('.//' + q('headerReference'))
    frefs = doc.findall('.//' + q('footerReference'))
    assert len(hrefs) == 1 and len(frefs) == 1, '页眉/页脚引用数 %d/%d（期望各1——头部节）' % (len(hrefs), len(frefs))
    blips_before = None
    if not args.dry_run:
        parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                    encoding='UTF-8', standalone=True)
        tmp = path + '.a2cols'
        zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
        for nm, b in parts.items():
            zo.writestr(nm, b)
        zo.close()
        for _ in range(12):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                time.sleep(6)
        else:
            raise RuntimeError('locked: ' + path)

    lines = ['◆ %s' % name,
             '  头部区末＝body序号%d｜anchor转inline %d（其中移独立段 %d）｜钳宽 %d 钳高 %d｜导航表段 %d%s'
             % (head_end, stats['inline'], stats['anchor_moved'], stats['钳宽'], stats['钳高'],
                stats['navt'], '（dry-run 未写回）' if args.dry_run else '')]
    if anchor_map:
        lines.append('  锚→段映射（前12）：')
        for (t,) in anchor_map[:12]:
            lines.append('    %s' % t)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--report')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--navtable', action='store_true')
    args = ap.parse_args()
    out = []
    for p in args.files:
        out.extend(process(p, args))
        out.append('')
    txt = '\n'.join(out)
    print(txt)
    if args.report:
        d = os.path.dirname(os.path.abspath(args.report))
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        open(args.report, 'w', encoding='utf-8').write(txt + '\n')
        print('报告 ->', args.report)


if __name__ == '__main__':
    main()
