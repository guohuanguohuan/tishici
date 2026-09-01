# -*- coding: utf-8 -*-
"""一次性脚本（E3讲练B）——OMML公式run显式w:sz/w:szCs剥除（规格书§6裁决1/A0-裁决①）
m:oMath子树内一切 w:sz/w:szCs 删除（18/21历史杂值统一交docDefaults继承24半点）；
公式字体Cambria Math与公式内容不碰、文字零改动（w:t/m:t流前后恒等断言）；
逐挂点族计数落盘（m:r/w:rPr 与 m:ctrlPr/w:rPr 分列＋删除值分布）。幂等（二跑删除0）。"""
import sys, os, re, zipfile, json, tempfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)

path = sys.argv[1]
report = sys.argv[2]

zin = zipfile.ZipFile(path)
members = zin.namelist()
parts = {n: zin.read(n) for n in members}
zin.close()

total = {'m:r': {}, 'm:ctrlPr': {}, 'other': {}}
removed_runs = 0
part_stats = {}
for name in sorted(members):
    if not (name.startswith('word/') and name.endswith('.xml')):
        continue
    if b'oMath' not in parts[name]:
        continue
    root = etree.fromstring(parts[name])
    dirty = False
    stats = {'m:r': {}, 'm:ctrlPr': {}, 'other': {}, '删除元素数': 0}
    for om in root.iter(qm('oMath'), qm('oMathPara')):
        pass
    # 遍历所有 w:sz/w:szCs，凡位于 m:oMath/m:oMathPara 子树内者删除
    def in_math(el):
        a = el.getparent()
        while a is not None:
            if a.tag in (qm('oMath'), qm('oMathPara')):
                return True
            a = a.getparent()
        return False
    for el in list(root.iter(q('sz'))) + list(root.iter(q('szCs'))):
        if not in_math(el):
            continue
        # 挂点族：最近的 math 命名空间祖先（m:r 或 m:ctrlPr）
        fam = 'other'
        a = el.getparent()  # w:rPr
        a = a.getparent() if a is not None else None
        while a is not None:
            if a.tag == qm('ctrlPr'):
                fam = 'm:ctrlPr'; break
            if a.tag == qm('r'):
                fam = 'm:r'; break
            if a.tag in (qm('oMath'), qm('oMathPara')):
                break
            a = a.getparent()
        val = el.get(q('val'))
        key = '%s=%s' % (etree.QName(el).localname, val)
        stats[fam][key] = stats[fam].get(key, 0) + 1
        stats['删除元素数'] += 1
        el.getparent().remove(el)
        dirty = True
    if dirty:
        # 清空 rPr（删除后可能空壳——留空壳合法，不清理，保守零副作用）
        parts[name] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        part_stats[name] = stats
        for fam in ('m:r', 'm:ctrlPr', 'other'):
            for k, v in stats[fam].items():
                total[fam][k] = total[fam].get(k, 0) + v

# 文字流恒等断言（w:t+m:t，全包）
def text_stream(parts, members):
    out = []
    for n in members:
        if not (n.startswith('word/') and n.endswith('.xml')):
            continue
        root = etree.fromstring(parts[n])
        for t in root.iter():
            if isinstance(t.tag, str) and etree.QName(t).localname == 't':
                out.append(t.text or '')
    return ''.join(out)

# 剥除不改文字（只有属性树变化），断言照做：与输入流比对
# 输入流重新读zip
z2 = zipfile.ZipFile(path)
in_stream = []
for n in members:
    if not (n.startswith('word/') and n.endswith('.xml')):
        continue
    root = etree.fromstring(z2.read(n))
    for t in root.iter():
        if isinstance(t.tag, str) and etree.QName(t).localname == 't':
            in_stream.append(t.text or '')
z2.close()
assert text_stream(parts, members) == ''.join(in_stream), '文字流变化——禁止落盘'

tmp = path + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n in members:
        zo.writestr(n, parts[n])
os.replace(tmp, path)

with open(report, 'w', encoding='utf-8') as f:
    json.dump({'文件': os.path.basename(path), '剥除挂点分族': total,
               '分部件': part_stats}, f, ensure_ascii=False, indent=1)
n_removed = sum(sum(v.values()) for v in total.values())
print('OMML w:sz/szCs 剥除元素数 =', n_removed)
print(json.dumps(total, ensure_ascii=False))
