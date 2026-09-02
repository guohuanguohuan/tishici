# -*- coding: utf-8 -*-
# 手术脚本 E2：高中同步总控.md · 4条替换（C1/C2/C4/C6）
# 方法：文本域 io.open 读取（按规格书净字符计算口径）→ 断言 count(old)==1 → replace → 写回
# 说明：目标文件为 CRLF。文本域读（universal newline）会把 CRLF 归一为 LF；
#       由于替换串不含换行符，文本域与二进制域等价，且文本域 len 与规格书基线 19620 一致。

import io, sys

PATH = r'C:\提示词\高中同步总控.md'

# ——每条 old/new（逐字照抄分析报告「原文（逐字）/改后（逐字）」；C6 用规格书定稿）——
C1_OLD = '**讲部标题化与嵌套编号**：讲部标题统一「父号.k 方法讲解｜主题名（大招N·大招名——进阶来源按源讲义回填真实号名）」、大招名与主题名同名时括注仅「（大招N）」、小四加粗（§7标题字号梯子），题型＝父号.j（节内无讲部时＝节号.k）；序号体系与层级表达（顶格＋字号梯子＋标题整行底纹）照公共规则§6/§7现行文本；禁止裸栏目标题（「大招讲解」四字类段落不得充当讲部标题）与题干内【典例N】栏目名残留（来源身份标签唯一合法位置＝讲部/题型标题括注）。'
C1_NEW = '**讲部标题化与嵌套编号**：讲部标题统一式、大招名括注、标题字号梯子、禁止裸栏目标题与题干内【典例N】栏目名残留（来源括注唯一合法位置）全部照公共规则§6讲部标题款＋§7标题字号梯子现行文本；题型＝父号.j（节内无讲部时＝节号.k，续层口径照§6）。'

C2_OLD = '**题型标题行末加统计段**「　N题：题号a～b」（单题「　1题：题号a」；组内多题用区间形——§7排版①）；恒等式「'
C2_NEW = '**题型标题行末加统计段**（形态照§7排版①）；恒等式「'

C4_OLD = '**讲部知识填空化（公共规则§5创作层③现行文本）**：讲部独有讲解性知识（范围与例外照公共规则§5创作层③）转填空形态，挖空形态照该条款执行；'
C4_NEW = '**讲部知识填空化（公共规则§5创作层③现行文本）**：讲部独有讲解性知识转填空形态（范围、例外与挖空形态全照该条款）；'

C6_OLD = '③新知识条目之下按需附对比辨析（判定、形态、封顶与恒等式细则全照公共规则§5创作层④⑤＋§7条目分类标记条款）；'
C6_NEW = '③新知识条目之下按需附对比辨析（判定、形态、封顶与恒等式细则全照上述条款）；'

ITEMS = [('C1', C1_OLD, C1_NEW),
         ('C2', C2_OLD, C2_NEW),
         ('C4', C4_OLD, C4_NEW),
         ('C6', C6_OLD, C6_NEW)]

def main():
    # 文本域读取（净字符/len 口径与规格书基线一致）
    with io.open(PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    before_len = len(text)

    print('=== 术前 ===')
    print('before_len (text-mode):', before_len)
    print('CR count in file:', open(PATH,'rb').read().count(b'\r'))
    print()

    result = {}
    any_fail = False
    for name, old, new in ITEMS:
        cnt = text.count(old)
        net = len(new) - len(old)
        print('--- %s ---' % name)
        print('count(old) ==', cnt)
        print('net char = %d (old=%d -> new=%d)' % (net, len(old), len(new)))
        if cnt != 1:
            print('   [断言不过] count(old)==1 失败，本项跳过不替换')
            result[name] = 'FAIL_COUNT=%d' % cnt
            any_fail = True
            continue
        text = text.replace(old, new)
        print('   [已替换] 改后串现在 count(new)=', text.count(new), ' old 残留='
              if False else '   old count now=')
        print('   old count now (should be 0):', text.count(old))
        result[name] = net

    # 写回前必须所有 count 断言通过（否则整项原样上报，不写盘）
    if any_fail:
        print('\n!!! 存在断言异常项，不写盘，原样上报报告。')
        print('results:', result)
        sys.exit(1)

    after_len = len(text)
    total_net = after_len - before_len
    print()
    print('=== 术后 ===')
    print('after_len (text-mode):', after_len)
    print('total net char =', total_net, ' (预期 -160)')
    print('per-item net:', result)
    print('sum per-item:', sum(result.values()))

    if total_net != -160:
        print('!!! 合计净字符 != -160，请核对')
    if after_len > 20000:
        print('!!! len 超预算 20000')

    # 逐条目确认改后串在位 + 旧串清零
    print('\n=== 改后逐条在位/清零确认 ===')
    ok = True
    for name, old, new in ITEMS:
        in_place = text.count(new)
        old_left = text.count(old)
        flag = 'OK' if (in_place >= 1 and old_left == 0) else 'FAIL'
        if flag == 'FAIL':
            ok = False
        print('%s: new在本文件出现 %d 次, old残留 %d -> %s' % (name, in_place, old_left, flag))

    if not ok:
        print('!!! 存在旧串残留或改后串缺失，请核对')
        sys.exit(1)

    # 写回（保持 CRLF：需把文本域 LF 还原为 CRLF；原文件为纯 CRLF，无遗漏 LF）
    with io.open(PATH, 'r', encoding='utf-8', newline='') as f:
        raw_text = f.read()  # newline='' 保留原始行尾，不回显归一
    # 上面已读取并替换的是归一化 text；但写回需保持 CRLF。
    # 由于替换串不含换行，且替换未增删换行，故用归一化 text 即可；
    # 为保证 CRLF，写回时以二进制进行：对归一化后的 text（LF 结尾）转 CRLF。
    # 但 text 是 universal newline 读的（LF），原文件 CRLF；还原为 CRLF。
    data = text.replace('\r\n', '\n').replace('\n', '\r\n')
    with open(PATH, 'wb') as f:
        f.write(data.encode('utf-8'))
    print('\n[已写回] 以 CRLF 写回，写入字节数 =', len(data.encode('utf-8')))

    # 写回后二进制复核
    raw = open(PATH, 'rb').read()
    btext = raw.decode('utf-8')
    print('write-back binary-decode len:', len(btext), '(应 = after_len + CR数)')
    print('write-back CR count:', raw.count(b'\r'), '(应与术前一致 = LF数)')

if __name__ == '__main__':
    main()
