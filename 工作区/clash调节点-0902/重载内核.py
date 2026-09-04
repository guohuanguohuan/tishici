import json, urllib.request, urllib.parse

BASE = 'http://127.0.0.1:9097'
HDR = {'Authorization': 'Bearer set-your-secret', 'Content-Type': 'application/json'}

def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, headers=HDR,
                                 data=json.dumps(body).encode('utf-8') if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode('utf-8', 'replace')[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')[:300]

# 1) 复测当前节点延迟（内核自测、不经数据面）
node = '🇸🇬新加坡01-0.1倍 | 电信联通推荐'
st, resp = api('GET', '/proxies/' + urllib.parse.quote(node, safe='') +
               '/delay?timeout=6000&url=' + urllib.parse.quote('http://www.gstatic.com/generate_204', safe=''))
print('节点复测:', st, resp)

# 2) 内核配置热重载（force）
st, resp = api('PUT', '/configs?force=true', {'path': '', 'payload': ''})
print('配置重载:', st, resp or '(empty=OK)')

# 3) 复测当前选择
st, resp = api('GET', '/proxies/' + urllib.parse.quote('🚀节点选择', safe=''))
print('当前选择:', json.loads(resp).get('now') if st == 200 else resp)
