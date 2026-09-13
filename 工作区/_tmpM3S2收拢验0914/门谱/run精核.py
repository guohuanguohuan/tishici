# -*- coding: utf-8 -*-
"""M3 S2 波1 收拢验·一致性精核（剔注释重计＋图债映射到键＋判模违例分型）。零 git，只读成卷。"""
import glob, io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:/提示词'
DJJ = os.path.join(ROOT, '工作区', 'M3-第2章量产0913', '成卷', '导学件')
OUT = os.path.join(ROOT, '工作区', '_tmpM3S2收拢验0914', '门谱')
ORDER = ['衔接节', '课时01', '课时02', '课时03', '课时04', '课时05', '课时06', '课时06B',
         '课时07', '课时08', '课时09', '课时10', '课时11', '课时12', '课时13', '课时14',
         '课时15', '课时16', '课时17', '课时18', '课时19']
RE_COMMENT = re.compile(r'(?<!\\)%.*$')

def piece_dir(pid):
    return [d for d in os.listdir(DJJ) if d == pid or d.startswith(pid + '-')][0]

print('＝A. 剔注释重计（回流死律/尾块/多选）＝')
for pid in ORDER:
    d = piece_dir(pid)
    body = open(os.path.join(DJJ, d, 'main.tex'), encoding='utf-8').read()
    lines = body.splitlines()
    code = [RE_COMMENT.sub('', l) for l in lines]
    codej = '\n'.join(code)
    vbox = len(re.findall(r'\\vbox', codej))
    newpage = len(re.findall(r'\\newpage', codej))
    kboxed = len(re.findall(r'ketangboxed', codej))
    colbr = len(re.findall(r'\\columnbreak', codej))
    tfs = [m.start() for m in re.finditer(r'\\tailfill', codej)]
    em = codej.find(r'\end{multicols}')
    duox = len(re.findall(r'\\duoxuan', codej))
    fanxi = len(re.findall(r'\\fanxi', codej))
    print('%-7s vbox%d newpage%d kboxed%d colbr%d tailfill%d(位%s) duoxuan%d fanxi%d'
          % (pid, vbox, newpage, kboxed, colbr, len(tfs),
             '√' if (len(tfs) == 1 and em != -1 and tfs[0] < em) else '×', duox, fanxi))

print('\n＝B. 图债哨映射到键（剔注释；键＝命中行后首个 ansblock 键）＝')
for pid in ORDER:
    d = piece_dir(pid)
    lines = open(os.path.join(DJJ, d, 'main.tex'), encoding='utf-8').read().splitlines()
    hits = []
    for i, l in enumerate(lines):
        if RE_COMMENT.sub('', l) and re.search(r'如图|图债|待补图|图嵌|数值未回', l):
            key = ''
            for l2 in lines[i:]:
                m = re.search(r'\\begin\{ansblock\}\[([^\]]+)\]', RE_COMMENT.sub('', l2))
                if m:
                    key = m.group(1)
                    break
            hits.append((i + 1, key, re.search(r'如图|图债|待补图|图嵌|数值未回', l).group(0), l.strip()[:58]))
    if hits:
        print('《%s》' % pid)
        for ln, key, w, t in hits:
            print('  :%d %s [%s] %s' % (ln, w, key, t))

print('\n＝C. 判模分型精核（灰底est>8＝真违例；括线est≤8＝登记·括线合法形态）＝')
for pid in ORDER:
    d = piece_dir(pid)
    led = json.load(open(glob.glob(os.path.join(DJJ, d, '值台账-*.json'))[0], encoding='utf-8'))
    items = led.get('items') or []
    gray_over, kuo_under = [], []
    for v in items:
        est = v.get('估高行数')
        mod = v.get('判模', '')
        if est is None or not mod:
            continue
        if mod == '灰底' and est > 8:
            gray_over.append((v.get('键'), est))
        if mod == '括线' and est <= 8:
            kuo_under.append((v.get('键'), est, v.get('渲染注记', '')[:30]))
    if gray_over or kuo_under:
        print('《%s》 灰底est>8：%s｜括线est≤8：%s' % (pid, gray_over, kuo_under))
