# -*- coding: utf-8 -*-
"""讲部填空候选扫描（公共规则§5创作层③「讲部知识填空化挖空位」的对应辅助工具，工具债看板④，2026-08-30建）

定位：只扫描登记、不修改任何文件——挖空点判定仍由人工按§5创作层③逐处亲做
（所挖必为需背结论/关键术语、挖后句义仍自足），本工具仅产出机械候选池供人工过目。

口径（§5/§7现行文本）：
  讲部识别：讲部标题段＝段文本含「方法讲解｜」（§7讲部标题形态
  「父号.k 方法讲解｜主题名（大招N·大招名）」）。
  讲部范围＝讲部标题段起、至下一节/讲部/题型标题段（段首匹配 ^数字.数字 且非小问）止——
  小问形态（（1）／①等）天然不匹配 ^\\d+\\.\\d+，无需特判；散句偶然以「N.M」起段会被
  误判为终止标题，如遇以逐讲部终止段对账为准。
候选判定（机械启发式，输出供人工核，绝不等于挖空点）：讲部范围内段落按句切分
（句终符＝。；！？及非小数点／非省略号的半角句点），命中以下任一即候选——
  ①定义句式：句含「叫做／称为／就叫／定义为」
  ②结论引导：句含「则有／可得／恒有／当且仅当／充要」（不含英文 we_have，按任务口径不用）
  ③公式密度：句内 oMath 数≥1 且句长≤60字（句长＝非空白线性化字符数，每个公式占位符计1字）
  ④数量词结论：句含 数词+(个|条)+(交点/准线/渐近线/焦点/顶点/对称轴/切线/公共点) 等
每候选一行：讲部序／讲部标题／段序号（全件 body 段序，含表格内段落）／句序（段内句序）／
句文本前50字（公式以⟦公式⟧占位）／命中类型（多命中以＋相连）／句内 oMath 数。
已知局限：公式内数字不参与④匹配（公式按占位符线性化，数字在 m:t 内不计入句文本）、
公式超长句的③按1字/公式计——漏检由人工过目兜底。
限制登记：每讲部候选数、全件候选总数；表尾固定注明
「候选≠挖空点：最终挖空1~3处/条由人工按§5创作层③亲判」。
备注列：句内已含空位线「＿＿」时登记提示（§5③：源自知识清单的条目复制件本就是
填空＋灰底形态、不属本项范围，人工复核剔除）。

用法：python 工具/讲部填空候选扫描.py <docx> [docx ...] [--out 输出前缀]
  输出：前缀.tsv＋前缀.md 双格式；无 --out 时默认与输入同目录、前缀＝输入名＋「.讲部填空候选」；
  多输入且给 --out 时前缀＝--out＋输入主名。
  无讲部件（如纯题目卷、知识清单）输出空表＋退出码0。
安全：全程只读（zip 以 'r' 打开），任何情况下不写输入文件。
"""
import argparse
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
MC = '{http://schemas.openxmlformats.org/markup-compatibility/2006}'

LECTURE_MARK = '方法讲解｜'      # §7讲部标题形态核心标记
BARE_MARK = '方法讲解'           # 裸栏目标记（§7禁止裸栏目标题充当讲部标题——只作提示）
NUM_TITLE_RE = re.compile(r'^\d+\.\d+')   # 节/讲部/题型标题段起段形态（终止讲部范围）
SENT_END = '。；！？'
DEF_WORDS = ('叫做', '称为', '就叫', '定义为')            # ①定义句式
CONC_WORDS = ('则有', '可得', '恒有', '当且仅当', '充要')  # ②结论引导
QUANT_RE = re.compile(                                    # ④数量词结论（含同族锥线量词名词）
    r'(?:[0-9]+|[一二两三四五六七八九十]+)(?:个|条)'
    r'(?:交点|准线|渐近线|焦点|顶点|对称轴|切线|公共点)')
F_PLACE = '⟦公式⟧'     # 公式占位符（线性化，参与句长/计数）
BLANK = '＿＿'          # 既有空位线（§5③既有填空形态提示）
LEN_LIMIT = 60          # ③公式密度句长上限（字）
EXCERPT = 50            # 句文本摘录上限（字）


def linearize(p):
    """段落线性化：w:t 文本与 m:oMath 占位交错；跳过 mc:Fallback（旧版兼容重复内容）。"""
    toks = []

    def walk(el):
        tag = el.tag
        if tag == MC + 'Fallback':
            return
        if tag == M + 'oMath':
            toks.append(('f', None))          # 公式整体一枚占位，不下钻（m:t 不计句文本）
            return
        if tag == W + 't':
            toks.append(('t', el.text or ''))
            return
        if tag in (W + 'tab', W + 'br'):
            toks.append(('t', ' '))
            return
        for c in el:
            walk(c)

    walk(p)
    return toks


def plain_text(toks):
    return ''.join(v for k, v in toks if k == 't')


def linear_text(toks):
    return ''.join(v if k == 't' else F_PLACE for k, v in toks)


def split_sentence_spans(s):
    """按句终符切分线性化段文本，返回 (start,end) 跨度列表（覆盖全文）。"""
    spans = []
    n = len(s)
    st = 0
    i = 0
    while i < n:
        ch = s[i]
        if ch in SENT_END:
            spans.append((st, i + 1))
            st = i + 1
        elif ch == '.':
            prev = s[i - 1] if i > 0 else ''
            nxt = s[i + 1] if i + 1 < n else ''
            # 半角句点为句终符，但小数（数字.数字）与省略号（…点连排）除外
            if not (prev.isdigit() and nxt.isdigit()) and prev != '.' and nxt != '.':
                spans.append((st, i + 1))
                st = i + 1
        i += 1
    if st < n:
        spans.append((st, n))
    return spans


def sentences_of(toks):
    """段 → [(句文本(含公式占位), 句内公式数)]；空白句剔除，纯公式尾句保留。"""
    s = linear_text(toks)
    out = []
    for a, b in split_sentence_spans(s):
        frag = s[a:b]
        core = frag.strip()
        nm = frag.count(F_PLACE)
        if not core and nm == 0:
            continue
        out.append((frag.strip(), nm))
    return out


def sent_len(frag, nmath):
    """句长＝非空白线性化字符数，每个公式占位符计1字。"""
    return len(re.sub(r'\s', '', frag)) - nmath * (len(F_PLACE) - 1)


def detect_lectures(paras):
    """返回 [(起段序(1基), 止段序(Exclusive), 标题文本)] 与裸标记段序列表。"""
    lectures = []
    bare = []
    texts = [plain_text(linearize(p)).strip() for p in paras]
    n = len(texts)
    i = 0
    while i < n:
        tx = texts[i]
        if LECTURE_MARK in tx:
            j = i + 1
            while j < n and not NUM_TITLE_RE.match(texts[j]):
                j += 1
            lectures.append((i + 1, j + 1, tx))   # 止段序为 Exclusive（1基）
            i = j
        elif BARE_MARK in tx:
            bare.append(i + 1)
            i += 1
        else:
            i += 1
    return lectures, bare


def scan_file(path):
    """返回 dict：lectures/candidates/counts 等。"""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    body = root.find(W + 'body')
    if body is None:
        raise RuntimeError('word/document.xml 无 body：%s' % path)
    paras = body.findall('.//' + W + 'p')
    lectures, bare = detect_lectures(paras)

    rows = []
    per_lecture = []
    type_dist = {'①定义': 0, '②结论引导': 0, '③公式密度': 0, '④数量词': 0}
    for li, (s, e, title) in enumerate(lectures, 1):
        cnt = 0
        for pi in range(s, e):                      # 段序 1基，含标题段（实测标题段零命中）
            toks = linearize(paras[pi - 1])
            for si, (frag, nm) in enumerate(sentences_of(toks), 1):
                hits = []
                if any(w in frag for w in DEF_WORDS):
                    hits.append('①定义')
                if any(w in frag for w in CONC_WORDS):
                    hits.append('②结论引导')
                slen = sent_len(frag, nm)
                if nm >= 1 and slen <= LEN_LIMIT:
                    hits.append('③公式密度')
                if QUANT_RE.search(frag):
                    hits.append('④数量词')
                if not hits:
                    continue
                remark = ''
                if BLANK in frag:
                    remark = '句内已含空位线＿＿（既有填空形态，§5③不计此句，人工复核剔除）'
                excerpt = frag[:EXCERPT]
                rows.append([str(li), title[:40], str(pi), str(si),
                             excerpt, '＋'.join(hits), str(nm), remark])
                for h in hits:
                    type_dist[h] += 1
                cnt += 1
        per_lecture.append((li, title, cnt))

    return {'paras': len(paras), 'lectures': lectures, 'bare': bare,
            'rows': rows, 'per_lecture': per_lecture, 'dist': type_dist}


def write_outputs(path, res, out_prefix):
    stem = os.path.splitext(os.path.basename(path))[0]
    tsv_path = out_prefix + '.tsv'
    md_path = out_prefix + '.md'
    n_lect = len(res['lectures'])
    n_cand = len(res['rows'])
    dist = res['dist']
    dist_line = ('①定义 %d｜②结论引导 %d｜③公式密度 %d｜④数量词 %d'
                 % (dist['①定义'], dist['②结论引导'], dist['③公式密度'], dist['④数量词']))

    header = ['讲部序', '讲部标题', '段序号', '句序', '句文本前50字', '命中类型', '句内oMath数', '备注']
    # —— TSV（utf-8-sig，Excel 直开）——
    with open(tsv_path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('\t'.join(header) + '\n')
        for r in res['rows']:
            f.write('\t'.join(c.replace('\t', ' ').replace('\n', ' ') for c in r) + '\n')
        if n_lect == 0:
            f.write('（本件无讲部——0个讲部块，空表）\n')
        for li, title, cnt in res['per_lecture']:
            f.write('小计\t讲部%d\t%s\t候选数=%d\n' % (li, title[:40], cnt))
        f.write('总计\t讲部数=%d\t候选总数=%d\t按类型（多命中重复计）：%s\n' % (n_lect, n_cand, dist_line))
        f.write('候选≠挖空点：最终挖空1~3处/条由人工按§5创作层③亲判\n')

    # —— MD ——
    def esc(x):
        return str(x).replace('|', '\\|').replace('\n', ' ')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('# 讲部填空候选登记表（%s）\n\n' % os.path.basename(path))
        f.write('- 全件 body 段数：%d；讲部块数：%d；候选总数：%d\n' % (res['paras'], n_lect, n_cand))
        f.write('- 按类型分布（多命中句在分布中重复计数）：①定义 %d｜②结论引导 %d｜③公式密度 %d｜④数量词 %d\n'
                % (dist['①定义'], dist['②结论引导'], dist['③公式密度'], dist['④数量词']))
        for li, title, cnt in res['per_lecture']:
            f.write('- 讲部%d「%s」：候选 %d\n' % (li, esc(title[:60]), cnt))
        if res['bare']:
            f.write('- 提示：%d 个段落含「方法讲解」但无「｜」标记（§7禁止裸栏目标题充当讲部标题），段序：%s\n'
                    % (len(res['bare']), '、'.join(map(str, res['bare']))))
        if n_lect == 0:
            f.write('\n（本件无讲部——0个讲部块，空表。纯题目卷/知识清单等无讲部形态件属正常。）\n')
        else:
            f.write('\n| 讲部序 | 讲部标题 | 段序号 | 句序 | 句文本前50字 | 命中类型 | 句内oMath数 | 备注 |\n')
            f.write('|---|---|---|---|---|---|---|---|\n')
            for r in res['rows']:
                f.write('| ' + ' | '.join(esc(c) for c in r) + ' |\n')
        f.write('\n> 候选≠挖空点：最终挖空1~3处/条由人工按§5创作层③亲判'
                '（所挖必为需背结论/关键术语、挖后句义仍自足；源自知识清单的条目复制件'
                '本就是填空＋灰底形态，不属本项范围）。\n')
    return tsv_path, md_path


def default_prefix(path):
    d = os.path.dirname(os.path.abspath(path))
    stem = os.path.splitext(os.path.basename(path))[0]
    return os.path.join(d, stem + '.讲部填空候选')


def main(argv=None):
    ap = argparse.ArgumentParser(description='讲部填空候选扫描（只读登记，不修改文件）')
    ap.add_argument('inputs', nargs='+', help='输入 docx（可多个）')
    ap.add_argument('--out', help='输出前缀（生成 前缀.tsv＋前缀.md；缺省＝输入名.讲部填空候选）')
    args = ap.parse_args(argv)

    rc = 0
    for path in args.inputs:
        if not os.path.exists(path):
            print('[缺文件] %s' % path)
            rc = 1
            continue
        try:
            res = scan_file(path)
        except Exception as ex:                                   # noqa: BLE001
            print('[失败] %s：%s' % (path, ex))
            rc = 1
            continue
        if args.out:
            if len(args.inputs) > 1:
                stem = os.path.splitext(os.path.basename(path))[0]
                prefix = args.out + '.' + stem
            else:
                prefix = args.out
        else:
            prefix = default_prefix(path)
        tsv_path, md_path = write_outputs(path, res, prefix)
        dist = res['dist']
        print('%s' % os.path.basename(path))
        print('  讲部块数=%d  候选总数=%d  （①定义 %d｜②结论引导 %d｜③公式密度 %d｜④数量词 %d）'
              % (len(res['lectures']), len(res['rows']),
                 dist['①定义'], dist['②结论引导'], dist['③公式密度'], dist['④数量词']))
        for li, title, cnt in res['per_lecture']:
            print('  讲部%d（段%d起）候选=%d  %s' % (li, res['lectures'][li - 1][0], cnt, title[:40]))
        if not res['lectures']:
            print('  无讲部（纯题目卷/知识清单等）——空表，退出码0')
        print('  输出：%s\n        %s' % (tsv_path, md_path))
    return rc


if __name__ == '__main__':
    sys.exit(main())
