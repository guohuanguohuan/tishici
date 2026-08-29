# -*- coding: utf-8 -*-
"""块标签芯片.py — 2026-08-28 拍板「块标签底纹（方案甲）＋答案值标记＋并行解法标记」；
2026-08-29 成书形态拍板扩面：枚举由封闭五个改为「凡行内【×】栏目标签一律挂」。
两阶段（spaces＝防连片补空格属内容改动，随 Pass1 对账；shade＝纯格式零字符，随 Pass2）：
  python 块标签芯片.py spaces <docx> <登记表md>    # 标签与相邻内容标记值间缺空格的补一个半角空格，逐处登记（登记数＝处理数）
  python 块标签芯片.py shade  <docx> <计数报告txt> [--legacy]  # 拆 run 隔离并挂 w:shd clear/auto/C9C9C9、不加粗
 shade 范围（2026-08-29 扩面口径）：
  ①块标签＝凡行内【×】栏目标签（【答案】【知识点】【分析】【详解】【点睛】【编注】【大招指引】
    【题后反思】【温馨提醒】【定义】【结论】及扫描发现的其余行内栏目标签，全件含表格内段落）
    ——只盖「【×】」本身；黑名单不挂：【典例N】类（题干内栏目名，规格§3.8删除对象）、
    【易错】【了解】（学史切片条目分类标记豁免——公共规则§7）；
  ②详解内并行解法起段标记（方法一/方法二/解法一/另解…，可带［］，允许段首小问编号(2)、
    块标签、「解：/证明：」前缀）——只盖标记本身；
  ③【答案】后的答案值（选项字母、填空/计算结果，含 OMML 公式区：m:r 与结构 ctrlPr 的 w:rPr
    挂 shd，分数整块覆盖）——只盖值本身、多值按「；」拆开各盖各的、值尾句读不盖；
    答案跨段续段（【答案】段无【知识点】时，下一标签前有实质内容的后续段）挂其前段。
  详解序号①②③与选项A．B．不挂（拍板不采纳）。--legacy＝回退 2026-08-28 封闭五标签口径（兼容开关）。
 实现：每段先按未变动的 w:t 文本流算好全部挂灰区间，再按起点倒序逐个 isolate_runs 手术（只拆不并，
  跨 oMath 的区间逐 run 分别挂灰，避免文字/公式交错序移动），区间互不重叠、文本不增删，坐标不受前次手术影响。
 幂等：已是 C9C9C9 的 run 不重复计数。报告含「全挂核验」：逐标签文本出现数 vs 整标签已挂 run 数。"""
import sys, io, zipfile, re, os, time
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname

LABELS = ['【答案】', '【知识点】', '【分析】', '【详解】', '【点睛】']   # 2026-08-28 封闭口径（--legacy 用）
CHIP_RE = re.compile(r'【[^】]{1,16}】')          # 2026-08-29 扩面：凡行内【×】栏目标签
CHIP_BLACKLIST = ('【易错】', '【了解】')          # 学史切片条目分类标记豁免（公共规则§7）
CHIP_BLACKLIST_RE = re.compile(r'^【典例[^】]*】$')  # 题干内【典例N】栏目名——规格§3.8删除对象，不挂
MARK_RE = re.compile(r'^(?:\(\d{1,2}\)|（\d{1,2}）)?(?:【[^】]{1,12}】)?(?:解：|证明：)?'
                     r'(［?(?:方法|解法)[一二三四五六七八九十]{1,3}］?|另解)')
NEXT_LB = re.compile(r'【[^】]{1,12}】')
FILL = 'C9C9C9'

def chip_spans(t, legacy=False):
    """段文本内全部可挂芯片标签区间 [(s, e, label)]（黑名单排除）。"""
    out = []
    for m in CHIP_RE.finditer(t):
        lb = m.group(0)
        if legacy and lb not in LABELS:
            continue
        if lb in CHIP_BLACKLIST or CHIP_BLACKLIST_RE.match(lb):
            continue
        out.append((m.start(), m.end(), lb))
    return out

def wtext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def items(p):
    """段内行级子项：[(el, 文本)]，w:r（w:t 文本）/ m:oMath、m:oMathPara（m:t 文本）。"""
    out = []
    for c in p:
        tg = tag(c)
        if tg == 'r':
            out.append((c, ''.join(t.text or '' for t in c.findall(q('t')))))
        elif tg in ('oMath', 'oMathPara'):
            out.append((c, ''.join(t.text or '' for t in c.iter(mq('t')))))
    return out

def set_shd(rpr):
    """rPr 挂 shd C9C9C9（去旧 shd），并按拍板去加粗。返回是否新挂。"""
    if rpr is None:
        return False
    old = rpr.find(q('shd'))
    if old is not None and old.get(q('fill')) == FILL:
        return False
    if old is not None:
        rpr.remove(old)
    shd = etree.Element(q('shd'))
    shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
    # CT_RPr 序：shd 在 bdr 之后、fitText/vertAlign/rtl/cs/em/lang 之前
    pos = len(list(rpr))
    for k, c in enumerate(list(rpr)):
        if tag(c) in ('fitText', 'vertAlign', 'rtl', 'cs', 'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath'):
            pos = k; break
    rpr.insert(pos, shd)
    for btag in ('b', 'bCs'):
        b = rpr.find(q(btag))
        if b is not None:
            rpr.remove(b)
    return True

def shade_run(r):
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    return set_shd(rpr)

def shade_omath(om):
    """OMML 公式整块挂 shd：m:r 与结构 ctrlPr 的 w:rPr（分数整块覆盖）。
    缺 w:rPr 的 m:r/ctrlPr 补建（w:rPr 为各自首子元素）。返回是否新挂。"""
    hung = False
    for host in om.iter():
        if etree.QName(host).namespace != M or tag(host) not in ('r', 'ctrlPr'):
            continue
        rpr = host.find(q('rPr'))
        if rpr is None:
            rpr = etree.Element(q('rPr'))
            host.insert(0, rpr)
        if set_shd(rpr):
            hung = True
    return hung

def split_run_at(r, off):
    """把 run 在文本 off 处拆成两个 run（复制 rPr），返回右半 run。"""
    ts = r.findall(q('t'))
    assert len(ts) == 1, 'split_run_at 仅支持单 w:t run'
    t = ts[0]
    txt = t.text or ''
    nr = etree.fromstring(etree.tostring(r))
    t.text = txt[:off]
    nt = nr.findall(q('t'))[0]
    nt.text = txt[off:]
    t.set(XMLSPACE, 'preserve'); nt.set(XMLSPACE, 'preserve')
    r.addnext(nr)
    return nr

def isolate_runs(p, s, e):
    """把段内 w:t 文本流 [s,e) 覆盖的 run 隔离出来：边界处拆 run，返回完全落入区间的 run 列表。
    只拆不并——跨 oMath 等非 run 元素合并 run 会把后段文字搬到前段位置（文字/公式交错序移动），
    违反零字符铁律；区间跨多个 run 时逐 run 分别挂灰，视觉效果与合并一致。
    坐标基于 w:t 流（公式 m:t 不占位）。"""
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
            split_run_at(r, s - a)
            return isolate_runs(p, s, e)  # 拆完重扫
        if b > e:
            split_run_at(r, e - a)
            return isolate_runs(p, s, e)
        out.append(r)
    return out

def insert_space_run(before_el, model_r):
    """在 before_el 前插入半角空格 run（rPr 仿 model_r，不带底纹）。"""
    nr = etree.Element(q('r'))
    rpr = model_r.find(q('rPr'))
    if rpr is not None:
        nrpr = etree.fromstring(etree.tostring(rpr))
        old = nrpr.find(q('shd'))
        if old is not None:
            nrpr.remove(old)
        nr.append(nrpr)
    t = etree.SubElement(nr, q('t'))
    t.text = ' '
    t.set(XMLSPACE, 'preserve')
    before_el.addprevious(nr)

def para_no(p):
    """段所属题号（同层往前找最近题号段；表格内段落上溯到表格再往前）——登记用。"""
    cur = p
    while cur is not None:
        if tag(cur) == 'p':
            m = re.match(r'^(\d+)．', wtext(cur))
            if m:
                return m.group(1)
        cur = cur.getprevious()
        if cur is None:
            cell = p
            while cell is not None and tag(cell) not in ('tbl', 'body'):
                cell = cell.getparent()
            if cell is not None and tag(cell) == 'tbl':
                p = cell
                cur = cell.getprevious()
    return '?'

def save_parts(path, parts, suffix='.chip'):
    tmp = path + suffix
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name, b in parts.items():
        zo.writestr(name, b)
    zo.close()
    for k in range(12):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(6)
    raise RuntimeError('locked: ' + path)

# ---------- spaces 阶段（内容改动：防连片补空格） ----------
def phase_spaces(path, regmd):
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    reg = []
    for p in body.iter(q('p')):
        if not wtext(p).startswith('【答案】'):
            continue
        # 每处手术完重扫本段（答案行极少，成本忽略）
        while True:
            its = items(p)
            stream = ''
            spans = []
            for el, txt in its:
                spans.append((el, len(stream), len(stream) + len(txt)))
                stream += txt
            aend = stream.find('【答案】') + len('【答案】')
            done = False
            # ①【答案】之后：紧邻内容非空格则补一个半角空格
            if aend < len(stream) and stream[aend] not in ' 　':
                for el, a, b in spans:
                    if a <= aend < b:
                        if tag(el) == 'r':
                            tt = el.findall(q('t'))[0]
                            tt.text = (tt.text or '')[:aend - a] + ' ' + (tt.text or '')[aend - a:]
                            tt.set(XMLSPACE, 'preserve')
                            reg.append((para_no(p), '【答案】后'))
                        else:
                            prev_r = its[[x[0] for x in its].index(el) - 1][0]
                            insert_space_run(el, prev_r)
                            reg.append((para_no(p), '【答案】后(公式前)'))
                        done = True
                        break
                if done:
                    continue
            # ②值末与下一标签之间：前一可见字符（含公式 m:t）非空格则补
            m2 = NEXT_LB.search(stream, aend)
            if m2:
                L = m2.start()
                if L > 0 and stream[L - 1] not in ' 　':
                    for el, a, b in spans:
                        if a <= L < b:
                            if tag(el) == 'r':
                                ts = el.findall(q('t'))
                                if ts:
                                    tt = ts[0]
                                    tt.text = (tt.text or '')[:L - a] + ' ' + (tt.text or '')[L - a:]
                                    tt.set(XMLSPACE, 'preserve')
                                    reg.append((para_no(p), '值末/下一标签前'))
                                    done = True
                            break
                    if done:
                        continue
            break
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    save_parts(path, parts)
    with open(regmd, 'w', encoding='utf-8') as f:
        f.write('# 防连片补空格登记：%s\n\n' % os.path.basename(path))
        f.write('| 题号 | 位置 |\n|---|---|\n')
        for no, kind in reg:
            f.write('| %s | %s |\n' % (no, kind))
        f.write('\n合计补空格 %d 处（登记数＝处理数）。\n' % len(reg))
    print('补空格 %d 处 -> %s' % (len(reg), regmd))

# ---------- shade 阶段（纯格式零字符） ----------
def value_spans(p):
    """【答案】行的答案值挂灰区间（w:t 流坐标）与公式元素清单。
    值区＝【答案】chip 末→下一标签「【」（或段尾）；文字按；;拆段、去首尾空白，
    全值区最末段再去句读。．；公式项整体返回由 shade_omath 挂。"""
    its = items(p)
    # w:t 流坐标与项边界
    wt_spans = []   # (el, a, b) 仅 w:r
    om_items = []   # (el, a, b) 公式项在文档序中的位置（a/b 为其前后 w:t 偏移夹点）
    off = 0
    for el, txt in its:
        if tag(el) == 'r':
            wt_spans.append((el, off, off + len(txt)))
            off += len(txt)
        else:
            om_items.append((el, off, off))
    full = wtext(p)
    chip_end = full.find('【答案】') + len('【答案】')
    m = NEXT_LB.search(full, chip_end)
    region_end = m.start() if m else len(full)
    spans = []
    for el, a, b in wt_spans:
        s = max(a, chip_end); e = min(b, region_end)
        if s >= e:
            continue
        txt = (el.findall(q('t'))[0].text or '')
        seg = txt[s - a:e - a]
        # 按；;拆段（分隔符不盖）；piece 坐标为 seg 内偏移
        cur = 0
        for piece in re.split(r'([；;])', seg):
            if piece in ('；', ';'):
                cur += len(piece)
                continue
            a2, b2 = cur, cur + len(piece)
            while a2 < b2 and piece[a2 - cur] in ' 　':
                a2 += 1
            while b2 > a2 and piece[b2 - cur - 1] in ' 　':
                b2 -= 1
            if b2 > a2:
                spans.append([s + a2, s + b2])
            cur += len(piece)
    # 值区最末文字段去句读
    if spans:
        last = max(spans, key=lambda x: x[1])
        e = last[1]
        while e > last[0] and full[e - 1] in '。．':
            e -= 1
        while e > last[0] and full[e - 1] in ' 　':
            e -= 1
        last[1] = e
        if last[0] >= last[1]:
            spans.remove(last)
    oms = [el for el, a, b in om_items if chip_end <= a and b <= region_end]
    return spans, oms

def phase_shade(path, report, legacy=False):
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    cnt = Counter()
    cnt['并行解法'] = 0; cnt['答案值文字run'] = 0; cnt['答案值公式块'] = 0
    ans_rows = 0; cont_rows = 0; warns = []
    for p in body.iter(q('p')):
        t = wtext(p)
        spans = []   # (s, e, kind, label)
        for s, e, lb in chip_spans(t, legacy):
            spans.append((s, e, 'chip', lb))
        m = MARK_RE.match(t)
        if m:
            spans.append((m.start(1), m.end(1), 'marker', None))
        oms = []
        if t.startswith('【答案】'):
            ans_rows += 1
            vs, oms = value_spans(p)
            spans += [(s, e, 'value', None) for s, e in vs]
            # 跨段续值
            if '【知识点】' not in t:
                nx = p.getnext()
                while nx is not None and tag(nx) == 'p' and not wtext(nx).strip():
                    nx = nx.getnext()
                if nx is not None and tag(nx) == 'p':
                    t2 = wtext(nx)
                    m2 = NEXT_LB.search(t2)
                    lead = t2[:m2.start()] if m2 else ''
                    e = len(lead)
                    while e > 0 and lead[e - 1] in ' 　。．；;':
                        e -= 1
                    if e > 0 and lead[:e].strip():
                        rs = isolate_runs(nx, 0, e)
                        hung = False
                        for r in rs:
                            hung = shade_run(r) or hung
                        if hung:
                            cnt['答案值文字run'] += 1
                            cont_rows += 1
        # 重叠检查（chip 与 value/marker 不应相交）
        spans.sort()
        for k in range(1, len(spans)):
            if spans[k][0] < spans[k - 1][1]:
                warns.append('区间相交@%s 题%s' % (spans[k], para_no(p)))
        # 倒序手术
        for s, e, kind, lb in sorted(spans, reverse=True):
            rs = isolate_runs(p, s, e)
            if not rs:
                warns.append('隔离失败 (%d,%d) 题%s' % (s, e, para_no(p)))
                continue
            # chip/marker 跨 run 碎片：相邻纯 run（中间无 oMath 等元素）时拼回单 run 再挂，
            # 保证标签 run 文本完整（下游脚本按整标签文本检索）；拼合只动 run 边界不动文字流。
            if kind in ('chip', 'marker') and len(rs) > 1:
                adj = all(rs[k].getnext() is rs[k + 1] for k in range(len(rs) - 1))
                if adj:
                    t0 = rs[0].findall(q('t'))[-1]
                    for r in rs[1:]:
                        t0.text = (t0.text or '') + ''.join(x.text or '' for x in r.findall(q('t')))
                        r.getparent().remove(r)
                    t0.set(XMLSPACE, 'preserve')
                    rs = rs[:1]
                else:
                    warns.append('chip/marker 跨非run元素 (%d,%d) 题%s' % (s, e, para_no(p)))
            hung = False
            for r in rs:
                hung = shade_run(r) or hung
            if hung:
                if kind == 'chip':
                    cnt[lb] += 1
                elif kind == 'marker':
                    cnt['并行解法'] += 1
                else:
                    cnt['答案值文字run'] += 1
        for om in oms:
            if shade_omath(om):
                cnt['答案值公式块'] += 1
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    save_parts(path, parts)
    # 全挂核验（2026-08-29 扩面口径）：逐标签文本出现数 vs 整标签已挂 C9C9C9 run 数
    occ = Counter()
    for p in body.iter(q('p')):
        for _, _, lb in chip_spans(wtext(p), legacy):
            occ[lb] += 1
    hungrun = Counter()
    for r in doc.iter(q('r')):
        rpr = r.find(q('rPr'))
        shd = rpr.find(q('shd')) if rpr is not None else None
        if shd is None or shd.get(q('fill')) != FILL:
            continue
        tx = ''.join(x.text or '' for x in r.findall(q('t')))
        m = CHIP_RE.fullmatch(tx) if tx else None
        if m and not (tx in CHIP_BLACKLIST or CHIP_BLACKLIST_RE.match(tx)):
            if not legacy or tx in LABELS:
                hungrun[tx] += 1
    miss = {lb: (occ[lb], hungrun[lb]) for lb in occ if hungrun[lb] != occ[lb]}
    with open(report, 'w', encoding='utf-8') as f:
        f.write('块标签芯片＋答案值标记 shade 计数（%s口径）：%s\n'
                % ('封闭五标签' if legacy else '2026-08-29 扩面·凡行内【×】栏目标签', os.path.basename(path)))
        for lb in sorted(set(list(occ) + [k for k in cnt if k.startswith('【')])):
            f.write('%s 出现 %d｜本轮新挂 %d｜整标签已挂run %d%s\n'
                    % (lb, occ[lb], cnt[lb], hungrun[lb], '' if hungrun[lb] == occ[lb] else '  <-- 不等!!'))
        f.write('并行解法标记 %d\n' % cnt['并行解法'])
        f.write('答案行 %d；答案值文字run %d；答案值公式块 %d；跨段续值段 %d\n'
                % (ans_rows, cnt['答案值文字run'], cnt['答案值公式块'], cont_rows))
        if miss:
            f.write('\n全挂核验不齐：%r\n' % miss)
        else:
            f.write('\n全挂核验：全部标签 出现数＝已挂run数 PASS\n')
        if warns:
            f.write('\n警告：\n' + '\n'.join('- ' + w for w in warns) + '\n')
    print('chips', {k: v for k, v in cnt.items() if v}, '| 答案行', ans_rows,
          '| 全挂核验', 'PASS' if not miss else miss, '| 警告', len(warns))
    for w in warns:
        print('  !', w)

if __name__ == '__main__':
    if sys.argv[1] == 'spaces':
        phase_spaces(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'shade':
        phase_shade(sys.argv[2], sys.argv[3], legacy=('--legacy' in sys.argv[4:4 + len(sys.argv)]))
    else:
        print(__doc__)
