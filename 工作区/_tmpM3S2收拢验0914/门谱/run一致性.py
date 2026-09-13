# -*- coding: utf-8 -*-
"""M3 S2 波1 收拢验·跨片一致性审计（组头/页脚/序位/双档形态/值台账/sty md5/CJK审计/回流死律/图债/多选门/括线判模）。
只读 成卷/导学件；输出落 工作区/_tmpM3S2收拢验0914/门谱/一致性审计.json＋.md。零 git。
"""
import glob, hashlib, io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'C:/提示词'
DJJ = os.path.join(ROOT, '工作区', 'M3-第2章量产0913', '成卷', '导学件')
OUT = os.path.join(ROOT, '工作区', '_tmpM3S2收拢验0914', '门谱')
STY_MD5 = '7c3930362be8a0a2bdf21bbf8ac16573'
ORDER = ['衔接节', '课时01', '课时02', '课时03', '课时04', '课时05', '课时06', '课时06B',
         '课时07', '课时08', '课时09', '课时10', '课时11', '课时12', '课时13', '课时14',
         '课时15', '课时16', '课时17', '课时18', '课时19']
RE_CJK_AUDIT = re.compile(r'\\[a-zA-Z]+[\u3400-\u4dbf\u4e00-\u9fff]')  # 母版死律①：控制词直连 CJK（rg \p{Han} 同域）
RE_COMMENT = re.compile(r'(?<!\\)%.*$')

def piece_dir(pid):
    return [d for d in os.listdir(DJJ) if d == pid or d.startswith(pid + '-')][0]

rows, problems = [], []
for pid in ORDER:
    d = piece_dir(pid)
    pdir = os.path.join(DJJ, d)
    body = open(os.path.join(pdir, 'main.tex'), encoding='utf-8').read()
    tshell = open(os.path.join(pdir, 'main-true.tex'), encoding='utf-8').read()
    fshell = open(os.path.join(pdir, 'main-false.tex'), encoding='utf-8').read()
    mani = json.load(open(os.path.join(pdir, '件manifest.json'), encoding='utf-8'))
    led_path = glob.glob(os.path.join(pdir, '值台账-*.json'))[0]
    led = json.load(open(led_path, encoding='utf-8'))
    sty_md5 = hashlib.md5(open(os.path.join(pdir, 'qp-m3.sty'), 'rb').read()).hexdigest()

    r = dict(片=pid, 目录=d)
    r['sty_md5钉版'] = sty_md5 == STY_MD5
    # 页脚件名
    r['页脚章名'] = bool(re.search(r'\\renewcommand\{\\qpzhangming\}\{第二章\\quad 平面解析几何\}', body))
    r['页脚件名导学件'] = bool(re.search(r'\\renewcommand\{\\qpjianming\}\{导学件\}', body))
    # 组头（章头＋节头）
    m = re.search(r'\\zhangtitle\{([^}]*)\}', body)
    r['章头'] = m.group(1) if m else ''
    m = re.search(r'\\(jietitle|xjkeshi)\{([^}]*)\}', body)
    r['节头宏'] = m.group(1) if m else ''
    r['节头'] = m.group(2) if m else ''
    # 双档形态
    r['true壳mthreepure0'] = bool(re.search(r'\\def\\mthreepure\{0\}', tshell)) and '\\input{main.tex}' in tshell
    r['false壳mthreepure1'] = bool(re.search(r'\\def\\mthreepure\{1\}', fshell)) and '\\input{main.tex}' in fshell
    # 值台账键序 ≡ manifest 键序（序级）
    r['值台账≡manifest序'] = led.get('keys') == mani['冻结manifest键序']
    # CJK 审计（raw＋剔注释行两口径）
    cjk_raw = [(i + 1, l.strip()[:60]) for i, l in enumerate(body.splitlines()) if RE_CJK_AUDIT.search(l)]
    cjk_code = [(i + 1, l.strip()[:60]) for i, l in enumerate(body.splitlines())
                if RE_CJK_AUDIT.search(RE_COMMENT.sub('', l))]
    r['CJK审计raw命中'] = len(cjk_raw)
    r['CJK审计code命中'] = len(cjk_code)
    r['_cjk_code_detail'] = cjk_code[:5]
    # 回流死律
    r['newpage'] = len(re.findall(r'\\newpage', body))
    r['vbox'] = len(re.findall(r'\\vbox', body))
    r['ketangboxed'] = len(re.findall(r'ketangboxed', body))
    r['columnbreak'] = len(re.findall(r'\\columnbreak', body))
    # tailfill 恰1 且在 \end{multicols} 前
    tfs = [m.start() for m in re.finditer(r'\\tailfill', body)]
    em = body.find(r'\end{multicols}')
    r['tailfill数'] = len(tfs)
    r['tailfill在multicols前'] = len(tfs) == 1 and em != -1 and tfs[0] < em
    # 多选门（\duoxuan 出现次数 ≤4）
    r['duoxuan'] = len(re.findall(r'\\duoxuan', body))
    # 图债哨：如图／图债／待补图
    hits = [(i + 1, l.strip()[:70]) for i, l in enumerate(body.splitlines())
            if re.search(r'如图|图债|待补图|见右图|如下图', l)]
    r['图债哨'] = hits
    # 括线判模（值台账 items：est>8 必须 括线）
    nkey = ngray = nkuo = nbad = 0
    items = led.get('items') or {}
    for v in items:
        est = v.get('估高行数', v.get('est', None))
        mod = v.get('判模', v.get('模', ''))
        if est is None or mod == '':
            continue
        nkey += 1
        if mod == '括线':
            nkuo += 1
            if est is not None and est <= 8:
                nbad += 1
        else:
            ngray += 1
            if est is not None and est > 8:
                nbad += 1
    r['判模键数'] = nkey
    r['括线键'] = nkuo
    r['灰底键'] = ngray
    r['判模违例'] = nbad
    rows.append(r)
    bad = []
    if not r['sty_md5钉版']:
        bad.append('sty_md5漂移')
    if not (r['页脚章名'] and r['页脚件名导学件']):
        bad.append('页脚异')
    if not (r['true壳mthreepure0'] and r['false壳mthreepure1']):
        bad.append('双档壳异')
    if not r['值台账≡manifest序']:
        bad.append('值台账键序漂')
    if r['CJK审计code命中'] > 0:
        bad.append('CJK死律命中%d' % r['CJK审计code命中'])
    if r['newpage'] or r['vbox'] or r['ketangboxed']:
        bad.append('回流死律')
    if not r['tailfill在multicols前']:
        bad.append('tailfill位异')
    if r['duoxuan'] > 4:
        bad.append('多选门破')
    if r['判模违例']:
        bad.append('判模违例%d' % r['判模违例'])
    problems.extend((pid, b) for b in bad)

# 序位（节头序列）
print('＝序位（章头＋节头，canonical 序）＝')
for r in rows:
    print('%-7s %s｜%s %s' % (r['片'], r['章头'], r['节头宏'], r['节头']))

print('\n＝逐片一致性读数＝')
for r in rows:
    print('%-7s sty%s 页脚%s 壳%s 台账%s CJKraw%d/code%d np%d vbox%d kboxed%d colbr%d tailfill%d(位%s) duoxuan%d 判模%d(括%d/灰%d/违%d) 图债哨%d'
          % (r['片'], '√' if r['sty_md5钉版'] else '×', '√' if (r['页脚章名'] and r['页脚件名导学件']) else '×',
             '√' if (r['true壳mthreepure0'] and r['false壳mthreepure1']) else '×',
             '√' if r['值台账≡manifest序'] else '×', r['CJK审计raw命中'], r['CJK审计code命中'],
             r['newpage'], r['vbox'], r['ketangboxed'], r['columnbreak'], r['tailfill数'],
             '√' if r['tailfill在multicols前'] else '×', r['duoxuan'], r['判模键数'], r['括线键'], r['灰底键'],
             r['判模违例'], len(r['图债哨'])))

print('\n＝问题清单＝')
print('\n'.join('%s：%s' % p for p in problems) or '无')

json.dump(rows, open(os.path.join(OUT, '一致性审计.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
# 图债哨明细落盘
det = [(r['片'], h) for r in rows for h in r['图债哨']]
with open(os.path.join(OUT, '图债哨明细.txt'), 'w', encoding='utf-8') as fh:
    for pid, (ln, t) in det:
        fh.write('%s main.tex:%d %s\n' % (pid, ln, t))
print('\n图债哨总命中：%d 处' % len(det))
