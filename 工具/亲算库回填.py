# -*- coding: utf-8 -*-
"""亲算库回填.py — 题目台账（题目台账预填.py 的 14 列格式）→ 亲算库行格式 机械转换草稿
用法: python 亲算库回填.py <题目台账.md> --line 线名 --date YYYY-MM-DD [-o 输出.md]
输出是**草稿**：答案要点列只搬机械答案、难度观察只并两列标签，须人工过目充实后再并入
素材普查/亲算库-*.md（并入时按「源文件＋题号」判重，已有行不重复登记、以新判定覆盖更新）。"""
import sys

SRC_COLS = ['源文件', '题号', '首句', '元素区间', '答案', '原难度', '原知识点', '图数',
            '档位', '亲算难度', '最晚知识点位置', '超纲判定', '组合归属', '典型性理由']

def main():
    args = sys.argv[1:]
    md, line, date, out = None, '未知线', '', '亲算库回填草稿.md'
    if '-o' in args:
        k = args.index('-o'); out = args[k+1]; args = args[:k] + args[k+2:]
    if '--line' in args:
        k = args.index('--line'); line = args[k+1]; args = args[:k] + args[k+2:]
    if '--date' in args:
        k = args.index('--date'); date = args[k+1]; args = args[:k] + args[k+2:]
    md = args[0]
    rows = []
    with open(md, encoding='utf-8') as f:
        for ln in f:
            s = ln.strip()
            if not s.startswith('|') or '---' in s:
                continue
            cols = [c.strip() for c in s.strip('|').split('|')]
            if len(cols) != len(SRC_COLS) or cols[1] == '题号':
                continue
            d = dict(zip(SRC_COLS, cols))
            ans = d['答案'] or '（待充实）'
            obs = '/'.join(x for x in (d['亲算难度'], d['原难度']) if x) or '（待充实）'
            note = '；'.join(x for x in (d['组合归属'], d['典型性理由']) if x)
            rows.append('| {}·{} | {} | {}（要点待充实） | {} | {} | {} | {}＋{} | {} |'.format(
                d['源文件'].replace('.docx', ''), d['题号'], d['档位'] or '（待定）', ans,
                d['最晚知识点位置'] or '（待填）', d['超纲判定'] or '（待填）', obs, line, date, note))
    with open(out, 'w', encoding='utf-8') as f:
        f.write('# 亲算库回填草稿（机械转换，须人工过目充实后并入亲算库）\n\n')
        f.write('| 源文件＋题号/块号 | 档位（全量/骨架） | 答案要点与关键步 | 最晚知识点位置 | 超纲判定 | 难度观察 | 产出线＋日期 | 备注 |\n')
        f.write('|---|---|---|---|---|---|---|---|\n')
        f.write('\n'.join(rows))
    print('OK 转换 %d 行 -> %s（记得人工过目：答案要点/难度观察需充实）' % (len(rows), out))

if __name__ == '__main__':
    main()
