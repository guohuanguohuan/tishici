# -*- coding: utf-8 -*-
"""A2 定点定位：H非段级E0E0E0/废止色1F4E79与000000/sz21run/tab与nbsp上下文/孤儿图引扩窗。只读。"""
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
def para_text(p):
    return ''.join(t.text or '' for t in p.iter() if tag(t)=='t')
def strip_ns(s):
    return re.sub(r'\sxmlns(:\w+)?="[^"]*"','',s)

for code,path in FILES.items():
    print('='*90); print('【%s】'%code)
    z=zipfile.ZipFile(path)
    doc=etree.fromstring(z.read('word/document.xml'))
    body=doc.find(q('body'))
    paras=body.findall(q('p'))
    raw=z.read('word/document.xml').decode('utf-8')

    # 1) E0E0E0 挂点分类
    ctx={}
    for m in re.finditer(r'E0E0E0', raw):
        s=max(0,m.start()-160)
        seg=raw[s:m.end()+40]
        # 判定挂点类型
        tail=raw[m.end():m.end()+200]
        head=raw[s:m.start()]
        if '<w:pPr>' in head[-120:] and '<w:rPr>' not in head[-60:]:
            k='pPr段级'
        elif '<w:pPr>' in head[-200:] and '<w:rPr>' in head[-60:]:
            k='pPr内rPr(段落标记)'
        elif '<w:tcPr>' in head[-200:]:
            k='tcPr表格'
        else:
            k='run级rPr'
        ctx[k]=ctx.get(k,0)+1
    print('E0E0E0挂点分类=%s'%ctx)
    if code=='H':
        # 找出非pPr段级样本3个
        shown=0
        for m in re.finditer(r'E0E0E0', raw):
            head=raw[max(0,m.start()-200):m.start()]
            if not ('<w:pPr>' in head[-120:] and '<w:rPr>' not in head[-60:]):
                print('  非段级样本: …%s…'%raw[max(0,m.start()-200):m.end()+30][-230:])
                shown+=1
                if shown>=3: break

    # 2) 颜色run计数
    for col in ('1F4E79','000000'):
        cnt=0; samples=[]
        for r in doc.iter(q('r')):
            rpr=r.find(q('rPr'))
            if rpr is None: continue
            c=rpr.find(q('color'))
            if c is not None and (c.get(q('val')) or '').upper()==col:
                cnt+=1
                if len(samples)<4:
                    rt=''.join(t.text or '' for t in r.findall(q('t')))
                    par=r.getparent()
                    while par is not None and tag(par)!='p': par=par.getparent()
                    samples.append((rt[:20], para_text(par)[:30] if par is not None else ''))
        # 段落标记rPr里的color（pPr/rPr）不算run
        print('w:color=%s run数=%d 样本=%s'%(col,cnt,samples))

    # 3) sz=21 run 定位
    n21=0; s21=[]
    for idx,p in enumerate(paras):
        for r in p.findall(q('r')):
            rpr=r.find(q('rPr'))
            if rpr is None: continue
            e=rpr.find(q('sz'))
            if e is not None and e.get(q('val'))=='21':
                n21+=1
                if len(s21)<6:
                    has_draw = r.find('.//'+q('drawing')) is not None
                    rt=''.join(t.text or '' for t in r.findall(q('t')))
                    s21.append((idx,'含图' if has_draw else '纯文本', repr(rt[:25]), strip_ns(etree.tostring(rpr,encoding='unicode'))[:200]))
    print('sz=21 run数=%d（正文顶层段）样例：'%n21)
    for s in s21: print('   段%s %s txt=%s rPr=%s'%s)
    # 数学区内sz21（m:r）
    m21=0
    for mr in doc.iter(qm_r:=('{%s}r'%M)):
        rpr=mr.find(q('rPr'))
        if rpr is not None:
            e=rpr.find(q('sz'))
            if e is not None and e.get(q('val'))=='21': m21+=1
    print('数学区m:r sz=21数=%d'%m21)

    # 4) w:tab 上下文分类
    tab_opt=0; tab_other=[]
    for idx,p in enumerate(paras):
        txt=para_text(p)
        isopt=bool(re.match(r'^[A-D]．',txt)) or bool(re.search(r'[A-D]．',txt[:6]))
        n=len(p.findall('.//'+q('tab')))
        if n:
            if isopt: tab_opt+=n
            elif len(tab_other)<6: tab_other.append((idx,n,txt[:40]))
    print('w:tab总数=%d 选项行内tab=%d 其他样例=%s'%(len(doc.findall('.//'+q('tab'))),tab_opt,tab_other))

    # 5) 孤儿图引扩窗±5
    orph=[]
    for idx,p in enumerate(paras):
        txt=para_text(p)
        if re.search(r'如图|图甲|图乙|图丙|图丁|图所示',txt):
            has=False
            for j in range(max(0,idx-5),min(len(paras),idx+6)):
                if paras[j].find('.//'+q('drawing')) is not None: has=True
            if not has: orph.append((idx,txt[:60]))
    print('孤儿图引（±5段窗）=%d：%s'%(len(orph),orph))

    # 6) 全角标点前空格复核（排除nbsp规定空格位）
    z.close()
print('DONE')
