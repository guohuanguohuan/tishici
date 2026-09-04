import json, urllib.request, urllib.parse

BASE = 'http://127.0.0.1:9097'
HDR = {'Authorization': 'Bearer set-your-secret', 'Content-Type': 'application/json'}
TARGET = '🇸🇬新加坡01-0.1倍 | 电信联通推荐'
GROUP = '🚀节点选择'

def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, headers=HDR,
                                 data=json.dumps(body).encode('utf-8') if body else None)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')

st, resp = api('PUT', '/proxies/' + urllib.parse.quote(GROUP, safe=''), {'name': TARGET})
print('PUT', st, resp[:200] if resp else '(empty=OK)')

# 回读确认
d = json.load(open(r'工作区/clash调节点-0902/proxies.json', encoding='utf-8'))['proxies']
req = urllib.request.Request(BASE + '/proxies/' + urllib.parse.quote(GROUP, safe=''), headers=HDR)
with urllib.request.urlopen(req, timeout=15) as r:
    now = json.load(r).get('now')
print('回读当前节点:', now)
