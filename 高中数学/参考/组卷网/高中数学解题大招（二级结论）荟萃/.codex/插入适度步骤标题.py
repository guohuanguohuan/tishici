from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from copy import deepcopy
from pathlib import Path
import os, tempfile

DOCX = Path(r'04_原始资料\模块1集合简易逻辑与不等式\模块1大招5三角换元.docx')
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
NS={'w':W,'m':M}
qn=lambda ns,tag:f'{{{ns}}}{tag}'

def ptext(p):
    out=[]
    for n in p.iter():
        if n.tag in (qn(W,'t'), qn(M,'t')) and n.text:
            out.append(n.text)
    return ''.join(out).strip()

def find_para(pars, needle, starts=False):
    import re
    clean=lambda s: re.sub(r"\s+", "", s)
    n=clean(needle)
    hits=[]
    for p in pars:
        t=clean(ptext(p))
        if (t.startswith(n) if starts else n in t):
            hits.append(p)
    if len(hits)!=1:
        raise RuntimeError(f'Anchor {needle!r}: expected 1 hit, got {len(hits)}: {[ptext(x)[:80] for x in hits]}')
    return hits[0]

def split_before_child(p, child_index):
    parent=p.getparent()
    p2=etree.Element(qn(W,'p'), nsmap=p.nsmap)
    pPr=p.find(qn(W,'pPr'))
    if pPr is not None:
        p2.append(deepcopy(pPr))
    moving=list(p)[child_index:]
    for ch in moving:
        p.remove(ch)
        p2.append(ch)
    parent.insert(parent.index(p)+1,p2)
    return p2

def heading_before(anchor, title):
    hp=etree.Element(qn(W,'p'), nsmap=anchor.nsmap)
    srcPr=anchor.find(qn(W,'pPr'))
    pPr=deepcopy(srcPr) if srcPr is not None else etree.Element(qn(W,'pPr'))
    # Keep heading with the next paragraph.
    if pPr.find(qn(W,'keepNext')) is None:
        pPr.append(etree.Element(qn(W,'keepNext')))
    spacing=pPr.find(qn(W,'spacing'))
    if spacing is None:
        spacing=etree.SubElement(pPr, qn(W,'spacing'))
    spacing.set(qn(W,'before'),'100')
    spacing.set(qn(W,'after'),'40')
    hp.append(pPr)
    r=etree.SubElement(hp, qn(W,'r'))
    rPr=etree.SubElement(r, qn(W,'rPr'))
    etree.SubElement(rPr, qn(W,'b'))
    color=etree.SubElement(rPr, qn(W,'color')); color.set(qn(W,'val'),'1F4E79')
    t=etree.SubElement(r, qn(W,'t')); t.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); t.text=title
    anchor.addprevious(hp)
    return hp

with ZipFile(DOCX,'r') as zin:
    xml=zin.read('word/document.xml')
    root=etree.fromstring(xml)
    pars=root.xpath('//w:body/w:p',namespaces=NS)

    # Split the two compact example analyses so each step title sits before its own derivation.
    p124=find_para(pars,'【解析】设P点的坐标为',starts=True)
    # Split before the run “，所以” (original top-level child 13).
    p124b=split_before_child(p124,13)
    p173=find_para(pars,'【解析】由于(2x-y)2+4y2=1',starts=True)
    # Split before “，则原式” (original top-level child 7).
    p173b=split_before_child(p173,7)

    # Rebuild paragraph list after splits, then resolve all anchors before inserting anything.
    pars=root.xpath('//w:body/w:p',namespaces=NS)
    specs=[]
    def add(needle,title,starts=False):
        specs.append((find_para(pars,needle,starts),title))

    # 典例1
    add('解析：由根式有意义可知','第一步　完成三角换元',True)
    add('因为θ+φ∈','第二步　利用角度范围求值域',True)

    # 典例2：三种方法分别连续编号
    add('不妨令c→=(3,0),b→=(2cosθ','第一步　建立坐标与参数方程',True)
    add('因此原等式有解的充要条件为','第二步　求参数的可行范围',True)
    add('|b→−c→|2=','第三步　表示目标式并求范围',True)

    add('同法一建立平面直角坐标系','第一步　建立坐标模型',True)
    add('先证明二维柯西不等式','第二步　应用柯西不等式',True)
    add('由于v→=(sinα,cosα)可以表示任意单位向量','第三步　验证可取性并回到目标式',True)

    add('令t=b→·c→','第一步　引入数量积参数',True)
    add('因为0≤cos2β≤1','第二步　求参数范围并验证充分性',True)
    add('由向量减法的模长公式','第三步　回到目标式',True)

    # 典例3（已拆分）
    specs.append((p124,'第一步　参数化圆上点'))
    specs.append((p124b,'第二步　表示距离平方并求最值'))

    # 典例4（已拆分）
    specs.append((p173,'第一步　对平方和作三角换元'))
    specs.append((p173b,'第二步　表示目标式并求最大值'))

    # 第8题
    add('【详解】令u=logax,v=logay','第一步　对数换元并化为圆',True)
    add('由于u≥0,v≥0，圆','第二步　参数化可行圆弧',True)
    add('∴当sin(θ+π4)=1时','第三步　求目标范围并核对端点',True)

    # 第17题：仅对复杂的（1）方法3和（2）分步
    add('方法3：由a2+b2+c2=1得','第一步　固定变量并参数化',True)
    add('原等式关于θ有解的充要条件为','第二步　判断方程有解并求范围',True)
    add('（2）由4a2-2ab+4b2-c=0得','第一步　配方并参数化',True)
    add('要使|2a+b|最大','第二步　确定极值的取等条件',True)
    add('若sinω+α=1','第三步　分类回代并比较',True)

    # 第18题
    add('【详解】（1）由于4≤x≤5','第一步　根据定义域完成换元',True)
    add('∵0≤α≤π2','第二步　结合角度范围求最值',True)
    add('（2）函数的定义域为R，令x=tanθ','第一步　用正切换元化简',True)
    add('由于-π2<θ<π2','第二步　分段判断值域',True)
    add('∵2x2-4x+6=2(x-1)2+4','第一步　配方并完成三角换元',True)
    add('设u=2+sinθcosθ，其中|θ|<π2。由于cosθ>0','第二步　转化为方程有解问题',True)
    add('由y=2u+1，得函数的值域','第三步　回到原函数值域',True)
    add('设u=2+sinθcosθ，其中|θ|<π2。令P','第一步　建立右半圆斜率模型',True)
    add('设过点A的直线为y+2=kx','第二步　利用直线与圆的位置关系',True)
    add('（4）令r=x2+y2','第一步　使用极坐标参数化',True)
    add('于是z=x2−xy+y2','第二步　分离半径与角度求最值',True)

    if len(specs)!=34:
        raise RuntimeError(f'Expected 34 headings, got {len(specs)}')
    for anchor,title in specs:
        heading_before(anchor,title)

    outxml=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone='yes')
    fd,tmpname=tempfile.mkstemp(suffix='.docx',dir=str(DOCX.parent)); os.close(fd)
    try:
        with ZipFile(tmpname,'w',ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data=outxml if item.filename=='word/document.xml' else zin.read(item.filename)
                zout.writestr(item,data)
        import shutil
        shutil.copyfile(tmpname,DOCX)
    finally:
        if os.path.exists(tmpname): os.unlink(tmpname)

print(f'Inserted {len(specs)} step headings and split 2 compact analysis paragraphs.')

