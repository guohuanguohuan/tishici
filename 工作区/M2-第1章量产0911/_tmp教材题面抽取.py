# -*- coding: utf-8 -*-
r"""_tmp教材题面抽取.py — 教材题入池前置闸·步骤1：从 _tmp教材全文.txt＋_tmp教材题目归属.json 重建 149 题题面。

乱码字形还原：人教B版PDF字库映射破损——斜体拉丁字母映射为 CJK 字形（犃=A…=Z，犪=a…狕=z，
经第1章全文频控＋上下文实证），根号＝槡，板块名/题号圆圈为区外乱码。
题块边界＝V2 坐标归属 json 的逐题「题干首行」按文档流排序切块，跨页续题天然覆盖；
块尾另设截断规则：节号行（1.1.2/1.2.4…）、乱码板块头、正文栏目（本章/尝试与发现/解/证/例题头）、
提示答案行（含全角双空格且非「（数字）/（字母）」开头的行）、图注行。
产出 _tmp教材题面149.txt（人读版）＋ _tmp教材题面.json（比对版）。
目验注：p36 顶部 ⑩⑪⑬ 四题（习题1—1B 续行，两位数圆圈字形在文本层不可见）＝V2 计数漏收，
不在 149 口径内；本件按覆写规则从 B·9 块尾截断，四题原文另落 _tmp教材题面-漏收4.txt。
"""
import re, json, os

WS = os.path.dirname(os.path.abspath(__file__))

_upper = {0x7283:'A',0x7285:'B',0x7286:'C',0x7287:'D',0x7288:'E',0x7289:'F',
          0x728C:'G',0x7295:'M',0x7296:'N',0x7297:'O',0x7298:'P',0x7299:'Q',
          0x729A:'R',0x729B:'S'}
_lower = {0x72AA:'a',0x72AB:'b',0x72AE:'c',0x72B1:'d',0x72B2:'e',
          0x72BB:'i',0x72BC:'j',0x72BD:'k',0x72BE:'l',0x72BF:'m',0x72C0:'n',
          0x72C6:'p',0x72C7:'q',0x72C9:'r',0x72CA:'s',0x72CB:'t',0x72CC:'u',
          0x72CF:'v',0x72D3:'x',0x72D4:'y',0x72D5:'z'}
MAP = dict(_upper); MAP.update(_lower)
EXTRA = {0x69E1:'√', 0xE010:'．', 0xE011:'－', 0xE01B:'⊂', 0xE039:'⇔', 0xE5C6:''}
HINTBOX = set(chr(o) for o in range(0xE4F3, 0xE4FB))      # 提示答案方框①-⑧
CIRC2 = set(chr(o) for o in range(0xE7E8, 0xE7EC))        # 两位圆圈⑩⑪⑫（V2漏收四题标记）
ALLOW_EXTRA = '→←′｜≤≥⊥∥△≠≈〈〉πλμθφ°√①②③④⑤⑥⑦⑧⑨⑩ⅠⅡⅢⅣⅤⅥⅦⅧ…·—－'

def restore(s):
    return ''.join(MAP.get(ord(c), EXTRA.get(ord(c), c)) for c in s)

# ---- 读页（题目区 PDF p18–75） ----
txt = open(os.path.join(WS, '_tmp教材全文.txt'), encoding='utf-8').read()
pages = re.split(r'===== 第(\d+)页 =====\n', txt)
stream = []
for i in range(1, len(pages), 2):
    n = int(pages[i])
    if 18 <= n <= 75:
        for ln in pages[i + 1].split('\n'):
            stream.append((n, ln))

attr = json.load(open(os.path.join(WS, '_tmp教材题目归属.json'), encoding='utf-8'))

def is_cjk(c): return '一' <= c <= '鿿'
def is_fwd(c): return '０' <= c <= '９'

def junky(t):
    """整行丢弃：页眉/页码/图注/顶点字母/板块乱码头/栏目标签行"""
    if t == '': return True
    if re.fullmatch(r'[０-９\s　.．]*', t): return True
    if re.match(r'^第[一二三]章', t): return True
    if re.match(r'^[０-９]*本章小结', t): return True
    if re.match(r'^１．[１２]　', t): return True
    if re.match(r'^图[０-９１-９]', t): return True
    if re.match(r'^（第[０-９１-９]+题）', t): return True
    if re.fullmatch(r"[A-Za-z''′１-９1-9]{1,3}", t): return True
    if re.fullmatch(r"[A-Za-z′]*（第[０-９１-９]+题）", t): return True
    if re.fullmatch(r'[犃犅犆]组', t): return True
    bad = sum(1 for c in t if not (is_cjk(c) or '！' <= c <= '￯' or '　' <= c <= '〿'
              or ' ' <= c <= '~' or ord(c) in MAP or ord(c) in EXTRA or c in ALLOW_EXTRA))
    good = len(t) - bad
    if bad >= 2 and good < 6: return True
    if bad >= max(4, len(t) * 0.5): return True
    return False

# 栏目头乱码字（区外码位：Ethiopic/Canadian/Phaistos 等），以码位表构造避免源文件字节漂移
COLHEAD = ''.join(chr(o) for o in (0x174D, 0x177D, 0x1748, 0x0393, 0x117C, 0x12A6,
                                   0x072D, 0x1B6F, 0x02F8, 0x1BA5, 0x113C, 0x110B,
                                   0x117B, 0x1A8E, 0x1A9F, 0x14F0, 0x1455, 0x1D0E))
CUTS = [
    re.compile(r'^1\.[12]'),                                # 节号行（1.1.2／1.2.4…）
    re.compile(r'^[!"][．"!#$%*+,./0-9A-Za-z!"]*$'),        # 「1.2 应用」乱码头（纯ASCII符号行）
    re.compile('[' + re.escape(COLHEAD) + ']'),             # 解/证/例/小结/结构图 栏目头
    re.compile(r'^本章'),
    re.compile(r'尝试与发现'),
    re.compile(r'^[犃犅犆]组|^[ABC]组$'),
    re.compile(r'^立体几何与物质'),
]

def is_cut(t):
    for c in CUTS:
        if c.search(t): return True
    if any(ch in HINTBOX for ch in t): return True          # 提示答案行（方框序号字形）
    if any(ch in CIRC2 for ch in t): return True            # 两位数圆圈题（V2漏收四题，另册登记）
    MATHPUNCT = '→＝｜＋－；，、．。（）〈〉°π×⊥∥≤≥′…·∈⊂⇔'
    if not any(is_cjk(ch) or is_fwd(ch) or ('a' <= ch <= 'z' or 'A' <= ch <= 'Z') or ch in MATHPUNCT
               for ch in t) and len(t) >= 2:
        return True                               # 纯乱码符号行（板块头残片，如「""」「!."!」）
    if re.match(r'^[０-９]', t) and not any(is_cjk(ch) for ch in t) and not re.match(r'^[０-９]+．', t):
        return True                               # 提示答案行（数字开头无汉字）
    if t.count('　　') >= 2 and '；' not in t and '（　　）' not in t and not re.match(r'^（[０-９]+）', t) \
            and not re.match(r'^（[ＡＢＣＤA-Za-z]', t) and not re.match(r'^[①②③⑥]', t):
        return True                               # 提示答案行（全角双空格分栏、无分号、非小问/选项行）
    return False

# 注：原对 习题1—1#·9 的人工覆写截断已由全局 CIRC2 规则替代（p36 目验：两位数圆圈字形＝V2 漏收）
OVERRIDES = {}

def norm_head(s):
    s = s.strip().lstrip('　')
    s = re.sub(r'^\?\s*', '', s)
    return s

qstarts = []
for sec, d in attr.items():
    for i, q in enumerate(d['题'], 1):
        qstarts.append([sec, i, q['页(pdf)'], norm_head(q['题干首行']), None])

pos = 0; miss = []
for qs in qstarts:
    found = None
    for k in range(pos, len(stream)):
        p, ln = stream[k]
        if p < qs[2]: continue
        if p > qs[2] + 1: break
        nh = norm_head(ln)
        if nh and (nh.startswith(qs[3][:18]) or qs[3].startswith(nh[:18])):
            found = k; break
    if found is None:
        for k, (p, ln) in enumerate(stream):
            if p == qs[2] and norm_head(ln).startswith(qs[3][:12]):
                found = k; break
    if found is None:
        miss.append(qs[:4]); qs[4] = None
    else:
        qs[4] = found; pos = found + 1

blocks = []
for idx, qs in enumerate(qstarts):
    if qs[4] is None:
        blocks.append((qs, [])); continue
    end = len(stream)
    for j in range(idx + 1, len(qstarts)):
        if qstarts[j][4] is not None:
            end = qstarts[j][4]; break
    qid = '%s·%d' % (qs[0], qs[1])
    ov = OVERRIDES.get(qid)
    lines = []
    for k in range(qs[4], end):
        p, ln = stream[k]
        t = ln.strip()
        if junky(t): continue
        if is_cut(t) or (ov and ov.match(t)): break
        lines.append((p, t))
    merged = []
    for p, ln in lines:
        if ln in ('（', '）', '(', ')', '［', '］', '[', ']') and merged:
            merged[-1] = (merged[-1][0], merged[-1][1] + ln)
        elif ln and merged and merged[-1][1].endswith(('，', '、', '（', '的', '是', '求', '且')) \
                and re.match(r'^[（）A-Za-z０-９]', ln) and len(ln) <= 12:
            merged[-1] = (merged[-1][0], merged[-1][1] + ln)
        else:
            merged.append((p, ln))
    blocks.append((qs, merged))

out_txt, out_js = [], []
for qs, merged in blocks:
    sec, no, pg, head, _ = qs
    body = '\n'.join(ln for p, ln in merged)
    body = re.sub(r'\n+', '\n', body)
    out_txt.append('### %s·%d [p%d]%s\n' % (sec, no, pg, '' if qs[4] is not None else ' [缺位!]'))
    out_txt[-1] += restore(body) + '\n'
    out_js.append({'id': '%s·%d' % (sec, no), 'sec': sec, 'no': no, 'page': pg,
                   'body_raw': body, 'body': restore(body)})
open(os.path.join(WS, '_tmp教材题面149.txt'), 'w', encoding='utf-8').write('\n'.join(out_txt))
json.dump(out_js, open(os.path.join(WS, '_tmp教材题面.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('题数=%d 缺位=%d' % (len(blocks), len(miss)))
for m in miss: print('  MISS', m)

# ---- 漏收4题（V2 计数漏收：习题1—1B ⑩⑪⑫⑬，p36 目验）单列 ----
miss4 = []
grab = False
for p, ln in stream:
    if p != 36: continue
    t = ln.strip()
    if any(ch in CIRC2 for ch in t):
        grab = True
        t = re.sub(r'^[﹣-]*[-]', '', t)   # 剥两位圆圈字形→题号另加
        t = '〔B〕' + t
    if grab:
        if t.startswith('? 如果存在三个不全为') or t.startswith('˸'): break
        if not junky(t): miss4.append(t)
open(os.path.join(WS, '_tmp教材题面-漏收4.txt'), 'w', encoding='utf-8').write(
    '# 习题1—1B ⑩⑪⑬（p36 目验，V2 坐标归属法漏收，不在149口径内）\n' + restore('\n'.join(miss4)) + '\n')
print('漏收4题行数=%d' % len(miss4))
