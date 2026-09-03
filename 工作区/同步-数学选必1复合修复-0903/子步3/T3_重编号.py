# -*- coding: utf-8 -*-
"""子步3 T3：编号联动驱动（减法后 → 定稿）
口径：知识讲解讲部＝节号.1（已挂，不动）；本节其余子元素 k 序整体 +1（直挂题型/方法讲解讲部），
     收编题型随父讲部；题号＝题型号-节内序号． 仅题型号联动、节内序号不变；题型标题统计段
     题号区间同步改写；节标题统计段题量不变；导航表组数列重算核验（预期不变）。
工序：①编号映射计算 → ②父链续层重编号.py（标题段首序号；缩进=0 顶格口径）→
     ③题号块段首＋题型统计段题号联动改写（本驱动）→ ④断言（编号序列/题量恒等/fill净增=0/文字流授权差异）。
"""
import sys, io, re, os, json, copy, zipfile, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def para_fill(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return None
    shd = ppr.find(q('shd'))
    return shd.get(q('fill')) if shd is not None else None
def para_style(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return None
    st = ppr.find(q('pStyle'))
    return st.get(q('val')) if st is not None else None

SUB3 = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3'
INDIR = SUB3 + r'\减法后'
OUTDIR = SUB3 + r'\定稿'
NAMES = {
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
QTY = {'B': 61, 'C': 79, 'E': 92, 'F': 90, 'G': 68, 'H': 89}
VOL_SECS = {
    'B': ['1.1.1', '1.1.2', '1.1.3', '1.2.1', '1.2.2', '1.2.3', '1.2.4'],
    'C': ['1.2.5'],
    'E': ['2.1', '2.2.1', '2.2.2', '2.2.3', '2.2.4', '2.3.1', '2.3.2', '2.3.3'],
    'F': ['2.3.4', '2.4', '2.5.1', '2.5.2'],
    'G': ['2.6.1', '2.6.2', '2.7.1', '2.7.2'],
    'H': ['2.8'],
}
TOOL = r'C:\提示词\工具\父链续层重编号.py'

SEC_TITLE_RE = re.compile(r'^(\d+(?:\.\d+)+)\s+(.+?)　本节(\d+)题')
PARENT_SEC_RE = re.compile(r'^(\d+\.\d+)\s+\S')                    # 父节（无统计段）
LECT_NEW_RE = re.compile(r'^(\d+(?:\.\d+)+)\s*知识讲解[｜|]')
LECT_OLD_RE = re.compile(r'^(\d+(?:\.\d+)+)\s*方法讲解[｜|]')
TITLE_NUM_RE = re.compile(r'^(\d+(?:\.\d+)+)\s')
QBLOCK_RE = re.compile(r'^(\d+(?:\.\d+)+)-(\d+)．（')
QREF_RE = re.compile(r'(\d+(?:\.\d+)+)-(\d+)')

def fill_counts(root):
    para = {}
    body = root.find(q('body'))
    for p in body.iter(q('p')):
        f = para_fill(p)
        if f: para[f] = para.get(f, 0) + 1
    run = {}
    for r in root.iter(q('r')):
        rpr = r.find(q('rPr'))
        shd = rpr.find(q('shd')) if rpr is not None else None
        f = shd.get(q('fill')) if shd is not None else None
        if f: run[f] = run.get(f, 0) + 1
    om = 0
    for el in root.iter():
        if etree.QName(el).namespace == M and tag(el) in ('r', 'ctrlPr'):
            rpr = el.find(q('rPr'))
            shd = rpr.find(q('shd')) if rpr is not None else None
            if shd is not None and shd.get(q('fill')) == 'C9C9C9':
                om += 1
    return para, run, om

def set_leading_text(p, old_len, new_prefix):
    """段首 old_len 字符整体替换为 new_prefix（跨 run 归并，其余文字零变更）"""
    runs = [c for c in p if tag(c) == 'r']
    covered, off = [], 0
    for r in runs:
        tx = ''.join(t.text or '' for t in r.findall(q('t')))
        if not tx:
            continue
        covered.append((r, tx))
        off += len(tx)
        if off >= old_len:
            break
    assert covered and off >= old_len, '前导序号未落在文本run内'
    first_r = covered[0][0]
    total = sum(len(tx) for _, tx in covered)
    last_r, last_tx = covered[-1]
    if total > old_len:
        cut = old_len - (total - len(last_tx))
        rest = last_tx[cut:]
        ts = last_r.findall(q('t'))
        ts[0].text = last_tx[:cut]
        ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        for t in ts[1:]:
            t.text = ''
        nr = copy.deepcopy(last_r)
        nts = nr.findall(q('t'))
        nts[0].text = rest
        nts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        for t in nts[1:]:
            t.text = ''
        nrpr = nr.find(q('rPr'))
        if nrpr is not None:
            nshd = nrpr.find(q('shd'))
            if nshd is not None:
                nrpr.remove(nshd)
        last_r.addnext(nr)
    ts = first_r.findall(q('t'))
    ts[0].text = new_prefix
    ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    for t in ts[1:]:
        t.text = ''
    for r, _ in covered[1:]:
        p.remove(r)

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    report = {}
    for vol, fname in NAMES.items():
        src_path = os.path.join(INDIR, fname)
        tgt_path = os.path.join(OUTDIR, fname)
        shutil.copy2(src_path, tgt_path)
        # —— Phase 1 编号映射 ——
        z = zipfile.ZipFile(tgt_path)
        root = etree.fromstring(z.read('word/document.xml'))
        z.close()
        body = root.find(q('body'))
        els = list(body)
        # 逐段快照（文字流授权差异断言用）
        pre_texts = {i: ptext(el) for i, el in enumerate(els) if tag(el) == 'p'}
        pre_para_fill, pre_run_fill, pre_om = fill_counts(root)
        titles = []   # (idx, 类型, 旧号, 新号, 旧文本)
        num_map = {}  # 旧标题号 → 新标题号（讲部/题型）
        cur_sec = None
        for i, el in enumerate(els):
            if tag(el) != 'p':
                continue
            t = ptext(el)
            if not t.strip():
                continue
            f = para_fill(el)
            m = SEC_TITLE_RE.match(t)
            if f == 'ADC2DA' and m:
                cur_sec = m.group(1)
                titles.append((i, '节', cur_sec, cur_sec, t))
                continue
            if f == 'ADC2DA' and para_style(el) != 'JieMingMao':
                pm = PARENT_SEC_RE.match(t)
                if pm and not re.match(r'^\d+(?:\.\d+)+\s', t):
                    cur_sec = pm.group(1)
                    titles.append((i, '节', cur_sec, cur_sec, t))
                    continue
                # 章/文内开头标题（ADC2DA 但非数码起段）
                titles.append((i, '章', None, None, t))
                continue
            if f == 'C6D4E3':
                tn = TITLE_NUM_RE.match(t)
                assert tn, '%s 标题段无序号: %r' % (vol, t[:40])
                old_num = tn.group(1)
                if LECT_NEW_RE.match(t):
                    assert old_num == cur_sec + '.1', '%s 知识讲解号异常 %s != %s.1' % (vol, old_num, cur_sec)
                    titles.append((i, '讲部', old_num, old_num, t))
                    continue
                if LECT_OLD_RE.match(t):
                    k = int(old_num[len(cur_sec) + 1:])
                    new_num = '%s.%d' % (cur_sec, k + 1)
                    num_map[old_num] = new_num
                    titles.append((i, '讲部', old_num, new_num, t))
                    continue
                # 题型：节号.k 或 讲部号.j
                rest = old_num[len(cur_sec) + 1:]
                parts = rest.split('.')
                if len(parts) == 1:
                    new_num = '%s.%d' % (cur_sec, int(parts[0]) + 1)
                else:
                    assert len(parts) == 2, '%s 题型序号异常: %s' % (vol, old_num)
                    parent_old = cur_sec + '.' + parts[0]
                    assert parent_old in num_map, '%s 题型 %s 父讲部未先映射' % (vol, old_num)
                    new_num = num_map[parent_old] + '.' + parts[1]
                num_map[old_num] = new_num
                titles.append((i, '题型', old_num, new_num, t))
                continue
        # 题型号映射（题型标题号）
        qnum_map = {o: n for (i, k, o, n, t) in titles if k == '题型'}
        # —— Phase 2 生成工具清单（仅序号变化者＋全部节标题作链上下文；章标题不入工具） ——
        jtitles = []
        for i, kind, old_num, new_num, t in titles:
            if kind == '章':
                continue
            jtitles.append({'旧文本': t, '类型': kind, '新序号': new_num, '缩进': 0})
        jpath = os.path.join(SUB3, 'T3_标题清单_%s.json' % vol)
        json.dump({'titles': jtitles}, open(jpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        # —— Phase 3 调工具改标题段首序号 ——
        mapmd = os.path.join(SUB3, 'T3_映射表_%s.md' % vol)
        r = subprocess.run([sys.executable, TOOL, tgt_path, jpath, mapmd],
                           capture_output=True, text=True, encoding='utf-8')
        assert r.returncode == 0, '%s 父链续层重编号失败:\n%s\n%s' % (vol, r.stdout[-800:], r.stderr[-800:])
        # —— Phase 4 题号块＋题型统计段联动 ——
        z = zipfile.ZipFile(tgt_path)
        root = etree.fromstring(z.read('word/document.xml'))
        z.close()
        body = root.find(q('body'))
        els = list(body)
        changes = []  # (idx, 旧文本, 新文本)
        n_qblock = n_statseg = 0
        for i, el in enumerate(els):
            if tag(el) != 'p':
                continue
            t = ptext(el)
            if not t.strip():
                continue
            # 题号块段首
            mqb = QBLOCK_RE.match(t)
            if mqb and mqb.group(1) in qnum_map:
                old_prefix = '%s-%s．' % (mqb.group(1), mqb.group(2))
                new_prefix = '%s-%s．' % (qnum_map[mqb.group(1)], mqb.group(2))
                set_leading_text(el, len(old_prefix), new_prefix)
                changes.append((i, t, ptext(el)))
                n_qblock += 1
                continue
            # 题型标题统计段（标题段首序号已被工具改写；此处改行末题号区间）
            if para_fill(el) == 'C6D4E3' and '　' in t:
                new_t = t
                for mref in QREF_RE.finditer(t):
                    o, s = mref.group(1), mref.group(2)
                    if o in qnum_map:
                        new_t = new_t.replace('%s-%s' % (o, s), '%s-%s' % (qnum_map[o], s))
                if new_t != t:
                    # 统计段在段尾单 run（或跨 run）——全段文本逐 run 改写定位
                    # 找到含旧区间文本的 run 逐字符替换（区间串不跨 run 的实测前提由断言兜底）
                    done = False
                    for r in el.iter(q('r')):
                        for tx in r.findall(q('t')):
                            if tx.text:
                                nt = tx.text
                                for mref in QREF_RE.finditer(tx.text):
                                    o, s = mref.group(1), mref.group(2)
                                    if o in qnum_map:
                                        nt = nt.replace('%s-%s' % (o, s), '%s-%s' % (qnum_map[o], s))
                                if nt != tx.text:
                                    tx.text = nt
                                    tx.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                                    done = True
                    assert ptext(el) == new_t, '%s 统计段改写不闭合: %r' % (vol, t[:50])
                    changes.append((i, t, new_t))
                    n_statseg += 1
        # 落盘
        new_xml = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        with zipfile.ZipFile(src_path) as zin, zipfile.ZipFile(tgt_path + '.tmp', 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
                zout.writestr(item, data)
        os.replace(tgt_path + '.tmp', tgt_path)
        # —— Phase 5 断言 ——
        z = zipfile.ZipFile(tgt_path)
        root = etree.fromstring(z.read('word/document.xml'))
        z.close()
        body = root.find(q('body'))
        els2 = list(body)
        # A1 题号序列：节内序号连续＋全件题量恒等
        sec_q = {}
        qtype_of = {}
        for el in els2:
            if tag(el) != 'p':
                continue
            t = ptext(el)
            m = QBLOCK_RE.match(t)
            if m:
                qtype_of.setdefault(m.group(1), 0)
                qtype_of[m.group(1)] += 1
        total_q = sum(qtype_of.values())
        assert total_q == QTY[vol], '%s 题量恒等失败: %d != %d' % (vol, total_q, QTY[vol])
        # 节内序号 1..N 连续（按节号前缀聚合）
        for qn in qtype_of:
            pass
        seqs = {}
        leaf_secs = sorted(VOL_SECS[vol], key=len, reverse=True)
        for el in els2:
            if tag(el) != 'p':
                continue
            m = QBLOCK_RE.match(ptext(el))
            if m:
                qn = m.group(1)
                sec = next((s for s in leaf_secs if qn == s or qn.startswith(s + '.')), None)
                assert sec, '%s 题号 %s 无法归属叶子节' % (vol, qn)
                seqs.setdefault(sec, []).append(int(m.group(2)))
        for sec, lst in seqs.items():
            assert sorted(lst) == list(range(1, len(lst) + 1)), '%s 节 %s 题号节内序列不连续: %r' % (vol, sec, sorted(lst)[:8])
        # A2 题型号集合＝题型标题集合
        title_qtypes = set()
        for el in els2:
            if tag(el) == 'p' and para_fill(el) == 'C6D4E3':
                t = ptext(el)
                if '知识讲解' in t or '方法讲解' in t:
                    continue
                m = TITLE_NUM_RE.match(t)
                if m:
                    title_qtypes.add(m.group(1))
        assert set(qtype_of) == title_qtypes, '%s 题型号↔题型标题集合不符: %r' % (
            vol, (set(qtype_of) ^ title_qtypes))
        # A3 统计段区间与实际题号一致（编号口径）；邻接隔断另列登记（存量结构缺陷不属本子步授权变更面）
        n_stat_bad = 0
        misplaced = []
        for el in els2:
            if tag(el) == 'p' and para_fill(el) == 'C6D4E3':
                t = ptext(el)
                if '知识讲解' in t or '方法讲解' in t:
                    continue
                ms = re.search(r'　(\d+)题：(\S+)$', t)
                if not ms:
                    continue
                m = TITLE_NUM_RE.match(t)
                qt = m.group(1)
                rng = ms.group(2)
                # 全件该组题号（不限邻接）
                grp = []
                for el2 in els2:
                    if tag(el2) == 'p':
                        m2 = QBLOCK_RE.match(ptext(el2))
                        if m2 and m2.group(1) == qt:
                            grp.append('%s-%s' % (m2.group(1), m2.group(2)))
                # 邻接题块（统计段口径的物理位置断言）
                sib = []
                for el2 in el.itersiblings():
                    if tag(el2) == 'p' and para_fill(el2) in ('C6D4E3', 'ADC2DA'):
                        break
                    if tag(el2) == 'p':
                        m2 = QBLOCK_RE.match(ptext(el2))
                        if m2 and m2.group(1) == qt:
                            sib.append('%s-%s' % (m2.group(1), m2.group(2)))
                n_declared = int(ms.group(1))
                # 编号口径：声明题数＝组实有题数、区间＝组实有首末
                if grp:
                    expect_rng = grp[0] if len(grp) == 1 else '%s～%s' % (grp[0], grp[-1])
                    if n_declared != len(grp) or rng != expect_rng:
                        n_stat_bad += 1
                else:
                    n_stat_bad += 1
                # 邻接口径：组题应紧接标题连续排列（§6）
                if sib != grp:
                    misplaced.append({'卷': vol, '题型号': qt, '声明': rng,
                                      '邻接题': sib, '组实有题': grp})
        assert n_stat_bad == 0, '%s 题型统计段题数/区间与组实有不符 %d 处' % (vol, n_stat_bad)
        KNOWN_MISPLACED = {'C': {'1.2.5.7.1'}, 'H': {'2.8.26.4'}}   # 新编号（存量：减法后 1.2.5.6.1/2.8.25.4 同址在案）
        got = {m['题型号'] for m in misplaced}
        assert got == KNOWN_MISPLACED.get(vol, set()), '%s 邻接错位集合与存量登记不符: %r' % (vol, got)
        # A4 fill 净增=0（四色段级/run级/OMML）
        post_para_fill, post_run_fill, post_om = fill_counts(root)
        assert post_para_fill == pre_para_fill, '%s 段级fill变化: %r→%r' % (vol, pre_para_fill, post_para_fill)
        assert post_run_fill == pre_run_fill, '%s run级fill变化' % vol
        assert post_om == pre_om, '%s OMML fill变化' % vol
        # A5 文字流授权差异：变更段 ⊆ 标题∪题号块，且逐段只剩序号改写
        changed_idx = [c[0] for c in changes]
        post_texts = {i: ptext(el) for i, el in enumerate(els2) if tag(el) == 'p'}
        n_tool_changed = 0
        for i, old_t in pre_texts.items():
            new_t = post_texts.get(i)
            if new_t is None:
                continue
            if new_t != old_t and i not in changed_idx:
                n_tool_changed += 1
                # 工具改写的标题段：只允许段首序号差异
                mo = TITLE_NUM_RE.match(old_t)
                mn = TITLE_NUM_RE.match(new_t)
                assert mo and mn, '%s 非授权变更段 @%d: %r→%r' % (vol, i, old_t[:40], new_t[:40])
                assert old_t[mo.end():] == new_t[mn.end():], '%s 标题序号外文本被改 @%d' % (vol, i)
                assert (mo.group(1) in num_map and num_map[mo.group(1)] == mn.group(1)) or mo.group(1) == mn.group(1), \
                    '%s 标题序号改写不在映射表 @%d %s→%s' % (vol, i, mo.group(1), mn.group(1))
        # 段落总数不变
        assert len(els2) == len(els), '%s body子元素数变化' % vol
        report[vol] = {
            '标题改写数': sum(1 for i, k, o, n, t in titles if o != n),
            '讲部数': sum(1 for t in titles if t[1] == '讲部'),
            '题型数': sum(1 for t in titles if t[1] == '题型'),
            '题号块改写': n_qblock, '统计段改写': n_statseg,
            '题量恒等': total_q, '节序列数': len(seqs),
            '存量邻接错位登记': misplaced,
            '编号映射': num_map,
        }
        print(vol, 'PASS 标题改写%d（讲部%d题型%d）题号块%d 统计段%d 题量%d 节序列%d' % (
            report[vol]['标题改写数'], report[vol]['讲部数'], report[vol]['题型数'],
            n_qblock, n_statseg, total_q, len(seqs)))
    json.dump(report, open(os.path.join(SUB3, 'T3_重编号对照.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('T3 全部 PASS →', os.path.join(SUB3, 'T3_重编号对照.json'))

if __name__ == '__main__':
    main()
