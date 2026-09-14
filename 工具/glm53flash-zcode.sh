#!/usr/bin/env bash
# GLM-5.3-Flash 专用子智能体入口:经 ZCode 内嵌 CLI 无头执行
# 用法: bash 工具/glm53flash-zcode.sh "任务提示词" [工作目录]
# 配置: ~/.zcode/cli/config.json (provider zai / GLM-5.3-Flash)
set -euo pipefail
PROMPT="${1:?用法: glm53flash-zcode.sh \"任务提示词\" [工作目录]}"
CWD="${2:-C:\\提示词}"
export ELECTRON_RUN_AS_NODE=1
exec "/c/Users/28120/AppData/Local/Programs/ZCode/ZCode.exe" \
  "C:\Users\28120\AppData\Local\Programs\ZCode\resources\glm\zcode.cjs" \
  --cwd "$CWD" --prompt "$PROMPT" --no-color
