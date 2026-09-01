# -*- coding: utf-8 -*-
r"""题号块三段式.py — 层级制题号/条目号改版工具（A'改制轮·工具债③·T3，2026-09-01 核心升级；可复用，幂等）

口径（公共规则§6编号唯一层形＋§7题号难度块底纹/条目号底纹条款现行文本）：
  · 层级制（同步线）：题号块「节号-序号．（档位·提分线·卡壳看答案）」——节号＝题所在教材节标题节号
    （内层节优先：节1.1.1之下不挂1.1）；序号＝节内连续（题族独立计数）；衔接件两段式同款
    「节号-序号．（衔接必会·卡壳看答案）」（--linkage，无档位无提分线）。旧全局「N．」输入照跑
    （重编为层级制——新旧双轨兼容）；已层级制输入幂等重跑。
  · 条目族（清单条目/讲部条目）独立节内连续「节号-序号．」：条目号底纹 C9C9C9 不加粗（纯序号锚，
    §7条目号底纹款），与题族分列计数、节内两族同号不判冲突；〔基〕/〔进〕标记位置照旧（号后）。
  · 底纹盖整个「节号-序号．」（run拆分处理跨run号）；括注不挂底纹、加粗维持整块（题族）；
    题干粘连文字随拆分剥底纹剥加粗。退化题号块「节号-序号．」（无括注）：默认模式不加括注。
  · 节标题边界识别（教材节标题段）：节号pattern（^\d+\.\d+(\.\d+)?[空格]）＋三信号任一
    （28半点run／整行底纹ADC2DA／标题3样式），负判据＝整行底纹C6D4E3（题型/讲部行）。
  · 跨卷接续（公共规则§12：层级制节内序列跨卷接续）：--sec-start 节号=序号显式映射；
    --sec-continue 前卷docx或本工具登记md（读各节两族末号自动续号）。
  · 统计段括注联动（默认开，--no-stats-sync关）：节标题行「（第X—Y题）」全局题号区间括注删除
    （题量括注「　本节N题：…」保留——规格书§1口径C授权差异②）。
  · 文件名题量恒等断言：文件名「（N题）」「（N条）」「（N题M条）」与两族计数断言；
    清单件文件名无条数时用 --expect-entry N 断言。

识别三重判据（题族）：①形态（括注式 q3/q1/ql 或裸号+块内【答案】）②序列门控（旧全局号＝
qstart..qstart+N−1 全件连续；层级制号＝节内连续，续卷按 --sec-start/-continue 起点）③块内【答案】
验证（与 extract_structure 题块判定同源锚）。条目族＝裸号＋块内无【答案】＋条目族启用。

断言（全过才落盘，任一不过抛异常不写文件）：
  A1 输入序列门控：旧全局号 qstart..qstart+N−1 连续无重复；层级制号各节两族序列连续、
     起点＝--sec-start/-continue 映射值（缺省1）；
  A2 每个改写段：题族 run[0]恰为「节号-序号．」挂C9C9C9＋b、run[1]（有括注时）无shd有b、
     退化/衔接同款；条目族 run[0]恰为「节号-序号．」挂C9C9C9且无b；余文无灰无粗（题族）；
  A3 零意外字符：改写段后期望文本（授权token替换＋区间括注删除）逐段精确相等；
  A5 文件名题量/条目数恒等（可解析或--expect给值时）＋extract_structure 题块数交叉核对；
  A4 幂等（登记md复核）：二跑文本改写/补底纹/剥底纹计数全为0。

用法: python 工具/题号块三段式.py <docx> <登记md> [--linkage] [--qstart N]
        [--sec-start 节号=序号[,节号=序号…]] [--sec-start-entry 节号=序号[,…]]
        [--sec-continue 前卷.docx[,前卷2.docx…]] [--families q|e|qe] [--expect N] [--expect-entry N]
        [--no-stats-sync]
输出: 就地改写 docx（仅 word/document.xml）＋登记md（计数＋逐题/逐条目映射＋#SEC-END机器行）＋stdout。
"""
import sys, os, re, zipfile, time, copy, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
FILL = 'C9C9C9'
def q(t): return '{%s}%s' % (W, t)

GRADE_MAP = {'简单': '简单·保60%', '中档': '中档·保80%', '难': '难·冲100%'}
TAIL = '卡壳看答案'
LINK_BODY = '衔接必会·' + TAIL
# 题号 token：层级制「节号-序号．」/ 旧全局「N．」（NUM_CORE=数字本体，TOK 含全角句点）
NUM_CORE = r'(?:\d+(?:\.\d+)+-\d+|\d+)'
NUMTOK_RE = re.compile(r'^(%s)．' % NUM_CORE)
Q3_RE  = re.compile(r'^(%s)．（(简单|中档|难)·(保60%%|保80%%|冲100%%)·%s）' % (NUM_CORE, TAIL))
Q1_RE  = re.compile(r'^(%s)．（(简单|中档|难)）' % NUM_CORE)
QL_RE  = re.compile(r'^(%s)．（%s）' % (NUM_CORE, LINK_BODY))
TITLE_RE = re.compile(r'^\d+(\.\d+)+\s')          # 节/讲部/题型标题（半角点分序号起段）
LECT_RE = re.compile(r'^\d+(\.\d+)*\s*方法讲解[｜|]')
SEC_TTL_RE = re.compile(r'^\d+\.\d+(\.\d+)?[\s\u3000]+\S')   # 节标题节号pattern（2~3级）
GRP_SHD = 'C6D4E3'                                  # 题型/讲部标题整行底纹（节标题负判据）
SEC_SHDS = ('ADC2DA', 'adc2da')
INTERVAL_RE = re.compile(r'（第[0-9．\-—–~～]+题）')           # 全局题号区间括注（删除对象）
FN_Q_RE = re.compile(r'（(\d+)题')
FN_E_RE = re.compile(r'（(\d+)条')


def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))


def set_run_text(r, s):
    ts = r.findall(q('t'))
    assert ts, 'run 内无 w:t（fldChar/图件 run 不得作题号块载体）'
    ts[0].text = s
    ts[0].set(XMLSPACE, 'preserve')
    for t in ts[1:]:
        t.text = ''


def shd_of(r):
    rpr = r.find(q('rPr'))
    return rpr.find(q('shd')) if rpr is not None else None


def ppr_shd_fill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None


def clone_rpr_without(r, drop=()):
    rpr = r.find(q('rPr'))
    if rpr is None:
        return None
    nr = copy.deepcopy(rpr)
    for t in drop:
        e = nr.find(q(t))
        if e is not None:
            nr.remove(e)
    return nr


def make_run(rpr, text, after):
    nr = etree.Element(q('r'))
    if rpr is not None:
        nr.append(rpr)
    t = etree.SubElement(nr, q('t'))
    t.text = text
    t.set(XMLSPACE, 'preserve')
    after.addnext(nr)
    return nr


def ensure_num_rpr(r, bold=True):
    """题号run 补（题族：加粗＋）底纹 C9C9C9（各自缺才补）；条目族 bold=False 剥加粗。
    返回 (是否补/剥底纹, 是否补/剥加粗)。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    fmt_changed = False
    if bold:
        if rpr.find(q('b')) is None:
            rpr.insert(0, etree.Element(q('b')))
            fmt_changed = True
    else:
        for tag in ('b', 'bCs'):
            e = rpr.find(q(tag))
            if e is not None:
                rpr.remove(e)
                fmt_changed = True
    shd_changed = False
    shd = rpr.find(q('shd'))
    if shd is None:
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
        rpr.append(shd)
        shd_changed = True
    elif shd.get(q('fill')) != FILL:
        raise RuntimeError('题号run已有其他底纹 fill=%s，需人工处置' % shd.get(q('fill')))
    return shd_changed, fmt_changed


def ensure_bold(r):
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    if rpr.find(q('b')) is None:
        rpr.insert(0, etree.Element(q('b')))
        return True
    return False


def consume_prefix_runs(p, length):
    """前缀消费：覆盖段首 [0,length) 的文本 run 序列（跨 run 碎裂题号安全）。"""
    covered, off = [], 0
    for r in p.findall(q('r')):
        tx = run_text(r)
        if not tx:
            continue
        covered.append((r, tx))
        off += len(tx)
        if off >= length:
            break
    assert covered and off >= length, '题号块token跨run碎裂超限（前缀消费失败）'
    return covered


def remove_span_runs(p, a, b):
    """删除段落字符区间 [a,b)（跨run安全：整段删除覆盖run、边界run切文本）。返回删除字符数。"""
    off = 0
    for r in list(p.findall(q('r'))):
        tx = run_text(r)
        if not tx:
            continue
        rs, re_ = off, off + len(tx)
        off = re_
        if re_ <= a or rs >= b:
            continue
        lo = max(a, rs) - rs
        hi = min(b, re_) - rs
        if lo == 0 and hi == len(tx):
            p.remove(r)
        else:
            set_run_text(r, tx[:lo] + tx[hi:])
    return b - a


def question_form(txt):
    """返回 (形态, 号token, 节号, 序号, token长度, 档位)。形态 ∈ q3/q1/ql/bare/None。
    层级制「1.1.1-5．」与旧全局「5．」统一解析；bare＝裸号（题族须【答案】验证，或条目族）。"""
    m = Q3_RE.match(txt)
    if m:
        return 'q3', m.group(1), sec_of(m.group(1)), ord_of(m.group(1)), m.end(), m.group(2)
    m = Q1_RE.match(txt)
    if m:
        return 'q1', m.group(1), sec_of(m.group(1)), ord_of(m.group(1)), m.end(), m.group(2)
    m = QL_RE.match(txt)
    if m:
        return 'ql', m.group(1), sec_of(m.group(1)), ord_of(m.group(1)), m.end(), None
    m = NUMTOK_RE.match(txt)
    if m:
        return 'bare', m.group(1), sec_of(m.group(1)), ord_of(m.group(1)), m.end(), None
    return None, None, None, None, 0, None


def sec_of(tok):
    m = re.match(r'^(\d+(?:\.\d+)+)-\d+$', tok)
    return m.group(1) if m else None


def ord_of(tok):
    m = re.match(r'^(\d+(?:\.\d+)+)?-(\d+)$|^\d+$', tok)
    return int(m.group(2) or m.group(0)) if m else None


def is_section_title(p, txt):
    """教材节标题段判定：节号pattern＋（28半点／整行底纹ADC2DA／标题3样式）任一；C6D4E3行除外。"""
    if LECT_RE.match(txt) or NUMTOK_RE.match(txt) or not SEC_TTL_RE.match(txt):
        return None
    fill = ppr_shd_fill(p)
    if fill == GRP_SHD:
        return None
    if fill in SEC_SHDS:
        m = re.match(r'^(\d+\.\d+(?:\.\d+)?)', txt)
        return m.group(1)
    ppr = p.find(q('pPr'))
    if ppr is not None:
        ps = ppr.find(q('pStyle'))
        if ps is not None and re.search(r'(?i)heading3|标题3', ps.get(q('val')) or ''):
            m = re.match(r'^(\d+\.\d+(?:\.\d+)?)', txt)
            return m.group(1)
    for r in p.findall(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None:
            continue
        z = rpr.find(q('sz'))
        if z is not None and z.get(q('val')) == '28' and run_text(r).strip():
            m = re.match(r'^(\d+\.\d+(?:\.\d+)?)', txt)
            return m.group(1)
    return None


def block_has_answer(els, i, n):
    """块内【答案】验证：els[i] 起到下一 题号起段/标题段/非段元素 前的文本里找【答案】
    （与 extract_structure 题块判定同界：块在表格处截断）。"""
    buf = para_text(els[i])
    j = i + 1
    while j < n:
        c = els[j]
        if c.tag != q('p'):
            break
        t = para_text(c)
        if NUMTOK_RE.match(t) or TITLE_RE.match(t) or LECT_RE.match(t):
            break
        buf += t
        j += 1
    return '【答案】' in buf


def rewrite_question(p, mode, toklen, new_num, grade, form):
    """题族改写：run[0]「节号-序号．」（C9C9C9＋b）→ run[1] 括注（b 无shd）→ run[2] 余文（无shd无b）。
    跨run碎裂先归并回收首run；零意外字符（A3 逐段断言）。返回计数 dict。"""
    before = para_text(p)
    if mode == 'linkage':
        tgt_body = '（%s）' % LINK_BODY
        text_changed = form != 'ql'
    elif form == 'q1':
        tgt_body = '（%s·%s）' % (GRADE_MAP[grade], TAIL)
        text_changed = True
    elif form == 'q3':
        tgt_body = '（%s·%s）' % (GRADE_MAP[grade], TAIL)
        text_changed = False
    else:   # bare 退化块：不加括注
        tgt_body = None
        text_changed = False

    covered = consume_prefix_runs(p, toklen)
    first_r = covered[0][0]
    tok_full = ''.join(tx for _, tx in covered)[:toklen]
    tail = ''.join(tx for _, tx in covered)[toklen:]
    num_txt = new_num + '．'

    set_run_text(first_r, num_txt)
    if first_r.find(q('rPr')) is None:
        first_r.insert(0, etree.Element(q('rPr')))
    shd_added, bold_added = ensure_num_rpr(first_r, bold=True)
    merged = len(covered) > 1
    for r, _ in covered[1:]:
        p.remove(r)
    anchor = first_r
    new_runs = 0
    if tgt_body is not None:
        brpr = clone_rpr_without(first_r, drop=('shd',))
        br = make_run(brpr, tgt_body, anchor)
        ensure_bold(br)
        anchor = br
        new_runs += 1
    if tail:
        trpr = clone_rpr_without(first_r, drop=('shd', 'b', 'bCs'))
        make_run(trpr, tail, anchor)
        new_runs += 1

    exp = num_txt + (tgt_body or '') + tail + before[toklen:]
    assert para_text(p) == exp, '改写后期望文本不符: %r != %r' % (para_text(p)[:50], exp[:50])
    return {'text_changed': text_changed or (tok_full != num_txt), 'old_tok': tok_full,
            'new_tok': num_txt + (tgt_body or ''), 'new_runs': new_runs, 'merged': merged,
            'shd_added': shd_added, 'bold_added': bold_added}


def rewrite_entry(p, toklen, new_num):
    """条目族改写：号run 文本换「节号-序号．」，确保 C9C9C9＋不加粗（§7条目号底纹款）；
    其余 run（〔基〕/题名/正文）不动。返回计数 dict。"""
    before = para_text(p)
    covered = consume_prefix_runs(p, toklen)
    first_r = covered[0][0]
    tok_full = ''.join(tx for _, tx in covered)[:toklen]
    num_txt = new_num + '．'
    set_run_text(first_r, num_txt)
    if first_r.find(q('rPr')) is None:
        first_r.insert(0, etree.Element(q('rPr')))
    shd_added, bold_stripped = ensure_num_rpr(first_r, bold=False)
    merged = len(covered) > 1
    for r, _ in covered[1:]:
        p.remove(r)
    exp = num_txt + before[toklen:]
    assert para_text(p) == exp, '条目改写后期望文本不符: %r != %r' % (para_text(p)[:50], exp[:50])
    return {'text_changed': tok_full != num_txt, 'old_tok': tok_full, 'new_tok': num_txt,
            'merged': merged, 'shd_added': shd_added, 'bold_stripped': bold_stripped}


def parse_secstart(spec):
    """'1.2.4=14,1.3=1' → {'1.2.4': 14, ...}"""
    out = {}
    if not spec:
        return out
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        k, _, v = part.partition('=')
        out[k.strip()] = int(v)
    return out


def read_prior_ends(paths):
    """--sec-continue：从前卷docx（层级制号扫描）或本工具登记md（#SEC-END行）读两族各节末号。
    返回 ({节: 题族末号}, {节: 条目族末号})。"""
    qmax, emax = {}, {}
    for path in paths.split(','):
        path = path.strip()
        if not path:
            continue
        if not os.path.isfile(path):
            raise RuntimeError('--sec-continue 文件不存在: %s' % path)
        if path.lower().endswith('.md'):
            for ln in open(path, encoding='utf-8'):
                if ln.startswith('#SEC-END'):
                    m = re.search(r'q:([0-9.,;=\-]+)', ln)
                    e = re.search(r'e:([0-9.,;=\-]+)', ln)
                    for mm, tgt in ((m, qmax), (e, emax)):
                        if mm:
                            for part in mm.group(1).split(';'):
                                k, _, v = part.partition('=')
                                if k and v:
                                    tgt[k] = max(tgt.get(k, 0), int(v))
        else:
            z = zipfile.ZipFile(path)
            doc = etree.fromstring(z.read('word/document.xml'))
            z.close()
            els = list(doc.find(q('body')))
            n = len(els)
            for i, c in enumerate(els):
                if c.tag != q('p'):
                    continue
                form, tok, sec, o, _t, _g = question_form(para_text(c))
                if form is None or sec is None or o is None:
                    continue
                if form == 'bare' and not block_has_answer(els, i, n):
                    emax[sec] = max(emax.get(sec, 0), o)
                else:
                    qmax[sec] = max(qmax.get(sec, 0), o)
    return qmax, emax


def fn_counts(path):
    b = os.path.basename(path)
    mq = FN_Q_RE.search(b)
    me = FN_E_RE.search(b)
    return (int(mq.group(1)) if mq else None, int(me.group(1)) if me else None)


def migrate(path, regmd, linkage=False, qstart=1, sec_start=None, sec_start_entry=None,
            sec_continue=None, families='qe', expect=None, expect_entry=None, stats_sync=True):
    mode = 'linkage' if linkage else 'base'
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()

    body = doc.find(q('body'))
    els = list(body)
    n = len(els)

    # ---- 跨卷接续：--sec-continue 末号 → 起点（显式 --sec-start 优先） ----
    qstart_map, estart_map = {}, {}
    if sec_continue:
        qe, ee = read_prior_ends(sec_continue)
        qstart_map = {k: v + 1 for k, v in qe.items()}
        estart_map = {k: v + 1 for k, v in ee.items()}
    qstart_map.update(parse_secstart(sec_start))
    estart_map.update(parse_secstart(sec_start_entry))

    do_q = families in ('q', 'qe')
    do_e = families in ('e', 'qe')

    rows, processed = [], set()
    expected = qstart                    # 旧全局号序列门控（题族）
    seq, eseq = [], []                   # 认定序列（题/条目）：(节, 输出序号, 输入序号)
    hier_in = False
    cur_sec = None
    sec_titles = []                      # (idx, 节号)
    c_q = c_e = c_rew = c_narrow = c_degr = c_skip = c_eskip = 0
    c_runs = c_shd = c_bold = c_merged = c_txt = c_iv = 0
    grade_cnt = {'简单': 0, '中档': 0, '难': 0, '衔接必会': 0}
    anomalies = []
    counters = {}                        # 节 → 题族下一序号
    ecounters = {}                       # 节 → 条目族下一序号

    # ---- 扫描＋改写（单遍；节标题先行识别供分区） ----
    sec_pre = []
    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        txt = para_text(c).strip()
        if txt:
            s = is_section_title(c, txt)
            if s:
                sec_pre.append((i, s))
    if not sec_pre:
        raise RuntimeError('未识别到任何教材节标题（判据：节号pattern＋28半点/ADC2DA/标题3）——'
                           '层级制改版无法进行，请核对该件节标题形态')
    sec_map = dict(sec_pre)

    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        txt = para_text(c)
        if not txt:
            continue
        if i in sec_map:
            cur_sec = sec_map[i]
            sec_titles.append((i, cur_sec))
            continue
        if TITLE_RE.match(txt) or LECT_RE.match(txt):
            continue
        form, tok, isec, iord, toklen, grade = question_form(txt)
        if form is None:
            continue
        bracketed = form in ('q3', 'q1', 'ql')
        has_ans = block_has_answer(els, i, n)
        is_question = bracketed or has_ans
        if is_question and not do_q:
            continue
        if (not is_question) and not do_e:
            continue
        if mode == 'base' and form == 'ql':
            anomalies.append('第%d段为两段式形态但默认模式运行（衔接件形态×模式不符，跳过）: %s' % (i, txt[:30]))
            continue
        # —— 节归属 ——
        sec = isec if isec is not None else cur_sec
        if sec is None:
            raise RuntimeError('第%d段题号 %s 位于首个节标题之前，无节号可挂（层级制必需）: %s'
                               % (i, tok, txt[:30]))
        # —— 输入序列门控（A1 素材）——
        if isec is None:   # 旧全局号：题族全件连续（qstart..），条目族无门控（随讲部/节重启）
            if is_question:
                seq_ok = (int(tok) == expected)
                if not seq_ok and not (bracketed and has_ans):
                    continue
                expected = int(tok) + 1
        else:              # 层级制号：节内两族各自连续，起点＝续号映射（缺省1）——错位即硬失败
            hier_in = True
            if is_question:
                exp_o = counters.get(isec, qstart_map.get(isec, 1))
                if iord != exp_o:
                    raise RuntimeError('第%d段层级制题号 %s 节内期望序号 %d（节%s）——若为续卷漏参，'
                                       '请补 --sec-start/-continue；若为本卷缺号，先核漏认（块边界：【答案】/标题）'
                                       % (i, tok, exp_o, isec))
            else:
                exp_e = ecounters.get(isec, estart_map.get(isec, 1))
                if iord != exp_e:
                    raise RuntimeError('第%d段层级制条目号 %s 节内期望序号 %d（节%s）——续卷补 '
                                       '--sec-start-entry/-continue；否则先核条目漏认' % (i, tok, exp_e, isec))
        # —— 重编号＋改写 ——
        if not is_question:
            nxt = ecounters.get(sec, estart_map.get(sec, 1))
            ecounters[sec] = nxt + 1
            eseq.append((sec, nxt, iord if iord is not None else int(tok)))
            r = rewrite_entry(c, toklen, '%s-%d' % (sec, nxt))
            c_e += 1
            c_txt += (1 if r['text_changed'] else 0)
            c_shd += (1 if r['shd_added'] else 0)
            c_bold += (1 if r['bold_stripped'] else 0)
            c_merged += (1 if r['merged'] else 0)
            if r['text_changed'] or r['shd_added'] or r['bold_stripped'] or r['merged']:
                rows.append(('%s-%d' % (sec, nxt), '条目重编（%s→）＋底纹核验' % r['old_tok'], r['new_tok']))
            else:
                c_eskip += 1
                rows.append(('%s-%d' % (sec, nxt), '条目幂等跳过（已合规）', r['new_tok']))
            processed.add(i)
            continue
        nxt = counters.get(sec, qstart_map.get(sec, 1))
        counters[sec] = nxt + 1
        seq.append((sec, nxt, int(iord) if iord is not None else int(tok)))
        new_num = '%s-%d' % (sec, nxt)
        already = (tok == new_num) and _q_compliant(c)
        if already:
            c_skip += 1
            rows.append((new_num, '幂等跳过（已合规）', txt[:44]))
            processed.add(i)
            continue
        r = rewrite_question(c, mode, toklen, new_num, grade, form)
        c_runs += r['new_runs']
        c_shd += (1 if r['shd_added'] else 0)
        c_bold += (1 if r['bold_added'] else 0)
        c_merged += (1 if r['merged'] else 0)
        c_txt += (1 if r['text_changed'] else 0)
        if form == 'q1':
            rows.append((new_num, '改写（%s→三段式）＋重编＋缩底纹' % grade, r['new_tok']))
            grade_cnt[grade] += 1
            c_rew += 1
        elif mode == 'linkage':
            disp = '改两段式＋重编＋缩底纹' if form in ('q3', 'q1') else '退化补两段式（授权）＋重编＋缩底纹'
            rows.append((new_num, disp, r['new_tok']))
            grade_cnt['衔接必会'] += 1
            c_rew += 1
        elif form == 'bare':
            rows.append((new_num, '退化块重编＋缩底纹（不加括注）', r['new_tok']))
            c_degr += 1
        else:
            rows.append((new_num, '重编＋缩底纹（括注文本不变）', r['new_tok']))
            grade_cnt[grade] += 1
            c_narrow += 1
        processed.add(i)

    n_q, n_e = len(seq), len(eseq)

    # ---- 统计段区间括注联动（授权差异②：删全局题号区间括注） ----
    if stats_sync:
        for i, sec in sec_titles:
            p = els[i]
            full = para_text(p)
            for m in INTERVAL_RE.finditer(full):
                remove_span_runs(p, m.start(), m.end())
                c_iv += 1
            if INTERVAL_RE.search(para_text(p)):
                raise RuntimeError('节标题区间括注删除失败: %s' % para_text(p)[:40])

    # ---- A1 序列断言（输入侧门控汇总＋输出侧连续性） ----
    if seq and not hier_in:
        nums = [x[2] for x in seq]
        gaps = [(nums[k-1], nums[k]) for k in range(1, n_q) if nums[k] != nums[k-1] + 1]
        assert not gaps and nums[0] == qstart, '旧全局题号序列门控失败: 起=%s 期望qstart=%s 断点=%s' % (
            nums[0] if nums else None, qstart, gaps[:5])
    bysec_out = {}
    for s, o, _oi in seq:
        bysec_out.setdefault(s, []).append(o)
    for s, lst in bysec_out.items():
        st = qstart_map.get(s, 1)
        for k in range(1, len(lst)):
            assert lst[k] == lst[k-1] + 1, '节%s 题族输出序列断点 %s' % (s, lst)
        assert lst[0] == st, '节%s 题族起始=%d 期望=%d（--sec-start/-continue 续号核对）' % (s, lst[0], st)
    ebysec = {}
    for s, o, _oi in eseq:
        ebysec.setdefault(s, []).append(o)
    for s, lst in ebysec.items():
        st = estart_map.get(s, 1)
        for k in range(1, len(lst)):
            assert lst[k] == lst[k-1] + 1, '节%s 条目族输出序列断点 %s' % (s, lst)
        assert lst[0] == st, '节%s 条目族起始=%d 期望=%d' % (s, lst[0], st)

    # ---- A2 形态断言（仅认定块） ----
    for i in sorted(processed):
        c = els[i]
        txt = para_text(c)
        form, tok, _s, _o, toklen, _g = question_form(txt)
        runs = [r for r in c.findall(q('r')) if run_text(r)]
        assert runs and run_text(runs[0]) == tok + '．', 'run[0]非独立号run: %r' % txt[:30]
        s = shd_of(runs[0])
        assert s is not None and s.get(q('fill')) == FILL, '号run缺C9C9C9: %r' % txt[:30]
        rpr = runs[0].find(q('rPr'))
        assert rpr is not None, '号run缺rPr: %r' % txt[:30]
        if form == 'bare' and not _block_ans_cached(els, i, n):
            assert rpr.find(q('b')) is None, '条目号run不得加粗: %r' % txt[:30]
        else:
            assert rpr.find(q('b')) is not None, '题号run缺加粗: %r' % txt[:30]
            if form != 'bare':
                r1t = run_text(runs[1])
                assert runs[1] is not None and not shd_of(runs[1]), '括注仍挂底纹: %r' % r1t[:30]
                rpr1 = runs[1].find(q('rPr'))
                assert rpr1 is not None and rpr1.find(q('b')) is not None, '括注缺加粗: %r' % r1t[:30]
                if mode == 'linkage':
                    assert r1t == '（%s）' % LINK_BODY, '两段式括注文本不符: %r' % r1t[:30]
                else:
                    m = Q3_RE.match(txt)
                    assert m and r1t == '（%s·%s）' % (GRADE_MAP[m.group(2)], TAIL), \
                        '三段式括注文本不符: %r' % r1t[:30]

    # ---- A5 文件名题量恒等＋交叉核对 ----
    f_q, f_e = fn_counts(path)
    exp_q = expect if expect is not None else f_q
    exp_e = expect_entry if expect_entry is not None else f_e
    if exp_q is not None and exp_q != n_q:
        raise AssertionError('文件名/--expect 题量 %d ≠ 题族认定 %d（漏认/多认，见登记md）' % (exp_q, n_q))
    if exp_e is not None and exp_e != n_e:
        raise AssertionError('文件名/--expect-entry 条目数 %d ≠ 条目族认定 %d' % (exp_e, n_e))
    try:
        from extract_structure import structure
        n_x = len(structure(path)['questions'])
    except Exception as e:
        n_x = -1
        anomalies.append('extract_structure 交叉核对不可用: %s' % e)
    if n_x >= 0 and n_x != n_q:
        raise AssertionError('题号门控认定 %d ≠ extract_structure 题块 %d——须人工核查（序列已连续，'
                             '差异在漏认或多认，样例见登记md）' % (n_q, n_x))

    # ---- 落盘 ----
    new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    fd, tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(path)) or '.')
    os.close(fd)
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

    # ---- 登记 md ----
    L = []
    L.append('# 题号块层级制改版登记 — %s（模式=%s，族=%s）' % (os.path.basename(path), mode, families))
    L.append('')
    L.append('口径：2026-09-01 A\'改制轮工具债③——题号/条目号「节号-序号．」层级制（节内连续、题族与条目族分列、'
             '跨卷接续）；底纹盖整个号run（题族C9C9C9＋b、条目族C9C9C9不加粗）；节标题判据＝节号pattern＋'
             '28半点/ADC2DA/标题3（C6D4E3负判据）；' + ('衔接件两段式。' if mode == 'linkage' else
             '三段式「节号-序号．（档位·提分线·卡壳看答案）」。')
             + ('续号：--sec-start=%s --sec-start-entry=%s --sec-continue=%s；' % (sec_start, sec_start_entry, sec_continue)
                if (sec_start or sec_start_entry or sec_continue) else ''))
    L.append('')
    sec_line = ';'.join('%s=%d' % (s, bysec_out[s][-1]) for s in bysec_out)
    esec_line = ';'.join('%s=%d' % (s, ebysec[s][-1]) for s in ebysec)
    L.append('题族 %d（%s）｜条目族 %d｜授权文本改写 %d｜纯缩底纹/重编 %d｜退化 %d｜幂等跳过 题%d/条%d｜'
             '补底纹 %d｜加粗处置 %d｜区间括注删除 %d｜文件名恒等 题%s/条%s｜交叉核对 %s'
             % (n_q, sec_line, n_e, c_txt, c_narrow, c_degr, c_skip, c_eskip,
                c_shd, c_bold, c_iv,
                ('%s＝%d PASS' % (f_q, n_q)) if f_q is not None else (('expect=%d PASS' % exp_q) if exp_q is not None else '未断言（文件名无题量）'),
                ('%s＝%d PASS' % (f_e, n_e)) if f_e is not None else (('expect=%d PASS' % exp_e) if exp_e is not None else '未断言'),
                ('%d＝%d PASS' % (n_x, n_q)) if n_x >= 0 else '不可用（见异常）'))
    L.append('')
    L.append('#SEC-END q:%s e:%s' % (sec_line, esec_line or '-'))
    if mode == 'linkage':
        L.append('两段式改写 %d 处' % grade_cnt['衔接必会'])
    else:
        L.append('档位分布：简单 %d／中档 %d／难 %d' % (grade_cnt['简单'], grade_cnt['中档'], grade_cnt['难']))
    if anomalies:
        L.append('异常登记：' + '；'.join(anomalies[:20]) + ('…共%d条' % len(anomalies) if len(anomalies) > 20 else ''))
    L.append('')
    L.append('| 号 | 处置 | 终态 |')
    L.append('|---|---|---|')
    for no, disp, tok in rows:
        L.append('| %s | %s | %s |' % (no, disp, tok))
    L.append('')
    open(regmd, 'w', encoding='utf-8').write('\n'.join(L))
    print('题族 %d（%s）｜条目族 %d｜文本改写 %d｜幂等跳过 题%d/条%d｜区间括注删 %d｜'
          '文件名恒等 题%s/条%s｜A2断言 %d段全过｜交叉核对 %s'
          % (n_q, sec_line, n_e, c_txt, c_skip, c_eskip, c_iv,
             f_q if f_q is not None else (exp_q if exp_q is not None else '未断言'),
             f_e if f_e is not None else (exp_e if exp_e is not None else '未断言'),
             len(processed), ('%d＝%d PASS' % (n_x, n_q)) if n_x >= 0 else 'N/A'))
    print('登记md -> %s' % regmd)


def _block_ans_cached(els, i, n):
    return block_has_answer(els, i, n)


def _q_compliant(p):
    """幂等判定：run[0]恰为号token（含全角句点）挂C9C9C9＋rPr存在（细形态由A2断言兜底）。"""
    runs = [r for r in p.findall(q('r')) if run_text(r)]
    if not runs:
        return False
    txt = para_text(p)
    m = NUMTOK_RE.match(txt)
    if not m or run_text(runs[0]) != m.group(1) + '．':
        return False
    s = shd_of(runs[0])
    if s is None or s.get(q('fill')) != FILL:
        return False
    return runs[0].find(q('rPr')) is not None


if __name__ == '__main__':
    argv = sys.argv[1:]
    linkage = '--linkage' in argv
    argv = [a for a in argv if a != '--linkage']
    qstart = 1
    if '--qstart' in argv:
        k = argv.index('--qstart'); qstart = int(argv[k + 1]); del argv[k:k + 2]
    sec_start = sec_start_entry = sec_continue = None
    if '--sec-start' in argv:
        k = argv.index('--sec-start'); sec_start = argv[k + 1]; del argv[k:k + 2]
    if '--sec-start-entry' in argv:
        k = argv.index('--sec-start-entry'); sec_start_entry = argv[k + 1]; del argv[k:k + 2]
    if '--sec-continue' in argv:
        k = argv.index('--sec-continue'); sec_continue = argv[k + 1]; del argv[k:k + 2]
    families = 'qe'
    if '--families' in argv:
        k = argv.index('--families'); families = argv[k + 1]; del argv[k:k + 2]
        assert families in ('q', 'e', 'qe'), '--families 须为 q/e/qe'
    expect = expect_entry = None
    if '--expect' in argv:
        k = argv.index('--expect'); expect = int(argv[k + 1]); del argv[k:k + 2]
    if '--expect-entry' in argv:
        k = argv.index('--expect-entry'); expect_entry = int(argv[k + 1]); del argv[k:k + 2]
    stats_sync = '--no-stats-sync' not in argv
    argv = [a for a in argv if a != '--no-stats-sync']
    migrate(argv[0], argv[1], linkage=linkage, qstart=qstart, sec_start=sec_start,
            sec_start_entry=sec_start_entry, sec_continue=sec_continue, families=families,
            expect=expect, expect_entry=expect_entry, stats_sync=stats_sync)
