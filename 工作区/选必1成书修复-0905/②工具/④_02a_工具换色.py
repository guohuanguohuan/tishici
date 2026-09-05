# -*- coding: utf-8 -*-
"""④轮步骤2a：工具写侧/计数侧常量 C9C9C9→C7C7C7 批量对账（10 件简单换色件）。
灰底改色.py 豁免（PRESETS 0831迁移＋docstring 沿革＝历史档案，不删不改）；
底纹去除器.py 另做标识符 C9→FILL_C 改名（值改 C7C7C7 后消名实差）。
逐处打印 行号: 旧文 → 新文 落对账；py_compile 由后续步骤2c统一跑。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TOOL = r'C:\提示词\工具'
FILES = ['底纹批量器.py', '底纹去除器.py', '题号块三段式.py', '标题整行底纹.py',
         '条目号底纹.py', '答案值分型改标.py', '块标签芯片.py', '难度前置.py',
         '环绕转换.py', '解析块浅底挂载.py']
total = 0
for fn in FILES:
    p = TOOL + '\\' + fn
    src = open(p, encoding='utf-8').read()
    n = src.count('C9C9C9')
    lines = src.split('\n')
    log = []
    for i, ln in enumerate(lines, 1):
        if 'C9C9C9' in ln:
            log.append('  L%d: %s' % (i, ln.strip()[:110]))
    new = src.replace('C9C9C9', 'C7C7C7')
    if fn == '底纹去除器.py':
        new = re.sub(r'\bC9\b', 'FILL_C', new)
    open(p, 'w', encoding='utf-8', newline='').write(new)
    total += n
    print('%s：C9C9C9×%d 处换 C7C7C7%s' % (fn, n, '＋标识符C9→FILL_C' if fn == '底纹去除器.py' else ''))
    print('\n'.join(log))
print('合计 %d 处（10 件）' % total)
