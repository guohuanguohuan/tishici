# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\提示词'
def rd(f): return open(os.path.join(R, f), encoding='utf-8').read()
ok = True
def chk(cond, msg):
    global ok
    print(('PASS' if cond else '!!FAIL'), msg)
    if not cond: ok = False

rules = ['公共规则.md','高中同步总控.md','二轮复习总控.md','强基竞赛总控.md','大学数学总控.md','ai自行经验积累.md','00总纲.md']
# ① 旧词族清零（规则层）
for w in ['方案A/B/C/D','A\u0027改制轮','A\u0027\u0027成品轮','紧凑化改版轮','后续卷仅文内开头标题',
          '只读与对用户汇报除外','不再就此征询','装订后各部分各成一套独立连续页码','背景：GitHub',
          '错题18半点','难档题补写','（A4双面约200张']:
    hits = [f for f in rules if w in rd(f)]
    chk(not hits, '旧词清零: '+w+('' if not hits else ' ←'+str(hits)))
# ② 前缀型替换的旧形态已挂新尾巴（旧串全库仅作为新串前缀存在）
for f in ['二轮复习总控.md','强基竞赛总控.md','大学数学总控.md']:
    t = rd(f)
    chk(t.count('文内开头标题与文件名完全一致（分卷照§8分卷例外）') == 1, f+' 分卷例外回指在位')
t = rd('高中同步总控.md')
chk('按教材章序衔接件→清单→讲练的章内顺序不变；物理册各章本之后册末依次排学史切片本、实验集训篇本' in t, '同步总控 册末学史/实验落位句在位')
chk('＋第1章首个部分（数学＝衔接件、物理＝知识清单）' in t, '同步总控 物理首本构成句在位')
chk('文内标题照§8分卷例外' in t and '按章内顺序枚举' in t, '同步总控 任务F④/枚举措辞')
# ③ 正向在位
g = rd('公共规则.md')
chk(g.count('〔方案A/B/C〕') == 1, '公共规则 方案A/B/C')
chk('一切决策与执行（拍板、写文件、推送、只读检查、向用户汇报均在内——无任何豁免、随时交流）' in g, '门条款无豁免裁定落正文')
chk('落盘工作区本轮子文件夹，未落盘视同未商议；多智能体下子代理关键判定经主会话汇总后统一过门' in g, '商议记录落盘位＋子代理边界')
chk(g.count('随首跑轮/回扫轮升级') == 2 and g.count('随首跑轮/回扫轮统一清零') == 1, '存量指针三处统一（2升级＋1清零）')
chk('文内开头标题仅首卷（照§8分卷例外）' in g and '文内开头标题照§8分卷例外' in g, '§12两处分卷口径')
chk(g.count('⑦**分片轮换') == 1 and '⑧**分片轮换' not in g, '§1 ⑦⑧重编号')
chk('底纹仍只盖题号本身；细则见高中同步总控任务C）加粗' in g, 'L103括号配平修复')
for f in ['二轮复习总控.md','强基竞赛总控.md','大学数学总控.md','ai自行经验积累.md']:
    chk('本n/共M本' in rd(f), f+' 页眉同串含本n/共M本')
e = rd('ai自行经验积累.md')
chk('均在提示词/工具/ 下' in e, '经验护栏残句补全')
chk('（分卷照§8分卷例外）' in e, '经验L25分卷回指')
chk('存量件随首跑/回扫轮升级' in e, '经验存量指针')
k = rd('进度看板.md')
chk('错题记录件生成.py随件废止退役' in k and '错题18半点' not in k and '全档位补写' in k, '看板三处')
# ④ len 实测（§15）
print()
BUDGET = {'进度看板.md':6000,'ai自行经验积累.md':12000,'公共规则.md':50000,'高中同步总控.md':20000,
          '大学数学总控.md':4000,'二轮复习总控.md':3000,'强基竞赛总控.md':3000,'00总纲.md':3500}
for fn in ['00总纲.md','公共规则.md','高中同步总控.md','二轮复习总控.md','强基竞赛总控.md','大学数学总控.md','进度看板.md','ai自行经验积累.md']:
    n = len(rd(fn)); b = BUDGET[fn]
    chk(n <= b, f'len实测 {fn}: {n}/{b}')
print('\n总体:', 'ALL PASS' if ok else 'FAIL')
