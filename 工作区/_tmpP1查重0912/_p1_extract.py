# -*- coding: utf-8 -*-
r"""_p1_extract.py — P1 轮1 查重分拣：docx 侧题面提取＋归一化落盘

产出：
  _p1池.json   —— 池41（三卷真题，按【答案】标签过滤）＋ 讲和练66（全量真题）
                  每题字段 id/vol/no/stem/norm/cjk/head/fig/diff/kp
  _p1映射.md   —— 池41×讲和练66 最佳配对表（验证保留41↔源题号映射＋实证落选25集合）

归一口径承 M2 `_tmp查重.py`：OMML 线性化→符号归一→数字→#→剥标点空白；双通道（全文骨架 norm／纯中文骨架 cjk）。
"""
import sys, os, re, json
sys.path.insert(0, os.path.join('..', '..', '工具'))
from dump_docx import body_elements

WS = os.path.dirname(os.path.abspath(__file__))
SYNC = os.path.join('..', '..', '高中物理', '高中物理同步')
ZXW = os.path.join('..', '..', '高中物理', '参考', '组卷网',
                   '知识图鉴·单元讲练测（2019人教版）', '人教版必修第3册')

VOL_FILES = {
    '简': os.path.join(SYNC, '人教版必修3 第9章 静电场及其应用·简单卷（10题）.docx'),
    '中': os.path.join(SYNC, '人教版必修3 第9章 静电场及其应用·中档卷（27题）.docx'),
    '冲': os.path.join(SYNC, '人教版必修3 第9章 静电场及其应用·冲刺卷（4题）.docx'),
    '源': os.path.join(ZXW, '第9章静电场及其应用讲和练.docx'),
}

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
    """块启发式＝行首 N． 且长≥8；真题＝块内含【答案】。返回按源题号排序的真题列表。"""
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
            continue  # 讲要点块／栏目标记块，按对账先例用【答案】标签过滤
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


def main():
    pool41, src66 = [], []
    for v in ('简', '中', '冲'):
        qs = extract(v)
        nums = [q['no'] for q in qs]
        assert nums == list(range(1, len(qs) + 1)), (v, nums)
        print('%s卷 真题=%d 题号连续1..%d ✓' % (v, len(qs), len(qs)))
        pool41 += qs
    src = extract('源')
    nums = [q['no'] for q in src]
    assert nums == list(range(1, 67)), nums
    print('讲和练 真题=%d 题号连续1..66 ✓' % len(src))
    src66 = src
    assert len(pool41) == 41, len(pool41)

    json.dump({'pool41': pool41, 'src66': src66},
              open(os.path.join(WS, '_p1池.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)

    # ---- 池41 × 源66 最佳配对（含包含度通道）----
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

    rows = []
    taken = {}
    for p in pool41:
        best = max(src66, key=lambda s: (max(ratio(p['norm'], s['norm']),
                                             ratio(p['cjk'], s['cjk'])),
                                         conf(p['norm'], s['norm'])))
        r = max(ratio(p['norm'], best['norm']), ratio(p['cjk'], best['cjk']))
        c = conf(p['norm'], best['norm'])
        rows.append((p['id'], best['no'], r, c, p['head'][:30], best['head'][:30]))
        taken.setdefault(best['no'], []).append(p['id'])
    rows.sort(key=lambda x: int(x[0][1:]))
    with open(os.path.join(WS, '_p1映射.md'), 'w', encoding='utf-8') as f:
        f.write('# 池41 → 讲和练66 最佳配对（验证保留映射；判＝双通道ratio最大值，conf＝短侧包含度）\n\n')
        f.write('| 池题 | 源Q | 判 | conf | 池首句 | 源首句 |\n|---|---|---|---|---|---|\n')
        for rid, q, r, c, h1, h2 in rows:
            f.write('| %s | Q%d | %.3f | %.3f | %s | %s |\n' % (rid, q, r, c, h1, h2))
        missing = [q for q in range(1, 67) if q not in taken]
        f.write('\n未配对源题（应＝对账落选25）：%s 共%d\n' % (
            '、'.join('Q%d' % q for q in missing), len(missing)))
        f.write('一对多配对：%s\n' % ('、'.join('Q%d←%s' % (k, '/'.join(v))
                                                for k, v in sorted(taken.items()) if len(v) > 1) or '无'))
    print('映射表 -> _p1映射.md；未配对源题数 =', len([q for q in range(1, 67) if q not in taken]))


if __name__ == '__main__':
    main()
