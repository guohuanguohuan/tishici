# -*- coding: utf-8 -*-
# 执行代理E4 手术脚本：三小总控无损压缩（体系-改进压缩轮-0902）
# 范围：C:\提示词\大学数学总控.md、二轮复习总控.md、强基竞赛总控.md
# 方法：rb -> decode utf-8 -> replace -> encode utf-8 -> wb（断言 count(old)==1，不过即停该项，原样上报）
import io, os

BASE = r'C:\提示词'
FILES = {
    'U': os.path.join(BASE, '大学数学总控.md'),
    'E': os.path.join(BASE, '二轮复习总控.md'),
    'Q': os.path.join(BASE, '强基竞赛总控.md'),
}

# 每条 (key, kid, old, new)；「（删）」= 整段删除该括号串 => new=""
ITEMS = {
    'U': [
        ('U1', '阶段1打开本学科 knowledge 文件确认本章章序位置与前序边界（超纲判定基准文件）；章完成后汇报并停等。',
               '阶段1打开本学科 knowledge 文件确认本章章序位置与前序边界（超纲判定基准文件）。'),
        ('U2', '照公共规则§7现行文本：统一C9C9C9灰底、公式型按OMML挂法；本线讲练件题干整体铺题干底纹、解析白底——公共规则§7题干底纹条款',
               '照公共规则§7现行文本；本线讲练件题干铺题干底纹、解析白底——公共规则§7题干底纹条款'),
        ('U3', '答案填写＋需背内容浅灰底纹标记 w:shd C9C9C9，细则同',
               '答案填写＋需背内容浅灰底纹标记，细则同'),
        ('U4', '。**本线无教材节层，页眉页脚同串去节名段（品牌·册名·件型（共N页）·本n/共M本＋第X页）**。',
               '。**本线无教材节层，页眉页脚同串去节名段**。'),
        ('U5', '层级表达（顶格＋字号梯子＋标题整行底纹）按公共规则§7现行文本执行',
               '层级表达按公共规则§7现行文本执行'),
        ('U6', '（粒度：科，见末句）', ''),
    ],
    'E': [
        ('E1', '（浅灰底纹 w:shd C9C9C9、不加粗不划线、选择性标记、公式区挂法随答案值/需背分型口径）', ''),
        ('E2', '（统一C9C9C9灰底、公式型按OMML挂法）', ''),
        ('E3', '。**本线无教材节层，页眉页脚同串去节名段（品牌·册名·件型（共N页）·本n/共M本＋第X页）**。',
               '。**本线无教材节层，页眉页脚同串去节名段**。'),
        ('E4', '层级表达（顶格＋字号梯子＋标题整行底纹）按公共规则§7现行文本执行',
               '层级表达按公共规则§7现行文本执行'),
        ('E5', '（粒度＝模块（数学）／专题（物理），见末句）', ''),
    ],
    'Q': [
        ('Q1', '（浅灰底纹 w:shd C9C9C9、不加粗不划线、选择性标记、公式区挂法随答案值/需背分型口径）', ''),
        ('Q2', '：统一C9C9C9灰底、公式型按OMML挂法）', '）'),
        ('Q3', '。**本线无教材节层，页眉页脚同串去节名段（品牌·册名·件型（共N页）·本n/共M本＋第X页）**。',
               '。**本线无教材节层，页眉页脚同串去节名段**。'),
        ('Q4', '层级表达（顶格＋字号梯子＋标题整行底纹）按公共规则§7现行文本执行',
               '层级表达按公共规则§7现行文本执行'),
        ('Q5', '（分本粒度：子线——见本条末句）', ''),
    ],
}

# 规格书声称的验收数字
OSHI = {  # 每条规格书预算净字符
    'U': {'U1': 11, 'U2': 24, 'U3': 13, 'U4': 26, 'U5': 16, 'U6': 10},
    'E': {'E1': 49, 'E2': 23, 'E3': 26, 'E4': 16, 'E5': 22},
    'Q': {'Q1': 49, 'Q2': 22, 'Q3': 26, 'Q4': 16, 'Q5': 16},
}
NET_TARGET = {'U': 100, 'E': 136, 'Q': 129}
AFTER_TARGET = {'U': 3787, 'E': 2757, 'Q': 2685}
LIMIT = {'U': 4000, 'E': 3000, 'Q': 3000}

def load(p):
    with open(p, 'rb') as f:
        return f.read().decode('utf-8')

def save(p, text):
    with open(p, 'wb') as f:
        f.write(text.encode('utf-8'))

def main():
    lines = []
    before_all = {k: len(load(FILES[k])) for k in ('U', 'E', 'Q')}

    # 阶段1断言（只读）
    fail = []
    for k, items in ITEMS.items():
        t = load(FILES[k])
        for (kid, old, new) in items:
            c = t.count(old)
            ok = (c == 1)
            lines.append(f'[断言] {k}-{kid} count=={c} {"PASS" if ok else "FAIL"}')
            if not ok:
                fail.append(kid)

    exec_all = (not fail)
    if not exec_all:
        lines.append('[异常] 存在断言不合项，跳过全部替换，照原样上报。')

    per_measured = {}
    if exec_all:
        for k, items in ITEMS.items():
            p = FILES[k]
            t = load(p)
            before = len(t)
            for (kid, old, new) in items:
                # 逐条实测净字符（对 当前t 变体做一次替换）
                t_after = t.replace(old, new)
                per_measured[kid] = len(t_after) - len(t)
                t = t_after
            save(p, t)
            lines.append(f'[替换] {k} 整文件净字符 = {len(t)-before}')

    # 阶段3：重读验证 改后串在位 + 旧串清零
    lines.append('--- 验证（改后串在位/旧串清零） ---')
    for k, items in ITEMS.items():
        t = load(FILES[k])
        for (kid, old, new) in items:
            old_gone = (t.count(old) == 0)
            new_in = (new == '') or (t.count(new) >= 1)
            lines.append(f'[验证] {k}-{kid} 旧串清零={old_gone} 改后在位={new_in}')

    # 阶段4：逐条净字符 规格书预算 vs 实测
    lines.append('--- 逐条净字符：规格书预算 vs 实测 ---')
    lines.append(f'{"条目":<6}{"规格书":>8}{"实测":>8}')
    for k in ('U', 'E', 'Q'):
        for (kid, old, new) in ITEMS[k]:
            o = OSHI[k][kid]
            m = per_measured.get(kid, 'N/A')
            flag = '' if (isinstance(m, int) and m == o) else '  <- 偏差'
            lines.append(f'{kid:<6}{o:>8}{str(m):>8}{flag}')

    # 阶段5：整文件 len 前后 + 预算/目标检查
    lines.append('--- 整文件 len 前后（实测） ---')
    for k in ('U', 'E', 'Q'):
        if exec_all:
            after = len(load(FILES[k]))
        else:
            after = before_all[k]
        net = after - before_all[k]
        limit_ok = after <= LIMIT[k]
        target_ok = (after == AFTER_TARGET[k])
        limit_txt = 'OK' if limit_ok else 'OVER'
        target_txt = 'OK' if target_ok else 'MISMATCH'
        lines.append(f'{k}: 前 {before_all[k]} -> 后 {after} | 净 {net} | 规格书目标净 {NET_TARGET[k]} | '
                     f'预算{limit_txt} | 目标{target_txt}')

    # 阶段6：Q2 改后行重读（语法连贯确认）
    qtext = load(FILES['Q'])
    lines.append('--- Q2 改后行（语法连贯确认） ---')
    lines.append('Q2所在句上下文：')
    for i, ln in enumerate(qtext.split('\n'), 1):
        if '答案值分型照公共规则§7现行文本' in ln:
            lines.append(f'  L{i}: {ln}')

    print('\n'.join(lines))
    return lines

if __name__ == '__main__':
    main()
