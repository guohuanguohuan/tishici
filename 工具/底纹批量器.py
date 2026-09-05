# -*- coding: utf-8 -*-
r"""底纹批量器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T6（工具先建后用；三合一）

口径（规格书T6）：
  a) 题干底纹色值 E0E0E0→F2F2F2（全册 w:shd fill 替换，逐件计数断言登记；实测 E0E0E0 仅见段级
     pPr——run/tcPr 级若出现记异常）；
  b) 讲部/题型标题撤整行底纹 C6D4E3 → 挂左侧粗竖条（w:pBdr/w:left 实线 single sz=18〔2.25pt〕
     space=3 color=auto 黑）；章/节标题底纹 ADC2DA 与章标题底边框一律不动（守恒断言）；
     适用性核验：凡 C6D4E3 段须为讲部（知识讲解｜/方法讲解｜）或题型标题（父链续层序号起段），
     不符者登记不撤；
  c) 详解区（题号块内【分析】【详解】【点睛】等解析块段落）run 级内容灰底 C7C7C7 一律去除。
     白名单（不动）：清单条目/讲部条目需背内容与清单答案行——本器作用域限题号块内解析段，
     构造性不触白名单。衔接件/知识清单件不在《讲练件底纹减法》适用面——c) 对其仅审计登记
     （粘滞口径计数），不剥除。讲练件题目侧本轮前已为 0：复核断言（发现即剥并记数）。
     --xj-clear（②-C T6c 专用，默认关，仅衔接件生效）：衔接件按解析块界定剥除——
     自题号块内首个【分析|详解|点睛|编注】段起（含其后的无标签详解公式段），至【答案】/
     【知识点】行或题块边界止；【答案】行及其值续段、【知识点】行及其值段、题号块行、
     题干续段、条目区一律保护不剥（硬断言：保护类前＝后零触碰；解析区剥后零残留）。
     同轮并出粘滞审计计数与块界定差集分解（对平 ②-C 登记基线 71/649）。
模式：
  默认            a＋b＋c 全做，就地改写（留 .bak_底纹批）
  --only a|b|c    只做指定子项（可逗号并列，如 --only a,b）
  --xj-clear      衔接件解析块清灰开关（默认关；仅对衔接件生效）
  --dry-run       分布预演不落盘：十件底纹 fill 分布表＋各子项命中量
用法:
  python 工具/底纹批量器.py <docx...> [--only a,b,c] [--xj-clear] [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None

PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
             'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
             'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN',
             'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing',
             'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection', 'textAlignment',
             'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange']

NUM = r'(?:\d+(?:\.\d+)+-\d+|\d+)'
QBLOCK_RE = re.compile(r'^%s．（' % NUM)
TITLE_RE = re.compile(r'^\d+(?:\.\d+)+\s')
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*(?:方法讲解|知识讲解)[｜|]')
GRP_RE = re.compile(r'^\d+(?:\.\d+){2,}[\s　]+\S')
ANALYSIS_RE = re.compile(r'【(?:分析|详解|点睛)】')
ENTRY_KEEP_RE = re.compile(r'^%s．' % NUM)   # 条目/讲部号（非括注题号块）
XJ_ANA_RE = re.compile(r'【(?:分析|详解|点睛|编注)】')   # 解析块开块触发（②-C 探针口径）
LBL_ANS_RE = re.compile(r'【答案】')
LBL_KNOW_RE = re.compile(r'【知识点】')
KNOWVAL_RE = re.compile(r'^\d+(?:\.\d+)*[\s　]+\S')      # 知识点值＝教材节号前缀


def has_bar18(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    pb = ppr.find(q('pBdr'))
    if pb is None:
        return False
    lf = pb.find(q('left'))
    return lf is not None and lf.get(q('sz')) == '18'


def rc9(p):
    """段落内 run 级（rPr 父）C7C7C7 计数（含 oMath 内 w:rPr——与 ②-C 探针同口径）"""
    n = 0
    for shd in p.iter(q('shd')):
        if tag(shd.getparent()) == 'rPr' and (shd.get(q('fill')) or '').upper() == 'C7C7C7':
            n += 1
    return n


def xj_clear_strip(els, dry, sticky_audit):
    """衔接件解析块界定剥除（②-C T6c；口径定案见 ②工具/②C_04_05_06 探针三件）。

    分区状态机：题干区（题号块行＋未标注续段）／解析区（【分析|详解|点睛|编注】块＋
    解析已开前提下知识点值段之后的未标注详解公式段）／答案区（【答案】行＋值续段）／
    知识点区（【知识点】行＋值段）。仅解析区剥 run 级 C7C7C7，其余区保护。
    同轮复算粘滞口径计数并与外部审计值对证；差集按保护类分解（对平登记基线）。
    硬断言：保护类零触碰（前＝后）、解析区零残留、全件 rPr C7C7C7 守恒（前＝后＋剥）。"""
    BUCKET_ORDER = ['题号块行', '题干区', '答案行', '答案值续段', '知识点行', '知识点值段', '知识点区余', '其他']
    bucket = {}
    targets = []
    strip = 0
    sticky = 0
    ana_paras = 0
    pre_total = 0
    pre_prot = 0
    region = None
    ana_open = False
    know_val_pending = False
    in_q = False
    in_ana = False
    for c in els:
        if c.tag != q('p'):
            region = None
            ana_open = False
            know_val_pending = False
            in_q = False
            in_ana = False
            continue
        t = ptext(c)
        is_title = (TITLE_RE.match(t) and (pfill(c) in ('ADC2DA', 'C6D4E3') or LECT_RE.match(t) or has_bar18(c)))
        if QBLOCK_RE.match(t):
            in_q = True
            in_ana = False
        elif is_title:
            in_q = False
            in_ana = False
        elif ENTRY_KEEP_RE.match(t) and not QBLOCK_RE.match(t):
            in_q = False
            in_ana = False
        if in_q and ANALYSIS_RE.search(t):
            in_ana = True
        sticky_hit = in_q and in_ana
        if is_title:
            region = '标题'
            ana_open = False
            know_val_pending = False
        elif QBLOCK_RE.match(t):
            region = '题干区'
            ana_open = False
            know_val_pending = False
        elif ENTRY_KEEP_RE.match(t):
            region = '条目区'
            ana_open = False
            know_val_pending = False
        elif region not in (None, '标题', '条目区'):
            if XJ_ANA_RE.search(t):
                region = '解析区'
                ana_open = True
                know_val_pending = False
            elif LBL_ANS_RE.search(t):
                region = '答案区'
                know_val_pending = False
            elif LBL_KNOW_RE.search(t):
                region = '知识点区'
                know_val_pending = True
            elif region == '知识点区':
                if know_val_pending and KNOWVAL_RE.match(t):
                    know_val_pending = False
                else:
                    region = '解析区' if ana_open else '知识点区余'
                    know_val_pending = False
        n = rc9(c)
        pre_total += n
        if sticky_hit:
            sticky += n
        if region == '解析区':
            ana_paras += 1
            if n:
                targets.append(c)
        else:
            pre_prot += n
            if sticky_hit and n:
                if QBLOCK_RE.match(t):
                    k = '题号块行'
                elif LBL_ANS_RE.search(t):
                    k = '答案行'
                elif LBL_KNOW_RE.search(t):
                    k = '知识点行'
                elif region == '答案区':
                    k = '答案值续段'
                elif region == '知识点区':
                    k = '知识点值段'
                elif region in ('知识点区余', '题干区'):
                    k = region
                else:
                    k = '其他'
                bucket[k] = bucket.get(k, 0) + n
    for c in targets:
        for shd in list(c.iter(q('shd'))):
            if tag(shd.getparent()) == 'rPr' and (shd.get(q('fill')) or '').upper() == 'C7C7C7':
                if not dry:
                    shd.getparent().remove(shd)
                strip += 1
    assert sticky_audit == sticky, 'xj-clear 粘滞复算 %d ≠ 外部审计 %d' % (sticky, sticky_audit)
    post_total = pre_total - strip
    post_prot = 0
    ana_residue = 0
    for c in els:
        if c.tag != q('p'):
            continue
        # 剥后重扫：解析区归属判定不受属性删除影响（文本未变），直接复用 targets 成员关系
        n = rc9(c)
        if c in targets:
            ana_residue += n
        else:
            post_prot += n
    want_residue = strip if dry else 0
    assert ana_residue == want_residue, '解析区剥后残留 %d 处（应 %d）' % (ana_residue, want_residue)
    assert pre_prot == post_prot, '保护类 C7C7C7 变动 %d→%d（禁触）' % (pre_prot, post_prot)
    return {'strip': strip, 'ana_paras': ana_paras, 'sticky': sticky,
            'bucket': bucket, 'bucket_order': BUCKET_ORDER,
            'pre_total': pre_total, 'post_total': post_total,
            'pre_prot': pre_prot, 'post_prot': post_prot}


def insert_ppr_ordered(ppr, el):
    idx = PPR_ORDER.index(tag(el))
    for c in ppr:
        cn = tag(c)
        if cn in PPR_ORDER and PPR_ORDER.index(cn) > idx:
            c.addprevious(el)
            return
    ppr.append(el)


def process(path, only, dry, xj_clear=False):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    is_jl = '讲练件' in os.path.basename(path)

    # ---- 全量 fill 分布（报告底表） ----
    dist = {}
    for shd in doc.iter(q('shd')):
        k = (tag(shd.getparent()), shd.get(q('fill')))
        dist[k] = dist.get(k, 0) + 1

    res = {'a': 0, 'b': 0, 'c': 0}
    notes = []

    # ---- a) E0E0E0→F2F2F2 ----
    a_by_parent = {}
    if 'a' in only:
        for shd in doc.iter(q('shd')):
            if (shd.get(q('fill')) or '').upper() == 'E0E0E0':
                pn = tag(shd.getparent())
                a_by_parent[pn] = a_by_parent.get(pn, 0) + 1
                if pn != 'pPr':
                    notes.append('a) E0E0E0 出现在 %s 级（非常规段级，仍改色并登记）' % pn)
                shd.set(q('fill'), 'F2F2F2')
                res['a'] += 1

    # ---- b) 讲部/题型标题 C6D4E3 → 左竖条 ----
    b_skipped = 0
    if 'b' in only:
        adc_pre = sum(1 for shd in doc.iter(q('shd'))
                      if tag(shd.getparent()) == 'pPr' and (shd.get(q('fill')) or '').upper() == 'ADC2DA')
        for p in body.iter(q('p')):
            ppr = p.find(q('pPr'))
            if ppr is None:
                continue
            sh = ppr.find(q('shd'))
            if sh is None or (sh.get(q('fill')) or '').upper() != 'C6D4E3':
                continue
            t = ptext(p)
            if not (LECT_RE.match(t) or GRP_RE.match(t)):
                notes.append('b) C6D4E3 段非讲部/题型标题（登记不撤）: %r' % t[:40])
                b_skipped += 1
                continue
            ppr.remove(sh)
            pb = ppr.find(q('pBdr'))
            if pb is None:
                pb = etree.Element(q('pBdr'))
                insert_ppr_ordered(ppr, pb)
            if pb.find(q('left')) is None:
                left = etree.Element(q('left'))
                left.set(q('val'), 'single')
                left.set(q('sz'), '18')
                left.set(q('space'), '3')
                left.set(q('color'), 'auto')
                pb.append(left)
            res['b'] += 1
        adc_post = sum(1 for shd in doc.iter(q('shd'))
                       if tag(shd.getparent()) == 'pPr' and (shd.get(q('fill')) or '').upper() == 'ADC2DA')
        assert adc_pre == adc_post, '章/节标题底纹 ADC2DA 数量变动（禁触）: %d→%d' % (adc_pre, adc_post)

    # ---- c) 解析区 run 级 C7C7C7 处置 ----
    #   讲练件：粘滞口径复核剥除（题目侧实测 0，发现即剥并记数）；
    #   衔接件：默认粘滞口径仅审计登记；--xj-clear 开启后按解析块界定剥除
    #           （答案行/知识点区/题号块/题干/条目区保护，同轮出对平差集分解）；
    #   清单件：粘滞口径仅审计登记（--xj-clear 不生效）。
    c_audit = 0
    c_xj = None
    if 'c' in only:
        is_xj = '衔接件' in os.path.basename(path)
        els = list(body)
        if is_jl:
            in_q = False
            in_ana = False
            for i, c in enumerate(els):
                if c.tag != q('p'):
                    in_q = False
                    in_ana = False
                    continue
                t = ptext(c)
                if QBLOCK_RE.match(t):
                    in_q = True
                    in_ana = False
                elif TITLE_RE.match(t) and (pfill(c) in ('ADC2DA', 'C6D4E3') or LECT_RE.match(t)):
                    in_q = False
                    in_ana = False
                elif ENTRY_KEEP_RE.match(t) and not QBLOCK_RE.match(t):
                    in_q = False
                    in_ana = False
                if in_q and ANALYSIS_RE.search(t):
                    in_ana = True
                if not (in_q and in_ana):
                    continue
                for shd in list(c.iter(q('shd'))):
                    if tag(shd.getparent()) == 'rPr' and (shd.get(q('fill')) or '').upper() == 'C7C7C7':
                        shd.getparent().remove(shd)
                        res['c'] += 1
        else:
            # 粘滞口径审计（登记不剥；与 ②-C 登记基线同口径）
            in_q = False
            in_ana = False
            for i, c in enumerate(els):
                if c.tag != q('p'):
                    in_q = False
                    in_ana = False
                    continue
                t = ptext(c)
                if QBLOCK_RE.match(t):
                    in_q = True
                    in_ana = False
                elif TITLE_RE.match(t) and (pfill(c) in ('ADC2DA', 'C6D4E3') or LECT_RE.match(t)):
                    in_q = False
                    in_ana = False
                elif ENTRY_KEEP_RE.match(t) and not QBLOCK_RE.match(t):
                    in_q = False
                    in_ana = False
                if in_q and ANALYSIS_RE.search(t):
                    in_ana = True
                if in_q and in_ana:
                    for shd in c.iter(q('shd')):
                        if tag(shd.getparent()) == 'rPr' and (shd.get(q('fill')) or '').upper() == 'C7C7C7':
                            c_audit += 1
            if is_xj and xj_clear:
                c_xj = xj_clear_strip(els, dry, c_audit)
                res['c'] = c_xj['strip']

    # 段级 C7C7C7 违规登记（不剥）
    for p in body.iter(q('p')):
        if pfill(p) == 'C7C7C7':
            notes.append('c) 段级 C7C7C7 误挂（违规登记不剥，交人工）: %r' % ptext(p)[:40])

    lines = []
    lines.append('## T6 底纹批量器（%s）— %s%s' % (
        '+'.join(only), os.path.basename(path), '（dry-run）' if dry else ''))
    lines.append('fill 分布：' + '；'.join('%s/%s×%d' % (k[0], k[1], v) for k, v in sorted(dist.items())))
    if 'a' in only:
        lines.append('a) E0E0E0→F2F2F2：%d 处（%s）' % (res['a'], '；'.join('%s×%d' % kv for kv in a_by_parent.items()) or '无'))
    if 'b' in only:
        lines.append('b) 讲部/题型标题撤 C6D4E3＋挂左竖条：%d 段（跳过非标题 %d）；ADC2DA 守恒断言 PASS' % (res['b'], b_skipped))
    if 'c' in only:
        if is_jl:
            lines.append('c) 详解区 run 级 C7C7C7 剥除：%d 处（讲练件题目侧复核%s）'
                         % (res['c'], '＝0 PASS' if res['c'] == 0 else '＞0 已剥除并登记'))
        elif c_xj is not None:
            bd = '＋'.join('%s%d' % (k, c_xj['bucket'][k])
                           for k in c_xj['bucket_order'] if c_xj['bucket'].get(k)) or '无'
            lines.append('c) 衔接件解析块清灰（--xj-clear）：解析区剥除 %d 处（解析区段 %d 段）｜'
                         '对平＝粘滞审计 %d − 块外保护 %d（%s）＝%d｜rPr C7C7C7 全件 前→后 %d→%d｜'
                         '保护类零触碰 %d→%d PASS｜解析区零残留 PASS'
                         % (c_xj['strip'], c_xj['ana_paras'], c_xj['sticky'],
                            c_xj['sticky'] - c_xj['strip'], bd, c_xj['strip'],
                            c_xj['pre_total'], c_xj['post_total'],
                            c_xj['pre_prot'], c_xj['post_prot']))
        else:
            lines.append('c) 详解区 run 级 C7C7C7 审计（非讲练件不剥，附则适用面）：%d 处登记' % c_audit)
    for nt in notes[:10]:
        lines.append('  ! ' + nt)
    lines.append('')

    if not dry and (res['a'] or res['b'] or res['c']):
        import shutil
        bak = path + '.bak_底纹批'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t6tmp'
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
                zout.writestr(item, data)
        for k in range(12):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                time.sleep(6)
        else:
            raise RuntimeError('locked: ' + path)
    return '\n'.join(lines)


def main():
    argv = sys.argv[1:]
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    xj_clear = '--xj-clear' in argv
    argv = [a for a in argv if a != '--xj-clear']
    only = ['a', 'b', 'c']
    if '--only' in argv:
        k = argv.index('--only')
        only = [x.strip() for x in argv[k + 1].split(',')]
        assert all(x in ('a', 'b', 'c') for x in only), '--only 须为 a/b/c 逗号列'
        del argv[k:k + 2]
    report = None
    if '--report' in argv:
        k = argv.index('--report'); report = argv[k + 1]; del argv[k:k + 2]
    assert argv, '用法: python 工具/底纹批量器.py <docx...> [--only a,b,c] [--xj-clear] [--dry-run] [--report r.md]'
    out = []
    for path in argv:
        r = process(path, only, dry, xj_clear)
        out.append(r)
        print(r)
    if report:
        with open(report, 'a', encoding='utf-8') as f:
            f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
