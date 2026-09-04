import json, subprocess, urllib.parse, urllib.request, concurrent.futures

BASE = 'http://127.0.0.1:9097'
HDR = {'Authorization': 'Bearer set-your-secret', 'Content-Type': 'application/json'}
TEST_URL = 'https://www.gstatic.com/generate_204'

def api(method, path, body=None, timeout=20):
    req = urllib.request.Request(BASE + path, method=method, headers=HDR,
                                 data=json.dumps(body).encode('utf-8') if body is not None else None)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8', 'replace')

d = json.load(open(r'工作区/clash调节点-0902/proxies.json', encoding='utf-8'))['proxies']
grp = '良心云'
cands = [n for n in d[grp]['all']
         if n not in ('DIRECT', 'REJECT') and d.get(n, {}).get('type') not in ('Selector', 'URLTest', 'Fallback')]
print('候选:', len(cands))

def test(name):
    try:
        st, resp = api('GET', f'/proxies/{urllib.parse.quote(name, safe="")}/delay?timeout=5000&url='
                       + urllib.parse.quote(TEST_URL, safe=''), timeout=11)
        j = json.loads(resp)
        return name, j.get('delay') if isinstance(j.get('delay'), int) else None
    except Exception:
        return name, None

ok = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, delay in ex.map(test, cands):
        if delay is not None:
            ok[name] = delay
print('健康:', len(ok))
for k, v in sorted(ok.items(), key=lambda x: x[1])[:10]:
    print(f'  {v:5d}ms  {k}')
