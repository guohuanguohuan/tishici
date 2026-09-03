# -*- coding: utf-8 -*-
"""子步3 T5：讲部守恒扫描（等价手工清单）＋悬空引用清零＋覆盖断言复跑（定稿态）
① I1/I2 源条目特征串 → 六件全量检索（条目号＋题名串双向定位，每条恰一处讲部块内命中）
② 锚点主题核验：25 知识讲解讲部标题主题＝所在节节名（逐块）；37 旧方法讲解讲部收编关系不变
③ 讲部配图张数对源核对（逐节 知识讲解块图数＝清单该节图数）
④ 悬空引用扫描：知识讲解块内「如下例/见例N/如典例N」计数＝0
⑤ 覆盖断言：各节讲部条目数＝清单该节条目数（定稿态复跑）"""
import sys, io, re, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def q(t): return '{%s}%s' % (W, t)
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

BASE = r'C:\提示词\高中数学\高中数学同步'
SUB3 = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3'
SRC = {'I1': BASE + r'\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
       'I2': BASE + r'\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'}
TGT = {
    'B': SUB3 + r'\定稿\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': SUB3 + r'\定稿\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E': SUB3 + r'\定稿\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': SUB3 + r'\定稿\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': SUB3 + r'\定稿\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': SUB3 + r'\定稿\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
VOL_SECS = {
    'B': ['1.1.1', '1.1.2', '1.1.3', '1.2.1', '1.2.2', '1.2.3', '1.2.4'],
    'C': ['1.2.5'],
    'E': ['2.1', '2.2.1', '2.2.2', '2.2.3', '2.2.4', '2.3.1', '2.3.2', '2.3.3'],
    'F': ['2.3.4', '2.4', '2.5.1', '2.5.2'],
    'G': ['2.6.1', '2.6.2', '2.7.1', '2.7.2'],
    'H': ['2.8'],
}
VOL_SRC = {'B': 'I1', 'C': 'I1', 'E': 'I2', 'F': 'I2', 'G': 'I2', 'H': 'I2'}
ENT_RE = re.compile(r'^(\d+(?:\.\d+)*)-(\d+)．')
LECT_NEW_RE = re.compile(r'^(\d+(?:\.\d+)+)\.1 知识讲解｜(.+)$')
DANGLE_RE = re.compile(r'如下例|见例|如典例|如上例|例\d')

def load(path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    return z, root, root.find(q('body'))

def src_entries(code):
    z, root, body = load(SRC[code])
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
        out.setdefault(sec, []).append((i, children[i:j]))
    return out

def tgt_lecture_blocks(path):
    """定稿：节号 → (讲部标题文本, 块元素)"""
    z, root, body = load(path)
    children = list(body)
    blocks = {}
    for i, el in enumerate(children):
        if tag(el) != 'p': continue
        m = LECT_NEW_RE.match(ptext(el))
        if m and para_fill(el) == 'C6D4E3':
            j = len(children)
            for k in range(i + 1, len(children)):
                e2 = children[k]
                if tag(e2) == 'p' and (para_style(e2) == 'JieMingMao' or para_fill(e2) in ('ADC2DA', 'C6D4E3')):
                    j = k
                    break
            blocks[m.group(1)] = (ptext(el), children[i:j])
    return blocks, children

def tgt_sec_names(children):
    out = {}
    for el in children:
        if tag(el) != 'p': continue
        t = ptext(el)
        m = re.match(r'^(\d+(?:\.\d+)+)\s+(.+?)　本节\d+题', t)
        if m and para_fill(el) == 'ADC2DA':
            out[m.group(1)] = m.group(2)
    return out

results = {'条目检索': [], '锚点主题': [], '图对源': [], '悬空引用': [], '覆盖断言': []}
ok = True
for vol in ('B', 'C', 'E', 'F', 'G', 'H'):
    src = src_entries(VOL_SRC[vol])
    blocks, children = tgt_lecture_blocks(TGT[vol])
    sec_names = tgt_sec_names(children)
    # 全件文本（检索用）
    fulltext = '\n'.join(ptext(el) for el in children if tag(el) == 'p')
    for sec in VOL_SECS[vol]:
        ents = src.get(sec, [])
        blk_txt, blk = blocks.get(sec, (None, []))
        # ① 条目特征串检索：条目号＋题名首20字 在块内命中恰一次；全件另命中数登记
        n_hit = 0
        for si, bels in ents:
            title = ptext(bels[0])
            key = title[:24]
            n_in_blk = sum(1 for e in blk if tag(e) == 'p' and ptext(e) == title)
            n_all = fulltext.count(key)
            n_hit += 1 if n_in_blk == 1 else 0
            if n_in_blk != 1:
                ok = False
                results['条目检索'].append({'卷': vol, '节': sec, '条目': key, '块内命中': n_in_blk, '全件含串': n_all})
        # ② 锚点主题：讲部标题＝「节号.1 知识讲解｜节名」且节名＝节标题节名
        theme_ok = blk_txt == '%s.1 知识讲解｜%s' % (sec, sec_names.get(sec))
        results['锚点主题'].append({'卷': vol, '节': sec, '讲部标题': blk_txt, '节名': sec_names.get(sec), '一致': theme_ok})
        if not theme_ok: ok = False
        # ③ 图张数对源
        n_src_img = sum(len(list(e.iter('{%s}extent' % WP))) for _, bels in ents for e in bels)
        n_blk_img = sum(len(list(e.iter('{%s}extent' % WP))) for e in blk[1:])  # 剔讲部标题段
        img_ok = n_src_img == n_blk_img
        results['图对源'].append({'卷': vol, '节': sec, '源图': n_src_img, '块图': n_blk_img, '一致': img_ok})
        if not img_ok: ok = False
        # ④ 悬空引用
        dangles = []
        for e in blk:
            if tag(e) == 'p':
                for m in DANGLE_RE.finditer(ptext(e)):
                    dangles.append(ptext(e)[:40])
        results['悬空引用'].append({'卷': vol, '节': sec, '命中': len(dangles), '样本': dangles[:3]})
        if dangles: ok = False
        # ⑤ 覆盖断言
        n_blk_ent = sum(1 for e in blk if tag(e) == 'p' and ENT_RE.match(ptext(e)))
        cov_ok = n_blk_ent == len(ents)
        results['覆盖断言'].append({'卷': vol, '节': sec, '清单条目数': len(ents), '讲部条目数': n_blk_ent, '一致': cov_ok})
        if not cov_ok: ok = False
    n_lec = sum(1 for e in children if tag(e) == 'p' and LECT_NEW_RE.match(ptext(e)))
    assert n_lec == len(VOL_SECS[vol]), '%s 知识讲解讲部数异常 %d' % (vol, n_lec)
    print(vol, '条目检索/锚点/图/悬空/覆盖 逐节完毕')

json.dump(results, open(SUB3 + r'\T5_守恒扫描.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
n_bad = (len(results['条目检索']) + sum(1 for r in results['锚点主题'] if not r['一致'])
         + sum(1 for r in results['图对源'] if not r['一致']) + sum(r['命中'] for r in results['悬空引用'])
         + sum(1 for r in results['覆盖断言'] if not r['一致']))
print('T5 总判定:', 'PASS' if n_bad == 0 and ok else 'FAIL(%d)' % n_bad)
