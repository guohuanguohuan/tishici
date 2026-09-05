# -*- coding: utf-8 -*-
"""难度前置.py — 2026-08-28 拍板「难度前置」内容改动（Pass1）：
逐题块删标签行「【难度】值」字段（连同其后分隔空格；无后分隔则删前分隔），
并把题号块「N．」扩为「N．（档位）」（全角括号；档位＝删下的【难度】值）。
讲练件【难度】已是三档词（简单/中档/难）直接迁移；衔接件为数值（0.65/0.85/0.94 等，
组卷网难度系数：值越大越易），按总控2.1绝对尺度词化——区间映射沿用 2026-08-25
第2章词化轮先例（0.94/0.85→简单、0.65→中档、0.4/0.15→难 的亲算落档归纳）：
  >=0.80 → 简单；0.50~0.79 → 中档；<0.50 → 难。全部数值映射写进映射表供复核。
题号块与题干同 run 时先拆出独立 run（含跨 run 拼合「N」＋「．」的情形）；
题号块 run 缺加粗/底纹的补 w:b＋w:shd C7C7C7（现行拍板色）。
用法: python 难度前置.py <docx> <映射表md输出路径>
输出: 迁移数/跳过数/异常清单；映射表「题号→档位（原值）」落盘。幂等：已迁移块自动跳过。"""
import sys, io, zipfile, re, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname

DIFF_RE = re.compile(r'【难度】[ 　]*(中档|简单|难|0?\.\d+|1\.0)')
NUM2WORD = [(0.80, '简单'), (0.50, '中档'), (-1, '难')]  # 组卷网系数：大=易

def ptext(p):
    """段内 w:t 序列文本（不含公式 m:t——难度字段与题号都是纯文字）"""
    return ''.join(t.text or '' for t in p.iter(q('t')))

def wt_nodes(p):
    return [t for t in p.iter(q('t'))]

def delete_range(p, s, e):
    """删除段内 w:t 文本流 [s,e) 区间；run 被删空且无其他内容子节点时删 run。"""
    off = 0
    for t in wt_nodes(p):
        txt = t.text or ''
        a, b = off, off + len(txt)
        off = b
        if b <= s or a >= e:
            continue
        cs, ce = max(s - a, 0), min(e - a, len(txt))
        t.text = txt[:cs] + txt[ce:]
        r = t.getparent()
        if tag(r) == 'r' and not (t.text or ''):
            # run 内还有其他内容（w:br/tab/drawing 等）则保留
            others = [c for c in r if tag(c) not in ('rPr', 't')]
            if not others and not [x for x in r.findall(q('t')) if (x.text or '')]:
                r.getparent().remove(r)
    return

def insert_text_at(p, pos, s):
    """在段内 w:t 文本流 pos 处插入字符串（落在哪个 w:t 就插入哪个）。"""
    off = 0
    for t in wt_nodes(p):
        txt = t.text or ''
        a, b = off, off + len(txt)
        if a <= pos <= b:
            t.text = txt[:pos - a] + s + txt[pos - a:]
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            return True
        off = b
    return False

def ensure_qnum_rpr(r):
    """题号块 run 补加粗＋底纹 C7C7C7（缺才补）。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    if rpr.find(q('b')) is None:
        b = etree.Element(q('b')); rpr.insert(0, b)
    if rpr.find(q('shd')) is None:
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), 'C7C7C7')
        rpr.append(shd)  # rPr 内 shd 序靠后（bdr 之后），追加即合法

def expand_qnum(p, no, grade):
    """题号块「N．」扩为「N．（档位）」；与题干同 run/跨 run 的先拆出独立 run。"""
    runs = [c for c in p if tag(c) == 'r']
    if not runs:
        return False
    r0 = runs[0]
    t0s = r0.findall(q('t'))
    t0 = t0s[0] if t0s else None
    if t0 is None:
        return False
    txt = t0.text or ''
    want = '%d．' % no
    if txt == want or txt == '%d．（%s）' % (no, grade):
        pass  # 已独立
    elif txt.startswith(want):
        # 同 run 粘连题干：拆分为 [N．]＋[其余]
        rest = txt[len(want):]
        t0.text = want
        t0.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        nr = etree.fromstring(etree.tostring(r0))
        nt = nr.findall(q('t'))[0]
        nt.text = rest
        nt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r0.addnext(nr)
    elif want.startswith(txt):
        # 跨 run（如「1」＋「．平行线…」）：从后续 run 逐字符借入 r0
        need = len(want) - len(txt)
        for r1 in runs[1:]:
            ts1 = r1.findall(q('t'))
            if not ts1:
                continue
            t1 = ts1[0]
            v = t1.text or ''
            take = v[:need]
            t0.text = (t0.text or '') + take
            t1.text = v[len(take):]
            t0.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t1.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            need -= len(take)
            if need <= 0:
                break
        if (t0.text or '') != want:
            return False
    else:
        return False
    if (t0.text or '') == want:
        t0.text = '%d．（%s）' % (no, grade)
    ensure_qnum_rpr(r0)
    return True

def migrate(path, mapmd):
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    els = list(body)

    # 题块切分（与 extract_structure 同口径：题号段→下一题号段/标题/表格前）
    def classify(el):
        if el.tag != q('p'):
            return 'other'
        t = ptext(el)
        if re.match(r'^\d+(\.\d+)*\s+\S', t):
            return 'head'
        if re.match(r'^\d+．', t):
            return 'q'
        return 'para'
    kinds = [classify(el) for el in els]
    rows, migrated, skipped, ent, errors = [], 0, 0, 0, []
    i = 0
    n = len(els)
    while i < n:
        if kinds[i] != 'q':
            i += 1; continue
        j = i + 1
        while j < n and kinds[j] == 'para':
            j += 1
        qps = [el for el in els[i:j] if el.tag == q('p')]
        # 含表格块：表内段落也纳入【难度】检索（讲练件标签行均在正文，此处仅兜底）
        for el in els[i:j]:
            if el.tag == q('tbl'):
                qps += list(el.iter(q('p')))
        mno = re.match(r'^(\d+)．', ptext(els[i]))
        no = int(mno.group(1))
        # 找【难度】所在段
        dp, dm = None, None
        for p in qps:
            m = DIFF_RE.search(ptext(p))
            if m:
                dp, dm = p, m
                break
        if dp is None:
            blk_txt = '\n'.join(ptext(p) for p in qps)
            if re.match(r'^\d+．（(简单|中档|难)(·(保60%|保80%|冲100%)·卡壳看答案)?)', ptext(els[i])):
                skipped += 1
            elif '【答案】' in blk_txt:
                errors.append('题%d 无【难度】字段且题号块无档位' % no)
            else:
                ent += 1  # 讲部编号条目（「N．」起段但非题块），不动
            i = j; continue
        raw = dm.group(1)
        if re.match(r'^[\d.]+$', raw):
            v = float(raw)
            grade = next(w for lim, w in NUM2WORD if v >= lim)
            src = '数值%s→%s' % (raw, grade)
        else:
            grade = raw
            src = raw
        # 删【难度】字段：区间＝【难度】起→值末，连带一个分隔空格（优先后，无后则前）
        full = ptext(dp)
        s, e = dm.start(), dm.end()
        if e < len(full) and full[e] in ' 　':
            e += 1
        elif s > 0 and full[s - 1] in ' 　':
            s -= 1
        delete_range(dp, s, e)
        if not expand_qnum(els[i], no, grade):
            errors.append('题%d 题号块拆 run 失败' % no)
        rows.append((no, grade, src))
        migrated += 1
        i = j

    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.diffmig'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name, b in parts.items():
        zo.writestr(name, b)
    zo.close()
    for k in range(12):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            time.sleep(6)
    else:
        raise RuntimeError('locked: ' + path)

    with open(mapmd, 'w', encoding='utf-8') as f:
        f.write('# 难度前置映射表：%s\n\n' % os.path.basename(path))
        f.write('| 题号 | 档位 | 原值 |\n|---|---|---|\n')
        for no, grade, src in rows:
            f.write('| %d | %s | %s |\n' % (no, grade, src))
        f.write('\n迁移 %d 题；跳过（已迁移）%d；异常 %d 起。\n' % (migrated, skipped, len(errors)))
        if errors:
            f.write('\n'.join('- ' + e for e in errors))
    print('迁移 %d | 跳过 %d | 讲部条目 %d | 异常 %d -> %s' % (migrated, skipped, ent, len(errors), mapmd))
    for e in errors:
        print('  !', e)

if __name__ == '__main__':
    migrate(sys.argv[1], sys.argv[2])
