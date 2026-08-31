# -*- coding: utf-8 -*-
# W-I2 步骤12：排版自检①~⑧全量＋清单件加核（数字全落盘）
import zipfile, re, json
from lxml import etree
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
z=zipfile.ZipFile('I2工作副本.docx')
root=etree.fromstring(z.read('word/document.xml'))
body=root.find(W+'body'); els=list(body)
def ptxt(el): return ''.join(t.text or '' for t in el.iter(W+'t'))
out={}
# ①结构：目录块清零（连续标题堆叠＞2）；节标题后首段=条目题名行或下级节标题
heads=[(i,ptxt(e)) for i,e in enumerate(els) if e.tag==W+'p' and re.match(r'^\d+(\.\d+)+\s',ptxt(e))]
out['节标题数']=len(heads)
stack=0; maxstack=0; dirblock=0
for i,e in enumerate(els):
    if e.tag==W+'p' and (re.match(r'^\d+(\.\d+)+\s',ptxt(e))): stack+=1; maxstack=max(maxstack,stack)
    elif e.tag==W+'p' and not ptxt(e).strip() and e.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip') is None: continue
    else: stack=0
out['最大连续标题堆叠']=maxstack
# 题名行序列1..67
nums=[]
for i,e in enumerate(els):
    if e.tag==W+'p':
        m=re.match(r'^(\d{1,3})．',ptxt(e))
        if m: nums.append(int(m.group(1)))
out['条目题名行数']=len(nums)
out['序列连续1..67']= (nums==list(range(1,68)))
# ③空段
empty=0; consec=0; maxc=0
prev_empty=False
for e in els:
    if e.tag==W+'p':
        t=ptxt(e).strip()
        img=e.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip') is not None
        om=e.find('.//'+M+'oMath') is not None
        ise = (not t) and not img and not om
        if ise:
            empty+=1
            if prev_empty: consec+=1
            maxc=max(maxc,consec if prev_empty else 1)
            prev_empty=True
        else: prev_empty=False; consec=0
out['空段数']=empty; out['最大连续空段']=maxc
# ④原卷结构标题残留
resid=[ptxt(e)[:30] for e in els if e.tag==W+'p' and re.match(r'^(一|二|三|四|五|六|七|八|九|十)、|^(（一）|（二）|（三）)|^考点\d|^题型\d|^第\d+讲',ptxt(e))]
out['原卷结构标题残留']=len(resid)
# ⑤页脚（现状记录——待M1重盖）
foot=z.read('word/footer1.xml').decode('utf-8')
out['页脚含NUMPAGES']='NUMPAGES' in foot
out['页脚含fldSimple']='fldSimple' in foot
out['页脚复杂域个数']=foot.count('fldChar')
m=re.search(r'<w:t[^>]*>([^<]{0,40})</w:t>',foot)
out['页脚首文本']=m.group(1) if m else None
setx=z.read('word/settings.xml').decode('utf-8')
out['settings含updateFields']='updateFields' in setx
# ⑥样式残留与禁排
cnt=lambda p: len(root.findall('.//'+W+p))
out['w:ins']=cnt('ins'); out['w:del']=cnt('del')
out['彩色run']=sum(1 for c in root.iter(W+'color') if c.get(W+'val') not in ('auto','000000','1F4E79',None))
out['删除线run']=sum(1 for s in root.iter(W+'strike') if s.get(W+'val') not in ('0','false','none',None))
out['突出显示run']=sum(1 for h in root.iter(W+'highlight'))
out['pageBreakBefore']=cnt('pageBreakBefore'); out['keepNext']=cnt('keepNext'); out['keepLines']=cnt('keepLines')
out['手动分页w:br page']=sum(1 for b in root.iter(W+'br') if b.get(W+'type')=='page')
out['w:br文本换行']=sum(1 for b in root.iter(W+'br') if b.get(W+'type') is None)
out['wp:anchor']=len(root.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}anchor'))
out['oMathPara块级公式段']=cnt('oMathPara')
out['w:bdr字符边框']=cnt('bdr')-2*19 if False else sum(1 for b in root.iter(W+'bdr')) # pBdr含4边×19段
# 孤字行：行末1~2汉字收尾段（近似——段文本<4字）
out['超短段(≤3字非空)']=sum(1 for e in els if e.tag==W+'p' and 0<len(ptxt(e).strip())<=3)
# ⑦编号：第一子层（N）序列同层连续检查＋块内多题号
subs=[]
for e in els:
    if e.tag==W+'p':
        m=re.match(r'^（(\d{1,2})）',ptxt(e))
        if m: subs.append(int(m.group(1)))
out['（N）子层行数']=len(subs)
# ⑧格式继承
sz={}; spacing={}; ind=0; jc={}
for p in root.iter(W+'p'):
    ppr=p.find(W+'pPr')
    sp=None; j=None
    if ppr is not None:
        e=ppr.find(W+'spacing')
        if e is not None: sp=(e.get(W+'line'),e.get(W+'lineRule'))
        jj=ppr.find(W+'jc'); j=jj.get(W+'val') if jj is not None else None
        if ppr.find(W+'ind') is not None: ind+=1
    spacing[sp]=spacing.get(sp,0)+1
    jc[j]=jc.get(j,0)+1
out['段落spacing分布']={str(k):v for k,v in spacing.items()}
out['jc分布']=jc
out['w:ind段数']=ind
# run字号（含继承docDefaults=24）
fonts={}
for r in root.iter(W+'r'):
    rpr=r.find(W+'rPr'); s=None
    if rpr is not None:
        e=rpr.find(W+'sz')
        if e is not None: s=e.get(W+'val')
    t=''.join(x.text or '' for x in r.findall(W+'t'))
    if not t: continue  # 纯图run不计
    fonts[s]=fonts.get(s,0)+1
out['文本run字号分布(继承=24)']=fonts
# docDefaults
st=z.read('word/styles.xml').decode('utf-8')
m=re.search(r'<w:rPrDefault>.*?</w:rPrDefault>',st,re.S); out['rPrDefault']=re.sub(r'xmlns[^ ]*','',m.group(0))[:220] if m else None
m=re.search(r'<w:pPrDefault>.*?</w:pPrDefault>',st,re.S); out['pPrDefault']=m.group(0)[:200] if m else None
# 深蓝字
out['深蓝1F4E79文本run']=sum(1 for c in root.iter(W+'color') if c.get(W+'val')=='1F4E79')
# 清单件加核
txt=''.join(t.text or '' for t in root.iter(W+'t'))
out['基标记']=txt.count('〔基〕'); out['进标记']=txt.count('〔进〕')
out['图例行在位']='〔基〕＝基础必会：必须学完本条目，才能做本章题目｜〔进〕＝进阶汇总' in txt
bz=txt.count('【编注】'); out['编注数']=bz
out['对比辨析数']=txt.count('对比辨析——')
# §12
import os
out['文件大小MB']=round(os.path.getsize('I2工作副本.docx')/1048576,2)
# 主题字体禁用
out['styles.xml主题字体minorHAnsi']= 'minorHAnsi' in st
json.dump(out,open('步骤12自检.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for k,v in out.items(): print(f'{k}: {v}')
