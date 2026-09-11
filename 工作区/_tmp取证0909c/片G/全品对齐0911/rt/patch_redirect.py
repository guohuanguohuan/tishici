# -*- coding: utf-8 -*-
r"""patch_v8断言.py —— _测v4断言.py 全品对齐0911 断言同步（行号区间替换＋锚点断言）。
区间按 2026-09-11 现状（2306 行档）钉；任一锚不符即整体不落盘（fail fast，防半改）。
"""
import io, sys

P = r"工作区/_tmp取证0909c/片G/全品对齐0911/rt/A_patched.py"
lines = io.open(P, encoding='utf-8').read().split('\n')
n = len(lines)
print('原行数', n)

def L(i):
    return lines[i - 1]

def chk(i, *pres):
    ok = any(L(i).startswith(p) or p in L(i) for p in pres)
    if not ok:
        print('锚失配 L%d 现为: %r' % (i, L(i)[:100])); sys.exit(1)

# ---- 锚点核验 ----
chk(6, '表内行距 4.90±0.4')
chk(433, "check('⑥排印层")
chk(657, "check('⑰解析")
chk(1074, 'par_ok, par_detail = True, []')
chk(1106, "check('N1")
chk(1108, "reg('N1 口径")
chk(1432, "check('⑦ 解析→下题题号墨距")
chk(1552, "check('②半角括号宽")
chk(1569, '# ---- ④ 判断括号末行右挂')
chk(1819, "check('⑦-4")
chk(1822, "reg('⑦-4")
chk(2077, "n_kd = body.count")
chk(2084, 'n_kd_anchor, kd_pt')
chk(2113, "reg('⑪-3")
chk(2115, "n_zt = body.count")
chk(2213, '# 正文侧「判分值 0 在场」')
chk(2261, "cnts21 = {")
chk(2264, "check('㉑b")
chk(2276, "check('㉑c")

# ---- 替换块（倒序应用，行号不串）----
def rep(a, b, new):
    lines[a - 1:b] = new

rep(2276, 2278, [
"check('㉑c 答案册 23 题判分值逐一在场（题号+[答案]+值核·去空白包含判定）',",
"      val_ok and len(a_items) == 23,",
"      f'条目 {len(a_items)}/23' + (' 全在场' if val_ok else ' 未在场: ' + '；'.join(val_bad)))",
"# ---- ㉑d 课前预习值在场（全品对齐0911 新立；素材＝去答案0911/课前预习素材0911.txt）----",
"PRE = r'C:\\提示词\\工作区\\_tmp取证0909c\\片G\\去答案0911\\课前预习素材0911.txt'",
"_pg = []",
"for _ln in open(PRE, encoding='utf-8').read().splitlines():",
"    _f = _ln.split('\\t')",
"    if _f[0] == 'G':",
"        _pg.append([_f[1], _f[2], [], []])",
"    elif _f[0] == 'K':",
"        _pg[-1][2].append((int(_f[1]), _f[2]))",
"    elif _f[0] == 'J':",
"        _pg[-1][3].append((_f[1], _f[2], _f[3]))",
"assert len(_pg) == 3 and [len(g[2]) for g in _pg] == [11, 5, 4] \\",
"    and [len(g[3]) for g in _pg] == [2] * 3, '㉑d 素材分组异常'",
"d_ok, d_bad = True, []",
"for _ci, _nm, _ks, _js in _pg:",
"    fill = ''.join('%d%s' % (i, _core21(v)) for i, v in _ks)",
"    judg = ''.join('%s%s' % (no, sy) for no, sy, _j in _js)",
"    if _norm21(fill) not in atxt:",
"        d_ok = False; d_bad.append('知' + _ci + '填空串')",
"    if _norm21(judg) not in atxt:",
"        d_ok = False; d_bad.append('知' + _ci + '判断答串')",
"    for no, _s, jx in _js:",
"        core = _norm21(_core21(jx.replace(r'\\cha{}', '×').replace(r'\\gou{}', '√')))[:12]",
"        if _norm21(no) + core not in atxt:",
"            d_ok = False; d_bad.append('知' + _ci + '析' + no)",
"check('㉑d 课前预习节值在场（三组填空整串＋判断答整串＋简析逐条头12字·去空白包含判定）', d_ok,",
"      '三组九判定全在场' if d_ok else '未在场: ' + '；'.join(d_bad))",
"reg('㉑d 口径（全品对齐0911 新立）', '册 body「一、课前预习」节每组 [答案]＝填空紧凑条目（N．值）＋判断 (N)√×'",
"    '两段、[解析]＝逐条 (N) 简析多段（　与全角空格随去空白剔除）——与 组装body.py._pre_lines 同式复组成串，'",
"    '过 _norm21 后 pdf 明文包含判定；简析取头 12 字锚（长数学串 TeX 提取字形不稳，㉑c run1 教训）；'",
"    '正文侧反向锁＝⑪（kongda 0）＋④/⑥/⑰/N1（（　）×6／[解析]0）')",
])

rep(2261, 2265, [
"cnts21 = {'[答案]': 26, '[分析]': 9, '[详解]': 9, '[点睛]': 2, '[解析]': 17, '题型:': 18, '[题型总结]': 9}",
"# （atxt 过 NFKC——全角冒号折半角，键用 ASCII '题型:'；全品对齐0911：[答案]23→26、[解析]14→17＝课前预习 +3/+3）",
"miss21 = [f'{t}={atxt.count(t)}/{w}' for t, w in cnts21.items() if atxt.count(t) != w]",
"check('㉑b 答案册排印计数（pdf 明文去空白：[答案]26/分析9/详解9/点睛2/解析17/题型行18/题型总结9）＋位图2',",
"      not miss21 and a_nimg == 2, ('缺异 ' + ' '.join(miss21) if miss21 else '七项全合') + f'｜位图 {a_nimg}/2')",
])

rep(2213, 2214, [
"# 正文侧「判分值 0 在场」＝⑥（含故答案为/故选/[解析]0＋（　）×6 正锁）＋⑩ 反向门＋⑫ zhenti 0＋⑪ kongda 0（全品对齐0911 全域反向）。",
"# 册侧「值在场」：编译三0＋页数4；排印七项计数（含课前预习 +3/+3）；23 题逐一＋㉑d 课前预习逐组 包含判定。",
])

# —— ⑫ ——
rep(2115, 2119, [
"n_zt = body.count(r'\\zhenti{')",
"n_ztb = body.count(r'\\zhentib{')",
"n_jx_body = body.count(r'\\jiexi{')",
"check('⑫判断题：\\\\zhenti ×0（反向锁，旧 ×6）＋\\\\zhentib（空括号式）×6＋简析 jiexi ×0（答案制0911：14 行出册）',",
"      n_zt == 0 and n_ztb == 6 and n_jx_body == 0,",
"      f'zhenti={n_zt} zhentib={n_ztb}/6 jiexi={n_jx_body}')",
])

# —— ⑪-3 ——
rep(2084, 2114, [
"n_blank_anchor, n_val_anchor, kd_pt = 0, 0, []",
"for pno in range(1, n_pages + 1):",
"    page = doc[pno - 1]",
"    for d in page.get_drawings():",
"        for it in d['items']:",
"            if it[0] != 'l' or abs(it[1].y - it[2].y) > 0.5:",
"                continue",
"            ux0, ux1 = sorted((it[1].x, it[2].x))",
"            uw = ux1 - ux0",
"            if not (42 <= uw <= 60) or ux0 < MARGIN - 8 or ux1 > COLR + 8:",
"                continue",
"            if in_fig(pno, ux0, it[1].y - 0.6, ux1, it[1].y + 0.6):",
"                continue   # 回退轮0910：图内水平棱防御排除（位图时代恒不触发）",
"            near = []",
"            for blk in page.get_text('dict')['blocks']:",
"                for ln in blk.get('lines', []):",
"                    for sp in ln['spans']:",
"                        sx0, _, sx1, sy1 = sp['bbox']",
"                        if not sp['text'].strip():",
"                            continue",
"                        ov = min(sx1, ux1) - max(sx0, ux0)",
"                        if ov > 0.5 * min(sx1 - sx0, uw) and -1.5 <= sy1 - it[1].y <= 1.5:",
"                            near.append(sp['text'])",
"            if len(near) == 0:",
"                n_blank_anchor += 1",
"                kd_pt.append(uw)",
"            elif len(near) == 1:",
"                n_val_anchor += 1",
"kd_min = min(kd_pt) if kd_pt else -1",
"check('⑪-3 空档盒全量实测（全品对齐0911：42–60pt 下划线＋线下无值 ×34＝kongbai 全集；印答盒线下恰一值 ×0 反向锁）',",
"      n_blank_anchor == 34 and n_val_anchor == 0 and n_kd == 0 and kd_min >= 42,",
"      f'空档 {n_blank_anchor}/34 最窄 {kd_min:.1f}pt；印答值盒 {n_val_anchor}/0；body kongbai={n_kb}/34')",
"reg('⑪-3 口径（全品对齐0911 换锁）', 'signature＝栏带 42–60pt 水平细线（\\\\kongbai 15mm＝42.5pt）且线下 ±1.5pt '",
"    '无紧贴值 span——旧「线下恰一值」印答盒签名（\\\\kongda 自适应盒）随 6h 出册归零；实测分布 '",
"    'p1-5＝11/9/6/5/3（全页扫描，旧门限 p1/p2 口径作废）；值在场正向锁＝㉑d 册侧包含判定；'",
"    '旧 20 处盒宽全量实测史（≥42pt＋寄存器 \\\\kdmind/\\\\kdwd）见 .bak_全品对齐0911')",
])

# —— ⑪／⑪-2 ——
rep(2077, 2083, [
"n_kd = body.count(r'\\kongda{')",
"n_kb = body.count(r'\\kongbai{}')",
"check('⑪挖空 body.tex：印答 \\\\kongda ×0（反向锁，旧 ×20）＋空留白 \\\\kongbai ×34（原题干 14＋知识点 20＝全品对齐0911 6h）',",
"      n_kd == 0 and n_kb == 34, f'kongda={n_kd} kongbai={n_kb}/34')",
"# ⑪-2 旧门「印答值 pdf 在场（p1/p2）」随全品对齐0911 出册作废（印答不再排印，值含 Common 词伪阳）——",
"#   值在场改册侧锁＝㉑d；正文侧反向锁＝⑪-3 空档盒（线下无值）＋⑥（　）×6。",
"reg('⑪-2 作废登记（全品对齐0911）', '旧 ANSWERS 14 词 p1/p2 包含判定停用（迁 ㉑d 册侧正向＋⑪-3 反向）；'",
"    '旧值与逐词表见 .bak_全品对齐0911')",
])

# —— ⑦-4 ——
rep(1805, 1825, [
"        zt_end = [k for k, r in enumerate(rows)",
"                  if re.sub(r'\\s+', '', r[2]).endswith('（）')]",
"        for k1, k2 in zip(zt_end, zt_end[1:]):",
"            if k2 != k1 + 1:      # 全品对齐0911：判断题干行直接相邻成对（旧「between 含[解析]」判据随简析出册作废；",
"                                   #   跨块 (2)→(1) 必隔 zsd/条目/表/说明行，天然不满足相邻条件）",
"                continue",
"            up = rows[k1]",
"            if up[0] == rows[k2][0]:      # 同线碎片",
"                continue",
"            pitch = (rows[k2][3][0]['origin'][1] - up[3][0]['origin'][1]) / PT",
"            gap = ink_gap600(pno, ci, up[3][0]['origin'][1], rows[k2][3][0]['origin'][1])",
"            zt_ok = zt_ok and (6.2 <= pitch <= 6.7) and gap is not None and (2.5 <= gap <= 3.3)",
"            zt_detail.append(f'p{pno}c{ci} pitch{pitch:.2f} 墨隙{gap:.2f}')",
"check('⑦-4 相邻判断题缝（全品对齐0911 换形：（　）尾题干行直接相邻——普通行距档 6.44±0.25／墨隙 2.5–3.3；F 片B #31 尾距 0pt 沿革）',",
"      zt_ok and len(zt_detail) >= 2, '；'.join(zt_detail) or '未找到判断题对')",
"if zt_detail:",
"    reg('⑦-4 判断题缝口径（全品对齐0911 重释）',",
"        '配对判据由「(N) 行对中间含 [解析]、无块签名」改为「两（　）结尾题干行 k2==k1+1 直接相邻」——'",
"        '判断简析随 6h 出册，块内不再有 [解析] 行；\\\\zhentib 尾 \\\\addvspace{0pt} 承 \\\\zhenti 同档，缝＝普通行距档'",
"        ' 6.3–6.8/墨 2.5–3.3 窗不动；预期对 3（p1-p3 各 1 对）')",
])

# —— ④ 整块 ——
rep(1569, 1652, [
"# ---- ④ 判断括号（　）末行右挂×6＋独占行 0 容忍（全品对齐0911 换形：\\zhentib 尾段全角空括号；",
"#      基线归并口径沿用 0908——\hfill 大空隙被 MuPDF 拆片段，逐片段判须先按基线归并） ----",
"zhentib_form_ok = (r'\\noindent#1\\kern2.1pt#2\\nobreak\\hspace{0pt plus 1fil}\\nobreak（　）\\hspace{0.56mm}\\par' in blkfile)",
"# 旧 (√)(×) 文本形＋× TikZ 墨盒伪片段合成整套停用（墨盒判据现仅涉 \\zhenhead 说明行×3，非判断槽）；",
"# 反向锁：正文 (√)/(×) 字串 0 出现（√ 文本在说明行「正确的打√」内不单独成 (√) 形）。",
"n_hang, n_alone = 0, 0",
"_grp16 = {}",
"for pno in range(1, n_pages + 1):",
"    for t, bb, sps in lines_of[pno]:",
"        base = sps[0]['origin'][1]",
"        cl = COLL[0] if bb[0] < MID else COLL[1]",
"        _grp16.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))",
"for frs in _grp16.values():",
"    frs.sort()",
"    mt = re.sub(r'\\s+', '', ''.join(x[1] for x in frs))",
"    n_par = mt.count('（）')",
"    if not n_par:",
"        continue",
"    if len(mt) > 2 * n_par:",
"        n_hang += n_par",
"    else:",
"        n_alone += n_par",
"check('④判断括号（　）挂题干末行 ×6＋独占括号行 0 容忍＋旧印答槽反向（(√)(×) 0）',",
"      n_hang == 6 and n_alone == 0 and zhentib_form_ok",
"      and full.count('(√)') + full.count('(×)') == 0,",
"      f'右挂{n_hang}/6 独占行{n_alone} 宏形{\"在\" if zhentib_form_ok else \"缺\"} 旧槽残留{full.count(\"(√)\")+full.count(\"(×)\")}')",
"reg('④ 判断括号换形（全品对齐0911）', '\\\\zhentib 尾段＝\\\\nobreak\\\\hspace{0pt plus 1fil}\\\\nobreak（　）\\\\hspace{0.56mm}——'",
"    '右挂机制（fil 双 nobreak 直连＋\\\\kern2.1pt 序号隙）承 \\\\zhenti 逐字不动，槽内容改空、括号改全角（照全品 p04 实拍）；'",
"    '旧 0909 收尾轮返修史（R2/\\\\mbox 实验、( × ) 剥空格、× 墨盒伪片段）见 .bak_全品对齐0911；'",
"    '×/√ 值出册后仅 \\\\zhenhead 说明行「正确的打√,错误的打×」内联保留（题面指引，非答案槽）')",
])

# —— ② ——
rep(1552, 1553, [
"check('②半角括号宽 0.3–0.7em（中位）＋全角括号恰 12＝（　）×6 豁免（全品对齐0911；旧门零残留）',",
"      paren_cnt >= 50 and 0.3 <= par_w <= 0.7 and fw_paren == 12,",
"      f'n={paren_cnt} 中位{par_w:.3f}em（Times 0.33 档；全品半角括 0.5em——登记差异）全角括号{fw_paren}/12（＝判断空括号（　）6 对，U+3000 随去空白并吞不计；除此零残留）')",
])

# —— N10 ⑦ 解析→题号 ——
rep(1432, 1434, [
"check('⑦ 解析→下题题号墨距（全品对齐0911：判断简析亦出册→正文 [解析] 行 0——配对 n==0 反向锁；旧门 n 1–2∈2.0–3.5 作废）',",
"      len(gaps_bb) == 0,",
"      f'n={len(gaps_bb)}（应 0＝正文无 [解析] 行；残余即判断简析回渗签名）')",
])

# —— N1 整块 ——
rep(1074, 1110, [
"par_ok, par_detail = True, []",
"# 全品对齐0911：判断槽＝全角空括号（　）右挂（\\zhentib）——旧半角 (√)(×)＋× 墨盒伪片段合成口径作废",
"#   （× 墨盒现仅存 \\zhenhead 说明行×3，不再作判断槽签名）；提取层对 U+3000 可拆段，判据＝去空白行尾「（）」且非纯括号行。",
"for pno in range(1, n_pages + 1):",
"    page = doc[pno - 1]",
"    for t, bb, sps in lines_of[pno]:",
"        tc = re.sub(r'\\s+', '', t)",
"        if not tc.endswith('（）') or len(tc) <= 2:",
"            continue",
"        cl = COLL[0] if bb[0] < MID else COLL[1]",
"        pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,",
"                             clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))",
"        w, h, s = pm.width, pm.height, pm.samples",
"        cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]",
"        ink_r = cl + (w - 1 - cols[::-1].index(True)) / SC",
"        ink_d = (cl + COLW - ink_r) / PT",
"        bb_d = (cl + COLW - bb[2]) / PT",
"        par_ok = par_ok and -0.1 <= ink_d <= 0.45 and -0.4 <= bb_d <= 0.2",
"        par_detail.append(f'p{pno}（　）ink{ink_d:.2f}/bbox{bb_d:.2f}')",
"check('N1 判断题括号固定列位（全品对齐0911 全角（　）右挂×6；ink≤0.45 贴栏右＋bbox −0.4~0.2）',",
"      par_ok and len(par_detail) == 6, ' '.join(par_detail))",
"reg('N1 口径（全品对齐0911 换形）', '旧半角 1.8em makebox 文本槽＋× 墨盒合并伪片段判定随判断答案出册停用——'",
"    '新形 \\\\zhentib 尾（　）（U+FF08 U+3000 U+FF09）行尾右挂；列位窗沿用 0909 R2 标定（ink 距栏右≤0.45、bbox −0.4~0.2）；'",
"    'MuPDF 拆段以基线片段行直接判（（　）系单字族连排，实际未见拆段，len(tc)<=2 排纯括号行）')",
])

# —— ⑰ ——
rep(657, 659, [
"check('⑰解析 10.5pt 档（全品对齐0911：判断简析 6→0 出册；变式/检测简析 14→0 答案制0911）＋\\\\zhuzhu [注意]前缀新体无小号层',",
"      sz_ok and n_jx_span == 0 and no_small,",
"      f'解析span {n_jx_span}/0 越档{0 if sz_ok else \"有\"}；\\\\zhuzhu 新体 {\"是\" if no_small else \"否\"}')",
])

# —— ⑥ ——
rep(433, 437, [
"check('⑥排印层 正文判分值 0 在场（全品对齐0911 全域）◆9/例1 9/变式9 题面不变＋[答案]0/故答案为0/故选0/分析0/详解0/点睛0/解析0（判断简析亦出册）＋（　）×6 正锁',",
"      n_tj == 9 and n_li1 == 9 and n_bs == 9 and n_ans == 0 and n_star == 0 and n_jx == 0",
"      and n_fx == 0 and n_xj2 == 0 and n_dj2 == 0 and n_gdaan == 0 and n_gxuan == 0",
"      and full.count('（）') == 6,",
"      f'◆{n_tj} 例1{n_li1} 变式{n_bs} 答案{n_ans} ★{n_star} 解析{n_jx} 分析{n_fx} 详解{n_xj2} 点睛{n_dj2}'",
"      f' 故答案{n_gdaan} 故选{n_gxuan} 空括号{full.count(\"（）\")}/6（值在场见 ㉑b/㉑c/㉑d）')",
])

# —— docstring v8 注 ——
rep(6, 6, [
L(6),
'',
'全品对齐0911（v8 轮）同步：⑪ kongda×20→0 反向＋kongbai×34 正向；⑪-2 p1/p2 印答值门→作废迁 ㉑d；',
'⑪-3 印答盒（线下恰一值）×20→空档盒（线下无值）×34＋印答 0 反向；⑫ zhenti 6→0＋zhentib 6 新锁；',
'④ (√)(×)×6 右挂→（　）×6 右挂（× 墨盒伪片段合成停用）；⑥ [解析]6→0＋（　）6 正锁；⑰ 解析span 6→0；',
'N1 槽列位换形（全角（　））；N10 解析→题号配对 1–2→0 反向；⑦-4 配对判据改「（　）尾行直接相邻」；',
'② 全角括号 0→恰12（（　）×6 豁免）；页数门 ①＝5 复测不变；㉑a 页数4 不变；㉑b [答案]23→26、[解析]14→17；',
'㉑c 23 题门不变；新立 ㉑d 课前预习节值在场。旧值全录 .bak_全品对齐0911。',
])

# ---- 尾检：docstring 收尾唯一性（原 L47 有 """，我在 L6 后插的行以 """ 收尾会双闭——需删原闭）----
# 原文件 docstring 起 L2 止 L47。若 L6 已是末行则不行——检查 L47：
print('注意：docstring 原止于', 'L47' if '"""' in L(47) else '别处')

out = '\n'.join(lines)
io.open(P, 'w', encoding='utf-8').write(out)
print('patched -> 新行数', out.count('\n') + 1)
