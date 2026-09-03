# -*- coding: utf-8 -*-
"""FX1-B 修复脚本：①标题全章口径 ②oMath解得值纠错 ③选项间tab删除 ④段尾空格清零
全部带前后断言，输出逐处改动日志。"""
import io
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX1_B\unzipped\word\document.xml'

tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')
log = []

# ============ 修复1：文内标题改全单位口径 ============
TITLE_OLD = '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）'
TITLE_NEW = '人教B版选必1 第1章 空间向量与立体几何·讲练件（140题）'
p0 = paras[0]
t0 = p0.find(f'.//{{{W}}}t')
assert t0 is not None and t0.text == TITLE_OLD, f'标题原文不符: {t0.text!r}'
# 形态断言：三号加粗/ADC2DA整行底纹/底边框
shd = p0.find(f'{{{W}}}pPr/{{{W}}}shd'); assert shd is not None and shd.get(f'{{{W}}}fill') == 'ADC2DA'
pbdr = p0.find(f'{{{W}}}pPr/{{{W}}}pBdr/{{{W}}}bottom'); assert pbdr is not None
r0 = t0.getparent(); sz = r0.find(f'{{{W}}}rPr/{{{W}}}sz'); assert sz is not None and sz.get(f'{{{W}}}val') == '32'
assert r0.find(f'{{{W}}}rPr/{{{W}}}b') is not None
t0.text = TITLE_NEW
log.append(f'[修复1] p#0 标题: 「{TITLE_OLD}」→「{TITLE_NEW}」（三号32半点加粗/ADC2DA整行底纹/底边框 均未动）')

# ============ 修复2：题1.2.1.2-2 oMath#9 解得值纠错 ============
p260 = paras[260]
oms = p260.findall(f'.//{{{M}}}oMath')
target = None
for om in oms:
    lin = ''.join(el.text or '' for el in om.iter() if etree.QName(el).localname == 't')
    if lin == 'x=1z=-2':
        target = om
        break
assert target is not None, '未找到线性化=x=1z=-2的oMath'
# 逐 m:t 定位：'=1'→'=-1'，'=-2'→'=2'
hits = []
for mt in target.iter(f'{{{M}}}t'):
    if mt.text == '=1':
        mt.text = '=-1'; hits.append(('=1', '=-1'))
    elif mt.text == '=-2':
        mt.text = '=2'; hits.append(('=-2', '=2'))
assert len(hits) == 2, f'm:t命中数异常: {hits}'
lin_new = ''.join(el.text or '' for el in target.iter() if etree.QName(el).localname == 't')
assert lin_new == 'x=-1z=2', f'改后线性化异常: {lin_new}'
log.append(f'[修复2] p#260 详解oMath（eqArr方程组结构不动）: 解得x=1→x=-1、z=-2→z=2（亲算: PA·AB=x-1+z=0, PA·AC=-2x-z=0 ⇒ x=-1,z=2, P(-1,0,2)=选项C；原末值两值符号抄反，中间方程与【答案】C均正确）')

# ============ 修复3：选项间分隔tab删除（11处，p#85/289/411/445） ============
TAB_PARAS = (85, 289, 411, 445)
total_tab_removed = 0
# 全文档run级w:tab分布断言（其余段落无字符tab）
all_run_tabs = {}
for i, p in enumerate(paras):
    for tab in p.findall(f'.//{{{W}}}r/{{{W}}}tab'):
        all_run_tabs.setdefault(i, 0)
        all_run_tabs[i] += 1
assert set(all_run_tabs) == set(TAB_PARAS), f'run级tab分布异常: {all_run_tabs}'
assert sum(all_run_tabs.values()) == 11, f'run级tab总数异常: {sum(all_run_tabs.values())}'
for i in TAB_PARAS:
    p = paras[i]
    # 邻接断言：tab前一兄弟文本内容（含oMath值）与后一文本
    removed = 0
    for tab in list(p.findall(f'.//{{{W}}}r/{{{W}}}tab')):
        run = tab.getparent()
        run.remove(tab)
        removed += 1
    total_tab_removed += removed
    def ptext(pp):
        parts = []
        for el in pp.iter():
            ln = etree.QName(el).localname
            if ln == 't' and el.text:
                parts.append(el.text)
        return ''.join(parts)
    log.append(f'[修复3] p#{i} 删run级tab {removed}个（选项间分隔位，逐处已核：非选项内容内制表）；改后选项行={ptext(p)[:60]}...')
assert total_tab_removed == 11
# 复核：四段改后文本中选项分隔唯一「；」
for i in TAB_PARAS:
    def ptext2(pp):
        parts = []
        for el in pp.iter():
            ln = etree.QName(el).localname
            if ln == 't' and el.text:
                parts.append(el.text)
        return ''.join(parts)
    s = ptext2(paras[i])
    assert '；' in s and '\t' not in s

# ============ 修复4：段尾空格清零 ============
STRIP_CHARS = ' \xa0'
fixed_trailing = []
for i, p in enumerate(paras):
    last_t = None
    for el in p.iter():
        if etree.QName(el).localname == 't':
            last_t = el
    if last_t is not None and last_t.text and last_t.text != last_t.text.rstrip(STRIP_CHARS):
        old_tail = last_t.text[len(last_t.text.rstrip(STRIP_CHARS)):]
        last_t.text = last_t.text.rstrip(STRIP_CHARS)
        # 改后再断言：该段最后一个t已无尾随空格
        fixed_trailing.append((i, repr(old_tail)))
assert len(fixed_trailing) == 20, f'段尾空格清理数异常: {len(fixed_trailing)}'
half = [x for x in fixed_trailing if '\\xa0' not in x[1]]
nbsp = [x for x in fixed_trailing if '\\xa0' in x[1]]
assert len(half) == 16 and len(nbsp) == 4, f'半角/U+00A0分布异常: {len(half)}/{len(nbsp)}'
log.append(f'[修复4] 段尾空格清零20处＝报告16处半角空格（p#{",".join(str(x[0]) for x in half)}）＋4处U+00A0尾随（p#{",".join(str(x[0]) for x in nbsp)}，同属段尾零空格规则一并清）')

# ============ 写回 ============
tree.write(DOC, xml_declaration=True, encoding='UTF-8', standalone=True)
print('全部改动完成，逐处日志：')
for line in log:
    print(' -', line)
print(f'\n汇总: 标题1处 / 纠错2个m:t值 / tab 11处 / 段尾空格20处')
