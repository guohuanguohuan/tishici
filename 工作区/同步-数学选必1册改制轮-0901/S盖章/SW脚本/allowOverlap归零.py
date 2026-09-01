# -*- coding: utf-8 -*-
"""
SW任务1：allowOverlap全件0化（一次性脚本）
动作：扫描指定docx全部XML部件的wp:anchor，allowOverlap="1"（或缺省等同1）→"0"，逐件计数。
依据：公共规则§5锚定形态条款「wrapSquare结构上不可能压字」——allowOverlap=0为OOXML标准实现
（E1返工§6.2定案：跨段锚定浮动图同侧posOffset叠放，同段护栏防不住）。
零副作用断言（逐件）：
  B1 anchor计数前=后；
  B2 改后全部anchor allowOverlap="0"（含缺省补挂）；
  B3 除被改部件外全部zip成员逐字节不变；被改部件「归一化(1→0)后」与原文逐字节相等
     ——证明改动面仅allowOverlap属性值。
用法: python allowOverlap归零.py [--check-only]
"""
import io
import os
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from lxml import etree

WPNS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
ANCHOR = '{%s}anchor' % WPNS

WORK = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW工作'
FILES = [
    'I1=人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'B=人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C=人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'I2=人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'E=人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F=人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G=人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H=人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
]


def surgery(path, check_only):
    """返回 (部件级计数dict, fails)。check_only=True只统计不改写。"""
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        members = [(i.filename, z.read(i.filename)) for i in infos]
    per_part = {}
    fails = []
    new_members = []
    for name, data in members:
        if not name.endswith('.xml') or (b'wp:anchor' not in data and b'allowOverlap' not in data):
            new_members.append((name, data))
            continue
        try:
            root = etree.fromstring(data)
        except etree.XMLSyntaxError:
            new_members.append((name, data))
            continue
        anchors = [a for a in root.iter(ANCHOR)]
        if not anchors:
            new_members.append((name, data))
            continue
        n1 = sum(1 for a in anchors if a.get('allowOverlap') == '1')
        nmiss = sum(1 for a in anchors if a.get('allowOverlap') is None)
        n0 = sum(1 for a in anchors if a.get('allowOverlap') == '0')
        nother = len(anchors) - n1 - nmiss - n0
        if check_only:
            per_part[name] = (len(anchors), n0, n1, nmiss, nother)
            new_members.append((name, data))
            continue
        # 手术：全部置"0"
        for a in anchors:
            a.set('allowOverlap', '0')
        out = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        # B3自证：原文将 allowOverlap="1" 全部替换为 "0" 后须与输出逐字节相等
        normalized = data.replace(b'allowOverlap="1"', b'allowOverlap="0"')
        if normalized != out:
            fails.append('B3失败：%s 归一化后与输出不等（改动面越界）' % name)
        new_members.append((name, out))
        per_part[name] = (len(anchors), n1 + nmiss, n1, nmiss, nother)
    if not check_only:
        tmp = path + '.tmp'
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
            for name, data in new_members:
                zo.writestr(name, data)
        os.replace(tmp, path)
    # B1/B2 复验（重开落盘件；check-only不改写、只复计anchor数=勘察基线）
    with zipfile.ZipFile(path) as z:
        for name, _ in new_members:
            if not name.endswith('.xml'):
                continue
            data2 = z.read(name)
            if b'wp:anchor' not in data2 and b'allowOverlap' not in data2:
                continue
            root2 = etree.fromstring(data2)
            anchors2 = [a for a in root2.iter(ANCHOR)]
            if not anchors2:
                continue
            n0 = sum(1 for a in anchors2 if a.get('allowOverlap') == '0')
            if not check_only and n0 != len(anchors2):
                fails.append('B2失败：%s 改后仍有非0值（%d/%d）' % (name, len(anchors2) - n0, len(anchors2)))
            pre = per_part[name][0] if name in per_part else None
            if pre is not None and pre != len(anchors2):
                fails.append('B1失败：%s anchor计数前%d≠后%d' % (name, pre, len(anchors2)))
    return per_part, fails


def main():
    check_only = '--check-only' in sys.argv
    grand = [0, 0, 0, 0]  # total, changed, already0, miss
    all_fails = []
    for spec in FILES:
        code, fname = spec.split('=', 1)
        path = os.path.join(WORK, fname)
        per_part, fails = surgery(path, check_only)
        all_fails.extend('%s:%s' % (code, f) for f in fails)
        tot = sum(v[0] for v in per_part.values())
        n0 = sum(v[1] for v in per_part.values())
        n1 = sum(v[2] for v in per_part.values())
        nmiss = sum(v[3] for v in per_part.values())
        nother = sum(v[4] for v in per_part.values())
        grand[0] += tot
        grand[1] += n1 + nmiss
        grand[2] += n0
        grand[3] += nmiss
        mode = '检查' if check_only else '改写'
        # 检查态：v=(n,已0,=1,缺省,他值)；改写态：v=(n,改写数,=1,缺省,他值)——改写后已0=n由B2断言背书
        lab0 = '已0' if check_only else '改写后已0(B2)'
        print('[%s] anchor=%d %s1→0=%d 缺省补挂=%d 他值=%d %s=%d | %s | 断言%s'
              % (code, tot, mode, n1, nmiss, nother, lab0, n0,
                 '; '.join('%s:n=%d' % (k, v[0]) for k, v in per_part.items()) or '（无anchor部件）',
                 '全过' if not fails else '失败:' + ';'.join(fails)))
    print('8件合计 anchor=%d 改写=%d（其中缺省补挂%d）' % (grand[0], grand[1], grand[3]))
    if all_fails:
        for f in all_fails:
            print('!! ' + f)
        sys.exit(2)


if __name__ == '__main__':
    main()
