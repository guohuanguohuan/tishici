from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from copy import deepcopy
import subprocess, tempfile, shutil, os

root_dir = Path(r'C:\sync\syncall\教育行业\k12相关\高中阶段\高中数学\组卷网\高中数学解题大招（二级结论）荟萃')
target = root_dir / r'04_原始资料\模块1集合简易逻辑与不等式\模块1大招5三角换元.docx'
backup = target.with_name(target.stem + '.合规复查前备份.docx')
if not backup.exists():
    shutil.copy2(target, backup)

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
NS={'w':W,'m':M}

repls = {
18: r'解析：由根式有意义可知 $x\in[-1,1]$。令 $x=\cos\theta,\theta\in[0,\pi]$，则 $\sin\theta\ge 0$，从而 $\sqrt{1-x^2}=\sin\theta$。取 $\varphi\in(0,\frac{\pi}{2})$，使 $\sin\varphi=\frac{3}{\sqrt{10}},\cos\varphi=\frac{1}{\sqrt{10}}$，于是 $y=3\cos\theta+\sin\theta=\sqrt{10}\sin(\theta+\varphi)$。',
20: r'因为 $\theta+\varphi\in[\varphi,\pi+\varphi]$，且 $\frac{\pi}{2}\in[\varphi,\pi+\varphi]$，所以当 $\theta=\frac{\pi}{2}-\varphi$ 时，$y$ 取得最大值 $\sqrt{10}$；当 $\theta=\pi$ 时，$y$ 取得最小值 $-3$。',
23: r'本题令 $x=\cos\theta,\theta\in[0,\pi]$，是因为 $\cos\theta$ 在该区间可取遍 $[-1,1]$，且 $\sin\theta\ge 0$，故 $\sqrt{1-x^2}=\sqrt{1-\cos^2\theta}=|\sin\theta|=\sin\theta$。',
65: r'先证明二维柯西不等式。设 $\vec u=(x_1,x_2),\vec v=(y_1,y_2)$。若其中一个为零向量，则不等式两边均为 $0$；若二者均为非零向量，设其夹角为 $\beta$。',
211: r'法一（三角换元）令 $x=r\cos\theta,y=r\sin\theta$，其中 $r=\sqrt{x^2+y^2}>0,\theta\in[0,2\pi)$，则 $x^2+y^2=r^2$。',
215: r'因为 $\cos2\theta+\sin2\theta\le\sqrt2$，且由约束可知 $\cos2\theta+\sin2\theta>0$，所以 $r^2=\frac{7}{\cos2\theta+\sin2\theta}\ge\frac{7}{\sqrt2}=\frac{7\sqrt2}{2}$。当 $2\theta=\frac{\pi}{4}$ 时等号成立，故端点可以取得。',
218: r'**第一步  将约束写成两个量的和，利用二维柯西不等式估计（原解法修正）**',
219: r'令 $A=x^2-y^2,B=2xy$，则 $A^2+B^2=(x^2+y^2)^2$，且由题意 $A+B=7$。由二维柯西不等式，$(A+B)^2\le 2(A^2+B^2)$，所以 $49\le 2(x^2+y^2)^2$。',
220: r'由于 $x^2+y^2>0$，所以 $x^2+y^2\ge\frac{7\sqrt2}{2}$。当 $A=B>0$ 时取等号；例如取 $x=(1+\sqrt2)y$，再令 $y^2=\frac{7}{4(1+\sqrt2)}$，即可同时满足原约束和取等条件。',
221: r'因此 $x^2+y^2$ 的最小值为 $\frac{7\sqrt2}{2}$。',
230: r'$\Longleftrightarrow (u-1)^2+(v-1)^2=4$。',
232: r'由于 $u\ge0,v\ge0$，圆 $(u-1)^2+(v-1)^2=4$ 的可行圆弧可参数化为 $u=1+2\cos\theta,v=1+2\sin\theta$，其中 $\theta\in[-\frac{\pi}{6},\frac{2\pi}{3}]$。于是 $u+v=2+2\cos\theta+2\sin\theta=2+2\sqrt2\sin(\theta+\frac{\pi}{4})$。该参数区间恰好覆盖全部可行点，不会遗漏端点。',
255: r'令 $2x+y-2=\sin\theta,\sqrt3y=\cos\theta$，其中 $\theta\in[0,2\pi)$，则 $2x+y-2=\sin\theta,y=\frac{\sqrt3}{3}\cos\theta$。',
267: r'【详解】设 $P(\cos\theta,\sin\theta)$，其中 $\theta\in[0,2\pi)$。',
280: r'【分析】利用数量积定义可得 $\vec a,\vec b$ 的夹角为 $\frac{2\pi}{3}$。不妨设 $\vec a=(1,0),\vec b=(-\frac12,\frac{\sqrt3}{2}),\vec c=(\cos\alpha,\sin\alpha)$，其中 $\alpha\in[0,2\pi)$；解出 $x,y$ 后，利用辅助角公式求 $x-y$ 的最小值。',
284: r'不妨设 $\vec a=(1,0),\vec b=(-\frac12,\frac{\sqrt3}{2}),\vec c=(\cos\alpha,\sin\alpha)$，其中 $\alpha\in[0,2\pi)$。',
289: r'由 $\alpha\in[0,2\pi)$，得 $\alpha+\frac{\pi}{6}\in[\frac{\pi}{6},\frac{13\pi}{6})$。',
299: r'【详解】由已知可设 $P(\cos\theta,\sin\theta)$，其中 $\theta\in[0,2\pi)$，则 $\overrightarrow{OP}=(\cos\theta,\sin\theta)$。',
304: r'所以 $2\lambda+\mu=2\sin\theta+\cos\theta\le\sqrt{2^2+1^2}=\sqrt5$。',
305: r'当 $\sin\theta=\frac{2}{\sqrt5},\cos\theta=\frac{1}{\sqrt5}$ 时等号成立，因此 $2\lambda+\mu$ 的最大值为 $\sqrt5$。',
344: r'【详解】$x^2-xy+y^2=1\Longleftrightarrow (x-\frac y2)^2+(\frac{\sqrt3}{2}y)^2=1$。故令 $x-\frac y2=\cos\theta,\frac{\sqrt3}{2}y=\sin\theta$，其中 $\theta\in[0,2\pi)$。',
355: r'【解析】设 $P(a\cos\theta,b\sin\theta)$，其中 $\theta\in[0,2\pi)$ 且 $\theta\ne0,\pi$（点 $P$ 异于左右顶点），$A(-a,0),B(a,0)$，计算可得 $k_1k_2=e^2-1$。',
356: r'【详解】设 $P(a\cos\theta,b\sin\theta)$，其中 $\theta\in[0,2\pi)$ 且 $\theta\ne0,\pi$，$A(-a,0),B(a,0)$。',
370: r'整理得 $(\frac a2+b)^2+\frac34a^2=\frac12$。令 $\frac a2+b=\frac{\sqrt2}{2}\cos\theta,\frac{\sqrt3}{2}a=\frac{\sqrt2}{2}\sin\theta$，其中 $\theta\in[0,2\pi)$，则 $a=\frac{\sqrt6}{3}\sin\theta\le\frac{\sqrt6}{3}$；当 $\theta=\frac\pi2$ 时等号成立，故 $a$ 的最大值为 $\frac{\sqrt6}{3}$。',
373: r'令 $a=x+y,b=x-y$，代入得 $6x^2+2y^2=1$。由椭圆参数方程，可令 $x=\frac{\sqrt6}{6}\cos\theta,y=\frac{\sqrt2}{2}\sin\theta$，其中 $\theta\in[0,2\pi)$。',
377: r'当 $|a|<1$ 时，令 $b=\sqrt{1-a^2}\sin\theta,c=\sqrt{1-a^2}\cos\theta$，其中 $\theta\in[0,2\pi)$。代入 $a+b+c=0$，得 $\sqrt2\sin(\theta+\frac\pi4)=-\frac{a}{\sqrt{1-a^2}}$。',
378: r'原等式关于 $\theta$ 有解的充要条件为 $\left|\frac{a}{\sqrt{1-a^2}}\right|\le\sqrt2$，解得 $a^2\le\frac23$。另外，$a=\pm1$ 时由 $b=c=0$ 与 $a+b+c=0$ 矛盾，故无需补入。',
379: r'因此 $-\frac{\sqrt6}{3}\le a\le\frac{\sqrt6}{3}$，且两个端点均可由取等条件取得，所以 $a$ 的最大值为 $\frac{\sqrt6}{3}$。',
382: r'令 $\frac{\sqrt{15}}2b=\sqrt c\cos\alpha,2a-\frac b2=\sqrt c\sin\alpha$，其中 $\alpha\in[0,2\pi)$，则 $b=\frac{2\sqrt{15}}{15}\sqrt c\cos\alpha,2a=\frac{\sqrt{15}}{15}\sqrt c\cos\alpha+\sqrt c\sin\alpha$。',
387: r'$b=\frac{\sqrt{10}}{10}\sqrt c,a=\frac{3\sqrt{10}}{20}\sqrt c$，从而 $\frac3a-\frac4b+\frac5c=\frac5c-\frac{2\sqrt{10}}{\sqrt c}=(\frac{\sqrt5}{\sqrt c}-\sqrt2)^2-2\ge-2$。当 $c=\frac52$ 时等号成立。',
424: r'设 $u=\frac{\sqrt2+\sin\theta}{\cos\theta}$，其中 $|\theta|<\frac\pi2$。由于 $\cos\theta>0$ 且 $\sqrt2+\sin\theta>0$，所以 $u>0$，并且 $u\cos\theta-\sin\theta=\sqrt2$。',
425: r'对固定的 $u>0$，令 $g_u(\theta)=u\cos\theta-\sin\theta$。在 $(-\frac\pi2,\frac\pi2)$ 内，$g_u$ 的最大值为 $\sqrt{u^2+1}$，且当 $\theta\to-\frac\pi2^+$ 时 $g_u(\theta)\to1<\sqrt2$。',
426: r'因此，方程 $g_u(\theta)=\sqrt2$ 在该区间有解的充要条件为 $\sqrt{u^2+1}\ge\sqrt2$，即 $u\ge1$。这同时说明所有 $u\in[1,+\infty)$ 均可取得。',
427: r'由 $y=\sqrt2u+1$，得函数的值域为 $[\sqrt2+1,+\infty)$；当 $u=1,\theta=-\frac\pi4$ 时取得左端点。',
430: r'设 $u=\frac{\sqrt2+\sin\theta}{\cos\theta}$，其中 $|\theta|<\frac\pi2$。令 $P(\cos\theta,\sin\theta)$，则 $P$ 在右半圆 $x^2+y^2=1\ (x>0)$ 上，且 $u$ 是点 $A(0,-\sqrt2)$ 与点 $P$ 连线的斜率。',
432: r'设过点 $A$ 的直线为 $y+\sqrt2=kx$。由于 $x_P=\cos\theta>0$ 且 $y_P+\sqrt2=\sin\theta+\sqrt2>0$，故对应斜率 $k>0$。',
435: r'该直线与单位圆有交点的充要条件是圆心到直线的距离 $d=\frac{\sqrt2}{\sqrt{k^2+1}}\le1$，即 $k\ge1$；当 $k=1$ 时直线与右半圆相切。',
436: r'因此右半圆上对应斜率的取值范围为 $[1,+\infty)$，即 $u\ge1$，从而 $y=\sqrt2u+1\ge\sqrt2+1$。',
438: r'（4）令 $r=\sqrt{x^2+y^2}$，则 $r\in[1,\sqrt2]$。再令 $x=r\cos\theta,y=r\sin\theta$，其中 $\theta\in[0,2\pi)$。',
439: r'**第一步  令 $x=r\cos\theta,y=r\sin\theta$，明确 $r\in[1,\sqrt2],\theta\in[0,2\pi)$**',
440: r'于是 $z=x^2-xy+y^2=r^2-r^2\sin\theta\cos\theta=r^2(1-\frac12\sin2\theta)$。'
}

# Generate a reference paragraph via pandoc for each replacement.
def make_p(md_text: str):
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); md=td/'x.md'; out=td/'x.docx'
        md.write_text(md_text+'\n',encoding='utf-8')
        subprocess.run(['pandoc',str(md),'-f','markdown+tex_math_dollars','-t','docx','-o',str(out)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        with ZipFile(out) as z:
            rr=etree.fromstring(z.read('word/document.xml'))
        pp=rr.xpath('.//w:body/w:p',namespaces=NS)
        for p in pp:
            text=''.join(p.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS)).strip()
            if text:
                return deepcopy(p)
        raise RuntimeError('no paragraph')

with ZipFile(target,'r') as zin:
    files={n:zin.read(n) for n in zin.namelist()}
root=etree.fromstring(files['word/document.xml'])
ps=root.xpath('.//w:body/w:p',namespaces=NS)
for idx,md in repls.items():
    old=ps[idx]
    new=make_p(md)
    old_ppr=old.find(f'{{{W}}}pPr')
    new_ppr=new.find(f'{{{W}}}pPr')
    if new_ppr is not None: new.remove(new_ppr)
    if old_ppr is not None: new.insert(0,deepcopy(old_ppr))
    old.getparent().replace(old,new)
    ps[idx]=new

files['word/document.xml']=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone='yes')
tmp=target.with_suffix('.tmp.docx')
with ZipFile(tmp,'w',ZIP_DEFLATED) as zout:
    for n,data in files.items(): zout.writestr(n,data)
os.replace(tmp,target)
print(f'updated {len(repls)} paragraphs')
print('backup:',backup)
