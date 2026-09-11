# -*- coding: utf-8 -*-
r"""组装body.py —— 导学件答案册-v1 正文组装器（可重跑，非手抄）。

输入：
  ① C:\提示词\工作区\_tmp取证0909c\片G\去答案0911\答案册素材0911.txt
     ＝variantF/postproc_daoxue.py 6g 去答案0911 pass 移出块全量（tex 原样、按导学件题号分组）；
  ② C:\提示词\工作区\字替对照-0909\variantF\body.tex（去答后正文）——取【素养小结】①②③，
     供题型总结块（识别信号/通法步骤/易错点＝样张 0911 题型轮三件式，文案承小结原句）。
  ③ C:\提示词\工作区\_tmp取证0909c\片G\去答案0911\课前预习素材0911.txt
     ＝全品对齐0911 postproc 6h 素材（知识点填空 20 值＋诊断判断 6 答案/简析，G/K/J 制表符行）——「一、课前预习」节输入。
输出：本件 body.tex（课前预习＋答案/解析/详解/点睛 全量入册＋题型行/总结块按探究点·题型名组织）。
口径登记（简报§口径）：
  · v10 对齐0911＝全品式层级缩进（草案 §7.1 更正版／§7.6 像素实测：全品 p1 条目≈70px／内容·续行≈100px，
    净缩进≈30px≈1.4 字；替代 v8「全顶格」）：条目/标签行基左缘起排，内容与续行收一档 5.0mm（\qpind），
    「知识点N」标题居中（\kdhead）；题型行/题型总结三行＝内容行同收一档（qp-answ-blocks 同修）；
  · v10-C 课前预习填空串＝全品 p04 式：按知识点区条目分组「N．值 值…」、全角空格分隔、不逐空编号
    （条目↔空数映射＝解析 variantF body 知识点区 \kongbai 计数硬断言；顺序＝对号由分组保证）；
  · 同号对应＝例1/变式1（探究点一～九）＋课堂评价1～5；题型行＝探究点题名（导学增量块名）；
  · 移出行标签保形：[分析]/[详解]/[点睛]/[解析]（样张件无 [解析] 先例——变式/检测简析行标签照移，登记）；
  · 例题 [答案] 值：变式/检测取 \ansline 原值；例1 无独立答案行（去答前正文答案值在 [详解]/故答案行内）——
    由「故答案为/故选/取值范围是/夹角的大小为」模式反解＋两处钉值复核，逐题断言值非空；
  · 探二 g1／探九 g5 详解配图：并排/下置形随 [详解] 退册，册内改 \ansfig 题下居中（绝对路径引 variantF 原位图，
    不复制二进制）；悬挂深度探区 12.2mm（"变式1"标签宽档）／检测区 5.8mm（单号档＝样张 #22 口径）；
  · 起页＝1（独立册；样张全书连续 P75 系练习册装订档，不适用，登记）。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
MAT = r'C:/提示词/工作区/_tmp取证0909c/片I-裁5页码块0911/v11/_负测tmp/素材-回卷模拟.txt'
VFBODY = r'C:\提示词\工作区\字替对照-0909\variantF\body.tex'
MEDIA = 'C:/提示词/工作区/字替对照-0909/variantF/'   # 绝对 graphicsbase（禁复制字体/图像二进制）

tjseq = ['一', '二', '三', '四', '五', '六', '七', '八', '九']


def strip_outer(s, head):
    assert s.startswith(head + '{') and s.endswith('}'), s[:24] + '…'
    return s[len(head) + 1:-1]


def unansul(s):
    """剥 \ansul{…} 恒等包装（花括号计数，任意嵌套；旧正则版在 \frac 双层花括号处漏剥）。"""
    out, i = [], 0
    while True:
        j = s.find(r'\ansul{', i)
        if j < 0:
            out.append(s[i:])
            break
        out.append(s[i:j])
        k, d = j + len(r'\ansul{'), 1
        while d:
            if s[k] == '{':
                d += 1
            elif s[k] == '}':
                d -= 1
            k += 1
        out.append(unansul(s[j + len(r'\ansul{'):k - 1]))
        i = k
    return ''.join(out)


# ---------- ① 素材解析 ----------
raw = open(MAT, encoding='utf-8').read()
recs = {}                      # q -> dict(name, fen[], xj[], dj[], ans, jx, figs[], gu)
order = []
parts = re.split(r'^=+ (.+?)　\[(.*?)\] =+\s*$', raw, flags=re.M)
for q, name, body in zip(parts[1::3], parts[2::3], parts[3::3]):
    d = recs.setdefault(q, dict(name=name, fen=[], xj=[], dj=[], ans=None, jx=None, figs=[], gu=None))
    order.append(q)
    last_label = 'xj'          # 续段归属＝紧邻上一标签块（探六：[分析] 跨两段，方法2 行系分析续段非详解）
    for m in re.finditer(r'^--\[(.+?)\]--\n(.*?)(?=^--\[|^=+|\Z)', body, flags=re.M | re.S):
        kind, txt = m.group(1), m.group(2).rstrip('\n')
        if kind == '例[分析]':
            last_label = 'fen'
            d['fen'].append(txt.replace(r'\bindp [分析]', '', 1))
        elif kind == '例[详解]':
            last_label = 'xj'
            d['xj'].append(txt.replace(r'\bindp [详解]', '', 1))
        elif kind == '例[点睛]':
            d['dj'].append(txt.replace(r'\bindp [点睛]', '', 1))
        elif kind == '故答案行':
            d['gu'] = txt.replace(r'\bindp ', '', 1)
            d['xj'].append(d['gu'])
        elif kind == '[详解/分析]续段':
            txt2 = txt.replace(r'\bindp ', '', 1)
            d['fen' if last_label == 'fen' else 'xj'].append(txt2)
        elif kind == '例[详解]并排图文行':
            last_label = 'xj'
            mt = re.search(r'\\raggedright (.*?)\\end\{minipage\}', txt, flags=re.S)
            assert mt, q
            d['xj'].append(mt.group(1).replace('[详解]', '', 1).strip())
            mw = re.search(r'width=([\d.]+)mm,alt=\{@@@[^}]*\}\]\{([^}]+)\}', txt)
            assert mw, txt[:80]
            d['figs'].append((float(mw.group(1)), mw.group(2)))
        elif kind == '例[详解]配图行':
            mw = re.search(r'width=([\d.]+)mm\]\{([^}]+)\}', txt)
            assert mw, txt[:80]
            d['figs'].append((float(mw.group(1)), mw.group(2)))
        elif kind == '答案行':
            d['ans'] = unansul(strip_outer(txt, r'\ansline'))
        elif kind == '答案行(题5内联)':
            d['ans'] = unansul(txt)
        elif kind == '简析行[解析]':
            d['jx'] = strip_outer(txt, r'\jiexi')
        else:
            raise AssertionError('未知块型 ' + kind)

# ---------- ①a 钉值门（v11 勘误0911·防 postproc 6g 重跑回卷——不符即中止，禁静默再生） ----------
assert r'\sqrt{7}' in recs['探究点九·变式1']['ans'], \
    '钉值门触发：探九变式1 答案值缺 \\sqrt{7}（疑素材回卷旧值 √13/2），中止组装待人工处置'

# ---------- ①b 课前预习素材（全品对齐0911·postproc 6h 产出） ----------
PRE = r'C:\提示词\工作区\_tmp取证0909c\片G\去答案0911\课前预习素材0911.txt'
pre_groups = []                      # [组次, 知识点题名, [(序, 填空值)…], [(序号, 符号, 解析tex)…]]
for _ln in open(PRE, encoding='utf-8').read().splitlines():
    _f = _ln.split('\t')
    if _f[0] not in ('G', 'K', 'J'):      # 文件头两行注释（6h 说明行无 # 前缀）——跳过，完备性由末断言兜底
        continue
    if _f[0] == 'G':
        pre_groups.append([_f[1], _f[2], [], []])
    elif _f[0] == 'K':
        pre_groups[-1][2].append((int(_f[1]), _f[2]))
    else:
        pre_groups[-1][3].append((_f[1], _f[2], _f[3]))
assert len(pre_groups) == 3 and [len(g[2]) for g in pre_groups] == [11, 5, 4] \
    and [len(g[3]) for g in pre_groups] == [2, 2, 2], '课前预习素材分组不完整'


def _pre_entry_counts():
    r"""v10-C 分组依据：解析 variantF body 知识点区（\zsd 起、◆探究点前止），
    逐知识点给 [(\tiaomu 条目号, 该条 \kongbai 数)]；总数硬断言＝素材值数（11/5/4）。"""
    i0 = bt.index('\\zsd{')
    i1 = bt.index('\\tjdnr{一}')
    zone = bt[i0:i1]
    parts = re.split(r'\\zsd\{(.)\}\{([^}]*)\}', zone)
    groups = []
    for gi in range(1, len(parts), 3):
        seg = parts[gi + 2]
        ents = re.split(r'\\tiaomu[zt]?\{(\d+)\}', seg)
        counts = [(int(ents[ei]), ents[ei + 1].count('\\kongbai{}'))
                  for ei in range(1, len(ents), 2)]
        groups.append(counts)
    assert len(groups) == 3 and [sum(c for _n, c in g) for g in groups] == [11, 5, 4], \
        '知识点区条目填空数解析与素材不平（v10-C 分组失效）'
    return groups


def _pre_lines():
    r"""「一、课前预习」节（v10-B/C 全品式）：每知识点＝\kdhead 居中标题＋[答案]（填空按条目分组
    「N．值 值…」＋判断 (N)√× 另段——段段收一档）＋[解析]（逐条，多段）。不逐空编号，序＝对号。"""
    groups = _pre_entry_counts()
    L = []
    for (ci, name, ks, js), ents in zip(pre_groups, groups):
        L.append(r'\kdhead{知识点' + ci + '　' + name + r'}{填空' + str(len(ks)) + '空／判断'
                 + str(len(js)) + '题——序与导学件同}')
        paras, idx = [], 0
        for n, k in ents:
            if k == 0:
                continue
            paras.append('%d．' % n + '　'.join(v for _i, v in ks[idx:idx + k]))
            idx += k
        assert idx == len(ks), '填空值数与条目空数不平：' + ci
        paras.append('　'.join('%s%s' % (no, sy) for no, sy, _j in js))
        L.append(r'\ansline{答案}{%s}' % '\n\n'.join(paras))
        L.append(r'\ansline{解析}{%s}' % '\n\n'.join(
            no + jx.replace(r'\cha{}', '×').replace(r'\gou{}', '√') for no, _s, jx in js))
    return L


# ---------- 例题 [答案] 值反解（去答前正文值句＝唯一值源；两处钉值复核） ----------
def derive_ans(q, d):
    if d['ans'] is not None:
        return d['ans']
    joined = '\n\n'.join(d['xj'])
    if d['gu']:
        v = re.search(r'故答案为：(.+)$', d['gu'], flags=re.S).group(1).strip().rstrip('.').rstrip('。')
        return v
    mm = re.findall(r'故选[：:]?\s*(?:\\emph\{([^{}]+)\}|\\\(([^\\\)]+)\\\)|([A-D]{1,4}))', joined)
    if mm:
        a, b, c = mm[-1]
        return a or b or c
    mm = re.search(r'故答案为：(.+)$', joined.split('\n')[-1], flags=re.S) if '故答案为：' in joined else None
    if mm:
        return mm.group(1).strip().rstrip('.')
    mm = re.search(r'取值范围是(.+?)\.\s*$', joined.split('\n')[-1], flags=re.S)
    if mm:
        return mm.group(1).strip()
    mm = re.search(r'夹角的大小为(.+?)\.', joined, flags=re.S)
    if mm:
        return mm.group(1).strip()
    raise AssertionError('答案值反解失败：' + q)


# ---------- ② 素养小结（①识别/②操作/③收束）→ 题型总结块文案 ----------
bt = open(VFBODY, encoding='utf-8').read()
blocks = bt.split('\n\n')
xj = {}
cur = None
for b in blocks:
    m = re.match(r'\\tjdnr\{(一|二|三|四|五|六|七|八|九)\}\{([^}]*)\}', b)
    if m:
        cur = m.group(1)
        xj.setdefault(cur, {})
        xj[cur]['name'] = m.group(2)
        continue
    if not cur:
        continue
    m = re.match(r'\\xiaojie\{①识别：(.+)\}', b)
    if m:
        xj[cur]['①'] = m.group(1)
    m = re.match(r'\\bindp \{\\kaishu (②操作|③收束)：(.+)\}', b)
    if m:
        xj[cur][m.group(1)[0]] = m.group(2)
assert len(xj) == 9 and all(len(v) == 4 for v in xj.values()), {k: sorted(v) for k, v in xj.items()}

# ---------- ③ 组册 ----------
out = [r'% body.tex —— 导学件答案册-v1（组装器 组装body.py 产出，可重跑；勿手改——改口径请先改组装器）']
out += [r'% 内容＝去答案0911 移出块全量（导学件正文判分值 0 在场，本册值在场）；题号与导学件同号。',
        r'% 页码＝独立册起页 1（样张全书连续 P75 系练习册装订档，不适用，登记简报）。',
        r'\setcounter{page}{1}',
        r'% ---------- 册首行（沿样张拍板⑨：册名「参考答案」，E2 节标题件承载） ----------',
        r'\par\nointerlineskip',
        r'{\centering\fontsize{16.88pt}{22pt}\selectfont\hejie 参考答案\par}',
        r'\vspace{2.4mm}',
        r'\zhangtitle{第一章\quad 空间向量与立体几何}',
        r'\jietitle{1.1.1\quad 空间向量及其运算(导学件答案)}',
        r'\begin{multicols}{2}',
        r'\raggedcolumns',
        r'\emergencystretch=1em',
        r'% ---------- 件：CJK 题号条目（样张 \ansitem 承形——「例1/变式1」非数字号，题号走 \heihao 中文族；v10-B 层级缩进＝续行/后续段收一档 \qpind，悬挂参数走 \everypar 段首重申） ----------',
        r'\newcommand{\dansitem}[2]{\par\glueguard{1}\addvspace{4pt}%',
        r'  {\everypar{\hangindent\qpind\hangafter=1\setlength{\parindent}{\qpind}}%',
        r'  \noindent',
        r'  \makebox[0pt][l]{{\fontsize{11.4pt}{13pt}\selectfont\heihao #1}}%',
        r'  \hspace*{\anshang}{\anlabel [答案]}\hspace{0.5em}#2\par}}',
        r'\newcommand{\txline}[1]{\par{\hangindent\qpind\hangafter=1\noindent\hspace*{\qpind}%',
        r'  {\kaishu\fontsize{10.09pt}{12pt}\selectfont 题型：#1}\par}}',
        r'\newcommand{\txsummaryhead}[1]{\par\glueguard{1}\addvspace{3pt}\noindent%',
        r'  {\heibf\fontsize{10.09pt}{13pt}\selectfont [题型总结]\hspace{0.5em}#1}\par\nopagebreak}',
        r'\newcommand{\txsumitem}[2]{\par{\hangindent\qpind\hangafter=1\noindent\hspace*{\qpind}%',
        r'  {\kaishu\fontsize{10.09pt}{12pt}\selectfont #1：#2}\par}}',
        r'\qufen{一、课前预习}{知识点填空与判断答案——序与导学件同}',
        ''
    ] + _pre_lines() + [
        r'\setlength{\anshang}{12.2mm}',
        r'\qufen{二、课中探究}{九探究点×例1／变式1——题号与导学件同号}',
        '']
n_ents = 0
for i, num in enumerate(tjseq, 1):
    q1, q2 = f'探究点{num}·例1', f'探究点{num}·变式1'
    d1, d2 = recs[q1], recs[q2]
    name = d1['name']
    assert name == xj[num]['name'], q1
    a1 = derive_ans(q1, d1)
    out.append('%% ---------- 探究点%s　%s ----------' % (num, name))
    out.append(r'\qufen{探究点' + num + '　' + name + r'}{例1／变式1}')
    out.append(r'\dansitem{例1}{%s}' % a1)
    out.append(r'\txline{%s}' % name)
    assert d1['fen'], q1 + ' 分析块缺失'
    out.append(r'\ansline{分析}{%s}' % '\n\n'.join(d1['fen']))
    xjtxt = '\n\n'.join(d1['xj'])
    assert xjtxt, q1
    out.append(r'\ansline{详解}{%s}' % xjtxt)
    for w, path in d1['figs']:
        assert path.startswith('media/media/'), path
        out.append(r'\ansfig{\includegraphics[width=%.3fmm]{%s%s}}' % (w, MEDIA, path))
    for dj in d1['dj']:
        out.append(r'\ansline{点睛}{%s}' % dj)
    assert d2['ans'] and d2['jx'], q2
    out.append(r'\dansitem{变式1}{%s}' % d2['ans'])
    out.append(r'\txline{%s}' % name)
    out.append(r'\ansline{解析}{%s}' % d2['jx'])
    out.append(r'\txsummaryhead{%s}' % name)
    out.append(r'\txsumitem{识别信号}{%s}' % xj[num]['①'])
    out.append(r'\txsumitem{通法步骤}{%s}' % xj[num]['②'])
    out.append(r'\txsumitem{易错点}{%s}' % xj[num]['③'])
    out.append('')
    n_ents += 2
out += [r'\setlength{\anshang}{5.8mm}',
        r'\qufen{三、课堂评价}{本组共5题——题号与导学件同号}', '']
for k in range(1, 6):
    q = f'课堂评价{k}'
    d = recs[q]
    assert d['ans'] and d['jx'], q
    out.append(r'\ansitem{%d}{%s}' % (k, d['ans']))
    out.append(r'\ansline{解析}{%s}' % d['jx'])
    n_ents += 1
out += ['', r'\end{multicols}']

# 断言：23 题全数在座；素材/正文无缺件
assert n_ents == 23, n_ents
assert len(order) == 23 and set(order) == set(recs), '素材题组缺漏'
assert sum(1 for l in out if l.startswith(r'\kdhead{知识点')) == 3 \
    and sum(1 for l in out if l.startswith(r'\ansline{答案}{1．')) == 3 \
    and sum(1 for l in out if l.startswith(r'\ansline{解析}{(1)')) == 3, '课前预习节缺漏'
for num in tjseq:
    assert recs[f'探究点{num}·例1']['fen'] and recs[f'探究点{num}·例1']['xj']

with open(os.path.join(HERE, 'body.tex'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')
print(f'body.tex 组装完成：课前预习节（知识点3组kdhead居中＋[答案]3＋[解析]3＝填空20值按条目分组/判断6）＋'
      f'23 题条目（例1×9＋变式1×9＋课堂评价×5）＋题型行×18＋题型总结块×9；'
      f'v10-B 层级缩进＝条目/标签行顶格＋内容/续行收一档 5.0mm；'
      f'详解配图入册＝{sum(len(d["figs"]) for d in recs.values())} 张；答案值反解钉查：探六/探七＝源串反解（夹角/取值范围式）')
for num in tjseq:
    print(' 例1值', num, '=', re.sub(r'\\[a-zA-Z]+|[{}\\]', '', str(derive_ans(f'探究点{num}·例1', recs[f'探究点{num}·例1'])))[:26],
          '｜变1值', re.sub(r'\\[a-zA-Z]+|[{}\\]', '', str(recs[f'探究点{num}·变式1']['ans']))[:26])
for k in range(1, 6):
    print(' 检测', k, '=', re.sub(r'\\[a-zA-Z]+|[{}\\]', '', str(recs[f'课堂评价{k}']['ans']))[:26])
