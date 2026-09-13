# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open(sys.argv[1], encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
print('duoxuan:', len(re.findall(r'\\duoxuan(?![a-zA-Z])', body)))
print('liubai:', len(re.findall(r'\\liubai(?![a-zA-Z])', body)))
print('liubai高:', re.findall(r'\\liubai\[([0-9.]+mm)\]', body))
print('kongda:', len(re.findall(r'\\kongda(?![a-zA-Z])', body)))
print('tailfill:', len(re.findall(r'\\tailfill(?![a-zA-Z])', body)))
for w in ('\\newpage', '\\clearpage', '\\ketangboxed', '\\vfill', '\\eject'):
    print(w, body.count(w))
print('ansblock:', len(re.findall(r'\\begin\{ansblock\}', src)))
print('ansitem:', len(re.findall(r'\\ansitem\{', src)))
print('ansnote:', src.count('\\ansnote{详解}'))
print('锚:', len(re.findall(r'^[ \t]*%[ \t]*ans:(\S+)', src, re.M)))
