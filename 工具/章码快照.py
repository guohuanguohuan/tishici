# -*- coding: utf-8 -*-
"""章码快照.py——docx 章码件 XML 签名快照与比对（§13 复审计/P3④「盖章晚于内容改动」哈希判据配套）。

用法：
  python 章码快照.py snap <docx目录> <快照输出目录> <文件清单.txt>
  python 章码快照.py diff <docx目录> <快照输出目录> <文件清单.txt>
文件清单.txt：每行一个 docx 文件名（相对 docx目录）。
签名口径：zip 内 word/document.xml、word/settings.xml、word/header\\d+.xml、word/footer\\d+.xml
逐 member 取 sha1 十六进制前 12 位；快照存 <快照输出目录>/_快照.json。
snap 同时把整件 docx 拷入快照输出目录（整件备份）；diff 只读比对、逐件印变动键。
由来：2026-09-05 选必1⓪轮修订3回环——盖章回拷重打包 docx 致 mtime 失真，
「盖章晚于内容改动」改以本工具快照哈希断言（经验件 2026-09-05④）。
"""
import os, re, json, shutil, zipfile, hashlib, sys

def sig(path):
    h = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n == 'word/document.xml' or re.fullmatch(r'word/(header|footer)\d+\.xml', n) or n == 'word/settings.xml':
                h[n] = hashlib.sha1(z.read(n)).hexdigest()[:12]
    return h

def main(argv):
    if len(argv) != 5 or argv[1] not in ('snap', 'diff'):
        print(__doc__)
        return 2
    mode, SRC, DST, listfile = argv[1], argv[2], argv[3], argv[4]
    FILES = [ln.strip() for ln in open(listfile, encoding='utf-8') if ln.strip()]
    os.makedirs(DST, exist_ok=True)
    snap_path = os.path.join(DST, '_快照.json')
    if mode == 'snap':
        snap = {}
        for f in FILES:
            p = os.path.join(SRC, f)
            assert os.path.isfile(p), p
            shutil.copy2(p, os.path.join(DST, f))
            snap[f] = sig(p)
        json.dump(snap, open(snap_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('备份+快照完成：%d 件 -> %s' % (len(FILES), DST))
    else:
        old = json.load(open(snap_path, encoding='utf-8'))
        bad = 0
        for f in FILES:
            now = sig(os.path.join(SRC, f))
            diff = {k for k, v in now.items() if old[f].get(k) != v}
            extra = set(now) - set(old[f]); gone = set(old[f]) - set(now)
            if diff or extra or gone:
                bad += 1
                print('变动: %s | 改:%s 增:%s 减:%s' % (f[:30], sorted(diff), sorted(extra), sorted(gone)))
            else:
                print('无变动: %s' % f[:30])
        print('diff 完成：%d 件变动 / %d 件' % (bad, len(FILES)))
        return 1 if bad else 0
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
