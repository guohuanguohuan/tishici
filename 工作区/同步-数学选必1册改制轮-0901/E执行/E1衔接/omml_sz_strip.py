# -*- coding: utf-8 -*-
# 一次性脚本（E1衔接·规格书§6裁决1）：剥除 m:oMath 子树内显式 w:sz/w:szCs（交docDefaults继承24半点）
# 公式字体Cambria Math与公式内容不碰；文字零改动（w:t/m:t流恒等断言）；计数落盘json。
import sys, io, os, json, zipfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)

path, out, report = sys.argv[1], sys.argv[2], sys.argv[3]

def textflow(xml_bytes):
    root = etree.fromstring(xml_bytes)
    return ''.join(t.text or '' for t in root.iter(q('t'))) + '|' + ''.join(
        t.text or '' for t in root.iter(qm('t')))

stats = {}
zin = zipfile.ZipFile(path)
members = {}
for name in zin.namelist():
    members[name] = zin.read(name)
zin.close()

for name in list(members):
    base = os.path.basename(name)
    if not (name.startswith('word/') and name.endswith('.xml')):
        continue
    if not any(k in base for k in ('document', 'header', 'footer')):
        continue
    root = etree.fromstring(members[name])
    omaths = root.findall('.//' + qm('oMath'))
    if not omaths:
        continue
    before = textflow(members[name])
    cnt = {'m:r挂点': 0, 'ctrlPr挂点': 0, '其他挂点': 0, 'szCs': 0}
    for om in omaths:
        for sz in om.iter(q('sz')):
            parent = sz.getparent()
            gp = parent.getparent() if parent is not None else None
            if gp is not None and etree.QName(gp).localname == 'ctrlPr':
                cnt['ctrlPr挂点'] += 1
            elif gp is not None and etree.QName(gp).localname == 'r' and parent.tag == q('rPr'):
                # m:r 内 w:rPr（gp.localname=='r' 但命名空间为 W）——判主run挂点
                cnt['m:r挂点'] += 1
            else:
                cnt['其他挂点'] += 1
            parent.remove(sz)
        for szcs in om.iter(q('szCs')):
            p = szcs.getparent()
            p.remove(szcs)
            cnt['szCs'] += 1
    after = textflow(etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True))
    assert before == after, '文字流意外变动: %s' % name
    if cnt['m:r挂点'] or cnt['ctrlPr挂点'] or cnt['其他挂点'] or cnt['szCs']:
        stats[name] = cnt
        members[name] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

# 复核：全包 m:oMath 子树内已无 w:sz/w:szCs
resid = 0
for name, data in members.items():
    base = os.path.basename(name)
    if not (name.startswith('word/') and name.endswith('.xml')):
        continue
    if not any(k in base for k in ('document', 'header', 'footer')):
        continue
    root = etree.fromstring(data)
    for om in root.findall('.//' + qm('oMath')):
        resid += len(om.findall('.//' + q('sz'))) + len(om.findall('.//' + q('szCs')))
assert resid == 0, '残留 %d' % resid

with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in members.items():
        zout.writestr(name, data)

total = {'m:r挂点': sum(v['m:r挂点'] for v in stats.values()),
         'ctrlPr挂点': sum(v['ctrlPr挂点'] for v in stats.values()),
         '其他挂点': sum(v['其他挂点'] for v in stats.values()),
         'szCs': sum(v['szCs'] for v in stats.values())}
rep = {'in': path, 'out': out, '部件明细': stats, '合计': total, '残留复核': resid}
with open(report, 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False))
