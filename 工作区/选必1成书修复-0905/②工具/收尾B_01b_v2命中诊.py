# -*- coding: utf-8 -*-
"""收尾B_01b_v2命中诊.py — v2 锚点对十件终态 PDF p1 的逐行命中诊断（只读）。"""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '工具'))
import 首页断言集执行器 as ex
import pymupdf

PDFDIR = os.path.abspath(os.path.join(HERE, '..', '成书交付', '全件PDF'))
V2 = os.path.join(ROOT, '工作区', '同步-数学选必1复合修复-0903', '子步3', '锚点映射表v2.json')
TEN = [
    ('清单1', 'I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.pdf'),
    ('衔接1', 'X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.pdf'),
    ('上61', 'B', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.pdf'),
    ('下79', 'C', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.pdf'),
    ('清单2', 'I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.pdf'),
    ('衔接2', 'X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.pdf'),
    ('92', 'E', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.pdf'),
    ('90', 'F', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.pdf'),
    ('68', 'G', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.pdf'),
    ('89', 'H', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.pdf'),
]

def main():
    v2 = json.load(open(V2, encoding='utf-8'))
    for sh, code, pdfname in TEN:
        ent = v2[code]
        pdf = os.path.join(PDFDIR, pdfname)
        page = ent['info_page']
        rx = re.compile(ent['anchor']['regex'])
        n_all, lines = ex.body_blocks(pdf, page)
        hit = None
        for i, ln in enumerate(lines):
            for seg in ln['text'].split('\n'):
                seg = ex.nospc(seg)
                if rx.match(seg):
                    hit = (i, ln['bbox'][1], seg[:44])
                    break
            if hit:
                break
        print('== %s (v2:%s %s) → %s' % (sh, code, ent['anchor']['family'],
              ('命中 行%d y=%.0f: %s' % hit) if hit else '未命中'))
        for i, ln in enumerate(lines[:12]):
            flat = [ex.nospc(s)[:52] for s in ln['text'].split('\n')]
            print('   行%-2d y=%-6.1f %s' % (i, ln['bbox'][1], ' ⏎ '.join(flat)[:100]))

if __name__ == '__main__':
    main()
