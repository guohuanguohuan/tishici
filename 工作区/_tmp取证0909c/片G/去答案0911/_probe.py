# -*- coding: utf-8 -*-
import io, re, os, json, sys
sys.stdout.reconfigure(encoding='utf-8')
C = r'C:/提示词/工作区/字替对照-0909'
def brace_arg(s, i):
    # s[i] == '{'; return (content, j) where s[j-1]=='}'
    assert s[i] == '{'
    d = 0
    for k in range(i, len(s)):
        if s[k] == '{': d += 1
        elif s[k] == '}':
            d -= 1
            if d == 0: return s[i+1:k], k+1
    raise ValueError('unbalanced')

def parse_items(body):
    items = []
    for m in re.finditer(r'\\dansitem\{|\\ansitem\{', body):
        start = m.end() - 1  # at '{' of first arg
        k1, j = brace_arg(body, start)
        if j >= len(body) or body[j] != '{':
            continue
        k2, j2 = brace_arg(body, j)
        items.append((k1, k2))
    return items

def clean_value(v):
    # 去 \( \) 包裹、LaTeX 命令、花括号与定界空格——留 pdf 明文可核的字符核
    v = re.sub(r'\\\(\\\)', '', v)
    core = re.sub(r'\\[a-zA-Z]+', '', v)
    core = re.sub(r'[{}\\^_$]', '', core)
    core = re.sub(r'\s+', '', core)
    return core

b = io.open(os.path.join(C, '导学件答案册-v1', 'body.tex'), encoding='utf-8').read()
items = parse_items(b)
print('items:', len(items))
for k, v in items:
    print(json.dumps([k, v[:60], clean_value(v)], ensure_ascii=False))
print('ansline defs:', len(re.findall(r'(?m)^\\ansline\{', b)))
from collections import Counter
lab = Counter(re.findall(r'(?m)^\\ansline\{([^}]*)\}', b))
print('ansline labels:', dict(lab))

db = io.open(os.path.join(C, 'variantF', 'body.tex'), encoding='utf-8').read()
print('variantF body: ansline', db.count('\\ansline{'), 'jiexi', db.count('\\jiexi{'),
      'anshang? no —; kongda', db.count('\\kongda{'), 'zhenti', db.count('\\zhenti{'))
