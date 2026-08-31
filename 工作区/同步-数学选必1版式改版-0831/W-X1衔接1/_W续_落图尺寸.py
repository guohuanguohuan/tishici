# -*- coding: utf-8 -*-
# 图定尺寸落盘：按决策表改 wp:extent + a:xfrm/a:ext（保持纵横比），登记原/新尺寸
import zipfile, tempfile, os, time, sys, json
from lxml import etree

WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
RNS='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WPDNS='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
ANS='http://schemas.openxmlformats.org/drawingml/2006/main'
PICNS='http://schemas.openxmlformats.org/drawingml/2006/picture'
def q(t): return '{%s}%s'%(WNS,t)

# 决策表：media名 -> (新宽cm, 判据)
DEC = {
 'image1': (6.83, '缩至9pt目标(最小字母20px,原7.28cm/9.6pt)'),
 'image2': (4.62, '缩至9pt(20px,原4.93/9.6pt)'),
 'image3': (4.59, '缩至9pt(20px,原4.89/9.59pt)'),
 'image4': (7.68, '缩至9pt(20px,原8.2/9.61pt)'),
 'image5': (5.02, '缩至9pt(20px,原5.35/9.6pt)'),
 'image6': (5.65, '缩至9pt(21px,原6.33/10.08pt,段34+120两处drawing同改)'),
 'image7': (7.12, '缩至9pt(21px,原7.97/10.07pt,段37+136两处drawing同改)'),
 'image8': (5.48, '缩至9pt(20px,原5.84/9.6pt)'),
 'image9': (5.25, '缩至9pt(21px,原5.88/10.09pt)'),
 'image10': (4.93, '维持:150dpi上限4.93cm卡(9pt需7.7),12px→5.76pt低于6.5可辨底线——源图分辨率天花板'),
 'image11': (10.99, '缩至9pt(67px手写证明字,原12.82/10.49pt);高7.61cm<9'),
 'image12': (10.99, '缩至9pt(67px手写证明字,原12.82/10.49pt);高7.61cm<9'),
 'image13': (6.71, '放大至9pt(最小字母P/Q≈55px,原5.38/7.22pt);dpi150=19.66内;高6.64<9'),
 'image14': (9.09, '放大:9pt需12.33cm而高将达12.2cm超9cm上限→取高9cm(宽9.09),30px→6.66pt≥6.5达标(9pt与9cm高不可兼得,取高约束)'),
 'image15': (6.32, '维持:图内无任何文字标注(仅圆+直径线,视觉亲判),无可锚定字号,按内容密度维持原尺寸'),
 'image16': (9.52, '放大至9pt(最小字母≈24.6px,原5.95/5.63pt);dpi150=12.5内'),
 'image17': (4.97, '缩至9pt(20px,原5.3/9.6pt)'),
 'image18': (8.46, '放大至9pt(最小字母≈21.1px,原4.53/4.82pt);dpi150=9.52内'),
 'image19': (4.47, '缩至9pt(47px,原5.32/10.72pt)'),
 'image20': (4.10, '缩至9pt(32px,原5.1/11.2pt)'),
 'image21': (4.09, '缩至9pt(32px,原5.09/11.21pt)'),
 'image22': (9.54, '放大至9pt(最小字母≈21.1px,原5.1/4.81pt);高8.29<9;dpi150=10.72内'),
 'image23': (7.04, '维持:150dpi上限7.04卡(9pt需8.81),当前15px→7.2pt'),
 'image24': (7.53, '维持:=150dpi自然宽7.53,当前14px→6.72pt≥6.5'),
 'image25': (5.74, '维持:150dpi上限5.74卡(9pt需8.97),当前12px→5.76pt,低于6.5——源图分辨率天花板'),
 'image26': (7.97, '维持:150dpi上限7.97卡(9pt需11.5),当前13px→6.24pt略低于6.5——源图分辨率天花板'),
 'image27': (5.59, '缩至9pt(55px,原6.53/10.51pt)'),
 'image28': (6.76, '缩至9pt(21px,原7.57/10.08pt)'),
 'image29': (6.59, '缩至9pt(21px,原7.38/10.08pt)'),
 'image30': (8.87, '维持:150dpi上限8.87卡(9pt需11.88),当前14px→6.72pt≥6.5'),
 'image31': (8.48, '放大至9pt(21px,原6.3/6.68pt);dpi150=9.5内;高5.58<9'),
 'image32': (17.73, '维持:9pt需25.6cm超版心18,17.73cm下13px→6.24pt略低6.5——版心约束天花板;不放大至满宽18(仅+0.09pt无意义)'),
 'image33': (8.67, '维持:150dpi上限8.67卡(9pt需11.56),当前14px→6.75pt≥6.5'),
 'image34': (8.26, '维持:150dpi上限8.26卡,当前14px→6.72pt≥6.5'),
 'image35': (8.13, '维持:150dpi上限8.13卡,当前14px→6.75pt≥6.5'),
 'image36': (8.06, '维持:150dpi上限8.06卡(9pt需11.63),当前13px→6.24pt略低6.5——源图分辨率天花板'),
 'image37': (17.30, '缩至9pt(59px,原18.0/9.37pt);高4.98<9'),
 'image38': (5.53, '缩至9pt(60px,原6.68/10.87pt)'),
 'image39': (7.31, '缩至9pt(30px,原8.54/10.51pt)'),
 'image40': (7.26, '缩至9pt(30px,原8.47/10.5pt)'),
 'image41': (6.86, '缩至9pt(57px,原8.6/11.28pt)'),
 'image42': (5.57, '维持:150dpi上限5.57卡(9pt需6.53),当前16px→7.68pt≥6.5'),
 'image43': (4.30, '维持:150dpi上限4.30卡(9pt需4.46),当前18px→8.69pt接近9'),
 'image44': (4.23, '维持:150dpi上限4.23卡,当前16px→7.66pt≥6.5'),
 'image45': (4.25, '维持:150dpi上限4.25卡,当前16px→7.68pt≥6.5'),
 'image46': (5.47, '缩至9pt(21px,原6.13/10.08pt)'),
 'image47': (6.13, '放大至150dpi上限6.13(9pt需6.37微超),18px→8.65pt'),
 'image48': (1.71, '缩至150dpi自然宽1.71纠正超限(原2.65超150dpi硬限),12px→5.76pt低于6.5——150dpi硬限优先于可辨底线,源图分辨率天花板'),
 'image49': (6.81, '维持:150dpi上限6.81卡(9pt需7.96),当前16px→7.69pt≥6.5'),
 'image50': (11.46, '放大:9pt需15.3cm而高将达12cm超9cm上限→取高9cm(宽11.46),34px→6.74pt≥6.5达标(9pt与9cm高不可兼得,取高约束)'),
 'image51': (6.36, '缩至9pt(56px,原7.55/10.68pt)'),
 'image52': (6.36, '缩至9pt(56px,原7.55/10.68pt)'),
 'image53': (6.30, '维持:150dpi上限6.30卡(9pt需8.42),当前14px→6.74pt≥6.5'),
 'image54': (4.94, '缩至9pt(57px,原6.2/11.31pt)'),
 'image55': (12.00, '主会话裁决12.0×12.25cm等比缩(原16.32×16.62):按19px口径最小字母6.68pt≥6.5,大标18.6pt;高12.25>9cm系裁决明示放行(9pt目标与6.5下限不可兼得,源图分辨率天花板,取下限合规最小显示);续测右下小图字母12-15px口径更低,以裁决为准'),
}
PX = {  # media像素尺寸（图扫描.tsv）
 'image1':(430,285),'image2':(291,302),'image3':(289,291),'image4':(484,258),'image5':(316,227),
 'image6':(374,212),'image7':(471,266),'image8':(345,235),'image9':(347,242),'image10':(291,148),
 'image11':(2320,1607),'image12':(2320,1607),'image13':(1161,1149),'image14':(1161,1149),
 'image15':(853,770),'image16':(738,419),'image17':(313,163),'image18':(562,356),'image19':(661,411),
 'image20':(413,549),'image21':(412,547),'image22':(633,550),'image23':(416,270),'image24':(445,243),
 'image25':(339,141),'image26':(471,263),'image27':(969,537),'image28':(447,256),'image29':(436,250),
 'image30':(524,290),'image31':(561,369),'image32':(1047,244),'image33':(512,298),'image34':(488,440),
 'image35':(480,285),'image36':(476,329),'image37':(3214,926),'image38':(1045,926),'image39':(691,490),
 'image40':(686,491),'image41':(1232,722),'image42':(329,232),'image43':(254,291),'image44':(250,283),
 'image45':(251,282),'image46':(362,339),'image47':(362,358),'image48':(101,138),'image49':(402,279),
 'image50':(1657,1301),'image51':(1122,640),'image52':(1122,640),'image53':(372,261),'image54':(886,864),
 'image55':(964,984),
}

p = sys.argv[1]
z = zipfile.ZipFile(p)
doc = etree.fromstring(z.read('word/document.xml'))
rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
z.close()
rid2media = {}
for rel in rels:
    t = rel.get('Target')
    if t and 'media/' in t:
        rid2media[rel.get('Id')] = t.split('/')[-1].rsplit('.',1)[0]

body = doc.find(q('body'))
changed = []
log = []
for drawing in body.iter(q('drawing')):
    inline = drawing.find('{%s}inline' % WPDNS)
    if inline is None: continue
    blip = None
    for b in inline.iter('{%s}blip' % ANS):
        blip = b; break
    if blip is None: continue
    rid = blip.get('{%s}embed' % RNS)
    media = rid2media.get(rid)
    if media not in DEC: continue
    new_w_cm, why = DEC[media]
    pw, ph = PX[media]
    new_h_cm = new_w_cm * ph / pw
    cx = round(new_w_cm * 360000)
    cy = round(new_h_cm * 360000)
    ext = inline.find('{%s}extent' % WPDNS)
    old = (int(ext.get('cx')), int(ext.get('cy')))
    # a:xfrm/a:ext 同步
    ax = inline.find('.//{%s}xfrm/{%s}ext' % (ANS, ANS))
    ext.set('cx', str(cx)); ext.set('cy', str(cy))
    if ax is not None:
        ax.set('cx', str(cx)); ax.set('cy', str(cy))
    changed.append(media)
    log.append((media, old[0]/360000, old[1]/360000, new_w_cm, round(new_h_cm,2), why))

new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
fd,tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(p))); os.close(fd)
with zipfile.ZipFile(p) as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        zout.writestr(it, new_xml if it.filename=='word/document.xml' else zin.read(it.filename))
for k in range(10):
    try: os.replace(tmp,p); break
    except PermissionError: time.sleep(5)

print('改动drawing数:', len(changed), '涉及media:', len(set(changed)))
with open(os.path.join(os.path.dirname(os.path.abspath(p)), '登记-图定尺寸.md'), 'w', encoding='utf-8') as f:
    f.write('# 图片定尺寸登记（W-X1续跑，2026-08-31）\n\n')
    f.write('口径：公共规则§7图片内容感知定尺寸＋规格书§1图片条；目标图内最小文字/字母视觉高≈9pt、下限≥6.5pt、≤版心18cm（并排≤8.5）、单图高≤9cm（超限判据落盘）、禁超150dpi自然尺寸（显示宽cm≤像素宽÷59.06）、<200×200图标不动（本件无图标类）、信息密度可确认；只改显示尺寸（wp:extent＋a:xfrm/a:ext同步），不改图像文件。测量法：Otsu二值化连通域（程序实测）＋基线聚类串＋视觉亲判互校（55media全覆盖，4张总览拼图＋证据拼图＋8张单图细判）；透明底图（image11/12/15/50/51/52）白底合成后测量。\n\n')
    f.write('改动汇总：落盘 %d 处drawing（%d media）。改动类型：缩至9pt 27张｜放大至9pt/高约束 8张｜150dpi纠正 1张（image48）｜主会话裁决 1张（image55）｜维持 18张（150dpi/版心/无文字约束）。\n\n' % (len(changed), len(set(changed))))
    f.write('| media | 原宽cm | 原高cm | 新宽cm | 新高cm | 判据 |\n|---|---|---|---|---|---|\n')
    for m, ow, oh, nw, nh, why in log:
        f.write('| %s | %.2f | %.2f | %.2f | %.2f | %s |\n' % (m, ow, oh, nw, nh, why))
print('登记表已写 登记-图定尺寸.md')
