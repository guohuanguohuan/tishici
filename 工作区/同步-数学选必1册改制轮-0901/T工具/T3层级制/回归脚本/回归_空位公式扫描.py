# -*- coding: utf-8 -*-
"""回归_空位公式扫描.py — 62题掉位回归门（A'改制轮·工具债③·T3）
样例自建：从讲练副本（C讲练下）构造已知掉位样例——复刻历史缺陷家族（2026-08-26 讲练下62题
「5式并1块堆段尾」＋「已知点，平面过原点，且垂直于向量」量词空位）＋v3新增签名样例
（「．」收尾变体、焦点词表、多赋值粘连、行内公式图片盲区抑制）。
门判据：四签名各自命中≥1 且 抑制样例不命中 —— 命中≥1才算升级成功（规格书§2工具债③）。
只动工作区副本，禁止触碰产出文件夹。"""
import sys, os, re, shutil, zipfile, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)                    # T3层级制/
SAMPLE_DIR = os.path.join(ROOT, '测试副本')
SRC = os.path.join(SAMPLE_DIR, 'C讲练下（79题）.docx')
SAMPLE = os.path.join(SAMPLE_DIR, '62题掉位回归样例.docx')
TOOL = r'C:\提示词\工具\空位公式扫描.py'

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

MARK = '回归样例'   # 样例段标记（断言用：命中须落在样例段上）


def build_sample():
    shutil.copyfile(SRC, SAMPLE)
    z = zipfile.ZipFile(SAMPLE)
    doc = etree.fromstring(z.read('word/document.xml'))
    names = z.namelist()
    z.close()
    body = doc.find(q('body'))

    # 找一个现成 w:drawing（行内图）供盲区抑制样例克隆
    drawing = None
    for d in body.iter(q('drawing')):
        drawing = d
        break
    assert drawing is not None, '源件未找到 w:drawing（盲区样例无载体）'

    def para(runs):
        p = etree.Element(q('p'))
        for kind, content in runs:
            r = etree.SubElement(p, q('r'))
            if kind == 't':
                t = etree.SubElement(r, q('t'))
                t.text = content
            elif kind == 'math':
                om = etree.SubElement(p, m('oMath'))
                mr = etree.SubElement(om, m('r'))
                mt = etree.SubElement(mr, m('t'))
                mt.text = content
            elif kind == 'img':
                import copy
                r.append(copy.deepcopy(drawing))
        return p

    # 样例段（插入 body 末尾 sectPr 前）：
    # S1 ③量词空位（62题历史形态：点，/向量，双空位、双逗不相邻①不触发）
    p1 = para([('t', '【%s1】已知点，平面过原点，且垂直于向量，求该平面方程．' % MARK)])
    # S2 ①双逗空位（主判据）
    p2 = para([('t', '【%s2】如图，，所示，求二面角的大小．' % MARK)])
    # S3 ②段尾公式簇＋④多赋值粘连（62题「5式并1块」复刻：）收尾后单块5式）
    p3 = para([('t', '【%s3】依题意建立坐标系（O为原点）' % MARK), ('math', 'a=1b=2c=3d=4e=5')])
    # S4 ③「．」收尾变体＋焦点词表（v3新增）＋②句点收尾簇＋④值起点粘连
    p4 = para([('t', '【%s4】已知焦点．于是有' % MARK), ('math', 'x=2y=3z=4')])
    # S5 盲区抑制（H①=1误报根因）：行内公式图片恰在两全角逗号之间——旧版视图片不可见判「，，」
    #    误报①；v3图件计为公式对象后应零命中
    p5 = para([('t', '【%s5】建立空间直角坐标系（O为原点），' % MARK), ('img', None), ('t', '，垂足为P．')])
    sect = body.find(q('sectPr'))
    for p in (p1, p2, p3, p4, p5):
        if sect is not None:
            sect.addprevious(p)
        else:
            body.append(p)

    new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    import tempfile
    fd, tmp = tempfile.mkstemp(suffix='.docx', dir=SAMPLE_DIR)
    os.close(fd)
    with zipfile.ZipFile(SAMPLE) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
            zout.writestr(item, data)
    os.replace(tmp, SAMPLE)
    return names


def load_scanner():
    spec = importlib.util.spec_from_file_location('kongwei_scan', TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    from lxml import etree  # noqa: F401  (build_sample 内使用)
    globals()['etree'] = etree
    build_sample()
    mod = load_scanner()
    rows, counts = mod.scan_file(SAMPLE)
    print('样例件全件命中计数:', counts)
    # 按样例标记逐段核验（不依赖摘录窗口是否含标记）
    z = zipfile.ZipFile(SAMPLE)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    per = {}
    for p in root.iter(mod.WT_P):
        seq = mod.paragraph_seq(p)
        txt = ''.join(s for k, s in seq if k == 't')
        mk = re.search(r'【%s([1-5])】' % MARK, txt)
        if mk:
            per[mk.group(1)] = (mod.scan_paragraph(seq), txt)
    ok = True
    def gate(cond, msg):
        nonlocal ok
        print(('  PASS ' if cond else '  FAIL ') + msg)
        ok = ok and cond
    gate('1' in per and '③' in per['1'][0] and '2处' in per['1'][0]['③'][0],
         'S1 ③量词空位＝62题历史形态（点，／向量，2处，双逗不相邻①不触发）')
    gate('1' in per and '①' not in per['1'][0], 'S1 ①不触发（量词空位与双逗分工正确）')
    gate('2' in per and '①' in per['2'][0], 'S2 ①双逗空位（主判据）命中')
    gate('3' in per and '②' in per['3'][0] and '碎片=5' in per['3'][0]['②'][0],
         'S3 ②段尾公式簇＝62题「5式并1块」复刻（碎片=5）')
    gate('3' in per and '④' in per['3'][0], 'S3 ④多赋值粘连命中（a=1b=2c=3d=4e=5）')
    gate('4' in per and '③' in per['4'][0] and '焦点' in per['4'][0]['③'][0],
         'S4 ③「．」收尾变体＋焦点词表命中（v3增签）')
    gate('4' in per and '④' in per['4'][0], 'S4 ④值起点粘连命中（x=2y=3z=4）')
    gate('5' in per and not per['5'][0],
         'S5 盲区抑制：行内公式图片在「，，」之间零命中（H①=1误报根因修复）')
    gate(counts['①'] >= 1 and counts['②'] >= 1 and counts['③'] >= 1 and counts['④'] >= 1,
         '回归门总量：四签名各命中≥1（命中≥1才算升级成功）')
    print('回归门结论：' + ('通过（命中≥1，升级成功）' if ok else '不通过'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
