# -*- coding: utf-8 -*-
"""灰底改色.py — 必背标记灰底批量改色（2026-08-26 用户拍板：D9D9D9 15%灰一眼难辨，加深为 A6A6A6＝35%灰）
用法: python 灰底改色.py <旧fill> <新fill> <docx...>   就地改色（原文件不动时先复制）
说明: 扫描包内全部 xml 部件（document/headers/footers/styles 等）中 w:shd 的 w:fill＝旧值，
      原位改为新值，其余属性与元素不动；不做任何增删，页数与排版不受影响（fill 不参与度量）。
      运行级与 ctrlPr 级（OMML）共用 w:rPr，同样生效。输出每件改色计数。"""
import sys, io, zipfile, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def recolor(path, old, new):
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    pat = re.compile(('w:fill="%s"' % old).encode())
    n = 0
    for name, b in parts.items():
        if not name.endswith('.xml'):
            continue
        cnt = len(pat.findall(b))
        if cnt:
            parts[name] = pat.sub(('w:fill="%s"' % new).encode(), b)
            n += cnt
    tmp = path + '.recolor'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name, b in parts.items():
        zo.writestr(name, b)
    zo.close()
    # 重试替换（防同步盘/杀软瞬时锁）
    import time
    for i in range(12):
        try:
            os.replace(tmp, path)
            return n
        except PermissionError:
            time.sleep(6)
    raise RuntimeError('locked: ' + path)

if __name__ == '__main__':
    old, new, total = sys.argv[1], sys.argv[2], 0
    for p in sys.argv[3:]:
        n = recolor(p, old, new)
        total += n
        print('%-46s 改色 %d 处' % (os.path.basename(p)[:46], n))
    print('合计', total)
