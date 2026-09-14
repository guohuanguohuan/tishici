# 探针：复算 opt_tier 对 241 行四选项的估宽，比对门读数 45.4pt
import importlib.util as ilu
spec = ilu.spec_from_file_location('gen', 'C:/提示词/工作区/_tmpM3S4拓展册0914/生成册tex.py')
g = ilu.module_from_spec(spec)
spec.loader.exec_module(g)

raws = ['A．5-√10', 'B．√10-5', 'C．√13-3', 'D．3-√13']
for o in raws:
    t, u = g.convert(o)
    w_body_style = g.ink_em(t, False) * 10.5
    print(repr(t), 'ink_em×10.5=%.1fpt' % w_body_style)
print('slot4_pt=%.2f 阈=%.2f' % ((g.COL_MM - g.HANG_MM) / 4 * g.MM2PT - 0.25 * 10.5,
      (g.COL_MM - g.HANG_MM) / 4 * g.MM2PT - 0.25 * 10.5) if False else
      'slot4_pt=%.2f 阈(slot4*0.85-1)=%.2f' % (
      (g.COL_MM - g.HANG_MM) / 4 * g.MM2PT - 0.25 * 10.5,
      ((g.COL_MM - g.HANG_MM) / 4 * g.MM2PT - 0.25 * 10.5) * 0.85 - 1.0))
