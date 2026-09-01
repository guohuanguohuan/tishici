# -*- coding: utf-8 -*-
"""一次性脚本（E3讲练B）——归一化diff对账：基线B副本 vs B_终.docx
逐段文本（w:t+m:t文档序）比对；差异逐笔分类登记（授权差异①—⑥类）；
正文段差异（授权外）必须为0。空段（环绕删除的空图段）单独清点不入文字diff。"""
import zipfile, re, json, difflib
from lxml import etree

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(W,t)

def para_list(path):
    z=zipfile.ZipFile(path)
    doc=etree.fromstring(z.read('word/document.xml'))
    hdr=''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', z.read('word/header1.xml').decode('utf-8')))
    ftr=''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', z.read('word/footer1.xml').decode('utf-8')))
    z.close()
    body=doc.find(q('body'))
    out=[]
    for el in body:
        if el.tag==q('p'):
            t=''.join(x.text or '' for x in el.iter() if isinstance(x.tag,str) and etree.QName(x).localname=='t')
            out.append(t)
        else:
            out.append('<%s>'%etree.QName(el).localname)
    return out, hdr, ftr

base,hdr0,ftr0 = para_list(r"C:\提示词\工作区\同步-数学选必1册改制轮-0901\E执行\E3讲练B\工作\B.docx")
fin,hdr1,ftr1 = para_list(r"C:\提示词\工作区\同步-数学选必1册改制轮-0901\E执行\E3讲练B\工作\B_终.docx")

# 空白归一（仅比较非空内容；空段/纯空白段差异系环绕删空图段，单独计）
def norm(s): return re.sub(r'\s+','',s)
base_n=[norm(x) for x in base]
fin_n=[norm(x) for x in fin]

sm=difflib.SequenceMatcher(None, base_n, fin_n, autojunk=False)
ops=sm.get_opcodes()
cats={'①题号重编':[], '②统计段区间括注删除':[], '④节名锚段插入':[], '其他差异':[]}
n_eq=n_del_empty=n_ins_empty=0
for tag,i1,i2,j1,j2 in ops:
    if tag=='equal':
        n_eq+=i2-i1; continue
    if tag=='delete':
        for k in range(i1,i2):
            s=base_n[k]
            if s=='' : n_del_empty+=1; continue
            cats['其他差异'].append(('delete',k,base[k][:60]))
    elif tag=='insert':
        for k in range(j1,j2):
            s=fin_n[k]
            if s=='': n_ins_empty+=1; continue
            if re.match(r'^\d+(\.\d+)+ \S+$', s) and s in fin_rawset if False else False:
                pass
            # 锚段：纯「节号 节名」形（与节标题前缀一致且短）
            if re.match(r'^\d+(\.\d+)+ [^\d]', s) and len(s)<40 and any(x.startswith(s) and len(x)>len(s) for x in fin_n if x):
                cats['④节名锚段插入'].append((k, fin[k][:60])); continue
            cats['其他差异'].append(('insert',k,fin[k][:60]))
    else:  # replace
        # 逐段配对分析（同段改写：题号重编/区间括注删除）
        for k in range(i1,i2):
            bs=base_n[k]
            # 在新侧找对应段（j侧同位移近似配对——replace块内通常等长）
            kj=j1+(k-i1) if j1+(k-i1)<j2 else None
            fs=fin_n[kj] if kj is not None else ''
            if bs=='' and fs=='': continue
            if bs=='' : n_del_empty+=1; continue
            if fs=='': n_ins_empty+=1; continue
            # 分类：题号token替换 or 区间括注删除
            b_raw, f_raw = base[k], (fin[kj] if kj is not None else '')
            iv=re.sub(r'（第[0-9．\-—–~～]+题）','',b_raw)
            iv_n=norm(iv)
            if iv_n==fs:
                cats['②统计段区间括注删除'].append((k, b_raw[:70], f_raw[:70])); continue
            # 题号重编：旧「N．（…」→新「节号-序号．（…」
            mb=re.match(r'^(\d+)．（(简单|中档|难)·(保60%|保80%|冲100%)·卡壳看答案）(.*)$', b_raw)
            mf=re.match(r'^(\d+(?:\.\d+)+-\d+)．（(简单|中档|难)·(保60%|保80%|冲100%)·卡壳看答案）(.*)$', f_raw)
            if mb and mf and mb.group(2)==mf.group(2) and mb.group(4)==mf.group(4):
                cats['①题号重编'].append((k, mb.group(1), mf.group(1))); continue
            # 条目重编（裸号）
            mb2=re.match(r'^(\d+)．(.*)$', b_raw); mf2=re.match(r'^(\d+(?:\.\d+)+-\d+)．(.*)$', f_raw)
            if mb2 and mf2 and mb2.group(2)==mf2.group(2):
                cats['①题号重编'].append((k, mb2.group(1)+'(条目)', mf2.group(1))); continue
            cats['其他差异'].append(('replace',k,b_raw[:60],f_raw[:60]))

# 页眉页脚差异（授权③）
hf={'页眉_前':hdr0,'页眉_后':hdr1,'页脚_前':ftr0,'页脚_后':ftr1}

print('equal段:', n_eq, '| 空白段删除(环绕删空图段计入):', n_del_empty, '| 空白段新增:', n_ins_empty)
for k,v in cats.items():
    print(k, len(v), ('样例:', v[:2]) if v else '')
print('页眉页脚:', {k:(v[:60] if v else v) for k,v in hf.items()})

out={'equal':n_eq,'空段删除':n_del_empty,'空段新增':n_ins_empty,
     '分类计数':{k:len(v) for k,v in cats.items()},
     '①题号重编明细':cats['①题号重编'],'②区间括注明细':cats['②统计段区间括注删除'],
     '④锚段明细':cats['④节名锚段插入'],'其他差异明细':cats['其他差异'],
     '页眉页脚':hf}
json.dump(out, open(r"C:\提示词\工作区\同步-数学选必1册改制轮-0901\E执行\E3讲练B\登记\09_归一化diff对账.json",'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('落盘 -> 登记/09_归一化diff对账.json')
