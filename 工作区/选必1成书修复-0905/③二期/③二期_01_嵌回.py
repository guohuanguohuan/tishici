# -*- coding: utf-8 -*-
"""③二期 嵌回执行器：20 张新图替换进 清单1/清单2/上61/下79 四件。
主脑裁决：嵌回一律用原 wp:extent（零版面回流）；B 族辅助点 N 不补。
srcRect 复核处置：
  - 清单1 image17：新图已转正 → 除 srcRect + 除 xfrm rot/flipH/flipV（extent 不动）
  - 清单1 image18 / 上61 sub3_B_17：原为手机照裁边放置（wp:extent=5.08x9.00，a:ext=6.38x9.00，
    PDF 实测渲染=5.07x7.16）→ 除 srcRect，a:ext 收窄为 1827391x2570731（5.08x7.142cm，
    与今日渲染框全等），wp:extent 不动
  - 其余 17 张无 srcRect/rot，纯媒体字节替换
等比处置：新图画布比例与显示比例失配 >1.5% 者白边 letterbox 加画布（零裁剪零缩放零变形），
<=1.5% 原字节直嵌。jpg 原件改名 .png（rels Target 同步改，[Content_Types].xml 四件均已有 png Default 零改动）。
断言：oMath 对锚 / w:t 零差 / 白名单外零 diff / 引用无悬空无孤儿 / 新图灰阶300dpi / wp:extent 与 rId 原值。
"""
import zipfile, hashlib, io, json, os, re, shutil, sys, time
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = r'C:/提示词'
SYNC = os.path.join(ROOT, '高中数学/高中数学同步')
WS   = os.path.join(ROOT, '工作区/选必1成书修复-0905/③二期')
PRE  = os.path.join(WS, '副本_嵌入前')
OUT  = os.path.join(ROOT, '工作区/选必1成书修复-0905/②工具/副本_③')
NEWIMG = os.path.join(ROOT, '工作区/选必1成书修复-0905/③图重绘')
REPORT = os.path.join(ROOT, '工作区/选必1成书修复-0905/②工具/报告')
for d in (PRE, OUT, REPORT):
    os.makedirs(d, exist_ok=True)

SYNC_MD5_ANCHOR = {  # ②E_MD5_回写.md
    '清单1': 'b3175eae9d57742f66621549a48f1b0b',
    '清单2': 'cf79bdc95a8f9d8b092e158477831482',
    '上61':  '139722a461839f6fc15bba20e1afbc44',
    '下79':  'fbe2cd47290b0d60049669516aa0ef49',
}
OMATH_ANCHOR = {'清单1': 396, '清单2': 1156, '上61': 3251, '下79': 2876}  # 2026-09-06 同步盘 XML 实测逐件坐实（锚序＝清单1,衔接1,上61,下79,清单2,衔接2,92,90,68,89）
PAD_T = 0.015

DOCS = {
    '清单1': ('人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', {
        'image17.jpg': dict(new='I1_image17.png', mode='rename_derotate'),
        'image18.jpg': dict(new='I1_image18.png', mode='rename_shrink_aext'),
    }),
    '清单2': ('人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', {
        'image3.png': dict(new='I2_image3.png', mode='replace'),
        'image4.png': dict(new='I2_image4.png', mode='replace'),
        'image5.png': dict(new='I2_image5.png', mode='replace'),
        'image6.png': dict(new='I2_image6.png', mode='replace'),
        'image25.png': dict(new='I2_image25.png', mode='replace'),
        'image26.png': dict(new='I2_image26.png', mode='replace'),
        'image27.png': dict(new='I2_image27.png', mode='replace'),
        'image28.png': dict(new='I2_image28.png', mode='replace'),
        'image29.png': dict(new='I2_image29.png', mode='replace'),
        'image30.png': dict(new='I2_image30.png', mode='replace'),
        'image31.png': dict(new='I2_image31.png', mode='replace'),
        'image32.png': dict(new='I2_image32.png', mode='replace'),
        'imageW2044.png': dict(new='I2_imageW2044.png', mode='replace'),
    }),
    '上61': ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', {
        'image76.png': dict(new='B_image76.png', mode='replace'),
        'image77.png': dict(new='B_image77.png', mode='replace'),
        'image78.png': dict(new='B_image78.png', mode='replace'),
        'sub3_B_17.jpg': dict(new='B_sub3_B_17.png', mode='rename_shrink_aext'),
    }),
    '下79': ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', {
        'image294.png': dict(new='C_image294.png', mode='replace'),
    }),
}
# 与今日渲染框全等的 a:ext（EMU）：宽=wp:extent.cx，高=宽×(原裁剪高/宽比)
SHRINK_AEXT = (1827391, 2570731)

def md5(b): return hashlib.md5(b).hexdigest()
def log(msg): print(msg, flush=True)

def robust_copy(src, dst, tries=3, timeout=300):
    for i in range(tries):
        try:
            shutil.copy2(src, dst)
            if md5(open(dst,'rb').read()) == md5(open(src,'rb').read()):
                return True
        except Exception as e:
            log(f'  copy try{i+1} err={e}')
        time.sleep(2)
    return False

def rels_map(rels_bytes):
    root = ET.fromstring(rels_bytes)
    return {r.get('Id'): (r.get('Target'), r.get('Type'), r.get('TargetMode') or '') for r in root}

def drawing_block(xml, rid):
    for m in re.finditer(r'<w:drawing>.*?</w:drawing>', xml, re.S):
        if re.search(r'r:embed="%s"' % rid, m.group(0)):
            return m.start(), m.end(), m.group(0)
    return None

def grayscale_ok(im):
    if im.mode == 'L':
        return True, 'L'
    if im.mode == 'RGBA':
        a = im.getchannel('A').getextrema()
        rgb = im.convert('RGB')
        arr = __import__('numpy').array(rgb).reshape(-1, 3).astype(int)
        chroma = int((arr.max(1) - arr.min(1)).max())
        return (a == (255, 255) and chroma == 0), f'RGBA alpha={a} chroma={chroma}'
    return False, im.mode

results = {}
ONLY = sys.argv[1] if len(sys.argv) > 1 else None
for code, (fn, targets) in DOCS.items():
    if ONLY and code != ONLY:
        continue
    log(f'====== {code} ======')
    sync_path = os.path.join(SYNC, fn)
    pre_path = os.path.join(PRE, f'{code}.docx')
    out_path = os.path.join(OUT, f'{code}.docx')
    r = {'targets': {}}
    # 1. 字节复制（FX-2 范式）
    assert robust_copy(sync_path, pre_path), f'{code} 同步盘复制失败'
    pre_bytes = open(pre_path, 'rb').read()
    assert md5(pre_bytes) == SYNC_MD5_ANCHOR[code], f'{code} 复制件 MD5 ≠ ②-E 锚'
    sync_now = md5(open(sync_path, 'rb').read())
    assert sync_now == SYNC_MD5_ANCHOR[code], f'{code} 同步盘 MD5 漂移'
    r['pre_md5'] = md5(pre_bytes)

    zin = zipfile.ZipFile(io.BytesIO(pre_bytes))
    names = zin.namelist()
    data = {n: zin.read(n) for n in names}
    compress = {i.filename: i.compress_type for i in zin.infolist()}
    doc_xml = data['word/document.xml'].decode('utf-8')
    rels_xml = data['word/_rels/document.xml.rels'].decode('utf-8')
    rmap = rels_map(data['word/_rels/document.xml.rels'])
    rid_of = {}
    for rid, (tg, _, _) in rmap.items():
        base = tg.split('/')[-1]
        if base in targets:
            assert base not in rid_of, f'{base} 多 rId 引用'
            rid_of[base] = rid
    assert set(rid_of) == set(targets), f'{code} 目标 rels 缺失: {set(targets)-set(rid_of)}'
    # 目标媒体仅被 document.xml.rels 引用（无其他 rels 牵连、无其他部件文本提及）
    for n in names:
        if n.endswith('.rels') and n != 'word/_rels/document.xml.rels':
            for base in targets:
                assert base not in data[n].decode('utf-8', 'ignore'), f'{base} 被 {n} 引用'
    for n in names:
        if n.endswith('.xml') and not n.endswith('.rels'):
            t = data[n].decode('utf-8', 'ignore')
            for base in targets:
                assert base not in t, f'{base} 被 {n} 文本提及'

    expected_media_changed = set()
    expected_xml_changed = set()
    if any(v['mode'].startswith('rename') for v in targets.values()):
        expected_xml_changed.add('word/_rels/document.xml.rels')

    # 2. 逐目标处置
    new_doc_xml = doc_xml
    new_rels = rels_xml
    for base, spec in targets.items():
        rid = rid_of[base]
        s, e, blk = drawing_block(new_doc_xml, rid)
        assert blk, f'{base} drawing 块未找到'
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', blk).groups()
        aext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', blk)
        srcRect = re.search(r'<a:srcRect[^>]*/>', blk)
        # 显示比（=嵌回后渲染框比）
        if spec['mode'] == 'replace':
            paint_ratio = int(ext[0]) / int(ext[1])
            paint_note = 'extent'
        elif spec['mode'] == 'rename_derotate':
            paint_ratio = int(ext[0]) / int(ext[1])
            paint_note = 'extent(去rot后)'
        elif spec['mode'] == 'rename_shrink_aext':
            paint_ratio = SHRINK_AEXT[0] / SHRINK_AEXT[1]
            paint_note = f'新a:ext={SHRINK_AEXT}'
        # 新图与加画布
        img_bytes = open(os.path.join(NEWIMG, spec['new']), 'rb').read()
        delivered_md5 = md5(img_bytes)
        im = Image.open(io.BytesIO(img_bytes))
        dpi = im.info.get('dpi')
        cw, ch = im.size
        img_ratio = cw / ch
        dev = abs(img_ratio - paint_ratio) / paint_ratio
        padded = False
        if dev > PAD_T:
            if img_ratio > paint_ratio:   # 新图偏宽 → 加高
                nh = round(cw / paint_ratio); ncw, nch = cw, nh
            else:                          # 新图偏窄/偏高 → 加宽
                nw = round(ch * paint_ratio); ncw, nch = nw, ch
            canvas = Image.new(im.mode, (ncw, nch), (255, 255, 255) if im.mode != 'L' else 255)
            canvas.paste(im, ((ncw - cw) // 2, (nch - ch) // 2))
            canvas.save(voice := io.BytesIO(), format='PNG', dpi=dpi)
            img_bytes = voice.getvalue()
            padded = True
            im2 = Image.open(io.BytesIO(img_bytes))
            assert im2.size == (ncw, nch)
        imf = Image.open(io.BytesIO(img_bytes))
        ok_gray, gray_note = grayscale_ok(imf)
        dpi2 = imf.info.get('dpi')
        ratio2 = imf.size[0] / imf.size[1]
        # XML 手术
        if spec['mode'] == 'replace':
            assert srcRect is None, f'{base} 意外含 srcRect'
        elif spec['mode'] == 'rename_derotate':
            assert srcRect, f'{base} 预期含 srcRect'
            sr = srcRect.group(0)
            assert new_doc_xml.count(sr) == 1
            new_doc_xml = new_doc_xml.replace(sr, '')
            xf = re.search(r'<a:xfrm rot="5400000" flipH="1" flipV="1">', blk)
            assert xf, f'{base} 预期 rot/flip'
            blk_new = blk.replace(xf.group(0), '<a:xfrm>').replace(sr, '')
            assert 'rot=' not in blk_new and 'flip' not in blk_new
            s2, e2, _ = drawing_block(new_doc_xml, rid)  # srcRect 移除后位置已变，重找
            new_doc_xml = new_doc_xml[:s2] + blk_new + new_doc_xml[e2:]
            new_doc_xml = new_doc_xml.replace('<a:xfrm></a:xfrm>', '<a:xfrm/>')
        elif spec['mode'] == 'rename_shrink_aext':
            assert srcRect, f'{base} 预期含 srcRect'
            sr = srcRect.group(0)
            assert new_doc_xml.count(sr) == 1
            new_doc_xml = new_doc_xml.replace(sr, '')
            old_aext = f'<a:ext cx="{aext.group(1)}" cy="{aext.group(2)}"/>'
            new_aext = f'<a:ext cx="{SHRINK_AEXT[0]}" cy="{SHRINK_AEXT[1]}"/>'
            # 块内唯一（a14 extLst 的 cx/cy 不带此形）
            s2, e2, blk2 = drawing_block(new_doc_xml, rid)
            assert blk2.count(old_aext) == 1, f'{base} a:ext 定位异常'
            blk2 = blk2.replace(old_aext, new_aext)
            new_doc_xml = new_doc_xml[:s2] + blk2 + new_doc_xml[e2:]
        expected_xml_changed.add('word/document.xml') if spec['mode'] != 'replace' else None
        # 媒体成员
        if spec['mode'] == 'replace':
            data[f'word/media/{base}'] = img_bytes
        else:
            newname = base.rsplit('.', 1)[0] + '.png'
            assert f'word/media/{newname}' not in data, f'{newname} 命名冲突'
            del data[f'word/media/{base}']
            data[f'word/media/{newname}'] = img_bytes
            old_t = f'Target="media/{base}"'
            new_t = f'Target="media/{newname}"'
            assert new_rels.count(old_t) == 1
            new_rels = new_rels.replace(old_t, new_t)
            expected_media_changed.add(f'word/media/{base}')
            expected_media_changed.add(f'word/media/{newname}')
            final_name = newname
        if spec['mode'] == 'replace':
            expected_media_changed.add(f'word/media/{base}')
            final_name = base
        r['targets'][base] = dict(rid=rid, wp_extent=f'{ext[0]}x{ext[1]}', old_aext=(aext.groups() if aext else None),
                                  srcRect=(srcRect.group(0) if srcRect else None), mode=spec['mode'],
                                  new_file=spec['new'], delivered_md5=delivered_md5, embedded_md5=md5(img_bytes),
                                  delivered_px=f'{cw}x{ch}', embedded_px=f'{imf.size[0]}x{imf.size[1]}',
                                  paint_ratio=round(paint_ratio, 5), img_ratio=round(img_ratio, 5),
                                  dev_pct=round(dev * 100, 2), padded=padded, paint_basis=paint_note,
                                  gray=gray_note, dpi=f'{dpi2[0]:.1f}' if dpi2 else None,
                                  embedded_name=final_name, embedded_media_md5=md5(img_bytes))
        log(f"  {base}: {spec['mode']} dev={dev*100:.2f}% padded={padded} px={cw}x{ch}->{imf.size[0]}x{imf.size[1]} gray={gray_note} dpi={dpi2}")

    # 3. 重组 zip（保持成员序、原时间戳与压缩方式；被删成员移除、新成员尾部插入）
    dt = {i.filename: i.date_time for i in zin.infolist()}
    out_buf = io.BytesIO()
    zout = zipfile.ZipFile(out_buf, 'w', zipfile.ZIP_DEFLATED)
    written = set()
    for n in names:
        if n in expected_media_changed and n not in data:
            continue  # 被改名删除的旧媒体
        zb = new_doc_xml.encode('utf-8') if n == 'word/document.xml' else (
             new_rels.encode('utf-8') if n == 'word/_rels/document.xml.rels' else data[n])
        zi = zipfile.ZipInfo(n, date_time=dt.get(n, (1980, 1, 1, 0, 0, 0)))
        zi.compress_type = compress.get(n, zipfile.ZIP_DEFLATED)
        zout.writestr(zi, zb)
        written.add(n)
    for n in data:
        if n not in written and n in expected_media_changed:
            zi = zipfile.ZipInfo(n); zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, data[n])
    # document.xml / rels 已按上方写入；但压缩方式对 XML 用 DEFLATED
    zout.close()
    open(out_path, 'wb').write(out_buf.getvalue())

    # 4. 断言（重开输出文件独立验证）
    zchk = zipfile.ZipFile(out_path)
    chk = {n: zchk.read(n) for n in zchk.namelist()}
    # a) oMath 对锚
    om = len(re.findall(r'<m:oMath[ >]', chk['word/document.xml'].decode('utf-8')))
    om_pre = len(re.findall(r'<m:oMath[ >]', doc_xml))
    assert om == OMATH_ANCHOR[code] == om_pre, f'{code} oMath {om} != 锚{OMATH_ANCHOR[code]}/前{om_pre}'
    # b) w:t 零差
    wt_pre = re.findall(r'<w:t[^>]*>(.*?)</w:t>', doc_xml, re.S)
    wt_post = re.findall(r'<w:t[^>]*>(.*?)</w:t>', chk['word/document.xml'].decode('utf-8'), re.S)
    assert wt_pre == wt_post and len(wt_post) > 0, f'{code} w:t 差异!'
    # c) 白名单外零 diff
    pre_all = {n: md5(zin.read(n)) for n in names}
    post_all = {n: md5(b) for n, b in chk.items()}
    added = set(post_all) - set(pre_all)
    removed = set(pre_all) - set(post_all)
    changed = {n for n in set(pre_all) & set(post_all) if pre_all[n] != post_all[n]}
    assert added <= expected_media_changed and removed <= expected_media_changed, f'{code} 成员增删越界 {added}/{removed}'
    assert changed <= expected_media_changed | expected_xml_changed, f'{code} 变更越界 {changed}'
    assert expected_xml_changed <= changed | set(), f'{code} 预期 XML 变更未发生 {expected_xml_changed - changed}'
    # rels 差异仅限 Target
    if 'word/_rels/document.xml.rels' in changed:
        pre_r = rels_map(zin.read('word/_rels/document.xml.rels'))
        post_r = rels_map(chk['word/_rels/document.xml.rels'])
        assert set(pre_r) == set(post_r)
        diffs = [(k, pre_r[k][0], post_r[k][0]) for k in pre_r if pre_r[k][0] != post_r[k][0]]
        assert all(pre_r[k][1:] == post_r[k][1:] for k in pre_r)
        for k, o, nn in diffs:
            assert o.endswith('.jpg') and nn.endswith('.png'), f'rels 非预期改 {o}->{nn}'
        r['rels_diffs'] = diffs
        log(f'  rels Target 改动 {len(diffs)} 处: {diffs}')
    # d) 引用无悬空无孤儿
    all_parts_xml = [chk[n].decode('utf-8', 'ignore') for n in chk if n.endswith('.xml')]
    used_rids = set()
    for t in all_parts_xml:
        used_rids |= set(re.findall(r'r:(?:embed|id|link)="(rId[^"]+)"', t))
    post_rmap = rels_map(chk['word/_rels/document.xml.rels'])
    doc_rids = set(post_rmap)
    dangling = used_rids - doc_rids
    assert not dangling, f'{code} 悬空 rId {list(dangling)[:5]}'
    media_members = {n.split('/')[-1] for n in chk if n.startswith('word/media/')}
    rels_targets = {v[0].split('/')[-1] for v in post_rmap.values() if 'media/' in v[0]}
    orphans = media_members - rels_targets
    assert not orphans, f'{code} 孤儿媒体 {sorted(orphans)[:5]}'
    missing = rels_targets - media_members
    assert not missing, f'{code} 缺媒体 {sorted(missing)[:5]}'
    # e) 嵌入媒体灰阶/300dpi/等比 复核
    for base, tr in r['targets'].items():
        zb = chk[f'word/media/{tr["embedded_name"]}']
        imx = Image.open(io.BytesIO(zb))
        ok, note = grayscale_ok(imx)
        assert ok, f'{base} 非灰阶: {note}'
        assert imx.info.get('dpi') and abs(imx.info['dpi'][0] - 300) < 1.5, f'{base} dpi 异常'
    # f) wp:extent/rId 原值
    for base, tr in r['targets'].items():
        s3, e3, blk3 = drawing_block(chk['word/document.xml'].decode('utf-8'), tr['rid'])
        ext3 = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', blk3).groups()
        assert f'{ext3[0]}x{ext3[1]}' == tr['wp_extent'], f'{base} wp:extent 变动!'
        assert f'r:embed="{tr["rid"]}"' in blk3
    # XML 良构
    ET.fromstring(chk['word/document.xml'])
    ET.fromstring(chk['word/_rels/document.xml.rels'])
    zchk.close()
    r.update(omath=om, wt_count=len(wt_post), added=sorted(added), removed=sorted(removed), changed=sorted(changed),
             out_md5=md5(open(out_path, 'rb').read()), out_size=os.path.getsize(out_path))
    results[code] = r
    log(f"  断言全过: oMath={om} w:t={len(wt_post)} added={len(added)} removed={len(removed)} changed={len(changed)}")

json.dump(results, open(os.path.join(WS, '嵌回结果.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
log('SUMMARY_EMBED OK 20目标=' + str(sum(len(v['targets']) for v in results.values())))
