# -*- coding: utf-8 -*-
r"""题号块三段式.py A''签名升级补丁（合并两部分）"""
p = r'C:\提示词\工具\题号块三段式.py'
s = open(p, encoding='utf-8').read()
orig = s
AP = "A''"   # 撇号常量（避免源串内裸撇号）

# —— 1) docstring ——
s = s.replace(
"""  · 层级制（同步线）：题号块「节号-序号．（档位·提分线·卡壳看答案）」——节号＝题所在教材节标题节号
    （内层节优先：节1.1.1之下不挂1.1）；序号＝节内连续（题族独立计数）；衔接件两段式同款
    「节号-序号．（衔接必会·卡壳看答案）」（--linkage，无档位无提分线）。旧全局「N．」输入照跑
    （重编为层级制——新旧双轨兼容）；已层级制输入幂等重跑。""",
"""  · 层级制（同步线，2026-09-02 A''成品轮签名升级）：题号块「题型号-节内序号．（档位·提分线·
    卡壳看答案）」——题型号＝该题所属题型组标题的父链序号（§6父链续层，如1.1.1.9；题型标题＝
    C6D4E3整行底纹＋序号起段）；序号＝节内连续（题族独立计数、同节跨题型累进）；衔接件两段式
    同款「题型号-节内序号．（衔接必会·卡壳看答案）」（--linkage）。旧全局「N．」与A'「节号-序号」
    输入照跑（重编为A''题型号形态——三轨兼容）；已A''形态输入幂等重跑。
  · 题型标题行末统计段（§7排版①）：每有题题型组标题行末追加「　N题：题号a」（单题）／
    「　N题：题号a～题号b」（多题区间形，新号形态）；幂等识别已挂统计段；无题组不挂。
  · 条目族维持「节号-序号．」（两形并存——§6编号唯一层形款）；题族门控节归属一律按位置
    （cur_sec＝最近节标题），A'输入前缀节号与位置节一致性有断言。""")

# —— 2) 常量 ——
s = s.replace(
"SEC_TTL_RE = re.compile(r'^\d+\.\d+(\.\d+)?[\s\u3000]+\S')   # 节标题节号pattern（2~3级）",
"""SEC_TTL_RE = re.compile(r'^\d+\.\d+(\.\d+)?[\s\u3000]+\S')   # 节标题节号pattern（2~3级）
GRP_TTL_RE = re.compile(r'^(\d+(?:\.\d+)+)[\s\u3000]+\S')      # 题型标题序号起段（A''题型统计段锚）
GRP_STATS_RE = re.compile(r'　\d+题：')                              # 已挂统计段幂等识别""")

# —— 3) 主循环 cur_group ——
s = s.replace(
"""        if i in sec_map:
            cur_sec = sec_map[i]
            sec_titles.append((i, cur_sec))
            continue
        if TITLE_RE.match(txt) or LECT_RE.match(txt):
            continue""",
"""        if i in sec_map:
            cur_sec = sec_map[i]
            sec_titles.append((i, cur_sec))
            continue
        if LECT_RE.match(txt):
            continue
        if TITLE_RE.match(txt):
            # A''：题型标题（C6D4E3整行底纹）→ cur_group＋组登记（统计段挂载锚）
            if ppr_shd_fill(c) == GRP_SHD:
                gm = GRP_TTL_RE.match(txt)
                if gm:
                    if cur_group is not None:
                        group_seq.append((cur_group, list(group_nums)))
                    cur_group = gm.group(1)
                    group_anchors.append((i, cur_group))
                    group_nums = []
            continue""")

# —— 4) 变量初始化 ——
s = s.replace(
"""    cur_sec = None
    sec_titles = []                      # (idx, 节号)""",
"""    cur_sec = None
    cur_group = None                     # A''：当前题型组标题序号（题族前缀）
    group_anchors = []                   # (idx, 题型号)——统计段挂载锚
    group_nums = []                      # 当前组题号新号收集
    group_seq = []                       # (题型号, [新号…]) 完整组序（末组统计段pass补录）
    sec_titles = []                      # (idx, 节号)""")

# —— 5) 节归属 ——
s = s.replace(
"""        # —— 节归属 ——
        sec = isec if isec is not None else cur_sec
        if sec is None:
            raise RuntimeError('第%d段题号 %s 位于首个节标题之前，无节号可挂（层级制必需）: %s'
                               % (i, tok, txt[:30]))""",
"""        # —— 节归属（A''：题族一律按位置节 cur_sec——前缀解析仅条目族用） ——
        if is_question:
            sec = cur_sec
            if isec is not None and re.fullmatch(r'\d+\.\d+(\.\d+)?', isec) and isec != cur_sec:
                raise RuntimeError("第%d段A'题号前缀节%s与位置节%s不符（节标题分区核对）: %s"
                                   % (i, isec, cur_sec, txt[:30]))
        else:
            sec = isec if isec is not None else cur_sec
        if sec is None:
            raise RuntimeError('第%d段题号 %s 位于首个节标题之前，无节号可挂（层级制必需）: %s'
                               % (i, tok, txt[:30]))
        if is_question and cur_group is None:
            raise RuntimeError("第%d段题号 %s 之前无题型组标题（%s题型号前缀必需——C6D4E3标题判定）: %s"
                               % (i, tok, AP, txt[:30]))""")

# —— 6) 门控 hier_in ——
s = s.replace(
"""            if is_question:
                exp_o = counters.get(isec, qstart_map.get(isec, 1))
                if iord != exp_o:
                    raise RuntimeError('第%d段层级制题号 %s 节内期望序号 %d（节%s）——若为续卷漏参，'
                                       '请补 --sec-start/-continue；若为本卷缺号，先核漏认（块边界：【答案】/标题）'
                                       % (i, tok, exp_o, isec))""",
"""            if is_question:
                exp_o = counters.get(sec, qstart_map.get(sec, 1))
                if iord != exp_o:
                    raise RuntimeError('第%d段层级制题号 %s 节内期望序号 %d（节%s，位置节门控）——若为续卷漏参，'
                                       '请补 --sec-start/-continue；若为本卷缺号，先核漏认（块边界：【答案】/标题）'
                                       % (i, tok, exp_o, sec))""")

# —— 7) 题族重编前缀 ——
s = s.replace(
"""        nxt = counters.get(sec, qstart_map.get(sec, 1))
        counters[sec] = nxt + 1
        seq.append((sec, nxt, int(iord) if iord is not None else int(tok)))
        new_num = '%s-%d' % (sec, nxt)""",
"""        nxt = counters.get(sec, qstart_map.get(sec, 1))
        counters[sec] = nxt + 1
        seq.append((sec, nxt, int(iord) if iord is not None else int(tok)))
        new_num = '%s-%d' % (cur_group, nxt)   # A''：题型号-节内序号
        group_nums.append(new_num)""")

# —— 8) 统计段挂载 pass（插在统计段区间括注联动之前） ——
s = s.replace(
"""    n_q, n_e = len(seq), len(eseq)

    # ---- 统计段区间括注联动（授权差异②：删全局题号区间括注） ----""",
"""    n_q, n_e = len(seq), len(eseq)
    if cur_group is not None:
        group_seq.append((cur_group, list(group_nums)))

    # ---- A'' 题型标题行末统计段挂载（§7排版①；幂等；无题组不挂） ----
    c_gstat = 0
    anchor_by_grp = dict(group_anchors)
    for grp, nums in group_seq:
        if not nums:
            continue                      # 无题组不挂
        gi = anchor_by_grp.get(grp)
        if gi is None:
            continue
        p_el = els[gi]
        full = para_text(p_el)
        if GRP_STATS_RE.search(full):
            continue                      # 幂等：已挂
        stat = ('　%d题：%s' % (len(nums), nums[0])) if len(nums) == 1 else \
               ('　%d题：%s～%s' % (len(nums), nums[0], nums[-1]))
        rs = [r for r in p_el.findall(q('r')) if run_text(r)]
        if not rs:
            continue
        last = rs[-1]
        nr = copy.deepcopy(last)
        for t in nr.findall(q('t')):
            nr.remove(t)
        t = etree.SubElement(nr, q('t'))
        t.text = stat
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        last.addnext(nr)
        c_gstat += 1
    # 统计段题数之和＝题量 恒等断言
    _gs = sum(len(nums) for _g, nums in group_seq)
    assert _gs == n_q, '题型组统计段题数之和%d≠题量%d（组序与题族核对）' % (_gs, n_q)

    # ---- 统计段区间括注联动（授权差异②：删全局题号区间括注） ----""")

# —— 9) _grp_rows 定义（登记md机器行数据） ——
s = s.replace("""    n_q, n_e = len(seq), len(eseq)""",
"""    _grp_rows = ['#GRP %s %s' % (g, ','.join(nums)) for g, nums in group_seq]
    n_q, n_e = len(seq), len(eseq)""", 1)

open(p, 'w', encoding='utf-8').write(s)
import ast
ast.parse(s)
print('patch ok, delta:', len(s) - len(orig))
