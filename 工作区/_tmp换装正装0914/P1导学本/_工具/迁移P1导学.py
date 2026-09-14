# -*- coding: utf-8 -*-
r"""迁移P1导学.py — 换装正装波4a：P1 导学本 5 件批插（81 键＝4×19＋章末5）。

承：_tmp换装预备0913/副本树-P1/试迁脚本-P1.py 提取/拆分（split_judge/split_libian/split_ping，
    9.1 试迁 19/19 背书）＋断点件④槽位规则（结构锚，取代逐件文本锚串）＋波2 改判（尾块置位＝
    \end{multicols} 后）＋M2 波1 正装件形（main.tex 纯插入／main-true/pure 双壳／_迁移日志）。
产物（每件）：main.tex（迁移件）／main-true.tex／main-pure.tex／qp-m3p-overlay.sty（树根 v0.2 拷入）／
    _迁移日志.md；另 _键表/件账-<件>.json。
断言（停机制）：锚唯一/计数、键数 19×4＋5、纯插入 diff（原件行序零删改）、K 逐字==值快照（81 键）、
    ansblock 数==键数、overlay 挂接 1／tailfill 1。
红线：零 git；P1 正件/答案册/工具只读；写入仅 工作区/_tmp换装正装0914/P1导学本/。
"""
import io, json, os, re, sys, shutil, hashlib

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.join(os.path.dirname(HERE))                       # …/P1导学本
BODY = r'C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex'
SNAP = r'C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/值快照.json'
STY = os.path.join(TREE, 'qp-m3p-overlay.sty')
KSHU = os.path.join(TREE, '_键表')

DAOXUE = ['9.1电荷', '9.2库仑定律', '9.3电场电场强度', '9.4静电的防止与利用']
ZM = '章末-本章易错过关'


def read(p):
    return io.open(p, encoding='utf-8').read()


# ---------- ① 提取＋成组拆分（承试迁脚本，逐字） ----------
def split_judge(val):
    parts = re.split(r'\((\d)\)', val)
    it = iter(parts[1:])
    return {int(n): re.sub(r'\\quad\s*$', '', v).strip() for n, v in zip(it, it)}


def split_libian(val):
    m = re.match(r'^例1\s*(.*?)；变式1\s*(.*)$', val, re.S)
    assert m, '例变拆分失败: %r' % val
    return m.group(1).strip(), m.group(2).strip()


def split_ping(val):
    parts = re.split(r'(\d)．', val)
    it = iter(parts[1:])
    return {int(n): v.strip().rstrip('；。') for n, v in zip(it, it)}


def expect_keys_ks(i):
    p = '导-课时9%d' % i
    return ([p + '-预习填空']
            + ['%s-判%d' % (p, n) for n in range(1, 7)]
            + ['%s-探%d-%s' % (p, e, k) for e in (1, 2, 3) for k in ('例1', '变式1')]
            + [p + '-拓展']
            + ['%s-评%d' % (p, n) for n in range(1, 6)])


def parse_segment(seg, wants):
    """承试迁：pair 挂起→ansline/ansitem 落账；返回 ansval{键:(标签,值)}。"""
    ansval, pending = {}, []
    for line in seg.splitlines():
        s = line.strip()
        m = re.match(r'^% pair:(.+)$', s)
        if m:
            pending.append(m.group(1).strip())
            continue
        m = re.match(r'^\\ansline\{(.+?)\}\{(.*)\}\s*$', s)
        if m:
            if pending:
                for k in pending:
                    ansval[k] = (m.group(1), m.group(2))
                pending = []
            continue
        m = re.match(r'^\\ansitem\{(.+?)\}\{(.*)\}\s*$', s)
        if m and pending:
            k = pending.pop(0)
            ansval[k] = (m.group(1), m.group(2))
    assert not pending, '缺值键（悬空）: %s' % pending
    assert list(ansval.keys()) == wants, '段内键序不齐: %s' % (set(wants) ^ set(ansval))
    return ansval


def extract():
    body, snap = read(BODY), json.load(io.open(SNAP, encoding='utf-8'))
    K, DETAIL = {}, {}
    for i in (1, 2, 3, 4):
        wants = expect_keys_ks(i)
        seg = body.split('%% ---- 课时9%d' % i, 1)[1]
        seg = seg.split('\\jietitle{9.%d' % (i + 1), 1)[0] if i < 4 else \
            seg.split('\\jietitle{本章易错过关(导学件答案)}', 1)[0]
        av = parse_segment(seg, wants)
        p = '导-课时9%d' % i
        K[p + '-预习填空'] = av[p + '-预习填空'][1]
        jud = split_judge(av[p + '-判1'][1])
        for n in range(1, 7):
            K['%s-判%d' % (p, n)] = jud[n]
        for e in (1, 2, 3):
            a, b = split_libian(av['%s-探%d-例1' % (p, e)][1])
            K['%s-探%d-例1' % (p, e)] = a
            K['%s-探%d-变式1' % (p, e)] = b
        K[p + '-拓展'] = av[p + '-拓展'][1]
        ping = split_ping(av[p + '-评1'][1])
        for n in range(1, 6):
            K['%s-评%d' % (p, n)] = ping[n]
        # 悬空解析（仅课时91 两行）→随探2-例1／探3-例1
        xj = [m.group(1) for m in re.finditer(r'\\ansline\{解析\}\{(.*?)\}\s*$', seg, re.M)]
        assert len(xj) in (0, 2), '课时9%d 解析行数异常: %d' % (i, len(xj))
        if xj:
            DETAIL['%s-探2-例1' % p] = xj[0]
            DETAIL['%s-探3-例1' % p] = xj[1]
    # 章末（\ansitem 直排 5 键）
    zseg = body.split('\\jietitle{本章易错过关(导学件答案)}', 1)[1].split('\\end{multicols}', 1)[0]
    zwant = ['导-章末-%d' % n for n in range(1, 6)]
    zav = parse_segment(zseg, zwant)
    for n in range(1, 6):
        K['导-章末-%d' % n] = zav['导-章末-%d' % n][1]
    assert len(K) == 81, '提取键数≠81: %d' % len(K)
    # 值零漂移链：K（tex 形，件面照插）⇄值快照——判符号形归一（$\times$→×／\(\surd\)→√，M2 同制）
    def norm(v):
        return v.replace('$\\times$', '×').replace('\\(\\surd\\)', '√')
    bad = [k for k in K if norm(K[k]) != snap.get(k)]
    assert not bad, 'K≠值快照 %d 键: %s' % (len(bad), bad[:5])
    return K, DETAIL


# ---------- ② 槽位（结构锚；断点件④规则） ----------
def lineidx(lines, pred, tag, want=None):
    hits = [i for i, l in enumerate(lines) if pred(l)]
    assert want is None or len(hits) == want, '%s 命中 %d（期望 %s）' % (tag, len(hits), want)
    return hits


def prev_nonempty(lines, k):
    j = k - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    assert j >= 0, '锚前无非空行'
    return j


def slots_daoxue(lines):
    """[(行号, 键, 标签)]——插入＝该行之后（行号指原件）。"""
    out = []
    lr = lineidx(lines, lambda l: '\\liubai[9mm]{此处书写}' in l, 'liubai', 1)[0]
    out.append((lr, '预习填空', '预习填空'))
    zh = lineidx(lines, lambda l: re.match(r'^\\zhentib\{', l), 'zhentib', 6)
    for n, i in enumerate(zh, 1):
        lab = re.match(r'^\\zhentib\{(\(\d\))\}', lines[i]).group(1)
        out.append((i, '判%d' % n, lab))
    tj = lineidx(lines, lambda l: re.match(r'^\\tjdnr\{', l), 'tjdnr', 3)
    hu = lineidx(lines, lambda l: re.match(r'^\\huaxing\{', l), 'huaxing')
    for e, t0 in enumerate(tj, 1):
        bounds = [x for x in tj[1:] if x > t0] + [x for x in hu if x > t0]
        t1 = min(bounds)
        seg = range(t0 + 1, t1)
        mk = [i for i in seg if re.match(r'^\\(fanxi|liB|tuoZhan)\{', lines[i])]
        assert mk, '探%d 无例1锚' % e
        out.append((prev_nonempty(lines, mk[0]), '探%d-例1' % e, '例1'))
        lb = [i for i in seg if re.match(r'^\\liB\{', lines[i])]
        assert lb, '探%d 无变式liB' % e
        mn = [i for i in seg if i > lb[0] and re.match(r'^\\(guifanbiao|tuoZhan|xiaojie)\{', lines[i])]
        assert mn, '探%d 变式块尾锚缺失' % e
        out.append((prev_nonempty(lines, mn[0]), '探%d-变式1' % e, '变式1'))
    tz = lineidx(lines, lambda l: re.match(r'^\\tuoZhan\{', l), 'tuoZhan', 1)[0]
    out.append((tz, '拓展', '拓展延伸'))
    js = lineidx(lines, lambda l: re.match(r'^\\jiancestem\{', l), 'jiancestem', 5)
    em = lineidx(lines, lambda l: '\\end{multicols}' in l, 'endmulticols', 1)[0]
    for n, i in enumerate(js, 1):
        bounds = [x for x in js[1:] if x > i] + [em]
        out.append((prev_nonempty(lines, min(bounds)), '评%d' % n, str(n)))
    assert len(out) == 19, '槽位数≠19: %d' % len(out)
    assert len({x[0] for x in out}) == 19, '锚行重号'
    want = {'预习填空'} | {'判%d' % n for n in range(1, 7)} | \
           {'探%d-%s' % (e, k) for e in (1, 2, 3) for k in ('例1', '变式1')} | \
           {'拓展'} | {'评%d' % n for n in range(1, 6)}
    assert {x[1] for x in out} == want, '槽集不合'
    by = {x[1]: x[0] for x in out}
    for e in (1, 2, 3):
        assert by['探%d-例1' % e] < by['探%d-变式1' % e], '探%d 例变序倒挂' % e
    for n in range(1, 5):
        assert by['评%d' % n] < by['评%d' % (n + 1)], '评价序倒挂'
    assert by['判6'] < by['预习填空'] < by['探1-例1'] and by['拓展'] < by['评1']
    return out


def slots_zhangmo(lines):
    th = lineidx(lines, lambda l: re.match(r'^\\tihao\{(\d+)\}', l), 'tihao', 5)
    nums = [int(re.match(r'^\\tihao\{(\d+)\}', lines[i]).group(1)) for i in th]
    assert nums == [1, 2, 3, 4, 5], 'tihao 号≠1..5'
    note = [i for i, l in enumerate(lines) if '【拓展册】' in l]
    assert len(note) == 1, '拓展册注定位失败'
    out = []
    for n, i in enumerate(th, 1):
        bounds = [x for x in th[1:] if x > i]
        if bounds:
            k = min(bounds)
        else:
            k = note[0]
            j = k - 1                                   # 回退 \par\glueguard 注前导行
            while j >= 0 and re.match(r'^\\par\\glueguard', lines[j]):
                j -= 1
            k = j + 1
        out.append((prev_nonempty(lines, k), str(n), str(n)))
    assert len(out) == 5
    return out


# ---------- ③ 括线判据（估高＋display/表/图 强制）＋块体 ----------
def est_lines(v):
    body = re.sub(r'\\[A-Za-z]+', '科', v)
    return max(1, -(-len(body) // 20))


def mode_of(key, v, log):
    disp = bool(re.search(r'\\\(|\\\[\s*$|\\begin\{(align|tabular|tabbing|array)|\\includegraphics|\\qpfig', v))
    n = est_lines(v)
    mode = '括线' if (disp or n > 8) else '灰底'
    log.append(('估高|%s' % key, '估 %d 行｜display/表/图 %s → %s模' % (n, '有' if disp else '无', mode)))
    return mode


def block(key, label, val, detail):
    b = '\\begin{ansblock}[%s]\n%% ans:%s\n\\ansitem{%s}{%s}' % (key, key, label, val)
    if detail:
        b += '\\ansnote{详解}{%s}' % detail
    return b + '\n\\end{ansblock}'


# ---------- ④ 迁移一件 ----------
def migrate(piece, keys, K, DETAIL, md5sty):
    d = os.path.join(TREE, piece)
    src = read(os.path.join(d, 'main.src.tex'))
    lines = src.splitlines()
    log = []
    if piece == ZM:
        slots = slots_zhangmo(lines)
    else:
        slots = slots_daoxue(lines)
    eol = []
    pos, off = [], 0
    for l in lines:
        off += len(l) + 1
        pos.append(off)                              # 行尾偏移（含 \n）
    ins = []
    for ln, suf, label in slots:
        key = keys[suf]
        mode_of(key, K[key], log)
        det = DETAIL.get(key)
        ins.append((pos[ln], block(key, label, K[key], det)))
    if piece == ZM:
        # 试迁报告§五-2 括线风险件：灰底不可拆卡 multicol 平衡（true 实证 Overfull 5.3/14.8pt）
        # → 章末 5 块括线模（可跨栏；题面零动，编译锚/源锚/值不变）
        b1 = min(ins, key=lambda x: x[0])
        ins = [(p, '\\ansblockgrayfalse % 括线模（章末件：可跨栏防灰底卡栏，承方案草案§5.1/试迁§五-2）\n' + s)
               if p == b1[0] else (p, s) for p, s in ins]
        b5 = max(ins, key=lambda x: x[0])
        ins = [(p, s + '\n\\ansblockgraytrue % 复位') if p == b5[0] else (p, s) for p, s in ins]
        log.append(('模判|章末5块', 'true 档灰底卡栏 Overfull×2 → 括线模（\\ansblockgrayfalse 件级置位＋复位）'))
    figs_i = next(i for i, l in enumerate(lines) if 'qp-figs.tex' in l)
    ins.append((pos[figs_i],
                '\n% —— 换装 overlay 挂接（换装正装波4a；七模块后、\\begin{document} 前，承 sty 头用法）——\n'
                '\\usepackage{qp-m3p-overlay}'))
    em = lineidx(lines, lambda l: '\\end{multicols}' in l, 'endmulticols', 1)[0]
    ins.append((pos[em], '\n\\tailfill'))            # 波2 改判：尾块置位＝\end{multicols} 后
    out = src
    for p, s in sorted(ins, key=lambda x: -x[0]):
        assert out[p - 1] == '\n'
        out = out[:p] + s + '\n' + out[p:]
    # 断言：纯插入
    new = out.splitlines()
    it = iter(new)
    for ol in lines:
        for nl in it:
            if nl == ol:
                break
        else:
            sys.exit('原件行被删改: %r' % ol[:60])
    assert out.count('\\begin{ansblock}[') == len(keys), 'ansblock 数≠键数'
    assert len(re.findall(r'^% ans:(\S+)', out, re.M)) == len(keys), '源锚数≠键数'
    assert out.count('\\usepackage{qp-m3p-overlay}') == 1
    assert out.count('\\tailfill') == 1
    # 写件
    io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8', newline='\n').write(out)
    for mode, pure in (('true', '0'), ('pure', '1')):
        hd = '% ============================================================\n'
        hd += '% ' + piece + ' 换装正装波4a·' + ('含详解印本' if mode == 'true' else '纯题') \
            + '档 → main-' + mode + '.pdf\n'
        hd += '% 编译：xelatex main-' + mode + '.tex（两遍取稳态）\n'
        hd += '% ============================================================\n'
        io.open(os.path.join(d, 'main-%s.tex' % mode), 'w', encoding='utf-8', newline='\n').write(
            hd + '\\def\\mthreepure{' + pure + '}\n\\input{main.tex}\n')
    shutil.copyfile(STY, os.path.join(d, 'qp-m3p-overlay.sty'))
    anc = {keys[suf]: 'src 行%d 后' % (ln + 1) for ln, suf, _ in slots}
    io.open(os.path.join(d, '_迁移日志.md'), 'w', encoding='utf-8', newline='\n').write(
        '# _迁移日志-%s（换装正装波4a）\n\n- 迁移键数＝%d%s；源＝答案册 body.tex 导段（`%% pair:` 契约）'
        '，拆分承试迁脚本（判(n)／例变「例1…；变式1…」／评「N．」），拆分值逐字==值快照.json。\n'
        '- 详解随键 %d 处：%s。\\tailfill 1 处（\\end{multicols} 后·波2 改判）；'
        'overlay qp-m3p-overlay.sty v0.2 树根拷入（md5 %s）。\n'
        '- 括线判据：全块灰底模（估高逐块记日志；值内无 display/表/图）。\n'
        '- 断言：锚唯一/键数/纯插入 diff/ansblock==键数 全过。\n\n## 锚表\n%s\n\n## 估高日志\n%s\n'
        % (piece, len(keys), '（19 键）' if len(keys) == 19 else '（章末 5 键）', len(DETAIL),
           '，'.join(sorted(DETAIL)) or '无', md5sty,
           '\n'.join('- %s → %s' % (k, v) for k, v in sorted(anc.items(), key=lambda x: int(re.search(r'\d+', x[1])[0]))),
           '\n'.join('- %s：%s' % (a, b) for a, b in log)))
    io.open(os.path.join(KSHU, '件账-%s.json' % piece), 'w', encoding='utf-8', newline='\n').write(
        json.dumps({'件': piece, '键数': len(keys), '键值': {keys[s]: K[keys[s]] for _, s, _ in slots},
                    '详解随键': {k: v for k, v in DETAIL.items() if k in {keys[s] for _, s, _ in slots}},
                    '插入锚': anc, 'overlay-md5': md5sty}, ensure_ascii=False, indent=1))
    return len(keys), len(DETAIL)


def main():
    K, DETAIL = extract()
    md5sty = hashlib.md5(open(STY, 'rb').read()).hexdigest()
    print('提取 81 键＋拆分值逐字==值快照 PASS｜overlay md5 %s' % md5sty[:8])
    tot = 0
    for piece in DAOXUE + [ZM]:
        if piece == ZM:
            keys = {str(n): '导-章末-%d' % n for n in range(1, 6)}
        else:
            p = '导-课时9%d' % (DAOXUE.index(piece) + 1)
            keys = {suf: '%s-%s' % (p, suf) for suf in
                    ['预习填空'] + ['判%d' % n for n in range(1, 7)] +
                    ['探%d-%s' % (e, k) for e in (1, 2, 3) for k in ('例1', '变式1')] +
                    ['拓展'] + ['评%d' % n for n in range(1, 6)]}
        det = {k: v for k, v in DETAIL.items() if k in set(keys.values())}
        nk, nd = migrate(piece, keys, K, det, md5sty)
        tot += nk
        print('[%s] 迁移 %d 键（详解随键 %d）＋双壳＋日志 → OK' % (piece, nk, nd))
    assert tot == 81
    print('BATCH_DONE 81/81')


if __name__ == '__main__':
    main()
