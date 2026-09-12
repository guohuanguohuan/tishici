# 批5b 互斥扫描（题块级）：拓展册／测评卷 vs 同章其余件
# 口径：只取 \begin{document}~\end{document} 之间的正文；按 \tihao{N}／\ti{N}{ 切题块；
#       去注释、去命令名、只留 CJK 字符流；12/14 字滑窗求交集，命中段按「题块×题块」归并。
# 通用物理措辞白名单（非双印，人工核）：见 GEN 表——命中段若整体落在白名单内则标〔通用〕。
import re, os, sys

ROOT = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷"
FILES = {
    '拓展册':   r"拓展册\main.tex",
    '测评卷':   r"测评卷\main.tex",
    '练习9.1':  r"练习件\9.1电荷\main.tex",
    '练习9.2':  r"练习件\9.2库仑定律\main.tex",
    '练习9.3':  r"练习件\9.3电场电场强度\main.tex",
    '练习9.4':  r"练习件\9.4静电的防止与利用\main.tex",
    '导学9.1':  r"导学件\9.1电荷\main.tex",
    '导学9.2':  r"导学件\9.2库仑定律\main.tex",
    '导学9.3':  r"导学件\9.3电场电场强度\main.tex",
    '导学9.4':  r"导学件\9.4静电的防止与利用\main.tex",
    '章末易错': r"章末-本章易错过关\main.tex",
    '学史切片': r"学史切片\第9章静电学史\main.tex",
}
GEN = ['下列说法正确的是', '下列说法中正确的是', '静电力常量为', '重力加速度为',
       '可视为点电荷', '如图所示']


def strip_comments(t):
    out = []
    for line in t.split('\n'):
        i, keep = 0, []
        while i < len(line):
            c = line[i]
            if c == '\\':
                keep.append(line[i:i+2]); i += 2; continue
            if c == '%':
                break
            keep.append(c); i += 1
        out.append(''.join(keep))
    return '\n'.join(out)


def body(path):
    t = open(os.path.join(ROOT, path), encoding='utf-8').read()
    t = strip_comments(t)
    m = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', t, re.S)
    return m.group(1) if m else t


def blocks(path):
    """→ [(块名, CJK流)]：按 \tihao{N} / \ti{N}{ 切题块，块间非题文归入「件层」"""
    t = body(path)
    pos = [(m.start(), '题' + m.group(1)) for m in
           re.finditer(r'\\(?:tihao|ti)\{(\d+)\}', t)]
    out = []
    for idx, (st, name) in enumerate(pos):
        en = pos[idx+1][0] if idx+1 < len(pos) else len(t)
        seg = t[st:en]
        seg = re.sub(r'\\[a-zA-Z@]+\*?', ' ', seg)
        seg = re.sub(r'\\.', ' ', seg)
        seg = re.sub(r'[{}$\[\]()&~^_]', ' ', seg)
        out.append((name, ''.join(c for c in seg if '\u4e00' <= c <= '\u9fff')))
    return out


def grams(s, n):
    return {s[i:i+n] for i in range(len(s)-n+1)}


def runs(s, common, n):
    hit = [s[i:i+n] in common for i in range(len(s)-n+1)]
    out, i = [], 0
    while i < len(hit):
        if hit[i]:
            j = i
            while j + 1 < len(hit) and hit[j+1]:
                j += 1
            out.append(s[i:j+n]); i = j + 1
        else:
            i += 1
    return out


B = {k: blocks(v) for k, v in FILES.items()}
for n in (14,):
    print('=' * 72)
    print(f'### {n} 字窗（题块级）###')
    for a in ('拓展册', '测评卷'):
        for b in B:
            if b == a or (a, b) in (('拓展册', '练习9.1'), ('拓展册', '练习9.2'), ('拓展册', '练习9.3'), ('拓展册', '练习9.4'), ('拓展册', '导学9.1'), ('拓展册', '导学9.2'), ('拓展册', '导学9.3'), ('拓展册', '导学9.4'), ('拓展册', '章末易错'), ('拓展册', '学史切片'), ('测评卷', '练习9.1'), ('测评卷', '练习9.2'), ('测评卷', '练习9.3'), ('测评卷', '练习9.4'), ('测评卷', '导学9.1'), ('测评卷', '导学9.2'), ('测评卷', '导学9.3'), ('测评卷', '导学9.4'), ('测评卷', '章末易错'), ('测评卷', '学史切片')):
                continue
            pairs = []
            for na, sa in B[a]:
                ga = grams(sa, n)
                if not ga:
                    continue
                for nb, sb in B[b]:
                    inter = ga & grams(sb, n)
                    if not inter:
                        continue
                    for seg in runs(sa, inter, n):
                        tag = '通用' if any(g in seg for g in GEN) and len(seg) <= 21 else '核'
                        pairs.append((na, nb, seg, tag))
            if not pairs:
                print(f'  {a} vs {b:8s}: 0 重叠  OK')
                continue
            print(f'  {a} vs {b:8s}: {len(pairs)} 段')
            for na, nb, seg, tag in pairs:
                print(f'      [{tag}] {a}·{na} ↔ {b}·{nb}（{len(seg)}字）{seg}')
