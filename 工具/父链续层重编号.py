# -*- coding: utf-8 -*-
"""父链续层重编号.py — 标题父链续层编号改写＋层级缩进挂载（2026-08-29 成书形态拍板§6题型编号；
公共规则§6「题型编号」/§3.3-3.4 配套工具；可复用，幂等重跑安全——同输入重跑只重写为相同终态）

输入：docx＋标题清单JSON（结构代理产出），每标题一项：
    [{"旧文本": "1.1.1 空间向量及其运算：空间向量的概念辨析", "类型": "节|讲部|题型", "新序号": "1.1.1.1",
      "缩进": 200}, ...]   （「缩进」可选覆盖；缺省按 2026-08-30 缩进梯子：二级节0＝顶格摘 ind／
      三级节200／讲部400／题型＝800（父号＝其前最近讲部序号，讲部下）或400（节下直挂））
行为：
  · 逐条匹配正文段（先全文精确匹配，再按「剥前导序号后的标题文字」唯一匹配）；一条恰配一段、
    一段至多一条；
  · 改写段首序号文本为「新序号＋单半角空格」（无前导序号的段前插序号）；标题文字其余部分零变更
    （断言：除序号段外逐字符一致）；
  · 按类型挂 w:ind leftChars（节＝摘除顶格）；只动标题段；
  · 内置断言（不过即拒改落盘）：①序号池无重复；②讲部/题型链连续——每节内直挂子元素（讲部 k＋
    直挂题型 k 共享同一序池）文档序 k=1,2,…连续，讲部内题型 j=1,2,…连续；③父链一致（讲部/题型
    父号必须恰为本清单内某节/讲部的新序号）；④无裸「大招讲解/方法讲解」段残留。
输出：改号后 docx（原地落盘）＋编号映射表 md（类型｜旧号→新号｜缩进｜标题全文）。
用法: python 父链续层重编号.py <docx> <标题清单.json> <映射表.md>
"""
import sys, io, os, re, json, zipfile, time, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

NUM_RE = re.compile(r'^(\d+(?:\.\d+)*)([ \t\u3000]*)')
BARE_LECT_RE = re.compile(r'^\s*(大招讲解|方法讲解)\s*$')
KINDS = ('节', '讲部', '题型')

PPR_AFTER_IND = ('contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection',
                 'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr',
                 'sectPr', 'pPrChange')

def ptext(p):
    return ''.join(e.text or '' for e in p.iter() if tag(e) == 't' and e.text)

def strip_num(t):
    m = NUM_RE.match(t)
    return t[m.end():] if m else t

def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))

def set_run_text(r, s):
    ts = r.findall(q('t'))
    if ts:
        ts[0].text = s
        ts[0].set(XMLSPACE, 'preserve')
        for t in ts[1:]:
            t.text = ''
    else:
        t = etree.SubElement(r, q('t'))
        t.text = s
        t.set(XMLSPACE, 'preserve')

def replace_prefix(p, old_end, new_prefix):
    """把段首 [0,old_end) 字符整体替换为 new_prefix（跨 run 归并；其余文字零变更）。
    old_end=0（无前导序号）时在段首插入承载 run（克隆首个文本 run 的 rPr）。"""
    import copy
    runs = [c for c in p if tag(c) == 'r']
    covered = []
    off = 0
    for r in runs:
        tx = run_text(r)
        if not tx:
            continue
        covered.append((r, tx))
        off += len(tx)
        if off >= old_end:
            break
    if old_end == 0:
        assert covered, '标题段无文本 run，无法插入序号'
        base = covered[0][0]
        nr = copy.deepcopy(base)
        set_run_text(nr, new_prefix)
        nrpr = nr.find(q('rPr'))
        if nrpr is not None:            # 序号 run 随后由 节标题序号底纹.py 独立挂底纹，此处保持原 rPr
            pass
        base.addprevious(nr)
        return
    assert covered and off >= old_end, '前导序号未落在文本run内'
    first_r = covered[0][0]
    total = sum(len(tx) for _, tx in covered)
    last_r, last_tx = covered[-1]
    if total > old_end:                  # 末覆盖 run 越界拆分：保留序号后文字
        cut = old_end - (total - len(last_tx))
        rest = last_tx[cut:]
        set_run_text(last_r, last_tx[:cut])
        nr = copy.deepcopy(last_r)
        set_run_text(nr, rest)
        nrpr = nr.find(q('rPr'))
        if nrpr is not None:
            nshd = nrpr.find(q('shd'))
            if nshd is not None:
                nrpr.remove(nshd)
        last_r.addnext(nr)
    set_run_text(first_r, new_prefix)
    for r, _ in covered[1:]:
        p.remove(r)

def set_indent(p, left_chars):
    ppr = p.find(q('pPr'))
    ind = ppr.find(q('ind')) if ppr is not None else None
    if left_chars in (None, 0):
        if ind is not None:
            ppr.remove(ind)
        return
    if ppr is None:
        ppr = etree.Element(q('pPr')); p.insert(0, ppr)
    if ind is None:
        ind = etree.Element(q('ind'))
        anchor = next((c for c in ppr if tag(c) in PPR_AFTER_IND), None)
        anchor.addprevious(ind) if anchor is not None else ppr.append(ind)
    for a in (q('left'), q('start')):
        if a in ind.attrib:
            del ind.attrib[a]
    ind.set(q('leftChars'), str(left_chars))

def load_titles(js):
    data = json.load(open(js, encoding='utf-8'))
    titles = data['titles'] if isinstance(data, dict) else data
    out = []
    for t in titles:
        assert t.get('类型') in KINDS and t.get('新序号'), 'JSON 条目缺类型/新序号: %r' % t
        out.append({'旧文本': t['旧文本'], '类型': t['类型'], '新序号': str(t['新序号']),
                    '缩进': t.get('缩进')})
    return out

def renumber(path, js, mapmd):
    titles = load_titles(js)
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)
    # ① 匹配：先精确全文，再剥序号唯一匹配
    paras = [(i, p, ptext(p)) for i, p in enumerate(els) if p.tag == q('p')]
    exact = {}
    for t in titles:
        for i, p, tx in paras:
            if tx == t['旧文本']:
                exact[id(t)] = (i, p, tx)
                break
    stripped_idx = {}
    for i, p, tx in paras:
        stripped_idx.setdefault(strip_num(tx).strip(), []).append((i, p, tx))
    used = set()
    matched = []   # (doc序, entry, para, 旧文本)
    for t in titles:
        if id(t) in exact:
            i, p, tx = exact[id(t)]
        else:
            cand = [c for c in stripped_idx.get(strip_num(t['旧文本']).strip(), []) if c[0] not in used]
            assert len(cand) == 1, '旧文本匹配段数=%d（预期1，精确与剥号均未唯一命中）: %r' % (len(cand), t['旧文本'][:30])
            i, p, tx = cand[0]
        assert i not in used, '同一段被两条标题清单命中: %r' % tx[:30]
        used.add(i)
        matched.append((i, t, p, tx))
    matched.sort(key=lambda x: x[0])
    # ② 序号池唯一
    pool = [t['新序号'] for _, t, _, _ in matched]
    dup = sorted({n for n in pool if pool.count(n) > 1})
    assert not dup, '序号池重复: %r' % dup
    # ③ 链连续＋父链一致（以新序号与文档序判定）
    secnums = {t['新序号'] for _, t, _, _ in matched if t['类型'] == '节'}
    lecnums = {t['新序号'] for _, t, _, _ in matched if t['类型'] == '讲部'}
    cur_sec = None
    cur_lec = None
    direct = {}     # 节号 -> [(doc序, k)]
    under = {}      # 讲部号 -> [(doc序, j)]
    for i, t, p, tx in matched:
        num = t['新序号']
        if t['类型'] == '节':
            cur_sec, cur_lec = num, None
            assert num not in secnums - {num} or True
            continue
        assert cur_sec, '讲部/题型前无节标题（父链断裂）: %r' % num
        assert num.startswith(cur_sec + '.'), '父链不一致: %s 不在当前节 %s 下' % (num, cur_sec)
        rest = num[len(cur_sec) + 1:]
        parts = rest.split('.')
        if t['类型'] == '讲部':
            assert len(parts) == 1 and parts[0].isdigit(), '讲部序号形态异常（应为 节号.k）: %s' % num
            direct.setdefault(cur_sec, []).append((i, int(parts[0])))
            cur_lec = num
        else:  # 题型
            if len(parts) == 1 and parts[0].isdigit():          # 节下直挂：节号.k
                direct.setdefault(cur_sec, []).append((i, int(parts[0])))
                cur_lec = None
            elif len(parts) == 2 and all(x.isdigit() for x in parts):   # 讲部下：讲部号.j
                lec_num = cur_sec + '.' + parts[0]
                assert lec_num in lecnums, '题型 %s 的父讲部 %s 不在清单' % (num, lec_num)
                under.setdefault(lec_num, []).append((i, int(parts[1])))
                cur_lec = lec_num
            else:
                raise AssertionError('题型序号形态异常（节号.k 或 讲部号.j）: %s' % num)
    for sec, seq in direct.items():
        ks = [k for _, k in seq]
        assert ks == list(range(1, len(ks) + 1)), '节 %s 直挂序池不连续（文档序应为1..M）: %r' % (sec, ks)
    for lec, seq in under.items():
        js_ = [j for _, j in seq]
        assert js_ == list(range(1, len(js_) + 1)), '讲部 %s 题型 j 链不连续: %r' % (lec, js_)
    # ④ 裸「大招讲解/方法讲解」段残留断言
    for i, p, tx in paras:
        assert not BARE_LECT_RE.match(tx), '裸「大招讲解/方法讲解」段残留: b#%d %r' % (i, tx[:30])
    # ⑤ 改写序号＋缩进（记录旧号）
    rows = []
    last_lecture = None   # 题型归属判定锚：其前最近讲部序号（2026-08-30 缩进梯子同口径）
    for i, t, p, tx in matched:
        num = t['新序号']
        m = NUM_RE.match(tx)
        old_num = m.group(1) if m else '（无）'
        old_end = m.end() if m else 0
        new_prefix = num + ' '
        replace_prefix(p, old_end, new_prefix)
        after = ptext(p)
        expect = new_prefix + tx[old_end:]
        assert after == expect, '改写后文本异常: %r != %r' % (after[:40], expect[:40])
        # 缩进（2026-08-30 拍板加倍梯子，与 工具/节标题序号底纹.py 同口径：
        #   二级节0＝顶格摘ind／三级节200／讲部400／题型按其前最近讲部——讲部下800、节下直挂400）
        if t['类型'] == '节':
            ind = 0 if num.count('.') == 1 else 200
        elif t['类型'] == '讲部':
            ind = 400
            last_lecture = num
        else:
            ind = 800 if (last_lecture is not None
                          and num.rsplit('.', 1)[0] == last_lecture) else 400
        if t['缩进'] is not None:
            ind = t['缩进']
        set_indent(p, ind if ind else None)
        rows.append((t['类型'], old_num, num, ind, tx))
    # 落盘 docx
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
    # 映射表 md
    lines = ['# 父链续层重编号映射表 — %s' % os.path.basename(path), '',
             '清单条目 %d（节 %d｜讲部 %d｜题型 %d）｜断言：序号池唯一 PASS｜直挂序池连续 PASS｜'
             '讲部内 j 链连续 PASS｜父链一致 PASS｜无裸「大招讲解」段 PASS'
             % (len(rows), sum(1 for r in rows if r[0] == '节'), sum(1 for r in rows if r[0] == '讲部'),
                sum(1 for r in rows if r[0] == '题型')),
             '', '| 类型 | 旧号 | 新号 | 缩进leftChars | 标题全文（旧） |', '|---|---|---|---|---|']
    for kind, old, new, ind, tx in rows:
        lines.append('| %s | %s | %s | %s | %s |' % (kind, old, new, '顶格' if not ind else ind,
                                                      tx.replace('|', '\\|')[:60]))
    lines.append('')
    open(mapmd, 'w', encoding='utf-8').write('\n'.join(lines))
    print('重编号 %d 条（节%d｜讲部%d｜题型%d）；断言全 PASS；映射表 -> %s'
          % (len(rows), sum(1 for r in rows if r[0] == '节'), sum(1 for r in rows if r[0] == '讲部'),
             sum(1 for r in rows if r[0] == '题型'), mapmd))

if __name__ == '__main__':
    renumber(sys.argv[1], sys.argv[2], sys.argv[3])
