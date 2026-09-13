# -*- coding: utf-8 -*-
"""M3 S3 全收验·跨片一致性审计（21 片）＋值快照逐字＋件型纪律＋图债哨＋降档登记收拢。
照 S2 收拢验制 run一致性.py 改造：对象＝成卷/练习件 21 片。
只读 成卷；输出仅落 工作区/_tmpM3S3全收验0914/门谱/。零 git。
"""
import hashlib, io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'C:/提示词'
M3 = os.path.join(ROOT, '工作区', 'M3-第2章量产0913', '成卷')
LXJ = os.path.join(M3, '练习件')
TMUB = os.path.join(M3, '题面库')
MENPU = os.path.join(ROOT, '工作区', '_tmpM3S3全收验0914', '门谱')

STY_MD5_LOCK = '7c3930362be8a0a2bdf21bbf8ac16573'
ORDER = ['衔接节'] + ['课时%02d' % i for i in range(1, 20)] + ['课时06B']
BAD_ATOMS = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
             '\\ketangboxed', '\\columnbreak', '\\eject', '\\vfill', '\\fanxi']
RE_CJK = re.compile(r'\\[a-zA-Z]+[\u4e00-\u9fff]')   # 控制词直连 CJK（rg \p{Han} 同义，标准 re 用码段）
RE_INLINE = re.compile(r'(?<!\\)%.*$')

def piece_dir(pid):
    for d in os.listdir(LXJ):
        if d == pid or d.startswith(pid + '-'):
            return d
    raise SystemExit(pid)

def md5f(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def braces(s, i):
    d, j = 0, i
    while j < len(s):
        if s[j] == '\\' and j + 1 < len(s):
            j += 2
            continue
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[i + 1:j], j
        j += 1
    raise ValueError('花括号不配平')

audit = {}
reds = []
for pid in ORDER:
    d = piece_dir(pid)
    pdir = os.path.join(LXJ, d)
    a = {}
    mani = json.load(open(os.path.join(TMUB, 'manifest', pid + '.manifest.json'), encoding='utf-8'))
    keyseq = [k for k in mani['键序'] if k.startswith('2章-练-')]
    a['manifest练键数'] = len(keyseq)

    # ① sty md5 ＋台账 toolchain锁
    a['sty_md5'] = md5f(os.path.join(pdir, 'qp-m3.sty'))
    led_file = [f for f in os.listdir(pdir) if f.startswith('值台账') and f.endswith('.json')]
    assert len(led_file) == 1
    led = json.load(open(os.path.join(pdir, led_file[0]), encoding='utf-8'))
    lock = led.get('toolchain锁', {})
    a['sty_md5_合锁'] = (a['sty_md5'] == STY_MD5_LOCK)
    a['台账锁字段'] = (lock.get('md5', lock.get('file_md5', '')) == STY_MD5_LOCK) if isinstance(lock, dict) else (STY_MD5_LOCK in str(lock))

    # ② 双档壳
    st = open(os.path.join(pdir, 'main-true.tex'), encoding='utf-8').read()
    sf = open(os.path.join(pdir, 'main-false.tex'), encoding='utf-8').read()
    a['壳true'] = bool(re.search(r'^\\def\\mthreepure\{0\}', st, re.M)) and '\\input{main.tex}' in st
    a['壳false'] = bool(re.search(r'^\\def\\mthreepure\{1\}', sf, re.M)) and '\\input{main.tex}' in sf

    # ③ 组头／页脚／序位
    src = open(os.path.join(pdir, 'main.tex'), encoding='utf-8').read()
    m = re.search(r'\\(keshi|xjkeshi)\{([^}]*)\}', src)
    a['组头宏'] = m.group(1) if m else '缺'
    a['组头文'] = m.group(2) if m else '缺'
    a['页脚章'] = (re.search(r'\\renewcommand\{\\qpzhangming\}\{([^}]*)\}', src) or [None, '缺'])[1] if re.search(r'\\renewcommand\{\\qpzhangming\}\{([^}]*)\}', src) else '缺'
    a['页脚册'] = (re.search(r'\\renewcommand\{\\qpjianming\}\{([^}]*)\}', src) or [None, '缺'])[1] if re.search(r'\\renewcommand\{\\qpjianming\}\{([^}]*)\}', src) else '缺'

    # ④ 值台账 keys 序级 ≡ manifest 练键序
    a['台账keys序级'] = (led.get('keys') == keyseq)
    a['台账vals键数'] = len(led.get('vals', {}))

    # ⑤ CJK catcode 审计（raw 全文含注释行）
    a['CJK命中'] = len(RE_CJK.findall(src))

    # ⑥ 回流死律（剔注释）
    body = '\n'.join((l if not l.lstrip().startswith('%') else '') for l in src.split('\n'))
    body = RE_INLINE.sub('', body)
    a['死律'] = {w: body.count(w) for w in BAD_ATOMS}
    a['ketang'] = body.count('\\begin{ketang}')
    n_tail = len(re.findall(r'\\tailfill(?![a-zA-Z])', body))
    pos_tail = body.find('\\tailfill')
    pos_endmc = body.find('\\end{multicols}')
    a['tailfill'] = n_tail
    a['tailfill在end multicols前'] = (0 <= pos_tail < pos_endmc)

    # ⑦ 件型纪律计数 vs manifest/台账
    a['duoxuan_实'] = len(re.findall(r'\\duoxuan(?![a-zA-Z])', body))
    a['duoxuan_期望'] = mani['期望值']['多选数']
    slots = [it.get('槽型', '') for it in led.get('items', [])]
    a['解答题数_台账'] = sum(1 for s in slots if '解答' in s)
    a['liubai_实'] = len(re.findall(r'\\liubai(?![a-zA-Z])', body))
    a['liubai高'] = re.findall(r'\\liubai\[([0-9.]+mm)\]', body)
    a['填空数_台账'] = sum(1 for s in slots if '填空' in s)
    a['kongda_实'] = len(re.findall(r'\\kongda(?![a-zA-Z])', body))

    # ⑧ 全线括线判模（件面）
    pre = src.split('\\begin{document}', 1)[0] if '\\begin{document}' in src else ''
    a['灰底导言恰1'] = len(re.findall(r'^\\ansblockgrayfalse\s*$', pre, re.M))
    a['灰底逐块包装'] = len(re.findall(r'\{\\ansblockgrayfalse', body))
    a['ansnote详解'] = len(re.findall(r'\\ansnote\{详解\}', src))

    # ⑨ 拓区隔离（件面）
    a['拓测滚G锚'] = sorted((set(re.findall(r'%\s*ans:(\S+)', src)) |
                          set(re.findall(r'\\begin\{ansblock\}\[([^\]]+)\]', src))) - set(keyseq))

    # ⑩ 值快照（字节级＋转义对归一）：ansitem 第二参 ≡ 答案侧值行
    #   （课时17-11 实证：件面 TeX 必需转义 \{ \}，值台账「值快照门 转义对归一在案」，
    #     与臂级判模同规：归一后逐字全等＝绿，归一不可消的漂移＝红）
    side_raw = open(os.path.join(TMUB, mani['答案侧']), encoding='utf-8').read()
    side = dict(re.findall(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', side_raw, re.M))

    def norm(s):
        return s.replace('\\{', '{').replace('\\}', '}')

    tex_vals = {}
    cur = None
    for ln in src.split('\n'):
        ls = ln.strip()
        if ls.startswith('%'):
            continue
        mb = re.match(r'\\begin\{ansblock\}\[([^\]]+)\]', ls)
        if mb:
            cur = mb.group(1)
            continue
        ma = re.search(r'\\ansitem\{(\d+)\}\{', ls)
        if ma and cur:
            tex_vals[cur], _ = braces(ls, ma.end() - 1)
    drift_raw = [k for k in keyseq if tex_vals.get(k) != side.get(k)]
    drift_norm = [k for k in keyseq if norm(tex_vals.get(k) or '') != norm(side.get(k) or '')]
    a['值快照漂移键raw'] = drift_raw
    a['值快照漂移键'] = drift_norm
    a['值快照转义对归一键'] = [k for k in drift_raw if k not in drift_norm]
    a['值快照对齐数'] = 16 - len(drift_norm)
    a['ansitem号序'] = [int(n) for n in re.findall(r'\\ansitem\{(\d+)\}\{', src)]

    # ⑪ 图债哨（台账字段＋件面占位扫描）
    a['图债台账'] = led.get('图债', '')
    occ = []
    for i, l in enumerate(src.split('\n'), 1):
        lb = RE_INLINE.sub('', l)
        if '如图' in lb or '〔图' in lb or '图嵌' in lb or '图债' in lb:
            occ.append(i)
    a['图债件面行'] = occ

    # ⑫ 降档登记收拢
    a['降档登记'] = led.get('降档登记', '')
    a['知识点预排注记'] = led.get('知识点预排注记', '')
    audit[pid] = a

# ---- 判红 ----
def flag(pid, k):
    a = audit[pid]
    bad = []
    if not a['sty_md5_合锁']: bad.append('sty_md5')
    if not a['台账锁字段']: bad.append('台账锁')
    if not a['壳true']: bad.append('壳true')
    if not a['壳false']: bad.append('壳false')
    if not a['台账keys序级']: bad.append('台账keys序级')
    if a['CJK命中'] != 0: bad.append('CJK%d' % a['CJK命中'])
    for w, n in a['死律'].items():
        if n != 0: bad.append('%s×%d' % (w, n))
    if a['ketang'] != 0: bad.append('ketang')
    if a['tailfill'] != 1 or not a['tailfill在end multicols前']: bad.append('tailfill位')
    if a['duoxuan_实'] != a['duoxuan_期望']: bad.append('duoxuan%d≠%d' % (a['duoxuan_实'], a['duoxuan_期望']))
    if a['liubai_实'] != a['解答题数_台账']: bad.append('liubai%d≠%d' % (a['liubai_实'], a['解答题数_台账']))
    for h in a['liubai高']:
        v = float(h[:-2])
        if not (16.0 <= v <= 40.0): bad.append('liubai高%s' % h)
    if a['kongda_实'] < 0 or a['kongda_实'] > 16: bad.append('kongda异常%d' % a['kongda_实'])
    # kongda＝逐空印答位（逐片登记制：T13 三空/T14 两空式逐空 kongda；
    # 求解型填空可零 kongda 走 ansitem 印答），无跨片不变量，只记数不判红。
    if a['灰底导言恰1'] != 1: bad.append('灰底导言%d' % a['灰底导言恰1'])
    if a['灰底逐块包装'] != 0: bad.append('灰底逐块%d' % a['灰底逐块包装'])
    if a['ansnote详解'] != 16: bad.append('ansnote%d' % a['ansnote详解'])
    if a['拓测滚G锚']: bad.append('外域锚%s' % a['拓测滚G锚'])
    if a['值快照漂移键']: bad.append('值快照漂移%s' % a['值快照漂移键'])
    if a['ansitem号序'] != list(range(1, 17)): bad.append('ansitem号序%s' % a['ansitem号序'])
    return bad

print('片        组头宏 组头文                                页脚(章/册)  锁  壳  台账序 CJK 死律 尾fill 多选 留白/印答 灰底 值快照 异常')
total_bad = 0
for pid in ORDER:
    a = audit[pid]
    bad = flag(pid, None)
    total_bad += len(bad)
    print(f"{pid:<8} {a['组头宏']:<3} {a['组头文'][:9]:<10} {str(a['页脚章'])[:3]}/{a['页脚册']} "
          f"{'√' if a['sty_md5_合锁'] and a['台账锁字段'] else 'X'} "
          f"{'√' if a['壳true'] and a['壳false'] else 'X'} "
          f"{'√' if a['台账keys序级'] else 'X'} CJK{a['CJK命中']} "
          f"{'死律0' if all(v == 0 for v in a['死律'].values()) else '死律红'} "
          f"尾{a['tailfill']} 多选{a['duoxuan_实']}/{a['duoxuan_期望']} "
          f"留白{a['liubai_实']} 印答{a['kongda_实']} 灰底{a['灰底导言恰1']} "
          f"值快照{a['值快照对齐数']}/16 {bad or '—'}")
    reds.extend(['%s:%s' % (pid, b) for b in bad])

# 组头序位核对
print('\n序位（物理目录序 vs 组头）：')
seq_ok = True
seen = []
for pid in ORDER:
    seen.append((pid, audit[pid]['组头宏'], audit[pid]['组头文']))
print('  ' + ' → '.join('%s(%s)' % (p, t[:14]) for p, _, t in seen))

json.dump({p: {k: v for k, v in a.items() if k != '降档登记'} for p, a in audit.items()},
          open(os.path.join(MENPU, '一致性审计.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
with open(os.path.join(MENPU, '降档登记收拢.txt'), 'w', encoding='utf-8') as f:
    for pid in ORDER:
        f.write('【%s】%s\n\n' % (pid, audit[pid]['降档登记']))
with open(os.path.join(MENPU, '图债哨明细.txt'), 'w', encoding='utf-8') as f:
    for pid in ORDER:
        f.write('【%s】台账：%s\n      件面占位行：%s\n' % (pid, audit[pid]['图债台账'] or '无', audit[pid]['图债件面行'] or '无'))

print('\n判红合计：%d（%s）' % (total_bad, reds or '无'))

# ---- ⑬ 在位 PDF 页数 vs 沙箱新编页数（在位件漂移哨） ----
try:
    import fitz
    fresh = {r['片']: (r['true页'], r['false页']) for r in json.load(
        open(os.path.join(ROOT, '工作区', '_tmpM3S3全收验0914', '复编', '复编读数.json'), encoding='utf-8'))}
    stale = []
    for pid in ORDER:
        d = piece_dir(pid)
        pdir = os.path.join(LXJ, d)
        inplace = []
        for tag in ('true', 'false'):
            fp = os.path.join(pdir, 'main-%s.pdf' % tag)
            doc = fitz.open(fp)
            inplace.append(doc.page_count)
            doc.close()
        if tuple(inplace) != fresh.get(pid):
            stale.append('%s 在位%s vs 新编%s' % (pid, tuple(inplace), fresh.get(pid)))
    print('在位PDF页数漂移哨：%s' % (stale or '21/21 全同（在位件＝新编稳态）'))
except Exception as e:
    print('在位PDF页数哨未跑：', e)
