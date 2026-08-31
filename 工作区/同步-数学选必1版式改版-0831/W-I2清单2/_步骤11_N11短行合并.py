# -*- coding: utf-8 -*-
# W-I2 步骤11：N11枚举短行合并——零字符（只删段落边界），保留首段pPr
# 原则：①②③/（N）连续短项、拆句对（前段以，/：收尾后段续句）必并；
#       证明推导链、【结论】【证明】【注】标签块、（N）小标题、题名行/编注/节标题/图段/表格不并。
import zipfile, time, os
from lxml import etree
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
path='I2工作副本.docx'
merge_runs=[
 (54,59),(90,92),(94,96),(109,110),(129,130),(132,133),(208,210),(211,212),
 (240,243),(260,261),(276,278),(285,286),(287,288),(305,306),(349,350),
 (362,363),(365,366),(368,369),(383,387),(391,392),(394,395),(397,400),
 (411,412),(431,432),(444,445),(461,464),(485,487),(489,491),(493,494),
 (512,513),(514,515),(521,522),(523,524),(539,540),(545,546),(548,549),
 (559,562),(584,585),(588,589),(590,591),
]
zin=zipfile.ZipFile(path); parts={n:zin.read(n) for n in zin.namelist()}; zin.close()
root=etree.fromstring(parts['word/document.xml'])
body=root.find(W+'body'); els=list(body)
def ptxt(el): return ''.join(t.text or '' for t in el.iter(W+'t'))
# pre-checks: all targets are paragraphs, no images, ordered non-overlapping descending-safe
prev=-1
for a,b in merge_runs:
    assert a>prev, f'overlapping run at {a}'
    prev=b
    for i in range(a,b+1):
        el=els[i]
        assert el.tag==W+'p', f'{i} not paragraph'
        assert el.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip') is None, f'{i} has image'
merged=0
for a,b in sorted(merge_runs, reverse=True):
    first=els[a]
    for i in range(b,a,-1):
        p=els[i]
        for child in list(p):
            if child.tag==W+'pPr': continue
            first.append(child)
        body.remove(p)
        merged+=1
parts['word/document.xml']=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
tmp=path+'.tmp'
for _ in range(12):
    try:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
            for n,d in parts.items(): zo.writestr(n,d)
        os.replace(tmp,path); break
    except PermissionError: time.sleep(6)
print('merged paragraph boundaries removed:', merged, '| runs:', len(merge_runs))
