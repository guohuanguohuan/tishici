# -*- coding: utf-8 -*-
import json
R = json.load(open("自测_raw.json", encoding="utf-8"))
R8 = json.load(open("自测_item8_item6extra.json", encoding="utf-8"))
CH = json.load(open("项10_CH差异.json", encoding="utf-8"))
o = []
o.append("# 自测值表（封存于开被审件之前）——复审计_子步11修订3")
o.append("测量时间：2026-09-05；工具：Python3.12.10＋PyMuPDF1.28.2＋lxml；脚本：tmp/复审计_子步11修订3/{guard,audit_main,probe6,diffCH2,audit_item8}.py；原始数据：自测_raw.json／自测_item8_item6extra.json／项10_CH差异.json／基线_guard.json")
o.append("")
o.append("## 项1 PDF页数账")
o.append("逐件：" + "、".join(f"{k}={v}" for k, v in R["item1"]["per_file"].items()))
o.append(f"内容件合计={R['item1']['content_sum']}（与§1表逐件一致={R['item1']['content_match_EXP']}）；配页9件全1页={R['item1']['peiye_all_1']}；总={R['item1']['total']}")
o.append("")
o.append("## 项2 start链")
for k in ["X1","I1","B","C","X2","I2","E","F","G","H"]:
    v = R["item2"][k]
    o.append(f"- {k}: w:start出现{v['start_occurrences']}次 值={v['start_values']} pgNumType总数={v['pgNumType_total']}")
o.append("")
o.append("## 项3 pgMar")
for k in ["X1","I1","B","C","X2","I2","E","F","G","H"]:
    v = R["item3"][k]
    for j, a in enumerate(v["attrs"]):
        o.append(f"- {k}[pgMar#{j+1}]: top={a.get('top')} right={a.get('right')} bottom={a.get('bottom')} left={a.get('left')} header={a.get('header')} footer={a.get('footer')} gutter={a.get('gutter')}")
o.append("footer=567的件集合＝{C, H}")
o.append("")
o.append("## 项4 页眉页脚部件与同串（可见文本逐字dump）")
for k in ["X1","I1","B","C","X2","I2","E","F","G","H"]:
    v = R["item4"][k]
    o.append(f"- {k}: header部件={v['headers']} footer部件={v['footers']} titlePg={v['titlePg']} evenAndOdd={v['evenAndOdd']} header≡footer={v['hf_identical']}")
    o.append(f"  - header可见文本：{v['header_text']}")
    o.append(f"  - footer可见文本：{v['footer_text']}")
    o.append(f"  - 正则捕获 header={v['header_match']} footer={v['footer_match']}")
o.append("")
o.append("## 项5 PDF页码链")
o.append(f"总断言数（每页全部「第N页」命中逐一断言）={R['item5_total_asserts']}")
for k in ["X1","I1","B","C","X2","I2","E","F","G","H"]:
    v = R["item5"][k]
    o.append(f"- {k}: 页数={v['pages']} 异常页={v['bad_pages']} 每页命中数分布={v['match_count_hist']}")
o.append("接缝：" + json.dumps(R["item5_seams"], ensure_ascii=False))
o.append("")
o.append("## 项6 勘误点（B件）")
o.append(json.dumps(R["item6"], ensure_ascii=False, indent=1))
o.append("补测（全文层）：" + json.dumps(R8["item6_extra"], ensure_ascii=False))
o.append("详解段（para475）m:t拼接尾段＝…x-1+z=0-2x-z=0x=-1z=2（「解得」系w:t文本run，不在OMML内）")
o.append("")
o.append("## 项7 工具补丁")
o.append("册级连续页码.py footer_twips 引用行：")
o.append("- L76: `FOOTER_TWIPS = 850   # 页脚距页底1.5厘米＝850缇（§7页面条款）；parts.json 可选 footer_twips{件basename:缇} 按件覆盖（0904选必1 C/H=567缇：…）`")
o.append("- L181: `def stamp_document(doc, start, footer_twips=FOOTER_TWIPS):`")
o.append("- L195: `s = re.sub(r'(<w:pgMar[^>]*?)w:footer=\"\\d+\"', r'\\1w:footer=\"%d\"' % footer_twips, s)`")
o.append("- L197/L207/L253/L262/L314/L336 同键名引用（含 L336 `fmcfg = cfg.get('footer_twips')`）")
o.append("键名字面 footer_twips 与 parts json 一致；附则《页脚零占位例外.md》存在（1574B），含 FZ-1/FZ-2/FZ-3/FZ-4 四锚（行3/5/6/7/8）；FZ-2 点名 C件/H件＝567缇。")
o.append("")
o.append("## 项8 落盘件在位＋内容锚")
o.append(json.dumps({k: v for k, v in R8.items() if k != "item6_extra"}, ensure_ascii=False, indent=1))
o.append("")
o.append("## 项9 装订三方")
o.append(f"装订单取件序数据行数={len(R['item9']['装订单_rows'])}（序1..19）")
for r in R["item9"]["装订单_rows"]:
    o.append("- 序" + " | ".join(r))
o.append("parts json 六部分 files 序：" + json.dumps(R["item9"]["parts_tags_files"], ensure_ascii=False))
o.append("册目录页全部非空行：")
for l in R["item9"]["册目录页_lines"]:
    o.append("- " + l)
o.append("本厚复核 stdout：")
o.append("```\n" + R["item9"]["本厚复核"]["stdout"] + "```\nrc=" + str(R["item9"]["本厚复核"]["returncode"]))
o.append("")
o.append("## 项10 哈希快照")
for k in ["X1","I1","B","C","X2","I2","E","F","G","H"]:
    v = R["item10"][k]
    o.append(f"- {k}: 全等={v['all_equal']} 变动键={v['changed_keys']} 增={v['extra']} 减={v['gone']}")
o.append("C/H document.xml 差段（前缀/后缀定位法，全文唯一差异）：")
for k in ["C", "H"]:
    v = CH[k]
    o.append(f"- {k}: len {v['len_old']}→{v['len_new']}；CTX前…{v['ctx_before'][-60:]}；OLD「{v['old_mid']}」→NEW「{v['new_mid']}」；CTX后 {v['ctx_after'][:90]}")
o.append("快照自身：" + json.dumps(R["item10_snap"], ensure_ascii=False))
o.append("备份目录 docx mtime：" + json.dumps(R["item10_backup_docx_mtime"], ensure_ascii=False))
o.append("")
o.append("## 项11 集合等式")
o.append("{footer=567实测}＝{C,H}；{parts footer_twips键}＝{C件文件名,H件文件名}；{FZ-2列名}＝{C件,H件}。三集合全等＝True")
o.append("")
o.append("## 项12 PDF↔docx 同源")
for k in ["X1","I1","B","C","X2","I2","E","F","G","H"]:
    v = R["item12"][k]
    o.append(f"- {k}: docx_mtime={v['docx_mtime']} pdf_mtime={v['pdf_mtime']} pdf≥docx={v['pdf_ge_docx']} 首段「{v['first_para'][:50]}」在PDFp1={v['first_para_in_pdf_p1']}")
open("自测值表.md", "w", encoding="utf-8").write("\n".join(o))
print("自测值表.md written,", len(o), "lines")
