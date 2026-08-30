# -*- coding: utf-8 -*-
"""题号块三段式.py — 2026-08-30 拍板「档位·提分线·卡壳看答案」三段改写（可复用，幂等）

口径（公共规则§7题号难度块底纹条款＋高中同步总控2.1提分线三形态，2026-08-30用户拍板）：
  题号块「N．（档位）」→「N．（档位·提分线·卡壳看答案）」——
    档位·提分线映射：简单→简单·保60%｜中档→中档·保80%｜难→难·冲100%（与三档分数目标
    一一对应：简单≈60%、简单＋中档≈80%、难＝冲击满分）；第三段固定「卡壳看答案」（逐题相同）；
    全角间隔点「·」。例：「5．（中档·保80%·卡壳看答案）」。
  形态：题号块保持单run形态＋原底纹（w:shd C9C9C9）＋加粗——整块（题号＋括注）同受题号块底纹；
    与题干同run粘连的先拆出独立run（拆出的题干run剥底纹——底纹只盖题号块本身）；
    跨多run碎裂的序号先归并回收首run（零字符、顺序不变）再改写。
  幂等：已三段形态（N．（档位·提分线·卡壳看答案））自动跳过；退化题号块「N．」无括注跳过并登记。
  断言：改写数＋幂等跳过数＝档位题号块数（改写前后）；改写后无单段括注残留
    （全文级扫描「（简单）」「（中档）」「（难）」计0）；逐段期望文本断言（改写后段落文本＝
    改写前文本按映射精确替换，防误伤他处）；与 extract_structure 题块数交叉核对并落盘。
用法: python 工具/题号块三段式.py <docx> <登记md>
输出: 登记md（计数＋逐题映射表）＋stdout 断言结果。
"""
import sys, os, re, zipfile, time, copy, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
FILL = 'C9C9C9'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

GRADE_MAP = {'简单': '简单·保60%', '中档': '中档·保80%', '难': '难·冲100%'}
TAIL = '卡壳看答案'
ONE_RE = re.compile(r'^(\d+)．（(简单|中档|难)）')                       # 单段括注（待改写）
THREE_RE = re.compile(r'^(\d+)．（(简单|中档|难)·(保60%|保80%|冲100%)·' + TAIL + r'）')  # 已三段（幂等跳过）
DEGR_RE = re.compile(r'^(\d+)．(?!（)')                                  # 退化题号块（N．无括注）
RESID_RE = re.compile(r'（简单）|（中档）|（难）')                        # 单段括注残留（全文级）

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def body_paras(doc):
    body = doc.find(q('body'))
    for p in body.findall(q('p')):
        yield p
    # 表格内段落不产题号块（题号块均在正文层），此处只扫正文层；全文残留扫描另行 p.iter 全覆盖

def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))

def set_run_text(r, s):
    ts = r.findall(q('t'))
    ts[0].text = s
    ts[0].set(XMLSPACE, 'preserve')
    for t in ts[1:]:
        t.text = ''

def shd_of(r):
    rpr = r.find(q('rPr'))
    return rpr.find(q('shd')) if rpr is not None else None

def strip_shd(r):
    rpr = r.find(q('rPr'))
    if rpr is not None:
        s = rpr.find(q('shd'))
        if s is not None:
            rpr.remove(s)

def ensure_qnum_rpr(r):
    """题号块 run 补加粗＋底纹 C9C9C9（缺才补）。返回 (补底纹, 补加粗)。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    bold = False
    if rpr.find(q('b')) is None:
        rpr.insert(0, etree.Element(q('b')))
        bold = True
    shd_added = False
    if rpr.find(q('shd')) is None:
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
        rpr.append(shd)
        shd_added = True
    return shd_added, bold

def rewrite_token(p, m):
    """把段首题号块 token [0,L) 改写为三段式，保持单run形态＋原rPr（补缺加粗/底纹）。
    返回 (新token文本, 拆run数, 补底纹, 补加粗)。调用方保证 m 为 ONE_RE 且整段未三段。"""
    no, grade = int(m.group(1)), m.group(2)
    new_tok = '%d．（%s·%s）' % (no, GRADE_MAP[grade], TAIL)
    L = m.end()
    before = para_text(p)
    runs = [c for c in p if tag(c) == 'r']
    assert runs, '段内无文本run: %r' % before[:30]
    # 覆盖 [0,L) 的 run 集合
    covered, off = [], 0
    for r in runs:
        tx = run_text(r)
        if not tx:
            continue
        covered.append((r, tx))
        off += len(tx)
        if off >= L:
            break
    assert covered and sum(len(tx) for _, tx in covered) >= L, '题号块token跨run碎裂超限: %r' % before[:30]
    first_r, first_tx = covered[0]
    # 多run归并回收首run（零字符、顺序不变）
    if len(covered) > 1:
        set_run_text(first_r, ''.join(tx for _, tx in covered))
        for r, _ in covered[1:]:
            p.remove(r)
    # 越界拆分：token 与题干粘连同run → 拆出题干独立run（剥底纹）
    n_split = 0
    cur = run_text(first_r)
    if len(cur) > L:
        rest = cur[L:]
        set_run_text(first_r, cur[:L])
        nr = copy.deepcopy(first_r)
        set_run_text(nr, rest)
        strip_shd(nr)
        first_r.addnext(nr)
        n_split = 1
    assert run_text(first_r) == m.group(0), 'token隔离失败: %r' % run_text(first_r)
    set_run_text(first_r, new_tok)
    shd_added, bold_added = ensure_qnum_rpr(first_r)
    # 期望文本断言：整段文本＝改写前按映射精确替换
    assert para_text(p) == before[:m.start()] + new_tok + before[m.end():], \
        '改写后期望文本不符: %r' % para_text(p)[:50]
    return new_tok, n_split, shd_added, bold_added

def migrate(path, regmd):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()

    # 题块判定以 extract_structure 为源（题号段→下一题号段/标题前＋块内【答案】；
    # 讲部条目「N．」无【答案】不入题块，天然排除）——题号块集合＝questions 的起段。
    from extract_structure import structure
    st = structure(path)
    body = doc.find(q('body'))
    els = list(body)
    qstarts = {x['start'] for x in st['questions']}
    n_q = len(st['questions'])

    rows, n_new, n_skip, n_degr = [], 0, 0, 0
    n_split = n_shd = n_bold = 0
    grade_cnt = {k: 0 for k in GRADE_MAP}
    for idx in sorted(qstarts):
        p = els[idx]
        txt = para_text(p)
        m3 = THREE_RE.match(txt)
        if m3:
            n_skip += 1
            rows.append((int(m3.group(1)), '跳过（已三段）', m3.group(0)))
            continue
        m1 = ONE_RE.match(txt)
        if m1:
            no, g = int(m1.group(1)), m1.group(2)
            tok, sp, sa, ba = rewrite_token(p, m1)
            rows.append((no, '改写（%s）' % g, tok))
            n_new += 1; n_split += sp; n_shd += (1 if sa else 0); n_bold += (1 if ba else 0)
            grade_cnt[g] += 1
            continue
        if DEGR_RE.match(txt):
            n_degr += 1   # 退化题号块（无档位括注），跳过登记
    # ---- 断言 ----
    # ①改写后全文：三段数＝改写数＋改写前三段数；单段括注残留=0（全文级含表格）
    n_three_after = sum(1 for p in doc.iter(q('p')) if THREE_RE.match(para_text(p)))
    n_one_after = sum(1 for p in doc.iter(q('p')) if ONE_RE.match(para_text(p)))
    n_resid = sum(len(RESID_RE.findall(para_text(p))) for p in doc.iter(q('p')))
    assert n_one_after == 0, '单段括注残留 %d 处' % n_one_after
    assert n_resid == 0, '单段括注字面残留 %d 处' % n_resid
    n_tok_before = n_new + n_skip
    assert n_three_after == n_tok_before, '三段数 %d ≠ 题号块数 %d' % (n_three_after, n_tok_before)
    if n_degr == 0 and n_tok_before != n_q:
        raise AssertionError('档位题号块数 %d ≠ extract题块数 %d（存在漏配形态，须人工核查）'
                             % (n_tok_before, n_q))
    # ②每个三段token：恰一个独立run承载全token、加粗、C9C9C9
    for p in doc.iter(q('p')):
        txt = para_text(p)
        m = THREE_RE.match(txt)
        if not m:
            continue
        carry = [r for r in p.findall(q('r')) if run_text(r) == m.group(0)]
        assert len(carry) == 1, 'token非单run承载: %r %d' % (m.group(0), len(carry))
        rpr = carry[0].find(q('rPr'))
        assert rpr is not None and rpr.find(q('b')) is not None, 'token缺加粗: %r' % m.group(0)
        assert shd_of(carry[0]) is not None and shd_of(carry[0]).get(q('fill')) == FILL, \
            'token缺C9C9C9底纹: %r' % m.group(0)
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
    L.append('# 题号块三段式改写登记 — %s' % os.path.basename(path))
    L.append('')
    L.append('口径：2026-08-30 拍板——「N．（档位）」→「N．（档位·提分线·卡壳看答案）」；'
             '简单·保60%／中档·保80%／难·冲100%＋固定第三段「卡壳看答案」；'
             '保持单run形态＋原C9C9C9底纹＋加粗；幂等（已三段跳过）；退化「N．」跳过登记。')
    L.append('')
    L.append('档位题号块数 %d（改写 %d＋已三段幂等跳过 %d）｜退化题号块（N．无括注）%d｜'
             '简单 %d／中档 %d／难 %d｜拆run（题干粘连剥离）%d｜补底纹 %d｜补加粗 %d｜'
             '改写后三段数 %d＝题号块数 ✓｜单段括注残留 0（全文级扫描）✓｜'
             'extract_structure题块数 %d%s'
             % (n_tok_before, n_new, n_skip, n_degr, grade_cnt['简单'], grade_cnt['中档'],
                grade_cnt['难'], n_split, n_shd, n_bold, n_three_after, n_q,
                '' if (n_degr > 0 or n_q == n_three_after) else '（≠三段数，请人工核查）'))
    L.append('')
    L.append('| 题号 | 处置 | 题号块终态 |')
    L.append('|---|---|---|')
    for no, disp, tok in rows:
        L.append('| %d | %s | %s |' % (no, disp, tok))
    L.append('')
    open(regmd, 'w', encoding='utf-8').write('\n'.join(L))
    print('题号块 %d＝改写 %d＋幂等跳过 %d｜退化 %d｜简单%d/中档%d/难%d｜拆run%d 补底纹%d 补加粗%d｜'
          '三段终态 %d｜残留 0｜extract题块 %d'
          % (n_tok_before, n_new, n_skip, n_degr, grade_cnt['简单'], grade_cnt['中档'], grade_cnt['难'],
             n_split, n_shd, n_bold, n_three_after, n_q))
    print('登记md -> %s' % regmd)

if __name__ == '__main__':
    migrate(sys.argv[1], sys.argv[2])
