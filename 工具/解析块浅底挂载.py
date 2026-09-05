# -*- coding: utf-8 -*-
"""题干底纹挂载.py — 2026-09-02 A''成品轮改造（原「解析块浅底挂载.py」A'口径废止；公共规则§7题干底纹款·第七类底纹）。
带题件（讲练件/衔接件/实验卷/真题卷等）题干段铺段落级 w:shd val="clear" color="auto" fill="E0E0E0"
（≈12%灰、PDF灰度≈224），挂 pPr（段落级），与 run 级标记（题号块/块标签芯片/答案值 C7C7C7）分层并存。
  本工具一遍完成三件事（A''换轴）：
    ①卸载 A' 遗留解析浅底 F2F2F2（全部段级——含解析块/通式句/续段；卸后断言残留=0）；
    ②题干底纹挂载 E0E0E0——适用段（§7题干底纹款）＝每题题号块段起至首个解析标签行
      （【答案】【知识点】【分析】【详解】【点睛】【编注】【大招指引】【题后反思】【温馨提醒】任一
      起段）之前的全部段落：题干文字、选项、小问设问；纯图独立段（有 drawing/pict 且无文字）豁免；
    ③段分类计数（题干段/解析白底段/图段豁免/通式句白底）供七类计数⑦恒等对账。
  白底维持（不铺）：解析块全部段落、题型通式句（【编注】起段）、讲部讲解正文、讲部/清单条目、
    标题、导航表；表格内段落不铺（登记待核）。
  知识清单件（文件名含「知识清单」）整件跳过（清单无题干，全件白底）——文件不触碰、不重写。
  恒等式＝题干底纹段落数＝题干段清点数（输出分类计数＋逐题块明细供人工对照）。
  幂等：已 E0E0E0 段落不重复挂载；零破坏断言＝run级 shd 各 fill 计数前后恒等＋w:t/m:t 文字流前后恒等
    ＋标题段（段级 ADC2DA/C6D4E3）零触碰。
  块边界识别参照 工具/extract_structure.py 解析逻辑（题号块签名＋块内含【答案】），题号形态兼容全局「N．」
    与层级制「前缀-序号．」（A'/A''前后两态可用）。
用法: python 解析块浅底挂载.py <docx...> [--report 报告.txt] [--dry-run] [--detail N]
  --dry-run 只清点不改写；--detail N 逐题块明细最多列 N 条（默认 40，0＝不列）。"""
import sys, io, zipfile, os, re, time, argparse
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname if isinstance(e.tag, str) else '?'

FILL = 'E0E0E0'          # A''题干底纹（≈224）
FILL_LEGACY = 'F2F2F2'   # A'解析浅底（卸载对象）
FILL_TITLE1 = 'ADC2DA'
FILL_TITLE2 = 'C6D4E3'
LABELS = ('【答案】', '【知识点】', '【分析】', '【详解】', '【点睛】', '【编注】',
          '【大招指引】', '【题后反思】', '【温馨提醒】')
# 题号块签名（全局 N．／层级制 节号-序号．；括注三段式/衔接两段式/退化档位——口径同六类底纹计数）
QBLOCK_HEAD_RE = re.compile(
    r'^(?:\d+(?:\.\d+)*-\d+|\d+)．（(?:(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%))?·卡壳看答案'
    r'|衔接必会·卡壳看答案|(?:简单|中档|难))')
QNUM_ANY_RE = re.compile(r'^(?:\d+(?:\.\d+)*-\d+|\d+)．')
LECTURE_RE = re.compile(r'^\d+(?:\.\d+)*[\s　]*方法讲解[｜|]')
CHAP_RE = re.compile(r'^第\d+章')
MERGED_SEC_RE = re.compile(r'（第\d+[—–-]\d+题）')
HEADNUM_RE = re.compile(r'^\d+(?:\.\d+)+[\s　]+\S')

# pPr 内 shd 合法插入位：其后元素集合（CT_PPr 序：… pBdr, shd, tabs, …, spacing, ind, …, jc, …, rPr, sectPr）
AFTER_SHD = {'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct',
             'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind',
             'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection',
             'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr',
             'pPrChange'}


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def para_fill(p):
    if p is None or p.tag != q('p'):
        return None
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    shd = ppr.find(q('shd'))
    return shd.get(q('fill')) if shd is not None else None


def set_para_shd(p, fill=FILL):
    """段落 pPr 挂 shd（已有则原位改属性）。返回 (是否新挂, 原fill)。"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    shd = ppr.find(q('shd'))
    if shd is not None and shd.get(q('fill')) == fill:
        return False, fill
    old = shd.get(q('fill')) if shd is not None else None
    if shd is None:
        shd = etree.Element(q('shd'))
        pos = len(list(ppr))
        for k, c in enumerate(list(ppr)):
            if tag(c) in AFTER_SHD:
                pos = k
                break
        ppr.insert(pos, shd)
    shd.set(q('val'), 'clear')
    shd.set(q('color'), 'auto')
    shd.set(q('fill'), fill)
    return True, old


def heading_kind(el, text, first_nonempty):
    """标题分型：pPr 段级底纹（ADC2DA=章/节、C6D4E3=讲部/题型）优先，文本签名兜底。
    返回 None 或 'chapter'/'section'/'lecture'/'group'。"""
    if el is not None and el.tag == q('p'):
        f = para_fill(el)
        if f == FILL_TITLE1:
            return 'chapter' if (CHAP_RE.match(text) or el is first_nonempty) else 'section'
        if f == FILL_TITLE2:
            return 'lecture' if LECTURE_RE.match(text) else 'group'
    if el is None or el.tag != q('p') or not text.strip():
        return None
    if el is first_nonempty:
        return 'chapter'
    if LECTURE_RE.match(text):
        return 'lecture'
    if CHAP_RE.match(text):
        return 'chapter'
    if MERGED_SEC_RE.search(text) and re.match(r'^\d+(?:\.\d+)*[\s　]', text):
        return 'section'
    if HEADNUM_RE.match(text):
        return 'group' if '：' in text[:24] else 'section'
    return None


def lead_label(text):
    t = text.lstrip()
    for lb in LABELS:
        if t.startswith(lb):
            return lb
    return None


def scan_blocks(els, ptexts):
    """题块清点（参照 extract_structure）：返回 [(start, end_exclusive)]。
    定签名＝题号＋括注（QBLOCK_HEAD_RE）；裸题号候选＝块内（至下一题号/标题/表格前）含【答案】标签行。
    定签名题块中途的表格透明穿过（候选块在表格处截止，防条目区经导航表渗入题区）。"""
    n = len(els)
    blocks = []
    i = 0
    while i < n:
        el = els[i]
        if el.tag != q('p'):
            i += 1
            continue
        t = ptexts[i]
        definite = QBLOCK_HEAD_RE.match(t)
        candidate = (not definite) and QNUM_ANY_RE.match(t)
        if definite:
            j = i + 1
            while j < n:
                ej = els[j]
                if ej.tag == q('tbl'):
                    j += 1
                    continue
                if ej.tag != q('p'):
                    break
                if QBLOCK_HEAD_RE.match(ptexts[j]) or heading_kind(ej, ptexts[j], None):
                    break
                j += 1
            blocks.append((i, j))
            i = j
        elif candidate:
            j = i + 1
            while j < n and els[j].tag == q('p') and not QNUM_ANY_RE.match(ptexts[j]) \
                    and heading_kind(els[j], ptexts[j], None) is None:
                j += 1
            has_ans = any(lead_label(ptexts[k]) == '【答案】'
                          for k in range(i, j) if els[k].tag == q('p'))
            if has_ans:
                blocks.append((i, j))
                i = j
            else:
                i += 1
        else:
            i += 1
    return blocks


def snapshot_doc(doc):
    """零破坏断言基线：run级 shd fill 计数（w:r 的 rPr，含 OMML m:r/ctrlPr 的 w:rPr）＋全文文字流。"""
    rc = Counter()
    for rpr in doc.iter(q('rPr')):
        par = rpr.getparent()
        shd = rpr.find(q('shd'))
        if shd is not None and par is not None and tag(par) == 'r':
            rc[shd.get(q('fill'))] += 1
    texts = [t.text or '' for t in doc.iter(q('t'))]
    texts += [t.text or '' for t in doc.iter('{%s}t' % M)]
    return rc, ''.join(texts)


def clear_para_shd(p, fill):
    """卸载段级 shd（匹配 fill 才删）。返回 是否删除。"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    shd = ppr.find(q('shd'))
    if shd is not None and shd.get(q('fill')) == fill:
        ppr.remove(shd)
        return True
    return False


def is_pure_image_para(el, text):
    """纯图独立段判定：段内有 drawing/pict 且无文字（§7图段豁免款）。"""
    if text.strip():
        return False
    return next(el.iter(q('drawing')), None) is not None \
        or next(el.iter(q('pict')), None) is not None


def process(path, args):
    basename = os.path.basename(path)
    z = zipfile.ZipFile(path)
    parts = {nm: z.read(nm) for nm in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    els = list(body)
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    first_ne = None
    for i, el in enumerate(els):
        if el.tag == q('p') and ptexts[i].strip():
            first_ne = el
            break

    def hkind(i):
        return heading_kind(els[i], ptexts[i], first_ne)

    blocks = scan_blocks(els, ptexts)
    in_block = {k: bi for bi, (s, e) in enumerate(blocks) for k in range(s, e)}

    # —— 题干段清点（A''：题号块段起至首个解析标签行前；图段豁免） ——
    scope = {}      # idx -> (类别, 题块序号)
    cat = Counter()
    detail = []     # (题块序号, 题号文本, 题干段数, 尾段类别)
    ana_white = 0   # 解析白底段计数（登记）
    skip_labels_out = 0
    tbl_mid = 0
    img_exempt = 0
    for bi, (s, e) in enumerate(blocks):
        n_blk = 0
        tail = None
        for k in range(s, e):
            el = els[k]
            if el.tag != q('p'):
                if k > s:
                    tbl_mid += 1
                continue
            t = ptexts[k]
            lb = lead_label(t)
            if lb:
                tail = lb
                break                      # 首个解析标签行起＝白底维持面
            if is_pure_image_para(el, t):
                img_exempt += 1
                scope[k] = ('图段豁免', bi)
                continue
            scope[k] = ('题干', bi)
            cat['题干段'] += 1
            n_blk += 1
        # 解析白底段计数（题块内其余段）
        for k in range(s, e):
            if k in scope:
                continue
            if els[k].tag == q('p') and ptexts[k].strip():
                ana_white += 1
        if tail is not None or n_blk:
            detail.append((bi, ptexts[s][:24], n_blk, tail or '无标签(纯题干)'))
    # 题型通式句（题块外、【×】起段、最近标题＝题型组）＝白底维持（A'浅底曾误铺——本工具卸载步骤清除）
    cur_head = None
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        hk = hkind(i)
        if hk:
            cur_head = hk
            continue
        if i in in_block:
            continue
        if lead_label(ptexts[i]):
            if cur_head == 'group':
                cat['通式句白底'] += 1
            else:
                skip_labels_out += 1
    predicted = cat['题干段']

    # —— 改写（两遍：①卸F2F2F2全部段级 ②挂E0E0E0到题干段） ——
    newly = already = replaced_auto = 0
    unloaded = 0
    if not args.dry_run:
        for el in els:
            if el.tag == q('p') and clear_para_shd(el, FILL_LEGACY):
                unloaded += 1
    for i in scope:
        if scope[i][0] != '题干':
            continue
        f = para_fill(els[i])
        if f == FILL:
            already += 1
            continue
        if not args.dry_run:
            set_para_shd(els[i])
        newly += 1
        if f == 'auto':
            replaced_auto += 1

    # —— 恒等式与断言 ——
    total_new = sum(1 for el in els if para_fill(el) == FILL)
    total_legacy = sum(1 for el in els if para_fill(el) == FILL_LEGACY)
    stray = [i for i, el in enumerate(els)
             if para_fill(el) == FILL and scope.get(i, ('',))[0] != '题干']
    hit_title = sum(1 for i in scope if para_fill(els[i]) in (FILL_TITLE1, FILL_TITLE2))
    lines = ['◆ %s' % basename]
    lines.append('  题块 %d｜题干段清点 %d（新挂 %d＋已有 %d；fill=auto 原位改写 %d）｜图段豁免 %d｜解析白底段 %d%s'
                 % (len(blocks), predicted, newly, already, replaced_auto, img_exempt, ana_white,
                    '，dry-run 未写回' if args.dry_run else ''))
    lines.append('  分类：%s' % '；'.join('%s%d' % kv for kv in sorted(cat.items()) if kv[1]))
    if args.dry_run:
        lines.append('  恒等式（写回后应为）：题干底纹段落数 %d ＝ 题干段清点数 %d（dry-run 预演）'
                     % (already + newly, predicted))
    else:
        lines.append('  恒等式：题干底纹段落数（实存 pPr fill=E0E0E0）%d ＝ 题干段清点数 %d %s'
                     % (total_new, predicted, '✓' if total_new == predicted else '←≠'))
        lines.append('  卸载断言：A\'浅底 F2F2F2 段级残留 %d（卸除 %d 段）%s'
                     % (total_legacy, unloaded, '✓' if total_legacy == 0 else '←≠ 残留违规'))
    if stray:
        lines.append('  ! 范围外已存在题干底纹段落 %d 个（body序号样本 %s）——请人工核对归属'
                     % (len(stray), stray[:6]))
    if skip_labels_out:
        lines.append('  登记：题块外标签行 %d 段维持白底（讲部/条目/节语境——清单【编注】说明句副本等）'
                     % skip_labels_out)
    if tbl_mid:
        lines.append('  ! 题干中途遇表格 %d 处（表格内段落未铺，登记待人工核验）' % tbl_mid)
    if hit_title:
        lines.append('  ! 标题段被纳入范围 %d 处（判定缺陷）' % hit_title)
    if args.detail and detail:
        lines.append('  逐题块明细（最多%d条）：' % args.detail)
        for bi, qt, cnt, lb in detail[:args.detail]:
            lines.append('    题块%02d %s 题干段%d 首标签%s' % (bi, qt, cnt, lb))
    return lines, parts, doc, newly


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--report')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--detail', type=int, default=40)
    args = ap.parse_args()
    out = []
    for p in args.files:
        if not os.path.exists(p):
            out.append('◆ %s 不存在，跳过' % os.path.basename(p))
            continue
        if '知识清单' in os.path.basename(p):
            out.append('◆ %s：整件跳过（知识清单——全件白底不铺题干底纹，文件未触碰）'
                       % os.path.basename(p))
            continue
        z = zipfile.ZipFile(p)
        doc0 = etree.fromstring(z.read('word/document.xml'))
        z.close()
        before = snapshot_doc(doc0)
        lines, parts, doc, newly = process(p, args)
        after = snapshot_doc(doc)
        lines.append('  零破坏断言：run级shd计数%s｜w:t/m:t文字流%s'
                     % ('恒等✓' if before[0] == after[0] else '←≠：%r→%r' % (before[0], after[0]),
                        '恒等✓' if before[1] == after[1] else '←≠'))
        if not args.dry_run and newly:
            parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                        encoding='UTF-8', standalone=True)
            tmp = p + '.a2stem'
            zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
            for nm, b in parts.items():
                zo.writestr(nm, b)
            zo.close()
            for _ in range(12):
                try:
                    os.replace(tmp, p)
                    break
                except PermissionError:
                    time.sleep(6)
            else:
                raise RuntimeError('locked: ' + p)
        out.extend(lines)
        out.append('')
    txt = '\n'.join(out)
    print(txt)
    if args.report:
        d = os.path.dirname(os.path.abspath(args.report))
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(txt + '\n')
        print('报告 ->', args.report)


if __name__ == '__main__':
    main()
