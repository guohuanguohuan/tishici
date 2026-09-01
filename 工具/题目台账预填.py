# -*- coding: utf-8 -*-
"""题目台账预填.py — 从源 docx 机械提取题目字段，生成题目台账 markdown 骨架
用法: python 题目台账预填.py <docx路径...> [-o 输出.md]
机械列（源文件、题号、首句、答案、原难度/知识点标签、图数、元素区间）由本脚本提取；
判定列（档位/亲算难度/最晚知识点/超纲/组合归属/典型性理由）留空，**必须由会话亲自填写，
禁止脚本代填**（公共规则§3）。元素区间与 dump_docx.py --index 同序号体系，
可用 `dump_docx.py --slice` 定点回读原文。
可复用工具：四条产品线题目台账通用。
2026-09-01 升级（A'改制轮·工具债③·T3）：层级制题号识别（公共规则§6编号唯一层形——同步线
「节号-序号．」）——题号列照出层级制号（如「1.1.1-5」）；旧全局「N．」照跑（双形态兼容）；
层级制骨架按节分组列出节内序列供人工过目（§7⑦编号核验素材）。"""
import sys, os, re
from dump_docx import body_elements, is_qstart, label_val

HNUM_RE = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){1,3})-(\d{1,3})．')

JUDGE_COLS = ['档位(全量/骨架)', '亲算难度(简/中/难)', '最晚知识点位置', '超纲判定', '组合归属', '典型性理由']

def hier_qstart(text):
    """层级制题号「1.1.1-5．」→ '1.1.1-5'；旧形态回退 is_qstart。"""
    if not text:
        return None
    t = text.strip()
    if len(t) >= 8:
        m = HNUM_RE.match(t)
        if m:
            return '%s-%s' % (m.group(1), m.group(2))
    return is_qstart(t)

def build(paths):
    lines = ['# 题目台账（预填骨架）',
             '',
             '> 机械列由 工具/题目台账预填.py 提取，仅供登记底稿；判定列必须亲自填写（公共规则§3亲算纪律）。',
             '> 元素区间对应 dump_docx.py 序号体系，回读原文用 --slice。题号支持层级制「节号-序号」与旧全局「N」双形态。', '']
    total = 0
    for src in paths:
        els = body_elements(src)
        starts = [(i, q) for i, tag, text in els if tag == 'p' and (q := hier_qstart(text)) is not None]
        rows = []
        groups = {}
        hier_byssec = {}
        for k, (i, q) in enumerate(starts):
            j = starts[k+1][0] - 1 if k + 1 < len(starts) else els[-1][0]
            block = '\n'.join(t for ii, tag, t in els if i <= ii <= j and t is not None)
            first = next((t.strip() for ii, tag, t in els if ii == i and t), '')[:36].replace('|', '／')
            kp = label_val(block, '知识点') or '（无标签）'
            ans = label_val(block, '答案')
            if '【答案】' not in block:
                ans = '⚠无答案块（讲块内部条目或答案在表格内，人工判定是否入台账）'
            groups.setdefault(kp, []).append(str(q))
            m = re.match(r'^(\d+(?:\.\d+)+)-\d+$', str(q))
            if m:
                hier_byssec.setdefault(m.group(1), []).append(str(q))
            rows.append('| {} | {} | {} | {}-{} | {} | {} | {} | {} | {} |'.format(
                os.path.basename(src), q, first.replace('\n', ' '), i, j,
                ans, label_val(block, '难度'), kp, block.count('【图】'),
                ' | '.join([''] * len(JUDGE_COLS))))
        total += len(rows)
        lines.append('## {}（题块 {}）'.format(os.path.basename(src), len(rows)))
        lines.append('')
        if hier_byssec:
            lines.append('> 层级制题号骨架（§7⑦编号核验素材——逐节序列须连续无重复，人工过目）：'
                         + '；'.join('节%s：%s' % (s, '、'.join(v)) for s, v in hier_byssec.items()))
            lines.append('')
        lines.append('| 源文件 | 题号 | 首句(36字) | 元素区间 | 答案 | 原难度 | 原知识点 | 图数 | ' +
                     ' | '.join(JUDGE_COLS) + ' |')
        lines.append('|' + '---|' * (8 + len(JUDGE_COLS)))
        lines.extend(rows)
        lines.append('')
        lines.append('### 组合归组草稿（按原【知识点】标签分组——仅起点参考）')
        lines.append('')
        lines.append('> 真实归组按判别特征亲自定（各总控选题规则：五维度硬门槛）；'
                     '源标签常偏细/偏粗，本分组只提供分堆起点，不构成组合结论。')
        lines.append('')
        for kp in sorted(groups, key=lambda k: -len(groups[k])):
            lines.append('- **{}**（{}题）：{}'.format(kp, len(groups[kp]), '、'.join(groups[kp])))
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
