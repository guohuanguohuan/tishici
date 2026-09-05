# -*- coding: utf-8 -*-
"""docx 级 word/document.xml 字符串置换工具。
用法: python docx_fix.py <docx路径> <job.json>
job.json: {"edits":[{"name":"...","old":"...","new":"..."}], "extra_files":{"word/_rels/document.xml.rels": [...edits...]}}
每个 old 必须在目标文件内恰好出现 1 次，否则拒绝写入。
产出: 直接覆盖写回 docx（调用方已留 .bak），并在 stdout 打印每处命中校验。
"""
import json, shutil, sys, zipfile, os

def main():
    docx_path, job_path = sys.argv[1], sys.argv[2]
    with open(job_path, encoding='utf-8') as f:
        job = json.load(f)
    zin = zipfile.ZipFile(docx_path, 'r')
    names = zin.namelist()
    data = {n: zin.read(n) for n in names}
    infos = {n: zin.getinfo(n) for n in names}
    zin.close()

    def apply_edits(target, edits):
        raw = data[target].decode('utf-8')
        for e in edits:
            cnt = raw.count(e['old'])
            want_all = e.get('count') == 'all'
            if cnt == 0 or (cnt != 1 and not want_all):
                print('REJECT [%s] %s: old 命中 %d 次（要求 %s）' % (target, e['name'], cnt, '≥1' if want_all else '恰好1次'))
                sys.exit(2)
            raw = raw.replace(e['old'], e['new'])
            print('OK [%s] %s: %d 处, 每处 -%d +%d 字节' % (target, e['name'], cnt, len(e['old']), len(e['new'])))
        data[target] = raw.encode('utf-8')

    apply_edits('word/document.xml', job.get('edits', []))
    for target, edits in job.get('extra_files', {}).items():
        apply_edits(target, edits)

    tmp_path = docx_path + '.newtmp'
    zout = zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED)
    skip = set(job.get('delete_entries', []))
    for n in skip:
        print('DEL 条目', n)
    for n in names:  # 保持原条目顺序
        if n in skip:
            continue
        zi = zipfile.ZipInfo(n, date_time=infos[n].date_time)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = infos[n].external_attr
        zout.writestr(zi, data[n])
    zout.close()
    shutil.move(tmp_path, docx_path)
    print('WROTE', docx_path)

if __name__ == '__main__':
    main()
