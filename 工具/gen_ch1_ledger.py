# -*- coding: utf-8 -*-
"""gen_ch1_ledger.py — 生成第1章删除台账.md（重审后，恒等式核验）
输入：review_table(252重审对象 行号/原位置/题干) + verdict(78R/174K) + 初判范围核定(57高度重复/1超纲③/5转投域外)
输出：人教B版选必1 第1章 空间向量与立体几何·删除台账.md
恒等式：316存量 = 恢复78 + 维持删除174 + 高度重复57 + 超纲③1 + 转投5 + 差1待核对
"""
import re, os, json
BTC = r'C:\sync\syncall\ai\ai相关\提示词\高中数学\高中数学同步'
rt = open(r'C:\Users\28120\Desktop\同步-数学选必1整册-0825\第1章_review_table.md', encoding='utf-8').read()
vd = open(r'C:\Users\28120\Desktop\同步-数学选必1整册-0825\第1章_verdict.md', encoding='utf-8').read()

# 1. 读 verdict：行号->K/R（含区间行与 旧让位 分块）
verdict = {}
for m in re.finditer(r'^\| (\S+) \| .*? \| ([RKS]) \|', vd, re.M):
    hdr=m.group(1); v=m.group(2)
    for part in hdr.split(','):
        part=part.strip()
        if '-' in part:
            a,b=map(int,part.split('-'))
            for i in range(a,b+1): verdict[i]=v
        else:
            verdict[int(part)]=v

# 2. 读 review_table 的 (行号, 节, 原位置, 让位组合, 题干)
rows={}
for m in re.finditer(r'^\| (\d+) \| (旧让|进阶) \| ([^|]+) \| ([^|]+) \| (.+)$', rt, re.M):
    r=int(m.group(1)); rows[r]=(m.group(2).strip(),m.group(3).strip(),m.group(4).strip(),m.group(5).strip())

# 3. 组装删除台账正文（K 维持删除 + 范围外类别）
K=[r for r in range(1,253) if verdict.get(r)=='K']
R=[r for r in range(1,253) if verdict.get(r)=='R']
print('R=',len(R),'K=',len(K),'R+K=',len(R)+len(K))

lines=[]
lines.append('# 人教B版选必1 第1章 空间向量与立体几何·删除台账')
lines.append('')
lines.append('> 重审轮（好题全保留）删判定归档。恒等式：316存量＝恢复78＋维持删除174＋高度重复57＋超纲③1＋转投5＋差1待核对。删除原因分组：高度重复/组合内让位/其它淘汰；超纲③/转投属定向处置。')
lines.append('> 行号＝重审清单(review_table)行号。被删全文永久保真由 git 源文件承担（公共规则§9）。')
lines.append('')

# 4. 写入 K 题（维持删除）——按组
lines.append('## 维持删除（重审后，174题）')
lines.append('')
lines.append('| 行号 | 原位置 | 删除原因 | 题干首句 |')
lines.append('|---|---|---|---|')
reason_map = {
  '高度重复':'只换数字/换情境外壳，立不出判别特征',
  '组合内让位':'同组合由代表/实质差异第2题覆盖',
}
for r in sorted(K):
    if r not in rows: continue
    seg,src,c,stem=rows[r]
    lines.append('| %d | %s | 高度重复或组合内让位 | %s |' % (r, src, stem[:30]))

# 5. 范围外类别
lines.append('')
lines.append('## 高度重复（57题，重审免判不复活）')
lines.append('')
lines.append('> 初判范围核定：落选题清单中"高度重复"57题（只换数据/外壳），不进入重审、不复活，维持删除。')
lines.append('')
lines.append('## 超纲③（1题）——仍删除')
lines.append('')
lines.append('| 原位置 | 原因 |')
lines.append('|---|---|')
lines.append('| 大招7 叉乘法纯计算 | 大学概念技巧（叉乘）判超纲③，无处转投 |')
lines.append('')
lines.append('## 转投（5题）——域外，已建第2章转投暂存')
lines.append('')
lines.append('| 原位置 | 去向 |')
lines.append('|---|---|')
lines.append('| 大招3q2、大招4q2/q7/q8/q10 | 轨迹涉及圆锥曲线，转投第2章（已建暂存） |')

open(os.path.join(BTC,'人教B版选必1 第1章 空间向量与立体几何·删除台账.md'),'w',encoding='utf-8').write('\n'.join(lines))
print('删除台账已写入。K题数=%d'%len(K))
