# -*- coding: utf-8 -*-
r"""probe_灰底分布.py（子步2一次性探针）——六讲练件 C9C9C9 挂点语境分布实测。
输出：逐件分桶（题号块/芯片/并行解法/条目号/第一子层/条目区内需背/讲部方法讲解区内/表内/其他题目侧）
＋pmark灰底数＋深蓝1F4E79 run数＋空文本灰底run数，各桶给样本。
"""
import sys, io, os, zipfile, re, json
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
DEEP_BLUE = '1F4E79'
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

BASE = r'C:\提示词\高中数学\高中数学同步'
FILES = {
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}

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

def probe(code, path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    # 语境状态机：entry区（条目号起段块）/ lecture区（方法讲解标题起至下一标题/题号块/条目）
    ctx = {}   # para idx -> 'entry'|'lecture'|'q'|'other'
    state = 'other'
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue            # 表格不断语境
        t = ptexts[i]
        if QBLOCK_HEAD_RE.match(t):
            state = 'q'
        elif LECTURE_RE.match(t):
            state = 'lecture'
        elif ENT_RE.match(t) and not HEAD_RE.match(t):
            state = 'entry'
        elif HEAD_RE.match(t):
            state = 'other'
        ctx[i] = state
    buckets = {}
    samples = {}
    pmark_gray = 0
    deep_blue_runs = 0
    deep_blue_samples = []
    empty_gray = 0
    def bump(bk, sample):
        buckets[bk] = buckets.get(bk, 0) + 1
        if sample and len(samples.setdefault(bk, [])) < 3:
            samples[bk].append(sample[:30])
    for i, el in enumerate(els):
        if el.tag != q('p'):
            continue
        c = ctx.get(i, 'other')
        # pmark 灰底
        ppr = el.find(q('pPr'))
        if ppr is not None:
            prpr = ppr.find(q('rPr'))
            if shd_fill(prpr) == C9:
                pmark_gray += 1
        runs = list(el.iter(q('r')))
        # 段首连续灰底串
        lead_txt = ''
        lead_runs = []
        for r in runs:
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t == '':
                continue
            if shd_fill(r.find(q('rPr'))) == C9:
                lead_txt += t; lead_runs.append(r)
            else:
                break
        lead_kind = None
        if lead_runs:
            if QBLOCK_HEAD_RE.match(ptexts[i]) and (LEAD_NUM_RE.fullmatch(lead_txt) or QNUM_LEGACY_RE.fullmatch(lead_txt)):
                lead_kind = '题号块'
            elif LEAD_NUM_RE.fullmatch(lead_txt) and not in_tbl(el):
                lead_kind = '条目号'
            elif LEAD_SUB_RE.fullmatch(lead_txt) and not in_tbl(el):
                lead_kind = '第一子层'
        # 字符蒙版
        chars, mask, ranges = [], [], {}
        for k, r in enumerate(runs):
            sh = shd_fill(r.find(q('rPr'))) == C9
            s0 = len(chars)
            for x in r.findall(q('t')):
                s = x.text or ''
                chars.extend(s); mask.extend([sh] * len(s))
            ranges[k] = (s0, len(chars))
        fulltext = ''.join(chars)
        chip_runs = set()
        n_chip = 0
        for mm in CHIP_RE.finditer(fulltext):
            lb = mm.group(0)
            if lb in CHIP_BLACKLIST or CHIP_BLACKLIST_RE.match(lb):
                continue
            a, bb = mm.span()
            if all(mask[a:bb]):
                n_chip += 1
                for k, (s0, s1) in ranges.items():
                    if s0 >= a and s1 <= bb:
                        chip_runs.add(k)
        if n_chip:
            bump('芯片', fulltext[:30])
            buckets['芯片'] += n_chip - 1   # bump已计1
        for k, r in enumerate(runs):
            rpr = r.find(q('rPr'))
            fill = shd_fill(rpr)
            col = rpr.find(q('color')) if rpr is not None else None
            if col is not None and col.get(q('val')) == DEEP_BLUE:
                deep_blue_runs += 1
                t = ''.join(x.text or '' for x in r.findall(q('t')))
                if t.strip() and len(deep_blue_samples) < 3:
                    deep_blue_samples.append(t[:30])
            if fill != C9:
                continue
            t = ''.join(x.text or '' for x in r.findall(q('t')))
            if t == '':
                empty_gray += 1
                continue
            if k in chip_runs or MARK_RE.match(t):
                if MARK_RE.match(t) and k not in chip_runs:
                    bump('并行解法', t)
                continue
            if lead_kind and r in lead_runs:
                bump(lead_kind, t)
                continue
            if in_tbl(r):
                bump('表内', t)
            elif c == 'entry':
                bump('条目区内', t)
            elif c == 'lecture':
                bump('讲部区内', t)
            else:
                bump('题目侧其他', t)
        # OMML 挂点按段语境
        for m_el in el.iter():
            if etree.QName(m_el).namespace != M:
                continue
            tg = tag(m_el)
            if tg in ('r', 'ctrlPr') and shd_fill(m_el.find(q('rPr'))) == C9:
                if in_tbl(m_el):
                    bk = 'OMML表内'
                elif c == 'entry':
                    bk = 'OMML条目区内'
                elif c == 'lecture':
                    bk = 'OMML讲部区内'
                else:
                    bk = 'OMML题目侧'
                buckets[bk] = buckets.get(bk, 0) + 1
    return {'buckets': buckets, 'samples': samples, 'pmark_gray': pmark_gray,
            'deep_blue_runs': deep_blue_runs, 'deep_blue_samples': deep_blue_samples,
            'empty_gray_runs': empty_gray}

if __name__ == '__main__':
    out = {}
    for code, fn in FILES.items():
        r = probe(code, os.path.join(BASE, fn))
        out[code] = r
        print('[%s] 分桶: %s' % (code, json.dumps(r['buckets'], ensure_ascii=False, sort_keys=True)))
        print('   pmark灰=%d 空文本灰run=%d 深蓝run=%d %s' % (r['pmark_gray'], r['empty_gray_runs'], r['deep_blue_runs'], r['deep_blue_samples']))
        for bk, ss in r['samples'].items():
            print('   样本[%s]: %s' % (bk, ss))
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), '灰底分布探测.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('落盘:', dst)
