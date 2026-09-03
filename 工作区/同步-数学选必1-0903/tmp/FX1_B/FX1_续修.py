# -*- coding: utf-8 -*-
"""FX1-B 续修·终版执行（保守逐处判定）
STRIP（去shd，值本身外）：8处
  - 整条答案值后的收尾终结符（值后句号）：p#180'．' p#617'．' p#632'。' p#678'。' p#918'．' p#1041'.' p#1061'．'
  - ①②子值间分隔符：p#225'；'
KEEP+登记（合法形态，不动）：27处
  - 值内分隔：p#151 3×'，'（坐标列表）、p#212','（x=6,y=15/2 单值）
  - 单值内连接：p#307 '(' ')'（DM⊥PC(或BM⊥PC) 单值含或）、p#632 '(' ')'（(1)(2)标签）
  - 值录入排版空格（标签与值间/值内）：p#283' ' p#632' ' p#918' ' p#1041' '
  - 子值边界标签括号：p#632(2) p#678(2) p#835(4) p#1061'（' p#1063'（）'
  - 连贯证明叙述（p#1061，单一答案值、叙述为值本体，非值外标点）
"""
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX1_B\unzipped\word\document.xml'
tree = etree.parse(DOC)
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def has_shd(run):
    rpr = run.find(f'{{{W}}}rPr')
    shd = rpr.find(f'{{{W}}}shd') if rpr is not None else None
    return shd is not None and shd.get(f'{{{W}}}fill') == 'C9C9C9'

def strip_shd(run):
    rpr = run.find(f'{{{W}}}rPr')
    shd = rpr.find(f'{{{W}}}shd') if rpr is not None else None
    if shd is not None and shd.get(f'{{{W}}}fill') == 'C9C9C9':
        rpr.remove(shd)
        return True
    return False

STRIP = [(180, '．'), (225, '；'), (617, '．'), (632, '。'),
         (678, '。'), (918, '．'), (1041, '.'), (1061, '．')]

log = []
done = 0
for pidx, txt in STRIP:
    p = paras[pidx]
    target = None
    for r in p:
        if etree.QName(r).localname != 'r':
            continue
        t = r.find(f'{{{W}}}t')
        if t is not None and t.text == txt:
            target = r
            break
    if target is None:
        log.append(f'[缺失] p#{pidx} 未找 run {txt!r}')
        continue
    if not has_shd(target):
        log.append(f'[无灰] p#{pidx} {txt!r} 无C9C9C9（跳过）')
        continue
    ok = strip_shd(target)
    assert not has_shd(target)
    done += 1
    log.append(f'[STRIP] p#{pidx} {txt!r} → 去灰 ✓')

print('执行日志：')
for l in log:
    print(' ', l)
print(f'\nSTRIP完成={done}/8')
assert done == 8
tree.write(DOC, xml_declaration=True, encoding='UTF-8', standalone=True)
print('已写回 document.xml')
