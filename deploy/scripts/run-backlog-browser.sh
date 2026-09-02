#!/bin/bash
# Backlog.md web board（ai-rules）—— :6422 常駐（mosaic :6420 配對；report-server :6421 /ai-rules route 供卡 references 點擊直達）
# --no-open：launchd 環境不自動開瀏覽器；--port 6422：明示釘住（佔用即 exit 由 launchd 節流重試）
# cd：backlog CLI 從 cwd 向上找 backlog/ 專案——launchd 預設 cwd 非 repo 會 "No Backlog.md project found" exit 1
cd /Users/ctai/Github/ai-rules || exit 1
exec /Users/ctai/.npm-global/bin/backlog browser --no-open --port 6422
