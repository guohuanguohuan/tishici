# -*- coding: utf-8 -*-
# P1 轮3 收口轧账校验：四行恒等式 + 列合计 + 难度翼 + 缺口 + 分域无双计
secs = {
 #        素材域 正文 代表 第2题 拓展 删除 衔接 移交 | 正文简 中 难 | 池 回捞 微专题 | 配额简 中 难
 '9.1': dict(m=12,z=10,rep=6,d2=4,e=2,x=0,j=0,y=0, sj=7,sm=3,sn=0, pool=6,hq=6,wk=0, qj=10,qm=4,qn=2),
 '9.2': dict(m=34,z=15,rep=14,d2=1,e=17,x=2,j=0,y=0, sj=9,sm=4,sn=2, pool=16,hq=4,wk=14, qj=10,qm=4,qn=2),
 '9.3': dict(m=38,z=14,rep=13,d2=1,e=21,x=3,j=0,y=0, sj=8,sm=4,sn=2, pool=13,hq=4,wk=21, qj=10,qm=4,qn=2),
 '9.4': dict(m=13,z=7,rep=5,d2=2,e=6,x=0,j=0,y=0, sj=2,sm=4,sn=1, pool=6,hq=5,wk=2, qj=10,qm=4,qn=2),
}
ok=True
def chk(tag,a,b):
    global ok
    r = '✓' if a==b else '✗'
    if a!=b: ok=False
    print(f'{r} {tag}: {a} vs {b}')
for s,d in secs.items():
    chk(f'{s} 行恒等式 素材域=正文+拓展+删+衔接+移交', d['m'], d['z']+d['e']+d['x']+d['j']+d['y'])
    chk(f'{s} 域构成 素材域=池+回捞+微专题', d['m'], d['pool']+d['hq']+d['wk'])
    chk(f'{s} 组合账 正文=代表+第2题', d['z'], d['rep']+d['d2'])
    chk(f'{s} 难度账 正文=简+中+难', d['z'], d['sj']+d['sm']+d['sn'])
T = lambda k: sum(d[k] for d in secs.values())
chk('列合计 素材域', T('m'), 97)
chk('列合计 正文', T('z'), 46)
chk('列合计 拓展', T('e'), 46)
chk('列合计 删除', T('x'), 5)
chk('全章恒等式 97=正文+拓展+删', T('m'), T('z')+T('e')+T('x'))
chk('池侧 60', T('pool')+T('hq'), 60); chk('池41', T('pool'), 41); chk('回捞19', T('hq'), 19)
chk('微专题 37', T('wk'), 37)
chk('正文难度 简26', T('sj'), 26); chk('中15', T('sm'), 15); chk('难5', T('sn'), 5)
chk('配额 64', 4*16, 64); chk('配额骨架 40/16/8', T('qj')+T('qm')+T('qn'), 64)
gj = sum(d['qj']-d['sj'] for d in secs.values()); gm = sum(d['qm']-d['sm'] for d in secs.values()); gn = sum(d['qn']-d['sn'] for d in secs.values())
chk('缺口简14', gj, 14); chk('缺口中1', gm, 1); chk('缺口难3', gn, 3)
chk('缺口合计=64-46', gj+gm+gn, 64-T('z'))
chk('逐节缺口和 9.1=6', (secs['9.1']['qj']-secs['9.1']['sj'])+(secs['9.1']['qm']-secs['9.1']['sm'])+(secs['9.1']['qn']-secs['9.1']['sn']), 6)
chk('逐节缺口和 9.2=1', (secs['9.2']['qj']-secs['9.2']['sj']), 1)
chk('逐节缺口和 9.3=2', (secs['9.3']['qj']-secs['9.3']['sj']), 2)
chk('逐节缺口和 9.4=9', (secs['9.4']['qj']-secs['9.4']['sj'])+(secs['9.4']['qn']-secs['9.4']['sn']), 9)
# 微专题分域：47=14(9.2)+4(9.3)=18；48=13(9.3)；49=4(9.3)+2(9.4)=6
chk('47讲18=14+4', 14+4, 18); chk('49讲6=4+2', 4+2, 6)
print('\n=== 全部通过 ===' if ok else '\n!!! 存在不平项 !!!')
