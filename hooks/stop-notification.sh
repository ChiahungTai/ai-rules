#!/bin/bash
# Claude Code Stop / SessionEnd Hook — 進度提醒（長任務召回）
# 觸發：Stop event（每 turn 結束）+ SessionEnd event（session 結束；Claude 端專屬——ZCode 無此事件）
# 跨 harness：Claude（Stop+SessionEnd）與 ZCode 3.7.7+（僅 Stop，見 hooks/zcode-registration.json）共用本腳本。
# 職責：長任務進行中（sentinel 存在）每 INTERVAL 秒召回用戶檢查。
#   - Stop：sentinel 存在 AND 距上次提醒 ≥ INTERVAL → say 進度提醒 + 更新時間
#   - Stop：usage-ping sentinel（內容 = 首 rung epoch）在 [T, T+PING_STALE) 內有 turn 結束
#     → 一次性 say「配額回來了」+ 自清（配額死 = 無 turn = Stop 不觸發 → 時窗內 Stop ≈ ping 落地，
#     誤報無害）；逾時靜默自清（階梯耗盡未落地）。0 LLM call，召回不靠落地 rung
#   - SessionEnd：清理殘留 sentinel（1.5s timeout，只 rm 不 say）
# 設計理念：誤報無害（召回用戶回來看一眼沒損失），故不判斷任務是否完成 —
#           sentinel 存在就該提醒，完成由 LLM rm sentinel 停止。
# 安全：通知型 hook，exit 0，絕不傳 decision:block（避免 8 次 block 迴圈）。
# 不註冊 SubagentStop（避免 build --max-agents 連播 N 次）。

INTERVAL=600  # 提醒間隔（秒），預設 10 分鐘
SENTINEL="/tmp/.claude-voice-pending"
PING_SENTINEL="/tmp/.usage-ping-pending"
PING_STALE=5400  # usage-ping 召回時窗上界（秒）＝ 90 分鐘（sync 副本：skills/usage-ping、skills/voice-notification——改階梯幾何三處同改）
EPOCH_RE='^[0-9]{1,11}$'  # sentinel 內容契約：trim 後 1-11 位純數字（epoch 10 位 + 餘裕；防 intmax overflow）
T=("主人" "帥哥" "前輩" "道友" "陛下" "道祖")  # 稱謂清單（sync 副本：skills/voice-notification/SKILL.md）

INPUT_JSON=$(cat)
EVENT=$(echo "$INPUT_JSON" | jq -r '.hook_event_name // ""')

# SessionEnd：清理殘留 sentinel（timeout 1.5s，只 rm）
if [[ "$EVENT" == "SessionEnd" ]]; then
    rm -f "$SENTINEL" "$PING_SENTINEL" 2>/dev/null
    exit 0
fi

# Stop：進度提醒（sentinel 存在才作用；不存在則靜默，不影響一般對話）
if [[ -f "$SENTINEL" ]]; then
    MTIME=$(stat -f %m "$SENTINEL" 2>/dev/null)
    NOW=$(date +%s)
    # 首次（MTIME 空）或距上次提醒 ≥ INTERVAL 才提醒
    if [[ -z "$MTIME" ]] || (( NOW - MTIME >= INTERVAL )); then
        say -v Meijia -r 180 "${T[$((RANDOM % ${#T[@]}))]}，做到一個段落了，該檢查囉" &
        touch "$SENTINEL"
    fi
fi

# Stop：usage-ping 召回（一次性；TARGET trim 後不符 EPOCH_RE 視同壞檔直接清；10# 強制十進位防前導零 octal 誤判）
if [[ -f "$PING_SENTINEL" ]]; then
    TARGET=$(tr -d '[:space:]' < "$PING_SENTINEL" 2>/dev/null)
    NOW=$(date +%s)
    if [[ ! "$TARGET" =~ $EPOCH_RE ]]; then
        rm -f "$PING_SENTINEL" 2>/dev/null
    elif (( NOW >= 10#$TARGET + PING_STALE )); then
        rm -f "$PING_SENTINEL" 2>/dev/null
    elif (( NOW >= 10#$TARGET )); then
        say -v Meijia -r 180 "${T[$((RANDOM % ${#T[@]}))]}，配額回來了，該回來工作囉" &
        rm -f "$PING_SENTINEL" 2>/dev/null
    fi
fi
exit 0
