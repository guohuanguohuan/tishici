# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""p6_width_probe.py — P6部分（第2章讲练 E/F/G/H 四卷）页眉同串品牌前缀串宽实测探针（E5）

方法＝复刻 工具/页眉面包屑挂载.py com_linecount（A4＋1.5cm边距、宋体/TNR 9pt单段、
ComputeStatistics(wdStatisticLines)）。worst-case节名取四卷最长锚（H卷 2.8 直线与圆锥曲线
的位置关系）。断言＝worst-case带前缀=1行 → 四卷保留品牌前缀；>1行 → 四卷统一 --no-brand。
"""
import win32com.client

PREFIX = '羿郭工作室·人教B版选必1 第2章 平面解析几何·讲练（共197页）'
NOBRAND = '人教B版选必1 第2章 平面解析几何·讲练（共197页）'
ANCHORS = {
    'E': '2.2.1 直线的倾斜角与斜率',
    'F': '2.3.4 圆与圆的位置关系',
    'G': '2.6.1 双曲线的标准方程',
    'H': '2.8 直线与圆锥曲线的位置关系',   # 四卷最长锚（worst-case）
}
TAIL = '第999页'


def lines(word, doc, s):
    doc.Content.Delete()
    rng = doc.Range(0, 0)
    rng.InsertAfter(s)
    r2 = doc.Range(0, len(s))
    r2.Font.NameFarEast = '宋体'
    r2.Font.Name = 'Times New Roman'
    r2.Font.Size = 9
    return r2.ComputeStatistics(1)   # wdStatisticLines


def main():
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    out = []
    try:
        doc = word.Documents.Add()
        try:
            ps = doc.PageSetup
            ps.PaperSize = 7
            cm = lambda c: c * 28.3465
            ps.TopMargin = ps.BottomMargin = cm(1.5)
            ps.LeftMargin = ps.RightMargin = cm(1.5)
            for k, a in ANCHORS.items():
                for tag, pre in (('带前缀', PREFIX), ('省前缀', NOBRAND)):
                    s = pre + '　' + a + '　' + TAIL
                    out.append((k, tag, lines(word, doc, s), s))
        finally:
            doc.Close(False)
    finally:
        word.Quit()
    for k, tag, n, s in out:
        print('%s %s %d行 | %s' % (k, tag, n, s))
    worst = [n for k, t, n, s in out if k == 'H' and t == '带前缀'][0]
    print('CONCLUSION:', 'KEEP-BRAND' if worst == 1 else 'NO-BRAND',
          '(P6四卷统一，worst-case=H带前缀%d行)' % worst)


if __name__ == '__main__':
    main()
