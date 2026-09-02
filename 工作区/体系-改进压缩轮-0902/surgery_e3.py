# -*- coding: utf-8 -*-
"""E3 手术脚本：ai自行经验积累.md（a1-a8 + 术语修复 + 教训条目，一次写完）
方法：二进制域替换（rb→decode utf-8→replace→encode→wb，保留 CRLF）。
测量：文本域（io.open universal-newline，CRLF 归一为 \n），与规格书/分析报告口径一致。
"""
import io, sys

PATH = r'C:\提示词\ai自行经验积累.md'

def text_read(p):
    return io.open(p, 'r', encoding='utf-8').read()

ENTRIES = [
    ('> 记录历次任务可复用经验，新任务前先读；按时间追加、标注日期与任务。唯一经验文件，经验禁另记他处；与公共规则/总控冲突以后者为准并立即修正本文件；追加前查重、收尾去重精简，≤200行且≤12,000字符；旧体系条目下次收尾压缩为1行。',
     '> 记录历次任务可复用经验，新任务前先读；按时间追加、标注日期与任务；与公共规则/总控冲突以后者为准（§4）；追加前查重、收尾去重精简，≤200行≤12,000字符；旧体系条目下次收尾压缩为1行。',
     'a1'),
    ('；PDF灰度四值190/209/201/224',
     '；灰度四值见首条',
     'a2'),
    ('（＝w:shd C9C9C9灰底，见OMML公式定论；w:bdr已废）',
     '（＝w:shd C9C9C9灰底；w:bdr方框已废）',
     'a3'),
    ('删除台账重生成＝行级手术；题块判定兼容答案标签变体（讲块「N．」误判见快查清单）',
     '删除台账重生成＝行级手术',
     'a4'),
    ('注册表AutoSave绝对路径模板+EnsureUniqueFilenames+OpenViewer=0；改后杀进程重启生效（注册表系旧径存档、现行主路径免全局配置，§14）',
     '（注册表旧径存档、现行主路径免全局配置，§14；旧径AutoSave模板+EnsureUniqueFilenames+OpenViewer=0+改后杀进程重启生效）',
     'a5'),
    ('公式Cambria Math不碰；PUA字符run跳过字体修改',
     '公式Cambria Math不碰；PUA字符run跳过',
     'a6'),
    ('>50MB跑未引用媒体审计（rels＋正文双查零引用才清），审计后>80MB自行拆件（禁压缩/降质/询问，边界同工作件，§12）',
     '>50MB跑未引用媒体审计（rels＋正文双查），审计后>80MB自行拆件（禁压缩/降质/询问，§12）',
     'a7'),
    ('退化件「N．」；分层卷断号合法＋跳号就地说明）；底纹盖全号',
     '退化件「N．」）；底纹盖全号',
     'a8'),
    ('「解析档」仅内容集合概念',
     '「解析块」仅内容集合概念',
     '术语'),
]

LESSON = '- 2026-09-02 体系改进压缩轮（多智能体）——独有教训：①六文件实释约669字（公共仅37）②目标量仅期望非配额、释不出实报不判返工③压缩主力＝删重抄公共规则段（页眉/层级/灰底参数三族）'

def main():
    b0 = open(PATH, 'rb').read()
    raw = b0.decode('utf-8')            # CRLF prescatived, len basis = 自动含2字符/换行
    t0 = text_read(PATH)                # 文本域基线
    base_len = len(t0)
    base_lines = len(t0.split('\n'))    # 文本域行数（末行无换行→136，追加后137）
    print('BASE   text_len=%d  text_lines=%d  split_n=%d' % (base_len, base_lines, len(t0.split('\n'))))

    # ---- 断言 + 应用（binary 域），并记录 net（文本域等价） ----
    total_net = 0
    for old, new, name in ENTRIES:
        c = raw.count(old)
        if c != 1:
            print('!! ASSERT FAIL %s count=%d -> ABORT' % (name, c))
            sys.exit(1)
        raw = raw.replace(old, new)
        net = len(new) - len(old)
        total_net += net
        print('OK   %-6s count=1  old_len=%d new_len=%d  net=%d' % (name, len(old), len(new), net))
    print('TOTAL net = %d' % total_net)

    # ---- 教训行：先断言 <=100（含换行）----
    lesson_nl = len(LESSON) + 1
    print('LESSON text_len=%d  with_newline=%d  (<=100 => %s)' % (len(LESSON), lesson_nl, lesson_nl <= 100))
    if lesson_nl > 100:
        print('!! LESSON over 100 -> ABORT')
        sys.exit(1)

    # ---- 追加（binary 域：末行已有 \r\n，追加 LESSON + CRLF）----
    raw = raw + LESSON + '\r\n'
    open(PATH, 'wb').write(raw.encode('utf-8'))
    print('WRITTEN binary_chars=%d' % len(raw))

    # ---- 文本域终态验证 ----
    v = text_read(PATH)
    v_len = len(v)
    v_lines = len(v.split('\n'))
    print('FINAL  text_len=%d  (<=12000 => %s)' % (v_len, v_len <= 12000))
    print('FINAL  text_lines=%d  (<=200 => %s)' % (v_lines, v_lines <= 200))
    print('FINAL  net vs base = %d' % (v_len - base_len))
    print('FINAL  lines vs base = %d' % (v_lines - base_lines))

    # 逐条目：改后串在位 + 旧串清零
    for old, new, name in ENTRIES:
        print('  VERIFY %-6s new_in=%s old_count=%d' % (name, (v.count(new) >= 1), v.count(old)))
    print('  VERIFY LESSON in=%s  LESSON newline_len=%d' % (LESSON in v, len(LESSON)+1))

if __name__ == '__main__':
    main()
