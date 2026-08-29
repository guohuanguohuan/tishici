# -*- coding: utf-8 -*-
#
# 收编：2026-08-29 条目号底纹轮·选必1两清单件落地（公共规则§7题号难度块底纹条款·条目号底纹）
#
"""条目号底纹.py — 知识清单件条目题名行条目号「N．」挂 C9C9C9 底纹（可复用，幂等）

口径注记（2026-08-29 用户拍板改口径，公共规则§7已落库）：知识清单件条目题名行的条目号
「N．」（数字＋全角句点）挂 w:shd val="clear" color="auto" fill="C9C9C9"——只盖条目号本身、
不盖题名文字（同 run 先拆独立 run 再挂）、不加粗（纯序号锚，与块标签芯片同则）；
恒等式＝条目号底纹 run 数＝条目名计数（件内条目题名行数）。
原 2026-08-28「条目号不挂底纹（条目非题目）」口径废止。
节标题序号底纹（类②，2026-08-28）与内容标记底纹（类④）不受影响。

条目题名行判定：body 级段落全文匹配 ^\\d+．（全角句点）。节标题为 N.N(.N) 式、无全角句点起段；
清单件无题号块——两者天然不与本判定冲突。

行为：
  · 条目号与题名同 run → 拆出独立 run（深拷 rPr，题名文字形态不变）；
  · 条目号跨多 run（如「12」＋「．题名」）→ 归并为单一「N．」run（字符合并、顺序不变、零字符增删）；
  · 已挂（恰有一独立 C9C9C9 run＝「N．」）→ 跳过并计数（幂等，重复执行安全）；
  · 底纹 run 强制去加粗（删 w:b/w:bCs）——不加粗口径；
  · 修改的 w:t 一律置 xml:space="preserve" 防吞空格。
输出：登记 md（条目号→条目名首句）＋stdout 计数（条目名计数/新挂/已挂跳过）与恒等式断言。

用法: python 条目号底纹.py <docx> <登记md>
"""
import sys, io, os, re, zipfile, shutil, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILL = 'C9C9C9'
ENT_RE = re.compile(r'^(\d+)．')   # 条目号：数字＋全角句点

def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))

def set_run_text(r, txt):
    """run 文字整体替换（多个 w:t 归一为一个，置 preserve）。"""
    for t in r.findall(q('t')):
        r.remove(t)
    t = etree.SubElement(r, q('t'))
    t.text = txt
    if txt != txt.strip() or txt == '':
        t.set(XMLSPACE, 'preserve')
    return t

def ensure_shd(r):
    """run 补 w:shd C9C9C9（缺才补；schema 序：vertAlign/rtl/lang 等尾部元素之前、否则末尾）。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr'))
        r.insert(0, rpr)
    shd = rpr.find(q('shd'))
    if shd is None:
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
        anchor = None
        for name in ('vertAlign', 'rtl', 'lang', 'eastAsianLayout', 'specVanish', 'oMath'):
            e = rpr.find(q(name))
            if e is not None:
                anchor = e
                break
        if anchor is not None:
            anchor.addprevious(shd)
        else:
            rpr.append(shd)
    else:
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
    return shd

def strip_bold(r):
    """去加粗（不加粗口径）：删 w:b / w:bCs。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        return
    for name in ('b', 'bCs'):
        e = rpr.find(q(name))
        if e is not None:
            rpr.remove(e)

def is_shaded(r):
    rpr = r.find(q('rPr'))
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd is not None and shd.get(q('fill')) == FILL

def process_para(p):
    """处理一个条目题名行。返回 'skip'（已挂幂等）| 'done'（本轮新挂/拆分/归并）| None（异常不动）。

    单 run 含「N．题名」→ 拆两 run；条目号跨多 run（如「12」＋「．题名」）→ 归并为单一「N．」run
    （字符合并、顺序不变、零字符增删）；已挂（独立 C9C9C9 run＝「N．」）→ 跳过。"""
    full = ''.join(t.text or '' for t in p.iter(q('t')))
    """同 process_para，但单 run 内条目号后带题名时正确拆分（题名回插独立 run）。"""
    full = ''.join(t.text or '' for t in p.iter(q('t')))
    m = ENT_RE.match(full)
    if not m:
        return None
    target = m.group(0)
    need = len(target)
    runs = [c for c in p if tag(c) == 'r']
    texts = [run_text(r) for r in runs]
    for r, tx in zip(runs, texts):
        if tx:
            if tx == target and is_shaded(r):
                strip_bold(r)
                return 'skip'
            break
    s = next((i for i, tx in enumerate(texts) if tx), None)
    if s is None:
        return None
    acc = 0
    k = off = None
    for i in range(s, len(runs)):
        ln = len(texts[i])
        if acc + ln >= need:
            k, off = i, need - acc
            break
        acc += ln
    if k is None:
        return None
    if s == k:
        base = runs[s]
        tx = texts[s]
        rest = tx[off:]
        set_run_text(base, target)
        ensure_shd(base)
        strip_bold(base)
        if rest:
            nr = etree.fromstring(etree.tostring(base))   # 深拷（带 rPr；shd 一并拷入，下面剥掉）
            nrpr = nr.find(q('rPr'))
            if nrpr is not None:
                nshd = nrpr.find(q('shd'))
                if nshd is not None:
                    nrpr.remove(nshd)
            set_run_text(nr, rest)
            base.addnext(nr)
    else:
        set_run_text(runs[s], target)
        ensure_shd(runs[s])
        strip_bold(runs[s])
        for i in range(s + 1, k):
            p.remove(runs[i])
        rest = texts[k][off:]
        if rest:
            set_run_text(runs[k], rest)
        else:
            p.remove(runs[k])
    return 'done'

def first_sentence(title):
    """条目名首句：题名文字至第一个全角句号（含）；无句号取全文。"""
    title = title.strip()
    i = title.find('。')
    return title[:i + 1] if i >= 0 else title

def main(path, regmd):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    rows = []
    n_done = n_skip = 0
    for p in body:
        if p.tag != q('p'):
            continue
        full = ''.join(t.text or '' for t in p.iter(q('t')))
        if not ENT_RE.match(full):
            continue
        num = ENT_RE.match(full).group(0)
        title = full[len(num):]
        st = process_para(p)
        if st == 'skip':
            n_skip += 1
        elif st == 'done':
            n_done += 1
        else:
            print('!! 未处理条目行: %r' % full[:40])
            continue
        rows.append((num, first_sentence(title)))
    n_total = len(rows)
    # 恒等式断言：条目号底纹 run 数＝条目名计数（body 级全部「N．」独立底纹 run，与四类底纹计数口径同源）
    shd_runs = 0
    for p in body:
        if p.tag != q('p'):
            continue
        for r in p.findall(q('r')):
            tx = run_text(r)
            if tx and re.match(r'^\d+．$', tx) and is_shaded(r):
                shd_runs += 1
    ok = (shd_runs == n_total == n_done + n_skip)
    # 落盘 docx（仅替换 word/document.xml，其余成员原样回写）
    new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    fd, tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(path)))
    os.close(fd)
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
            zout.writestr(item, data)
    shutil.move(tmp, path)
    # 登记 md
    lines = []
    lines.append('# 条目号底纹登记 — %s' % os.path.basename(path))
    lines.append('')
    lines.append('轮次：条目号底纹轮 2026-08-29（公共规则§7条目号底纹新口径：C9C9C9 底纹、不加粗、')
    lines.append('只盖条目号本身不盖题名文字；恒等式＝条目号底纹 run 数＝条目名计数；原 08-28 不挂口径废止）')
    lines.append('')
    lines.append('条目名计数 %d｜新挂底纹 %d｜已挂跳过 %d｜条目号底纹 run 数 %d（恒等式 %s）'
                 % (n_total, n_done, n_skip, shd_runs, '成立' if ok else '不成立!!'))
    lines.append('')
    lines.append('| 条目号 | 条目名首句 |')
    lines.append('|---|---|')
    for num, sent in rows:
        lines.append('| %s | %s |' % (num, sent.replace('|', '\\|')))
    lines.append('')
    open(regmd, 'w', encoding='utf-8').write('\n'.join(lines))
    print('条目名计数 %d = 新挂 %d ＋ 已挂跳过 %d；条目号底纹 run 数 %d；恒等式%s'
          % (n_total, n_done, n_skip, shd_runs, '成立 PASS' if ok else '不成立 CHECK'))
    print('登记md -> %s' % regmd)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
