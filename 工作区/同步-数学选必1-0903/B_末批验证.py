# -*- coding: utf-8 -*-
"""B代理·末批验证：页眉页脚jc/sz/字体；C件恢复完整性哈希比对；装订单件名↔实际文件映射。只读。"""
import io, re, sys, zipfile, hashlib, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SYNC = r'C:\提示词\高中数学\高中数学同步'
CONTENT = [
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
    ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
    ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
    ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
    ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
    ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
    ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
    ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
    ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
    ('H',  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
]
print('## 1、页眉页脚形态：jc/sz/字体（十件×2部件）')
for tag, fn in CONTENT:
    z = zipfile.ZipFile(SYNC + '\\' + fn)
    for part in ('word/header1.xml', 'word/footer1.xml'):
        x = z.read(part).decode('utf-8')
        jcs = set(re.findall(r'<w:jc w:val="([^"]+)"', x))
        szs = set(re.findall(r'<w:sz w:val="(\d+)"/>', x))
        fonts = set(re.findall(r'w:eastAsia="([^"]+)"', x)) | set(re.findall(r'w:ascii="([^"]+)"', x))
        paras = len(re.findall(r'<w:p\b', x))
        tabs = len(re.findall(r'<w:tab/>', x))
        print(f'{tag} {part.split("/")[-1]}: jc={jcs or "(无,默认left)"} sz={szs} fonts={sorted(fonts)} 段落数={paras} w:tab={tabs}')
    z.close()
print()
print('## 2、C件恢复完整性：当前文件 vs 工作区head_C.docx留档（sha256+逐部件）')
cur = SYNC + r'\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'
bak = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\head_C.docx'
h1 = hashlib.sha256(open(cur, 'rb').read()).hexdigest()
h2 = hashlib.sha256(open(bak, 'rb').read()).hexdigest()
print(f'当前C sha256={h1}')
print(f'留档   sha256={h2}')
print(f'整包一致={h1 == h2}')
z1, z2 = zipfile.ZipFile(cur), zipfile.ZipFile(bak)
n1, n2 = set(z1.namelist()), set(z2.namelist())
print(f'成员集一致={n1 == n2}（{len(n1)}/{len(n2)}）')
diffs = 0
for n in sorted(n1 & n2):
    a, b = z1.read(n), z2.read(n)
    if a != b:
        diffs += 1
        print(f'  差异部件：{n} {len(a)}B vs {len(b)}B')
print(f'逐部件差异数={diffs}')
print()
print('## 3、装订单19实体行↔实际文件映射核对')
for v in ['人教B版选必1·封面.docx', '人教B版选必1·使用说明.docx', '人教B版选必1·册目录页.docx']:
    print(f'  配页行 → {v} 存在={os.path.exists(SYNC + os.sep + v)}')
for p in sorted(os.path.basename(x) for x in glob.glob(SYNC + os.sep + '*部分封面*')):
    print(f'  部分封面行 → {p}')
for tag, fn in CONTENT:
    print(f'  内容件行[{tag}] → {fn} 存在={os.path.exists(SYNC + os.sep + fn)}')
