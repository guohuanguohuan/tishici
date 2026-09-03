# -*- coding: utf-8 -*-
"""子步3 T4 补挂断言：讲部块逐块属性 vs I1/I2 源节（照抄断言）＋条目族增量逐节＋标题/题干底纹变化
输出：T4_补挂断言.json（机器可读全量）＋控制台摘要"""
import sys, io, re, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def shd_fill(rpr):
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd.get(q('fill')) if shd is not None else None
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
def in_tbl(el):
    cur = el.getparent()
    while cur is not None:
        if tag(cur) == 'tbl': return True
        cur = cur.getparent()
    return False

C9 = 'C9C9C9'
CHIP_RE = re.compile(r'【[^】]{1,16}】')
CHIP_BLACKLIST = ('【易错】', '【了解】')
CHIP_BLACKLIST_RE = re.compile(r'^【典例[^】]*】$')
ENT_RE = re.compile(r'^(\d+(?:\.\d+)*)-(\d+)．')
LECT_TITLE_RE = re.compile(r'^(\d+(?:\.\d+)+)\.1 知识讲解｜')
LEAD_NUM_RE = re.compile(r'^(?:\d+|\d+(?:\.\d+)+-\d+)．(?:【[^】]{1,16}】)*$')
LEAD_SUB_RE = re.compile(r'^（\d+）(?:【[^】]{1,16}】)*$')

BASE = r'C:\提示词\高中数学\高中数学同步'
SRC = {
    'I1': BASE + r'\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'I2': BASE + r'\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
}
OUTD = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3\补挂态'
TGT = {
    'B': OUTD + r'\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': OUTD + r'\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E': OUTD + r'\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': OUTD + r'\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': OUTD + r'\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': OUTD + r'\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
VOL_SRC = {'B': 'I1', 'C': 'I1', 'E': 'I2', 'F': 'I2', 'G': 'I2', 'H': 'I2'}
OLD_FILL = {  # 子步2后成品段级四色（子步2报告T3/减后计数在案值）
    'B': {'ADC2DA': 10, 'C6D4E3': 52, 'E0E0E0': 131}, 'C': {'ADC2DA': 1, 'C6D4E3': 75, 'E0E0E0': 123},
    'E': {'ADC2DA': 11, 'C6D4E3': 68, 'E0E0E0': 161}, 'F': {'ADC2DA': 5, 'C6D4E3': 69, 'E0E0E0': 164},
    'G': {'ADC2DA': 6, 'C6D4E3': 52, 'E0E0E0': 118}, 'H': {'ADC2DA': 1, 'C6D4E3': 73, 'E0E0E0': 138},
}
LECT_N = {'B': 7, 'C': 1, 'E': 8, 'F': 4, 'G': 4, 'H': 1}

def classify_block(elements):
    """一组 body 子元素（讲部块/源节条目集合）的 C9C9C9 分类计数"""
    c = {'条目号run': 0, '第一子层run': 0, '需背run': 0, '条目区OMML': 0,
         '表内run': 0, '表内OMML': 0, '芯片run': 0, '条目数': 0, '其他run': 0}
    for el in elements:
        if tag(el) == 'tbl':
            for r in el.iter(q('r')):
                if shd_fill(r.find(q('rPr'))) == C9:
                    c['表内run'] += 1
            for mel in el.iter():
                if etree.QName(mel).namespace != M: continue
                if tag(mel) in ('r', 'ctrlPr') and shd_fill(mel.find(q('rPr'))) == C9:
                    c['表内OMML'] += 1
            continue
        if tag(el) != 'p':
            continue
        runs = list(el.iter(q('r')))
        # lead 判定
        lead_txt, lead_runs = '', []
        for r in runs:
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t == '': continue
            if shd_fill(r.find(q('rPr'))) == C9:
                lead_txt += t
                lead_runs.append(r)
            else:
                break
        lead_set = set(id(r) for r in lead_runs)
        is_ent = bool(ENT_RE.match(ptext(el)))
        if is_ent:
            c['条目数'] += 1
        if lead_runs and LEAD_NUM_RE.fullmatch(lead_txt) and is_ent:
            c['条目号run'] += len(lead_runs)
        elif lead_runs and LEAD_SUB_RE.fullmatch(lead_txt):
            c['第一子层run'] += len(lead_runs)
        else:
            lead_set = set()
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
        chip_ids = set()
        for mm in CHIP_RE.finditer(fulltext):
            lb = mm.group(0)
            if lb in CHIP_BLACKLIST or CHIP_BLACKLIST_RE.match(lb): continue
            a, bb = mm.span()
            if not mask[a:bb] or not all(mask[a:bb]): continue
            hit = [k for k, (s0, s1) in ranges.items() if s0 < bb and s1 > a]
            if all(ranges[k][0] >= a and ranges[k][1] <= bb for k in hit):
                chip_ids.update(hit)
        c['芯片run'] += len(chip_ids)
        for k, r in enumerate(runs):
            if shd_fill(r.find(q('rPr'))) != C9: continue
            if id(r) in lead_set or k in chip_ids: continue
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t.strip() == '':
                c['需背run'] += 1   # 空白尾巴 run 在条目区按需背留白计（减法器同 zone 口径）
            else:
                c['需背run'] += 1
        for mel in el.iter():
            if etree.QName(mel).namespace != M: continue
            if tag(mel) in ('r', 'ctrlPr') and shd_fill(mel.find(q('rPr'))) == C9:
                c['条目区OMML'] += 1
    return c

def src_sections(code):
    """源清单：节号 → 条目块元素全列表"""
    z = zipfile.ZipFile(SRC[code])
    root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(q('body'))
    children = list(body)
    bounds = []
    for i, el in enumerate(children):
        if tag(el) != 'p': continue
        t = ptext(el)
        if not t.strip(): continue
        if ENT_RE.match(t):
            bounds.append((i, ENT_RE.match(t).group(1)))
        elif para_style(el) == 'JieMingMao' or para_fill(el) == 'ADC2DA':
            bounds.append((i, None))
    marks = [(i, s) for i, s in bounds if s]
    out = {}
    for i, sec in marks:
        j = len(children)
        for bi, _ in bounds:
            if bi > i:
                j = bi
                break
        out.setdefault(sec, []).extend(children[i:j])
    return out

def tgt_blocks(path):
    """补挂态：节号 → 讲部块元素（讲部标题段起 → 下一节锚/节标题/文末）"""
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(q('body'))
    children = list(body)
    starts = []
    for i, el in enumerate(children):
        if tag(el) != 'p': continue
        m = LECT_TITLE_RE.match(ptext(el))
        if m and para_fill(el) == 'C6D4E3':
            starts.append((i, m.group(1)))
    blocks = {}
    for i, sec in starts:
        j = len(children)
        for k in range(i + 1, len(children)):
            el = children[k]
            if tag(el) == 'p':
                if para_style(el) == 'JieMingMao' or para_fill(el) == 'ADC2DA':
                    j = k
                    break
                # 下一讲部标题（方法讲解）或题型标题不终结本块？——知识讲解块内只有条目；
                # 防御：题型标题/方法讲解出现即终结（正常不会发生在块内）
                if para_fill(el) == 'C6D4E3':
                    j = k
                    break
        blocks[sec] = children[i:j]
    return blocks

results = {}
allpass = True
for vol in ('B', 'C', 'E', 'F', 'G', 'H'):
    src = src_sections(VOL_SRC[vol])
    blocks = tgt_blocks(TGT[vol])
    rows = []
    for sec, bels in blocks.items():
        bc = classify_block(bels)
        sc = classify_block(src.get(sec, []))
        same = all(bc[k] == sc[k] for k in ('条目数', '条目号run', '第一子层run', '需背run', '条目区OMML', '表内run', '表内OMML', '芯片run'))
        rows.append({'节': sec, '照抄全等': same, '块': bc, '源': sc})
        if not same:
            allpass = False
    results[vol] = rows
    n_ok = sum(1 for r in rows if r['照抄全等'])
    print(vol, '讲部块', len(rows), '照抄全等', n_ok, '/' , len(rows))
    for r in rows:
        if not r['照抄全等']:
            print('  失配:', r['节'], '块', r['块'], '源', r['源'])
    # 段级四色增量
    z = zipfile.ZipFile(TGT[vol])
    root = etree.fromstring(z.read('word/document.xml'))
    pf = {'ADC2DA': 0, 'C6D4E3': 0, 'E0E0E0': 0}
    for p in root.find(q('body')).iter(q('p')):
        f = para_fill(p)
        if f in pf: pf[f] += 1
    exp = {'ADC2DA': OLD_FILL[vol]['ADC2DA'], 'C6D4E3': OLD_FILL[vol]['C6D4E3'] + LECT_N[vol], 'E0E0E0': OLD_FILL[vol]['E0E0E0']}
    ok = pf == exp
    if not ok: allpass = False
    print('  段级四色: 实测', pf, '预期(旧+讲部标题%d)' % LECT_N[vol], exp, 'PASS' if ok else 'FAIL')

with open('T4_补挂断言.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print('总判定:', 'PASS' if allpass else 'FAIL')
