# -*- coding: utf-8 -*-
"""收尾B_02_v3构建复跑.py — 2026-09-06 收尾-B 步2：构建 锚点映射表v3.json 并逐件复核。
锚点源＝十件终态 PDF 第1页实际首块（条目号/题号块）稳定前缀；容错双形态：
  regex     紧凑式（^+re.escape 源串；配合执行器 v3 归一化：去空白＋WJ/零宽＋数学字形→ASCII）；
  regex_raw 逐字弹性间隔式（[\\s\\u2060\\u200b\\u200c\\u200d\\ufeff]*，原始提取文本上直匹配）。
复核项：①compact 命中且为首token块 ②raw 命中且为首token块 ③反向校验（黑名单全串/stem/头部要素）
④阴性对照 衔接2缺陷态.pdf 须 FAIL。只读 PDF；产物落 ②工具\\报告\\。"""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '工具'))
import 首页断言集执行器 as ex
import pymupdf

PDFDIR = os.path.abspath(os.path.join(HERE, '..', '成书交付', '全件PDF'))
V2 = os.path.join(ROOT, '工作区', '同步-数学选必1复合修复-0903', '子步3', '锚点映射表v2.json')
NEG = os.path.join(ROOT, '工作区', '体系-双栏首页与PDFCreator主路径-0903', '阴性对照证据', '衔接2缺陷态.pdf')
OUT_JSON = os.path.join(HERE, '报告', '锚点映射表v3.json')
OUT_MD = os.path.join(HERE, '报告', '收尾B_v3复跑证据.md')

# 报告代号 → (v2代号, 全件PDF文件名)
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

# v3 锚点源（稳定前缀；九件承 v2 前缀、衔接2 更正为首块条目号；止于数学字形前）
CUR = {
    '清单1': '1.1.1-1．〔基〕空间向量',
    '衔接1': '1.2.1-1．平行线分线段成比',
    '上61': '1.1.1-1．〔基〕空间向量',
    '下79': '1.2.5-1．〔基〕距离',
    '清单2': '2.1-1．〔基〕平面上的两点',
    '衔接2': '2.8-1．一元二次方程的判别式',
    '92': '2.1-1．〔基〕平面上的两点',
    '90': '2.3.4-1．〔基〕圆与圆位',
    '68': '2.6.1-1．〔基〕',
    '89': '2.8-1．〔基〕直线',
}

RE_TQH = ex.RE_TQH
RE_TMH = ex.RE_TMH
ELASTIC = r'[\s\u2060\u200b\u200c\u200d\ufeff]*'


def italic_to_ascii(ch):
    o = ord(ch)
    if not (0x1D400 <= o <= 0x1D7FF):
        return ch
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
    """v3 匹配归一化：数学字形→ASCII＋去空白＋去 WJ/零宽/软连字（与执行器同步实现）。"""
    s = ''.join(italic_to_ascii(c) for c in s)
    return re.sub(r'[\s\u2060\u200b\u200c\u200d\ufeff\u00ad]+', '', s)


def main():
    v2 = json.load(open(V2, encoding='utf-8'))
    v3, checks, all_ok = {}, {}, True
    for sh, code, pdfname in TEN:
        ent = v2[code]
        pdf = os.path.join(PDFDIR, pdfname)
        page = ent['info_page']
        src = CUR[sh]
        rx_c = re.compile('^' + re.escape(src))
        rx_r = re.compile('^' + ELASTIC.join(re.escape(c) for c in src))
        n_all, lines = ex.body_blocks(pdf, page)
        # 文档实际首token块（条目号/题号块）
        first_tok_i = None
        for i, ln in enumerate(lines):
            flat0 = norm_v3(ln['text'].split('\n')[0])
            if RE_TQH.match(flat0) or RE_TMH.match(flat0):
                first_tok_i = i
                flat_full = norm_v3(ln['text'])
                break
        ok_prefix = first_tok_i is not None and norm_v3(lines[first_tok_i]['text']).startswith(norm_v3(src))
        fam = '条目号式' if RE_TMH.match(norm_v3(src)) else ('题号块式' if RE_TQH.match(norm_v3(src)) else '?')
        # ① compact 命中（v3 归一化；段级＋块级拼行）
        hit_c = None
        for i, ln in enumerate(lines):
            segs = [norm_v3(s) for s in ln['text'].split('\n')] + [norm_v3(ln['text'])]
            for seg in segs:
                if rx_c.match(seg):
                    hit_c = (i, ln['bbox'][1], seg)
                    break
            if hit_c:
                break
        # ② raw 弹性正则命中（原始块文本，仅并块内换行）
        doc = pymupdf.open(pdf)
        raw_blocks = [b[4].replace('\n', '') for b in doc[0].get_text('blocks')]
        doc.close()
        hit_r = None
        for i, t in enumerate(raw_blocks):
            if rx_r.match(t):
                hit_r = (i, t[:40])
                break
        # ③ 反向校验：黑名单全串 / 文件名主干 / 头部要素形态
        blacklist = ent.get('blacklist') or []
        stem = ent['stem']
        rev = {'source_in_blacklist': src in blacklist,
               'rx_fullmatch_blacklist': [b for b in blacklist if rx_c.fullmatch(norm_v3(b))],
               'rx_match_stem': bool(rx_c.match(norm_v3(stem))),
               'hit_is_header': bool(hit_c and (ex.RE_STATS_ROW.match(hit_c[2]) or ex.RE_LEGEND.match(hit_c[2])))}
        rev_ok = not any([rev['source_in_blacklist'], rev['rx_fullmatch_blacklist'],
                          rev['rx_match_stem'], rev['hit_is_header']])
        # 伪影普查（p1 全文）
        doc = pymupdf.open(pdf)
        raw_all = doc[0].get_text()
        doc.close()
        wj_n = sum(raw_all.count(c) for c in '\u2060\u200b\u200c\u200d\ufeff')
        glyphs = ''.join(sorted({c for c in raw_all if 0x1D400 <= ord(c) <= 0x1D7FF}))
        ok = (first_tok_i is not None and ok_prefix and hit_c is not None and hit_c[0] == first_tok_i
              and hit_r is not None and rev_ok)
        all_ok = all_ok and ok
        checks[sh] = {'ok': ok, 'family': fam, 'first_tok_line': first_tok_i,
                      'prefix_ok': ok_prefix, 'compact_hit': hit_c and (hit_c[0], round(hit_c[1], 1), hit_c[2][:36]),
                      'raw_hit': hit_r and (hit_r[0], hit_r[1][:36]), 'rev': rev, 'rev_ok': rev_ok,
                      'wj_n': wj_n, 'glyphs': glyphs[:40], 'n_all': n_all, 'n_body': len(lines)}
        print('%-4s %s 首token行=%s 前缀合=%s compact命中=%s(y=%.0f 行%s, 首token行一致=%s) raw命中=%s 反向校验=%s → %s'
              % (sh, fam, first_tok_i, ok_prefix, hit_c is not None, hit_c[1] if hit_c else -1,
                 hit_c[0] if hit_c else '?', hit_c and hit_c[0] == first_tok_i,
                 hit_r is not None, '通过' if rev_ok else '违规%s' % rev, 'PASS' if ok else 'FAIL'))
        v3[sh] = {
            'v2code': code, 'file': pdfname, 'stem': stem,
            'anchor': {'family': fam, 'regex': '^' + re.escape(src), 'regex_raw': rx_r.pattern,
                       'source': src,
                       'note': ('承v2前缀' if sh != '衔接2' else 'v3更正自题号块式^2\\.8\\.1\\-1．：讲部条目2.8-1实落p1首块y≈113，题号块2.8.1-1在y≈582，按前置步0「锚点＝正文首块机读特征」更正（同子步1/3先例）')},
            'info_page': ent['info_page'], 'stats_row': ent.get('stats_row'),
            'legends': ent.get('legends') or [], 'stats_row_in_header': ent.get('stats_row_in_header', False),
            'legends_in_header': ent.get('legends_in_header') or [], 'navtbl': ent.get('navtbl'),
            'title': ent.get('title', ''), 'has_break': ent.get('has_break', True),
            'blacklist': blacklist,
            'v3_evidence': {'first_tok_line': first_tok_i, 'hit_y': round(hit_c[1], 1) if hit_c else None,
                            'hit_line': hit_c[0] if hit_c else None, 'prefix_ok': ok_prefix,
                            'raw_hit_block': hit_r[0] if hit_r else None, 'rev_ok': rev_ok,
                            'wj_p1': wj_n, 'math_glyphs_p1': glyphs, 'blocks_p1': n_all},
        }
    # ④ 阴性对照：v3 断言①对 衔接2缺陷态.pdf 须 FAIL（X2 正式口径＋十件加测）
    neg = {}
    c, det = ex.assert1(NEG, v3['衔接2']['info_page'], v3['衔接2']['anchor']['regex'], v3['衔接2']['stem'])
    neg['衔接2(正式)'] = {'结论': c, '细节': det, '期望': 'FAIL', 'ok': c == 'FAIL'}
    all_ok = all_ok and neg['衔接2(正式)']['ok']
    print('阴性对照(衔接2, 正式口径): %s — %s' % (c, det))
    for sh, code, pdfname in TEN:
        if sh == '衔接2':
            continue
        c2, det2 = ex.assert1(NEG, v3[sh]['info_page'], v3[sh]['anchor']['regex'], v3[sh]['stem'])
        neg[sh] = {'结论': c2, '细节': det2, 'ok': c2 == 'FAIL'}
        if c2 != 'FAIL':
            all_ok = False
            print('  !! 阴性对照加测 %s = %s（期望FAIL）' % (sh, c2))
    print('阴性对照加测十件: %s' % ('全FAIL（正确）' if all(n['ok'] for n in neg.values()) else '存在非FAIL'))
    json.dump(v3, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# 收尾B v3 复跑证据（2026-09-06，终态PDF＝成书交付/全件PDF 十件）', '',
          '| 代号 | 族 | v3锚源 | 首token行 | compact命中(行/y) | raw命中块 | 反向校验 | WJ | 数学字形 | 判定 |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for sh, code, pdfname in TEN:
        c3 = checks[sh]
        md.append('| %s | %s | %s | %s | %s/%s | %s | %s | %d | %s | %s |'
                  % (sh, c3['family'], CUR[sh], c3['first_tok_line'],
                     c3['compact_hit'][0], c3['compact_hit'][1], c3['raw_hit'][0] if c3['raw_hit'] else '—',
                     '通过' if c3['rev_ok'] else '违规', c3['wj_n'], c3['glyphs'][:12] or '无',
                     'PASS' if c3['ok'] else 'FAIL'))
    md += ['', '## 阴性对照（衔接2缺陷态.pdf，v3断言①）', '',
           '| 口径 | 结论 | 细节 | 期望 |', '|---|---|---|---|']
    for k, n in neg.items():
        md.append('| %s | %s | %s | FAIL |' % (k, n['结论'], n['细节'].replace('|', '｜')))
    md.append('')
    md.append('总判定：%s' % ('全部通过（10/10 命中且首块落位＋反向校验全过＋阴性对照 FAIL）' if all_ok else '存在FAIL——见上表'))
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    print('\nJSON=%s\n证据=%s\n总判定: %s' % (OUT_JSON, OUT_MD, 'PASS' if all_ok else 'FAIL'))
    sys.exit(0 if all_ok else 2)


if __name__ == '__main__':
    main()
