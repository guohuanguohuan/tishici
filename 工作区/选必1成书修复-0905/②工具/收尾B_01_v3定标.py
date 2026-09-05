# -*- coding: utf-8 -*-
"""收尾B_01_v3定标.py — 2026-09-06 收尾-B（锚点v3定标）步1。
对 成书交付/全件PDF 十件终态 PDF 逐件提取第1页文本块（复用 工具/首页断言集执行器.py 的
body_blocks 几何口径），登记各件首页实际形态（头部＋清单表＋首块落位），探测 WJ(U+2060)/
数学斜体字形/拆行三类终态伪影，导出 v3 锚点候选（稳定前缀＋容错），输出 中间证据 JSON。
只读 PDF，零 COM，零写入规则件。"""
import sys, io, os, re, json, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '工具'))
import 首页断言集执行器 as ex
import pymupdf

PDFDIR = os.path.abspath(os.path.join(HERE, '..', '成书交付', '全件PDF'))
V2 = os.path.join(ROOT, '工作区', '同步-数学选必1复合修复-0903', '子步3', '锚点映射表v2.json')
OUTJ = os.path.join(HERE, '报告', '收尾B_定标证据.json')

# 报告代号 → 全件PDF文件名（与 ②E_07_断言批.py TEN 清单一致；件名取 v2 file 去 .docx）
TEN = [
    ('清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）'),
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）'),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）'),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）'),
    ('清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）'),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）'),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）'),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）'),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）'),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）'),
]
CODE2V2 = {'清单1': 'I1', '衔接1': 'X1', '上61': 'B', '下79': 'C', '清单2': 'I2',
           '衔接2': 'X2', '92': 'E', '90': 'F', '68': 'G', '89': 'H'}

def glyph_class(ch):
    return 'math' if 0x1D400 <= ord(ch) <= 0x1D7FF else ('wj' if ch in '\u2060\u200b\ufeff' else 'plain')

def italic_to_ascii(ch):
    """数学字母字形（U+1D400–U+1D7FF）→ASCII 等价（粗斜体/斜体/无衬线族并入基字母）。"""
    o = ord(ch)
    if not (0x1D400 <= o <= 0x1D7FF):
        return ch
    # 各族基偏移：bold=0x1D400/52 italic=0x1D434/52 bold-italic=0x1D468/52 script…
    for base, n in ((0x1D400, 52), (0x1D434, 52), (0x1D468, 52), (0x1D49C, 52), (0x1D4D0, 52),
                    (0x1D504, 52), (0x1D538, 52), (0x1D56C, 52), (0x1D5A0, 52), (0x1D5D4, 52),
                    (0x1D608, 52), (0x1D63C, 52), (0x1D670, 10), (0x1D6A8, 52), (0x1D6E2, 52),
                    (0x1D71C, 52), (0x1D756, 52), (0x1D790, 52), (0x1D7CA, 52)):
        if base <= o < base + n:
            idx = o - base
            if idx < 26:
                return chr(ord('A') + idx)
            if idx < 52:
                return chr(ord('a') + idx - 26)
    return ch

def norm_v3(s):
    """v3 归一化：去全部空白＋U+2060/零宽符＋数学字形转 ASCII＋全角点/连字归一。"""
    s = ''.join(italic_to_ascii(c) for c in s)
    s = re.sub(r'[\s\u2060\u200b\ufeff\u00ad]+', '', s)
    return s

def main():
    v2 = json.load(open(V2, encoding='utf-8'))
    ev = {}
    for sh, stem_name in TEN:
        pdf = os.path.join(PDFDIR, stem_name + '.pdf')
        ent = v2[CODE2V2[sh]]
        page = ent['info_page']
        doc = pymupdf.open(pdf)
        pg = doc[0]
        raw = pg.get_text()
        doc.close()
        n_all, lines = ex.body_blocks(pdf, page)
        # 伪影普查
        wj_n = raw.count('\u2060') + raw.count('\u200b') + raw.count('\ufeff')
        math_chars = sorted({c for c in raw if 0x1D400 <= ord(c) <= 0x1D7FF})
        # 头部要素形态（前6个正文区行）
        head = []
        for ln in lines[:6]:
            t = ln['text'].replace('\n', '⏎')
            head.append({'y': round(ln['bbox'][1], 1), 'text': t[:80],
                         'raw': repr(t[:80])})
        # 首块（正文区第一行）及其族判
        first = lines[0]['text'] if lines else ''
        first_flat = norm_v3(first.split('\n')[0])
        m_tqh = re.match(r'^\d+(?:\.\d+){3,}-\d+．', first_flat)
        m_tmh = re.match(r'^\d+\.\d+(?:\.\d+)?-\d+．', first_flat)
        fam = ('题号块式' if m_tqh else '条目号式' if m_tmh else '其它')
        ev[sh] = {
            'pdf': os.path.basename(pdf), 'n_all': n_all, 'n_body': len(lines),
            'wj_count': wj_n, 'math_chars': ''.join(math_chars)[:60],
            'v2_anchor': ent['anchor']['regex'], 'v2_family': ent['anchor']['family'],
            'first_flat': first_flat[:70], 'first_family': fam, 'first_y': round(lines[0]['bbox'][1], 1) if lines else None,
            'head': head,
        }
        print('== %s == 块%d/正文行%d WJ=%d 数学字形=%s' % (sh, n_all, len(lines), wj_n, ''.join(math_chars)[:24] or '无'))
        print('  v2锚(%s): %s' % (ent['anchor']['family'], ent['anchor']['regex']))
        print('  首行[y=%.0f %s]: %s' % (ev[sh]['first_y'] or -1, fam, first_flat[:64]))
        print('  raw前3行: %s' % ' || '.join(h['raw'][:60] for h in head[:3]))
    json.dump(ev, open(OUTJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n证据落盘: %s' % OUTJ)

if __name__ == '__main__':
    main()
