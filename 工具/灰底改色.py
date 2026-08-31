# -*- coding: utf-8 -*-
"""灰底改色.py — 通用 w:shd/w:fill 批量映射改色（幂等；任意旧fill→新fill，就地改色）
沿革：2026-08-26 建版（D9D9D9→A6A6A6 加深轮）；2026-08-28 A6A6A6→C9C9C9 回调轮；
      2026-08-31 欠账A版式改版回扫轮（T2，工具债⑥）扩为通用映射工具＋预置色板入口。
预置映射（--preset，可叠加多组一次改完）：
  0831迁移 : A6A6A6→C9C9C9 ＋ D9D9D9→C9C9C9（本轮旧灰清债迁移——内容标记/题号块/
             块标签/条目号/第一子层/导航表头同法一次改；fill 改动不影响页数、免重盖页码
             ——2026-08-26/08-28 两轮改色实证）
用法:
  python 灰底改色.py <旧fill> <新fill> <docx...>            # 历史兼容入口（单映射）
  python 灰底改色.py --preset 0831迁移 <docx...>             # 预置映射（A6A6A6/D9D9D9→C9C9C9）
  python 灰底改色.py --map A6A6A6=C9C9C9 [--map ...] <docx...>  # 自定义多映射
  可选 --dry-run：只计数不改写。
说明: 扫描包内全部 xml 部件（document/headers/footers/styles 等）中 w:shd 的 w:fill＝旧值，
      原位改为新值，其余属性与元素不动；不做任何增删，页数与排版不受影响（fill 不参与度量）。
      运行级与 ctrlPr 级（OMML）共用 w:rPr，同样生效。幂等：二跑旧值已清零计数＝0。
      每件输出逐旧值改色计数；旧值＝新值或非法十六进制拒绝执行。"""
import sys, io, zipfile, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PRESETS = {
    '0831迁移': [('A6A6A6', 'C9C9C9'), ('D9D9D9', 'C9C9C9')],
}
HEX_RE = re.compile(r'^[0-9A-Fa-f]{6}$')

def recolor(path, mapping, dry=False):
    """mapping: [(old,new), ...]；返回 {old: count}。就地改写（dry 时不写回）。"""
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    hits = {old: 0 for old, _ in mapping}
    changed = False
    for name, b in parts.items():
        if not name.endswith('.xml'):
            continue
        nb = b
        for old, new in mapping:
            pat = re.compile(('w:fill="%s"' % old).encode())
            cnt = len(pat.findall(nb))
            if cnt:
                hits[old] += cnt
                nb = pat.sub(('w:fill="%s"' % new).encode(), nb)
                changed = True
        if changed and nb is not b:
            parts[name] = nb
    if dry or not changed:
        return hits
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
            return hits
        except PermissionError:
            time.sleep(6)
    raise RuntimeError('locked: ' + path)

def main():
    argv = [a for a in sys.argv[1:] if a != '--dry-run']
    dry = '--dry-run' in sys.argv[1:]
    mapping = []
    files = []
    if len(argv) >= 3 and HEX_RE.match(argv[0]) and HEX_RE.match(argv[1]):
        # 历史兼容入口：python 灰底改色.py <旧fill> <新fill> <docx...>
        mapping = [(argv[0].upper(), argv[1].upper())]
        files = argv[2:]
    else:
        i = 0
        while i < len(argv):
            a = argv[i]
            if a == '--preset':
                i += 1
                if i >= len(argv) or argv[i] not in PRESETS:
                    print('未知预置：%s（可用：%s）' % (argv[i] if i < len(argv) else '?', '/'.join(PRESETS)))
                    sys.exit(2)
                mapping += PRESETS[argv[i]]
            elif a == '--map':
                i += 1
                if i >= len(argv) or '=' not in argv[i]:
                    print('--map 需 OLD=NEW（6位十六进制）'); sys.exit(2)
                old, new = argv[i].split('=', 1)
                mapping.append((old.upper(), new.upper()))
            elif a.lower().endswith(('.docx', '.docm')):
                files.append(a)
            else:
                print('无法识别参数：%s' % a); sys.exit(2)
            i += 1
    if not mapping or not files:
        print(__doc__)
        sys.exit(2)
    for old, new in mapping:
        if old == new or not HEX_RE.match(old) or not HEX_RE.match(new):
            print('拒绝：映射 %s=%s（旧新相同或非6位十六进制）' % (old, new))
            sys.exit(2)
    grand = {old: 0 for old, _ in mapping}
    for p in files:
        if not os.path.exists(p):
            print('%-46s 不存在，跳过' % os.path.basename(p)[:46])
            continue
        hits = recolor(p, mapping, dry)
        for k, v in hits.items():
            grand[k] += v
        detail = '；'.join('%s→%s %d 处' % (o, dict(mapping)[o], hits[o]) for o, _ in mapping)
        print('%-46s %s%s' % (os.path.basename(p)[:46], detail, '（dry-run 未写回）' if dry else ''))
    print('合计 ' + '；'.join('%s→%s %d 处' % (o, dict(mapping)[o], grand[o]) for o, _ in mapping)
          + ('（dry-run）' if dry else ''))

if __name__ == '__main__':
    main()
