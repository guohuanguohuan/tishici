# -*- coding: utf-8 -*-
# W-I2 步骤10：内容感知定尺寸落地——7张图放大（目标≈9pt/下限6.5pt，受版心18cm/单图高9cm/150dpi自然尺寸三上限约束）
import zipfile, time, os
from lxml import etree
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WP='{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
path='I2工作副本.docx'
# media -> new display cm (width)
plan={
 'image12.png': 14.48,  # 9pt目标命中（高7.52≤9、≤150dpi 18.61）
 'image14.png': 13.32,  # 高度9cm界（8.0pt）
 'image18.png':  7.64,  # 高度9cm界（4.8pt，下限不可达登记）
 'image22.png': 10.10,  # 高度9cm界（5.3pt，下限不可达登记）
 'imageW2062.png':4.23, # 150dpi上限命中（6.7pt≥6.5达标）
 'image17.png': 12.66,  # 高度9cm界（4.4pt，下限不可达登记）
 'image21.png':  9.84,  # 高度9cm界（3.8pt，下限不可达登记）
}
zin=zipfile.ZipFile(path); parts={n:zin.read(n) for n in zin.namelist()}; zin.close()
root=etree.fromstring(parts['word/document.xml'])
rels=etree.fromstring(parts['word/_rels/document.xml.rels'])
rid2media={r.get('Id'):r.get('Target').split('/')[-1] for r in rels}
changed=0
for d in root.iter(WP+'inline'):
    blip=d.find('.//'+A+'blip')
    if blip is None: continue
    media=rid2media.get(blip.get(R+'embed'))
    if media not in plan: continue
    ext=d.find(WP+'extent')
    oldw=int(ext.get('cx'))/360000
    ratio=int(ext.get('cy'))/int(ext.get('cx'))
    neww=int(plan[media]*360000); newh=int(neww*ratio)
    # 三上限断言
    assert plan[media]<=18.0
    assert newh/360000<=9.0+1e-6, media
    ext.set('cx',str(neww)); ext.set('cy',str(newh))
    xfrm=d.find('.//'+A+'xfrm')
    ae=xfrm.find(A+'ext')
    ae.set('cx',str(neww)); ae.set('cy',str(newh))
    changed+=1
    print(f'{media}: {oldw:.2f} -> {plan[media]:.2f}cm (h={newh/360000:.2f}cm)')
parts['word/document.xml']=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
tmp=path+'.tmp'
for _ in range(12):
    try:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
            for n,d in parts.items(): zo.writestr(n,d)
        os.replace(tmp,path); break
    except PermissionError: time.sleep(6)
print('changed drawings:',changed)
