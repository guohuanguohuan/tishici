# 批5b 图位对账：TSV ↔ 件内 figs/ 实文件（存在＋md5）＋ main.tex 引用 ↔ figs/ 文件双向清点
import os, re, hashlib

BASE = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷"
TSV = r"C:\提示词\工作区\_tmpP1成卷0912\批5b\_图提取台账.tsv"
DMAP = {'拓': '拓展册', '测': '测评卷'}
EXTS = ('.png', '.jpg', '.jpeg')


def md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()[:8]


rows, bad, notes = 0, [], []
for line in open(TSV, encoding='utf-8'):
    c = line.rstrip('\n').split('\t')
    if len(c) != 7 or c[0] not in DMAP or not c[1].lower().endswith(EXTS):
        notes.append(line.strip()[:70])
        continue
    rows += 1
    k, fn, src, media, wh, typ, m = c
    p = os.path.join(BASE, DMAP[k], 'figs', fn)
    if not os.path.exists(p):
        bad.append(('缺文件', p))
    elif md5(p) != m:
        bad.append(('md5不符', p, md5(p), m))

print('TSV 数据行 %d ／ 异常 %d ／ 注记行 %d' % (rows, len(bad), len(notes)))
for b in bad:
    print('  !', b)
for t in notes:
    print('  #', t)

pat = re.compile(r'\\qpfig(?:\[[^\]]*\])?\{([^}]*)\}')
for k, d in DMAP.items():
    tex = open(os.path.join(BASE, d, 'main.tex'), encoding='utf-8').read()
    refs = [m for m in pat.findall(tex)]
    files = sorted(f for f in os.listdir(os.path.join(BASE, d, 'figs')) if f.lower().endswith(EXTS))
    stems = {os.path.splitext(f)[0]: f for f in files}
    miss = [r for r in refs if r not in stems]
    unused = [f for s, f in stems.items() if s not in refs]
    print('%s：\\qpfig 引用 %d 处（去重 %d）／figs 文件 %d ／缺图 %s ／未引用 %s'
          % (d, len(refs), len(set(refs)), len(files), miss or '无', unused or '无'))
