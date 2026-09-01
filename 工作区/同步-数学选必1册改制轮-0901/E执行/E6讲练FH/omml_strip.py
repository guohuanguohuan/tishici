# -*- coding: utf-8 -*-
"""omml_strip.py — E6一次性脚本（§6裁决1）：m:oMath/m:oMathPara 子树内全部显式 w:sz/w:szCs 剥除
（m:r 挂点与结构 ctrlPr 挂点一律剥，交 docDefaults 继承24半点；公式字体/内容/文字零触碰）。
断言：w:t/m:t 文字流前后恒等；仅移除 w:sz/w:szCs 两类元素、不动其他任何节点。
用法: python omml_strip.py <docx> [--json 报告.json]"""
import sys, os, zipfile, json, time
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def mtag(e):
    try:
        return etree.QName(e).localname
    except ValueError:
        return ''

def text_stream(root):
    return [t.text or '' for t in root.iter() if isinstance(t.tag, str) and mtag(t) == 't']

def main():
    path = sys.argv[1]
    jp = None
    if '--json' in sys.argv:
        jp = sys.argv[sys.argv.index('--json') + 1]
    zin = zipfile.ZipFile(path)
    members = zin.namelist()
    parts = {n: zin.read(n) for n in members}
    zin.close()
    doc = etree.fromstring(parts['word/document.xml'])
    before = ''.join(text_stream(doc))
    counts = {'m:r挂点sz': 0, 'm:r挂点szCs': 0, 'ctrlPr挂点sz': 0, 'ctrlPr挂点szCs': 0,
              '其他math内挂点sz': 0, '其他math内挂点szCs': 0}
    removed_vals = {}
    targets = []
    for el in doc.iter():
        if not isinstance(el.tag, str):
            continue
        if el.tag not in (q('sz'), q('szCs')):
            continue
        # 祖先含 m:oMath / m:oMathPara 才剥
        anc = el.getparent()
        in_math = False
        while anc is not None:
            if isinstance(anc.tag, str) and anc.tag.startswith('{%s}' % M):
                in_math = True
                break
            anc = anc.getparent()
        if in_math:
            targets.append(el)
    for el in targets:
        par = el.getparent()
        # 定位容器：向上找最近的 math 命名空间祖先名
        a = par
        container = '其他math内'
        while a is not None and isinstance(a.tag, str):
            if a.tag.startswith('{%s}' % M):
                ln = a.tag.split('}')[1]
                if ln == 'r':
                    container = 'm:r'
                    break
                if ln == 'ctrlPr':
                    container = 'ctrlPr'
                    break
            a = a.getparent()
        key = container + '挂点' + mtag(el)
        if key not in counts:
            key = '其他math内挂点' + mtag(el)
        counts[key] += 1
        v = el.get(q('val'))
        removed_vals[v] = removed_vals.get(v, 0) + 1
        par.remove(el)
    after = ''.join(text_stream(doc))
    assert after == before, '文字流变化——禁止落盘'
    log = {'文件': os.path.basename(path), '剥除计数': counts,
           '剥除值分布': dict(sorted(removed_vals.items(), key=lambda x: -x[1])),
           '合计': sum(counts.values())}
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                encoding='UTF-8', standalone=True)
    tmp = path + '.tmpstrip'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n in members:
            zo.writestr(n, parts[n])
    for _ in range(12):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            time.sleep(6)
    else:
        raise RuntimeError('locked: ' + path)
    if jp:
        json.dump(log, open(jp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(log, ensure_ascii=False))

if __name__ == '__main__':
    main()
