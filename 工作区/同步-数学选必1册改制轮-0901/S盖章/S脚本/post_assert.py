# -*- coding: utf-8 -*-
"""S盖章·盖章后独立断言（不依赖工具代码路径）：
① 页眉页脚两处 PAGE 复杂域缓存 run 文本 = start；
② 页眉页脚两处「（共N页）」= 部分总页数 N；
③ sectPr pgNumType w:start = 指定值（全部sectPr）；
④ settings.xml updateFields=true；⑤ 域形态（无fldSimple/NUMPAGES、复杂域两组）；
⑥ COM 复测页数与盖章前 pre_pages.json 逐一相等（页数零漂移）。
"""
import io
import json
import os
import re
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r'C:\提示词\高中数学\高中数学同步'
SPEC = [  # 代码, 文件名, start, N
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 1, 16),
    ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 1, 20),
    ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 1, 154),
    ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 78, 154),
    ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 1, 5),
    ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 1, 39),
    ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 1, 221),
    ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 54, 221),
    ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 110, 221),
    ('H',  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 151, 221),
]
PRE = json.load(open(os.path.join(HERE, 'pre_pages.json'), encoding='utf-8'))
INSTR_PAGE = re.compile(r'<w:instrText[^>]*>[^<]*\bPAGE\b[^<]*</w:instrText>')


def page_cache(xml):
    ms = INSTR_PAGE.findall(xml)
    assert len(ms) == 1, 'PAGE instrText数=%d' % len(ms)
    m = INSTR_PAGE.search(xml)
    i_sep = xml.index('w:fldCharType="separate"', m.end())
    j = xml.index('<w:t', i_sep)
    gt = xml.index('>', j)
    k = xml.index('</w:t>', j)
    return xml[gt + 1:k]


fail = []
rows = []
for tag, fn, start, n in SPEC:
    p = os.path.join(OUT, fn)
    ok = []
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
        hfs = sorted(x for x in names if re.fullmatch(r'word/header\d+\.xml', x)) + \
              sorted(x for x in names if re.fullmatch(r'word/footer\d+\.xml', x))
        assert len(hfs) == 2, '%s 页眉页脚部件数=%d' % (tag, len(hfs))
        for nm in hfs:
            xml = z.read(nm).decode('utf-8')
            where = '%s:%s' % (tag, os.path.basename(nm))
            c = page_cache(xml)
            ok.append(('X缓存=start', c == str(start), '%s缓存=%s' % (where, c)))
            ns = re.findall(r'（共(\d+)页）', xml)
            ok.append(('N写死', ns == [str(n)], '%s（共N页）=%r' % (where, ns)))
            ok.append(('域形态', xml.count('fldCharType="begin"') == 2 and 'fldSimple' not in xml
                       and 'NUMPAGES' not in xml and 'STYLEREF "节名锚"' in xml, where))
            vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml))
            m = re.fullmatch(r'(.+)（共(\d+)页）　(.+)　第(\d+)页', vis)
            ok.append(('可见串', bool(m) and int(m.group(2)) == n and int(m.group(4)) == start,
                       '%s可见串=%r' % (where, vis[:56])))
        d = z.read('word/document.xml').decode('utf-8')
        starts = [int(x) for x in re.findall(r'<w:pgNumType w:start="(\d+)"/>', d)]
        ok.append(('sectPr start', starts and all(x == start for x in starts) and len(starts) >= 1,
                   '%s sectPr start=%r' % (tag, starts)))
        ok.append(('footer=850缇', 'w:footer="850"' in d, tag))
        ok.append(('无titlePg', '<w:titlePg' not in d, tag))
        s = z.read('word/settings.xml').decode('utf-8')
        ok.append(('updateFields', '<w:updateFields' in s and 'evenAndOddHeaders' not in s, tag))
    bad = [(k, v, e) for k, v, e in ok if not v]
    rows.append((tag, fn, start, n, ok, bad))
    for k, v, e in bad:
        fail.append(e)
        print('  ✗ %s | %s | %s' % (tag, k, e))
    print('%s | start=%d N=%d | %s | %d项断言%s' %
          (tag, start, n, '全过✓' if not bad else 'FAIL', len(ok), '' if not bad else '（失败%d）' % len(bad)))

# COM 页数零漂移复测
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
drift = []
try:
    for tag, fn, start, n in SPEC:
        doc = word.Documents.Open(os.path.join(OUT, fn), ReadOnly=True, AddToRecentFiles=False)
        try:
            cur = doc.ComputeStatistics(2)
        finally:
            doc.Close(False)
        same = cur == PRE[tag]
        print('%s 盖章后复测 %d页 vs 盖章前 %d页 | %s' % (tag, cur, PRE[tag], '零漂移✓' if same else '漂移!'))
        if not same:
            drift.append(tag)
finally:
    word.Quit()

print('===断言汇总：XML级 %s | 页数零漂移 %s===' %
      ('全绿' if not fail else '失败%d项' % len(fail), '全绿' if not drift else '漂移件=%r' % drift))
with open(os.path.join(HERE, 'post_assert.json'), 'w', encoding='utf-8') as f:
    json.dump({'fail': fail, 'drift': drift,
               'detail': {t: {'start': st, 'N': n, 'asserts': len(ok), 'bad': len(bad)}
                          for t, fn, st, n, ok, bad in rows}}, f, ensure_ascii=False, indent=1)
sys.exit(0 if not fail and not drift else 1)
