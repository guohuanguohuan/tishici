# -*- coding: utf-8 -*-
"""全库对齐与垃圾图回扫（公共规则§5垃圾图清理＋§7左对齐无例外，2026-08-26首轮回扫）
用法：python 全库对齐垃圾图回扫.py scan|fix [--only 目录]
scan：只列命中不落盘；fix：左对齐规整＋安全垃圾图删除（双阈值＋像素空白核验）＋清理未引用媒体
范围：高中数学/高中数学同步、高中物理/高中物理同步、大学数学/大学数学同步 的主目录docx（旧体系存档冻结件除外）
改动登记（2026-08-30，FX4修0，公共规则§5工具升级门＋§7段落条款2026-08-30缩进梯子合法化）：
  fix模式删除原L88「re.sub(r'<w:ind [^>]*/>','',out)」无条件剥w:ind一行——垃圾图清理职责与缩进无关，
  w:ind 自2026-08-29/30成书形态拍板起系合法属性（标题缩进梯子＋册目录页层级缩进），fix模式不再剥除任何
  w:ind；ind 计数仅作 scan 诊断保留。自测：带缩进样本（leftChars=400×8）跑fix断言w:ind零变化。
"""
import zipfile, re, os, sys, io, shutil, tempfile

ROOT = r'C:\sync\syncall\ai\ai相关\提示词'
DIRS = ['高中数学/高中数学同步', '高中物理/高中物理同步', '大学数学/大学数学同步']

def files():
    out = []
    for d in DIRS:
        p = os.path.join(ROOT, d)
        if not os.path.isdir(p):
            continue
        for n in os.listdir(p):
            if n.endswith('.docx') and not n.startswith('~$'):
                out.append(os.path.join(p, n))
    return out

JC = re.compile(r'(<w:jc w:val=")(?:center|right|both|distribute|distributeLeft|distributeRight|start|end|thaiDistribute)(")')

def scan_docxml(xml):
    jc = len(JC.findall(xml))
    ind = len(re.findall(r'<w:ind [^>]*/>', xml))
    wpg = xml.count('<wpg:wgp>')
    return jc, ind, wpg

def blankish(data):
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data)).convert('RGBA')
    except Exception:
        return None
    w, h = img.size
    px = list(img.getdata())
    total = len(px)
    opaque = [p for p in px if p[3] > 40]
    if not opaque:
        return (w, h, True)
    nonwhite = sum(1 for p in opaque if not (p[0] > 245 and p[1] > 245 and p[2] > 245))
    return (w, h, nonwhite / max(1, len(opaque)) < 0.02)

def garbage_drawings(xml, z):
    """返回可安全删除的 r:embed rId 集合与段定位：显示<3磅 且 位图<50×50 且 像素近空白"""
    rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
    rid2t = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="media/([^"]+)"', rels))
    bad = set()
    for m in re.finditer(r'<w:drawing>.*?</w:drawing>', xml, re.S):
        d = m.group(0)
        if 'wpg:wgp' in d:
            continue
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', d)
        rid = re.search(r'r:embed="(rId\d+)"', d)
        if not (ext and rid):
            continue
        cx, cy = int(ext.group(1)), int(ext.group(2))
        if cx / 914400 * 72 >= 3 and cy / 914400 * 72 >= 3:
            continue
        t = rid2t.get(rid.group(1))
        if not t:
            continue
        data = None
        try:
            data = z.read('word/media/' + t)
        except KeyError:
            continue
        info = blankish(data)
        if info and info[0] < 50 and info[1] < 50 and info[2]:
            bad.add(rid.group(1))
    return bad

def fix_file(path, mode):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8')
        names = z.namelist()
        blob = {n: z.read(n) for n in names}
    jc0, ind0, wpg = scan_docxml(xml)
    bad = garbage_drawings(xml, zipfile.ZipFile(path))
    if mode == 'scan':
        return jc0, ind0, wpg, len(bad), 0
    out = xml
    njc = len(JC.findall(out))
    out = JC.sub(r'\1left\2', out)
    # 2026-08-30 FX4修0：删除原「nind=…; out=re.sub(r'<w:ind [^>]*/>','',out)」剥w:ind逻辑——
    # w:ind 系2026-08-29/30拍板后合法属性（标题缩进梯子/册目录页层级缩进），fix模式一律保留。
    nind = len(re.findall(r'<w:ind [^>]*/>', out))
    # 删除垃圾图所在 run（含drawing的整个w:r）
    ng = 0
    for rid in bad:
        pat = re.compile(r'<w:r(?: [^>]*)?>(?:(?!</?w:r[ >]).)*?r:embed="' + rid + r'"(?:(?!</w:r>).)*?</w:r>', re.S)
        out, k = pat.subn('', out)
        ng += k
    # 清未引用媒体与rel
    used = set(re.findall(r'r:embed="(rId\d+)"', out))
    rels = blob['word/_rels/document.xml.rels'].decode('utf-8')
    dropped_media = []
    def drop_rel(m):
        rid, target = m.group(1), m.group(2)
        if rid not in used and target.startswith('media/'):
            dropped_media.append('word/' + target)
            return ''
        return m.group(0)
    rels = re.sub(r'<Relationship Id="(rId\d+)"[^>]*Target="([^"]+)"[^>]*/>', drop_rel, rels)
    # 空run清理后的空段落保留（无害）
    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n in names:
            if n in dropped_media:
                continue
            if n == 'word/document.xml':
                zo.writestr(n, out)
            elif n == 'word/_rels/document.xml.rels':
                zo.writestr(n, rels)
            elif re.match(r'word/(footer|header)\d+\.xml$', n):
                # 页脚/页眉段落一律左对齐（§7无豁免条款）
                zo.writestr(n, JC.sub(r'\1left\2', blob[n].decode('utf-8')).encode('utf-8'))
            else:
                zo.writestr(n, blob[n])
    os.replace(tmp, path)
    return njc, nind, wpg, len(bad), ng

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    total = {}
    for f in files():
        jc, ind, wpg, bad, ng = fix_file(f, mode)
        if jc or ind or wpg or bad:
            print(f'{os.path.basename(f)[:40]} | jc非左:{jc} ind计数(不剥除):{ind} wpg组:{wpg} 垃圾图:{bad}' + (f' 已删run:{ng}' if mode == 'fix' else ''))
        total['jc'] = total.get('jc', 0) + jc
        total['ind'] = total.get('ind', 0) + ind
        total['wpg'] = total.get('wpg', 0) + wpg
        total['bad'] = total.get('bad', 0) + bad
    print('合计:', total)

if __name__ == '__main__':
    main()
