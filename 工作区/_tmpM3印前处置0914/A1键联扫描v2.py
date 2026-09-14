# -*- coding: utf-8 -*-
"""A1 键联扫描 v2：标签对读＋无N片的 tjdnr→zsd 域映射判定＋错位行证据摘录。只读。"""
import difflib, io, json, os, re, sys
from collections import OrderedDict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
ORDER = ['衔接节'] + ['课时%02d' % i for i in range(1, 20)] + ['课时06B']
NCN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6}
ICN = {v: k for k, v in NCN.items()}


def pdir(tree, pid):
    base = os.path.join(CJ, tree)
    for d in os.listdir(base):
        if d == pid or d.startswith(pid + '-'):
            return os.path.join(base, d)
    raise SystemExit(pid)


def skip_ws(s, i):
    while i < len(s) and s[i] in ' \t\r\n':
        i += 1
    return i


def brace_group(s, i):
    d, j, buf = 0, i, []
    while j < len(s):
        c = s[j]
        if c == '\\' and j + 1 < len(s):
            buf.append(c); buf.append(s[j + 1]); j += 2; continue
        if c == '{':
            d += 1
            if d > 1:
                buf.append(c)
        elif c == '}':
            d -= 1
            if d == 0:
                return ''.join(buf), j + 1
            buf.append(c)
        else:
            buf.append(c)
        j += 1
    raise ValueError('brace')


def parse_args(s, i, n):
    args = []
    for _ in range(n):
        i = skip_ws(s, i)
        g, i = brace_group(s, i)
        args.append(g)
    return args, i


def norm(t):
    t = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?', '', t)
    t = re.sub(r'[\\\$\{\}]', '', t)
    for a, b in (('（', '('), ('）', ')'), ('，', ','), ('．', '.'), ('、', ','), ('：', ':'), ('　', ''), (' ', ''), ('\u3000', '')):
        t = t.replace(a, b)
    return t


def parse_practice(src):
    out, positions = [], [(m.start(), m.group(1)) for m in re.finditer(r'\\tihao\{(\d+)\}', src)]
    for k, (pos, num) in enumerate(positions):
        end = positions[k + 1][0] if k + 1 < len(positions) else len(src)
        seg = src[pos:end]
        mt = re.search(r'\\tieside\{([^}]*)\}', seg)
        mk = re.search(r'\\begin\{ansblock\}\[([^\]]+)\]', seg)
        body = seg[mt.end():] if mt else seg
        body = re.split(r'\\(bindopt|lxopt|liubai|kongda|begin\{ansblock\}|par\b)', body)[0]
        out.append(dict(num=int(num), label=mt.group(1) if mt else '', key=mk.group(1) if mk else None,
                        body=norm(body)[:110]))
    return out


def parse_guide(src):
    out, spots = [], []
    for mac in ('\\tjdnr', '\\liB', '\\jiancestem'):
        for m in re.finditer(re.escape(mac) + r'(?![a-zA-Z])', src):
            spots.append((m.start(), mac))
    spots.sort()
    sec, title = '', ''
    for k, (pos, mac) in enumerate(spots):
        end = spots[k + 1][0] if k + 1 < len(spots) else len(src)
        if mac == '\\jiancestem':
            mk = re.search(r'\\begin\{ansblock\}\[([^\]]+)\]', src[pos:end])
            mm = re.search(r'\\tieside\{([^}]*)\}', src[pos:pos + 400])
            out.append(dict(seat='检%d' % (k + 1), label=mm.group(1) if mm else '', key=mk.group(1) if mk else None,
                            sec=sec, title=title, body=''))
            continue
        nargs = 5 if mac == '\\tjdnr' else 4
        try:
            args, after = parse_args(src, skip_ws(src, pos + len(mac)), nargs)
        except (ValueError, AssertionError):
            continue
        if mac == '\\tjdnr':
            sec, title = args[0], args[1]
            seat, label, body = args[2], args[3], args[4]
        else:
            seat, label, body = args[0], args[1], args[3]
        seat = re.sub(r'\\textbf|[\s{}]', '', seat)
        mk = re.search(r'\\begin\{ansblock\}\[([^\]]+)\]', src[after:end])
        out.append(dict(seat=seat, label=label, key=mk.group(1) if mk else None,
                        sec=sec, title=title, body=norm(body)[:110]))
    return out


def nof(label):
    m = re.search(r'知识点([一二三四五六])', label)
    return NCN[m.group(1)] if m else None


report = OrderedDict()
for pid in ORDER:
    prac = parse_practice(open(os.path.join(pdir('练习件', pid), 'main.tex'), encoding='utf-8').read())
    guide = parse_guide(open(os.path.join(pdir('导学件', pid), 'main.tex'), encoding='utf-8').read())
    gmap = {g['key']: g for g in guide if g['key']}
    zsd = re.findall(r'\\zsd\{([一二三四五六])\}\{([^}]*)\}',
                     open(os.path.join(pdir('导学件', pid), 'main.tex'), encoding='utf-8').read())
    rows = []
    for p in prac:
        g = gmap.get(p['key'])
        pn = nof(p['label'])
        row = dict(num=p['num'], plabel=p['label'], pn=pn, key=p['key'], pbody=p['body'])
        if g is None:
            row.update(kind='无匹配', glabel='', gn=None, gsec='', gtitle='', gbody='')
        else:
            gn = nof(g['label'])
            row.update(glabel=g['label'], gn=gn, gsec=g['sec'], gtitle=g['title'], gbody=g['body'],
                       sim=round(difflib.SequenceMatcher(None, p['body'][:60], g['body'][:60]).ratio(), 2))
            if gn is None:
                row.update(kind='导无N')
            elif pn is None:
                row.update(kind='练无N')
            elif pn == gn:
                row.update(kind='符')
            else:
                row.update(kind='错位')
        rows.append(row)
    report[pid] = dict(zsd=zsd, rows=rows)

with open(r'C:/提示词/工作区/_tmpM3印前处置0914/A1扫描v2.txt', 'w', encoding='utf-8') as f:
    for pid, rep in report.items():
        n_bad = sum(1 for r in rep['rows'] if r['kind'] == '错位')
        n_non = sum(1 for r in rep['rows'] if r['kind'] == '导无N')
        f.write('== %s  错位%d 导无N%d  zsd=%s\n' % (pid, n_bad, n_non,
                '；'.join(a + '=' + b for a, b in rep['zsd']) or '无'))
        for r in rep['rows']:
            if r['kind'] in ('错位', '导无N', '无匹配', '练无N'):
                f.write('  题%-2d [%s] 练N=%s 导=%s(%s,%s) sim=%s\n    练:%s\n    导:%s\n' % (
                    r['num'], r['kind'], r.get('pn'), r.get('glabel', ''), r.get('gsec', ''),
                    r.get('gtitle', '')[:12], r.get('sim', '-'), r['pbody'][:70], r.get('gbody', '')[:70]))
print('done → A1扫描v2.txt')
for pid, rep in report.items():
    kinds = [r['kind'] for r in rep['rows']]
    print('%-5s 错位%d 导无N%d 符%d 无匹配%d' % (pid, kinds.count('错位'), kinds.count('导无N'),
          kinds.count('符'), kinds.count('无匹配')))
