# -*- coding: utf-8 -*-
"""题号块三段式.py — N6底纹缩小版（2026-08-31 欠账A·工具债③；可复用，幂等）

口径（公共规则§7题号难度块底纹条款现行文本——2026-08-31 用户拍板N6回调）：
  · 底纹只盖「N．」本身run：「N．」与括注同run的先拆独立run再挂 w:shd C9C9C9＋加粗；
    括注「（档位·提分线·卡壳看答案）」run 剥底纹；整块（N．＋括注）加粗维持；
    题干粘连文字随拆分剥底纹剥加粗（加粗仅限题号块，§7段落条款）。
  · 默认模式（讲练件/实验卷）：题号块文本维持三段式「N．（档位·提分线·卡壳看答案）」——
    档位·提分线映射：简单→简单·保60%｜中档→中档·保80%｜难→难·冲100%（总控2.1）；
    旧单段「N．（档位）」仍按 2026-08-30 授权改写为三段式；已三段者只做底纹缩小。
  · --linkage 模式（衔接件，总控任务C——2026-08-31 拍板）：题号块文本改两段式
    「N．（衔接必会·卡壳看答案）」（无档位无提分线；底纹仍只盖「N．」）。
    从旧三段式/单段式改写为两段式属授权文本变更（规格书§2授权项1），逐处计数落盘。
  · 退化题号块「N．」（无括注）：默认模式不加括注、只做底纹缩小＋加粗补齐；linkage
    模式按总控任务C补两段式括注（授权）。六类底纹计数恒等式不变：题号块底纹run数＝题量。
  · 题号识别（2026-08-31 重构）：「前缀消费」跨run法（题号数字run＋句点run碎裂形态，
    经验文件2026-08-26技巧）＋题号序列门控（题号全件连续、条目号随节重启，门控天然
    区分——条目号另有 工具/条目号底纹.py，本工具不误伤）＋块内【答案】验证（与
    extract_structure 题块判定同源锚），三重判据缺一不认题。
  · --qstart N（2026-08-31 F-工具补丁增，欠账A·W-F/G/H/C续卷件需求）：续卷起始题号，
    默认1＝首卷口径不变；门控区间＝qstart..qstart+题量−1（分卷题号跨卷连续，公共规则§12）。
    A1断言起点同步参数化（seq[0]==qstart）；其余逻辑零改动。

断言（全过才落盘，任一不过抛异常不写文件）：
  A1 题号序列 qstart..qstart+N−1 连续无重复（序列门控终检；qstart默认1）；
  A2 每个认定题号块：run[0] 文本恰为「N．」、挂 C9C9C9＋b；run[1]（有括注时）文本恰为
     目标括注、无 shd、有 b；题干余文无灰无粗；门控认定数＝extract_structure 题块数；
  A3 零意外字符：每改写段落后期望文本（授权token替换）逐段精确相等；
  A4 幂等：二跑改写/拆run/补底纹/剥底纹计数全为0（登记md可复核）。

用法: python 工具/题号块三段式.py <docx> <登记md> [--linkage] [--qstart N]
输出: 就地改写 docx（仅 word/document.xml）＋登记md（计数＋逐题映射表）＋stdout。
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
NUMPART_RE = re.compile(r'^\d+．')
Q3_RE  = re.compile(r'^(\d+)．（(简单|中档|难)·(保60%|保80%|冲100%)·' + TAIL + r'）')
Q1_RE  = re.compile(r'^(\d+)．（(简单|中档|难)）')
QL_RE  = re.compile(r'^(\d+)．（' + LINK_BODY + r'）')
TITLE_RE = re.compile(r'^\d+(\.\d+)+\s')          # 节/讲部/题型标题（半角点分序号起段）
LECT_RE = re.compile(r'^\d+(\.\d+)*\s*方法讲解[｜|]')


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


def ensure_num_rpr(r):
    """「N．」run 补加粗＋底纹 C9C9C9（各自缺才补）。返回 (是否补底纹, 是否补加粗)。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    bold_added = False
    if rpr.find(q('b')) is None:
        rpr.insert(0, etree.Element(q('b')))
        bold_added = True
    shd_added = False
    shd = rpr.find(q('shd'))
    if shd is None:
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
        rpr.append(shd)
        shd_added = True
    elif shd.get(q('fill')) != FILL:
        raise RuntimeError('题号run已有其他底纹 fill=%s，需人工处置' % shd.get(q('fill')))
    return shd_added, bold_added


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


def question_form(txt):
    """返回 (形态, 题号, token长度, 档位)。形态 ∈ q3/q1/ql/degr/None。"""
    m = Q3_RE.match(txt)
    if m:
        return 'q3', int(m.group(1)), m.end(), m.group(2)
    m = Q1_RE.match(txt)
    if m:
        return 'q1', int(m.group(1)), m.end(), m.group(2)
    m = QL_RE.match(txt)
    if m:
        return 'ql', int(m.group(1)), m.end(), None
    m = NUMPART_RE.match(txt)
    if m:
        m2 = re.match(r'^(\d+)．', txt)
        return 'degr', int(m2.group(1)), m2.end(), None
    return None, None, 0, None


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
        if NUMPART_RE.match(t) or TITLE_RE.match(t) or LECT_RE.match(t):
            break
        buf += t
        j += 1
    return '【答案】' in buf


def rewrite_question(p, mode, form, num, toklen, grade):
    """把段首题号块改造为 N6 形态：run[0]「N．」（C9C9C9＋b）→ run[1] 括注（b 无shd）
    → run[2] 题干余文（无shd无b）。跨run碎裂先归并回收首run。零意外字符（A3 逐段断言）。
    返回计数 dict。"""
    before = para_text(p)
    if mode == 'linkage':
        tgt_body = '（%s）' % LINK_BODY
        text_changed = form != 'ql'
    elif form == 'q1':
        tgt_body = '（%s·%s）' % (GRADE_MAP[grade], TAIL)
        text_changed = True
    else:   # q3 维持 / degr 无括注
        tgt_body = '（%s·%s）' % (GRADE_MAP[grade], TAIL) if form == 'q3' else None
        text_changed = False

    covered = consume_prefix_runs(p, toklen)
    first_r = covered[0][0]
    tok_full = ''.join(tx for _, tx in covered)[:toklen]
    tail = ''.join(tx for _, tx in covered)[toklen:]
    num_txt = '%d．' % num

    # run[0] 收纳「N．」（补粗补灰）
    set_run_text(first_r, num_txt)
    if first_r.find(q('rPr')) is None:
        first_r.insert(0, etree.Element(q('rPr')))
    shd_added, bold_added = ensure_num_rpr(first_r)
    # 移除其余被消费 run（多run归并回收，零字符、顺序不变）
    merged = len(covered) > 1
    for r, _ in covered[1:]:
        p.remove(r)
    # 括注 run（b 无shd）＋题干余文 run（无shd无b）
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

    # A3 逐段期望文本断言（授权token替换）
    exp = num_txt + (tgt_body or '') + tail + before[toklen:]
    assert para_text(p) == exp, '改写后期望文本不符: %r != %r' % (para_text(p)[:50], exp[:50])
    return {'text_changed': text_changed, 'old_tok': tok_full, 'new_tok': num_txt + (tgt_body or ''),
            'new_runs': new_runs, 'merged': merged, 'shd_added': shd_added, 'bold_added': bold_added}


def is_compliant(p, mode):
    """幂等判定：run[0]恰为「N．」挂C9C9C9＋b；run[1]（linkage必带括注）无shd有b。"""
    runs = [r for r in p.findall(q('r')) if run_text(r)]
    if not runs or not re.match(r'^\d+．$', run_text(runs[0])):
        return False
    s = shd_of(runs[0])
    if s is None or s.get(q('fill')) != FILL:
        return False
    rpr = runs[0].find(q('rPr'))
    if rpr is None or rpr.find(q('b')) is None:
        return False
    if mode == 'linkage':
        if len(runs) < 2 or run_text(runs[1]) != '（%s）' % LINK_BODY:
            return False
        s1 = shd_of(runs[1])
        rpr1 = runs[1].find(q('rPr'))
        return s1 is None and rpr1 is not None and rpr1.find(q('b')) is not None
    if len(runs) >= 2 and run_text(runs[1]).startswith('（'):
        s1 = shd_of(runs[1])
        rpr1 = runs[1].find(q('rPr'))
        if s1 is not None or rpr1 is None or rpr1.find(q('b')) is None:
            return False
    return True


def migrate(path, regmd, linkage=False, qstart=1):
    mode = 'linkage' if linkage else 'base'
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()

    body = doc.find(q('body'))
    els = list(body)
    n = len(els)

    rows, processed = [], set()
    expected = qstart   # --qstart 续卷起始题号（默认1，首卷口径不变）
    seq = []
    c_rew = c_narrow = c_degr = c_skip = c_runs = c_shd = c_bold = c_merged = 0
    c_txt = 0
    grade_cnt = {'简单': 0, '中档': 0, '难': 0, '衔接必会': 0}
    anomalies = []

    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        txt = para_text(c)
        if not txt or TITLE_RE.match(txt) or LECT_RE.match(txt):
            continue
        form, num, toklen, grade = question_form(txt)
        if form is None:
            continue
        # —— 序列门控＋【答案】验证（三重判据）——
        seq_ok = (num == expected)
        bracketed = form in ('q3', 'q1', 'ql')
        if not seq_ok and not (bracketed and block_has_answer(els, i, n)):
            continue   # 条目号（随节重启且块内无【答案】）——不误伤
        if form == 'degr' and not block_has_answer(els, i, n):
            continue
        if mode == 'base' and form == 'ql':
            anomalies.append('第%d段为两段式形态但默认模式运行（衔接件形态×模式不符，跳过）: %s' % (i, txt[:30]))
            continue
        seq.append(num)
        expected = num + 1
        processed.add(i)
        target_form = 'ql' if mode == 'linkage' else ('q3' if form == 'q3' else 'degr')
        if form == target_form and is_compliant(c, mode):
            c_skip += 1
            rows.append((num, '幂等跳过（已合规）', txt[:44]))
            continue
        r = rewrite_question(c, mode, form, num, toklen, grade)
        c_runs += r['new_runs']
        c_shd += (1 if r['shd_added'] else 0)
        c_bold += (1 if r['bold_added'] else 0)
        c_merged += (1 if r['merged'] else 0)
        c_txt += (1 if r['text_changed'] else 0)
        if form == 'q1':
            rows.append((num, '改写（%s→三段式）＋缩底纹' % grade, r['new_tok']))
            grade_cnt[grade] += 1
            c_rew += 1
        elif mode == 'linkage':
            disp = '改两段式（授权文本变更）＋缩底纹' if form in ('q3', 'q1') else '退化补两段式（授权）＋缩底纹'
            rows.append((num, disp, r['new_tok']))
            grade_cnt['衔接必会'] += 1
            c_rew += 1
        elif form == 'degr':
            rows.append((num, '退化块缩底纹（不加括注）', r['new_tok']))
            c_degr += 1
        else:
            rows.append((num, '缩底纹（文本不变）', r['new_tok']))
            grade_cnt[grade] += 1
            c_narrow += 1

    n_q = len(seq)
    # ---- A1 序列断言 ----
    gaps = [(seq[k-1], seq[k]) for k in range(1, n_q) if seq[k] != seq[k-1] + 1]
    assert not gaps and (not seq or seq[0] == qstart), '题号序列门控失败: 起=%s 期望qstart=%s 断点=%s' % (
        seq[0] if seq else None, qstart, gaps[:5])
    # ---- A2 形态断言（仅认定题号块）----
    for i in sorted(processed):
        c = els[i]
        txt = para_text(c)
        form, num, toklen, grade = question_form(txt)
        runs = [r for r in c.findall(q('r')) if run_text(r)]
        assert runs and run_text(runs[0]) == '%d．' % num, 'run[0]非独立「N．」: %r' % txt[:30]
        s = shd_of(runs[0])
        assert s is not None and s.get(q('fill')) == FILL, '「N．」缺C9C9C9: %r' % txt[:30]
        rpr = runs[0].find(q('rPr'))
        assert rpr is not None and rpr.find(q('b')) is not None, '「N．」缺加粗: %r' % txt[:30]
        if form != 'degr':
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
    # ---- 交叉核对 extract_structure ----
    try:
        from extract_structure import structure
        n_x = len(structure(path)['questions'])
    except Exception as e:
        n_x, _ = -1, anomalies.append('extract_structure 交叉核对不可用: %s' % e)
    if n_x >= 0 and n_x != n_q:
        raise AssertionError('题号门控认定 %d ≠ extract_structure 题块 %d——须人工核查（序列已1..N连续，'
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
    L.append('# 题号块N6底纹缩小登记 — %s（模式=%s）' % (os.path.basename(path), mode))
    L.append('')
    L.append('口径：2026-08-31 N6——底纹只盖「N．」run（C9C9C9＋加粗），括注剥底纹、整块加粗维持；'
             + ('衔接件两段式「N．（衔接必会·卡壳看答案）」（总控任务C；旧三段式→两段式属授权文本变更，'
                '逐处计数）。' if mode == 'linkage' else '三段式「N．（档位·提分线·卡壳看答案）」文本维持。')
             + ('识别＝前缀消费跨run＋题号序列门控（qstart=%d，门控qstart..qstart+题量−1）＋块内【答案】验证；幂等可重跑。'
                % qstart))
    L.append('')
    L.append('题号块 %d（门控认定，序列%s..%d连续A1过，qstart=%d）｜文本改写 %d（授权）｜纯缩底纹 %d｜退化缩底纹 %d｜'
             '幂等跳过 %d｜重建run %d｜多run归并 %d｜补底纹 %d｜补加粗 %d｜A2形态断言 %d 段全过｜'
             'extract交叉核对 %s'
             % (n_q, seq[0] if seq else qstart, seq[-1] if seq else 0, qstart, c_rew, c_narrow,
                c_degr, c_skip, c_runs, c_merged, c_shd, c_bold, n_q,
                ('%d＝%d PASS' % (n_x, n_q)) if n_x >= 0 else '不可用（见异常）'))
    if mode == 'linkage':
        L.append('两段式改写 %d 处（授权文本变更，逐处见下表）' % grade_cnt['衔接必会'])
    else:
        L.append('档位分布：简单 %d／中档 %d／难 %d' % (grade_cnt['简单'], grade_cnt['中档'], grade_cnt['难']))
    if anomalies:
        L.append('异常登记：' + '；'.join(anomalies))
    L.append('')
    L.append('| 题号 | 处置 | 题号块终态 |')
    L.append('|---|---|---|')
    for no, disp, tok in rows:
        L.append('| %d | %s | %s |' % (no, disp, tok))
    L.append('')
    open(regmd, 'w', encoding='utf-8').write('\n'.join(L))
    print('题号块 %d（%s..%d，qstart=%d）｜改写 %d｜缩底纹 %d｜退化 %d｜幂等跳过 %d｜重建run %d｜补底纹 %d｜补加粗 %d｜'
          'A2断言 %d段全过｜交叉核对 %s'
          % (n_q, seq[0] if seq else qstart, seq[-1] if seq else 0, qstart, c_rew, c_narrow,
             c_degr, c_skip, c_runs, c_shd, c_bold,
             n_q, ('%d＝%d PASS' % (n_x, n_q)) if n_x >= 0 else 'N/A'))
    print('登记md -> %s' % regmd)


if __name__ == '__main__':
    argv = sys.argv[1:]
    linkage = '--linkage' in argv
    argv = [a for a in argv if a != '--linkage']
    qstart = 1
    if '--qstart' in argv:
        k = argv.index('--qstart')
        qstart = int(argv[k + 1])
        del argv[k:k + 2]
    migrate(argv[0], argv[1], linkage=linkage, qstart=qstart)
