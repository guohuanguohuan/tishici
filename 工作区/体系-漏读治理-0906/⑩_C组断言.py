# -*- coding: utf-8 -*-
# ⑩轮C组验收断言。C1守恒：基线=⑩_改前快照（勿git HEAD）。双侧同法归一：
#   剥换行符、行首缩进、行首项目符号、「▽留痕：」前缀（含行内，标记即行内插入）、摘要行号数字。
#   EOL原样保持单独核验。许可改动单独diff展示：①摘要L19/L20/L21概括刷新 ②头部源文件/生成日期/覆盖断言行＋覆盖自检重算行。
# C2：全库规则件无>1000字符行。C3：留痕清单/歧义清单落盘存在性核验。
import pathlib, re, difflib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SNAP = ROOT / '工作区/体系-漏读治理-0906/⑩_改前快照'
MARK = '▽留痕：'
RULES = ['公共规则.md', '附则/PDF导出链.md', '附则/主脑协审制.md', '附则/代理节点处置.md', '附则/元素守恒断言.md',
         '附则/双栏首页断言.md', '附则/多机协作与工具纪律.md', '附则/多脑调用登记.md', '附则/故障先修纪律.md',
         '附则/网上打印成书口径.md', '附则/节标题栏顶规则.md', '附则/表格规范.md', '附则/规则巡检.md',
         '附则/讲练件底纹减法.md', '附则/跨脑复审计制.md', '附则/页脚零占位例外.md', '附则/页面与页码细则.md',
         '大学数学总控.md', '二轮复习总控.md', '高中同步总控.md', '强基竞赛总控.md', '00总纲.md']
SUMMARY = '公共规则·目录摘要.md'

def norm_rule(text):
    s = text.replace(MARK, '')
    lines = [re.sub(r'^[\s>-]+', '', L) for L in re.split(r'\r\n|\n', s)]
    return ''.join(lines)

print('== C1 守恒断言（规则件，基线=⑩_改前快照）==')
ok_all = True
for f in RULES:
    old = (SNAP / f).read_bytes().decode('utf-8')
    cur = (ROOT / f).read_bytes()
    curd = cur.decode('utf-8')
    a, b = norm_rule(old), norm_rule(curd)
    eq = a == b
    eol_ok = (cur.count(b'\r\n') == cur.count(b'\n')) or (cur.count(b'\r') == 0)
    ok_all &= eq and eol_ok
    print(f'  {f}: 归一逐字符全等={eq} 原EOL保持={eol_ok}')
assert ok_all, 'C1 规则件守恒失败'

print('== C1 摘要（行号数字同法剥）==')
old = (SNAP / SUMMARY).read_bytes().decode('utf-8')
cur = (ROOT / SUMMARY).read_bytes().decode('utf-8')
def norm_sum(s):
    s = s.replace(MARK, '')
    s = re.sub(r'L\d+', 'L#', s)
    s = re.sub(r'(?<=L#-)\d+', '#', s)
    s = re.sub(r'(?<=·)\d+', '#', s)
    return ''.join(re.sub(r'^[\s>-]+', '', L) for L in re.split(r'\r\n|\n', s))
a, b = norm_sum(old), norm_sum(cur)
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
resid = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != 'equal':
        resid.append((a[max(0,i1-12):i2][:90], b[j1:j2][:120]))
print(f'  归一后残余差异数={len(resid)}（应全部属许可两类）')
for x in resid:
    print('   ◇', x[0].replace(chr(10),'⏎'), ' ⇒ ', x[1].replace(chr(10),'⏎'))

print('== C2 全库规则件超长行 ==')
bad = []
for f in RULES + [SUMMARY]:
    for i, L in enumerate((ROOT / f).read_bytes().decode('utf-8').replace('\r\n', '\n').split('\n'), 1):
        if len(L) > 1000:
            bad.append((f, i, len(L)))
print('  >1000字符行:', bad if bad else '无（通过）')

print('== C3 清单落盘 ==')
for f in ['⑩_留痕标记清单.md', '⑩_留痕歧义清单.md', '⑩_拆段映射表.md']:
    p = ROOT / '工作区/体系-漏读治理-0906' / f
    n = len([x for x in p.read_text(encoding='utf-8').split('\n') if x.startswith('- ')])
    print(f'  {f}: 条目{n} 存在={p.exists()}')
