# -*- coding: utf-8 -*-
r"""_tmp教材查重.py — 教材149题 × 我方池（外源可用77＋docx169＋样张82）机械初筛

仿 _tmp查重.py 归一口径（canon/cjk_only 复制自该件，不 import 以免拉入 docx 依赖）。
教材题面用 _tmp教材题面.json 的 body（已完成 犃→A 等字形还原），再 NFKC→canon。
阈值 0.55 出候选（比轮1的0.60放宽一档，宁滥勿缺）；判重必须逐对亲算（公共规则§5）。
双通道：①全文/中文 ratio≥0.55；②短题干包含度 conf≥0.95 且短侧 norm≥18 字
（教材分数排版残损如 ½→"12"，ratio 通道对 F2·10 类算题失明，conf 通道补召回——F2·10 实测 conf=1.00）。
另出教材 149×149 自撞（≥0.60），防同料多栏；V2《教材题源核查》点名 9 族强制入检（不受阈值）。
产出 _tmp教材查重-候选.md。
"""
import os, re, json, unicodedata
from difflib import SequenceMatcher


def conf(a, b):
    if not a or not b:
        return 0.0
    sm = SequenceMatcher(None, a, b, autojunk=False)
    return sum(bl.size for bl in sm.get_matching_blocks()) / min(len(a), len(b))


# V2《教材题源核查.md》§同型换数族 点名对：强制亲算，不受机械阈值
V2_PAIRS = [
    ('1.1.3练习A·3', ['F4·13']),
    ('1.1.3练习A·4', ['F4·13']),
    ('1.1.3练习B·8', ['讲上·1.1.3.6-8']),
    ('1.2.1练习A·1', ['F5·1']),
    ('1.2.2练习B·3', ['讲上·1.2.2.2-1', 'F5·2']),
    ('习题1—2"·2', ['讲上·1.2.2.2-1', 'F5·2']),
    ('习题1—2"·7', ['讲上·1.1.1.7-6', 'F2·21']),
    ('复习题犃组·2', ['讲上·1.1.1.8-7']),
    ('复习题犅组·2', ['F4·15']),
    ('复习题犆组·1', ['F2·14']),
]

WS = os.path.dirname(os.path.abspath(__file__))

# ---------- 归一（复制自 _tmp查重.py） ----------
OMML_MAP = [
    (r'⟦|⟧', ''),
    (r'_\(([^()]*)\)', r'_\1'), (r'\^\(([^()]*)\)', r'^\1'),
    (r'root\[[^\]]*\]\(([^()]*)\)', r'root(\1)'),
    (r'√\(([^()]*)\)', r'root(\1)'),
    (r'‖', ''),
    (r'−', '-'), (r'⋅', '·'), (r'//', '∥'),
]
PUNCT = '，。；：、！？“”‘’\'",.!?—－-…·・_/／|｜*^$@+=~`’'
ZW = dict.fromkeys(map(ord, '\u2060\ufeff\u200b\u200c\u200d\u00ad'), None)


def canon(t, is_tex=False):
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


def ratio(a, b):
    if not a or not b:
        return 0.0
    if len(a) > len(b) * 2 or len(b) > len(a) * 2:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


# ---------- 数据 ----------
def norm_book(body):
    t = unicodedata.normalize('NFKC', body.translate(ZW))
    return canon(t), cjk_only(canon(t))


def main():
    book = json.load(open(os.path.join(WS, '_tmp教材题面.json'), encoding='utf-8'))
    pool = json.load(open(os.path.join(WS, '_tmp查重-池.json'), encoding='utf-8'))
    keep = set(open(os.path.join(WS, '_tmp可用77id.txt'), encoding='utf-8').read().split())
    ext = [p for p in pool['ext'] if p['id'] in keep]
    missing = keep - {p['id'] for p in ext}
    assert not missing, '池内缺可用id: %s' % missing
    mine = ext + pool['old'] + pool['slice']
    print('教材=%d 池=%d（外源可用%d＋docx%d＋样张%d）' % (
        len(book), len(mine), len(ext), len(pool['old']), len(pool['slice'])))

    for b in book:
        b['norm'], b['cjk'] = norm_book(b['body'])

    pairs = []
    for b in book:
        for m in mine:
            r = ratio(b['norm'], m['norm'])
            r2 = ratio(b['cjk'], m['cjk'])
            best = max(r, r2)
            ch = 'ratio'
            if best < 0.55:
                c1 = conf(b['norm'], m['norm'])
                c2 = conf(b['cjk'], m['cjk'])
                cc = max(c1, c2)
                if cc >= 0.95 and min(len(b['norm']), len(m['norm'])) >= 18:
                    best, ch = cc, 'conf'
            if best >= 0.55:
                pairs.append((best, r, r2, b, m, ch))
    pairs.sort(key=lambda x: -x[0])
    print('跨池候选对=%d（conf通道=%d）' % (len(pairs), sum(1 for p in pairs if p[5] == 'conf')))

    self_pairs = []
    for i in range(len(book)):
        for j in range(i + 1, len(book)):
            a, b = book[i], book[j]
            r = ratio(a['norm'], b['norm'])
            r2 = ratio(a['cjk'], b['cjk'])
            best = max(r, r2)
            if best >= 0.60:
                self_pairs.append((best, r, r2, a, b))
    self_pairs.sort(key=lambda x: -x[0])
    print('教材自撞对=%d' % len(self_pairs))

    byid = {m['id']: m for m in mine}
    with open(os.path.join(WS, '_tmp教材查重-候选.md'), 'w', encoding='utf-8') as f:
        f.write('# 教材149 × 我方池 机械初筛候选（未判定，判重须亲算）\n\n')
        f.write('> 归一：教材body（字形还原后）NFKC→canon；池侧沿用轮1 norm/cjk。通道①全文/中文ratio双指标取大≥0.55；通道②包含度conf≥0.95且短侧≥18字（救分数残损算题）。自撞阈值0.60。\n\n')
        f.write('## 〇、V2点名强制亲算对（不受阈值）\n\n')
        for bid, mids in V2_PAIRS:
            b = next((t for t in book if t['id'] == bid), None)
            if b is None:
                f.write('!! 教材id未找到：%s\n\n' % bid)
                continue
            for mid in mids:
                m = byid.get(mid)
                if m is None:
                    f.write('!! 池id未找到：%s ↔ %s\n\n' % (bid, mid))
                    continue
                r = ratio(b['norm'], m['norm'])
                r2 = ratio(b['cjk'], m['cjk'])
                f.write('### V2 %s ↔ %s ｜ 全文r=%.3f 中文r2=%.3f conf=%.3f ｜ 池侧[%s] kp=%s\n\n' % (
                    bid, mid, r, r2, max(conf(b['norm'], m['norm']), conf(b['cjk'], m['cjk'])),
                    m['tag'], m.get('kp', '')[:30]))
                f.write('教材题面：\n\n%s\n\n池题面：\n\n%s\n\n---\n\n' % (
                    b['body'].strip(), m['stem'].strip()[:600]))
        f.write('## 一、跨池候选（教材×池）\n\n')
        for i, (bb, r, r2, b, m, ch) in enumerate(pairs, 1):
            f.write('### 候%d %.3f[%s] ｜ %s ↔ %s ｜ 全文r=%.3f 中文r2=%.3f ｜ 池侧[%s] kp=%s diff=%s\n\n' % (
                i, bb, ch, b['id'], m['id'], r, r2, m['tag'], m.get('kp', '')[:30], m.get('diff', '')))
            f.write('教材题面：\n\n%s\n\n池题面：\n\n%s\n\n---\n\n' % (
                b['body'].strip(), m['stem'].strip()[:600]))
        f.write('## 二、教材自撞（≥0.60）\n\n')
        for i, (bb, r, r2, a, b) in enumerate(self_pairs, 1):
            f.write('### 自%d %.3f ｜ %s ↔ %s ｜ 全文r=%.3f 中文r2=%.3f\n\n' % (i, bb, a['id'], b['id'], r, r2))
            f.write('甲：\n\n%s\n\n乙：\n\n%s\n\n---\n\n' % (a['body'].strip(), b['body'].strip()))
    print('-> _tmp教材查重-候选.md')

    # 复现 V2 举证：F2·10 ↔ 1.1.1练习A·2 必须在候选中
    hit = [p for p in pairs if p[3]['id'] == '1.1.1练习A·2' and p[4]['id'] == 'F2·10']
    print('F2·10↔1.1.1练习A·2 命中:', ['%.3f/%s' % (h[0], h[5]) for h in hit] or '未命中!!')
    # V2 点名对覆盖核对
    pset = {(p[3]['id'], p[4]['id']) for p in pairs}
    for bid, mids in V2_PAIRS:
        for mid in mids:
            if (bid, mid) not in pset:
                print('  V2对不在机械候选（仅靠〇节强制检）：%s↔%s' % (bid, mid))
    # 各教材题最高命中一览
    top = {}
    for bb, r, r2, b, m, ch in pairs:
        if b['id'] not in top:
            top[b['id']] = (bb, m['id'], ch)
    with open(os.path.join(WS, '_tmp教材查重-最高.txt'), 'w', encoding='utf-8') as f:
        for b in book:
            t = top.get(b['id'])
            f.write('%s\t%s\n' % (b['id'], ('%.3f[%s]↔%s' % (t[0], t[2], t[1])) if t else '—'))
    print('有候选教材题=%d / 149' % len(top))


if __name__ == '__main__':
    main()
