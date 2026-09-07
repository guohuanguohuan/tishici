# -*- coding: utf-8 -*-
import zipfile, re
from lxml import etree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP14 = "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"

for label, path in (("源文件", r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"),
                    ("输出样张", r"工作区/全品结构提取/数学选必一/样张v2/人教B版选必1-1.1.1-v2样张.docx")):
    z = zipfile.ZipFile(path)
    xml = z.read("word/document.xml").decode("utf-8")
    root = ET.fromstring(xml.encode())
    body = root.find(f"{{{W}}}body")
    kids = list(body)
    print("="*30, label, "="*30)
    # 找包含 drawing 的独立段落
    n = 0
    for i, el in enumerate(kids):
        if el.tag != f"{{{W}}}p": continue
        drs = el.findall(f".//{{{W}}}drawing")
        if not drs: continue
        in_tbl = False
        for dr in drs:
            n += 1
            host = dr[0]
            tag = host.tag.split('}')[1]
            ext = host.find(f"{{{WP}}}extent")
            cx, cy = int(ext.get("cx")), int(ext.get("cy"))
            # wp14 百分比
            pct = [ (e.tag.split('}')[1], e.attrib) for e in host.iter() if e.tag.startswith(f"{{{WP14}}}") ]
            # a:ext 全部
            aexts = [ (int(e.get("cx")), int(e.get("cy"))) for e in host.iter(f"{{{A}}}ext") ]
            # xfrm
            xf = host.find(f".//{{{A}}}xfrm")
            # blip 媒体
            blip = host.find(f".//{{{A}}}blip")
            rid = blip.get(f"{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}embed") if blip is not None else None
            # media 尺寸
            msz = ""
            if rid:
                tgt = None
                # 从 rels 拿
                rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
                for r in rels:
                    if r.get("Id") == rid: tgt = r.get("Target")
                if tgt:
                    try:
                        from PIL import Image
                        import io
                        im = Image.open(io.BytesIO(z.read("word/" + tgt)))
                        msz = f"{tgt} {im.size[0]}x{im.size[1]}px"
                    except Exception as ex:
                        msz = tgt + " (PIL不可用)"
            mc_wrap = ""
            par = dr.getparent()
            if par.tag == f"{{{MC}}}AlternateContent": mc_wrap = " [mc包裹]"
            print(f"段落#{i} drawing{n} {tag} extent={cx/360000:.1f}x{cy/360000:.1f}mm a:ext={[(a/360000, b/360000) for a,b in aexts]}mm wp14={pct} {msz}{mc_wrap}")
