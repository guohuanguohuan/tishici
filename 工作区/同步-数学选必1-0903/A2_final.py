# -*- coding: utf-8 -*-
"""A2 终验：⑦题干段清点恒等/tab与nbsp上下文样本/图中孤儿/I2灰底抽检材料/小图提取。只读。"""
import sys, io, os, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILES = {
 'X2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
NUMPAT = re.compile(r'^(\d+(?:\.\d+)+-\d+)．（(简单·保60%|中档·保80%|难·冲100%|衔接必会)·卡壳看答案）')

def para_text(p):
    return ''.join(t.text or '' for t in p.iter() if tag(t)=='t')

for code,path in FILES.items():
    print('='*90); print('【%s】'%code)
    z=zipfile.ZipFile(path)
    doc=etree.fromstring(z.read('word/document.xml'))
    body=doc.find(q('body'))
    paras=body.findall(q('p'))

    # ⑦ 题干段清点（题号块段起至含【答案】段前；白底维持面=以【答案】【知识点】【分析】【详解】【点睛】【编注】【大招指引】【题后反思】【温馨提醒】起头段、题型通式句；图段豁免；题型/讲部/节标题边界）
    n_stem=0; detail=[]
    in_q=False
    for idx,p in enumerate(paras):
        ppr=p.find(q('pPr'))
        pshd=None; pstyle=None
        if ppr is not None:
            sh=ppr.find(q('shd'))
            if sh is not None: pshd=sh.get(q('fill'))
            ps=ppr.find(q('pStyle'))
            pstyle=ps.get(q('val')) if ps is not None else None
        txt=para_text(p)
        if NUMPAT.match(txt): in_q=True
        if not in_q: continue
        # 边界：解析区起头段
        if re.match(r'^【(答案|知识点|分析|详解|点睛|编注|大招指引|题后反思|温馨提醒)】',txt) or txt.startswith('【编注】题型通式'):
            in_q=False; continue
        # 标题边界
        if pshd and pshd.upper() in ('ADC2DA','C6D4E3'):
            in_q=False; continue
        # 图段豁免
        if p.find('.//'+q('drawing')) is not None:
            continue
        n_stem+=1
    # 实测段级E0E0E0
    n_e0=0
    for p in paras:
        ppr=p.find(q('pPr'))
        if ppr is not None:
            sh=ppr.find(q('shd'))
            if sh is not None and (sh.get(q('fill')) or '').upper()=='E0E0E0': n_e0+=1
    print('题干段清点数=%d  段级E0E0E0=%d  差=%d  %s'%(n_stem,n_e0,n_e0-n_stem,'PASS' if n_stem==n_e0 else 'FAIL'))

    # tab上下文样本（3个）
    shown=0
    for idx,p in enumerate(paras):
        tabs=p.findall('.//'+q('tab'))
        if tabs and shown<3:
            # 重建带tab标记的文本
            out=[]
            for node in p.iter():
                if tag(node)=='t' and node.text: out.append(node.text)
                elif tag(node)=='tab': out.append('⟦TAB⟧')
                elif tag(node)=='drawing': out.append('⟦图⟧')
            print('  tab样本段[%d]: %s'%(idx,''.join(out)[:110]))
            shown+=1
    # nbsp选项样本（2个）
    shown=0
    for idx,p in enumerate(paras):
        txt=para_text(p)
        if re.search(r'\u00a0{2,}',txt) and re.match(r'^[A-D]．',txt) and shown<2:
            print('  nbsp选项段[%d]: %r'%(idx,txt[:100]))
            shown+=1
    # 题号块段内nbsp样本
    shown=0
    for idx,p in enumerate(paras):
        txt=para_text(p)
        if NUMPAT.match(txt) and '\u00a0' in txt and shown<2:
            i=txt.index('\u00a0')
            print('  题号块段含nbsp[%d]: %r'%(idx,txt[max(0,i-15):i+15]))
            shown+=1
    # 「图中」孤儿
    orph=[]
    for idx,p in enumerate(paras):
        txt=para_text(p)
        if '图中' in txt:
            has=False
            for j in range(max(0,idx-5),min(len(paras),idx+6)):
                if paras[j].find('.//'+q('drawing')) is not None: has=True
            if not has: orph.append((idx,txt[:50]))
    print('「图中」孤儿（±5窗）=%s'%(orph if orph else '无'))
    z.close()

# I2 灰底抽检材料：列出30处内容标记灰底run（条目号后、答案值）与其条目上下文
print('='*90); print('【I2 灰底标记抽检材料（内容标记族30处）】')
z=zipfile.ZipFile(FILES['I2'])
doc=etree.fromstring(z.read('word/document.xml'))
body=doc.find(q('body'))
paras=body.findall(q('p'))
picked=[]
for idx,p in enumerate(paras):
    runs=p.findall(q('r'))
    for ri,r in enumerate(runs):
        rpr=r.find(q('rPr'))
        if rpr is None: continue
        sh=rpr.find(q('shd'))
        if sh is None or (sh.get(q('fill')) or '').upper()!='C9C9C9': continue
        rt=''.join(t.text or '' for t in r.findall(q('t')))
        if rt and not re.match(r'^（\d+）$',rt) and not rt.startswith('【') and not re.match(r'^\d+(\.\d+)+-\d+．$',rt):
            picked.append((idx,ri,rt))
sel=picked[::max(1,len(picked)//22)][:22]
for idx,ri,rt in sel:
    ctx=para_text(paras[idx])
    print('  段[%d] run%d 灰底=%r | 段落=%s'%(idx,ri,rt[:30],ctx[:60]))
print('灰底答案值run总数=%d，抽样%d处'%(len(picked),len(sel)))
z.close()
print('DONE')
