# -*- coding: utf-8 -*-
"""题目台账预填.py — 从源 docx 机械提取题目字段，生成题目台账 markdown 骨架
用法: python 题目台账预填.py <docx路径...> [-o 输出.md]
机械列（源文件、题号、首句、答案、原难度/知识点标签、图数、元素区间）由本脚本提取；
判定列（档位/亲算难度/最晚知识点/超纲/组合归属/典型性理由）留空，**必须由会话亲自填写，
禁止脚本代填**（公共规则§3）。元素区间与 dump_docx.py --index 同序号体系，
可用 `dump_docx.py --slice` 定点回读原文。
可复用工具：四条产品线题目台账通用。"""
import sys, os
from dump_docx import body_elements, is_qstart, label_val

JUDGE_COLS = ['档位(全量/骨架)', '亲算难度(简/中/难)', '最晚知识点位置', '超纲判定', '组合归属', '典型性理由']

def build(paths):
    lines = ['# 题目台账（预填骨架）',
             '',
             '> 机械列由 工具/题目台账预填.py 提取，仅供登记底稿；判定列必须亲自填写（公共规则§3亲算纪律）。',
             '> 元素区间对应 dump_docx.py 序号体系，回读原文用 --slice。', '']
    total = 0
    for src in paths:
        els = body_elements(src)
        starts = [(i, q) for i, tag, text in els if tag == 'p' and (q := is_qstart(text)) is not None]
        rows = []
        for k, (i, q) in enumerate(starts):
            j = starts[k+1][0] - 1 if k + 1 < len(starts) else els[-1][0]
            block = '\n'.join(t for ii, tag, t in els if i <= ii <= j and t is not None)
            first = next((t.strip() for ii, tag, t in els if ii == i and t), '')[:36].replace('|', '／')
            rows.append('| {} | {} | {} | {}-{} | {} | {} | {} | {} |'.format(
                os.path.basename(src), q, first.replace('\n', ' '), i, j,
                label_val(block, '答案'), label_val(block, '难度'),
                label_val(block, '知识点'), block.count('【图】')))
        total += len(rows)
        lines.append('## {}（题块 {}）'.format(os.path.basename(src), len(rows)))
        lines.append('')
        lines.append('| 源文件 | 题号 | 首句(36字) | 元素区间 | 答案 | 原难度 | 原知识点 | 图数 | ' +
                     ' | '.join(JUDGE_COLS) + ' |')
        lines.append('|' + '---|' * (8 + len(JUDGE_COLS)))
        lines.extend(rows)
        lines.append('')
    return lines, total

def main():
    args = sys.argv[1:]
    out = '题目台账预填.md'
    if '-o' in args:
        k = args.index('-o')
        out = args[k+1]
        args = args[:k] + args[k+2:]
    lines, total = build(args)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('OK 题块合计={} -> {}'.format(total, out))

if __name__ == '__main__':
    main()
