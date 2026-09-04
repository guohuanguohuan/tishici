# -*- coding: utf-8 -*-
"""子步8 T2：使用说明页图例区同步改（附则《讲练件底纹减法》执行节＋任务书T2）。
改动面＝使用说明件图例区（可改）：段4题号块去底纹保加粗＋适用范围标注；段5衔接件式样保留底纹＋标注；
段13芯片/答案值去底纹；段14说明句改写；段14后新增「讲部需背灰底」图例行（样例建模自B讲部1.1.1-1（1）实物）。
不动：段11题干底纹/段16-17条目族/段21定理双标记/二、三区。zip手术仅document.xml，先备份bak/。幂等。"""
import zipfile, re, os, sys, io, shutil, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = r'C:\提示词\高中数学\高中数学同步\人教B版选必1·使用说明.docx'
BAK = os.path.join(HERE, 'bak', '人教B版选必1·使用说明.docx')
SHD = '<w:shd w:val="clear" w:color="auto" w:fill="C9C9C9"/>'
RF = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>'

def run(text, bold=False, shd=False, sz=24):
    rpr = '<w:rPr>%s%s<w:sz w:val="%d"/>%s</w:rPr>' % (
        RF, '<w:b/>' if bold else '<w:b w:val="0"/>', sz, SHD if shd else '')
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, text)

def para_shd(p):
    return re.findall(r'fill="([0-9A-Fa-f]{6})"', p)
def t(p):
    return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))

with zipfile.ZipFile(TARGET) as z:
    names = z.namelist()
    blob = {n: z.read(n) for n in names}
doc = blob['word/document.xml'].decode('utf-8')
rows = re.findall(r'<w:p[ >].*?</w:p>', doc, re.S)
APPLIED = len(rows) == 36   # 已改造过则跳过手术直进回读断言

if not APPLIED:
    assert len(rows) == 35, len(rows)
    if not os.path.exists(BAK):
        shutil.copy2(TARGET, BAK)
        print('备份→bak ✓')
    # ---- 段4：题号run去底纹（保加粗）＋说明句改写加注 ----
    p4 = rows[4]
    assert p4.count(SHD) == 1, p4.count(SHD)   # 仅题号run挂底纹，括注run本无底纹
    p4n = p4.replace(SHD, '', 1)
    old_t4 = '　题号块：「题型号-节内序号．（档位·提分线·卡壳看答案）」——底纹盖整个题号、括注不挂底纹、整块加粗；序号＝节内连续（同节跨题型累进）；题间不留空行，靠底纹分隔。'
    new_t4 = '　题号块：「题型号-节内序号．（档位·提分线·卡壳看答案）」——整块加粗、括注不挂底纹；序号＝节内连续（同节跨题型累进）；题间不留空行。本行题号＝讲练件现行形态（黑字白底·底纹已废止，题块分隔锚＝题干底纹首段）；题号块底纹式样仅衔接件·清单件仍现行（下行即衔接件式样）。'
    assert old_t4 in p4n
    p4n = p4n.replace(old_t4, new_t4, 1)
    # ---- 段5：衔接件式样保留底纹，说明句加注 ----
    p5 = rows[5]
    old_t5 = '　衔接件不区分难度——两段式括注、全部必会。'
    new_t5 = '　衔接件不区分难度——两段式括注、全部必会；题号块底纹维持现行（底纹减法不适用衔接件·清单件）。'
    assert old_t5 in p5
    p5n = p5.replace(old_t5, new_t5, 1)
    assert p5n.count(SHD) == 1   # 衔接题号run底纹不动
    # ---- 段13：芯片×2＋答案值 三处去底纹 ----
    p13 = rows[13]
    assert p13.count(SHD) == 3, p13.count(SHD)
    p13n = p13.replace(SHD, '')
    # ---- 段14：说明句改写（适用范围标注） ----
    p14 = rows[14]
    old_t14 = '　块标签芯片：【答案】【知识点】【分析】【详解】【点睛】【编注】【大招指引】【题后反思】等行内栏目标签挂同款灰底；其后答案值与需背内容一律挂同款灰底（公式型随公式整体挂灰）。'
    new_t14 = '　块标签芯片：【答案】【知识点】【分析】【详解】【点睛】【编注】【大招指引】【题后反思】等行内栏目标签——上行＝讲练件现行形态（芯片与答案值一律黑字白底·底纹已废止）；芯片底纹与答案值灰底仅衔接件·清单件仍现行（其答案值与需背内容挂同款灰底、公式型随公式整体挂灰）。'
    assert old_t14 in p14
    p14n = p14.replace(old_t14, new_t14, 1)
    # ---- 新增「讲部需背灰底」图例行（样例逐字建模自B讲部条目1.1.1-1（1）实物段） ----
    ppr = '<w:pPr><w:spacing w:before="0" w:after="0" w:line="300" w:lineRule="exact"/><w:jc w:val="left"/></w:pPr>'
    newrow = '<w:p>' + ppr + \
        run('定义：在空间，我们把具有') + run('大小', shd=True) + run('和') + \
        run('方向', shd=True) + run('的量叫做空间向量．') + \
        run('　——讲部需背内容灰底＝讲练件讲部保留形态（甲案：填空化遮答自测职能保留，C9C9C9随知识清单权威源照抄带入）。') + '</w:p>'
    # 逐段替换法（防串位）：顺序替换段4→5→13→14，再于14后插入新行
    doc2 = doc.replace(rows[4], p4n, 1).replace(rows[5], p5n, 1) \
              .replace(rows[13], p13n, 1).replace(rows[14], p14n + newrow, 1)
    assert doc2 != doc and doc2.count(newrow) == 1
    assert len(re.findall(r'<w:p[ >].*?</w:p>', doc2, re.S)) == 36
    with zipfile.ZipFile(TARGET + '.tmp', 'w', zipfile.ZIP_DEFLATED) as zo:
        for n in names:
            zo.writestr(n, doc2 if n == 'word/document.xml' else blob[n])
    os.replace(TARGET + '.tmp', TARGET)
    print('使用说明图例区改造落盘：35段→36段')
else:
    print('幂等：改造已在案（36段），跳过手术直进回读断言')

# ---- 回读断言：图例区改造后形态 ----
with zipfile.ZipFile(TARGET) as z:
    d2 = z.read('word/document.xml').decode('utf-8')
r2 = re.findall(r'<w:p[ >].*?</w:p>', d2, re.S)
assert len(r2) == 36
assert para_shd(r2[4]) == [] and '<w:b/>' in r2[4], '段4应无底纹保加粗'
assert para_shd(r2[5]) == ['C9C9C9'], '段5衔接式样底纹保留'
assert para_shd(r2[13]) == [], '段13芯片/答案值应无底纹'
assert '仍现行' in t(r2[4]) and '仍现行' in t(r2[14]) and '底纹已废止' in t(r2[14])
assert para_shd(r2[15]).count('C9C9C9') == 2 and '甲案' in t(r2[15]), '新增讲部需背灰底行'
assert para_shd(r2[17]) == ['C9C9C9'] and para_shd(r2[18]) == ['C9C9C9'], '段16/17条目族不动'
assert para_shd(r2[11]) == ['E0E0E0'], '段11题干底纹不动'
assert para_shd(r2[22]) == ['C9C9C9'], '段21定理双标记不动'
print('回读断言：段4去底纹加粗✓ 段5衔接底纹保留✓ 段13芯片白底✓ 段15讲部需背灰底新增✓ 条目族/题干/定理不动✓')
json.dump({'paras': 36, 'new_row_index': 15,
           'texts': {str(k): t(r2[k]) for k in (4, 5, 13, 14, 15)}},
          open(os.path.join(HERE, '图例改造_子步8.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('图例改造_子步8.json 落盘')
