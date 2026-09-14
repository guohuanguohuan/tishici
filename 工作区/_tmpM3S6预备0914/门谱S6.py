# -*- coding: utf-8 -*-
"""S6 销案·门谱复跑（导学件 02/03/10/14/16/17）：
对号门 --strict 全量＋槽宽门双档×6＋键账对平门×6＋件面审计（值快照/ansitem号序/CJK/死律/
tailfill/sty锁/ANSKEY逐位）。输出落本目录 门谱S6/。零 git。门工具自身只读。
"""
import io, json, os, re, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'C:/提示词'
M3 = os.path.join(ROOT, '工作区', 'M3-第2章量产0913', '成卷')
TMUB = os.path.join(M3, '题面库')
HERE = os.path.join(ROOT, '工作区', '_tmpM3S6预备0914')
OUT = os.path.join(HERE, '门谱S6')
os.makedirs(OUT, exist_ok=True)

PIECES = ['课时02', '课时03', '课时10', '课时14', '课时16', '课时17']
STY_MD5_LOCK = '7c3930362be8a0a2bdf21bbf8ac16573'
# 值面转写基线（0914 S6 快照对照实证：改前快照同法抽取差集与此全等＝存量已注册转写，非本轮引入）
BASELINE_TRANS = {'2章-拓-课时02-T2', '2章-拓-课时17-04'}
BAD_ATOMS = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
             '\\ketangboxed', '\\columnbreak', '\\eject', '\\vfill', '\\fanxi']
RE_INLINE = re.compile(r'(?<!\\)%.*$')


def gdir(pid):
    base = os.path.join(M3, '导学件')
    for d in os.listdir(base):
        if d == pid or d.startswith(pid + '-'):
            return os.path.join(base, d)
    raise SystemExit(pid)


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True)
    return p.returncode, (p.stdout or b'').decode('utf-8', 'replace') + (
        '\n[stderr] ' + (p.stderr or b'').decode('utf-8', 'replace') if (p.stderr or b'').strip() else '')


R = []
# ① 对号门 --strict（题面库全量＝零漂形式闸）
rc, out = run([sys.executable, os.path.join(TMUB, '对号门.py'), '--strict'])
open(os.path.join(OUT, '对号门-strict.txt'), 'w', encoding='utf-8').write(out)
tail = out.strip().splitlines()[-1] if out.strip() else ''
R.append(('对号门--strict', rc, tail))
print('① 对号门 --strict exit=%d｜%s' % (rc, tail), flush=True)


def find_brace(s, i):
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
    raise ValueError


audit = {}
for pid in PIECES:
    gd = gdir(pid)
    mani = json.load(open(os.path.join(TMUB, 'manifest', pid + '.manifest.json'), encoding='utf-8'))
    keyseq = mani['键序']
    led_file = [f for f in os.listdir(gd) if f.startswith('值台账') and f.endswith('.json')][0]

    # ② 槽宽门双档
    for mode in ('zero-fp', 'strict'):
        rc, out = run([sys.executable, os.path.join(ROOT, '工具', 'makebox槽宽门.py'), gd, '--mode', mode])
        open(os.path.join(OUT, '槽宽门-%s-%s.txt' % (mode, pid)), 'w', encoding='utf-8').write(out)
        last = [l for l in out.splitlines() if l.startswith('——') or l.startswith('[PASS') or l.startswith('[FAIL')]
        R.append(('槽宽门-%s-%s' % (mode, pid), rc, last[-1] if last else ''))

    # ③ 键账对平门
    kt = os.path.join(OUT, '键表-%s.txt' % pid)
    open(kt, 'w', encoding='utf-8').write('\n'.join(keyseq) + '\n')
    rc, out = run([sys.executable, os.path.join(ROOT, '工具', '键账对平门.py'),
                   '--ledger', '台账=' + os.path.join(gd, led_file),
                   '--piece', 'true档=' + os.path.join(gd, 'main-true.tex'),
                   '--piece', 'false档=' + os.path.join(gd, 'main-false.tex'),
                   '--expect', 'manifest键序=' + kt])
    open(os.path.join(OUT, '对平门-%s.txt' % pid), 'w', encoding='utf-8').write(out)
    last = [l for l in out.splitlines() if l.startswith('[PASS') or l.startswith('[FAIL')]
    R.append(('对平门-%s' % pid, rc, last[-1] if last else ''))

    # ④ 件面审计（导学件正口径：值链＝件面 ansitem ≡ 值台账 vals；答案侧字面转写差集另列基线对照）
    src = open(os.path.join(gd, 'main.tex'), encoding='utf-8').read()
    body = '\n'.join((l if not l.lstrip().startswith('%') else '') for l in src.split('\n'))
    body = RE_INLINE.sub('', body)
    led = json.load(open(os.path.join(gd, led_file), encoding='utf-8'))
    ledger_vals = led['vals']
    side_raw = open(os.path.join(TMUB, mani['答案侧']), encoding='utf-8').read()
    side = dict(re.findall(r'^%[ \t]*ans:(\S+)\s*\n值：(.*)$', side_raw, re.M))
    tex_vals, cur = {}, None
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
            tex_vals[cur], _ = find_brace(ls, ma.end() - 1)
    norm = lambda s: s.replace('\\{', '{').replace('\\}', '}')
    drift = [k for k in keyseq if norm(tex_vals.get(k) or '') != norm(ledger_vals.get(k) or '')]
    trans = sorted(k for k in keyseq if norm(tex_vals.get(k) or '') != norm(side.get(k) or ''))
    a = {}
    a['值快照漂移（件面vs台账）'] = drift
    a['答案侧字面转写差集'] = trans
    seq = [int(n) for n in re.findall(r'\\ansitem\{(\d+)\}\{', src)]
    a['ansitem号序'] = seq
    a['CJK命中'] = len(re.findall(r'\\[a-zA-Z]+[\u4e00-\u9fff]', src))
    a['死律'] = {w: body.count(w) for w in BAD_ATOMS}
    a['tailfill'] = len(re.findall(r'\\tailfill(?![a-zA-Z])', body))
    a['sty_md5合锁'] = __import__('hashlib').md5(open(os.path.join(gd, 'qp-m3.sty'), 'rb').read()).hexdigest() == STY_MD5_LOCK
    log = open(os.path.join(gd, 'main-true.log'), encoding='utf-8', errors='replace').read()
    keys_t = re.findall(r'^M3-ANSKEY: (\S+)', log, re.M)
    logf = open(os.path.join(gd, 'main-false.log'), encoding='utf-8', errors='replace').read()
    keys_f = re.findall(r'^M3-ANSKEY: (\S+)', logf, re.M)
    a['ANSKEY双档逐位'] = (keys_t == keys_f)
    a['ANSKEY键集全等manifest'] = (set(keys_t) == set(keyseq))
    audit[pid] = a
    bad = []
    new_drift = [k for k in drift if k not in BASELINE_TRANS]
    if new_drift:
        bad.append('值快照%s' % new_drift)
    if drift:
        print('  （%s 基线转写差集：%s——改前快照同在，承 S2 注册口径）' % (pid, drift))
    if seq != list(range(1, len(keyseq) + 1)):
        bad.append('号序末%s' % seq[-1] if seq else '号序空')
    if a['CJK命中']:
        bad.append('CJK%d' % a['CJK命中'])
    if any(a['死律'].values()):
        bad.append('死律')
    if a['tailfill'] != 1:
        bad.append('tailfill%d' % a['tailfill'])
    if not a['sty_md5合锁']:
        bad.append('sty')
    if not (a['ANSKEY双档逐位'] and a['ANSKEY键集全等manifest']):
        bad.append('ANSKEY')
    R.append(('审计-%s' % pid, 1 if bad else 0, '；'.join(bad) or '全绿'))
    print('④ %s 审计：%s' % (pid, '；'.join(bad) or '全绿'), flush=True)

lines = ['＝＝ S6 印前销案·门谱复跑汇总（导学件 02/03/10/14/16/17）＝＝']
nbad = 0
for name, rc, tail in R:
    if rc != 0:
        nbad += 1
    lines.append('[%s] exit=%d｜%s｜%s' % ('PASS' if rc == 0 else 'FAIL', rc, name, tail))
lines.append('合计：%d 项门跑，%d 项非零/有旗' % (len(R), nbad))
open(os.path.join(OUT, '门谱汇总S6.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
json.dump(audit, open(os.path.join(OUT, '审计S6.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n'.join(lines[-4:]))
