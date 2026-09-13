# -*- coding: utf-8 -*-
"""结构指标（zip 条目/段落/公式/底纹/文字流）——续作 D+S 两件套对照用"""
import hashlib, json, sys, zipfile
sys.path.insert(0, '工具')
from dxml import qn
from lxml import etree

W, M = qn('w:t'), qn('m:t')


def metric(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    x = etree.fromstring(z.read('word/document.xml'))
    txt = ''.join((n.text or '') for n in x.iter() if n.tag in (W, M))
    return {
        'bytes': __import__('os').path.getsize(path),
        'entries': len(names),
        'media': len([n for n in names if n.startswith('word/media/')]),
        'paras': len(x.findall('.//' + qn('w:p'))),
        'tables': len(x.findall('.//' + qn('w:tbl'))),
        'drawings': len(x.findall('.//' + qn('w:drawing'))),
        'blips': len([n for n in x.iter() if hasattr(n, 'tag') and isinstance(n.tag, str) and etree.QName(n).localname == 'blip']),
        'omath': len(x.findall('.//' + qn('m:oMath'))),
        'omathpara': len(x.findall('.//' + qn('m:oMathPara'))),
        'rad': len(x.findall('.//' + qn('m:rad'))),
        'frac': len(x.findall('.//' + qn('m:f'))),
        'shd_all': len(x.findall('.//' + qn('w:shd'))),
        'pBdr': len(x.findall('.//' + qn('w:pBdr'))),
        'rels': len(z.read('word/_rels/document.xml.rels').split(b'<Relationship ')) - 1,
        'chars': len(txt),
        'sha_text': hashlib.sha256(txt.encode('utf-8')).hexdigest()[:12],
        'sha_docxml': hashlib.sha256(z.read('word/document.xml')).hexdigest()[:12],
    }


out = {}
for tag, p in (('D', sys.argv[1]), ('S', sys.argv[2])):
    out[tag + ' ' + p.split('/')[-1][:24]] = metric(p)
dst = sys.argv[3]
old = {}
try:
    old = json.load(open(dst, encoding='utf-8'))
except Exception:
    pass
for k, v in out.items():
    side = 'old' if k not in old or 'old' not in old[k] else 'new'
    old.setdefault(k, {})[side] = v
json.dump(old, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(old, ensure_ascii=False, indent=1))
