#!/bin/bash
# Claude Code Stop / SessionEnd Hook — 進度提醒（長任務召回）
# 觸發：Stop event（每 turn 結束）+ SessionEnd event（session 結束）
# 職責：長任務進行中（sentinel 存在）每 INTERVAL 秒召回用戶檢查。
#   - Stop：sentinel 存在 AND 距上次提醒 ≥ INTERVAL → say 進度提醒 + 更新時間
#   - SessionEnd：清理殘留 sentinel（1.5s timeout，只 rm 不 say）
# 設計理念：誤報無害（召回用戶回來看一眼沒損失），故不判斷任務是否完成 —
#           sentinel 存在就該提醒，完成由 LLM rm sentinel 停止。
# 安全：通知型 hook，exit 0，絕不傳 decision:block（避免 8 次 block 迴圈）。
# 不註冊 SubagentStop（避免 build --max-agents 連播 N 次）。

INTERVAL=600  # 提醒間隔（秒），預設 10 分鐘
SENTINEL="/tmp/.claude-voice-pending"

INPUT_JSON=$(cat)
EVENT=$(echo "$INPUT_JSON" | jq -r '.hook_event_name // ""')

# SessionEnd：清理殘留 sentinel（timeout 1.5s，只 rm）
if [[ "$EVENT" == "SessionEnd" ]]; then
    rm -f "$SENTINEL" 2>/dev/null
    exit 0
fi

# Stop：進度提醒（sentinel 存在才作用；不存在則靜默，不影響一般對話）
if [[ -f "$SENTINEL" ]]; then
    MTIME=$(stat -f %m "$SENTINEL" 2>/dev/null)
    NOW=$(date +%s)
    # 首次（MTIME 空）或距上次提醒 ≥ INTERVAL 才提醒
    if [[ -z "$MTIME" ]] || (( NOW - MTIME >= INTERVAL )); then
        T=("主人" "帥哥" "前輩" "道友" "陛下" "道祖")
        say -v Meijia -r 180 "${T[$((RANDOM % ${#T[@]}))]}，做到一個段落了，該檢查囉" &
        touch "$SENTINEL"
    fi
fi
exit 0
