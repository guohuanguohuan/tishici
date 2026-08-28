# -*- coding: utf-8 -*-
"""空位公式回填：修复「行内公式掉位堆积到段尾」缺陷（2026-08-26 定案）。

背景：修复轮重装配曾把段落内交错的内联公式整体挪到段尾堆积（甚至把源的多条公式
挤进单个 oMath），句中留下「，，」空位（欧拉线题即此类）。本工具按源文件模板回填：
  1) 扫描目标 docx 中「双逗空位」签名段（工具/空位公式扫描.py 同款签名）；
  2) 用段落去前缀规范化文字（公式抽走后的纯文字流）在源索引
     （高中数学/参考/**/*.docx 全量）中定位源段落；详解合并段允许链式消费多个源段
     （每步剥【标签】/编号前缀、交界允许吞 ≤2 个「；。．,」连接符），段尾剩余纯文字
     （无空位）可保留；
  3) 公式对位三态：等数→成品元素按模板顺序搬移；成品挤成单块→校验拼接恒等且无灰底
     后整体换源克隆（剥显式字号，继承成品 docDefaults）；成品缺公式→缺位源克隆补齐；
  4) 按源交错模板切成品文字 run（逐段规范化内容校验；rPr 原样保留，灰底/字号/图不丢；
     零文本 run（含图）按位置归组），先模拟验证再落笔，任一断言不过判 MANUAL 不动段。

用法：python 空位公式回填.py [--apply] <docx> [docx ...]   （默认 DRY-RUN 只出计划）
回填后必须重跑该件全部对账自检（公共规则修复轮纪律），本工具不替代对账。
"""
import glob
import re
import shutil
import sys
import time
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WT, WR, WOM = f'{{{W}}}t', f'{{{W}}}r', f'{{{M}}}oMath'
WOMP = f'{{{M}}}oMathPara'

SRC_GLOB = '高中数学/参考/**/*.docx'
_TR = str.maketrans('（），．；：（）－＝', '(),.;:()-=')
JUNCTION = set(';。．.,，')
PREFIX_RE = re.compile(
    r'^\s*(?:【[^】]{1,14}】|\d{1,3}[\.．、]|\(\d{1,3}\)|（\d{1,3}）|新序号：\d+|\d{1,3}、|[A-D][\.．])*')


def norm(s):
    # 匹配键：去空白/分号/等号（装配曾把'='挪进公式块），字符本体仍在 raw 组内保留
    return re.sub(r'\s+', '', s).translate(_TR).replace(';', '').replace('=', '')


def strip_prefix(s):
    prev = None
    for _ in range(4):
        if prev == s:
            break
        prev = s
        s = PREFIX_RE.sub('', s)
    return s


def math_lin(om):
    return ''.join(t.text or '' for t in om.iter(f'{{{M}}}t'))


def math_norm(s):
    return re.sub(r'\s+', '', s).translate(str.maketrans('－＝（），−–′', '-=(),--' + chr(39)))


_PSTRIP = str.maketrans('', '', '()[]')


def math_cmp(s):
    """比较形态：括号差异（成品文本括号 vs 源 m:d 定界符线性化不可见）不算内容差。"""
    return math_norm(s).translate(_PSTRIP)


def math_loose(s):
    """宽松形态：≤/≥ 与 </> 视同（装配期单字符微差），仅用于对位，不用于改内容。"""
    return math_cmp(s).translate(str.maketrans('≤≥', '<>'))


def r_text(r):
    return ''.join(t.text or '' for t in r.findall(WT))


def para_seq(p):
    seq = []
    for child in p.iter():
        qn = etree.QName(child)
        if qn.namespace == W and qn.localname == 't' and child.text:
            seq.append(('t', child.text))
        elif qn.namespace == M and qn.localname == 'oMath':
            seq.append(('m', math_lin(child)))
    return seq


BN_PREFIX = re.compile(r'^(?:【[^】]{1,14}】|\(\d{1,3}\)|\d{1,3}[\.．、]|[A-D][\.．])')


def _walk_match(bn, cursor, want):
    """段首匹配：直接 / 容忍一个多余连接符 / 剥段首编号标签后同前两态。返回命中位或 -1。"""
    if bn[cursor:cursor + len(want)] == want:
        return cursor
    if cursor < len(bn) and bn[cursor] in JUNCTION and bn[cursor + 1:cursor + 1 + len(want)] == want:
        return cursor + 1
    m = BN_PREFIX.match(bn[cursor:])
    if m:
        c3 = cursor + m.end()
        if bn[c3:c3 + len(want)] == want:
            return c3
        if c3 < len(bn) and bn[c3] in JUNCTION and bn[c3 + 1:c3 + 1 + len(want)] == want:
            return c3 + 1
    return -1


def has_slot(n):
    return ',,' in n


def build_source_index(root_dir='.'):
    exact, all_keys, file_keys = {}, [], {}
    for f in sorted(glob.glob(f'{root_dir}/{SRC_GLOB}', recursive=True)):
        try:
            with zipfile.ZipFile(f) as z:
                doc = etree.fromstring(z.read('word/document.xml'))
        except Exception:
            continue
        for pi, p in enumerate(doc.iter(f'{{{W}}}p')):
            seq = para_seq(p)
            txt = ''.join(s for k, s in seq if k == 't')
            if len(txt) < 4 or not any(k == 'm' for k, _ in seq):
                continue
            key = norm(strip_prefix(txt))
            if len(key) < 4:
                continue
            exact.setdefault(key, []).append((f, pi))
            all_keys.append(key)
            file_keys.setdefault(f, []).append((pi, key))
    buckets, short_keys = {}, set()
    for k in all_keys:
        if len(k) < 8:
            short_keys.add(k)
        else:
            buckets.setdefault(k[:8], set()).add(k)
    return exact, buckets, short_keys, file_keys


def clone_src_math(elem):
    """深拷贝源 oMath；剥 m:r 层 w:rPr 显式 w:sz/w:szCs（字号继承成品 docDefaults）。"""
    nr = etree.fromstring(etree.tostring(elem))
    for rpr in nr.iter(f'{{{W}}}rPr'):
        for tag in ('sz', 'szCs'):
            for e in rpr.findall(f'{{{W}}}{tag}'):
                rpr.remove(e)
    return nr


def math_elems_of(p):
    """段落直接子级中的公式元素（oMathPara 展平为其内各 oMath）。"""
    out = []
    for c in p:
        if c.tag == WOM:
            out.append(c)
        elif c.tag == WOMP:
            out.extend(c.findall(WOM))
    return out


def extract_template(path, pidx):
    """源段落交错模板：[('t',text,None) | ('m',lin,元素)]，连续文字合并、剥前缀。"""
    with zipfile.ZipFile(path) as z:
        doc = etree.fromstring(z.read('word/document.xml'))
    for pi, p in enumerate(doc.iter(f'{{{W}}}p')):
        if pi != pidx:
            continue
        tmpl = []
        for child in p:
            if child.tag == WR:
                txt = r_text(child)
                if not txt:
                    continue
                if tmpl and tmpl[-1][0] == 't':
                    tmpl[-1] = ('t', tmpl[-1][1] + txt, None)
                else:
                    tmpl.append(('t', txt, None))
            elif child.tag == WOM:
                tmpl.append(('m', math_lin(child), child))
            elif child.tag == WOMP:
                for om in child.findall(WOM):
                    tmpl.append(('m', math_lin(om), om))
        if tmpl and tmpl[0][0] == 't':
            stripped = strip_prefix(tmpl[0][1])
            if not stripped:
                tmpl.pop(0)
            else:
                tmpl[0] = ('t', stripped, None)
        return tmpl or None
    return None


def _step_strip(remaining):
    remaining = re.sub(r'^(【[^】]{1,14}】)+', '', remaining)
    return PREFIX_RE.sub('', remaining)


def _junction_skip(remaining):
    skipped = 0
    while remaining[:1] in JUNCTION and skipped < 2:
        remaining = remaining[1:]
        skipped += 1
    return remaining


def file_run_match(key, exact, buckets, short_keys, file_keys):
    """同文件连续段游走：正确碎片在源文件里逐段相邻（详解一式一段时尤甚）。"""
    starts = []
    for k in buckets.get(key[:8], ()):
        if len(k) >= 8 and key.startswith(k):
            starts.append(k)
    for k in short_keys:
        if len(k) >= 4 and key.startswith(k):
            starts.append(k)
    starts.sort(key=len, reverse=True)
    tried = set()
    for k in starts[:60]:
        for f, pi in exact[k][:6]:
            if (f, pi) in tried:
                continue
            tried.add((f, pi))
            fl = file_keys[f]
            idx = next((i for i, (p2, _) in enumerate(fl) if p2 == pi), None)
            if idx is None:
                continue
            plan, remaining = [], key
            j = idx
            dead = False
            while remaining:
                cur = fl[j][1] if j < len(fl) else None
                if cur is not None and (remaining == cur or remaining.startswith(cur)):
                    plan.append((f, fl[j][0]))
                    remaining = _junction_skip(remaining[len(cur):])
                    remaining = _step_strip(remaining)
                    j += 1
                    continue
                if cur is not None and len(cur) >= 4 and cur.startswith(remaining):
                    plan.append((f, fl[j][0]))  # 末段源比成品长（段尾截断）
                    return plan, ''
                if not plan or not has_slot(remaining):
                    break
                dead = True  # 还有空位但断链：换下一个起点
                break
            if dead:
                continue
            if plan and not remaining:
                return plan, ''
            if plan and remaining and not has_slot(remaining):
                return plan, remaining
    return None


def greedy_match(key, exact, buckets, short_keys):
    plan, remaining = [], key
    while remaining and has_slot(remaining):
        remaining = _step_strip(remaining)
        cand = exact.get(remaining)
        if cand:
            plan.append(cand[0])
            return plan, ''
        best = None
        for k in buckets.get(remaining[:8], ()):
            if len(k) >= 8 and remaining.startswith(k) and (best is None or len(k) > len(best)):
                best = k
        for k in short_keys:
            if remaining.startswith(k) and (best is None or len(k) > len(best)):
                best = k
        if best is None:
            return plan, remaining
        plan.append(exact[best][0])
        remaining = _junction_skip(remaining[len(best):])
    return plan, remaining


def sub_index(exact, file_keys, sub):
    ex2 = {k: [e for e in v if sub in e[0]] for k, v in exact.items()}
    ex2 = {k: v for k, v in ex2.items() if v}
    keys2 = set(ex2)
    bk2 = {}
    for k in keys2:
        if len(k) >= 8:
            bk2.setdefault(k[:8], set()).add(k)
    sk2 = {k for k in keys2 if len(k) < 8}
    fk2 = {f: v for f, v in file_keys.items() if sub in f}
    return ex2, bk2, sk2, fk2


def chain_match(key, exact, buckets, short_keys, file_keys, sub=None):
    cand = exact.get(key)
    if cand:
        return [cand[0]], ''
    for idx in ((exact, buckets, short_keys, file_keys),
                sub_index(exact, file_keys, sub) if sub else None):
        if idx is None:
            continue
        run = file_run_match(key, *idx)
        if run is not None:
            return run
        g_plan, g_rem = greedy_match(key, idx[0], idx[1], idx[2])
        if g_plan and not (g_rem and has_slot(g_rem)):
            return g_plan, g_rem
    return greedy_match(key, exact, buckets, short_keys)


def cut_group(runs, a, b, total):
    """复制 runs 中 raw 区间 [a,b) 为新元素列表；零文本 run（含图）按位置归组。"""
    grp, pos = [], 0
    for r in runs:
        t = r_text(r)
        s, e = pos, pos + len(t)
        pos = e
        if not t:
            if a <= s < b or (b >= total and s >= a):
                grp.append(etree.fromstring(etree.tostring(r)))
            continue
        lo, hi = max(a, s), min(b, e)
        if lo >= hi:
            continue
        nr = etree.fromstring(etree.tostring(r))
        nt = nr.findall(WT)
        nt[0].text = t[lo - s:hi - s]
        grp.append(nr)
    return grp


def _build_tmpl(plan):
    tmpl = extract_template(plan[0][0], plan[0][1])
    if tmpl is None:
        return None
    for nxt in plan[1:]:
        t2 = extract_template(nxt[0], nxt[1])
        if t2 is None:
            return None
        tmpl += t2  # 不合并相邻文字段：保留源段边界，交界连接符由走位段首跳过
    return tmpl


def repair_paragraph(p, exact, buckets, short_keys, file_keys, sub=None):
    kids = [c for c in p if c.tag != f'{{{W}}}pPr']
    for c in kids:
        if etree.QName(c).localname not in ('r', 'oMath', 'oMathPara',
                                            'bookmarkStart', 'bookmarkEnd', 'proofErr'):
            return 'MANUAL', f'非常规子元素{etree.QName(c).localname}'
    runs = [c for c in kids if c.tag == WR]
    maths = math_elems_of(p)
    if not runs or not maths:
        return 'MANUAL', '无文字run或无公式'
    for r in runs:
        if r.findall(f'{{{W}}}tab') or r.findall(f'{{{W}}}br'):
            return 'MANUAL', 'run含制表/断行'
        if not r.findall(WT) and not r.findall(f'{{{W}}}drawing'):
            return 'MANUAL', '空run'
        ts = r.findall(WT)
        if len(ts) > 1:
            ts[0].text = ''.join(t.text or '' for t in ts)
            for extra in ts[1:]:
                r.remove(extra)
    p_raw = ''.join(r_text(r) for r in runs)
    total = len(p_raw)
    stripped = strip_prefix(p_raw)
    prefix_len = p_raw.find(stripped) if stripped else total
    if prefix_len < 0:
        return 'MANUAL', '前缀定位失败'
    p_key = norm(stripped)
    if len(p_key) < 4:
        return 'MANUAL', '文字过短'
    plan, remaining = chain_match(p_key, exact, buckets, short_keys, file_keys, sub)
    if not plan:
        return 'MANUAL', '源索引未命中'
    if remaining and has_slot(remaining):
        return 'MANUAL', f'链式残留空位:{remaining[:40]}'
    tmpl = _build_tmpl(plan)
    if tmpl is None:
        return 'MANUAL', '模板提取失败'
    t_elems = [e for k, lin, e in tmpl if k == 'm']
    tm = [math_cmp(lin) for k, lin, e in tmpl if k == 'm']
    if len(maths) not in (len(tm),) and len(maths) != 1 and len(plan) > 1:
        # file_run 选错起点致公式数不齐：回退重试（子索引链 / greedy）
        for plan2, rem2 in (
                chain_match(p_key, exact, buckets, short_keys, file_keys, sub)
                if sub else (None, None),
                greedy_match(p_key, exact, buckets, short_keys)):
            if not plan2 or (rem2 and has_slot(rem2)):
                continue
            tmpl2 = _build_tmpl(plan2)
            if tmpl2 is None:
                continue
            tm2 = [math_cmp(lin) for k, lin, e in tmpl2 if k == 'm']
            if len(maths) == len(tm2):
                plan, tmpl = plan2, tmpl2
                t_elems = [e for k, lin, e in tmpl if k == 'm']
                tm = tm2
                break
    pm = [math_cmp(math_lin(m)) for m in maths]
    tl = [math_loose(lin) for k, lin, e in tmpl if k == 'm']
    pl = [math_loose(math_lin(m)) for m in maths]
    micro = pm != tm and sorted(pm) == sorted(tm)
    if len(maths) == len(tm):
        order = list(range(len(maths)))
        if pl != tl:
            if sorted(pl) != sorted(tl):
                return 'MANUAL', '公式多重集不一致'
            pool, order = maths[:], []
            for x in tl:
                for j, e in enumerate(pool):
                    if math_loose(math_lin(e)) == x:
                        order.append(maths.index(e))
                        pool.pop(j)
                        break
    elif len(maths) == 1 and len(tm) > 1:
        joined = pl[0]
        pat = ''.join(re.escape(x) + '[,;，；()（）]?' for x in tl)
        if joined != ''.join(tl) and not re.fullmatch(pat, joined):
            return 'MANUAL', f'挤块拼接不恒等:{joined[:28]}'
        if maths[0].find('.//' + f'{{{W}}}shd') is not None:
            return 'MANUAL', '挤块含灰底标记需手工'
        maths = [clone_src_math(e) for e in t_elems]
        order = list(range(len(maths)))
        micro = False
    elif len(maths) < len(tm):
        left = maths[:]
        new_maths = []
        for i, x in enumerate(tl):
            hit = None
            for e in left:
                if math_loose(math_lin(e)) == x:
                    hit = e
                    break
            if hit is not None:
                new_maths.append(hit)
                left.remove(hit)
            else:
                new_maths.append(clone_src_math(t_elems[i]))
        if left:
            return 'MANUAL', f'成品多出公式{math_cmp(math_lin(left[0]))[:20]}'
        maths = new_maths
        order = list(range(len(maths)))
    else:
        return 'MANUAL', f'公式数不齐 源{len(tm)}≠成{len(maths)}'
    # —— 正文按模板逐段内容校验（norm 坐标→raw 坐标），段首可跳连接符 ——
    body = p_raw[prefix_len:]
    npos, bn = [], ''
    for i, ch in enumerate(body):
        cn = norm(ch)
        if cn:
            bn += cn
            npos.append(i)
    cursor = 0
    bounds = []
    for ent in tmpl:
        if ent[0] != 't':
            continue
        want = norm(ent[1])
        pos = _walk_match(bn, cursor, want)
        if pos < 0:
            return 'MANUAL', f'文字段校验失败:{want[:20]}'
        cursor = pos + len(want)
        bounds.append(npos[cursor - 1] + 1 if cursor > 0 else 0)
    if bn[cursor:] and has_slot(bn[cursor:]):
        return 'MANUAL', '段尾剩余含空位'
    # —— 组装新子元素序列 ——
    new_kids = []
    if prefix_len > 0:
        new_kids += cut_group(runs, 0, prefix_len, total)
    mi = seg_i = 0
    raw_pos = prefix_len
    for ent in tmpl:
        if ent[0] == 't':
            end = prefix_len + bounds[seg_i]
            new_kids += cut_group(runs, raw_pos, end, total)
            raw_pos = end
            seg_i += 1
        else:
            new_kids.append(maths[order[mi]])
            mi += 1
    if cursor < len(npos):
        tail_start = npos[cursor]
    elif npos:
        tail_start = npos[-1] + 1  # norm 已尽但尾部可能有空白
    else:
        tail_start = len(body)
    if tail_start < len(body):  # 尾部剩余（含尾随空白）原样保留
        new_kids += cut_group(runs, prefix_len + tail_start, total, total)
    # —— 模拟验证（未落笔）——
    sim = []
    for c in new_kids:
        if c.tag == WR:
            sim.append(('t', r_text(c)))
        elif c.tag == WOM:
            sim.append(('m', math_lin(c)))
    joined = ''.join(f'⟦{s}⟧' if k == 'm' else s for k, s in sim)
    if re.search(r'，[^\S⟦]{0,4}，', joined):
        return 'MANUAL', f'重建后仍有空位:{joined[:60]}'
    if ''.join(s for k, s in sim if k == 't') != p_raw:
        return 'MANUAL', '重建文字流≠原文（内容校验拦截）'
    # —— 落笔 ——
    for c in list(kids):
        if etree.QName(c).localname not in ('bookmarkStart', 'bookmarkEnd'):
            p.remove(c)
    for c in kids:
        if etree.QName(c).localname in ('bookmarkStart', 'bookmarkEnd'):
            p.append(c)
    for c in new_kids:
        p.append(c)
    tag = f'{plan[0][0].split("/")[-1][:36]}#p{plan[0][1]}' + (f'+{len(plan)-1}链' if len(plan) > 1 else '')
    if micro:
        tag += ' ※内容微差见对账'
    return 'OK', f'{tag} | {joined[:70]}'


def main():
    args = [a for a in sys.argv[1:] if a != '--apply']
    apply_mode = '--apply' in sys.argv
    print('建源索引…', file=sys.stderr)
    exact, buckets, short_keys, file_keys = build_source_index()
    print(f'索引键 {len(exact)}', file=sys.stderr)
    grand_ok = grand_manual = 0
    for path in args:
        with zipfile.ZipFile(path) as z:
            doc = etree.fromstring(z.read('word/document.xml'))
        targets = []
        for pi, p in enumerate(doc.iter(f'{{{W}}}p')):
            seq = para_seq(p)
            if not any(k == 'm' for k, _ in seq):
                continue
            joined = ''.join(f'⟦{s}⟧' if k == 'm' else s for k, s in seq)
            if re.search(r'，[^\S⟦]{0,4}，', joined):
                targets.append((pi, p, joined))
                continue
            # 弱签名：题干以（）收尾后还堆积 >=2 个公式（单空位掉位）
            j2 = len(seq) - 1
            while j2 >= 0 and seq[j2][0] == 'm':
                j2 -= 1
            cluster = sum(1 for k, _ in seq[j2 + 1:] if k == 'm')
            tail_text = seq[j2][1] if j2 >= 0 and seq[j2][0] == 't' else ''
            if cluster >= 2 and tail_text.rstrip().endswith(('）', ')')):
                targets.append((pi, p, joined))
        ok = manual = 0
        print(f'== {path} 目标 {len(targets)} 段')
        sub = '选择性必修3' if '选必2' in path else None
        for pi, p, joined in targets:
            status, info = repair_paragraph(p, exact, buckets, short_keys, file_keys, sub)
            if status == 'OK':
                ok += 1
            else:
                manual += 1
            print(f'  p#{pi} {status}: {info} | 原:{joined[:90]}')
        print(f'   小计 OK={ok} MANUAL={manual}')
        grand_ok += ok
        grand_manual += manual
        if apply_mode and ok:
            buf = etree.tostring(doc.getroottree(), xml_declaration=True,
                                 encoding='UTF-8', standalone=True)
            tmp = path + '.tmp'
            with zipfile.ZipFile(path) as zin, \
                 zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
                for it in zin.infolist():
                    data = buf if it.filename == 'word/document.xml' else zin.read(it.filename)
                    zout.writestr(it, data)
            for _ in range(5):
                try:
                    shutil.move(tmp, path)
                    break
                except PermissionError:
                    time.sleep(2)
            print(f'   已落盘（{ok} 段）')
    print(f'总计 OK={grand_ok} MANUAL={grand_manual}')


if __name__ == '__main__':
    main()
