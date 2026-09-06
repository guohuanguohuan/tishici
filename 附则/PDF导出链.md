# PDF 导出链（附则；外移自公共规则§14 L189，2026-09-06 用户拍板外移降预算，原文逐字保留）

> 原语境注记：文中「附则《故障先修纪律》」等引用照旧；公共规则§14 原位留指针。

导出方式（主路径）：**Word 直导（ExportAsFixedFormat，wdExportFormatPDF=17；工具＝工具/逐页巡检管线.py --direct）**——**导出必开书签**（ExportAsFixedFormat 的 CreateBookmarks 参数或 PDFCreator 等效开关；书签层级＝文内标题层级）；Word COM 用自己新建的 Word.Application 实例（不可见）打开**本地副本**后直接导出 PDF；异常重试一次（换新实例），仍败记「该件未过视觉门」fail-closed（其余件继续）；同步 COM 调用不可轮询中断，单件 600s 帽由外层幂等续跑兜底（已出 PDF 件跳过导出只补 PNG）。**备胎链＝打印链**（仅直导故障时启用，且照附则《故障先修纪律》先修后跑，禁带病兜底常态）：Word→PDFCreator 虚拟打印机→spool .PS→本机任一可用 Ghostscript 渲染（GS来源不限、版本须匹配；严禁用 PrintToFile「打印到文件」变体）：⓪**spawn前清GS_LIB**（TinyTeX装的GS_LIB〔10.07.1〕会污染PDFCreator自带GS〔10.05.1〕致gs_init版本错配10051≠10071、引擎死锁.PS零产物；**该污染面同时覆盖 PDFCreator 常驻进程自身**——其被带 GS_LIB 环境启动（如开机自启）即自动转换死锁、spool 只产 .PS 不产 .pdf、每次白等轮询期满，处置＝净环境重启 PDFCreator 进程；全局变量不动）：①打开本地副本；②快照 spool 目录 %LOCALAPPDATA%\Temp\PDFCreator\Spool\；③PrintOut（Background=False）；④轮询等新出现的 .pdf 任务文件（GUID 命名、快照比对、多会话各认各的），取走校验，**用完删除自己的任务文件（.pdf 与同名 .inf），不动他人文件**；⑤全程无需启动 PDFCreator 应用、无需改任何全局配置。端口渲染不压缩；
需留档或过大时用 Ghostscript 压缩（gswin64c -dNOPAUSE -dBATCH -dSAFER -sDEVICE=pdfwrite -sOutputFile=输出.pdf 该任务.pdf），压缩件与原任务件用完都删。
