# -*- coding: utf-8 -*-
import io

P = r'C:\提示词\ai自行经验积累.md'
s = io.open(P, encoding='utf-8').read()
orig_len = len(s)

pairs = []

# a. 本轮教训条目措辞紧缩（语义保留）
pairs.append((
"- 2026-09-02 A''体系修订轮（双栏改制20项拍板落库）——已固化§2/§5/§6/§7/§11/§14/§15；独有教训：条款逐字写死的成品文案入规则前必须按版面宽度预检（61字图例行单行必折行等5笔由用户点名发现）——已落库§2读者视角观感门＋§15固定文案先见实物＋43条全量复评",
"- 2026-09-02 A''体系修订轮（双栏改制拍板20项落库）——已固化§2/§5/§6/§7/§11/§14/§15；独有教训：逐字写死的成品文案入规则前必须按版面宽度预检（61字图例行单行必折行等5笔用户点名）——已落库§2读者视角观感门＋§15固定文案先见实物＋43条全量复评"
))

# b. 三卷装配纯指针句压缩（要点指针在「构建与重编号坑」「空行折叠」条已有）
pairs.append((
"- 续跑接管先找工作区本轮子文件夹定位分界；题号正则只认全角「．」；三卷装配要点不在此重列——游离sectPr归位、选项正序合并、emf/wmf兜底与get_or_add_image、空段清理公式感知分见「构建与重编号坑」「选项合并」条、0825历轮、trim_tail_empty条；页脚旧成品须按现行规范重建",
"- 续跑接管先找工作区本轮子文件夹定位分界；题号正则只认全角「．」；三卷装配要点（游离sectPr归位/选项正序合并/emf-wmf兜底/空段清理公式感知）分见「构建与重编号坑」「选项合并」条；页脚旧成品须按现行规范重建"
))

# c. wpg句修饰删
pairs.append((
"wpg组合图形包着的图Word可能不渲染（压扁且导出不可见）——判定须PDF渲染过目",
"wpg组合图形包着的图Word可能不渲染——判定须PDF渲染过目"
))

# d. 样式挂载括注紧缩
pairs.append((
"新建样式basedOn须指向该件真实Normal styleId（字面量'Normal'部分件悬空、样式链断解析值丢）",
"新建样式basedOn须指向该件真实Normal styleId（字面量悬空即样式链断）"
))

for i, (old, new) in enumerate(pairs, 1):
    c = s.count(old)
    assert c == 1, "pair %d count=%d" % (i, c)
    s = s.replace(old, new)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
lines = s.count('\n') + (0 if s.endswith('\n') else 1)
print("exp2 OK: %d -> %d (budget 12000), lines=%d (budget 200)" % (orig_len, len(s), lines))
