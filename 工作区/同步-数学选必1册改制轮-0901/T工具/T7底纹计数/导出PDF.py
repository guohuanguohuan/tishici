# -*- coding: utf-8 -*-
# 一次性：副本导出 PDF（ExportAsFixedFormat 主路径；自建 COM 实例用完 Quit）
import os, sys
import win32com.client

BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\T工具\T7底纹计数'
JOBS = [
    (os.path.join(BASE, '副本', '变体_挂浅底全量.docx'), os.path.join(BASE, 'PDF', 'B挂浅底全量.pdf')),
    (os.path.join(BASE, '副本', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
     os.path.join(BASE, 'PDF', 'I1知识清单.pdf')),
]
os.makedirs(os.path.join(BASE, 'PDF'), exist_ok=True)

word = win32com.client.DispatchEx('Word.Application')   # 自建实例，不碰他人
word.Visible = False
word.DisplayAlerts = 0
try:
    print('Word COM 版本:', word.Version, word.Build)
    for src, dst in JOBS:
        if os.path.exists(dst):
            os.remove(dst)
        doc = word.Documents.Open(src, ReadOnly=True)
        try:
            doc.ExportAsFixedFormat(dst, 17)   # 17 = wdExportFormatPDF
            print('导出OK:', os.path.basename(dst), os.path.getsize(dst), 'bytes,', doc.ComputeStatistics(2), '页')
        finally:
            doc.Close(False)
finally:
    word.Quit()
    print('COM Quit 完成')
