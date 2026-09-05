# -*- coding: utf-8 -*-
"""答案值分型改标.py — 2026-09-01 A'改制轮（T4·工具债⑤，口径E／公共规则§7答案值标记·分型标记款）。
【答案】标签后答案值与需背内容（知识清单填空/讲部挖空等既有 C7C7C7 灰底标记）分型改标
（2026-09-02 A''成品轮改造——深蓝 #1F4E79 全体系废止、统一灰底制）：
  文字型（纯文字 run）＝C7C7C7 灰底＋剥深蓝；公式型（值内含 OMML）＝挂灰（OMML挂法：m:r/ctrlPr
  的 w:rPr 内 w:shd、分数整块覆盖——同知识清单填空标记方案）＋剥深蓝；混合型整值按公式型；多值各标各的（；;分隔＋子问 (N) 前缀边界）；值间分隔符与缝隙剥灰防连片；
  答案跨段续值段（【答案】行后文字空白-only 含公式的段落）并入末值处理；
  与【答案】/【知识点】芯片间保留空格（缺则补一个半角空格并登记——唯一授权文字增量）；
  芯片【×】黑字不变（chip/题号/条目号/第一子层/并行解法标记 run 的 text·shd·color 指纹前后恒等断言）。
  需背内容同款分型：值区以外的灰底标记按「连续灰底簇」清点——簇内含灰 OMML 即公式型同挂灰（A''统一），
  纯文字簇保灰底并剥深蓝；导航表头（tcPr 级 C7C7C7 单元格）内 run 不触碰；段首题号/条目号/（N）
  锚 run 不入簇。
  恒等式＝文字型灰底run数＋公式型挂灰oMath值数＝答案值数（值级计数，口径同 工具/块标签芯片.py 的
  「答案值文字run」按值计；文字型 rPr 相同且相邻的 run 拼回单 run，斜体变量等 rPr 差异依法保留
  不硬并、多 run 值登记；公式型每值整值挂灰）；写盘后独立复核道重算恒等式。
  全局断言（A''）：处理后全文 w:color val=1F4E79 挂点＝0（深蓝废止——run级与OMML级双扫）。
  幂等：二跑零改动；块边界参照 工具/extract_structure.py（题号兼容全局 N．与层级制 节号-序号．）；
  不动公式内容与字体（Cambria Math/PUA 不触碰——OMML定论）。
 2026-09-04 减法口径改造（选必1⓪复合修复轮子步2，工具债案6——附则《讲练件底纹减法》甲案）：
 讲练件族（文件名含 讲练件/简单卷/中档卷/冲刺卷/实验卷）题目侧答案值灰底已废止——本工具
 对该族拒绝执行改标（防回挂；讲部条目区需背灰底为甲案保留项，由 底纹去除器.py/六类底纹计数.py
 的条目区口径守护）；--verify 对该族切换为减法终态断言＝【答案】值区灰底/深蓝逐值＝0。
用法: python 答案值分型改标.py <docx...> [--report 报告.txt] [--dry-run] [--verify] [--no-recite] [--detail N]
  --verify 只读复核不改写；--no-recite 跳过需背簇（只处理【答案】值）；--detail N 值明细条数（默认25）。"""
import sys, io, zipfile, os, re, time, argparse, difflib
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

JLP_RE = re.compile(r'讲练件|简单卷|中档卷|冲刺卷|实验卷')   # 2026-09-04 减法口径：讲练件族禁改标

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname if isinstance(e.tag, str) else '?'

FILL = 'C7C7C7'
BLUE = '1F4E79'
FILL_TITLE1 = 'ADC2DA'
FILL_TITLE2 = 'C6D4E3'
NEXT_LB = re.compile(r'【[^】]{1,12}】')
CHIP_RE = re.compile(r'【[^】]{1,16}】')
CHIP_BLACKLIST = ('【易错】', '【了解】')
CHIP_BLACKLIST_RE = re.compile(r'^【典例[^】]*】$')
MARK_RUN_RE = re.compile(r'^[\s]*(?:［?(?:方法|解法)[一二三四五六七八九十]{1,3}］?|另解)[：:]?$')
LEADNUM_RE = re.compile(r'^(?:\d+(?:\.\d+)*-\d+|\d+)．$|^（\d+）$')
QBLOCK_HEAD_RE = re.compile(
    r'^(?:\d+(?:\.\d+)*-\d+|\d+)．（(?:(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%))?·卡壳看答案'
    r'|衔接必会·卡壳看答案|(?:简单|中档|难))')
QNUM_ANY_RE = re.compile(r'^(?:\d+(?:\.\d+)*-\d+|\d+)．')
LECTURE_RE = re.compile(r'^\d+(?:\.\d+)*[\s　]*方法讲解[｜|]')
CHAP_RE = re.compile(r'^第\d+章')
MERGED_SEC_RE = re.compile(r'（第\d+[—–-]\d+题）')
HEADNUM_RE = re.compile(r'^\d+(?:\.\d+)+[\s　]+\S')
LABELS = ('【答案】', '【知识点】', '【分析】', '【详解】', '【点睛】', '【编注】',
          '【大招指引】', '【题后反思】', '【温馨提醒】')
# 子问边界：(N)/（N）前缀、前面是空白/；（值内中文紧邻括号不切——无空白即无边界）
BN_BOUND = re.compile(r'(?<=[\s　；;])[(（]\d{1,2}[)）]')
AFTER_COLOR = {'spacing', 'w', 'kern', 'position', 'sz', 'szCs', 'highlight', 'u', 'effect',
               'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs', 'em', 'lang',
               'eastAsianLayout', 'specVanish', 'oMath'}
AFTER_SHD = {'fitText', 'vertAlign', 'rtl', 'cs', 'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath'}


# ---------------- 基础件 ----------------
def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def para_fill(p):
    if p is None or p.tag != q('p'):
        return None
    ppr = p.find(q('pPr'))
    shd = ppr.find(q('shd')) if ppr is not None else None
    return shd.get(q('fill')) if shd is not None else None


def heading_kind(el, text, first_nonempty):
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
    """题块边界（参照 工具/extract_structure.py；同 工具/解析块浅底挂载.py 口径）。"""
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
                if els[j].tag == q('tbl'):
                    j += 1
                    continue
                if els[j].tag != q('p'):
                    break
                if QBLOCK_HEAD_RE.match(ptexts[j]) or heading_kind(els[j], ptexts[j], None):
                    break
                j += 1
            blocks.append((i, j))
            i = j
        elif candidate:
            j = i + 1
            while j < n and els[j].tag == q('p') and not QNUM_ANY_RE.match(ptexts[j]) \
                    and heading_kind(els[j], ptexts[j], None) is None:
                j += 1
            if any(lead_label(ptexts[k]) == '【答案】' for k in range(i, j) if els[k].tag == q('p')):
                blocks.append((i, j))
                i = j
            else:
                i += 1
        else:
            i += 1
    return blocks


def items(p):
    """段内行级子项 [(el, kind, 文本)]：w:r（含 hyperlink 内）/ m:oMath / m:oMathPara。"""
    out = []
    for c in p:
        tg = tag(c)
        if tg == 'r':
            out.append((c, 'r', ''.join(t.text or '' for t in c.findall(q('t')))))
        elif tg == 'hyperlink':
            for r in c.findall(q('r')):
                out.append((r, 'r', ''.join(t.text or '' for t in r.findall(q('t')))))
        elif tg in ('oMath', 'oMathPara'):
            out.append((c, 'om', ''.join(t.text or '' for t in c.iter(mq('t')))))
    return out


def split_run_at(r, off):
    """把 run 在 w:t 合文本 off 处拆两 run（复制 rPr；支持多 w:t；含图形/域等屏障返回 None）。"""
    if any(tag(c) in ('drawing', 'pict', 'br', 'object', 'fldChar') for c in r):
        return None
    ts = r.findall(q('t'))
    acc = 0
    for k, t in enumerate(ts):
        s = t.text or ''
        if acc <= off < acc + len(s):
            rel = off - acc
            if rel == 0:
                return None
            nr = etree.fromstring(etree.tostring(r))
            ts[k].text = s[:rel]
            nr.findall(q('t'))[k].text = s[rel:]
            for extra in ts[k + 1:]:
                extra.getparent().remove(extra)
            for extra in nr.findall(q('t'))[:k]:
                extra.getparent().remove(extra)
            for t2 in ts + nr.findall(q('t')):
                t2.set(XMLSPACE, 'preserve')
            r.addnext(nr)
            return nr
        acc += len(s)
    return None


def isolate_runs(p, s, e, warn):
    """隔离 w:t 文本流 [s,e) 的 run（边界拆 run）；坐标基于 w:t 流（m:t 不占位）。
    口径同 工具/块标签芯片.py。"""
    out = []
    off = 0
    for t in list(p.iter(q('t'))):
        r = t.getparent()
        if tag(r) != 'r':
            continue
        txt = t.text or ''
        a, b = off, off + len(txt)
        off = b
        if b <= s or a >= e:
            continue
        if a < s:
            nr = split_run_at(r, s - a)
            if nr is None:
                warn.append('拆run屏障@[%d,%d)' % (s, e))
                continue
            return isolate_runs(p, s, e, warn)
        if b > e:
            nr = split_run_at(r, e - a)
            if nr is None:
                warn.append('拆run屏障@[%d,%d)' % (s, e))
                continue
            return isolate_runs(p, s, e, warn)
        out.append(r)
    return out


def rpr_of(el):
    """取/建 w:rPr：m:r 内须排在 m:rPr 之后（OMML定论——w:rPr 为 m:rPr 后首元素）。"""
    rpr = el.find(q('rPr'))
    if rpr is not None:
        return rpr
    rpr = etree.Element(q('rPr'))
    kids = list(el)
    if kids and etree.QName(kids[0]).namespace == M and tag(kids[0]) == 'rPr':
        kids[0].addnext(rpr)
    else:
        el.insert(0, rpr)
    return rpr


def ensure_shd(rpr, fill=FILL):
    shd = rpr.find(q('shd'))
    if shd is None:
        shd = etree.Element(q('shd'))
        pos = len(list(rpr))
        for k, c in enumerate(list(rpr)):
            if tag(c) in AFTER_SHD:
                pos = k
                break
        rpr.insert(pos, shd)
        shd.set(q('val'), 'clear')
        shd.set(q('color'), 'auto')
        shd.set(q('fill'), fill)
        return True
    if shd.get(q('fill')) != fill:
        shd.set(q('val'), 'clear')
        shd.set(q('color'), 'auto')
        shd.set(q('fill'), fill)
        return True
    return False


def strip_shd(rpr):
    shd = rpr.find(q('shd'))
    if shd is not None:
        rpr.remove(shd)
        return True
    return False


def ensure_color(rpr, val=BLUE):
    c = rpr.find(q('color'))
    if c is None:
        c = etree.Element(q('color'))
        pos = len(list(rpr))
        for k, ch in enumerate(list(rpr)):
            if tag(ch) in AFTER_COLOR:
                pos = k
                break
        rpr.insert(pos, c)
        c.set(q('val'), val)
        return True
    if c.get(q('val')) != val:
        c.set(q('val'), val)
        return True
    return False


def strip_blue(rpr):
    """A''深蓝废止：删除 w:color val=1F4E79（其他颜色值不碰）。返回是否删除。"""
    if rpr is None:
        return False
    c = rpr.find(q('color'))
    if c is not None and c.get(q('val')) == BLUE:
        rpr.remove(c)
        return True
    return False


def om_hosts(om):
    for e in om.iter():
        if etree.QName(e).namespace != M:
            continue
        t2 = tag(e)
        if t2 in ('r', 'ctrlPr'):
            yield e, t2


def run_is_blue(r):
    rpr = r.find(q('rPr'))
    if rpr is None:
        return False
    c = rpr.find(q('color'))
    return c is not None and c.get(q('val')) == BLUE


def om_is_blue(om):
    for host, _ in om_hosts(om):
        if run_is_blue(host):
            return True
    return False


def om_is_gray(om):
    for host, _ in om_hosts(om):
        rpr = host.find(q('rPr'))
        shd = rpr.find(q('shd')) if rpr is not None else None
        if shd is not None and shd.get(q('fill')) == FILL:
            return True
    return False


def treat_omath(om, stats):
    """A''统一灰底（2026-09-02）：公式整块挂 C7C7C7（m:r/ctrlPr 的 w:rPr，分数整块覆盖——OMML挂法）＋剥深蓝。"""
    for host, kind in om_hosts(om):
        rpr = rpr_of(host)
        if ensure_shd(rpr):
            stats['挂shd_' + ('mr' if kind == 'r' else 'ctrl')] += 1
        if strip_blue(rpr):
            stats['剥深蓝_' + ('mr' if kind == 'r' else 'ctrl')] += 1


def merge_runs(runs, stats):
    """rPr 完全相同且相邻的纯文本 run 拼回单 run（只动 run 边界不动文字流）。"""
    if len(runs) < 2:
        return runs
    sers = [etree.tostring(r.find(q('rPr'))) if r.find(q('rPr')) is not None else b'' for r in runs]
    if len(set(sers)) != 1:
        stats['值rPr不一致未并'] += 1
        return runs
    if not all(runs[k].getnext() is runs[k + 1] for k in range(len(runs) - 1)):
        stats['值不相邻未并'] += 1
        return runs
    t0 = runs[0].findall(q('t'))[-1]
    for r in runs[1:]:
        for t in r.findall(q('t')):
            t0.text = (t0.text or '') + (t.text or '')
        r.getparent().remove(r)
    t0.set(XMLSPACE, 'preserve')
    stats['合并run组'] += 1
    return runs[:1]


# ---------------- 值区解析 ----------------
def parse_answer_para(p):
    """【答案】行值区解析。返回 (pieces, chip_end, region_end)；piece＝[ps,pe) w:t 坐标＋公式元素表。
    分隔＝；;＋子问 (N) 边界；坐标基于 w:t 流（公式 m:t 不占位、按文档序夹点归属所在值）。"""
    om_events = []
    wt_off = 0
    for el, kind, txt in items(p):
        if kind == 'r':
            wt_off += len(txt)
        else:
            om_events.append((wt_off, el))
    full = ptext(p)
    ci = full.find('【答案】')
    if ci < 0:
        return None, -1, -1
    chip_end = ci + len('【答案】')
    m = NEXT_LB.search(full, chip_end)
    region_end = m.start() if m else len(full)
    pieces = []
    cur = [chip_end, chip_end]
    cur_oms = []
    oi = [0]

    def take_oms(pos):
        got = []
        while oi[0] < len(om_events) and om_events[oi[0]][0] <= pos:
            o, el = om_events[oi[0]]
            if chip_end <= o <= region_end:
                got.append(el)
            oi[0] += 1
        return got

    i = chip_end
    while i < region_end:
        cur_oms += take_oms(i)
        ch = full[i]
        if ch in '；;':
            pieces.append([cur[0], cur[1], cur_oms])
            cur = [i + 1, i + 1]
            cur_oms = []
            i += 1
            continue
        if BN_BOUND.match(full, i) and cur[1] > cur[0]:
            pieces.append([cur[0], cur[1], cur_oms])
            cur = [i, i]
            cur_oms = []
            continue
        cur[1] = i + 1
        i += 1
    cur_oms += take_oms(region_end)
    pieces.append([cur[0], cur[1], cur_oms])
    out = []
    for ps, pe, oms in pieces:
        while ps < pe and full[ps] in ' 　':
            ps += 1
        while pe > ps and full[pe - 1] in ' 　':
            pe -= 1
        out.append([ps, pe, oms])
    return out, chip_end, region_end


def find_continuations(els, ptexts, ans_idx, block_end):
    """【答案】行后的跨段续值段：文字空白-only 且含 oMath；至标签/题号/标题/实质文字段止。"""
    cont = []
    k = ans_idx + 1
    while k < block_end:
        el = els[k]
        if el.tag != q('p'):
            break
        t = ptexts[k]
        if lead_label(t) or QNUM_ANY_RE.match(t.lstrip()) or heading_kind(el, t, None):
            break
        if t.strip():
            break
        if not [c for c in el if tag(c) in ('oMath', 'oMathPara')]:
            break
        cont.append(k)
        k += 1
    return cont


def insert_space_at(p, pos, stats):
    """w:t 流 pos 处补一个半角空格（芯片与值/下一标签间防连片）。
    pos 恰为公式夹点（值以 oMath 开头）时在其前插独立空格 run（不带底纹不带色）。"""
    off = 0
    for el, kind, txt in items(p):
        if kind == 'r':
            off += len(txt)
        elif off == pos:
            nr = etree.Element(q('r'))
            t = etree.SubElement(nr, q('t'))
            t.text = ' '
            t.set(XMLSPACE, 'preserve')
            el.addprevious(nr)
            stats['补空格'] += 1
            return True
    off = 0
    for t in p.iter(q('t')):
        r = t.getparent()
        if tag(r) != 'r':
            continue
        s = t.text or ''
        if off <= pos < off + len(s):
            t.text = s[:pos - off] + ' ' + s[pos - off:]
            t.set(XMLSPACE, 'preserve')
            stats['补空格'] += 1
            return True
        off += len(s)
    return False


# ---------------- 快照与断言件 ----------------
def snapshot_text(doc):
    return ''.join(t.text or '' for t in doc.iter(q('t')))


def snapshot_chips(doc):
    fps = []
    for r in doc.iter(q('r')):
        txt = ''.join(t.text or '' for t in r.findall(q('t')))
        if not txt:
            continue
        if CHIP_RE.fullmatch(txt) or MARK_RUN_RE.match(txt) or LEADNUM_RE.match(txt):
            rpr = r.find(q('rPr'))
            shd = rpr.find(q('shd')) if rpr is not None else None
            col = rpr.find(q('color')) if rpr is not None else None
            fps.append((txt, shd.get(q('fill')) if shd is not None else None,
                        col.get(q('val')) if col is not None else None))
    return Counter(fps)


def count_omml_gray(doc):
    n = 0
    for rpr in doc.iter(q('rPr')):
        par = rpr.getparent()
        if par is None or etree.QName(par).namespace != M or tag(par) not in ('r', 'ctrlPr'):
            continue
        shd = rpr.find(q('shd'))
        if shd is not None and shd.get(q('fill')) == FILL:
            n += 1
    return n


def count_omml_blue(doc):
    """A''深蓝废止断言用：OMML 宿主 rPr 内 w:color val=1F4E79 挂点数（期望 0）。"""
    n = 0
    for rpr in doc.iter(q('rPr')):
        par = rpr.getparent()
        if par is None or etree.QName(par).namespace != M or tag(par) not in ('r', 'ctrlPr'):
            continue
        c = rpr.find(q('color'))
        if c is not None and c.get(q('val')) == BLUE:
            n += 1
    return n


def runs_in_span(p, s, e):
    """只读：w:t 流 [s,e) 覆盖的 run——(完全落入列表, 部分重叠数)。"""
    full_in, partial = [], 0
    off = 0
    for t in p.iter(q('t')):
        r = t.getparent()
        if tag(r) != 'r':
            continue
        txt = t.text or ''
        a, b = off, off + len(txt)
        off = b
        if b <= s or a >= e:
            continue
        if a >= s and b <= e:
            full_in.append(r)
        else:
            partial += 1
    return full_in, partial


# ---------------- 主流程 ----------------
def process(path, args):
    basename = os.path.basename(path)
    z = zipfile.ZipFile(path)
    parts = {nm: z.read(nm) for nm in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    els = list(body)
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    first_ne = next((els[i] for i, el in enumerate(els)
                     if el.tag == q('p') and ptexts[i].strip()), None)
    blocks = scan_blocks(els, ptexts)
    stats = Counter()
    warn = []
    vals = []
    skip_paras = set()
    gray_om_before = count_omml_gray(doc)

    for bi, (s, e) in enumerate(blocks):
        for k in range(s, e):
            if els[k].tag != q('p') or lead_label(ptexts[k]) != '【答案】':
                continue
            p = els[k]
            skip_paras.add(k)
            # —— 防连片空格（先补后切，坐标以补后重算为准） ——
            for _ in range(4):
                full = ptext(p)
                ci = full.find('【答案】') + len('【答案】')
                m2 = NEXT_LB.search(full, ci)
                if ci < len(full) and full[ci] not in ' 　':
                    if insert_space_at(p, ci, stats):
                        ptexts[k] = ptext(p)
                        continue
                if m2 and ci < m2.start() and full[m2.start() - 1] not in ' 　':
                    if insert_space_at(p, m2.start(), stats):
                        ptexts[k] = ptext(p)
                        continue
                break
            pieces, chip_end, region_end = parse_answer_para(p)
            if pieces is None:
                continue
            for ci2 in find_continuations(els, ptexts, k, e):
                skip_paras.add(ci2)
                for c in els[ci2]:
                    if tag(c) in ('oMath', 'oMathPara'):
                        pieces[-1][2].append(c)
            live = []
            for pc in pieces:
                has_txt = pc[1] > pc[0] and ptexts[k][pc[0]:pc[1]].strip() != ''
                if has_txt or pc[2]:
                    live.append(pc)
            for vi, (ps, pe, oms) in enumerate(live):
                is_formula = bool(oms)
                preview = (ptexts[k][ps:pe] if pe > ps else '')[:14] or '<公式×%d>' % len(oms)
                if is_formula:
                    if pe > ps:
                        for r in isolate_runs(p, ps, pe, warn):
                            rpr = rpr_of(r)
                            if ensure_shd(rpr):
                                stats['挂shd_run'] += 1
                            if strip_blue(rpr):
                                stats['剥深蓝_run'] += 1
                    for om in oms:
                        treat_omath(om, stats)
                    stats['公式型值'] += 1
                    vals.append((bi, vi, '公式', preview))
                else:
                    rs = isolate_runs(p, ps, pe, warn)
                    for r in rs:
                        rpr = rpr_of(r)
                        ensure_shd(rpr)
                        strip_blue(rpr)
                    stats['物理灰run'] += len(rs)
                    if len(rs) > 1:
                        stats['多run值'] += 1
                    rs = merge_runs(rs, stats)
                    stats['文字型值'] += 1
                    vals.append((bi, vi, '文字', preview))
            if live:
                gaps = []
                prev = chip_end
                for pc in live:
                    gaps.append((prev, pc[0]))
                    prev = pc[1]
                gaps.append((prev, region_end))
                for gs, ge in gaps:
                    if ge > gs:
                        for r in isolate_runs(p, gs, ge, warn):
                            if strip_shd(rpr_of(r)):
                                stats['剥shd_分隔'] += 1

    # —— 需背簇（值区以外；含表格内填空，导航表头 tcPr 级 C7C7C7 单元格跳过） ——
    recite = Counter()
    if not args.no_recite:
        body_idx = {id(el): i for i, el in enumerate(els)}
        for p in doc.iter(q('p')):
            if id(p) in body_idx and body_idx[id(p)] in skip_paras:
                continue
            cell = p.getparent()
            in_hdr = False
            if cell is not None and tag(cell) == 'tc':
                tcpr = cell.find(q('tcPr'))
                shd = tcpr.find(q('shd')) if tcpr is not None else None
                in_hdr = shd is not None and shd.get(q('fill')) == FILL
            if in_hdr:
                continue
            its = items(p)
            if not its:
                continue
            lead_excl = set()
            lead_txt = ''
            for el, kind, txt in its:
                if kind != 'r':
                    break
                if not txt:
                    continue
                rpr = el.find(q('rPr'))
                shd = rpr.find(q('shd')) if rpr is not None else None
                if shd is not None and shd.get(q('fill')) == FILL:
                    lead_txt += txt
                    lead_excl.add(id(el))
                else:
                    break
            if lead_txt and not LEADNUM_RE.match(lead_txt):
                lead_excl.clear()
            # —— 前导锚号保护（2026-09-01 E2补丁·缺陷修复）——
            # 旧逻辑要求整段前导灰串恰为锚全式；「（1）【定理】正文…」（锚号+芯片+灰正文，I1实测3处）
            # 与「（N）+灰正文」形态漏保护→锚号run入簇被ensure深蓝（指纹断言←≠、退出码1）。
            # 修正＝首非空run恰为锚号（LEADNUM_RE）且挂灰时，锚号与其后紧邻灰芯片run一律不入簇（黑字恒定）。
            _lead_runs = [it for it in its if it[1] == 'r' and it[2]]
            if _lead_runs:
                _el0, _k0, _t0 = _lead_runs[0]
                _rpr0 = _el0.find(q('rPr'))
                _shd0 = _rpr0.find(q('shd')) if _rpr0 is not None else None
                if _shd0 is not None and _shd0.get(q('fill')) == FILL and LEADNUM_RE.match(_t0):
                    lead_excl.add(id(_el0))
                    for _elx, _kx, _tx in _lead_runs[1:]:
                        if CHIP_RE.fullmatch(_tx) and _tx not in CHIP_BLACKLIST \
                                and not CHIP_BLACKLIST_RE.match(_tx):
                            _rprx = _elx.find(q('rPr'))
                            _shdx = _rprx.find(q('shd')) if _rprx is not None else None
                            if _shdx is not None and _shdx.get(q('fill')) == FILL:
                                lead_excl.add(id(_elx))
                            else:
                                break
                        else:
                            break
            k = 0
            while k < len(its):
                el, kind, txt = its[k]
                if kind == 'r':
                    rpr = el.find(q('rPr'))
                    shd = rpr.find(q('shd')) if rpr is not None else None
                    gray = shd is not None and shd.get(q('fill')) == FILL
                    if not gray and not run_is_blue(el):
                        k += 1
                        continue
                    chip = CHIP_RE.fullmatch(txt) and txt not in CHIP_BLACKLIST \
                        and not CHIP_BLACKLIST_RE.match(txt)
                    if chip or MARK_RUN_RE.match(txt) or id(el) in lead_excl:
                        k += 1
                        continue
                else:  # 公式项：灰/蓝 OMML 可独立成簇起点（A''：纯蓝深蓝标记同入簇转灰）
                    if not om_is_gray(el) and not om_is_blue(el):
                        k += 1
                        continue
                j = k
                cluster = []
                has_om = False
                while j < len(its):
                    el2, k2, t2 = its[j]
                    if k2 == 'r':
                        rpr2 = el2.find(q('rPr'))
                        shd2 = rpr2.find(q('shd')) if rpr2 is not None else None
                        ch2 = CHIP_RE.fullmatch(t2) and t2 not in CHIP_BLACKLIST \
                            and not CHIP_BLACKLIST_RE.match(t2)
                        if ch2 or MARK_RUN_RE.match(t2) or id(el2) in lead_excl:
                            break
                        if (shd2 is None or shd2.get(q('fill')) != FILL) and not run_is_blue(el2):
                            break
                        cluster.append((el2, 'r'))
                    else:
                        if not om_is_gray(el2) and not om_is_blue(el2):
                            break
                        cluster.append((el2, 'om'))
                        has_om = True
                    j += 1
                recite['簇数'] += 1
                if has_om:
                    recite['公式簇'] += 1
                    for el3, k3 in cluster:
                        if k3 == 'r':
                            rpr3 = rpr_of(el3)
                            if ensure_shd(rpr3):
                                stats['需背挂shd_run'] += 1
                            if strip_blue(rpr3):
                                stats['需背剥深蓝_run'] += 1
                        else:
                            treat_omath(el3, stats)
                else:
                    recite['文字簇'] += 1
                    for el3, k3 in cluster:
                        rpr3 = rpr_of(el3)
                        if ensure_shd(rpr3):
                            stats['需背挂shd_run'] += 1
                        if strip_blue(rpr3):
                            stats['需背剥深蓝_run'] += 1
                k = j

    # A''全文兜底：簇外/值区外散点深蓝一律剥蓝（深蓝全体系废止；散点run按需背标记语境转灰——
    # 保守口径：孤立蓝run若无灰底语境，仅剥蓝不挂灰（避免误扩标记面），登记计数供人工复核）
    blue_orphan_run = 0
    if not args.dry_run:
        for r in doc.iter(q('r')):
            par = r.getparent()
            if par is None or tag(par) != 'p':
                continue
            rpr = r.find(q('rPr'))
            if rpr is not None and strip_blue(rpr):
                ensure_shd(rpr)          # A'蓝字即标记本体——换轴转灰底（非扩面）
                blue_orphan_run += 1
    gray_om_after = count_omml_gray(doc)
    n_vals = stats['文字型值'] + stats['公式型值']
    lines = ['◆ %s' % basename]
    lines.append('  题块 %d｜答案值数 %d＝文字型 %d（物理灰run %d）＋公式型 %d%s'
                 % (len(blocks), n_vals, stats['文字型值'], stats['物理灰run'],
                    stats['公式型值'], '，dry-run 未写回' if args.dry_run else ''))
    if not args.no_recite:
        lines.append('  需背簇 %d＝文字簇 %d＋公式簇 %d（A款统一灰底：公式簇挂灰OMML）'
                     % (recite['簇数'], recite['文字簇'], recite['公式簇']))
    lines.append('  恒等式：文字型灰底run数 %d＋公式型挂灰oMath值数 %d＝答案值数 %d %s'
                 % (stats['文字型值'], stats['公式型值'], n_vals,
                    '✓' if n_vals == stats['文字型值'] + stats['公式型值'] else '←≠'))
    lines.append('  run口径登记：文字型物理灰run %d（多run值 %d——斜体变量等 rPr 差异依法保留不硬并；'
                 '计数口径同 块标签芯片.py 按值计）｜合并run组 %d（未并 %d）'
                 % (stats['物理灰run'], stats['多run值'], stats['合并run组'],
                    stats['值rPr不一致未并'] + stats['值不相邻未并']))
    lines.append('  A2改标计数：run挂灰 %d＋m:r挂灰 %d＋ctrlPr挂灰 %d＋需背run挂灰 %d｜'
                 'run剥深蓝 %d＋m:r剥深蓝 %d＋ctrlPr剥深蓝 %d＋需背run剥深蓝 %d＋分隔剥灰 %d｜合并run组 %d（未并 %d）｜补空格 %d'
                 % (stats['挂shd_run'], stats['挂shd_mr'], stats['挂shd_ctrl'], stats.get('需背挂shd_run', 0),
                    stats['剥深蓝_run'], stats['剥深蓝_mr'], stats['剥深蓝_ctrl'],
                    stats['需背剥深蓝_run'], stats['剥shd_分隔'], stats['合并run组'],
                    stats['值rPr不一致未并'] + stats['值不相邻未并'], stats['补空格']))
    blue_om_after2 = count_omml_blue(doc)
    lines.append('  全局断言：OMML深蓝挂点 后 %d（期望 0）%s｜散点蓝run转灰 %d｜OMML灰挂点 前 %d→后 %d'
                 % (blue_om_after2, '✓' if blue_om_after2 == 0 else '←≠',
                    blue_orphan_run, gray_om_before, gray_om_after))
    if args.detail:
        lines.append('  值明细（最多%d条）：' % args.detail)
        for bi, vi, ty, pv in vals[:args.detail]:
            lines.append('    题块%02d 值%d %s型 %r' % (bi, vi, ty, pv))
    if warn:
        lines.append('  ! 警告 %d 条（样本：%s）' % (len(warn), warn[:5]))
    return lines, parts, doc, stats


def verify(path, no_recite=False):
    """写盘后独立复核（只读）：重开文件，按值重算恒等式与逐值断言。"""
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    blocks = scan_blocks(els, ptexts)
    W = F = bad = multi = phys = 0
    for s, e in blocks:
        for k in range(s, e):
            if els[k].tag != q('p') or lead_label(ptexts[k]) != '【答案】':
                continue
            p = els[k]
            pieces, chip_end, region_end = parse_answer_para(p)
            if pieces is None:
                continue
            for ci2 in find_continuations(els, ptexts, k, e):
                for c in els[ci2]:
                    if tag(c) in ('oMath', 'oMathPara'):
                        pieces[-1][2].append(c)
            for ps, pe, oms in pieces:
                has_txt = pe > ps and ptexts[k][ps:pe].strip() != ''
                if not has_txt and not oms:
                    continue
                if oms:
                    F += 1
                    for om in oms:
                        for host, kind in om_hosts(om):
                            rpr = host.find(q('rPr'))
                            shd = rpr.find(q('shd')) if rpr is not None else None
                            col = rpr.find(q('color')) if rpr is not None else None
                            if shd is None or shd.get(q('fill')) != FILL:
                                bad += 1
                            if col is not None and col.get(q('val')) == BLUE:
                                bad += 1
                    if pe > ps:
                        rs, part = runs_in_span(p, ps, pe)
                        bad += part
                        for r in rs:
                            rpr = r.find(q('rPr'))
                            shd = rpr.find(q('shd')) if rpr is not None else None
                            col = rpr.find(q('color')) if rpr is not None else None
                            if shd is None or shd.get(q('fill')) != FILL:
                                bad += 1
                            if col is not None and col.get(q('val')) == BLUE:
                                bad += 1
                else:
                    rs, part = runs_in_span(p, ps, pe)
                    bad += part
                    W += 1
                    phys += len(rs)
                    if len(rs) > 1:
                        multi += 1
                    for r in rs:
                        rpr = r.find(q('rPr'))
                        shd = rpr.find(q('shd')) if rpr is not None else None
                        col = rpr.find(q('color')) if rpr is not None else None
                        if shd is None or shd.get(q('fill')) != FILL:
                            bad += 1
                        if col is not None and col.get(q('val')) == BLUE:
                            bad += 1
    blue_om = count_omml_blue(doc)
    n = W + F
    ok = (bad == 0 and blue_om == 0)
    return ('  复核（重开只读）：文字型灰底run数 %d＋公式型挂灰oMath值数 %d＝答案值数 %d %s｜'
            '文字型物理灰run %d（多run值 %d——rPr 差异保留登记）｜逐值违规 %d｜OMML深蓝挂点残留 %d（期望0）%s'
            % (W, F, n, '✓' if W + F == n else '←≠', phys, multi, bad, blue_om,
               '✓' if blue_om == 0 else '←≠')), ok


def verify_jlp(path):
    """讲练件族减法终态复核（只读，2026-09-04）：【答案】值区灰底/深蓝逐值＝0（附则减法②）。"""
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    blocks = scan_blocks(els, ptexts)
    n_vals = bad = 0
    for s, e in blocks:
        for k in range(s, e):
            if els[k].tag != q('p') or lead_label(ptexts[k]) != '【答案】':
                continue
            p = els[k]
            pieces, chip_end, region_end = parse_answer_para(p)
            if pieces is None:
                continue
            for ci2 in find_continuations(els, ptexts, k, e):
                for c in els[ci2]:
                    if tag(c) in ('oMath', 'oMathPara'):
                        pieces[-1][2].append(c)
            for ps, pe, oms in pieces:
                has_txt = pe > ps and ptexts[k][ps:pe].strip() != ''
                if not has_txt and not oms:
                    continue
                n_vals += 1
                for om in oms:
                    for host, _kind in om_hosts(om):
                        rpr = host.find(q('rPr'))
                        shd = rpr.find(q('shd')) if rpr is not None else None
                        col = rpr.find(q('color')) if rpr is not None else None
                        if shd is not None and shd.get(q('fill')) == FILL:
                            bad += 1
                        if col is not None and col.get(q('val')) == BLUE:
                            bad += 1
                if pe > ps:
                    rs, _part = runs_in_span(p, ps, pe)
                    for r in rs:
                        rpr = r.find(q('rPr'))
                        shd = rpr.find(q('shd')) if rpr is not None else None
                        col = rpr.find(q('color')) if rpr is not None else None
                        if shd is not None and shd.get(q('fill')) == FILL:
                            bad += 1
                        if col is not None and col.get(q('val')) == BLUE:
                            bad += 1
    ok = bad == 0
    return ('  复核（讲练件族·减法终态口径）：【答案】值区逐值 %d｜灰底/深蓝违规 %d（期望0）%s'
            % (n_vals, bad, '✓' if ok else '←≠')), ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--report')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--no-recite', action='store_true')
    ap.add_argument('--detail', type=int, default=25)
    args = ap.parse_args()
    out = []
    allok = True
    for p in args.files:
        if not os.path.exists(p):
            out.append('◆ %s 不存在，跳过' % os.path.basename(p))
            continue
        if JLP_RE.search(os.path.basename(p)):
            # 2026-09-04 减法口径：讲练件族禁改标（防回挂）；--verify 走减法终态断言
            if args.verify:
                out.append('◆ %s' % os.path.basename(p))
                vline, ok = verify_jlp(p)
                out.append(vline)
                allok = allok and ok
                out.append('')
            else:
                out.append('◆ %s 属讲练件族——题目侧答案值灰底已废止（附则《讲练件底纹减法》），'
                           '本工具拒绝对其改标；如需剥除用 工具/底纹去除器.py' % os.path.basename(p))
                out.append('')
                allok = False
            continue
        if args.verify:
            out.append('◆ %s' % os.path.basename(p))
            vline, ok = verify(p, args.no_recite)
            out.append(vline)
            allok = allok and ok
            out.append('')
            continue
        z = zipfile.ZipFile(p)
        doc0 = etree.fromstring(z.read('word/document.xml'))
        z.close()
        t_before = snapshot_text(doc0)
        chips_before = snapshot_chips(doc0)
        lines, parts, doc, stats = process(p, args)
        t_after = snapshot_text(doc)
        chips_after = snapshot_chips(doc)
        sm = difflib.SequenceMatcher(None, t_before, t_after, autojunk=False)
        ops = sm.get_opcodes()
        only_space = all(op == 'equal' or (op == 'insert' and set(t_after[j1:j2]) <= {' '})
                         for op, i1, i2, j1, j2 in ops)
        n_ins = sum(j2 - j1 for op, i1, i2, j1, j2 in ops if op == 'insert')
        lines.append('  零破坏断言：文字流仅补空格%s（插入%d，登记%d）｜芯片/题号/标记run指纹%s'
                     % ('✓' if only_space else '←≠', n_ins, stats['补空格'],
                        '恒等✓' if chips_before == chips_after else '←≠'))
        allok = allok and only_space and n_ins == stats['补空格'] and chips_before == chips_after
        if not args.dry_run:
            parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                        encoding='UTF-8', standalone=True)
            tmp = p + '.t4type'
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
            vline, ok = verify(p, args.no_recite)
            lines.append(vline)
            allok = allok and ok
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
    if not allok:
        sys.exit(1)


if __name__ == '__main__':
    main()
