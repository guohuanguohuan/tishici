import three;
settings.render = 0;              // 矢量输出
settings.tex = "pdflatex";
size(7cm, 0);
currentprojection = orthographic(5, 4, 2, up=Z);

// 顶点
triple A = (-1, -1, 0);
triple B = (1, -1, 0);
triple C = (1, 1, 0);
triple D = (-1, 1, 0);
triple P = (0, 0, 1.6);

// 被遮挡棱（相邻面全背向视点，人工核对）→ 虚线
pen hiddenEdge = linewidth(1.0) + dashed;
draw(A--C, hiddenEdge);

// 可见棱 → 实线
pen solidEdge = linewidth(1.1);
draw(A--B ^^ B--C ^^ C--D ^^ D--A ^^ P--A ^^ P--B ^^ P--C ^^ P--D, solidEdge);

// 顶点标注
label("$A$", A, SW);
label("$B$", B, SE);
label("$C$", C, NE);
label("$D$", D, NW);
label("$P$", P, E);
