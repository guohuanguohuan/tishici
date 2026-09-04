# -*- coding: utf-8 -*-
"""外网断流补推看守 v2（附则《代理节点处置》NW-3/NW-4/NW-5 配套件）
轮次循环：全量测速（仅日本/美国节点）→ 最快且复测仍活 → 切主选择器 → TLS 双验 github → git push。
当前订阅日美节点零健康或 TLS 连败两轮 → 换另一个订阅（profiles 目录）再测速（NW-4）。
成功推送即退出0。日志：补推看守.log。用法：python 补推看守.py [仓库根] [分支]"""
import json, subprocess, sys, time, urllib.parse, urllib.request, concurrent.futures, os, glob

BASE = 'http://127.0.0.1:9097'
HDR = {'Authorization': 'Bearer set-your-secret', 'Content-Type': 'application/json'}
PROXY = 'http://127.0.0.1:7897'
TEST_URL = 'http://www.gstatic.com/generate_204'
REPO = sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词'
BRANCH = sys.argv[2] if len(sys.argv) > 2 else 'main'
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '补推看守.log')
DEADLINE = time.time() + 3 * 3600
PROFILES = os.path.expandvars(r'%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\profiles')
JPUS = ('🇯🇵', '🇺🇸', '日本', '美国')

def log(msg):
    line = time.strftime('%H:%M:%S') + ' ' + msg
    print(line, flush=True)
    open(LOG, 'a', encoding='utf-8').write(line + '\n')

def api(method, path, body=None, timeout=20):
    req = urllib.request.Request(BASE + path, method=method, headers=HDR,
                                 data=json.dumps(body).encode('utf-8') if body is not None else None)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8', 'replace')

def main_group():
    """主选择器＝候选最多的 Selector（排除 GLOBAL）——订阅切换后组名自适应"""
    st, resp = api('GET', '/proxies')
    ps = json.loads(resp)['proxies']
    sels = [(len(v.get('all', [])), k) for k, v in ps.items()
            if v.get('type') == 'Selector' and k != 'GLOBAL']
    if not sels:
        raise RuntimeError('无 Selector 组')
    return max(sels)[1], ps

def test_node(name):
    try:
        st, resp = api('GET', f'/proxies/{urllib.parse.quote(name, safe="")}/delay?timeout=6000&url='
                       + urllib.parse.quote(TEST_URL, safe=''), timeout=12)
        j = json.loads(resp)
        return name, j.get('delay') if isinstance(j.get('delay'), int) else None
    except Exception:
        return name, None

def tls_ok():
    for _ in range(2):
        r = subprocess.run(['curl', '-x', PROXY, '-s', '-o', '/dev/null', '-w', '%{http_code}',
                            '--max-time', '25', 'https://github.com'], capture_output=True, text=True, timeout=35)
        if r.stdout.strip() != '200':
            return False
        time.sleep(2)
    return True

def push():
    r = subprocess.run(['git', '-c', f'http.proxy={PROXY}', '-C', REPO, 'push', 'origin', BRANCH],
                       capture_output=True, text=True, timeout=900)
    return r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]

def switch_subscription():
    """NW-4：装载 profiles 目录里另一份订阅 YAML（与现订阅不同者）"""
    yamls = sorted(glob.glob(os.path.join(PROFILES, '*.yaml')), key=os.path.getmtime, reverse=True)
    if len(yamls) < 2:
        log('profiles 不足两份，无法换订阅')
        return False
    for y in yamls[1:]:  # 最新一份通常是当前在用，从次新起试
        st, resp = api('PUT', '/configs?force=true', {'path': y, 'payload': ''}, timeout=60)
        log(f'换订阅→{os.path.basename(y)} PUT={st}')
        if st == 204:
            time.sleep(5)
            return True
    return False

rounds, tls_fails = 0, 0
sub_switched = False
while time.time() < DEADLINE:
    rounds += 1
    try:
        grp, ps = main_group()
        now = ps[grp].get('now')
        cands = [n for n in ps[grp].get('all', []) if n not in ('DIRECT', 'REJECT', 'GLOBAL')
                 and any(k in n for k in JPUS)]
        ok = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            for name, delay in ex.map(test_node, cands):
                if delay is not None:
                    ok[name] = delay
        log(f'轮{rounds}: 组={grp} 日美健康{len(ok)}/{len(cands)} 当前={now}')
        if not ok:
            if not sub_switched and switch_subscription():
                sub_switched = True
                continue
            time.sleep(240); continue
        best = min(ok, key=ok.get)
        if best != now:
            st, _ = api('PUT', '/proxies/' + urllib.parse.quote(grp, safe=''), {'name': best})
            log(f'轮{rounds}: 切换→{best}({ok[best]}ms) PUT={st}')
            time.sleep(3)
        _, d2 = test_node(best)
        if d2 is None:
            log(f'轮{rounds}: {best} 复测即死，跳过'); time.sleep(120); continue
        if not tls_ok():
            tls_fails += 1
            log(f'轮{rounds}: TLS双验不过（连败{tls_fails}）')
            if tls_fails >= 2 and not sub_switched and switch_subscription():
                sub_switched = True; tls_fails = 0
                continue
            time.sleep(240); continue
        suc, out = push()
        log(f'轮{rounds}: push rc={"0" if suc else "非0"} {out}')
        if suc or 'Everything up-to-date' in out:
            log('SUCCESS 推送完成')
            sys.exit(0)
        time.sleep(240)
    except Exception as e:
        log(f'轮{rounds}: 异常 {e!r}'); time.sleep(120)
log('TIMEOUT 3小时未推送成功')
sys.exit(1)
