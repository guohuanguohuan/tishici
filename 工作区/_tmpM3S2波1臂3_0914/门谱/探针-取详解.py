import re
import io

tex = io.open(r'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时07-圆的方程/main.tex', encoding='utf-8').read()
for key in ['T15', 'T16', 'T10', 'T13', 'T11']:
    m = re.search(r'begin\{ansblock\}\[2章-练-课时07-' + key + r'\](.*?)end\{ansblock\}', tex, re.S)
    body = m.group(1)
    a = re.search(r'ansnote\{详解\}\{(.*)', body, re.S)
    txt = a.group(1).replace('\\par\\noindent', '§')
    txt = re.sub(r'\\[a-zA-Z]+', '', txt)
    txt = re.sub(r'[{}\\$]', '', txt)
    print(key, '=>', txt[:70].replace('\n', ' '))
