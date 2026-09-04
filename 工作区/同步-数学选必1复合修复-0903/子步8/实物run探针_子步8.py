# -*- coding: utf-8 -*-
"""实物run探针：从十件实物抽取T2同构断言所需式样run参数。
①讲练件题号块（B/H：层级制题号run）②衔接件题号块（X1）③讲练件芯片【答案】（B/H）
④讲练件答案值run（B/H）⑤讲部需背灰底run（H讲部补挂件）⑥清单需背/条目灰底run（I1/I2）。"""
import zipfile, re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

BASE = r'C:\提示词\高中数学\高中数学同步'
F = {
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
    'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
}

def runs_of(tag):
    with zipfile.ZipFile(os.path.join(BASE, F[tag])) as z:
        doc = z.read('word/document.xml').decode('utf-8')
    out = []
    for rm in re.finditer(r'<w:r>(<w:rPr>.*?</w:rPr>)(<w:t[^>]*>([^<]*)</w:t>)</w:r>', doc, re.S):
        rpr, _, text = rm.group(1), rm.group(2), rm.group(3)
        shd = re.search(r'<w:shd [^>]*fill="([0-9A-Fa-f]{6})"', rpr)
        b = '<w:b/>' in rpr
        b0 = '<w:b w:val="0"/>' in rpr
        sz = re.search(r'<w:sz w:val="(\d+)"/>', rpr)
        out.append({'text': text, 'shd': shd.group(1) if shd else None,
                    'bold': b, 'b0': b0, 'sz': sz.group(1) if sz else None})
    return out

def show(tag, pred, label, cap=4):
    rs = [r for r in runs_of(tag) if pred(r)]
    print('[%s|%s] 命中%d run' % (tag, label, len(rs)))
    for r in rs[:cap]:
        print('   shd=%s bold=%s b0=%s sz=%s | %s' % (r['shd'], r['bold'], r['b0'], r['sz'], r['text'][:60]))
    return rs

R = {}
# ①讲练件题号块：「1.1.1.1-1．」式
R['B_题号块'] = show('B', lambda r: re.match(r'^\d+\.\d+\.\d+\.\d+-\d+．$', r['text']), '讲练件B题号块')
R['H_题号块'] = show('H', lambda r: re.match(r'^\d+\.\d+(\.\d+)*-\d+．$', r['text']), '讲练件H题号块')
# ②衔接件题号块
R['X1_题号块'] = show('X1', lambda r: re.match(r'^\d+\.\d+\.\d+\.\d+-\d+．$', r['text']), '衔接件X1题号块')
# ③芯片【答案】
R['B_芯片'] = show('B', lambda r: r['text'] == '【答案】', '讲练件B芯片【答案】')
R['H_芯片'] = show('H', lambda r: r['text'] == '【答案】', '讲练件H芯片【答案】')
# ④答案值run：【答案】run后紧邻非空白run——简化：抽全文C9C9C9以外的【答案】行答案值不易，改为统计B/H全文C9C9C9 run文本样本
R['B_gray'] = show('B', lambda r: r['shd'] == 'C9C9C9', '讲练件B全文C9C9C9 run', 8)
R['H_gray'] = show('H', lambda r: r['shd'] == 'C9C9C9', '讲练件H全文C9C9C9 run', 8)
# ⑤⑥清单灰底run
R['I1_gray'] = show('I1', lambda r: r['shd'] == 'C9C9C9', '清单I1 C9C9C9 run', 8)
R['I2_gray'] = show('I2', lambda r: r['shd'] == 'C9C9C9', '清单I2 C9C9C9 run', 6)
json.dump({k: [r for r in v[:20]] for k, v in R.items()},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '实物run探针_子步8.json'),
               'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('实物run探针_子步8.json 落盘')
