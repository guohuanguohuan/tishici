# -*- coding: utf-8 -*-
"""M1盖章·自检①②③：XML层全量断言——sectPr start级联／页脚域形态／件标识N／pgMar850／titlePg／updateFields。
纯zip读取，无COM。落盘 自检XML输出.txt + 自检XML结果.json"""
import io
import json
import os
import re
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
PROD = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'

EXPECT = [  # (件名, 部分tag, start, N)
    ('人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', '第1章·衔接', 1, 20),
    ('人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', '第1章·清单', 1, 20),
    ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', '第1章·讲练', 1, 156),
    ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', '第1章·讲练', 79, 156),
    ('人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', '第2章·衔接', 1, 4),
    ('人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', '第2章·清单', 1, 40),
    ('人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', '第2章·讲练', 1, 197),
    ('人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', '第2章·讲练', 48, 197),
    ('人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', '第2章·讲练', 99, 197),
    ('人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', '第2章·讲练', 135, 197),
]

N_ALL = [0]
N_FAIL = [0]


def run():
    results = []
    for name, tag, start, N in EXPECT:
        path = os.path.join(PROD, name)
        z = zipfile.ZipFile(path)
        names = z.namelist()
        footers = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
        doc = z.read('word/document.xml').decode('utf-8')
        settings = z.read('word/settings.xml').decode('utf-8')
        checks = {}

        def chk(key, cond, detail=''):
            N_ALL[0] += 1
            if not cond:
                N_FAIL[0] += 1
            checks[key] = ('PASS' if cond else 'FAIL') + ((' ' + detail) if detail else '')

        # ② 唯一页脚部件
        chk('唯一页脚部件', len(footers) == 1, 'footer数=%d' % len(footers))
        ftr = z.read(footers[0]).decode('utf-8')
        # ② 域形态断言
        chk('fldChar-begin=1', ftr.count('fldCharType="begin"') == 1, '=%d' % ftr.count('fldCharType="begin"'))
        chk('fldChar-end=1', ftr.count('fldCharType="end"') == 1, '=%d' % ftr.count('fldCharType="end"'))
        chk('fldChar-separate=1', ftr.count('fldCharType="separate"') == 1, '=%d' % ftr.count('fldCharType="separate"'))
        chk('instrText含PAGE', ' PAGE ' in ftr)
        chk('无NUMPAGES', 'NUMPAGES' not in ftr)
        chk('无fldSimple', 'fldSimple' not in ftr)
        chk('页脚唯一自动数(instrText组数=1)', len(re.findall(r'<w:instrText[^>]*>[^<]*</w:instrText>', ftr)) == 1)
        # ③ 件标识与N（页脚可见文本整串核对）
        vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', ftr))
        expect_vis = '%s（共%d页）　第%d页' % (tag, N, start)
        chk('页脚可见文本=件标识（共N页）第start页', vis == expect_vis, '%r' % vis)
        # ② 页脚字号9pt／字体／左对齐／单段
        szs = re.findall(r'<w:sz w:val="(\d+)"/>', ftr)
        chk('页脚全部run字号18半点', bool(szs) and all(s == '18' for s in szs), 'sz集合=%s' % sorted(set(szs)))
        chk('页脚宋体+TNR', 'w:eastAsia="宋体"' in ftr and 'Times New Roman' in ftr)
        chk('页脚左对齐jc=left', '<w:jc w:val="left"/>' in ftr)
        chk('页脚单段落', len(re.findall(r'<w:p\b', ftr)) == 1, '段数=%d' % len(re.findall(r'<w:p\b', ftr)))
        # PAGE域缓存=start（separate与end之间的w:t）
        m = re.search(r'fldCharType="separate"/>.*?<w:t[^>]*>(\d+)</w:t>.*?fldCharType="end"', ftr, re.S)
        chk('PAGE域缓存=start', m is not None and int(m.group(1)) == start,
            '缓存=%s' % (m.group(1) if m else 'None'))
        # ① sectPr start实测=预期级联（全部sectPr）
        starts = [int(x) for x in re.findall(r'<w:pgNumType w:start="(\d+)"/>', doc)]
        chk('sectPr start级联', starts == [start], '=%s 预期[%d]' % (starts, start))
        # ① pgMar footer=850（全部sectPr）
        foots = set(re.findall(r'w:footer="(\d+)"', doc))
        chk('pgMar footer=850', foots == {'850'}, '=%s' % sorted(foots))
        chk('无titlePg', '<w:titlePg' not in doc)
        chk('settings含updateFields', '<w:updateFields' in settings)
        chk('settings无evenAndOddHeaders', '<w:evenAndOddHeaders' not in settings)
        z.close()
        results.append({'file': name, 'tag': tag, 'start': start, 'N': N, 'checks': checks})
    return results


results = run()
out = []
for r in results:
    out.append('== %s | %s | start=%d | N=%d ==' % (r['file'][:44], r['tag'], r['start'], r['N']))
    for k, v in r['checks'].items():
        out.append('  [%s] %s' % (v.split()[0], k + ('' if v.split()[0] == 'PASS' else ' <' + ' '.join(v.split()[1:]) + '>')))
out.append('断言总数=%d FAIL=%d -> %s' % (N_ALL[0], N_FAIL[0], '全绿' if N_FAIL[0] == 0 else '存在失败'))
open(os.path.join(BASE, '自检XML输出.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
json.dump(results, open(os.path.join(BASE, '自检XML结果.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n'.join(out[-3:]))
print('总断言=%d 失败=%d' % (N_ALL[0], N_FAIL[0]))
sys.exit(1 if N_FAIL[0] else 0)
