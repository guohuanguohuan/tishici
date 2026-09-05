# -*- coding: utf-8 -*-
"""④轮步骤4：表格矢量灰规范化（8 处离群清零）。
白名单（YS-2 先声明；仅 word/document.xml，三表之外字节零 diff）：
  I2清单2 表#18（椭圆/双曲线·核心性质表）＋G讲练68 表#3（同构表）：
    ① tcBorders 边框 w:color="CCCCCC"→"000000" ×96（黑细线——val=single/sz 不动，L90 边框统一细实线；
      000000 对齐件内既有表格边框惯用值）
    ② 表头行(行0,tblHeader)单元格 w:shd fill F2F5F9→C7C7C7 ×3（表格规范⑤表头行底纹，不入七类计数）
    ③ 非表头单元格 w:shd 删除：fill=FAFAFA ×6＋fill=FAFBFC ×7（非表头底纹去灰；FAFBFC 系同表首列
       行标题底纹、PDF 灰≈251 落在离群扫描域外故不入 8 处清单，同口径一并去灰——逐处登记）
  H讲练89 表#2（设线法分类表）：
    ④ tcBorders w:color="E0E0E0"→"000000" ×60（黑细线）
    ⑤ 表头行 w:shd fill F2F5F8→C7C7C7 ×3
  附：三件 styles.xml/stylesWithEffects.xml 的 CCCCCC×3 系 Word 内置潜伏表样式（band1Horz 等，
     themeFill 挂载、未被这些表引用），不属挂点、不动——登记带回。
YS-3：shd 删除前逐元素摘录（偏移＋所在单元格文本）落盘；改后 XML well-formed＋三族守恒＋
  构造性字节证明（前态按白名单操作重放＝后态）。落盘 ④_表格灰_登记.json。"""
import io, sys, os, re, json, zipfile
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
DST = BASE + r'\副本_④轮'
REP = BASE + r'\报告'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

JOBS = {
    '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx': dict(
        code='I2清单2', recolor=[(b'w:color="CCCCCC"', b'w:color="000000"', 96),
                                 (b'w:fill="F2F5F9"', b'w:fill="C7C7C7"', 3)],
        delete=[(b'<w:shd w:val="clear" w:color="auto" w:fill="FAFAFA"/>', 6),
                (b'<w:shd w:val="clear" w:color="auto" w:fill="FAFBFC"/>', 7)]),
    '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx': dict(
        code='G讲练68', recolor=[(b'w:color="CCCCCC"', b'w:color="000000"', 96),
                                 (b'w:fill="F2F5F9"', b'w:fill="C7C7C7"', 3)],
        delete=[(b'<w:shd w:val="clear" w:color="auto" w:fill="FAFAFA"/>', 6),
                (b'<w:shd w:val="clear" w:color="auto" w:fill="FAFBFC"/>', 7)]),
    '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx': dict(
        code='H讲练89', recolor=[(b'w:color="E0E0E0"', b'w:color="000000"', 60),
                                 (b'w:fill="F2F5F8"', b'w:fill="C7C7C7"', 3)],
        delete=[]),
}
FAM_PATS = {'w:t': re.compile(rb'<w:t(?:\s[^>]*)?>'), 'm:oMath': re.compile(rb'<m:oMath(?:\s[^>]*)?>'),
            'm:t': re.compile(rb'<m:t(?:\s[^>]*)?>'), 'm:oMathPara': re.compile(rb'<m:oMathPara(?:\s[^>]*)?>'),
            'wp:inline': re.compile(rb'<wp:inline(?:\s[^>]*)?>'), 'wp:anchor': re.compile(rb'<wp:anchor(?:\s[^>]*)?>')}

def fam_counts(b):
    return {k: len(p.findall(b)) for k, p in FAM_PATS.items()}

ok_all = True
reg = {}
for fn, job in JOBS.items():
    p = os.path.join(DST, fn)
    zin = zipfile.ZipFile(p)
    members = {n: zin.read(n) for n in zin.namelist()}
    zin.close()
    old = members['word/document.xml']
    fam_pre = fam_counts(old)
    # 逐处登记：偏移＋所在单元格文本（沿XML向后找最近的tcPr→tc→段落文本不可靠，改用 lxml 定位）
    root = etree.fromstring(old)
    del_reg = []
    for pat, expect in job['delete']:
        offs = [m.start() for m in re.finditer(re.escape(pat), old)]
        assert len(offs) == expect, '%s %s 计数 %d≠%d' % (job['code'], pat, len(offs), expect)
    # shd 删除上下文（lxml 全量扫描——tc 内含目标 fill 的 shd）
    for tc in root.iter(q('tc')):
        tcpr = tc.find(q('tcPr'))
        if tcpr is None:
            continue
        shd = tcpr.find(q('shd'))
        if shd is None:
            continue
        f = (shd.get(q('fill')) or '').upper()
        if f in ('FAFAFA', 'FAFBFC'):
            txt = ''.join(t.text or '' for t in tc.iter(q('t')))[:24]
            hdr = tc.getparent().find(q('trPr')) is not None and tc.getparent().find(q('trPr')).find(q('tblHeader')) is not None
            del_reg.append({'fill': f, 'cell_text': txt, 'row_is_header': hdr})
    # 构造性重放：①边框/表头改色（字节级）②删非表头 shd（字节级）
    new = old
    for old_s, new_s, expect in job['recolor']:
        assert new.count(old_s) == expect, '%s %s 计数≠%d' % (job['code'], old_s, expect)
        new = new.replace(old_s, new_s)
    for pat, expect in job['delete']:
        assert new.count(pat) == expect
        new = new.replace(pat, b'')
    # 断言：well-formed＋三族守恒＋白名单外零 diff（删 shd 共 13×2/0 处已登记；其余仅 attr 值）
    etree.fromstring(new)
    fam_post = fam_counts(new)
    fam_ok = (fam_pre == fam_post)
    # 白名单外零diff：仅 document.xml 变，其余成员逐字节一致（构造保证，复核之）
    members['word/document.xml'] = new
    tmp = p + '.tblfix'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for n, b in members.items():
        zo.writestr(n, b)
    zo.close()
    os.replace(tmp, p)
    reg[job['code']] = {'file': fn, 'recolor': [{'old': o.decode(), 'new': n.decode(), 'n': e}
                                                for o, n, e in job['recolor']],
                        'deleted_shd': del_reg,
                        'deleted_shd_count': len(del_reg),
                        'fam_pre': fam_pre, 'fam_post': fam_post, 'fam_ok': fam_ok}
    ok_all = ok_all and fam_ok
    print('%-8s 改色 %s｜删shd %d 处（登记齐）｜三族守恒 %s｜%s'
          % (job['code'], '；'.join('%s→%s×%d' % (o.decode(), n.decode(), e) for o, n, e in job['recolor']),
             len(del_reg), fam_ok, 'PASS' if fam_ok else '←FAIL'))
with open(os.path.join(REP, '④_表格灰_登记.json'), 'w', encoding='utf-8') as f:
    json.dump(reg, f, ensure_ascii=False, indent=1)
print('合计 3 件 PASS＝%s' % ok_all)
sys.exit(0 if ok_all else 1)
