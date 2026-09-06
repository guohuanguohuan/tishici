# -*- coding: utf-8 -*-
"""extract_structure.py — 讲练件结构提取：节标题/题型组/题块（含难度）/讲块位置
用法: python extract_structure.py <docx> [out.json]
2026-08-28 升级：题块判定签名由「块内含【难度】字段」改为「题号块 N．（档位）＋块内含【答案】」双锚定
（难度前置拍板后标签行删【难度】，旧签名失效）；兼容旧件回退：块内仍有【难度】的按旧口径识别。
2026-08-29 增（成书形态回扫轮·T代理）：新增 kind='lecture'（讲部标题——「父号.k 方法讲解｜主题名」，
公共规则§6题型编号/§3.3讲部标题化）。此前该形态（无「：」）会被误判为 section——消费方
（节标题序号底纹/六类底纹计数）已同步按三标题分型；旧消费方（标题字号梯子等）按
kind=='section'/'group' 取集合，lecture 不入两集合（讲部标题五号加粗由内容代理按§3.3落，
不落小四节级字号——行为变更见 T-工具改版报告）。题块判定签名与输出结构其余不变。
2026-09-01 升级（A'改制轮·工具债③·T3）：
  ① 合并统计段签名兼容：节标题行与节级统计行合并后（公共规则§7排版①/N11）形如
     「2.4 曲线与方程　本节19题：简单1｜中档12｜难6」（旧式带「（第101—119题）」区间括注），
     因统计段含「：」曾被误判 group（题型标题）——现凡含统计段「　本节N题」的节号起段行
     一律判 section（看板工具债销号）。
  ② 层级制题号识别（公共规则§6编号唯一层形/§7⑦编号核验——同步线题号「节号-序号．」）：
     qstart 兼容「N．」（旧全局）与「1.1.1-5．」（层级制）两形态；题块正则同步两形态；
     题块记录增 sec 字段（题所在节号——层级制题号自带节号直接取，旧全局号取最近节标题）。
  ③ 编号核验输出双轨：旧全局号按 1..N 全件连续断言；层级制号按「节内序列连续无重复＋
     全件总数」断言（§7⑦），stdout 增各节序列清单。条目号（清单条目/讲部条目）同为
     「节号-序号．」/「N．」起段、归入 qstart kind，题块判定按块内【答案】过滤（条目无
     【答案】不计题块）——与题号块三段式.py 题族/条目族分列口径一致。
2026-09-06 债1修复（⑧轮·选必1成书修复-0905）：题块锚改钉现行件型题头括注族——档位括注
  「N．（简单|中档|难[·提分线][·卡壳看答案]）」与衔接必会括注「N．（衔接必会[·卡壳看答案]）」
  直接入题块（现行件型解析标签内嵌 U+2060，旧双锚「块内含【答案】」原文匹配第二腿全失效——
  B 实测 61/61 答案行带 ⁠）；〔…〕条目括注形显式排除不入题块；裸题号回退旧双锚且题头/标签
  匹配前一律 U+2060 归一（【⁠答⁠案⁠】原文计数为 0 的假阴性坑，⑥终报§三.6 同款）。括注词表与
  六类底纹计数.QBLOCK_HEAD_RE 同源对齐（提取题头集 ⊆ 计数器题号块签名段集）；kind 分型
  与输出结构不变。"""
import sys, io, zipfile, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)

STATS_RE = re.compile(r'[\s\u3000]本节\d+题')                      # 节级统计段（合并行）
QSTART_RE = re.compile(r'^(?:\d+(?:\.\d+)+-\d+|\d+)．')            # 层级制「节号-序号．」＋旧「N．」
SECNO_RE = re.compile(r'^(\d+(?:\.\d+)+)[\s\u3000]')
WJ = '\u2060'   # U+2060 WORD JOINER——成书件解析标签/题头内嵌，一切标签/题头匹配前归一（⑧债1）
# ⑧债1：题头括注族（词表与 六类底纹计数.QBLOCK_HEAD_RE 同源对齐——档位[·提分线]·卡壳看答案／
# 衔接必会[·卡壳看答案]／裸档位，须带全括注）＝现行件型题目区题头，直接入题块。
KUOHAO_RE = re.compile(r'^(\d+(?:\.\d+)+-\d+|\d+)．'
                       r'（((?:简单|中档|难)(?:·(?:保60%|保80%|冲100%))?·卡壳看答案'
                       r'|衔接必会(?:·卡壳看答案)?'
                       r'|(?:简单|中档|难))）')
TIAOMU_RE = re.compile(r'^(\d+(?:\.\d+)+-\d+|\d+)．〔')             # ⑧债1：〔…〕条目括注形——显式排除不入题块

def ptext(p):
    parts = []
    for e in p.iter():
        t = etree.QName(e).localname
        if t == 't' and e.text:
            parts.append(e.text)
    return ''.join(parts)

def sec_of_qnum(tok):
    """层级制题号「1.1.1-5」→ 节号「1.1.1」；旧全局号返回 None。"""
    m = re.match(r'^(\d+(?:\.\d+)+)-\d+$', tok)
    return m.group(1) if m else None

def structure(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))
    els = list(body)  # body级元素（含表格）
    items = []  # (kind, idx_in_els, text)
    cur_sec = None
    for i, el in enumerate(els):
        if el.tag != q('p'):
            items.append({'kind': 'other', 'el': i, 'text': '[TBL]' if el.tag == q('tbl') else etree.QName(el).localname, 'p': el})
            continue
        t = ptext(el)
        kind = 'para'
        if re.match(r'^\d+(\.\d+)*\s*方法讲解[｜|]', t):
            kind = 'lecture'    # 讲部标题 父号.k 方法讲解｜主题名（2026-08-29 成书形态拍板§6）
        elif SECNO_RE.match(t) and STATS_RE.search(t):
            kind = 'section'    # 合并统计段行——「N.N 标题[（第X—Y题）]　本节N题：…」含「：」不判group
        elif re.match(r'^\d+(\.\d+)*\s+\S', t):
            if '：' in t and re.match(r'^\d+(\.\d+)+\s', t):
                kind = 'group'      # 题型标题 X.Y.Z 标题：题型
            else:
                kind = 'section'    # 节标题（X.Y / X.Y.Z 无冒号）
        elif QSTART_RE.match(t):
            kind = 'qstart'
        if kind == 'section':
            cur_sec = SECNO_RE.match(t).group(1)
        items.append({'kind': kind, 'el': i, 'text': t, 'p': el, 'sec': cur_sec})

    # 题块判定：qstart 起到下一个 qstart/标题/表格 前；
    # ⑧债1 新锚（2026-09-06）：题头括注族（档位括注／衔接必会括注，KUOHAO_RE）直接入题块——
    # 现行件型题目区解析标签内嵌 U+2060，旧双锚「块内含【答案】」原文匹配对题目区/详解区全失效；
    # 〔…〕条目括注形显式排除（TIAOMU_RE，清单/讲部条目不得入题块）；裸题号回退旧双锚
    # （块内【答案】/【难度】legacy）——旧件与裸号卷型件语义不变。题头/标签匹配前一律 U+2060 归一。
    n = len(items)
    qinfo = []  # {no, start, end(Exclusive), diff, sec}
    i = 0
    while i < n:
        it = items[i]
        if it['kind'] == 'qstart':
            j = i + 1
            while j < n and items[j]['kind'] == 'para':
                j += 1
            block = [items[k]['text'] for k in range(i, j)]
            blk = '\n'.join(block)
            tn = it['text'].replace(WJ, '')      # 题头匹配前 U+2060 归一
            blkn = blk.replace(WJ, '')           # 标签匹配前 U+2060 归一（【⁠答⁠案⁠】假阴性坑）
            mno = re.match(r'^(\d+(?:\.\d+)+-\d+|\d+)．', tn)
            kuo = KUOHAO_RE.match(tn)
            tiao = TIAOMU_RE.match(tn)
            legacy = re.search(r'【难度】(简单|中档|难|[\d.]+)', blkn)
            if kuo or (mno and not tiao and ('【答案】' in blkn or legacy)):
                diff = (kuo.group(2) if kuo else '') or (legacy.group(1) if legacy else '')
                no = (kuo or mno).group(1)
                sec = sec_of_qnum(no) or it.get('sec')
                qinfo.append({'no': no, 'start': it['el'],
                              'end': items[j-1]['el'] + 1 if j > i + 1 else it['el'] + 1,
                              'diff': diff, 'sec': sec})
                i = j
                continue
        i += 1
    return {'items': [{'kind': x['kind'], 'el': x['el'], 'text': x['text'][:80]} for x in items],
            'questions': qinfo}

def hier_check(qs):
    """层级制题号核验（§7⑦：节内序列连续无重复）。返回 (按节序列dict, 问题清单)。"""
    bysec, probs = {}, []
    for k, x in enumerate(qs):
        m = re.match(r'^(\d+(?:\.\d+)+)-(\d+)$', x['no'])
        if not m:
            probs.append('非层级制题号 %s（第%d块）' % (x['no'], k))
            continue
        bysec.setdefault(m.group(1), []).append(int(m.group(2)))
    for sec, seq in bysec.items():
        for k in range(1, len(seq)):
            if seq[k] != seq[k-1] + 1:
                probs.append('节%s 序列断点：%d→%d' % (sec, seq[k-1], seq[k]))
        if seq and seq[0] != 1:
            probs.append('节%s 起始=%d（应为1，跨卷续号须配 --qstart 类参数核验）' % (sec, seq[0]))
    return bysec, probs

if __name__ == '__main__':
    s = structure(sys.argv[1])
    secs = [x for x in s['items'] if x['kind'] == 'section']
    grps = [x for x in s['items'] if x['kind'] == 'group']
    lecs = [x for x in s['items'] if x['kind'] == 'lecture']
    qs = s['questions']
    print('节标题 %d | 题型组 %d | 讲部 %d | 题块 %d（%s..%s）'
          % (len(secs), len(grps), len(lecs), len(qs), qs[0]['no'] if qs else 0, qs[-1]['no'] if qs else 0))
    if qs and re.match(r'^\d+(?:\.\d+)+-\d+$', qs[0]['no']):
        bysec, probs = hier_check(qs)
        for sec, seq in bysec.items():
            print(' 节%s 题号 %d..%d（%d题）' % (sec, seq[0], seq[-1], len(seq)))
        print('层级制核验:', probs if probs else '节内连续无重复 全过')
    else:
        cont = [qs[k]['no'] for k in range(1, len(qs)) if int(qs[k]['no']) != int(qs[k-1]['no']) + 1]
        print('题号连续性断点:', cont if cont else '无（1..N 连续）' if qs and int(qs[0]['no']) == 1 else '异常')
    for x in secs: print(' 节', x['el'], x['text'])
    for x in lecs: print(' 讲部', x['el'], x['text'])
    if len(sys.argv) > 2:
        json.dump(s, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
