# -*- coding: utf-8 -*-
import zipfile, io
from lxml import etree as ET
from PIL import Image as PIL

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

z = zipfile.ZipFile(r"工作区/全品结构提取/数学选必一/样张v2/人教B版选必1-1.1.1-v2样张.docx")
rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("word/_rels/document.xml.rels"))}
body = ET.fromstring(z.read("word/document.xml")).find(f"{{{W}}}body")
n = 0
for i, el in enumerate(body):
    if el.tag != f"{{{W}}}p": continue
    for dr in el.findall(f".//{{{W}}}drawing"):
        n += 1
        host = dr[0]
        ext = host.find(f"{{{WP}}}extent")
        aexts = [(e.get("cx"), e.get("cy")) for e in host.iter(f"{{{A}}}ext")]
        blip = host.find(f".//{{{A}}}blip")
        rid = blip.get(f"{{{R}}}embed") if blip is not None else None
        msz = ""
        if rid and rels.get(rid):
            try:
                im = PIL.open(io.BytesIO(z.read("word/" + rels[rid])))
                msz = f"{rels[rid]} {im.size[0]}x{im.size[1]}px dpi={im.info.get('dpi')}"
            except Exception as e:
                msz = rels[rid] + f" err={e}"
        # srcRect / stretch
        sr = host.find(f".//{{{A}}}srcRect")
        print(f"段#{i} drawing{n} extent=({int(ext.get('cx'))/360000:.1f},{int(ext.get('cy'))/360000:.1f})mm "
              f"a:ext={[(int(a)/360000 if a else -1, int(b)/360000 if b else -1) for a,b in aexts]}mm "
              f"srcRect={'有' if sr is not None else '无'} {msz}")
