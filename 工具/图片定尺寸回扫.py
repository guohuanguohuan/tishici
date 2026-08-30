# -*- coding: utf-8 -*-
"""图片定尺寸回扫（公共规则§7图片内容感知定尺寸条款的对应工具，工具债看板①，2026-08-30建）
定位：只扫描登记、不修改任何文件——尺寸判定仍由人工按§7判据逐张亲做，本工具仅产出客观数据。
口径（§7现行文本，2026-08-30拍板改版）：
  上限＝版心宽（约18cm；两图并排时单图≤8.5cm）；禁止放大超过150dpi印刷自然尺寸
  （显示宽cm≤像素宽÷59.06——防糊硬底线；像素＜200×200的图标类小图不放大不缩放）。
扫描范围：正文 body 全部 w:drawing（wp:inline 为常态；wp:anchor 出现即单独红旗列——
  §7排版自检「锚定形态全 inline（正文无 wp:anchor）」现行禁令）。页眉页脚件不在扫描范围，
  但在三查中对账归属（media 可能被页眉页脚合法引用）。
每图登记：序号／所在段序号／段内文本前20字（归属线索）／同段图数（两图并排检测）／
  显示宽×高（wp:extent，EMU→cm＝EMU÷360000）／媒体像素宽×高（zip media part，PIL 优先、
  PNG/JPEG 头解析兜底）／150dpi自然宽cm＝像素宽÷59.06。
标记列（自动预筛，供人工过目，不替代亲判）：
  ①显示宽＞18cm（版心超限）
  ②同段多图且单图显示宽＞8.5cm（并排超限）
  ③显示宽＞自然宽×1.00（放大超限防糊；像素未知时记「未知」）
  ④显示宽＜5cm（疑似过小，人工过目列——含§7「像素＜200×200图标类不放大不缩放」的小图线索）
一致性三查（对账口径：图片守恒）：media 文件数＝rels 引用数＝正文 drawing 数，差异行单列。
用法：python 图片定尺寸回扫.py 输入.docx [--out 输出前缀]
  输出：前缀.tsv＋前缀.md 双格式；无 --out 时默认与输入同目录、前缀＝输入名＋「.图片定尺寸回扫」。
  无图件输出空表＋退出码0。
安全：全程只读（zip 以 'r' 打开、不落任何临时内容到输入路径），任何情况下不写输入文件。
"""
import argparse
import io
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

EMU_PER_CM = 360000.0
PX_PER_CM_150DPI = 59.06  # 150dpi → 150/2.54≈59.06像素/cm；自然宽cm＝像素宽÷59.06（§7口径）

NS = {
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wp':  'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}
def qn(tag):
    p, t = tag.split(':')
    return '{%s}%s' % (NS[p], t)

# mc:Fallback 内为 VML 兜底（w:pict）或重复内容，剔除防重复计数
RE_FALLBACK = re.compile(r'<mc:Fallback>.*?</mc:Fallback>', re.S)
RE_WS = re.compile(r'[\t\r\n]+')

HEADERS = ['序号', '段序号', '段文本前20字', '段内图数', '锚形态',
           '显示宽cm', '显示高cm', '像素宽', '像素高', '150dpi自然宽cm', '媒体文件',
           '①版心超限', '②并排超限', '③放大超限', '④过小过目']


def pixel_size(data):
    """媒体像素尺寸：PIL 优先，PNG/JPEG 头解析兜底。返回((w,h),来源)或(None,原因)。"""
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as im:
            return im.size, 'PIL'
    except Exception:
        pass
    if data[:8] == b'\x89PNG\r\n\x1a\n' and len(data) >= 24:
        return (int.from_bytes(data[16:20], 'big'),
                int.from_bytes(data[20:24], 'big')), 'PNG头'
    if data[:2] == b'\xff\xd8':
        i, n = 2, len(data)
        while i + 9 < n:
            if data[i] != 0xFF:
                i += 1
                continue
            m = data[i + 1]
            if m == 0xD8 or m == 0x01 or 0xD0 <= m <= 0xD7:
                i += 2
                continue
            if m == 0xD9:
                break
            seglen = int.from_bytes(data[i + 2:i + 4], 'big')
            if seglen < 2:
                break
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                h = int.from_bytes(data[i + 5:i + 7], 'big')
                w = int.from_bytes(data[i + 7:i + 9], 'big')
                return (w, h), 'JPEG头'
            i += 2 + seglen
    return None, '头解析失败'


def parse_rels(z, part='word/_rels/document.xml.rels'):
    """返回(rid→target字典, image关系列表[(rid,target)])。"""
    try:
        raw = z.read(part)
    except KeyError:
        return {}, []
    root = ET.fromstring(raw)
    rid2t, imgs = {}, []
    for rel in root.iter(qn('rel:Relationship')):
        rid = rel.get('Id')
        target = rel.get('Target') or ''
        rid2t[rid] = target
        if (rel.get('Type') or '').endswith('/image'):
            imgs.append((rid, target))
    return rid2t, imgs


def para_text(p):
    return RE_WS.sub('', ''.join(t.text or '' for t in p.iter(qn('w:t'))))


def fmt(x, nd=2):
    return ('%.' + str(nd) + 'f') % x if x is not None else '未知'


def scan(docx_path):
    """只读扫描。返回(dict汇总, [行], [三查差异行])。"""
    z = zipfile.ZipFile(docx_path, 'r')  # 只读打开
    try:
        xml_text = z.read('word/document.xml').decode('utf-8')
        root = ET.fromstring(RE_FALLBACK.sub('', xml_text))
        body = root.find(qn('w:body'))
        if body is None:
            raise ValueError('document.xml 无 w:body')
        rid2t, rels_imgs = parse_rels(z)
        # 全包 rels 对账归属（页眉页脚等其他件的 image 引用，不计入正文口径）
        other_parts = {}
        for name in z.namelist():
            if name.endswith('.rels') and name != 'word/_rels/document.xml.rels':
                _, pimgs = parse_rels(z, name)
                for rid, tgt in pimgs:
                    other_parts.setdefault(os.path.basename(tgt), []).append(name)

        rows, drawings_total, anchor_rows, used_rids = [], 0, 0, []
        para_idx = 0
        for p in body.iter(qn('w:p')):
            para_idx += 1
            draws = list(p.iter(qn('w:drawing')))
            if not draws:
                continue
            text20 = para_text(p).strip()[:20] or '(空段)'
            n_in_para = len(draws)
            for d in draws:
                drawings_total += 1
                is_anchor = d.find(qn('wp:anchor')) is not None
                if is_anchor:
                    anchor_rows += 1
                ext = next(d.iter(qn('wp:extent')), None)
                dw = (int(ext.get('cx')) / EMU_PER_CM) if ext is not None and ext.get('cx') else None
                dh = (int(ext.get('cy')) / EMU_PER_CM) if ext is not None and ext.get('cy') else None
                blip = next(d.iter(qn('a:blip')), None)
                rid = blip.get(qn('r:embed')) if blip is not None else None
                if rid:
                    used_rids.append(rid)
                tgt = rid2t.get(rid) if rid else None
                media = os.path.basename(tgt) if tgt else '(无blip引用)' if not rid else '(rels缺%s)' % rid
                pw = ph = None
                if tgt:
                    zpath = 'word/' + tgt if not tgt.startswith('/') else tgt[1:]
                    try:
                        (pw, ph), psrc = pixel_size(z.read(zpath))
                    except KeyError:
                        psrc = 'zip缺' + tgt
                else:
                    psrc = '无媒体'
                nat = (pw / PX_PER_CM_150DPI) if pw else None
                f1 = (dw is not None and dw > 18.0)
                f2 = (dw is not None and n_in_para > 1 and dw > 8.5)
                f3 = '未知' if (dw is None or nat is None) else (1 if dw > nat * 1.00 + 1e-9 else 0)
                f4 = (dw is not None and dw < 5.0)
                rows.append([drawings_total, para_idx, text20, n_in_para,
                             'anchor' if is_anchor else 'inline',
                             fmt(dw), fmt(dh), pw if pw else '未知', ph if ph else '未知',
                             fmt(nat), media,
                             1 if f1 else 0, 1 if f2 else 0, f3, 1 if f4 else 0])

        media_files = [n for n in z.namelist()
                       if n.startswith('word/media/') and not n.endswith('/')]
    finally:
        z.close()

    # —— 一致性三查（图片守恒）：A=media文件数 B=document.xml.rels image关系数 C=正文drawing数
    A, B, C = len(media_files), len(rels_imgs), drawings_total
    rels_targets = [os.path.basename(t) for _, t in rels_imgs]
    used_set = set(used_rids)
    used_targets_seq = [os.path.basename(rid2t[r]) for r in used_rids if r in rid2t]
    used_targets = set(used_targets_seq)
    diffs = []
    for m in sorted(set(os.path.basename(x) for x in media_files)):
        if m not in rels_targets:
            who = other_parts.get(m)
            diffs.append('差异：media文件 %s 未被 document.xml.rels 引用%s'
                         % (m, ('（被' + '、'.join(who) + '引用→归属页眉页脚等，不计违规）') if who else '（全包无引用→真孤儿）'))
    for rid, tgt in rels_imgs:
        if rid not in used_set:
            who = other_parts.get(os.path.basename(tgt))
            diffs.append('差异：rels image关系 %s→%s 未被正文 drawing 引用%s'
                         % (rid, tgt, ('（被' + '、'.join(who) + '引用→归属页眉页脚等）') if who else ''))
    for rid in sorted(used_set):
        if rid not in rid2t:
            diffs.append('差异：正文 drawing 引用 %s 在 document.xml.rels 无对应关系（孤儿图引）' % rid)
        # rid→target 缺文件的检查已在行内「媒体文件」列标注，不在此重复
    from collections import Counter
    for m, cnt in Counter(used_targets_seq).items():
        if cnt > 1:
            diffs.append('提示：media文件 %s 被正文 %d 个 drawing 复用（计数口径：drawing数＞media数属此因）' % (m, cnt))
    ident = (A == B == C) and not [d for d in diffs if d.startswith('差异')]
    summary = {
        'media_files': A, 'rels_imgs': B, 'drawings': C,
        'anchor_rows': anchor_rows, 'identity': ident, 'diffs': diffs,
        'f1': sum(1 for r in rows if r[11] == 1), 'f2': sum(1 for r in rows if r[12] == 1),
        'f3': sum(1 for r in rows if r[13] == 1),
        'f3_unk': sum(1 for r in rows if r[13] == '未知'),
        'f4': sum(1 for r in rows if r[14] == 1),
        'multi_para': sum(1 for r in rows if r[3] > 1),
    }
    return summary, rows, diffs


def write_out(summary, rows, diffs, out_prefix, docx_path):
    tsvp, mdp = out_prefix + '.tsv', out_prefix + '.md'
    with open(tsvp, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('\t'.join(HEADERS) + '\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    ident = summary['identity']
    with open(mdp, 'w', encoding='utf-8') as f:
        f.write('# 图片定尺寸回扫登记表\n\n')
        f.write('- 输入件：`%s`（只读扫描，未做任何修改）\n' % docx_path)
        f.write('- 一致性三查（图片守恒）：media 文件数＝%d；rels 引用数＝%d；正文 drawing 数＝%d；'
                '恒等判定＝%s\n' % (summary['media_files'], summary['rels_imgs'],
                                     summary['drawings'], '恒等✓' if ident else '不等✗（见差异）'))
        f.write('- wp:anchor 计数＝%d（现行禁令：正文无 wp:anchor，非0即红旗）\n' % summary['anchor_rows'])
        f.write('- 标记命中：①版心超限 %d；②并排超限 %d；③放大超限 %d（另未知 %d）；④过小过目 %d；'
                '同段多图段 %d 处\n' % (summary['f1'], summary['f2'], summary['f3'],
                                         summary['f3_unk'], summary['f4'], summary['multi_para']))
        if diffs:
            f.write('- 三查差异/提示（%d 行）：\n' % len(diffs))
            for d in diffs:
                f.write('  - %s\n' % d)
        else:
            f.write('- 三查差异：无\n')
        f.write('\n标记列仅为自动预筛，尺寸判定按公共规则§7图片内容感知定尺寸条款逐张亲做。\n\n')
        f.write('| ' + ' | '.join(HEADERS) + ' |\n')
        f.write('|' + '|'.join(['---'] * len(HEADERS)) + '|\n')
        for r in rows:
            f.write('| ' + ' | '.join(str(x) for x in r) + ' |\n')
        if not rows:
            f.write('\n（本件无正文图片——空表，退出码0）\n')
    return tsvp, mdp


def main():
    ap = argparse.ArgumentParser(description='docx 正文图片定尺寸回扫（只读登记）')
    ap.add_argument('input', help='输入 docx（只读，绝不写入）')
    ap.add_argument('--out', help='输出前缀（生成 前缀.tsv 与 前缀.md）')
    a = ap.parse_args()
    if not os.path.isfile(a.input) or not a.input.lower().endswith('.docx'):
        print('输入不存在或非 docx：%s' % a.input)
        return 1
    prefix = a.out or (os.path.splitext(a.input)[0] + '.图片定尺寸回扫')
    try:
        summary, rows, diffs = scan(a.input)
    except Exception as e:
        print('扫描失败：%r' % e)
        return 1
    odir = os.path.dirname(os.path.abspath(prefix))
    if odir:
        os.makedirs(odir, exist_ok=True)
    tsvp, mdp = write_out(summary, rows, diffs, prefix, os.path.basename(a.input))
    s = summary
    print('输入：%s' % a.input)
    print('三查：media=%d rels=%d drawing=%d 恒等=%s' % (s['media_files'], s['rels_imgs'], s['drawings'], s['identity']))
    print('wp:anchor=%d | 登记行=%d' % (s['anchor_rows'], len(rows)))
    print('标记：①%d ②%d ③%d(未知%d) ④%d | 同段多图段=%d' % (s['f1'], s['f2'], s['f3'], s['f3_unk'], s['f4'], s['multi_para']))
    for d in diffs:
        print(d)
    print('输出：%s | %s' % (tsvp, mdp))
    return 0  # 无图件同样 0（空表）


if __name__ == '__main__':
    sys.exit(main())
