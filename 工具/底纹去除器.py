# -*- coding: utf-8 -*-
r"""底纹去除器.py — 2026-09-04 选必1版式复合修复轮·子步2新建（附则《讲练件底纹减法》执行工具；
工具债案6「先建后用」；用户令2026-09-03「题干底纹已足，题号/编注/答案/解析的额外底纹去掉」＋
甲案拍板：讲部条目填空/需背内容灰底保留）。

适用面：讲练件（含派生分层卷/实验卷随骨架复制的同类标记）。衔接件/知识清单件/学史切片不适用
（--audit-only 出零变化对照用，不对其执行剥除）。

剥除（四类废止，全部 fill=C9C9C9 的 run 级 w:rPr/w:shd 与 OMML m:r、ctrlPr 的 w:rPr/w:shd 挂点）：
  ①题号难度块底纹——题号块段（「题型号-节内序号．（档位…）」起段）段首连续灰底 run 串
    恰为「N．」新形或过渡旧形整块者；黑字白底、加粗维持（只删 w:shd 子元素，不动 rPr 其余属性）。
  ②题目侧答案值灰底——白名单外全部内容标记 run（【答案】值/需背/知识点值/空白尾巴 run 等）
    与 OMML 公式型挂灰；含讲部方法讲解区（非条目块）灰底——依据＝附则目标计数表①行双值口径
    ＋四值校验「201灰度值＝条目号＋第一子层＋讲部需背三源合计、且仅此来源」（甲案改文）。
  ③块标签芯片底纹——全部行内【×】标签（字符级灰底蒙版整 chip 识别，口径同 六类底纹计数.py；
    含讲部【定义】【结论】与条目区内芯片——附则③「一律黑字白底」；标签文字保留）。
  ④并行解法标记底纹——方法一/解法一/另解起段标记 run（MARK_RE 整 run 口径，同源计数工具）。

保留（白名单禁触，计数变化=0 硬断言）：
  W1 标题整行底纹（段级 #ADC2DA/#C6D4E3）与题干底纹（段级 #E0E0E0）——本器只删 C9C9C9 挂点，
     段级 shd 一概不动（构造性豁免）；段级 C9C9C9 误挂若存在＝违规登记且不剥（交人工）。
  W2 条目号／条目第一子层 lead run（条目族）。
  W3 讲部条目区内需背灰底——条目区＝条目号「节号-序号．」起段（非题号块段、非标题）至下一条目号
     ／题号块／标题边界；区内非芯片灰底 run 与 OMML 挂点保留（甲案；区内芯片照③剥除）。
  W4 表内一切 C9C9C9（run/tcPr/OMML——导航表表头等 §6 样式位）。
  〔基〕/〔进〕本无底纹。

作用域断言（写盘前硬门，任一不过即拒写）：
  A1 剥除挂点 fill 集合＝{C9C9C9} 精确枚举；
  A2 白名单计数变化=0（W1段级四色分记、W2、W3、W4 逐项前后恒等）；
  A3 文字流零变更——w:t/m:t 文档序字符流前后全等；w:p/w:tbl/w:t/m:r/m:oMath/drawing/sectPr/w:r
     元素计数全等（不拆 run）；w:shd 减数＝剥除挂点数；
  A4 芯片 run 隔离断言——芯片 span 与保留区（条目区）非芯片文字同 run 时不剥该 run、登记 MANUAL
     （选必1六件实测芯片均为独立 run，本断言为兜底）；
  A5 分区划分＝全体 C9C9C9 run/OMML 挂点的不交并（剥除∪保留，无遗漏无重复）。

模式：
  默认          剥除并写 <out.docx>（容器其余成员逐字节复制，document.xml 仅删 w:shd 子元素）。
  --dry-run     全量模拟＋分布报告（类别×减前/减后计数），不落盘。
  --audit-only  只出 fill 分布与分区计数（减前＝减后零变化对照用；不适用件登记）。
报告：--report <txt> 落盘（缺省打印 stdout）；报告路径拒绝成品扩展名与同路径（防误用）。
用法:
  python 底纹去除器.py <in.docx> <out.docx> [--report r.txt]            # 执行
  python 底纹去除器.py <in.docx> --dry-run [--report r.txt]             # 预演
  python 底纹去除器.py <in.docx> --audit-only [--report r.txt]          # 零变化对照
"""
import sys, io, os, re, zipfile, json
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

C9 = 'C9C9C9'
FILL_TITLE1 = 'ADC2DA'
FILL_TITLE2 = 'C6D4E3'
FILL_STEM = 'E0E0E0'
PRODUCT_EXT = ('.docx', '.docm', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.pdf', '.zip')

# —— 与 工具/六类底纹计数.py 同源口径（复制常量避免中文名模块导入脆性；改动须两处同步）——
CHIP_RE = re.compile(r'【[^】]{1,16}】')
CHIP_BLACKLIST = ('【易错】', '【了解】')
CHIP_BLACKLIST_RE = re.compile(r'^【典例[^】]*】$')
MARK_RE = re.compile(r'^(?:\(\d{1,2}\)|（\d{1,2}）)?(?:【[^】]{1,12}】)?(?:解：|证明：)?'
                     r'(［?(?:方法|解法)[一二三四五六七八九十]{1,3}］?|另解)[：:]?$')
NUM_HEAD = r'(?:\d+|\d+(?:\.\d+)+-\d+)'
QBLOCK_HEAD_RE = re.compile(
    r'^' + NUM_HEAD + r'．（(?:(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%))?·卡壳看答案'
    r'|衔接必会·卡壳看答案|(?:简单|中档|难))')
QNUM_LEGACY_RE = re.compile(
    r'^' + NUM_HEAD + r'．（(?:(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%)·卡壳看答案)?|衔接必会·卡壳看答案)）$')
LEAD_NUM_RE = re.compile(r'^(?:\d+|\d+(?:\.\d+)+-\d+)．(?:【[^】]{1,16}】)*$')
LEAD_SUB_RE = re.compile(r'^（\d+）(?:【[^】]{1,16}】)*$')
ENT_RE = re.compile(r'^' + NUM_HEAD + r'．')
HEAD_RE = re.compile(r'^\d+(?:\.\d+){1,6}(?:\s|方法讲解)')
LECTURE_RE = re.compile(r'^\d+(?:\.\d+)*\s*方法讲解[｜|]')

TEXT_TAGS = {q('t'), qm('t')}


def shd_fill(rpr):
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd.get(q('fill')) if shd is not None else None


def in_tbl(el):
    cur = el.getparent()
    while cur is not None:
        if tag(cur) == 'tbl':
            return True
        cur = cur.getparent()
    return False


def text_stream(root):
    return ''.join((el.text or '') for el in root.iter() if el.tag in TEXT_TAGS)


def elem_counts(root):
    return {
        'w:p': len(root.findall('.//' + q('p'))),
        'w:tbl': len(root.findall('.//' + q('tbl'))),
        'w:r': len(root.findall('.//' + q('r'))),
        'w:t': len(root.findall('.//' + q('t'))),
        'm:r': len(root.findall('.//' + qm('r'))),
        'm:t': len(root.findall('.//' + qm('t'))),
        'm:oMath': len(root.findall('.//' + qm('oMath'))),
        'w:drawing': len(root.findall('.//' + q('drawing'))),
        'sectPr': len(root.findall('.//' + q('sectPr'))),
        'w:shd': len(root.findall('.//' + q('shd'))),
    }


def classify2(doc):
    body = doc.find(q('body'))
    els = list(body)
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    zone = {}
    state = 'other'
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        t = ptexts[i]
        if QBLOCK_HEAD_RE.match(t):
            state = 'q'
        elif LECTURE_RE.match(t):
            state = 'lecture'
        elif ENT_RE.match(t) and not HEAD_RE.match(t):
            state = 'entry'
        elif HEAD_RE.match(t):
            state = 'other'
        zone[i] = state

    strip = {'题号块': [], '芯片run': [], '并行解法': [], '答案值run': [], '答案值OMML': []}
    keep = {'条目号': 0, '第一子层': 0, '条目区需背run': 0, '条目区OMML': 0,
            '表内run': 0, '表内OMML': 0}
    viol = []
    notes = []
    chip_strip_ids = set()
    para_c9 = 0
    chip_total = 0          # 芯片出现数（计数工具口径：全体非黑名单【×】）
    chip_gray = 0           # 其中全灰（剥除对象，按出现数计）
    chip_not_gray = 0
    fill_para = {FILL_TITLE1: 0, FILL_TITLE2: 0, FILL_STEM: 0}
    tcpr_c9 = 0

    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        ppr = el.find(q('pPr'))
        if ppr is not None:
            pshd = ppr.find(q('shd'))
            if pshd is not None:
                f = pshd.get(q('fill'))
                if f in fill_para:
                    fill_para[f] += 1
                elif f == C9:
                    para_c9 += 1
                    viol.append('段级C9C9C9误挂 @body%d %r' % (i, ptexts[i][:30]))
        zn = zone[i]
        runs = list(el.iter(q('r')))
        lead_txt = ''
        lead_runs = []
        for r in runs:
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t == '':
                continue
            if shd_fill(r.find(q('rPr'))) == C9:
                lead_txt += t
                lead_runs.append(r)
            else:
                break
        lead_kind = None
        if lead_runs:
            if QBLOCK_HEAD_RE.match(ptexts[i]) and (LEAD_NUM_RE.fullmatch(lead_txt) or QNUM_LEGACY_RE.fullmatch(lead_txt)):
                lead_kind = '题号块'
            elif zn == 'entry' and not in_tbl(el) and LEAD_NUM_RE.fullmatch(lead_txt):
                lead_kind = '条目号'
            elif zn == 'entry' and not in_tbl(el) and LEAD_SUB_RE.fullmatch(lead_txt):
                lead_kind = '第一子层'
        lead_set = set(id(r) for r in lead_runs)
        if lead_kind == '题号块':
            strip['题号块'].extend(lead_runs)
        elif lead_kind in ('条目号', '第一子层'):
            keep[lead_kind] += 1
        # 芯片（字符蒙版）
        chars, mask, ranges = [], [], {}
        for k, r in enumerate(runs):
            sh = shd_fill(r.find(q('rPr'))) == C9
            s0 = len(chars)
            for x in r.findall(q('t')):
                s = x.text or ''
                chars.extend(s)
                mask.extend([sh] * len(s))
            ranges[k] = (s0, len(chars))
        fulltext = ''.join(chars)
        chip_runs = set()
        for mm in CHIP_RE.finditer(fulltext):
            lb = mm.group(0)
            if lb in CHIP_BLACKLIST or CHIP_BLACKLIST_RE.match(lb):
                continue
            chip_total += 1
            a, bb = mm.span()
            if not any(mask[a:bb]):
                chip_not_gray += 1
                continue
            if not all(mask[a:bb]):
                viol.append('芯片半挂灰 @body%d %r' % (i, lb))
                continue
            chip_gray += 1
            hit = [k for k, (s0, s1) in ranges.items() if s0 < bb and s1 > a]
            if zn == 'entry':
                if not all(ranges[k][0] >= a and ranges[k][1] <= bb for k in hit):
                    viol.append('条目区芯片与非芯片文字同run（MANUAL，不剥）@body%d %r'
                                % (i, fulltext[max(0, a - 8):bb + 8]))
                    continue
            chip_runs.update(hit)
        for k in sorted(chip_runs):
            if id(runs[k]) in lead_set:
                if lead_kind in ('条目号', '第一子层'):
                    notes.append('条目族lead内嵌芯片（保留优先不剥）@body%d' % i)
                # lead_kind=='题号块'：已随①剥除；lead_kind None 时下方照常入③
                if lead_kind in ('条目号', '第一子层', '题号块'):
                    continue
            strip['芯片run'].append(runs[k])
            chip_strip_ids.add(id(runs[k]))
        # run 级分类
        for k, r in enumerate(runs):
            rpr = r.find(q('rPr'))
            if shd_fill(rpr) != C9:
                continue
            if id(r) in lead_set and lead_kind in ('题号块', '条目号', '第一子层'):
                continue                         # lead 已在①剥除或W2保留
            if id(r) in chip_strip_ids:
                continue                         # 已在③
            if in_tbl(r):
                keep['表内run'] += 1
                continue
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t and MARK_RE.match(t):
                strip['并行解法'].append(r)
                continue
            if zn == 'entry':
                keep['条目区需背run'] += 1
                continue
            strip['答案值run'].append(r)
        # OMML 挂点
        for mel in el.iter():
            if etree.QName(mel).namespace != M:
                continue
            if tag(mel) in ('r', 'ctrlPr') and shd_fill(mel.find(q('rPr'))) == C9:
                if in_tbl(mel):
                    keep['表内OMML'] += 1
                elif zone.get(i) == 'entry':
                    keep['条目区OMML'] += 1
                else:
                    strip['答案值OMML'].append(mel)
    for tel in body.iter(q('tbl')):
        for shd in tel.iter(q('shd')):
            if shd.get(q('fill')) == C9:
                par = shd.getparent()
                if par is not None and tag(par) == 'tcPr':
                    tcpr_c9 += 1
    # 划分断言（A5）：run 级与 OMML 分别做不交并（命名空间区分——m:r 亦含 w:rPr）
    n_all_runs = 0
    for shd in doc.iter(q('shd')):
        if shd.get(q('fill')) != C9:
            continue
        par = shd.getparent()
        if par is None or tag(par) != 'rPr':
            continue
        gp = par.getparent()
        if gp is not None and etree.QName(gp).namespace == W and tag(gp) == 'r':
            n_all_runs += 1
    n_all_om = 0
    for mel in doc.iter():
        if etree.QName(mel).namespace != M:
            continue
        if tag(mel) in ('r', 'ctrlPr') and shd_fill(mel.find(q('rPr'))) == C9:
            n_all_om += 1
    n_strip_runs = len(strip['题号块']) + len(strip['芯片run']) + len(strip['并行解法']) + len(strip['答案值run'])
    n_keep_runs = keep['表内run'] + keep['条目区需背run']
    # lead 保留 run 直接重扫（精确，A5 分母用；与主环同口径：条目区＋非表内＋全式匹配）
    n_lead_keep_runs = 0
    zone2 = {}
    state = 'other'
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        t = ptexts[i]
        if QBLOCK_HEAD_RE.match(t):
            state = 'q'
        elif LECTURE_RE.match(t):
            state = 'lecture'
        elif ENT_RE.match(t) and not HEAD_RE.match(t):
            state = 'entry'
        elif HEAD_RE.match(t):
            state = 'other'
        zone2[i] = state
    for i, el in enumerate(els):
        if el.tag != q('p') or zone2[i] != 'entry':
            continue
        runs = list(el.iter(q('r')))
        lead_txt = ''
        lead_runs = []
        for r in runs:
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t == '':
                continue
            if shd_fill(r.find(q('rPr'))) == C9:
                lead_txt += t
                lead_runs.append(r)
            else:
                break
        if lead_runs and not in_tbl(el) and (LEAD_NUM_RE.fullmatch(lead_txt) or LEAD_SUB_RE.fullmatch(lead_txt)):
            n_lead_keep_runs += len(lead_runs)
    run_ok = (n_strip_runs + n_keep_runs + n_lead_keep_runs == n_all_runs)
    om_ok = (len(strip['答案值OMML']) + keep['表内OMML'] + keep['条目区OMML'] == n_all_om)
    partition_ok = run_ok and om_ok
    return {
        'strip': strip, 'keep': keep, 'viol': viol, 'notes': notes, 'para_c9': para_c9,
        'chip_total': chip_total, 'chip_gray': chip_gray, 'chip_not_gray': chip_not_gray,
        'fill_para': fill_para, 'tcpr_c9': tcpr_c9,
        'partition': {'all_runs': n_all_runs, 'strip_runs': n_strip_runs,
                      'keep_runs': n_keep_runs, 'lead_keep_runs': n_lead_keep_runs,
                      'run_ok': run_ok,
                      'all_om': n_all_om, 'strip_om': len(strip['答案值OMML']),
                      'keep_om': keep['表内OMML'] + keep['条目区OMML'], 'om_ok': om_ok,
                      'ok': partition_ok},
        'zone_of': zone, 'els': els, 'ptexts': ptexts,
    }


def strip_shd(el_holder):
    """删除 el_holder（w:r 或 m:r/m:ctrlPr）rPr 内的 w:shd；返回是否实际删除。"""
    rpr = el_holder.find(q('rPr'))
    if rpr is None:
        return False
    shd = rpr.find(q('shd'))
    if shd is None:
        return False
    rpr.remove(shd)
    return True


def para_fill_counts(doc):
    """段级四色直挂计数（白名单 W1 前后恒等断言用）。"""
    out = {FILL_TITLE1: 0, FILL_TITLE2: 0, FILL_STEM: 0, C9: 0}
    body = doc.find(q('body'))
    for p in body.iter(q('p')):
        ppr = p.find(q('pPr'))
        if ppr is None:
            continue
        shd = ppr.find(q('shd'))
        if shd is None:
            continue
        f = shd.get(q('fill'))
        if f in out:
            out[f] += 1
        else:
            out[f] = out.get(f, 0) + 1
    return out


def run_fill_counts(doc):
    """run级＋OMML 挂点 fill 分布。"""
    out = {}
    for r in doc.iter(q('r')):
        f = shd_fill(r.find(q('rPr')))
        if f:
            out[f] = out.get(f, 0) + 1
    om = {}
    for el in doc.iter():
        if etree.QName(el).namespace != M:
            continue
        if tag(el) in ('r', 'ctrlPr'):
            f = shd_fill(el.find(q('rPr')))
            if f:
                om[f] = om.get(f, 0) + 1
    return out, om


def process(path, out_path=None, dry_run=False, audit_only=False):
    z = zipfile.ZipFile(path)
    doc_bytes = z.read('word/document.xml')
    members = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    doc = etree.fromstring(doc_bytes)
    pre_stream = text_stream(doc)
    pre_counts = elem_counts(doc)
    pre_para_fill = para_fill_counts(doc)
    pre_run_fill, pre_om_fill = run_fill_counts(doc)

    cls = classify2(doc)
    n_strip = (len(cls['strip']['题号块']) + len(cls['strip']['芯片run'])
               + len(cls['strip']['并行解法']) + len(cls['strip']['答案值run'])
               + len(cls['strip']['答案值OMML']))

    report = {}
    report['file'] = os.path.basename(path)
    report['mode'] = 'audit-only' if audit_only else ('dry-run' if dry_run else 'apply')
    report['pre'] = {
        '题号块段数': len(cls['strip']['题号块']),
        '芯片出现数_全灰': cls['chip_gray'],
        '芯片涉及run数': len(cls['strip']['芯片run']),
        '芯片出现数_总计': cls['chip_total'],
        '芯片未挂灰': cls['chip_not_gray'],
        '并行解法run': len(cls['strip']['并行解法']),
        '答案值run': len(cls['strip']['答案值run']),
        '答案值OMML': len(cls['strip']['答案值OMML']),
        '保留_条目号段': cls['keep']['条目号'],
        '保留_第一子层段': cls['keep']['第一子层'],
        '保留_条目区需背run': cls['keep']['条目区需背run'],
        '保留_条目区OMML': cls['keep']['条目区OMML'],
        '保留_表内run': cls['keep']['表内run'],
        '保留_表内OMML': cls['keep']['表内OMML'],
        '保留_表内tcPr': cls['tcpr_c9'],
        '段级四色': dict(cls['fill_para']),
        '段级C9误挂': cls['para_c9'],
        'run级fill分布': dict(pre_run_fill),
        'OMMLfill分布': dict(pre_om_fill),
        '剥除总挂点': n_strip,
    }
    report['viol'] = cls['viol']
    report['notes'] = cls.get('notes', [])
    report['partition'] = cls['partition']

    if audit_only:
        report['post'] = '不适用件·零变化对照（减前＝减后）'
        return report, None

    # 模拟/执行剥除
    n_done = 0
    for r in cls['strip']['题号块'] + cls['strip']['芯片run'] + cls['strip']['并行解法'] + cls['strip']['答案值run']:
        if strip_shd(r):
            n_done += 1
    for mel in cls['strip']['答案值OMML']:
        if strip_shd(mel):
            n_done += 1

    post_stream = text_stream(doc)
    post_counts = elem_counts(doc)
    post_para_fill = para_fill_counts(doc)
    post_run_fill, post_om_fill = run_fill_counts(doc)

    checks = {
        'A1_剥除fill集合精确C9': n_done == n_strip,
        'A2a_段级四色恒等': post_para_fill == pre_para_fill,
        'A2b_白名单run级C9恒等': post_run_fill.get(C9, 0) == pre_run_fill.get(C9, 0) - (
            len(cls['strip']['题号块']) + len(cls['strip']['芯片run'])
            + len(cls['strip']['并行解法']) + len(cls['strip']['答案值run'])),
        'A2c_白名单OMML恒等': post_om_fill.get(C9, 0) == pre_om_fill.get(C9, 0) - len(cls['strip']['答案值OMML']),
        'A2d_他色run级零变化': {k: v for k, v in post_run_fill.items() if k != C9} == {
            k: v for k, v in pre_run_fill.items() if k != C9},
        'A3a_文字流全等': post_stream == pre_stream,
        'A3b_元素计数恒等': all(post_counts[k] == pre_counts[k] for k in post_counts if k != 'w:shd'),
        'A3c_shd减数等于剥除数': pre_counts['w:shd'] - post_counts['w:shd'] == n_done,
        'A4_无MANUAL违规': not cls['viol'],
        'A5_分区不交并': cls['partition']['ok'],
    }
    report['post'] = {
        'run级fill分布': dict(post_run_fill),
        'OMMLfill分布': dict(post_om_fill),
        '实剥挂点数': n_done,
        '减后残留_题号块run': 0,   # 由下方重扫填实测
    }
    # 减后残留实测（重扫分类——剥除后题号块/芯片/并行解法/题目侧答案值应全 0）
    resid = classify2(doc)
    report['post']['减后残留_题号块run'] = len(resid['strip']['题号块'])
    report['post']['减后残留_芯片run'] = len(resid['strip']['芯片run'])
    report['post']['减后残留_并行解法run'] = len(resid['strip']['并行解法'])
    report['post']['减后残留_答案值run'] = len(resid['strip']['答案值run'])
    report['post']['减后残留_答案值OMML'] = len(resid['strip']['答案值OMML'])
    report['post']['减后保留_条目区需背run'] = resid['keep']['条目区需背run']
    report['post']['减后保留_条目区OMML'] = resid['keep']['条目区OMML']
    report['post']['减后保留_表内run'] = resid['keep']['表内run']
    checks['T3_四类废止残留全0'] = all(report['post'][k] == 0 for k in (
        '减后残留_题号块run', '减后残留_芯片run', '减后残留_并行解法run',
        '减后残留_答案值run', '减后残留_答案值OMML'))
    report['checks'] = checks
    report['all_pass'] = all(checks.values())

    if not dry_run and report['all_pass'] and out_path:
        xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = out_path + '.tmp'
        zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
        for info, blob in members:
            ni = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            ni.compress_type = zipfile.ZIP_DEFLATED
            ni.external_attr = info.external_attr
            zo.writestr(ni, xml if info.filename == 'word/document.xml' else blob)
        zo.close()
        os.replace(tmp, out_path)
        report['written'] = out_path
    elif not dry_run and not report['all_pass']:
        report['written'] = None
        report['refuse'] = '作用域断言未全过——拒写（fail-closed）'
    return report, doc


def fmt_report(rep):
    L = []
    L.append('## %s（模式 %s）' % (rep['file'], rep['mode']))
    p = rep['pre']
    L.append('| 类别 | 减前计数 | 减后计数 | 差异备注 |')
    L.append('|---|---|---|---|')
    if rep['mode'] == 'audit-only':
        L.append('| 四类废止对象 | （不适用件不枚举剥除） | 同左 | 减前＝减后零变化对照 |')
        L.append('| run级fill分布 | %s | 同左 | 恒等 |' % p['run级fill分布'])
        L.append('| OMML fill分布 | %s | 同左 | 恒等 |' % p['OMMLfill分布'])
        L.append('| 段级四色 | %s | 同左 | 恒等 |' % p['段级四色'])
        return '\n'.join(L)
    po = rep['post']
    L.append('| ①题号难度块底纹（run） | %d | 0 | 实测残留 %d |' % (p['题号块段数'], po['减后残留_题号块run']))
    L.append('| ③块标签芯片底纹（出现数/涉及run） | %d/%d | 0 | 实测残留run %d；未挂灰芯片 %d（登记） |'
             % (p['芯片出现数_全灰'], p['芯片涉及run数'], po['减后残留_芯片run'], p['芯片未挂灰']))
    L.append('| ④并行解法标记底纹（run） | %d | 0 | 实测残留 %d |' % (p['并行解法run'], po['减后残留_并行解法run']))
    L.append('| ②题目侧答案值灰底 run级 | %d | 0 | 实测残留 %d |' % (p['答案值run'], po['减后残留_答案值run']))
    L.append('| ②题目侧答案值灰底 OMML挂点 | %d | 0 | 实测残留 %d |' % (p['答案值OMML'], po['减后残留_答案值OMML']))
    L.append('| 保留·标题整行底纹 ADC2DA段 | %d | %d | 恒等 |' % (p['段级四色']['ADC2DA'], p['段级四色']['ADC2DA']))
    L.append('| 保留·标题整行底纹 C6D4E3段 | %d | %d | 恒等 |' % (p['段级四色']['C6D4E3'], p['段级四色']['C6D4E3']))
    L.append('| 保留·题干底纹 E0E0E0段 | %d | %d | 恒等 |' % (p['段级四色']['E0E0E0'], p['段级四色']['E0E0E0']))
    L.append('| 保留·条目号段/第一子层段 | %d/%d | 同左 | 恒等 |' % (p['保留_条目号段'], p['保留_第一子层段']))
    L.append('| 保留·讲部条目区需背 run/OMML | %d/%d | %d/%d | 恒等（甲案保留） |'
             % (p['保留_条目区需背run'], p['保留_条目区OMML'], po['减后保留_条目区需背run'], po['减后保留_条目区OMML']))
    L.append('| 保留·表内 run/OMML/tcPr | %d/%d/%d | 同左 | 恒等 |' % (p['保留_表内run'], p['保留_表内OMML'], p['保留_表内tcPr']))
    L.append('| C9C9C9 run级挂点总 | %d | %d | 减数=%d |'
             % (p['run级fill分布'].get(C9, 0), po['run级fill分布'].get(C9, 0),
                p['run级fill分布'].get(C9, 0) - po['run级fill分布'].get(C9, 0)))
    L.append('| C9C9C9 OMML挂点总 | %d | %d | 减数=%d |'
             % (p['OMMLfill分布'].get(C9, 0), po['OMMLfill分布'].get(C9, 0),
                p['OMMLfill分布'].get(C9, 0) - po['OMMLfill分布'].get(C9, 0)))
    L.append('| 段级C9误挂 | %d | — | 期望0，有则违规登记不剥 |' % p['段级C9误挂'])
    L.append('')
    ck = rep['checks']
    L.append('作用域断言：' + '；'.join('%s=%s' % (k, '✓' if v else '✗✗✗') for k, v in ck.items()))
    if rep['viol']:
        L.append('违规/MANUAL登记：' + '；'.join(rep['viol'][:8]))
    if rep.get('notes'):
        L.append('登记注记（非阻断）：' + '；'.join(rep['notes'][:8]))
    L.append('分区划分（A5）：%s' % json.dumps(rep['partition'], ensure_ascii=False))
    L.append('总判定：%s' % ('PASS（可执行）' if rep['all_pass'] else 'CHECK（禁执行）'))
    return '\n'.join(L)


def main():
    args, opts, kv, i = [], {}, {}, 0
    argv = sys.argv[1:]
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            if '=' in a:
                k, v = a[2:].split('=', 1)
                kv[k] = v
            elif a == '--report' and i + 1 < len(argv):
                kv['report'] = argv[i + 1]
                i += 1
            else:
                opts[a] = True
        else:
            args.append(a)
        i += 1
    if not args:
        print(__doc__)
        sys.exit(1)
    src = args[0]
    dry = '--dry-run' in opts
    audit = '--audit-only' in opts
    out_path = None if (dry or audit) else (args[1] if len(args) > 1 else None)
    if not (dry or audit) and not out_path:
        print('执行模式须给 <out.docx>；或加 --dry-run/--audit-only')
        sys.exit(1)
    rep_path = kv.get('report')
    if rep_path:
        rp = os.path.abspath(rep_path)
        ap = os.path.abspath(src)
        if os.path.normcase(rp) == os.path.normcase(ap) or rp.lower().endswith(PRODUCT_EXT):
            sys.stderr.write('拒绝：报告路径误用（防写进成品）——报告请用 .txt/.md\n')
            sys.exit(2)
    rep, _ = process(src, out_path, dry_run=dry, audit_only=audit)
    txt = fmt_report(rep)
    if rep_path:
        d = os.path.dirname(os.path.abspath(rep_path))
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        open(rep_path, 'w', encoding='utf-8').write(txt + '\n')
    print(txt)
    if rep['mode'] != 'audit-only' and not rep.get('all_pass'):
        sys.exit(3)


if __name__ == '__main__':
    main()
