import re, glob, os
pat = re.compile(r'\\+[a-zA-Z@]+')
mac = {}
for f in sorted(glob.glob(r'C:\提示词\工作区\字替对照-0909\variantF\figs\*.tikz')):
    lines = open(f, encoding='utf-8').read().split('\n')
    for ln, s in enumerate(lines, 1):
        # 剥去行内注释（TikZ 注释 % 至行尾；\% 转义不算）
        code = re.split(r'(?<!\\)%', s)[0]
        for m in pat.findall(code):
            mac.setdefault(m, []).append((os.path.basename(f), ln))
print('TOTAL DISTINCT (代码区, 注释已剥)', len(mac))
for m in sorted(mac):
    where = mac[m]
    print('%-22s n=%-3d %s' % (m, len(where), where[0][0] + ':' + str(where[0][1])))
