# -*- coding: utf-8 -*-
"""课时01 试迁对勘（副本树内作业；源件只读）。
A. 源层答案值零漂移：答案册 body.tex 的 \ansitem{N}{…} 体 vs 换装 main-true.tex 的
   \ansitem{N}{…} 体逐键字节比对（\ansline→\ansnote 改名除外）。
B. 印面题序/题面零漂移：原印面 main.pdf（只读树）与换装 true/false PDF 的文本层——
   原印面逐行文本须为换装档文本的子序列（题面行序不变、零漂移）；
   另验 原样基线复编译 PDF vs 原印面 逐行全等（工具链零漂基线）。
C. 答案值印面读数：true 档文本层须含 16 键 \ansitem 答案行、false 档不得含「[答案]」。
"""
import re, sys, io
import fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:/提示词/工作区/_tmp换装预备0913/副本树-练习本"
BODY = r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册/body.tex"
ORIG_PDF = r"C:/提示词/工作区/M2-第1章量产0911/成卷/练习件/课时01/main.pdf"

def ansitems(path, only_section=None):
    """抓 \ansitem{N}{体} 行（含行内前后文原样）；返回 [(N, 原行)]。"""
    out = []
    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()
    sec = None
    for ln in lines:
        if only_section:
            m = re.match(r'\\qufen\{(.+?)\}', ln)
            if m:
                sec = m.group(1)
                continue
        m = re.match(r'\\ansitem\{(\d+)\}\{(.+)\}\s*$', ln)
        if m and (not only_section or (sec and sec.startswith(only_section))):
            out.append((int(m.group(1)), m.group(2)))
    return out

# ---- A. 源层答案值零漂移（第一课时 16 键）----
body_items = ansitems(BODY, only_section='第一课时') if False else []
# body.tex 的 \ansitem 无 \qufen 分节行守卫问题：直接按 pair 键顺序取前 16 个（练-课时01 段 647–707 行）
with open(BODY, encoding='utf-8') as f:
    blines = f.read().splitlines()
grab = False
for ln in blines:
    if ln.startswith('% pair:练-课时01-1\n') or ln.strip() == '% pair:练-课时01-1':
        grab = True
    elif grab and ln.strip().startswith('% pair:练-课时02-'):
        break
    if grab:
        m = re.match(r'\\ansitem\{(\d+)\}\{(.+)\}\s*$', ln)
        if m:
            body_items.append((int(m.group(1)), m.group(2)))

true_items = ansitems(BASE + '/课时01-换装/main-true.tex')
ok = True
if len(body_items) != 16 or len(true_items) != 16:
    ok = False
    print(f'[A] FAIL 键数：body={len(body_items)} true={len(true_items)}（应 16/16）')
for (nb, vb), (nt, vt) in zip(body_items, true_items):
    if nb != nt or vb != vt:
        ok = False
        print(f'[A] FAIL 题{nb}: body「{vb}」 vs true「{vt}」')
print(f'[A] 源层答案值零漂移：{"PASS 16/16 逐字节相等" if ok and len(body_items)==16 else "FAIL"}')

# ---- B. 印面文本层对勘 ----
def pdftext(path):
    doc = fitz.open(path)
    pages = [p.get_text('text') for p in doc]
    doc.close()
    return pages

orig = pdftext(ORIG_PDF)
base = pdftext(BASE + '/00原样基线/main.pdf')
truep = pdftext(BASE + '/课时01-换装/main-true.pdf')
falsep = pdftext(BASE + '/课时01-换装/main-false.pdf')
print(f'[B] 页数：原印面={len(orig)} 基线复编译={len(base)} true={len(truep)} false={len(falsep)}')

def lines_of(pages):
    out = []
    for pg in pages:
        for ln in pg.splitlines():
            s = ln.strip()
            if s:
                out.append(s)
    return out

def col_lines(pdf_path):
    """按阅读序（页×左半栏→右半栏）抽行：fitz 默认 y 序抽取会把双栏内容按行高交错，
    原/迁两档断栏位不同则交错序不同（伪漂移），故显式按半栏裁剪抽取。"""
    doc = fitz.open(pdf_path)
    out = []
    for p in doc:
        W, H = p.rect.width, p.rect.height
        for clip in (fitz.Rect(0, 0, W/2, H), fitz.Rect(W/2, 0, W, H)):
            for ln in p.get_text('text', clip=clip).splitlines():
                s = ln.strip()
                if s:
                    out.append(s)
    doc.close()
    return out

# 工具链基线：原印面 vs 基线复编译 逐行全等
lo, lb = lines_of(orig), lines_of(base)
same = lo == lb
print(f'[B] 基线复编译 vs 原印面 逐行全等：{"PASS" if same else "FAIL"}（行数 {len(lo)}/{len(lb)}）')
if not same:
    for i, (a, b) in enumerate(zip(lo, lb)):
        if a != b:
            print(f'    首个差异行{i}: 原「{a}」 vs 基线「{b}」')
            break

# 题序/题面零漂移（三重核）：
#  B2 tex 源层——题面层行字节零漂移（原样基线 main.tex vs 换装 main-true.tex，
#     滤除插入的答案机制行后余行必须逐行全等）；
#  B3 PDF 内容零丢失——原印面归一化行全部包含于 true/false 档文本（无序包含；
#     分栏流在两档断栏位不同，跨栏行序不可作不变量，序不变量由 B4 承担）；
#  B4 题序——16 个组名标（\zu 体，逐题唯一）在 true 档归一化全文中的命中位严格递增。
import re as _re
with open(BASE + '/00原样基线/main.tex', encoding='utf-8') as f:
    src_base = f.read().splitlines()
with open(BASE + '/课时01-换装/main-true.tex', encoding='utf-8') as f:
    src_new = f.read().splitlines()

def body_question_lines(src):
    """取 \begin{document} 后正文行，滤答案机制行（ansblock/%ans:/\ansitem/\ansnote/
    \setlength{\anshang}/\tailfill）与注释行——余下＝题面层。"""
    try:
        i0 = next(i for i, s in enumerate(src) if s.startswith(r'\begin{document}'))
    except StopIteration:
        return []
    drop = _re.compile(r'^\\(begin\{ansblock\}|end\{ansblock\}|ansitem|ansnote|setlength\{\\anshang\}|tailfill)|^% ans:')
    return [s for s in src[i0+1:] if s.strip() and not s.lstrip().startswith('%') and not drop.match(s)]

qb, qn = body_question_lines(src_base), body_question_lines(src_new)
b2 = qb == qn
print(f'[B2] tex 源题面层零漂移：{"PASS" if b2 else "FAIL"}（题面行 {len(qb)}/{len(qn)}）')
if not b2:
    for a, b in zip(qb, qn):
        if a != b:
            print(f'    首个差异：基线「{a}」 vs 换装「{b}」')
            break

COMB = _re.compile(r'[\u20d0-\u20ff]')
def norm2(s):
    return COMB.sub('', _re.sub(r'\s+', '', s))

full_t = norm2('\n'.join(lines_of(truep)))
full_f = norm2('\n'.join(lines_of(falsep)))
footerish = _re.compile(r'^(第一章|高中数学|练习件|\d{3})')
orig_n = [norm2(s) for s in lines_of(orig)]
orig_nq = [s for s in orig_n if s and not footerish.search(s)]
miss_t = [s for s in orig_nq if s not in full_t]
miss_f = [s for s in orig_nq if s not in full_f]
print(f'[B3] 原印面行零丢失（无序包含，页脚除外）：true 未命中={len(miss_t)} false 未命中={len(miss_f)}（应 0/0）')
for s in (miss_t + miss_f)[:4]:
    print(f'    未命中：「{s[:60]}」')

def zu_body(line):
    """花括号配平取 \zu{ 体。"""
    i = line.find(r'\zu{')
    if i < 0:
        return None
    depth = 0
    for j in range(i + 3, len(line)):
        if line[j] == '{':
            depth += 1
        elif line[j] == '}':
            depth -= 1
            if depth == 0:
                return line[i + 4:j]
    return None

zus = []
for b in (zu_body(s) for s in qb):
    if not b:
        continue
    head = _re.split(r'[\\(（]', b)[0]  # 数学记号（如 \frac）抽取层变竖式，取其前唯一 CJK 前缀
    if len(head) >= 4:
        zus.append(norm2(head))
pos = []
cur = 0
ok4 = True
for z in zus:
    p = full_t.find(z, cur)
    if p < 0:
        ok4 = False
        print(f'    组名标未命中：「{z}」')
    else:
        pos.append(p)
        cur = p + len(z)
mono = all(a < b for a, b in zip(pos, pos[1:]))
print(f'[B4] 题序（16 组名标位严格递增）：{"PASS" if ok4 and mono and len(pos)==16 else "FAIL"}（命中 {len(pos)}/16，递增={mono}）')

# ---- C. 答案值印面读数 ----
t_all = '\n'.join(lines_of(truep))
f_all = '\n'.join(lines_of(falsep))
nans_t = t_all.count('[答案]')
nans_f = f_all.count('[答案]')
nxy_t = t_all.count('[解析]')
nxy_f = f_all.count('[解析]')
print(f'[C] true 印面 [答案]×{nans_t}（应16） [解析]×{nxy_t}（应6）；false [答案]×{nans_f}（应0） [解析]×{nxy_f}（应0）')
c16 = nans_t == 16 and nans_f == 0 and nxy_t == 6 and nxy_f == 0
print(f'[C] 答案印面读数：{"PASS" if c16 else "FAIL"}')
# 中文答案值抽点（文字层可抽取；数学值层已由 A 源层逐字节核对承保）
# 纯答案语（题面层不存在）在 false 档必须缺席；题面兼用语不作 false 判据
pure_ans = ['证明见解析']
spot_true_miss = [x for x in pure_ans if x not in t_all]
spot_false_res = [x for x in pure_ans if x in f_all]
print(f'[C] 纯答案语抽点：true 缺={spot_true_miss}（应空）；false 残留={spot_false_res}（应空）')
tail_t = '笔记与错题整理' in t_all
tail_f = '笔记与错题整理' in f_all
print(f'[C] 尾页填充块（笔记与错题整理）印面在位：true={tail_t} false={tail_f}')
