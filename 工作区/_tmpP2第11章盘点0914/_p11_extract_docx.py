# -*- coding: utf-8 -*-
r"""_p11_extract_docx.py — P2 第11章 轮1 查重分拣：docx 侧题面提取＋归一化落盘（口径承 P2 _p2_extract.py；轮0 PDF 提取件 _p11_extract.py 不动）

产出（全部写入本目录）：
  _p11池.json     —— 三卷30（简15/中13/冲2，按【答案】过滤）＋ 实验卷14 ＋ 讲和练61（全量真题）
                    ＋ 落选31名单（对账§五三组）＋ 保留映射（对账§三）
                    每题字段 vol/no/id/stem/norm/cjk/head/fig/diff/kp
  _p11映射核.md   —— 三卷30 × 讲和练61 最佳配对（验证对账保留映射 1.000 同文）＋ 实验卷14 × 三卷30（验证复制件）
  _p11微专题.json —— 107微专题 59~72 讲全块（真题/讲料标记＋归一化）
  _p11微专题题面.txt —— 微专题全块题面（按讲分节，供人工通读）
"""
import sys, os, re, json
WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(WS, '..', '..', '工具'))
from dump_docx import body_elements

SYNC = os.path.join(WS, '..', '..', '高中物理', '高中物理同步')
ZXW = os.path.join(WS, '..', '..', '高中物理', '参考', '组卷网',
                   '知识图鉴·单元讲练测（2019人教版）', '人教版必修第3册')
WZT = os.path.join(WS, '..', '..', '高中物理', '参考', '组卷网',
                   '备战高考·107微专题模型精讲精练', '9恒定电流')

VOL_FILES = {
    '简': os.path.join(SYNC, '人教版必修3 第11章 电路及其应用·简单卷（15题）.docx'),
    '中': os.path.join(SYNC, '人教版必修3 第11章 电路及其应用·中档卷（13题）.docx'),
    '冲': os.path.join(SYNC, '人教版必修3 第11章 电路及其应用·冲刺卷（2题）.docx'),
    '实': os.path.join(SYNC, '人教版必修3 第11章 电路及其应用·实验卷（14题3条）.docx'),
    '源': os.path.join(ZXW, '第11章电路及其应用讲和练.docx'),
}
WZT_FILES = {
    59: '第59讲求电流三公式的理解及应用-2023届高三物理高考复习101微专题模型精讲精练.docx',
    60: '第60讲欧姆定律与电阻定律-2023届高三物理高考复习101微专题模型精讲精练.docx',
    61: '第61讲纯电阻电路和非纯电阻电路中的电功与电热-2023届高三物理高考复习101微专题模型精讲精练.docx',
    62: '第62讲电路的动态分析-2023届高三物理高考复习101微专题模型精讲精练.docx',
    63: '第63讲含电容器电路的动态分析-2023届高三物理高考复习101微专题模型精讲精练.docx',
    64: '第64讲电阻及电源UI图像的分析与计算-2023届高三物理高考复习101微专题模型精讲精练.docx',
    65: '第65讲电路故障分析-2023届高三物理高考复习101微专题模型精讲精练.docx',
    66: '第66讲电表的改装-2023届高三物理高考复习101微专题模型精讲精练.docx',
    67: '第67讲欧姆表的原理与多用电表的使用-2023届高三物理高考复习101微专题模型精讲精练.docx',
    68: '第68讲电流表内外接的选择方法及解决电表分压或分流引起的系统误差问题-2023届高三物理高考复习1.docx',
    69: '第69讲半偏法测电阻的原理及其思维方法的迁移-2023届高三物理高考复习101微专题模型精讲精练.docx',
    70: '第70讲替代法和电桥法测量电阻-2023届高三物理高考复习101微专题模型精讲精练.docx',
    71: '第71讲电路设计之两种控制电路与六种测量电路以及器材选择原则-2023届高三物理高考复习101微专.docx',
    72: '第72讲测量电源的电动势和内阻实验设计与误差分析-2023届高三物理高考复习101微专题模型精讲精.docx',
}
# 对账§三 三卷保留（源题号）／§五 落选31（超纲16＋高度重复6＋组合内让位9）
KEEP = {
    '简': [1, 8, 9, 10, 12, 14, 18, 22, 23, 28, 36, 41, 44, 46, 58],
    '中': [7, 11, 16, 17, 24, 25, 29, 30, 32, 34, 37, 40, 57],
    '冲': [60, 61],
}
LOST = sorted([26, 38, 42, 43, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 59]
              + [2, 3, 4, 6, 21, 33]
              + [5, 13, 15, 19, 20, 27, 31, 35, 39])

ZW = dict.fromkeys(map(ord, '\u2060\ufeff\u200b\u200c\u200d\u00ad'), None)
OMML_MAP = [
    (r'⟦|⟧', ''),
    (r'_\(([^()]*)\)', r'_\1'), (r'\^\(([^()]*)\)', r'^\1'),
    (r'root\[[^\]]*\]\(([^()]*)\)', r'root(\1)'),
    (r'√\(([^()]*)\)', r'root(\1)'),
    (r'‖', ''),
    (r'−', '-'), (r'⋅', '·'), (r'//', '∥'),
]
PUNCT = '，。；：、！？“”‘’\'",.!?—－-…·・_/／|｜*^$@+=~`’'


def canon(t):
    for pat, rep in OMML_MAP:
        t = re.sub(pat, rep, t)
    t = re.sub(r'\\[A-Za-z]+', '', t)
    t = t.replace('【图】', '').replace('⏎', ' ')
    t = re.sub(r'\d+(?:\.\d+)?%?', '#', t)
    t = re.sub(r'[零一二两三四五六七八九十百千万]+', '#', t)
    t = re.sub(r'\s+', '', t)
    t = ''.join(c for c in t if c not in PUNCT)
    return t.lower()


def cjk_only(t):
    return ''.join(c for c in t if '一' <= c <= '鿿' or c in '#')


QSTART = re.compile(r'^(\d{1,3})．')


def extract(fname, need_ans=True):
    els = body_elements(VOL_FILES[fname])
    lines = [(i, t) for i, tg, t in els if tg == 'p' and t is not None]
    starts = [k for k, (i, t) in enumerate(lines)
              if len(t.strip()) >= 8 and QSTART.match(t.strip())]
    out = []
    for k_i, k in enumerate(starts):
        no = int(QSTART.match(lines[k][1].strip()).group(1))
        end = starts[k_i + 1] if k_i + 1 < len(starts) else len(lines)
        block = '\n'.join(t for i, t in lines[k:end] if t.strip()).translate(ZW)
        if need_ans and '【答案】' not in block:
            continue
        stem = block.split('【答案】')[0].split('【解析】')[0].strip()
        m = re.search(r'【难度】\s*([-\d.]+)', block)
        diff = m.group(1) if m else ''
        m = re.search(r'【知识点】\s*([^\n【]+)', block)
        kp = m.group(1).strip() if m else ''
        n = canon(stem)
        out.append({'vol': fname, 'no': no,
                    'id': ('Q%d' % no) if fname == '源' else '%s%d' % (fname, no),
                    'stem': stem, 'norm': n, 'cjk': cjk_only(n),
                    'head': re.sub(r'\s+', '', stem)[:60].replace('|', '／'),
                    'fig': stem.count('【图】'), 'diff': diff, 'kp': kp})
    return out


def extract_wzt(lecture):
    """微专题：N．块全收；【答案】/【解析】有＝真题，无＝讲料。返回块列表。"""
    path = os.path.join(WZT, WZT_FILES[lecture])
    els = body_elements(path)
    lines = [(i, t) for i, tg, t in els if tg == 'p' and t is not None]
    starts = [k for k, (i, t) in enumerate(lines)
              if t.strip() and QSTART.match(t.strip())]
    out = []
    for k_i, k in enumerate(starts):
        no = int(QSTART.match(lines[k][1].strip()).group(1))
        end = starts[k_i + 1] if k_i + 1 < len(starts) else len(lines)
        block = '\n'.join(t for i, t in lines[k:end] if t.strip()).translate(ZW)
        is_ti = '【答案】' in block or '【解析】' in block
        stem = block.split('【答案】')[0].split('【解析】')[0].strip()
        n = canon(stem)
        out.append({'lecture': lecture, 'block': len(out) + 1, 'no': no,
                    'id': '讲%d-%d' % (lecture, len(out) + 1),
                    'is_ti': is_ti, 'stem': stem, 'norm': n, 'cjk': cjk_only(n),
                    'head': re.sub(r'\s+', '', stem)[:60].replace('|', '／'),
                    'fig': block.count('【图】')})
    return out


def ratio(a, b):
    if not a or not b:
        return 0.0
    if len(a) > len(b) * 2 or len(b) > len(a) * 2:
        return 0.0
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


def conf(a, b):
    if not a or not b:
        return 0.0
    from difflib import SequenceMatcher
    sm = SequenceMatcher(None, a, b)
    m = sum(bl.size for bl in sm.get_matching_blocks())
    return m / min(len(a), len(b))


def best_match(q, refs):
    best = max(refs, key=lambda s: (max(ratio(q['norm'], s['norm']),
                                        ratio(q['cjk'], s['cjk'])),
                                    conf(q['norm'], s['norm'])))
    r = max(ratio(q['norm'], best['norm']), ratio(q['cjk'], best['cjk']))
    c = conf(q['norm'], best['norm'])
    return best, r, c


def main():
    pool, exp = [], []
    for v in ('简', '中', '冲'):
        qs = extract(v)
        nums = [q['no'] for q in qs]
        assert nums == list(range(1, len(qs) + 1)), (v, nums)
        print('%s卷 真题=%d 题号连续1..%d ✓' % (v, len(qs), len(qs)))
        pool += qs
    exp = extract('实')
    nums = [q['no'] for q in exp]
    assert nums == list(range(1, len(exp) + 1)), ('实', nums)
    print('实验卷 真题=%d 题号连续1..%d ✓' % (len(exp), len(exp)))
    assert len(pool) == 30, len(pool)

    src = extract('源')
    nums = [q['no'] for q in src]
    assert nums == list(range(1, 62)), nums
    print('讲和练 真题=%d 题号连续1..61 ✓' % len(src))
    assert sorted(KEEP['简'] + KEEP['中'] + KEEP['冲'] + LOST) == list(range(1, 62))

    json.dump({'pool30': pool, 'exp14': exp, 'src61': src,
               'lost': LOST, 'keep': KEEP},
              open(os.path.join(WS, '_p11池.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)

    # ---- 三卷30 × 讲和练61：验证对账保留映射 ----
    rows = []
    for p in pool:
        best, r, c = best_match(p, src)
        rows.append((p['id'], p['no'], best['no'], r, c))
    ok, bad = 0, []
    for pid, pno, sno, r, c in rows:
        vol = pid[0]
        if sno == KEEP[vol][pno - 1] and r > 0.98:
            ok += 1
        else:
            bad.append((pid, sno, round(r, 3), KEEP[vol][pno - 1]))
    print('三卷30→讲和练映射：与对账一致且≥0.98 同文 = %d/30；异常=%s' % (ok, bad or '无'))

    # ---- 实验卷14 × 三卷30：验证复制件（对账：简Q8/9/11/12/13/14/15、中Q5/6/11/12/13、冲Q1/2）----
    EXP_EXPECT = ['简8', '简9', '简11', '简12', '简13', '简14', '简15',
                  '中5', '中6', '中11', '中12', '中13', '冲1', '冲2']
    rows2 = []
    for e in exp:
        best, r, c = best_match(e, pool)
        rows2.append((e['id'], best['id'], r, c))
    ok2 = sum(1 for (eid, bid, r, c) in rows2
              if bid == EXP_EXPECT[int(eid[1:]) - 1] and r > 0.95)
    print('实验卷14→三卷30：与对账底包清单一致且≥0.95 = %d/14' % ok2)

    with open(os.path.join(WS, '_p11映射核.md'), 'w', encoding='utf-8') as f:
        f.write('# 三卷30 → 讲和练61 配对核（验证对账§三保留映射）＋ 实验卷14 → 三卷30 配对核\n\n')
        f.write('| 卷题 | 源Q | 判 | conf | 对账保留题号 | 一致 |\n|---|---|---|---|---|---|\n')
        for pid, pno, sno, r, c in rows:
            vol = pid[0]
            exp_no = KEEP[vol][pno - 1]
            f.write('| %s | Q%d | %.3f | %.3f | Q%d | %s |\n' % (
                pid, sno, r, c, exp_no, '✓' if sno == exp_no else '**✗**'))
        f.write('\n| 实验卷题 | 三卷出处 | 判 | conf | 对账底包清单 | 一致 |\n|---|---|---|---|---|---|\n')
        for (eid, bid, r, c) in rows2:
            exp_id = EXP_EXPECT[int(eid[1:]) - 1]
            f.write('| %s | %s | %.3f | %.3f | %s | %s |\n' % (
                eid, bid, r, c, exp_id, '✓' if bid == exp_id else '**✗**'))
    print('映射核 -> _p11映射核.md')

    # ---- 微专题 59~72 ----
    allblocks = []
    for lec in sorted(WZT_FILES):
        bs = extract_wzt(lec)
        allblocks += bs
        nti = sum(1 for b in bs if b['is_ti'])
        print('讲%d 块=%d（真题=%d 讲料=%d）' % (lec, len(bs), nti, len(bs) - nti))
    json.dump(allblocks, open(os.path.join(WS, '_p11微专题.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    ti_total = sum(1 for b in allblocks if b['is_ti'])
    print('微专题 59~72 块合计=%d（轮0口径190） 真题=%d 讲料=%d' % (
        len(allblocks), ti_total, len(allblocks) - ti_total))

    with open(os.path.join(WS, '_p11微专题题面.txt'), 'w', encoding='utf-8') as f:
        cur = None
        for b in allblocks:
            if b['lecture'] != cur:
                cur = b['lecture']
                f.write('\n========== 第%d讲 ==========\n' % cur)
            f.write('\n[%s|%s]\n%s\n' % (b['id'], '真题' if b['is_ti'] else '讲料', b['stem']))
    print('题面通读件 -> _p11微专题题面.txt')


if __name__ == '__main__':
    main()
