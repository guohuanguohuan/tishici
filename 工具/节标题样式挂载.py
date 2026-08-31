# -*- coding: utf-8 -*-
#
# 沿革：2026-08-30 工具债清偿（看板工具债②）新建——公共规则§7「标题真实样式挂载」条款落地；
#   2026-08-31 W10 缺陷修复（created 分支漏调 create_style）；
#   2026-08-31 欠账A·工具债④ 改版——N3/N4/N5 新参数：28半点＋顶格＋整行底纹#ADC2DA＋左对齐，
#   basedOn 指向该件 styles.xml 真实 Normal styleId（字面量'Normal'在部分件悬空、样式链断教训），
#   节层识别改以 extract_structure 三标题分型为源（讲练件「三级无标记＝题型组」启发式随之废止，
#   清单/衔接件无标记真教材节不再漏挂）；旧缩进梯子（0/200/400/800）挂载逻辑不存在于本工具、
#   亦不新增（段落级 w:ind 清零归 工具/标题整行底纹.py，本工具只挂样式不动段落直接格式）。
#
"""节标题样式挂载.py — 教材节标题挂内置样式「标题3」（只处理副本，断言不过不动输出文件）

样式定义（N3/N4/N5 现行参数，挂载前后视觉零变化的镜像参数——须在 工具/标题整行底纹.py
之后运行：节标题段的直接格式（sz28加粗＋pPr shd #ADC2DA＋w:ind清零）先行落地，本工具
把同参数写入样式定义并挂 pStyle，A2 断言逐 run/逐段核对解析值不变）：
  · rPr＝rFonts 宋体/Times New Roman＋b＋sz 28半点（不带 szCs/bCs——无直接 szCs/bCs 的 run
    解析值保持不变，A2 可全过）；
  · pPr＝w:shd(clear,auto,#ADC2DA)＋w:ind 全零（顶格）＋jc=left＋outlineLvl=2（保留原值）；
  · basedOn＝该件 styles.xml 真实默认段落样式 styleId（default=1 的 paragraph 样式；
    部分件为 'a' 等——字面量 'Normal' 悬空即样式链断、解析值丢失，既有错值就地纠正并计数）；
  · styles.xml 已有「标题3」（name=heading 3/标题3 或 styleId=Heading3）则复用其 styleId 并
    规整定义到现行参数；无则新建（basedOn 真实 Normal、qFormat、显式携全部现行参数）；
    stylesWithEffects.xml 存在同 id 定义时同步规整。

节层识别（extract_structure kind=section，body 级；表内段落天然不入）；
  讲部/题型（lecture/group）不入样式（页眉 STYLEREF 只需节层——§7标题真实样式挂载条款）；
  章/讲标题挂「标题2」属后续扩展，本工具不处理。

段落处理：节标题段 pPr 首位插 pStyle（已有他值 pStyle 拒绝覆盖）；run 属性一律不动。

安全断言（全过才写输出，任一不过退出码 2、不产生输出文件）：
  A1 挂载段计数 ≥1（空件需 --allow-empty 显式放行）；
  A2 视觉零变化——document＋全部 header/footer 件内每个 w:r 的 sz/szCs/b/bCs/i/iCs/
     rFonts(含主题)/color/shd 与每个段落的 keepNext/keepLines/pageBreakBefore/widowControl/
     spacing/ind/jc 解析值（docDefaults→样式链→直接格式）挂载前后逐一相等（outlineLvl 非
     视觉项不计）；等价归一：jc ∈ {None,left,start} 等价（默认左）、w:ind 全零 ≡ 缺省；
     唯一例外＝挂载段上 jc both/justify→left（§7一律左对齐条款的存量纠偏，单行标题视觉
     等价），逐段计数落盘；
  A3 零字符变化——全件 w:t 拼接文本前后相等；
  A4 幂等——对已挂载件重复运行零改动（样式已规整且段落已挂时输出=输入字节级拷贝）。

用法: python 节标题样式挂载.py <in.docx> <out.docx> [--verbose] [--dry-run] [--allow-empty]
"""
import sys, os, re, zipfile, copy
try:   # reconfigure 防双重包装（extract_structure 导入时会重包 stdout——二次包装GC关buffer坑）
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lxml import etree
from extract_structure import structure

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

STYLE_NAME_CANDIDATES = ('heading 3', '标题3')
DEFAULT_STYLE_ID = 'Heading3'
SEC_FILL = 'ADC2DA'          # 节标题整行底纹（N5）
SEC_SZ = '28'                # 节标题字号（N3 四号）

OFF_VALS = ('0', 'false', 'none', 'off')

# w:pPr 子件 schema 序（样式 pPr 构建定位）
PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
             'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
             'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN',
             'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing',
             'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection', 'textAlignment',
             'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange']
RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike',
             'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish',
             'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs', 'highlight',
             'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs', 'em', 'lang',
             'eastAsianLayout', 'specVanish', 'oMath']


class ToolError(Exception):
    pass


def _insert_ordered(parent, el, order):
    name = etree.QName(el).localname
    idx = order.index(name)
    for c in parent:
        cn = etree.QName(c).localname
        if cn not in order or order.index(cn) > idx:
            c.addprevious(el)
            return
    parent.append(el)


# ---------- 样式表上下文 ----------

def build_styles_ctx(styles_root):
    ctx = {'by_id': {}, 'default_para': None, 'rpr_default': None}
    dd = styles_root.find(q('docDefaults'))
    if dd is not None:
        rprd = dd.find(q('rPrDefault'))
        if rprd is not None:
            ctx['rpr_default'] = rprd.find(q('rPr'))
    for st in styles_root.findall(q('style')):
        sid = st.get(q('styleId'))
        nm = st.find(q('name'))
        based = st.find(q('basedOn'))
        entry = {
            'el': st,
            'name': nm.get(q('val')) if nm is not None else None,
            'basedOn': based.get(q('val')) if based is not None else None,
            'rpr': st.find(q('rPr')),
            'ppr': st.find(q('pPr')),
            'type': st.get(q('type')),
        }
        ctx['by_id'][sid] = entry
        if st.get(q('type')) == 'paragraph' and st.get(q('default')) in ('1', 'true'):
            ctx['default_para'] = sid
    return ctx


def style_chain(ctx, start_id):
    chain, seen, cur = [], set(), start_id
    while cur and cur not in seen:
        seen.add(cur)
        st = ctx['by_id'].get(cur)
        if st is None:
            break
        chain.append(st)
        cur = st['basedOn']
    chain.reverse()
    return chain


def real_normal_sid(ctx):
    """真实 Normal styleId（default=1 的段落样式）。"""
    return ctx['default_para']


# ---------- 解析值收集（含等价归一） ----------

def _toggle(el):
    if el is None:
        return None
    v = el.get(q('val'))
    if v is None:
        return True
    return False if v.strip().lower() in OFF_VALS else True


def _norm_jc(v):
    if v is None or v in ('left', 'start'):
        return 'LEFT'
    return v


def _norm_ind(d):
    """全零/缺省归一：全部现值为 '0' 的属性视为缺省（顶格≡无缩进设置）。"""
    return {k: v for k, v in d.items() if str(v) != '0'}


def collect_rpr_keys(rpr, out):
    if rpr is None:
        return
    for c in rpr:
        t = etree.QName(c).localname
        if t in ('sz', 'szCs'):
            out[t] = c.get(q('val'))
        elif t in ('b', 'bCs', 'i', 'iCs'):
            out[t] = _toggle(c)
        elif t == 'rFonts':
            for a in ('ascii', 'hAnsi', 'eastAsia', 'cs',
                      'asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
                v = c.get(q(a))
                if v is not None:
                    out['rFonts.' + a] = v
        elif t == 'color':
            for a in ('val', 'themeColor', 'themeShade', 'themeTint'):
                v = c.get(q(a))
                if v is not None:
                    out['color.' + a] = v
        elif t == 'shd':
            for a in ('val', 'fill', 'color'):
                v = c.get(q(a))
                if v is not None:
                    out['shd.' + a] = v


def collect_ppr_keys(ppr, out):
    if ppr is None:
        return
    for c in ppr:
        t = etree.QName(c).localname
        if t in ('keepNext', 'keepLines', 'pageBreakBefore', 'widowControl'):
            out[t] = _toggle(c)
        elif t == 'spacing':
            for a in ('before', 'after', 'line', 'lineRule',
                      'beforeAutospacing', 'afterAutospacing'):
                v = c.get(q(a))
                if v is not None:
                    out['spacing.' + a] = v
        elif t == 'ind':
            for a in ('left', 'right', 'leftChars', 'rightChars',
                      'firstLine', 'firstLineChars', 'hanging', 'hangingChars'):
                v = c.get(q(a))
                if v is not None:
                    out['ind.' + a] = v
        elif t == 'jc':
            v = c.get(q('val'))
            if v is not None:
                out['jc'] = _norm_jc(v)


def resolved_run_keys(run_el, para_chain, ctx):
    out = {}
    collect_rpr_keys(ctx['rpr_default'], out)
    for st in para_chain:
        collect_rpr_keys(st['rpr'], out)
    rpr = run_el.find(q('rPr'))
    if rpr is not None:
        collect_rpr_keys(rpr, out)
    return out


def chain_for_para(p, ctx):
    ppr = p.find(q('pPr'))
    sid = None
    if ppr is not None:
        ps = ppr.find(q('pStyle'))
        if ps is not None:
            sid = ps.get(q('val'))
    if not sid:
        sid = ctx['default_para']
    return style_chain(ctx, sid)


def resolved_para_keys(p, ctx):
    out = {}
    for st in chain_for_para(p, ctx):
        collect_ppr_keys(st['ppr'], out)
    ppr = p.find(q('pPr'))
    if ppr is not None:
        collect_ppr_keys(ppr, out)
    # ind 全零归一
    for k in [k for k in out if k.startswith('ind.')]:
        if out[k] == '0':
            del out[k]
    if 'jc' not in out:
        out['jc'] = 'LEFT'
    return out


# ---------- 节标题识别（extract_structure 为源） ----------

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def find_section_titles(path, doc_root):
    """返回 [(段落元素, 文本)]——body 直接子段落的节层标题（kind=section）。"""
    body = doc_root.find(q('body'))
    els = list(body)
    hits = []
    for x in structure(path)['items']:
        if x['kind'] != 'section':
            continue
        hits.append((els[x['el']], x['text']))
    return hits


# ---------- 挂载 ----------

def mount_paragraph(p, style_id):
    """返回 'added' / 'kept'（幂等跳过）"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    ps = ppr.find(q('pStyle'))
    if ps is None:
        ps = etree.Element(q('pStyle'))
        ps.set(q('val'), style_id)
        ppr.insert(0, ps)
        return 'added'
    if ps.get(q('val')) == style_id:
        return 'kept'
    raise ToolError('段落已有其他 pStyle=%s，拒绝覆盖：%s' % (ps.get(q('val')), para_text(p)[:40]))


# ---------- 样式定义定位 / 规整 / 新建 ----------

def find_heading3(styles_root):
    for st in styles_root.findall(q('style')):
        nm = st.find(q('name'))
        nv = (nm.get(q('val')) or '') if nm is not None else ''
        if nv.strip().lower() in STYLE_NAME_CANDIDATES:
            return st
    for st in styles_root.findall(q('style')):
        if st.get(q('styleId')) == DEFAULT_STYLE_ID:
            return st
    return None


def target_rpr():
    # 28半点＋b＋rFonts（不带 szCs/bCs：无直接值的 run 挂载前后解析值严格相等，A2 全过）
    r = etree.Element(q('rPr'))
    rf = etree.SubElement(r, q('rFonts'))
    rf.set(q('ascii'), 'Times New Roman')
    rf.set(q('hAnsi'), 'Times New Roman')
    rf.set(q('eastAsia'), '宋体')
    rf.set(q('cs'), 'Times New Roman')
    etree.SubElement(r, q('b'))
    sz = etree.SubElement(r, q('sz')); sz.set(q('val'), SEC_SZ)
    return r


def target_ppr(keep_outline_val):
    # 整行底纹#ADC2DA＋ind全零（顶格）＋jc left＋outlineLvl（schema 序）
    p = etree.Element(q('pPr'))
    shd = etree.SubElement(p, q('shd'))
    shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), SEC_FILL)
    ind = etree.SubElement(p, q('ind'))
    for a in ('left', 'leftChars', 'firstLine', 'firstLineChars', 'hanging', 'hangingChars'):
        ind.set(q(a), '0')
    jc = etree.SubElement(p, q('jc')); jc.set(q('val'), 'left')
    ol = etree.SubElement(p, q('outlineLvl'))
    ol.set(q('val'), keep_outline_val if keep_outline_val is not None else '2')
    return p


def _sig(el):
    if el is None:
        return None
    return [(etree.QName(c).localname, tuple(sorted((k.split('}')[-1], v) for k, v in c.attrib.items())))
            for c in el]


def style_outline_val(st):
    old_ppr = st.find(q('pPr'))
    if old_ppr is not None:
        ol = old_ppr.find(q('outlineLvl'))
        if ol is not None:
            return ol.get(q('val'))
    return None


def fix_basedOn(st, real_sid):
    """basedOn 纠偏：指向真实 Normal styleId（错值/悬空就地纠正）。返回 (旧值, 是否改动)。"""
    bo = st.find(q('basedOn'))
    if bo is None:
        bo = etree.Element(q('basedOn'))
        bo.set(q('val'), real_sid)
        nm = st.find(q('name'))
        anchor = nm if nm is not None else st[0] if len(st) else None
        if anchor is not None:
            anchor.addnext(bo)
        else:
            st.insert(0, bo)
        return None, True
    old = bo.get(q('val'))
    if old != real_sid:
        bo.set(q('val'), real_sid)
        return old, True
    return old, False


def style_needs_norm(st):
    return (_sig(st.find(q('pPr'))) != _sig(target_ppr(style_outline_val(st)))) or \
           (_sig(st.find(q('rPr'))) != _sig(target_rpr()))


def apply_norm(st):
    old_rpr = st.find(q('rPr'))
    old_ppr = st.find(q('pPr'))
    new_ppr = target_ppr(style_outline_val(st))
    new_rpr = target_rpr()
    if old_ppr is not None:
        st.remove(old_ppr)
    if old_rpr is not None:
        st.remove(old_rpr)
    st.append(new_ppr)   # pPr 在 rPr 之前、均在 name/basedOn/… 之后（追加到尾部合法）
    st.append(new_rpr)


def create_style(styles_root, real_sid):
    st = etree.SubElement(styles_root, q('style'))
    st.set(q('type'), 'paragraph')
    st.set(q('styleId'), DEFAULT_STYLE_ID)
    nm = etree.SubElement(st, q('name')); nm.set(q('val'), 'heading 3')
    bo = etree.SubElement(st, q('basedOn')); bo.set(q('val'), real_sid)
    etree.SubElement(st, q('qFormat'))
    st.append(target_ppr(None))
    st.append(target_rpr())
    return st


def scan_style_references(zin, style_id):
    refs = []
    for name in zin.namelist():
        if not name.startswith('word/') or not name.endswith('.xml'):
            continue
        base = name.rsplit('/', 1)[-1]
        if base.startswith('styles'):
            continue
        try:
            root = etree.fromstring(zin.read(name))
        except etree.XMLSyntaxError:
            continue
        for el in root.iter(q('pStyle'), q('rStyle')):
            if el.get(q('val')) == style_id:
                refs.append(name)
                break
    return refs


# ---------- 主流程 ----------

def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    flags = set(a for a in argv if a.startswith('--'))
    verbose = '--verbose' in flags
    dry = '--dry-run' in flags
    allow_empty = '--allow-empty' in flags
    if len(args) != 2:
        print(__doc__)
        return 1
    src, dst = args
    if os.path.abspath(src) == os.path.abspath(dst):
        print('[中止] 输出路径与输入相同——本工具只处理副本，禁止原地改写。')
        return 2
    if not os.path.exists(src):
        print('[中止] 输入不存在：', src)
        return 2

    zin = zipfile.ZipFile(src)
    doc_root = etree.fromstring(zin.read('word/document.xml'))
    styles_root = etree.fromstring(zin.read('word/styles.xml'))
    swe_name = 'word/stylesWithEffects.xml' if 'word/stylesWithEffects.xml' in zin.namelist() else None
    swe_root = etree.fromstring(zin.read(swe_name)) if swe_name else None

    ctx_before = build_styles_ctx(styles_root)
    real_sid = real_normal_sid(ctx_before)
    if real_sid is None:
        print('[中止] styles.xml 无 default=1 段落样式（真实 Normal styleId 不可解析）。')
        return 2

    # ---- 样式定位 ----
    st_el = find_heading3(styles_root)
    bo_fixed = None
    if st_el is None:
        action = 'created'
        sid = DEFAULT_STYLE_ID
        create_style(styles_root, real_sid)
    else:
        sid = st_el.get(q('styleId'))
        bo_old, bo_chg = fix_basedOn(st_el, real_sid)
        if bo_chg:
            bo_fixed = (bo_old, real_sid)
        refs = scan_style_references(zin, sid)
        if style_needs_norm(st_el):
            # 引用不预中止：A2 对全件（document＋header/footer）逐 run/逐段解析值核验，
            # 任何真实视觉变化（含样式规整波及的既有引用段）都会被 A2 拦下。
            apply_norm(st_el)
            action = 'normalized(refs=%d)' % len(refs)
        else:
            action = 'already-normalized(refs=%d)' % len(refs)

    # ---- 段落挂载 ----
    hits = find_section_titles(src, doc_root)
    mounted_els = []
    added = kept = 0
    for p, t in hits:
        r = mount_paragraph(p, sid)
        if r == 'added':
            added += 1
        else:
            kept += 1
        mounted_els.append(p)
    total_mounted = added + kept
    print('真实 Normal styleId=%r｜识别节标题（kind=section）：%d 段；本次新挂载 %d 段，幂等已挂 %d 段'
          % (real_sid, len(hits), added, kept))
    if verbose:
        for i, (p, t) in enumerate(hits, 1):
            print('  %2d. %s' % (i, t))
    if total_mounted == 0 and not allow_empty:
        print('[中止] 节标题识别数为 0——疑似与该件形态不匹配，按安全纪律不动文件'
              '（确认无误可加 --allow-empty）。')
        return 2

    # ---- stylesWithEffects 同步规整 ----
    swe_changed = False
    if swe_root is not None:
        st2 = find_heading3(swe_root)
        if st2 is not None and st2.get(q('styleId')) == sid and style_needs_norm(st2):
            fix_basedOn(st2, real_sid)
            apply_norm(st2)
            swe_changed = True

    # ---- 断言 A2/A3：视觉零变化 + 零字符（document＋header/footer 全件） ----
    ctx_after = build_styles_ctx(styles_root)
    parts = ['word/document.xml'] + [n for n in zin.namelist()
                                     if re.match(r'word/(header|footer)\d*\.xml$', n)]
    mounted_ids = {id(p) for p in mounted_els}
    jc_fixed = 0
    n_runs_checked = n_paras_checked = 0
    for part in parts:
        root_before = etree.fromstring(zin.read(part))
        root_after = doc_root if part == 'word/document.xml' else root_before
        pb_list = list(root_before.find(q('body')).iter(q('p'))) if part == 'word/document.xml' \
            else list(root_before.iter(q('p')))
        pa_list = list(root_after.find(q('body')).iter(q('p'))) if part == 'word/document.xml' \
            else list(root_after.iter(q('p')))
        if len(pb_list) != len(pa_list):
            print('[断言失败] %s 前后段落数不一致（%d→%d）' % (part, len(pb_list), len(pa_list)))
            return 2
        for pb, pa in zip(pb_list, pa_list):
            cb = chain_for_para(pb, ctx_before)
            ca = chain_for_para(pa, ctx_after)
            rb_runs = list(pb.iter(q('r')))
            ra_runs = list(pa.iter(q('r')))
            if len(rb_runs) != len(ra_runs):
                print('[断言失败 A2] %s run数不一致: %r' % (part, para_text(pb)[:30]))
                return 2
            for r0, r1 in zip(rb_runs, ra_runs):
                k0 = resolved_run_keys(r0, cb, ctx_before)
                k1 = resolved_run_keys(r1, ca, ctx_after)
                if k0 != k1:
                    diff = {k: (k0.get(k), k1.get(k)) for k in set(k0) | set(k1) if k0.get(k) != k1.get(k)}
                    print('[断言失败 A2] %s 段「%s」run「%s」差异 %s'
                          % (part, para_text(pb)[:30], ''.join(x.text or '' for x in r1.findall(q('t')))[:20], diff))
                    return 2
                n_runs_checked += 1
            k0 = resolved_para_keys(pb, ctx_before)
            k1 = resolved_para_keys(pa, ctx_after)
            if k0 != k1:
                diff = {k: (k0.get(k), k1.get(k)) for k in set(k0) | set(k1) if k0.get(k) != k1.get(k)}
                if list(diff) == ['jc'] and k0.get('jc') in ('both', 'justify') and k1.get('jc') == 'LEFT' \
                        and id(pa) in mounted_ids:
                    jc_fixed += 1   # §7一律左对齐条款存量纠偏（单行标题视觉等价），计数放行
                else:
                    print('[断言失败 A2] %s 段「%s」pPr 差异 %s' % (part, para_text(pb)[:30], diff))
                    return 2
            n_paras_checked += 1
        if part == 'word/document.xml':
            txt_before = ''.join(t.text or '' for t in root_before.iter(q('t')))
            txt_after = ''.join(t.text or '' for t in root_after.iter(q('t')))
            if txt_before != txt_after:
                print('[断言失败 A3] 字符级文本发生变化')
                return 2
    print('断言 A2 视觉零变化：PASS（%d 部件 × %d run × sz/szCs/b/bCs/i/iCs/rFonts/color/shd ＋ '
          '%d 段 pPr 解析值逐一相等；jc存量纠偏 %d 段〔both/justify→left，§7左对齐条款〕）'
          % (len(parts), n_runs_checked, n_paras_checked, jc_fixed))
    print('断言 A3 零字符变化：PASS')

    # ---- 落盘 ----
    if dry:
        print('[dry-run] 不写输出。样式动作=%s，挂载=%d（新%d/已%d），目标 styleId=%s，basedOn=%s'
              % (action, total_mounted, added, kept, sid, real_sid))
        return 0

    doc_changed = added > 0
    chg = {'word/document.xml': etree.tostring(doc_root, xml_declaration=True, encoding='UTF-8', standalone=True) if doc_changed else None,
           'word/styles.xml': etree.tostring(styles_root, xml_declaration=True, encoding='UTF-8', standalone=True) if action.startswith(('created', 'normalized')) or bo_fixed else None}
    if swe_name and swe_changed:
        chg[swe_name] = etree.tostring(swe_root, xml_declaration=True, encoding='UTF-8', standalone=True)

    if not any(v for v in chg.values()):
        with open(dst, 'wb') as f:
            f.write(open(src, 'rb').read())
        print('断言 A4 幂等：零改动，输出=输入字节级拷贝 -> %s' % dst)
        print('完成：挂载段合计 %d，styleId=%s（动作=%s，basedOn=%s）' % (total_mounted, sid, action, real_sid))
        return 0

    zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
    try:
        for item in zin.infolist():
            data = chg.get(item.filename)
            if data is not None:
                zout.writestr(item.filename, data, compress_type=zipfile.ZIP_DEFLATED)
            else:
                zout.writestr(item, zin.read(item.filename))
    finally:
        zout.close()
    print('输出 -> %s（替换 %s）' % (dst, ', '.join(k for k, v in chg.items() if v)))
    print('完成：挂载段合计 %d（新%d/已%d），styleId=%s（动作=%s，basedOn=%s%s）'
          % (total_mounted, added, kept, sid, action, real_sid,
             '，basedOn纠偏 %s→%s' % bo_fixed if bo_fixed else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
