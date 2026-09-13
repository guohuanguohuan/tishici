# -*- coding: utf-8 -*-
r"""_p2_extract.py — P2 第10章 轮1 查重分拣：docx 侧题面提取＋归一化落盘（口径承 P1 _p1_extract.py）

产出（全部写入本目录）：
  _p2池.json     —— 三卷59（按【答案】过滤）＋ 讲和练70（全量真题）＋落选11名单
                    每题字段 id/vol/no/stem/norm/cjk/head/fig/diff/kp
  _p2映射.md     —— 三卷59 × 讲和练70 最佳配对（验证保留59映射＋实证落选11集合）
  _p2微专题.json —— 107微专题 50~58 讲全块（真题/讲料标记＋归一化）
  _p2微专题题面.txt —— 微专题全块题面（按讲分节，供人工时间线初筛通读）

归一口径承 M2/P1：OMML 线性化→符号归一→数字→#→剥标点空白；双通道（全文norm／纯中文cjk）。
"""
import sys, os, re, json
WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(WS, '..', '..', '工具'))
from dump_docx import body_elements

SYNC = os.path.join(WS, '..', '..', '高中物理', '高中物理同步')
ZXW = os.path.join(WS, '..', '..', '高中物理', '参考', '组卷网',
                   '知识图鉴·单元讲练测（2019人教版）', '人教版必修第3册')
WZT = os.path.join(WS, '..', '..', '高中物理', '参考', '组卷网',
                   '备战高考·107微专题模型精讲精练', '8静电场')

VOL_FILES = {
    '简': os.path.join(SYNC, '人教版必修3 第10章 静电场中的能量·简单卷（14题）.docx'),
    '中': os.path.join(SYNC, '人教版必修3 第10章 静电场中的能量·中档卷（33题）.docx'),
    '冲': os.path.join(SYNC, '人教版必修3 第10章 静电场中的能量·冲刺卷（12题）.docx'),
    '源': os.path.join(ZXW, '第10章静电场中的能量—讲和练.docx'),
}
WZT_FILES = {
    50: '第50讲电场中的图像-2023届高三物理高考复习101微专题模型精讲精练.docx',
    51: '第51讲匀强电场中的场强、电势、电势能的定性分析与定量计算-2023届高三物理高考复习101微专题.docx',
    52: '第52讲非匀强电场中的场强、电势、电势能的定性分析与定量计算-2023届高三物理高考复习101微专.docx',
    53: '第53讲单体或多体在电场中的运动之力、电综合问题-2023届高三物理高考复习101微专题模型精讲精.docx',
    54: '第54讲电容器的充电与放电实验-2023届高三物理高考复习101微专题模型精讲精练.docx',
    55: '第55讲电容器的动态分析-2023届高三物理高考复习101微专题模型精讲精练.docx',
    56: '第56讲带电粒子在电场中的直线运动-2023届高三物理高考复习101微专题模型精讲精练.docx',
    57: '第57讲带电粒子在电场中的曲线运动-2023届高三物理高考复习101微专题模型精讲精练.docx',
    58: '第58讲带电粒子在交变电场中的运动-2023届高三物理高考复习101微专题模型精讲精练.docx',
}
LOST = [6, 15, 19, 33, 37, 44, 48, 49, 53, 55, 67]  # 对账§三 删除11（Q59转投系第9章件不在70内）

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


def extract(fname):
    els = body_elements(VOL_FILES[fname])
    lines = [(i, t) for i, tg, t in els if tg == 'p' and t is not None]
    starts = [k for k, (i, t) in enumerate(lines)
              if len(t.strip()) >= 8 and QSTART.match(t.strip())]
    out = []
    for k_i, k in enumerate(starts):
        no = int(QSTART.match(lines[k][1].strip()).group(1))
        end = starts[k_i + 1] if k_i + 1 < len(starts) else len(lines)
        block = '\n'.join(t for i, t in lines[k:end] if t.strip()).translate(ZW)
        if '【答案】' not in block:
            continue
        stem = block.split('【答案】')[0].strip()
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
    """微专题：N．块全收；【答案】有＝真题，无＝讲料。返回块列表。"""
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


def main():
    pool, src = [], []
    for v in ('简', '中', '冲'):
        qs = extract(v)
        nums = [q['no'] for q in qs]
        assert nums == list(range(1, len(qs) + 1)), (v, nums)
        print('%s卷 真题=%d 题号连续1..%d ✓' % (v, len(qs), len(qs)))
        pool += qs
    src = extract('源')
    nums = [q['no'] for q in src]
    assert nums == list(range(1, 71)), nums
    print('讲和练 真题=%d 题号连续1..70 ✓' % len(src))
    assert len(pool) == 59, len(pool)

    json.dump({'pool59': pool, 'src70': src, 'lost': LOST},
              open(os.path.join(WS, '_p2池.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)

    # ---- 池59 × 源70 最佳配对 ----
    from difflib import SequenceMatcher

    def ratio(a, b):
        if not a or not b:
            return 0.0
        if len(a) > len(b) * 2 or len(b) > len(a) * 2:
            return 0.0
        return SequenceMatcher(None, a, b).ratio()

    def conf(a, b):
        if not a or not b:
            return 0.0
        sm = SequenceMatcher(None, a, b)
        m = sum(bl.size for bl in sm.get_matching_blocks())
        return m / min(len(a), len(b))

    rows, taken = [], {}
    for p in pool:
        best = max(src, key=lambda s: (max(ratio(p['norm'], s['norm']),
                                           ratio(p['cjk'], s['cjk'])),
                                       conf(p['norm'], s['norm'])))
        r = max(ratio(p['norm'], best['norm']), ratio(p['cjk'], best['cjk']))
        c = conf(p['norm'], best['norm'])
        rows.append((p['id'], best['no'], r, c, p['head'][:30], best['head'][:30]))
        taken.setdefault(best['no'], []).append(p['id'])
    rows.sort(key=lambda x: x[0])
    with open(os.path.join(WS, '_p2映射.md'), 'w', encoding='utf-8') as f:
        f.write('# 三卷59 → 讲和练70 最佳配对（验证保留59映射；判＝双通道ratio最大值，conf＝短侧包含度）\n\n')
        f.write('| 池题 | 源Q | 判 | conf | 池首句 | 源首句 |\n|---|---|---|---|---|---|\n')
        for rid, q, r, c, h1, h2 in rows:
            f.write('| %s | Q%d | %.3f | %.3f | %s | %s |\n' % (rid, q, r, c, h1, h2))
        unpaired = [q for q in range(1, 71) if q not in taken]
        f.write('\n未配对源题（应＝落选11）：%s 共%d\n' % (
            '、'.join('Q%d' % q for q in unpaired), len(unpaired)))
        f.write('一对多配对：%s\n' % ('、'.join('Q%d←%s' % (k, '/'.join(v))
                                                for k, v in sorted(taken.items()) if len(v) > 1) or '无'))
    print('映射表 -> _p2映射.md；未配对=%d 最低配对判=%.3f' % (
        len([q for q in range(1, 71) if q not in taken]), min(r[2] for r in rows)))

    # ---- 微专题 50~58 ----
    allblocks = []
    for lec in sorted(WZT_FILES):
        bs = extract_wzt(lec)
        allblocks += bs
        nti = sum(1 for b in bs if b['is_ti'])
        print('讲%d 块=%d（真题=%d 讲料=%d）' % (lec, len(bs), nti, len(bs) - nti))
    json.dump(allblocks, open(os.path.join(WS, '_p2微专题.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    ti_total = sum(1 for b in allblocks if b['is_ti'])
    print('微专题 50~58 块合计=%d 真题=%d 讲料=%d' % (len(allblocks), ti_total, len(allblocks) - ti_total))

    with open(os.path.join(WS, '_p2微专题题面.txt'), 'w', encoding='utf-8') as f:
        cur = None
        for b in allblocks:
            if b['lecture'] != cur:
                cur = b['lecture']
                f.write('\n========== 第%d讲 ==========\n' % cur)
            f.write('\n[%s|%s]\n%s\n' % (b['id'], '真题' if b['is_ti'] else '讲料', b['stem']))
    print('题面通读件 -> _p2微专题题面.txt')


if __name__ == '__main__':
    main()
