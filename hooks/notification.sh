#!/bin/bash
# Claude Code Notification Hook — 系統級召回
# 觸發：Notification event（Claude 需要使用者輸入，如權限確認）
# 職責分工：本 hook 只做系統召回固定句池（不含稱謂）；
#           任務完成通知的隨機稱謂歸 voice-notification skill（single-source）。
# 對應 rule：載體選擇見 ai-rules/CLAUDE.md（Hook = 確定性保證）

INPUT_JSON=$(cat)
MESSAGE=$(echo "$INPUT_JSON" | jq -r '.message // "Claude Code 通知"')
TITLE=$(echo "$INPUT_JSON" | jq -r '.title // "Claude Code"')

echo "📢 [Notification Hook] $(date '+%H:%M:%S'): $TITLE - $MESSAGE"

# 預熱語音引擎（減少初始化延遲）
say -v Meijia "" 2>/dev/null &

# 跳過等待輸入的通知（避免煩人）
if [[ "$MESSAGE" == *"Claude is waiting for your input"* ]]; then
    echo "🔇 跳過語音播放 (等待使用者輸入)"
else
    # 固定系統召回句池（不含稱謂 — 稱謂隨機歸 voice-notification skill）
    msgs=(
        '需要你的確認'
        '這裡需要你決定'
        '請看一下'
        '等你回應'
    )
    random_msg="${msgs[RANDOM % ${#msgs[@]}]}"
    echo "🔊 播放語音: $random_msg"
    say -v Meijia -r 180 "$random_msg" &
fi
exit 0
