# -*- coding: utf-8 -*-
r"""_tmp查重.py — M2 轮1 外源132题 × 我方池（docx 169＋样张族 82）题面比对（机械初筛，非判定）

产出 _tmp查重-池.json（三池归一化题面）＋ _tmp查重-候选.md（候选题对，按相似度降序）。
判重（知识点+题型+解法相同且只换数）必须亲算，本件只出候选（公共规则§5）。
归一口径：OMML 线性化文本与 LaTeX 文本先各自符号归一（\frac/\sqrt/上下标/希腊/关系符→统一Unicode），
再数字→#、剥 LaTeX 命令与定界符、剥标点与空白、小写。
"""
import sys, os, re, json, itertools
sys.path.insert(0, os.path.join('..', '..', '工具'))
from dump_docx import body_elements, para_text
from docx import Document
from lxml import etree

WS = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join('..', '..', '高中数学', '参考', '组卷网',
                   '【新课标 新探索】大单元作业设计', '人教A版选择性必修1',
                   '第1章 空间向量与立体几何')
OLD = os.path.join('..', '..', '高中数学', '高中数学同步')
SLICES = os.path.join('..', '逻辑闸-样张族0911', 'slices')

EXT_FILES = {
    '2': ('2空间向量及其运算.docx', 'F2'),
    '3': ('3空间向量基本定理.docx', 'F3'),
    '4': ('4空间向量及其运算的坐标表示.docx', 'F4'),
    '5': ('5空间向量的应用.docx', 'F5'),
    '6': ('6空间向量与立体几何中的高考新题型.docx', 'F6'),
    '7': ('7单元综合测试-空间向量与立体几何.docx', 'F7'),
}

# ---------- 通用归一 ----------
SYM_MAP = [
    (r'\\overrightarrow\s*\{([^{}]*)\}', r'\1'),
    (r'\\vec\s*\{([^{}]*)\}', r'\1'),
    (r'\\widehat\s*\{([^{}]*)\}', r'\1'),
    (r'\\dot\s*\{([^{}]*)\}', r'\1'),
    (r'\\bm\s*\{([^{}]*)\}', r'\1'),
    (r'\\text\s*\{([^{}]*)\}', r'\1'),
    (r'\\mathrm\s*\{([^{}]*)\}', r'\1'),
    (r'\\mathbf\s*\{([^{}]*)\}', r'\1'),
    (r'\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}', r'(\1)/(\2)'),
    (r'\\dfrac\s*\{([^{}]*)\}\s*\{([^{}]*)\}', r'(\1)/(\2)'),
    (r'\\sqrt\s*\[[^\]]*\]\s*\{([^{}]*)\}', r'root(\1)'),
    (r'\\sqrt\s*\{([^{}]*)\}', r'root(\1)'),
    (r'\^\s*\{([^{}]*)\}', r'^\1'),
    (r'_\s*\{([^{}]*)\}', r'_\1'),
    (r'\^\s*\\circ', '°'),
    (r'\\circ', '°'),
    (r'\\perp', '⊥'), (r'\\parallel', '∥'), (r'//', '∥'),
    (r'\\cdot', '·'), (r'\\times', '×'), (r'\\div', '÷'),
    (r'\\angle', '∠'), (r'\\triangle', '△'), (r'\\pi', 'π'), (r'\\infty', '∞'),
    (r'\\lambda', 'λ'), (r'\\mu', 'μ'), (r'\\alpha', 'α'), (r'\\beta', 'β'),
    (r'\\theta', 'θ'), (r'\\varphi', 'φ'), (r'\\gamma', 'γ'), (r'\\Omega', 'Ω'),
    (r'\\neq|\\ne', '≠'), (r'\\leqslant|\\leq|\\le', '≤'), (r'\\geqslant|\\geq|\\ge', '≥'),
    (r'\\approx', '≈'), (r'\\in', '∈'), (r'\\notin', '∉'), (r'\\subset', '⊂'),
    (r'\\cos|\\sin|\\tan', lambda m: m.group(0)[1:]),
    (r'\\,|\\;|\\!|\\:|\\quad|\\qquad|\\left|\\right|\\middle', ''),
    (r'\\begin\{[^{}]*\}|\\end\{[^{}]*\}', ''), (r'\\\\', ''),
    (r'[\[\]\{\}()（）〈〉<>]', ''),
]
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


def strip_tex(t):
    t = t.replace('$$', '$').replace('\\(', ' ').replace('\\)', ' ').replace('\\[', ' ').replace('\\]', ' ')
    t = re.sub(r'\$([^$]*)\$', r' \1 ', t)
    return t


def canon(t, is_tex=False):
    if is_tex:
        t = strip_tex(t)
        for pat, rep in SYM_MAP:
            t = re.sub(pat, rep if isinstance(rep, str) else rep, t)
    else:
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


# ---------- 池 1：外源 132 ----------
def load_ext():
    pool = []
    for key, (fn, tag) in EXT_FILES.items():
        els = body_elements(os.path.join(SRC, fn))
        lines = [(i, t) for i, tg, t in els if tg == 'p' and t is not None]
        starts = [k for k, (i, t) in enumerate(lines)
                  if re.match(r'^\d{1,3}．', t.strip()) and len(t.strip()) >= 8]
        for k_i, k in enumerate(starts):
            no = re.match(r'^(\d{1,3})．', lines[k][1].strip()).group(1)
            end = starts[k_i + 1] if k_i + 1 < len(starts) else len(lines)
            block = '\n'.join(t for i, t in lines[k:end] if t.strip()).translate(ZW)
            stem = block.split('【答案】')[0]
            m = re.search(r'【难度】\s*([-\d.]+)', block)
            diff = m.group(1) if m else ''
            m = re.search(r'【知识点】\s*([^\n【]+)', block)
            kp = m.group(1).strip() if m else ''
            head = re.sub(r'\s+', '', stem)[:60].replace('|', '／')
            n = canon(stem)
            pool.append({'id': '%s·%s' % (tag, no), 'tag': tag, 'no': int(no),
                         'stem': stem, 'norm': n, 'cjk': cjk_only(n),
                         'diff': diff, 'kp': kp, 'head': head,
                         'fig': stem.count('【图】')})
    return pool


# ---------- 池 2：我方 docx 169 ----------
# 题块区间沿用 R2 结构提取中间件（_tmp结构-*.json，61/79/29＝169 实测口径）
STRUCT = {'讲上': '_tmp结构-讲上.json', '讲下': '_tmp结构-讲下.json', '衔接': '_tmp结构-衔接件.json'}


def load_old():
    pool = []
    for tag, fn in STRUCT.items():
        d = json.load(open(os.path.join(WS, fn), encoding='utf-8'))
        its = {i['el']: i for i in d['items']}
        for q in d['questions']:
            lines = [its[e]['text'] for e in range(q['start'], q['end'] + 1)
                     if e in its and its[e].get('text')]
            block = '\n'.join(lines).translate(ZW)
            stem = block.split('【答案】')[0]
            m = re.search(r'【知识点】\s*\n?\s*([^\n【]+)', block)
            kp = m.group(1).strip() if m else ''
            m = re.search(r'（(简单|中档|难|衔接必会)）', lines[0] if lines else '')
            diff = m.group(1) if m else q.get('diff', '')
            n = canon(stem)
            pool.append({'id': '%s·%s' % (tag, q['no']), 'tag': tag, 'no': q['no'],
                         'sec': q.get('sec', ''), 'stem': stem,
                         'norm': n, 'cjk': cjk_only(n),
                         'diff': diff, 'kp': kp,
                         'head': re.sub(r'\s+', '', stem)[:60].replace('|', '／'),
                         'fig': stem.count('【图】')})
    return pool


# ---------- 池 3：样张族 82（LaTeX 盲解片） ----------
def load_slices():
    pool = []
    for fn in sorted(os.listdir(SLICES)):
        if not fn.startswith('slice-') or not fn.endswith('.md'):
            continue
        txt = open(os.path.join(SLICES, fn), encoding='utf-8').read()
        parts = re.split(r'\n(?=### )', txt)
        for p in parts[1:]:
            m = re.match(r'### ([^\s（(]+)(（[^）]*）)?', p.strip())
            if not m:
                continue
            label = m.group(1)
            body = p[m.end():]
            body = re.split(r'\n## |^> ', body)[0]
            n = canon(body, is_tex=True)
            if len(n) < 8:
                continue
            pool.append({'id': '%s·%s' % (fn[:-3], label), 'tag': fn[:-3], 'no': label,
                         'stem': body.strip()[:400], 'norm': n, 'cjk': cjk_only(n),
                         'diff': '', 'kp': (m.group(2) or '').strip('（）'),
                         'head': re.sub(r'\s+', '', body)[:60].replace('|', '／'),
                         'fig': 0})
    return pool


def ratio(a, b):
    from difflib import SequenceMatcher
    if not a or not b:
        return 0.0
    if len(a) > len(b) * 2 or len(b) > len(a) * 2:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def main():
    ext, old, sl = load_ext(), load_old(), load_slices()
    json.dump({'ext': ext, 'old': old, 'slice': sl},
              open(os.path.join(WS, '_tmp查重-池.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    print('池：外源=%d docx=%d 样张=%d' % (len(ext), len(old), len(sl)))

    mine = old + sl
    pairs = []
    for e in ext:
        for m in mine:
            r = ratio(e['norm'], m['norm'])
            r2 = ratio(e['cjk'], m['cjk'])
            best = max(r, r2)
            if best >= 0.60:
                pairs.append((best, r, r2, e, m))
    pairs.sort(key=lambda x: -x[0])
    with open(os.path.join(WS, '_tmp查重-候选.md'), 'w', encoding='utf-8') as f:
        f.write('# 外源132 × 我方池 候选题对（机械初筛，未判定）\n\n')
        f.write('> 归一化：OMML/LaTeX 符号归一→数字→#→剥标点空白。双指标取大：全文骨架 r ／ 纯中文骨架 r2。')
        f.write('阈值 0.60 只出候选；判重须亲算（公共规则§5）。\n\n')
        f.write('| # | 判 | 外源题 | 外源知识点 | 外源难度标 | ↔ | 我方题 | 我方知识点 | 全文r | 中文r2 | 外源首句 | 我方首句 |\n')
        f.write('|---|---|---|---|---|---|---|---|---|---|---|---|\n')
        for i, (b, r, r2, e, m) in enumerate(pairs, 1):
            f.write('| %d | %.2f | %s | %s | %s | ↔ | %s | %s | %.3f | %.3f | %s | %s |\n' % (
                i, b, e['id'], e['kp'][:24], e['diff'], m['id'], m['kp'][:24],
                r, r2, e['head'][:34], m['head'][:34]))
    print('候选对=%d -> _tmp查重-候选.md' % len(pairs))


if __name__ == '__main__':
    main()
