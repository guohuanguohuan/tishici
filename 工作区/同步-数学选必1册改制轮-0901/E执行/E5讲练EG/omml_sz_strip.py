# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
r"""omml_sz_strip.py — OMML公式run显式w:sz/w:szCs剥除（A'改制轮§6裁决1；E5一次性脚本）

动作：m:oMath/m:oMathPara 子树内全部 w:sz/w:szCs 显式挂点剥除（m:r的w:rPr、m:ctrlPr的w:rPr、
其他math容器内挂点），交 docDefaults 继承24半点。公式字体Cambria Math与公式内容不碰、
w:t/m:t文字流零改动（断言）。幂等（二跑剥除计数=0）。

用法: python omml_sz_strip.py <in.docx> <out.docx> [--json 报告.json]
"""
import sys, os, re, json, zipfile, shutil, tempfile

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

OMML_ROOTS = (m('oMath'), m('oMathPara'))


def text_stream(root):
    """w:t + m:t 全文档序拼接（文字流断言用）。"""
    out = []
    for el in root.iter():
        ln = el.tag.rsplit('}', 1)[-1] if isinstance(el.tag, str) else ''
        if ln in ('t',):
            out.append(el.text or '')
    return ''.join(out)


def strip_part(data):
    """对单个xml部件剥除OMML子树内w:sz/w:szCs。返回 (new_bytes, 计数dict, 变更bool)。"""
    from lxml import etree
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(data, parser)
    before_text = text_stream(root)
    counts = {}
    n = 0
    # 先全量收集（含math子树嵌套去重），后统一删除——禁止边iter边改树（lxml迭代中修改会跳元素）
    targets = []
    seen = set()
    math_roots = [el for el in root.iter() if el.tag in OMML_ROOTS]
    for omath in math_roots:
        for el in omath.iter():
            if el.tag in (q('sz'), q('szCs')) and id(el) not in seen:
                seen.add(id(el))
                targets.append(el)
    for el in targets:
        parent = el.getparent()
        gp = parent.getparent() if parent is not None else None
        kind = 'other'
        if gp is not None and gp.tag == m('ctrlPr'):
            kind = 'ctrlPr'
        elif gp is not None and gp.tag == m('r'):
            kind = 'm_r'
        elif gp is not None and gp.tag == q('r'):
            kind = 'w_r_in_math'
        val = el.get(q('val')) or ''
        counts['%s:%s' % (kind, val)] = counts.get('%s:%s' % (kind, val), 0) + 1
        el.getparent().remove(el)
        n += 1
    after_text = text_stream(root)
    assert before_text == after_text, '文字流前后不等（剥除误伤文字）'
    out = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    return out, {'strip_total': n, 'by_kind_val': counts}, (n > 0)


def main(argv):
    argv = list(argv)
    jsonpath = None
    if '--json' in argv:
        i = argv.index('--json')
        if i + 1 < len(argv):
            jsonpath = argv[i + 1]
            del argv[i:i + 2]
    args = [a for a in argv if not a.startswith('--')]
    if len(args) != 2:
        print(__doc__)
        return 2
    src, dst = args
    zin = zipfile.ZipFile(src, 'r')
    tmp = tempfile.mktemp(suffix='.docx')
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    report = {'src': os.path.basename(src), 'parts': {}}
    total = 0
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.startswith('word/') and item.filename.endswith('.xml'):
            if b'oMath' in data:
                new, cnt, changed = strip_part(data)
                if changed:
                    report['parts'][item.filename] = cnt
                    total += cnt['strip_total']
                    data = new
        # 保持压缩属性
        zi = zipfile.ZipInfo(item.filename, date_time=item.date_time)
        zi.compress_type = item.compress_type
        zi.external_attr = item.external_attr
        zi.internal_attr = item.internal_attr
        zi.create_system = item.create_system
        zout.writestr(zi, data)
    zout.close(); zin.close()
    report['strip_total_all_parts'] = total
    if os.path.abspath(dst) != os.path.abspath(src):
        shutil.move(tmp, dst)
    else:
        shutil.move(tmp, dst)
    if jsonpath:
        with open(jsonpath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
    print('OMML sz strip:', os.path.basename(src), '->', os.path.basename(dst),
          'total=', total, 'parts=', len(report['parts']))
    for p, c in report['parts'].items():
        print(' ', p, c)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
