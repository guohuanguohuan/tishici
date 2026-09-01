# -*- coding: utf-8 -*-
"""R1审计工具运行器v2：os级stdout重定向，兼容工具自身的TextIOWrapper重包。
用法: python run_tool.py <工具.py> <输出文件> [args...]"""
import sys, os, tempfile
tool, outpath, args = sys.argv[1], sys.argv[2], sys.argv[3:]
TOOLDIR = r'C:\提示词\工具'
code = open(os.path.join(TOOLDIR, tool), encoding='utf-8').read()
sys.path.insert(0, TOOLDIR)
os.chdir(TOOLDIR)
sys.argv = [tool] + args
tmp = tempfile.NamedTemporaryFile(mode='w+b', suffix='.log', delete=False)
tmp.close()
saved = os.dup(1)
fd = os.open(tmp.name, os.O_WRONLY | os.O_TRUNC)
os.dup2(fd, 1); os.close(fd)
try:
    exec(compile(code, tool, 'exec'), {'__name__': '__main__', '__file__': os.path.join(TOOLDIR, tool)})
except SystemExit:
    pass
finally:
    sys.stdout.flush()
    os.dup2(saved, 1); os.close(saved)
data = open(tmp.name, 'rb').read()
try:
    txt = data.decode('utf-8')
except UnicodeDecodeError:
    txt = data.decode('gbk', 'replace')
os.unlink(tmp.name)
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(txt)
print(txt[:1500].encode('utf-8', 'replace').decode('utf-8'))
