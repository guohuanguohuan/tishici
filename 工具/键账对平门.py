# -*- coding: utf-8 -*-
r"""键账对平门.py — 键账对平门（军师收口轮0913 §九钉②：「对集合不对数」三源对平）。

三源键集合（各源＝键的多重表，判定取集合）：
  ①答案册/键账侧：--book 答案册 body.tex（`% pair:键` 对号契约行＝M2/P1 口径；
    `\ansitem{N}{…}`＝M3/[E] 口径，--ansitem 开腿、配 --pair-prefix 拼前缀成 测-N 键，
    默认不开——M2 册式 ansitem 系版式裸号非账钥）；--ledger 键账
    json（[E] --keys 同制式：{"keys":N,"vals":{键:值}}｜{"keys":[…]}｜平铺 {键:值}，
    切丁区喂单件子集亦同制式）；--expect 外部键表（一行一键，`-`＝stdin——M2 四本侧
    632 档即由 check_pairs.collect_expected() 出临时清单承接）。
  ②件面锚侧：--piece 件 tex（含 \input/\include 链展平）之行首注释锚 `% ans:键`；
    编译锚 `\begin{ansblock}[键]` 另腿对平（锚↔块＝[E] 锚账2 同款）。
  ③实题侧：同件 tex 剔注释后 `\ti{N}`/`\tihao{N}` 实题数号，经 --keyfmt（或 --prefix）
    成键（如 测-{n}、拓-{n:03d}、练-{dir}-{n}，{dir}＝件所在目录名）。

判定（军师钉「对集合不对数」）：
  两两源**集合双向 diff**（缺＝下游丢键，浮＝幻影键）；计数相等**不构成**对平——
  号集不同亦红（防 1..19 挪成 2..20 式假对平，红语标注「挪号假对平」）；
  重号/计数差只登记不判死（集合裁决）。
  剔注释行规则（P1「差1键」核销同款）：`\ti` 计数前先逐行剥未转义 `%` 至行尾（[D]
  RE_INLINE 同制）——注释行/行尾注里的 `\ti{` 假命中**不入账**，只作「假命中剔除登记」
  列行号；契约锚只认行首单 `%` 形（`^%[ \t]*pair:`／`^[ \t]*%[ \t]*ans:`），`%%` 双注释、
  行间散提（含正文注释里提及 `% ans:`/`pair:`）一律计作假命中不计入集合。
  已知设计内差（如 M2 四本侧 160 档浮键 拓-057＝义A-1 撤下、M2 键账 json 中文别名 2 键
  ＝钉-1/钉-3 直查哨）用 --waive 键@源标签子串 挂哨核销＝从标签匹配的**含该键诸源**摘除
  该键（子串留空＝全源）；至少命中一源，否则用法错。核销后仍逐条印出，退出码转绿。

用法: python 工具/键账对平门.py [--book [标签=]body.tex]… [--ledger [标签=]键账.json]…
        [--expect [标签=]键表.txt|-]… [--piece [标签=]件.tex]…
        [--keyfmt '拓-{n:03d}' | --prefix 测] [--slice 测,滚A] [--ansitem] [--pair-prefix 测]
        [--waive '拓-057@四本']… [--quiet] [--out 报告.txt] [--selftest]
  例（P1 测评本三源）: python 工具/键账对平门.py --book 答案册/body.tex --ledger 试迁键账.json
        --slice 测 --piece 原件=测评卷/main.tex --piece 换装B=测评卷/main-换装B.tex --prefix 测
  例（M2 全册三源）: python 工具/键账对平门.py --book 册原=成卷/答案册/body.tex
        --ledger 快照=成卷/答案册/值快照.json --expect 四本160档=临时键表.txt
退出码: 0＝全对平（含核销后对平）；1＝有红（缺键/浮键/挪号）；2＝用法/输入错（含 --waive
  未命中任何源、可对比腿不足两条）。
负测自测: --selftest 系统临时目录合成 健康正例（含注释假命中）＋缺键/浮键/挪号假对平
  三负例＋核销转绿例＋无腿用法错例，断言真拦真放行，跑毕即删不落项目树。
红线: 全部输入只读；本脚本不写 tex/件树；--out 报告与 selftest 临时件除外。
"""
import argparse
import io
import itertools
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RE_INLINE = re.compile(r'(?<!\\)%.*$')                    # 剥注释（\% 转义不剥）——[D] 同制
RE_PAIR = re.compile(r'^%[ \t]*pair:(\S+)', re.M)         # 答案册对号契约（check_pairs 口径）
RE_PAIR_STRICT = re.compile(r'^%[ \t]*pair:')             # 契约行判据（假命中排除用）
RE_ANSITEM = re.compile(r'\\ansitem\{([^}]+)\}\{')        # M3 答案册条目（[E] 口径）
RE_ANCHOR = re.compile(r'^[ \t]*%[ \t]*ans:(\S+)')        # 件面行首注释锚（单 % 形）
RE_BLOCK = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]')
RE_TI_NUM = re.compile(r'\\ti(?:hao)?[ \t]*(?:\[[^\]]*\])?[ \t]*\{(\d+)\}')
RE_TI_RAW = re.compile(r'\\ti(?:hao)?[ \t]*\{')           # naive 计数（假命中取证用）
RE_PCT_ANY = re.compile(r'%[ \t]*ans:(\S+)')              # 锚假命中扫描
RE_PAIR_ANY = re.compile(r'%[ \t]*pair:(\S+)')            # pair 假命中扫描
RE_INPUT = re.compile(r'\\(?:input|include)\{([^}]+)\}')


def _read(path):
    return open(path, encoding='utf-8-sig', errors='replace').read()


def _label(spec, default):
    if '=' in spec and not re.match(r'^[A-Za-z]:[\\/]', spec):
        lab, p = spec.split('=', 1)
        return lab, p
    return default, spec


def load_book(path, pair_prefix):
    """答案册腿：行首 `% pair:` 契约集＋`\ansitem{N}` 集（[E] 兼容拼前缀）＋假命中行。"""
    raw = _read(path)
    pair = RE_PAIR.findall(raw)
    ai = RE_ANSITEM.findall(raw)
    if ai and pair_prefix:
        ai = ['%s-%s' % (pair_prefix, k) for k in ai]
    ghost = [(i, l.strip()[:64]) for i, l in enumerate(raw.splitlines(), 1)
             if RE_PAIR_ANY.search(l) and not RE_PAIR_STRICT.match(l)]
    return pair, ai, ghost


def load_ledger(path):
    """键账 json（[E] --keys 同制式）：{"keys":N,"vals":{…}}｜{"keys":[…]}｜平铺 {键:值}。"""
    j = json.loads(_read(path))
    if isinstance(j, dict):
        if isinstance(j.get('vals'), dict):
            return list(j['vals'].keys())
        if isinstance(j.get('keys'), list):
            return list(j['keys'])
        return list(j.keys())
    return list(j)


def load_expect(spec):
    if spec == '-':
        raw = sys.stdin.buffer.read().decode('utf-8', 'replace')
    else:
        raw = _read(spec)
    ks = []
    for l in raw.splitlines():
        l = l.strip()
        if l and not l.startswith('#'):
            ks.append(l.split()[0])
    return ks


def flatten_tex(path, seen=None, out=None, depth=0):
    r"""件 tex＋\input/\include 链展平→[(file, lineno, raw)]（[D] load_tex 同制）。"""
    if seen is None:
        seen, out = set(), []
    ap = os.path.abspath(path)
    if ap in seen or depth > 6:
        return out
    seen.add(ap)
    mine = []
    for i, raw in enumerate(_read(ap).splitlines(), 1):
        line = (ap, i, raw)
        mine.append(line)
        out.append(line)
    for _, _, raw in mine:
        for m in RE_INPUT.finditer(RE_INLINE.sub('', raw)):
            sub = m.group(1)
            if not sub.endswith('.tex'):
                sub += '.tex'
            cand = os.path.join(os.path.dirname(ap), sub)
            if os.path.isfile(cand):
                flatten_tex(cand, seen, out, depth + 1)
    return out


def num2key(fmt, texfile, n):
    d = os.path.basename(os.path.dirname(os.path.abspath(texfile)))
    return fmt.format(n=n, dir=d)


def load_piece(spec, keyfmt, prefix):
    """件面腿：行首锚集＋编译锚集＋实题键集（剔注释后）＋假命中登记。"""
    lab, path = _label(spec, None)
    lines = flatten_tex(path)
    anchors, blocks, ti = [], [], []
    naive = real = 0
    ghost_ti, ghost_anchor = [], []
    fmt = keyfmt or ('%s-{n}' % prefix if prefix else None)
    for f, i, raw in lines:
        code = RE_INLINE.sub('', raw)
        m1 = RE_ANCHOR.match(raw)
        if m1:
            anchors.append(m1.group(1))
        elif RE_PCT_ANY.search(raw):
            ghost_anchor.append((os.path.basename(f), i, raw.strip()[:64]))
        for m in RE_BLOCK.finditer(code):
            blocks.append(m.group(1).strip())
        a = RE_TI_NUM.findall(code)
        b = len(RE_TI_RAW.findall(raw))
        real += len(a)
        naive += b
        if b > len(a):
            ghost_ti.append((os.path.basename(f), i, raw.strip()[:64]))
        for k in a:
            ti.append(num2key(fmt, f, int(k)) if fmt else str(int(k)))
    lab = lab or (os.path.basename(os.path.dirname(path)) + '/' + os.path.basename(path))
    return {'label': lab, 'anchors': anchors, 'blocks': blocks, 'ti': ti, 'fmt': fmt,
            'naive': naive, 'real': real, 'ghost_ti': ghost_ti, 'ghost_anchor': ghost_anchor}


def diff_pair(la, ka, lb, kb):
    sa, sb = set(ka), set(kb)
    miss = sorted(sa - sb)
    extra = sorted(sb - sa)
    if miss or extra:
        m = []
        if miss:
            m.append('%s有%s无（缺 %d）%s' % (la, lb, len(miss), miss[:12] + (['…'] if len(miss) > 12 else [])))
        if extra:
            m.append('%s有%s无（浮 %d）%s' % (lb, la, len(extra), extra[:12] + (['…'] if len(extra) > 12 else [])))
        if len(sa) == len(sb):
            m.append('！计数相等而集合不等＝挪号假对平')
        return False, '｜'.join(m), len(miss), len(extra)
    return True, '集合相等 %d↔%d' % (len(sa), len(sb)), 0, 0


def selftest():
    import tempfile
    rc = 0
    with tempfile.TemporaryDirectory(prefix='键账对平门-selftest-') as td:
        ks = ['测-%d' % i for i in (1, 2, 3, 4)]
        body = os.path.join(td, 'body.tex')
        with open(body, 'w', encoding='utf-8') as fh:
            fh.write('% 头注：对号契约 `%% pair:键` 一行一键（此 pair: 系口径说明非标记）\n')
            for k in ks:
                fh.write('%% pair:%s\n\\ansline{dummy}{值%s}\n' % (k, k))
        ledger = os.path.join(td, 'ledger.json')
        json.dump({'keys': 4, 'vals': {k: 'v' for k in ks}}, open(ledger, 'w', encoding='utf-8'),
                  ensure_ascii=False)

        def mkpiece(name, anchors, extra_ti=(), ghost=True):
            p = os.path.join(td, name)
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write(f'% 件壳 {name}\n')
                if ghost:
                    fh.write('% \\ti{9} 注释行假命中（P1 核销同款）\n')
                    fh.write('% % ans:测-77 双注释假锚（不计）\n')
                for k in anchors:
                    fh.write('\\ti{%s}{题干} %% 行尾散提 ans:测-88 不计\n' % k.split('-')[-1])
                    fh.write('  %% ans:%s\n  \\begin{ansblock}[%s]答\\end{ansblock}\n' % (k, k))
                for n in extra_ti:
                    fh.write('\\ti{%d}{浮题}\n' % n)
            return p

        base = ['x', '--book', body, '--ledger', ledger, '--prefix', '测']

        def run(tag, extra, expect):
            got = main(base + extra)
            ok = got == expect
            print('[selftest %s] %s：退出码 %d（期望 %d）\n' % ('PASS' if ok else 'FAIL', tag, got, expect))
            return ok
        run('P0 健康件（含注释行/行尾注/双注释假命中·全剔后真放行）',
            ['--piece', mkpiece('ok.tex', ks)], 0)
        run('N1 缺键（锚+块+实题缺 测-3）真拦',
            ['--piece', mkpiece('miss.tex', [k for k in ks if k != '测-3'])], 1)
        run('N2 浮键（件面多 测-99 锚＋实题浮 88）真拦',
            ['--piece', mkpiece('ghost.tex', ks + ['测-99'], extra_ti=[88])], 1)
        run('N3 挪号假对平（锚/块齐·实题号挪成 2..5·计数等集合不等）真拦',
            ['--piece', mkshift(td, ks)], 1)
        run('P4 核销（N1 缺键 --waive 测-3@ 全源摘除挂哨后转绿）',
            ['--piece', mkpiece('miss2.tex', [k for k in ks if k != '测-3']),
             '--waive', '测-3@'], 0)
        print('[selftest] 无对账腿应回 2：退出码 %d（期望 2）' % main(['x']))
        rc |= (main(['x']) != 2)
    print('[selftest %s]' % ('PASS 负测真拦·正测真放行' if rc == 0 else 'FAIL'))
    return 0 if rc == 0 else 1


def mkshift(td, ks):
    """N3 挪号件：锚/块保持 1..4（与键账对平），实题号挪成 2..5。"""
    p = os.path.join(td, 'shift.tex')
    with open(p, 'w', encoding='utf-8') as fh:
        for k in ks:
            fh.write('  %% ans:%s\n  \\begin{ansblock}[%s]答\\end{ansblock}\n' % (k, k))
        for n in (2, 3, 4, 5):
            fh.write('\\ti{%d}{题}\n' % n)
    return p


def main(argv):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--book', action='append', default=[])
    ap.add_argument('--ledger', action='append', default=[])
    ap.add_argument('--expect', action='append', default=[])
    ap.add_argument('--piece', action='append', default=[])
    ap.add_argument('--keyfmt')
    ap.add_argument('--prefix', default='')
    ap.add_argument('--pair-prefix', dest='pair_prefix', default='')
    ap.add_argument('--ansitem', action='store_true')
    ap.add_argument('--slice', default='')
    ap.add_argument('--waive', action='append', default=[])
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--out')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('-h', '--help', action='store_true')
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if a.help or not (a.book or a.ledger or a.expect or a.piece):
        print(__doc__)
        return 2
    L = []

    def out(s=''):
        L.append(s)
        if not a.quiet:
            print(s)

    def _pfx(k):
        return k.split('-')[0] if '-' in k else k

    srcs = []
    for b in a.book:
        lab, p = _label(b, '')
        lab = lab or os.path.basename(os.path.dirname(p)) or '册'
        if not os.path.isfile(p):
            print('[FAIL] 输入不存在:', p)
            return 2
        pair, ai, ghost = load_book(p, a.pair_prefix)
        note = '剔行首外 pair: 假命中 %d 行：%s' % (len(ghost), ghost[:3]) if ghost else '无假命中'
        if pair:
            out('[源] 答案册pair=%s：%d 键（`%% pair:` 行首契约；%s）' % (lab, len(pair), note))
            srcs.append(('答案册pair=' + lab, pair))
        if ai and a.ansitem:
            if not a.pair_prefix:
                out('[提示] --ansitem 未配 --pair-prefix：裸数号跨域重号，仅作在体断言')
            out('[源] 答案册ansitem=%s：%d 键（--pair-prefix=%s）' % (lab, len(ai), a.pair_prefix or '（无·裸号）'))
            srcs.append(('答案册ansitem=' + lab, ai))
        elif ai:
            out('[注] %s：另见 `\\ansitem{N}` 条目宏 %d 处——版式裸号非对号键（跨域重号），'
                '默认不入对账（[E]/M3 册口径用 --ansitem 开腿）' % (p, len(ai)))
        if not pair and not (ai and a.ansitem):
            print('[FAIL] 答案册无可用键腿（pair 标记%s）：%s' % ('/ansitem 均未获键' if not ai else '，ansitem 腿未开', p))
            return 2
    for lg in a.ledger:
        lab, p = _label(lg, '键账')
        if not os.path.isfile(p):
            print('[FAIL] 输入不存在:', p)
            return 2
        ks = load_ledger(p)
        out('[源] 键账json=%s：%d 键（[E] --keys 同制式）' % (lab, len(ks)))
        srcs.append(('键账json=' + lab, ks))
    for e in a.expect:
        p = _label(e, '')[1]
        if e != '-' and not os.path.isfile(p):
            print('[FAIL] 输入不存在:', e)
            return 2
        lab, p = _label(e, '外账')
        ks = load_expect(p)
        out('[源] 外账=%s：%d 键（一行一键）' % (lab, len(ks)))
        srcs.append(('外账=' + lab, ks))
    pc_anchors, pc_blocks, pc_ti, pc_lab = [], [], [], []
    for pc in a.piece:
        d = load_piece(pc, a.keyfmt, a.prefix)
        out('[件] %s：行首锚 %d｜编译锚 %d｜实题 %d（naive 含注释 %d·剔假命中 %d）'
            % (d['label'], len(set(d['anchors'])), len(set(d['blocks'])),
               len(d['ti']), d['naive'], d['naive'] - d['real']))
        for f, i, t in d['ghost_ti']:
            out('    [假命中·不计] \\ti 注释行 %s:%d｜%s' % (f, i, t))
        for f, i, t in d['ghost_anchor']:
            out('    [假命中·不计] 非行首 ans: %s:%d｜%s' % (f, i, t))
        pc_anchors += d['anchors']
        pc_blocks += d['blocks']
        if d['ti']:
            if d['fmt'] is None:
                out('[提示] %s：实题腿无 --keyfmt/--prefix（裸号键），不入对账' % d['label'])
            else:
                pc_ti += d['ti']
        pc_lab.append(d['label'].split('/')[0])
    # 多件并集对平（同册分卷/一件多页＝件面侧并集；逐件读数已在 [件] 行列出）
    ulab = '诸件并集(%s)' % '+'.join(dict.fromkeys(pc_lab)) if len(pc_lab) > 1 else (
        pc_lab[0] if pc_lab else '件')
    if pc_anchors:
        srcs.append(('件面锚(% ans:)=' + ulab, pc_anchors))
    if pc_blocks:
        srcs.append(('编译锚(ansblock)=' + ulab, pc_blocks))
    if pc_ti:
        srcs.append(('实题(\\ti)=' + ulab, pc_ti))
    slices = {x.strip() for x in a.slice.split(',') if x.strip()}
    if slices:
        srcs = [(l, [k for k in ks if _pfx(k) in slices]) for l, ks in srcs]
        out('[切丁] --slice %s 过滤后：%s' % (a.slice, '，'.join('%s=%d' % (l, len(set(k))) for l, k in srcs)))
    for lab, ks in srcs:
        if len(ks) != len(set(ks)):
            dup = sorted({k for k in ks if ks.count(k) > 1})
            out('[计数] %s：多重表 %d→集合 %d（重号 %s）——对集合不对数，只登记不判死'
                % (lab, len(ks), len(set(ks)), dup[:8]))
    waived = []
    for w in a.waive:
        if '@' not in w:
            print('[FAIL] --waive 须为 键@源标签子串：%s' % w)
            return 2
        key, sub = w.split('@', 1)
        hit = False
        for i, (lab, ks) in enumerate(srcs):
            if sub in lab and key in ks:
                srcs[i] = (lab, [x for x in ks if x != key])
                hit = True
        if not hit:
            print('[FAIL] --waive 未命中任何源：%s（先核源标签再挂哨）' % w)
            return 2
        waived.append(w)
    live = [(l, k) for l, k in srcs if k]
    for l, k in srcs:
        if not k:
            out('[跳过] %s：0 键（该腿缺席——册式件答案在答案册、无件面锚属正常）' % l)
    if len(live) < 2:
        print('[FAIL] 可对比腿不足两条，无从对平')
        return 2
    nred = 0
    for (la, ka), (lb, kb) in itertools.combinations(live, 2):
        ok, msg, nm, nx = diff_pair(la, ka, lb, kb)
        out('[对账] %s(%d)↔%s(%d)：%s → %s'
            % (la, len(set(ka)), lb, len(set(kb)), msg, 'PASS' if ok else 'FAIL'))
        nred += (not ok)
    for w in waived:
        out('[核销] --waive %s（设计内差·挂哨放行）' % w)
    verdict = '[PASS] 键账三源集合对平（对集合不对数）' if nred == 0 else \
        '[FAIL] %d 对集合不平，须定位键名回查' % nred
    out(verdict)
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(L + [verdict]) + '\n')
    return 0 if nred == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
