# -*- coding: utf-8 -*-
"""空位公式扫描 v2：三签名版（2026-08-27 升级，公共规则§5「空位公式红旗扫描」现行口径）。

检测「行内公式掉位堆积」缺陷家族（欧拉线题109段缺陷、讲练下62题「5式并1块堆段尾」等）：

  签名① 双逗空位【主判据】——段落线性化（文字＋⟦公式⟧交错流）中出现两个全角逗号
          相邻（中间至多空白）且无任何公式隔开＝公式掉位主判据。
  签名② 段尾公式簇【弱判据·须人工核验】——段尾文字以「）」收尾后仍堆积 ≥2 个独立
          式子碎片。碎片按线性化结构切分计数：等号/逗号/分号边界各断开一件，坐标
          括号式整体各计一件；掉位公式被并进单个 oMath 块同样计入，块数不作计数单位
          （62题5式并1块即此变体——旧版按 oMath 块数计数即漏）。
  签名③ 量词空位【弱判据·须人工核验】——量词名词（点/直线/向量/平面/曲线/圆/函数/
          数列及同族延伸）后紧跟全角逗号且中间无名号符号＝单空位掉位弱判据
          （62题「已知点，平面过原点，且垂直于向量」空位之间隔有文字、双逗不相邻，
          ①不触发，靠本签名兜住）。

命中＝红旗：必须对照源文件交错模板定位核验（回填走 工具/空位公式回填.py），禁止未定位
即以「扫描误报」为由放过。本工具只读不改；②③为弱判据输出带「须人工核验」标记，
但①②③计数一律真实输出。线性化命名空间/压扁逻辑与 回填.py 同款（m:t 全拼接），
可先用 dump_docx.py --slice 定点复核命中段全文。

用法：python 工具/空位公式扫描.py <docx> [docx ...]
输出：逐命中行（文件｜题号·正文b#N·p#N｜签名类型｜摘录≤100字）＋每件小计＋总计。
"""
import re
import sys
import zipfile

from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WT_P = '{%s}p' % W

EXCERPT_LEN = 100          # 摘录上限（字）
WS = '[ \u3000\t]'         # 半角空格／全角空格／制表

# —— 签名③量词名词：核心＝公共规则§5列举（点/直线/向量/平面/曲线/圆/函数/数列）
#    ＋同族锥线三类（椭圆/双曲线/抛物线）。模式：
#      'excl'——前邻字符属排除集即不报（构成原点/交点/奇函数等单位向量类复合词，或
#              数字限定的一/两点等泛指短语，非掉位形态）；
#      'known'——延伸名（立体几何载体/方程/球，纯叙述中泛用极易误报）：只在前邻字符
#              属引导语境白名单（已知/设/若…、句读边界）时才报——恰好截住「已知X，
#              …」式掉位主语形态。
QUANT_NOUNS_EXCL = ('双曲线', '抛物线', '椭圆', '曲线', '直线', '向量', '平面',
                    '圆', '函数', '数列', '点')
QUANT_NOUNS_KNOWN = ('四面体', '平行六面体', '正方体', '长方体', '四棱锥',
                     '三棱锥', '三棱柱', '圆锥', '圆柱', '圆台', '球', '方程')
# 复合名词/泛指短语排除（前邻字）。全局集＝决定词、量词、系动词、连接成分——
# 的/一/在/个/条/两/为/是/成/共/关…（「四点共圆」「一条直线」「相关平面」「高考热点」
# 类完整短语非掉位形态）；「已知X／设X／若X／给定X」语境的引导字不在排除集，
# 保证掉位主语形态可命中。字母数字希腊符号由 _SYM_PREV 统一拦（O点/B点＝带名号）。
_GLOBAL_EXCL = set('的一在个条只支位次批类种为是成作取得到有与及或并也又均即'
                   '就都还使令从对当向朝往沿替给帮跟同关相共整较更最太挺满全部彼此相互其中之这那该此某任另'
                   '其些热少高低长短大小左右里中等')
# 各名词专属复合词尾字：原点/焦点/切点…奇偶函数、单位/法/零/投影/共线/方向向量、半圆等。
_QUANT_EXCL_PREV = {
    '点': {'原', '交', '焦', '顶', '定', '切', '端', '起', '终', '基', '分', '动', '殊',
           '热', '优', '零', '一', '二', '两', '三', '四', '五', '六', '七', '八', '九', '十', '几'},
    '函数': {'奇', '偶', '标'},
    '向量': {'法', '零', '投', '影'},
    '圆': {'半', '切', '内', '外', '接', '同', '弧', '补', '扇', '面', '圆'},
}


def _excl_for(q):
    """全局泛指前缀∪名词专属复合词尾字（统一对所有核心名词生效）。"""
    return _QUANT_EXCL_PREV.get(q, set()) | _GLOBAL_EXCL
_SYM_PREV = re.compile(
    r'[A-Za-z0-9α-ωΑ-Ωа-яＡ-Ｚａ-ｚ０-９°′″∆∇∞±∓×÷≠≤≥≈]')
# known 延伸名的语境白名单：仅「已知X／设X／若X／给定X」与句读/串首后允许裸名——
# 其余叙述性泛用（补成正方体，/内切球，等）不报。
_KNOWN_PREV_OK = set('知设若定。；：？！')


def _compile_quant():
    pats = []
    for q in QUANT_NOUNS_EXCL:
        pats.append((q, 'excl', _excl_for(q),
                     re.compile(re.escape(q) + WS + r'{0,2}，')))
    for q in QUANT_NOUNS_KNOWN:
        pats.append((q, 'known', _KNOWN_PREV_OK,
                     re.compile(re.escape(q) + WS + r'{0,2}，')))
    return pats


_QUANT_PATS = _compile_quant()

_COMMA_PAIR = re.compile(r'，' + WS + r'{0,4}，')   # 签名①：全角逗号对（间隔至多空白）

# —— 签名②碎片切分用：坐标括号式（圆/方括号对，内部至少一个逗号的元组/向量形态）
_COORD_RE = re.compile(r'[（(\[][^（()）\[\]{}]*[,，][^（()）\[\]{}]*[）)\]]')
_FRAG_SEP_RE = re.compile(r'[,，;；]')
_PLACE = '\u2999'   # ⦙ 坐标式占位符
_EQ_RE = re.compile(r'[=＝]')


def paragraph_seq(p):
    """段落交错序列 [(kind, text)]，kind='t' 文字 / 'm' 公式线性化（文档序）。"""
    seq = []
    for child in p.iter():
        qn = etree.QName(child)
        if qn.namespace == W and qn.localname == 't' and child.text:
            seq.append(('t', child.text))
        elif qn.namespace == M and qn.localname == 'oMath':
            lin = ''.join(t.text or '' for t in child.iter(f'{{{M}}}t'))
            seq.append(('m', lin))
    return seq


def _stream(seq):
    """把交错流拼成整串并记录公式区区间 [(起,末)]，供 zone 判定。"""
    buf, zones, pos = [], [], 0
    for k, s in seq:
        if k == 'm':
            if s:
                zones.append((pos, pos + len(s)))
        buf.append(s)
        pos += len(s)
    return ''.join(buf), zones


def _in_formula_zone(zones, a, b):
    return any(a < ze and zs < b for zs, ze in zones)


def fragment_count(lin):
    """签名②碎片计数：独立式子碎片件数。

    口径（公共规则§5现行版）：逗号/分号每断开一处多计一件；同一无逗号片段内第 2 个
    及以后的等号再各加一件（首等号属该件自身——「x+2y-5=0」是一件而非两件，
    「a=1b=2c=3」三式无分隔粘连即 3 件）；坐标括号式整体各计一件（先替换占位符，
    防其内部逗号虚增切分）。掉位公式被并进单个 oMath 块不影响结果——先串接全部
    尾部公式线性化再计数，块数不作计数单位。"""
    s = re.sub(r'\s+', '', lin)
    if not s:
        return 0
    s2 = _COORD_RE.sub(_PLACE, s)
    n = 0
    for part in _FRAG_SEP_RE.split(s2):
        coords = part.count(_PLACE)
        rest = part.replace(_PLACE, '').strip()
        if coords and rest:
            n += coords + 1 + max(0, len(_EQ_RE.findall(rest)) - 1)
        elif coords:
            n += 1          # 纯坐标括号式（或纯坐标组）整体一件
        elif rest:
            n += 1 + max(0, len(_EQ_RE.findall(rest)) - 1)
    return n


def scan_paragraph(seq):
    """返回 {签名: [证据片段]}；无命中返回空 dict。①②③分别至多一条/段（合并同段多处）。"""
    hits = {}
    full, zones = _stream(seq)
    # 签名③量词空位：核心名词前邻字排除复合词/泛指；延伸名词须「已知/设/若」语境。
    cand = []
    for q, mode, charset, pat in _QUANT_PATS:
        for mo in pat.finditer(full):
            a, b = mo.span()
            prev = full[a - 1] if a > 0 else '\x00'
            if mode == 'excl':
                if prev != '\x00' and (prev in charset or _SYM_PREV.match(prev)):
                    continue
            else:   # known 延伸名：仅语境白名单（含串首）后放行
                if prev != '\x00' and prev not in charset:
                    continue
            if _in_formula_zone(zones, a, b):
                continue    # 名词落在公式线性化内不算文字层证据
            if any(a < eb and ab < b for ab, eb, _ in cand):
                continue    # 重叠span去重（双曲线 vs 曲线等同处只记一次）
            cand.append((a, b, q))
    if cand:
        per = max(12, (EXCERPT_LEN // len(cand)) // 2 - 4)
        segs = []
        for a, b, q in sorted(cand):
            lo = max(0, a - per)
            hi = min(len(full), b + per)
            seg = (q + '｜' + ('…' if lo > 0 else '') + full[lo:hi] +
                   ('…' if hi < len(full) else ''))
            if seg not in segs:
                segs.append(seg)
        joined = ' ∥ '.join(segs)
        hits['③'] = [f'{len(cand)}处|{joined}'[:EXCERPT_LEN]]
    # 签名①双逗空位
    pairs = [mo.span() for mo in _COMMA_PAIR.finditer(full)
             if not _in_formula_zone(zones, *mo.span())]
    if pairs:
        a, b = pairs[0]
        lo = max(0, a - (EXCERPT_LEN // 2 - 5))
        hi = min(len(full), b + (EXCERPT_LEN // 2 - 5))
        note = f'{len(pairs)}处' if len(pairs) > 1 else ''
        excerpt = (('…' if lo > 0 else '') + full[lo:hi] + ('…' if hi < len(full) else ''))[:EXCERPT_LEN]
        hits['①'] = [f'[{note}]{excerpt}']
    # 签名②段尾公式簇：段尾为公式堆积、其前文字以「）」收尾，碎片≥2
    j = len(seq) - 1
    while j >= 0 and seq[j][0] == 'm':
        j -= 1
    tail_lins = [s for k, s in seq[j + 1:] if k == 'm']
    if tail_lins:
        tail_text = seq[j][1] if j >= 0 and seq[j][0] == 't' else ''
        frags = fragment_count(''.join(tail_lins))
        if frags >= 2 and tail_text.rstrip().endswith(('）', ')')):
            stem_tail = tail_text.rstrip()[-20:]
            pile = ''.join(tail_lins)[:EXCERPT_LEN - len(stem_tail) - 8]
            hits.setdefault('②', []).append(
                f'碎片={frags}｜…)「{stem_tail}」+⟦{pile}⟧')
    return hits


_SIG_LABEL = {
    '①': '双逗空位[主]',
    '②': '段尾公式簇[弱·须人工核验]',
    '③': '量词空位[弱·须人工核验]',
}


def _body_index_map(root):
    """元素id → 正文元素号（dump_docx 同一口径：body直接子元素序号）＋正文/表格标记。"""
    m = {}
    body = root.find('{%s}body' % W)
    if body is None:
        return m
    for bi, child in enumerate(body.iterchildren()):
        qn = etree.QName(child)
        if qn.localname == 'p':
            m[id(child)] = f'正文b#{bi}'
        elif qn.localname == 'tbl':
            tag = f'表格@b#{bi}'
            for p in child.iter(WT_P):
                m.setdefault(id(p), tag)
    return m


_QNUM_RE = re.compile(r'^(\d{1,3})．')
_MARK_RE = re.compile(r'^(【例题】|【典例\d*】|【举一反三】|【练习题】|【易错题)')
QNUM_MINLEN = 8            # 与 dump_docx 同款经验口径：小数/年份不起误报


def scan_file(path):
    """返回命中行列表 [(题号, 定位, 摘要行)] 与计数 dict。"""
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read('word/document.xml'))
    bimap = _body_index_map(root)
    rows, counts = [], {'①': 0, '②': 0, '③': 0}
    cur_q = None
    for pi, p in enumerate(root.iter(WT_P)):
        seq = paragraph_seq(p)
        txt = ''.join(s for k, s in seq if k == 't').strip()
        mq = _QNUM_RE.match(txt)
        if mq and len(txt) >= QNUM_MINLEN:
            cur_q = mq.group(1)
        else:
            mm = _MARK_RE.match(txt)
            if mm:
                cur_q = mm.group(1)
        sig = scan_paragraph(seq)
        if not sig:
            continue
        loc = []
        if cur_q:
            loc.append(f'题{cur_q}')
        loc.append(bimap.get(id(p), ''))
        loc.append(f'p#{pi}')
        base = '/'.join(x for x in loc if x)
        for key in ('①', '②', '③'):
            if key in sig:
                counts[key] += 1
                ev = sig[key][0]
                rows.append((cur_q or '', pi, key,
                             f'{_SIG_LABEL[key]} | {base} | {ev}'))
    return rows, counts


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    grand = {'①': 0, '②': 0, '③': 0}
    grand_paras = set()
    for path in sys.argv[1:]:
        name = path.replace('\\', '/').split('/')[-1]
        try:
            rows, counts = scan_file(path)
        except Exception as e:
            print(f'ERR {path}: {e}')
            continue
        print(f'== {name}')
        for _, _, _, line in rows:
            print('  HIT | ' + line)
        print(f'  小计[{name}] 命中段落事件: '
              f'①双逗空位={counts["①"]} ②段尾公式簇(须人工核验)={counts["②"]} '
              f'③量词空位(须人工核验)={counts["③"]} 合计={sum(counts.values())}')
        for k in grand:
            grand[k] += counts[k]
        for cur_q, pi, _, _line in rows:
            grand_paras.add((path, pi))
    print(f'TOTAL ①={grand["①"]} ②={grand["②"]} ③={grand["③"]} '
          f'事件合计={sum(grand.values())} 命中段落={len(grand_paras)}')
    print('说明：①主判据命中即须回源定位；②③弱判据须人工核验——对照源文件交错顺序确认，'
          '禁止未定位即以「扫描误报」放过。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
