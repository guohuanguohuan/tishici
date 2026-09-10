import re, glob, os, sys
pat = re.compile(r'\\+[a-zA-Z@]+')
mac = {}
for f in sorted(glob.glob(r'C:\提示词\工作区\字替对照-0909\variantF\figs\*.tikz')):
    s = open(f, encoding='utf-8').read()
    for m in sorted(set(pat.findall(s))):
        mac.setdefault(m, []).append(os.path.basename(f))
print('TOTAL DISTINCT', len(mac))
for m in sorted(mac):
    print('%-24s %s' % (m, ' '.join(mac[m])))
