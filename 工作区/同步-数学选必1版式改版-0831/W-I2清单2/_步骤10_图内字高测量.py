# -*- coding: utf-8 -*-
# W-I2 步骤10辅助：图内最小字形视觉高估算（连通域高度法）
# pt高 = 组件像素高 × (28.35pt/cm) × 显示cm / 像素宽
import zipfile, io, re, csv
from PIL import Image
import numpy as np

z=zipfile.ZipFile('I2工作副本.docx')
rows=list(csv.DictReader(open('图片复扫.tsv',encoding='utf-8-sig'),delimiter='\t'))
print('tsv rows:',len(rows), 'cols:', list(rows[0].keys())[:14])
def min_text_pt(img, disp_cm):
    im=img.convert('L')
    a=np.array(im)
    H,W=a.shape
    mask=a<140
    if not mask.any(): return None,H,W
    # connected components via simple flood (scipy may not exist) - use union-find lite via labeling with numpy trick
    try:
        from scipy import ndimage
        lab,n=ndimage.label(mask)
        objs=ndimage.find_objects(lab)
        hs=[o[0].stop-o[0].start for o in objs if o is not None]
    except ImportError:
        # fallback: row-run heuristic — count dark pixel row-clusters per column
        hs=[]
        colvals=mask.sum(axis=0)
        # crude: use horizontal projection runs
        proj=mask.sum(axis=1)
        run=0
        for v in proj:
            if v>0: run+=1
            else:
                if run>0: hs.append(run); run=0
        if run>0: hs.append(run)
    if not hs: return None,H,W
    hs=sorted(hs)
    # 文本样组件：取25百分位（排除噪点1px与图形大块）
    txt=[h for h in hs if 3<=h<=max(8,H*0.25)]
    if not txt: return None,H,W
    hmin=txt[max(0,int(len(txt)*0.15))]
    pt=hmin*28.35*disp_cm/W
    return round(pt,1),H,W
out=[]
for r in rows:
    media=r['媒体文件']; 
    data=z.read('word/'+media)
    img=Image.open(io.BytesIO(data))
    disp=float(r['显示宽cm'].replace(',','.'))
    res=min_text_pt(img,disp)
    pxh,pxw=int(r['像素高']),int(r['像素宽'])
    pt=res[0] if res else None
    out.append((r['序号'],media,r['显示宽cm'],r['显示高cm'],pxw,pxh,pt))
    print(r['序号'],media,f"{r['显示宽cm']}x{r['显示高cm']}cm",f"{pxw}x{pxh}px",'minText≈',pt,'pt')
import json
json.dump(out,open('步骤10图内字高.json','w',encoding='utf-8'),ensure_ascii=False)
