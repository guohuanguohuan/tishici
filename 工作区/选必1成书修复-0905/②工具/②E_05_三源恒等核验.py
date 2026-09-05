# -*- coding: utf-8 -*-
"""②E_05_三源恒等核验.py — 盖章实测 vs 预期底稿 逐件对账＋节页码实测复核＋同串落账。
①解析 报告/②E_盖章记录.md（权威实测）与 报告/预期盖章记录_②E.md（②-D 权威页数推算）逐件对页数/start/N；
②重跑 节页码定位 @parts_②E.json --record 实测记录 --json → 节页码_②E.json（COM面实测）；
  与预期版逐节对 in_page（页内定位与盖章无关，应全等）、对 part_page（随 start）；
③逐件读 zip 页眉页脚可见串落账（（共N页）·本n/共M本/PAGE缓存=start）。
预期全等则 ①的册目录/装订单（预期版输入）即定版；否则打印 DRIFT 提示全链重造。证据：报告/②E_05_三源恒等.md"""
import sys, io, os, re, json, zipfile, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RPT = os.path.join(HERE, '报告')
DST = os.path.join(HERE, '副本_②E')

ROW = re.compile(r'\| P(\d+) \| 本(\d+) \| (.+?) \| (\d+) \| (\d+) \| (.+?) \| (\d+) \|')
def parse(p):
    d = {}
    for ln in open(p, encoding='utf-8'):
        m = ROW.match(ln.strip())
        if m:
            d[m.group(3)] = (int(m.group(4)), int(m.group(5)), int(m.group(7)))
    return d

act = parse(os.path.join(RPT, '②E_盖章记录.md'))
exp = parse(os.path.join(RPT, '预期盖章记录_②E.md'))
assert len(act) == 10 and len(exp) == 10
rows, drift = [], []
for k in sorted(act):
    a, e = act[k], exp[k]
    hit = a == e
    if not hit:
        drift.append(k)
    rows.append('| %s | 页%d/start%d/N%d | 页%d/start%d/N%d | %s |'
                % (k[:18], a[0], a[1], a[2], e[0], e[1], e[2], 'PASS' if hit else '!!DRIFT'))
    print('  %-18s 实测 页%d start%d N%d | 预期 页%d start%d N%d %s'
          % (k[:18], a[0], a[1], a[2], e[0], e[1], e[2], 'PASS' if hit else '!!DRIFT'))
print('盖章实测 vs 预期底稿：10件 %s' % ('全等（册目录/装订单预期版即定版）' if not drift else '漂移件=%s → 全链重造' % drift))

# ② 节页码定位（实测 start）
r = subprocess.run([sys.executable, os.path.join(ROOT, '工具', '节页码定位.py'),
                    '@' + os.path.join(HERE, 'parts_②E.json'),
                    '--record', os.path.join(RPT, '②E_盖章记录.md'), '--json'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace',
                   timeout=1200, cwd=ROOT)
print('节页码定位（实测start）exit=%d' % r.returncode)
assert r.returncode == 0, (r.stderr or '')[:600]
open(os.path.join(RPT, '节页码_②E.json'), 'w', encoding='utf-8').write(r.stdout)
loc_act = json.loads(r.stdout)
loc_exp = json.load(open(os.path.join(RPT, '节页码_②E_预期.json'), encoding='utf-8'))
sec_rows, sec_bad = [], 0
fa = {f['name']: f for f in loc_act['files']}
fe = {f['name']: f for f in loc_exp['files']}
assert set(fa) == set(fe)
for name in fa:
    sa = {(s['no']): (s['in_page'], s['part_page']) for s in fa[name]['sections']}
    se = {(s['no']): (s['in_page'], s['part_page']) for s in fe[name]['sections']}
    assert set(sa) == set(se), name
    for no in sorted(sa):
        ia, pa = sa[no]; ie, pe = se[no]
        ok_pg = (ia == ie)
        ok_pp = (pa == pe)
        if not (ok_pg and ok_pp):
            sec_bad += 1
        sec_rows.append('| %s | %s | %d/%d | %d/%d | %s |' % (name[:16], no, ia, ie, pa, pe,
                        'PASS' if (ok_pg and ok_pp) else '!!'))
nsec = len(sec_rows)
print('节级对账：%d 节，in_page 全等=%s、part_page 全等=%s（bad=%d）'
      % (nsec, all('PASS' in r for r in sec_rows), sec_bad == 0, sec_bad))
assert sec_bad == 0

# ③ 同串落账（副本十件 zip 页眉+页脚可见串＋PAGE缓存）
HF = []
import zipfile as zf
for full in sorted(act):
    z = zf.ZipFile(os.path.join(DST, full))
    names = z.namelist()
    h = [n for n in names if re.fullmatch(r'word/header\d+\.xml', n)][0]
    f = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)][0]
    def vis(nm):
        x = z.read(nm).decode('utf-8')
        return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', x))
    hv, fv = vis(h), vis(f)
    d = z.read('word/document.xml').decode('utf-8')
    st = re.findall(r'<w:pgNumType w:start="(\d+)"/>', d)
    z.close()
    ok_form = bool(re.fullmatch(r'(.+)（共(\d+)页）·本(\d+)/共(\d+)本　(.+)　第(\d+)页', hv))
    HF.append('| %s | %s | start域=%s | %s |' % (full[:28], fv[:46], st, '串形OK' if ok_form else '!!串形异常'))
    print('  %-28s %s start域=%s' % (full[:28], fv[:46], st))

allok = (not drift) and sec_bad == 0 and all('串形OK' in r for r in HF)
with open(os.path.join(RPT, '②E_05_三源恒等.md'), 'w', encoding='utf-8') as fo:
    fo.write('# ②-E 三源恒等核验（盖章实测 vs 预期底稿 vs 节页码实测）\n\n'
             '## 一、逐件对账（页数/start/N）\n\n| 件 | 实测 | 预期 | 判定 |\n|---|---|---|---|\n'
             + '\n'.join(rows) + '\n\n'
             + ('结论：十件全等——册目录页/装订单/节页码（预期版底稿）即定版。\n\n' if not drift
                else '结论：DRIFT=%s → 须以实测记录重造 01/02/03。\n\n' % drift)
             + '## 二、节页码实测复跑对账（in_page 应与预期版全等：节定位与盖章无关）\n\n| 件 | 节 | in_page 实/预 | part_page 实/预 | 判定 |\n|---|---|---|---|---|\n'
             + '\n'.join(sec_rows) + '\n\n'
             + '## 三、同串落账（副本十件页脚可见串）\n\n| 件 | 页脚同串 | document start域 | 判定 |\n|---|---|---|---|\n'
             + '\n'.join(HF) + '\n')
print('SUMMARY_05_ALLOK=%s' % allok)
sys.exit(0 if allok else 2)
