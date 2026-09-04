# -*- coding: utf-8 -*-
"""COM driver：配页两件一次会话＋成品三件逐件会话；90s/开卷护栏、每件≤2次尝试；挂→SHA全同副本降级→再挂记环境阻断。禁动用户WINWORD实例。"""
import sys, io, os, json, time, subprocess, hashlib, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TMP = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp'
WORKER = os.path.join(TMP, 'com_worker_收尾.py')
BASE = r'C:\提示词\高中数学\高中数学同步'
COPYDIR = os.path.join(TMP, '原件全同副本')
os.makedirs(COPYDIR, exist_ok=True)
USER_PIDS = {28012, 26168, 5988, 13320, 10308}  # 任务书登记的5个用户WINWORD实例
GUARD = 90

PEIYE = [os.path.join(BASE, '人教B版选必1·册目录页.docx'), os.path.join(BASE, '人教B版选必1·使用说明.docx')]
SPOT = {
 '讲练2d(H)': os.path.join(BASE, '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
 '衔接2(X2)': os.path.join(BASE, '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
 '讲练2b(F)': os.path.join(BASE, '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
}
EXPECT = {'讲练2d(H)': 70, '衔接2(X2)': 5, '讲练2b(F)': 56}

def sha(fp):
    h = hashlib.sha256()
    with open(fp, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def make_copy(fp):
    dst = os.path.join(COPYDIR, os.path.basename(fp))
    shutil.copyfile(fp, dst)  # 自进程字节拷贝，不碰原件元数据
    s1, s2 = sha(fp), sha(dst)
    assert s1 == s2, '副本sha不等'
    return dst, s1

def read_status(path):
    evs = []
    if os.path.exists(path):
        for ln in open(path, encoding='utf-8'):
            ln = ln.strip()
            if ln:
                evs.append(json.loads(ln))
    return evs

def run_session(tag, files):
    """一次worker会话顺开files；逐开卷90s护栏。返回 {basename: pages or None}"""
    status = os.path.join(TMP, 'com_status_%s.jsonl' % tag)
    if os.path.exists(status):
        os.remove(status)
    proc = subprocess.Popen([sys.executable, WORKER, status] + files,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    pending = [os.path.basename(f) for f in files]
    result = {n: None for n in pending}
    while True:
        evs = read_status(status)
        done_files = {e['file']: e for e in evs if e['ev'] == 'open_done'}
        starts = {e['file']: e for e in evs if e['ev'] == 'open_start'}
        for n in pending:
            if n in done_files:
                result[n] = done_files[n]['pages']
        # 完成判定
        if any(e['ev'] == 'all_done' for e in evs) or proc.poll() is not None:
            time.sleep(0.3)
            evs = read_status(status)
            for e in evs:
                if e['ev'] == 'open_done':
                    result[e['file']] = e['pages']
                if e['ev'] == 'error':
                    print('  [%s] worker error: %s' % (tag, e['msg']))
            break
        # 护栏：当前开卷中超90s
        cur = None
        for n in pending:
            if n in starts and n not in done_files:
                cur = (n, starts[n]['ts'])
        if cur and time.time() - cur[1] > GUARD:
            wp = next((e.get('pid') for e in evs if e['ev'] == 'word_started'), None)
            if wp and wp not in USER_PIDS:
                subprocess.run(['taskkill', '/F', '/PID', str(wp)], capture_output=True)
            elif wp in USER_PIDS:
                print('  [%s] !! worker的Word PID=%d 撞上用户实例名单，拒绝taskkill' % (tag, wp))
            proc.kill()
            print('  [%s] 开卷超90s挂死，已中止: %s' % (tag, cur[0]))
            break
        time.sleep(1)
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    return result

out = {'配页会话': {}, '成品抽测': {}, 'attempts': {}}

# 配页两件：一次会话（P2）
r = run_session('peiye', PEIYE)
out['attempts']['配页'] = 1
if any(v is None for v in r.values()):
    # 降级：SHA全同副本重试（第2次尝试）
    files2 = []
    for f in PEIYE:
        if r[os.path.basename(f)] is None:
            cp, s = make_copy(f)
            print('  原件受阻→SHA全同副本: %s sha=%s' % (os.path.basename(f), s[:16]))
            files2.append(cp)
        else:
            files2.append(f)
    r2 = run_session('peiye2', files2)
    out['attempts']['配页'] = 2
    for k in r:
        if r[k] is None:
            r[k] = r2.get(k)
out['配页会话'] = r
print('配页两件 COM页数: %s' % r)

# 成品三件：逐件会话，各自≤2次
for tag, fp in SPOT.items():
    r = run_session('spot_' + tag, [fp])
    n = os.path.basename(fp)
    att = 1
    if r[n] is None:
        cp, s = make_copy(fp)
        print('  [%s] 原件受阻→SHA全同副本 sha=%s' % (tag, s[:16]))
        r = run_session('spot2_' + tag, [cp])
        att = 2
    pages = r[n]
    verdict = None
    if pages is None:
        verdict = '环境阻断'
    else:
        verdict = '零漂移✓' if pages == EXPECT[tag] else '漂移✗(实测%d≠期望%d)' % (pages, EXPECT[tag])
    out['成品抽测'][tag] = {'pages': pages, 'expect': EXPECT[tag], 'verdict': verdict, 'attempts': att}
    print('[%s] COM页数=%s 期望=%d → %s（尝试%d次）' % (tag, pages, EXPECT[tag], verdict, att))

json.dump(out, open(os.path.join(TMP, 'com复核_收尾.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('com复核_收尾.json 落盘')
