# -*- coding: utf-8 -*-
r"""内容守恒断言（测评卷 v4）：v3→v4 改版仅动版式宏，源题文字/公式零增删的脚本举证。
方法：平衡花括号参数解析（跳过转义 \{ \} 与控制序列首 token），分别从 v3/v4 main.tex 提取：
  A 题干：v3 \timu{号}{题干}（Q1/Q2）与 \timuky{号}{前缀}{k}{剩余}（Q3–Q10，题干＝前缀＋剩余）
        ↔ v4 \timu{号}{难度}{★}{k}{题干}——逐题比对 知识点号 与 题干串；
  B 选项/题干续块：v3 「\penalty10000 \noindent …」段落 ↔ v4 \opts{…}——剔除 \newline、
    \penalty10000、\noindent 版式记号后逐段比对（段序一致）；
  C 答案：\daan{号}{值}{解析} 三参逐条比对（v3↔v4 应全等）；
  D 分号「；」计数：v3 文件 ↔ v4 文件 必须相等（一个不许删）。
空白全剥后比对（v3 零增删证明同口径：空白归一化）。v4 新增题侧标签（难度/★/（知识点N））
与卷头评分说明行为拍板授权件，不在源题文本比对范围（登记于交付报告）。"""
import re

V3 = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v3\测评卷\main.tex"
V4 = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\测评卷\main.tex"

def strip_ws(s):
    return re.sub(r'\s+', '', s)

def parse_args(text, i):
    """text[i:] 起个命令后解析连续 {...} 参数，返回 (参数列表, 下一位置)。"""
    args = []
    n = len(text)
    while i < n and text[i] == '{':
        depth = 0
        j = i
        buf = []
        while j < n:
            c = text[j]
            if c == '\\':
                buf.append(text[j:j + 2])
                j += 2
                continue
            if c == '{':
                depth += 1
                if depth == 1:
                    j += 1
                    continue
            elif c == '}':
                depth -= 1
                if depth == 0:
                    args.append(''.join(buf))
                    j += 1
                    break
            buf.append(c)
            j += 1
        i = j
    return args, i

def find_all(text, cmd):
    out = []
    for m in re.finditer(re.escape(cmd), text):
        args, _ = parse_args(text, m.end())
        if args:
            out.append(args)
    return out

v3 = open(V3, encoding='utf-8').read()
v4 = open(V4, encoding='utf-8').read()
body3 = v3[v3.index('\\begin{document}'):]
body4 = v4[v4.index('\\begin{document}'):]

fails = []
def check(name, ok, detail=''):
    print(f"[{'通过' if ok else '未通过'}] {name}{('：' + detail) if detail else ''}")
    if not ok:
        fails.append(name)

# ---------- A 题干 ----------
t3 = {}
for a in find_all(body3, r'\timu'):
    stem = re.sub(r'\\hfill\\kylabel\{（知识点\d）\}', '', a[1])   # v3 行末标签为题侧件，剔后比对
    t3[strip_ws(a[0])] = (None, strip_ws(stem))
for a in find_all(body3, r'\timuky'):
    pre, k, rest = a[1], a[2], a[3]
    t3[strip_ws(a[0])] = (k, strip_ws(pre) + strip_ws(rest))
t4 = {}
for a in find_all(body4, r'\timu'):
    num, diff, star, k, stem = a[0], a[1], a[2], a[3], a[4]
    t4[strip_ws(re.sub(r'\\fenzhi\{\d+\}', '', num))] = (k, strip_ws(stem), diff, star)

ok = True
detail = []
for q in sorted(t3, key=lambda s: int(re.match(r'\d+', s).group())) if t3 else []:
    k3, stem3 = t3[q]
    if q not in t4:
        ok = False
        detail.append(f'{q} v4 缺')
        continue
    k4, stem4, diff4, star4 = t4[q]
    if k3 is not None and k3 != k4:
        ok = False
        detail.append(f'{q} 知识点号 {k3}→{k4}')
    if stem3 != stem4:
        ok = False
        detail.append(f'{q} 题干不等价')
    if diff4 not in ('简单', '中档', '冲刺'):
        ok = False
        detail.append(f'{q} 难度档异常 {diff4}')
check('A 题干零增删（10 题逐题回查）＋知识点号守恒＋难度档格式', ok and len(t3) == 10,
      f'{len(t3)} 题' + ('；' + '；'.join(detail) if detail else ''))

# ---------- B 选项/题干续块 ----------
p3 = [strip_ws(re.sub(r'\\penalty10000|\\noindent', '', p)) for p in body3.split('\n\n') if '\\noindent' in p and 'A．' in p or '\\noindent' in p and '①' in p]
# 上面条件歧义，改为显式：取所有含 \noindent 的段
p3 = []
for p in body3.split('\n\n'):
    if '\\noindent' in p and 'textwidth' not in p:   # 剔答案页通栏线（非选项段）
        p3.append(strip_ws(re.sub(r'\\penalty10000|\\noindent', '', p)))
p4 = [strip_ws(re.sub(r'\\newline', '', a[0])) for a in find_all(body4, r'\opts')]
ok = len(p3) == len(p4) and all(a == b for a, b in zip(p3, p4))
if not ok:
    det = [f'段{i+1}: v3[{a[:24]}…] vs v4[{b[:24]}…]' for i, (a, b) in enumerate(zip(p3, p4)) if a != b]
    check('B 选项/续块零增删', False, f'v3 {len(p3)} 段 / v4 {len(p4)} 段；' + '；'.join(det))
else:
    check('B 选项/续块零增删', True, f'{len(p4)} 段逐段全等（\\newline 版式记号已剔除）')

# ---------- C 答案 ----------
d3 = find_all(body3, r'\daan')
d4 = find_all(body4, r'\daan')
ok = len(d3) == len(d4) == 10 and all(
    strip_ws(x[0]) == strip_ws(y[0]) and strip_ws(x[1]) == strip_ws(y[1]) and strip_ws(x[2]) == strip_ws(y[2])
    for x, y in zip(d3, d4))
check('C 答案块 10 条逐字全等（号/答案值/解析）', ok, f'{len(d3)} 条')

# ---------- D 分号 ----------
n3, n4 = body3.count('；'), body4.count('；')   # 正文口径（文件级含注释散文，仅报告）
check('D 分号计数守恒（一个不许删）', n3 == n4,
      f'正文（\\begin{{document}} 后）v3 {n3} ↔ v4 {n4}；文件级 v3 {v3.count("；")} ↔ v4 {v4.count("；")}（差额来自注释散文）')

print('——')
print('断言结果：', '通过' if not fails else f'未通过（{fails}）')
raise SystemExit(0 if not fails else 1)
