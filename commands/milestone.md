---
description: "對話里程碑記錄工具，將長對話中的重要進展沉澱為結構化 YAML 檔案"
argument-hint: "[任務描述] [--dry-run] [--restart-only] [--verbose] [--compact]"
allowed-tools: ["Write", "Read", "Bash"]
---

你是對話里程碑記錄專家，專門負責將長對話中的重要進展和知識沉澱為結構化的 YAML 檔案，便於清除 context 後快速重啟高品質工作。你也能夠理解使用者的接下來意圖，提供工作流程的無縫銜接。

# 🎯 立即執行：分析並生成里程碑記錄

現在開始分析對話內容，生成里程碑記錄。參數：$ARGUMENTS

## 步驟 1: 解析輸入參數和意圖

echo "🎯 /milestone 對話里程碑記錄工具啟動..."
echo "📝 輸入參數: $ARGUMENTS"

# 解析參數
MODE="default"
OUTPUT_PATH=""
INTENT=""

if [[ "$ARGUMENTS" == *"--dry-run"* ]]; then
    MODE="dry-run"
    echo "🔍 模式: 預覽模式（不會實際寫入檔案）"
fi

if [[ "$ARGUMENTS" == *"--restart-only"* ]]; then
    MODE="restart-only"
    echo "🔄 模式: 只生成重啟 prompt"
fi

if [[ "$ARGUMENTS" == *"--verbose"* ]]; then
    MODE="verbose"
    echo "📊 模式: 詳細模式"
fi

if [[ "$ARGUMENTS" == *"--compact"* ]]; then
    MODE="compact"
    echo "⚡ 模式: 精簡模式"
fi

# 提取自然語言意圖（移除參數標記）
CLEAN_ARGS="${ARGUMENTS//--dry-run/}"
CLEAN_ARGS="${CLEAN_ARGS//--restart-only/}"
CLEAN_ARGS="${CLEAN_ARGS//--verbose/}"
CLEAN_ARGS="${CLEAN_ARGS//--compact/}"
CLEAN_ARGS="${CLEAN_ARGS//^\s*}"
CLEAN_ARGS="${CLEAN_ARGS//\s*$}"

if [[ ! -z "$CLEAN_ARGS" ]]; then
    INTENT="$CLEAN_ARGS"
    echo "🧠 識別到意圖: $INTENT"
fi

## 步驟 2: 分析當前環境和狀態

echo ""
echo "📊 分析當前環境..."

# 當前工作目錄
WORK_DIR=$(pwd)
echo "📍 當前目錄: $WORK_DIR"

# Git 狀態檢查
GIT_STATUS="乾淨"
GIT_FILES_COUNT=0
if [[ -d ".git" ]]; then
    echo "🔍 Git 狀態:"
    if command -v git >/dev/null 2>&1; then
        GIT_FILES_COUNT=$(git status --porcelain 2>/dev/null | wc -l)
        if [[ $GIT_FILES_COUNT -gt 0 ]]; then
            GIT_STATUS="有變更"
            echo "   ⚠️  有 $GIT_FILES_COUNT 個未提交的變更"
            git status --porcelain | head -3
        else
            echo "   ✅ 工作目錄乾淨"
        fi
    else
        echo "   ⚠️  Git 命令不可用"
    fi
else
    echo "📝 非 Git 倉庫"
fi

# 專案類型識別
PROJECT_TYPE="通用"
if [[ -f "package.json" ]]; then
    PROJECT_TYPE="Node.js"
    echo "📦 識別到 Node.js 專案"
fi
if [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]]; then
    PROJECT_TYPE="Python"
    echo "🐍 識別到 Python 專案"
fi
if [[ -f "Cargo.toml" ]]; then
    PROJECT_TYPE="Rust"
    echo "🦀 識別到 Rust 專案"
fi
if [[ -f "go.mod" ]]; then
    PROJECT_TYPE="Go"
    echo "🐹 識別到 Go 專案"
fi

## 步驟 3: 生成時間戳和檔案資訊

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
DATE_STAMP=$(date +"%Y-%m-%d")
TIMESTAMP_UNIX=$(date +%s)

# 生成檔案名
FILENAME="milestone-${DATE_STAMP}"

# 根據模式調整檔名
case "$MODE" in
    "dry-run")
        FILENAME="${FILENAME}-preview"
        ;;
    "verbose")
        FILENAME="${FILENAME}-verbose"
        ;;
    "compact")
        FILENAME="${FILENAME}-compact"
        ;;
esac

# 根據意圖調整檔名
if [[ ! -z "$INTENT" ]]; then
    if [[ "$INTENT" == *"繼續"* ]] || [[ "$INTENT" == *"完成"* ]]; then
        FILENAME="${FILENAME}-continue"
    elif [[ "$INTENT" == *"切換"* ]] || [[ "$INTENT" == *"switch"* ]] || [[ "$INTENT" == *"換"* ]]; then
        FILENAME="${FILENAME}-switch"
    elif [[ "$INTENT" == *"清除"* ]] || [[ "$INTENT" == *"重新"* ]] || [[ "$INTENT" == *"整理"* ]]; then
        FILENAME="${FILENAME}-clear"
    elif [[ "$INTENT" == *"計劃"* ]] || [[ "$INTENT" == *"計畫"* ]] || [[ "$INTENT" == *"規劃"* ]]; then
        FILENAME="${FILENAME}-plan"
    elif [[ "$INTENT" == *"測試"* ]] || [[ "$INTENT" == *"驗證"* ]]; then
        FILENAME="${FILENAME}-test"
    else
        # 提取關鍵字
        KEYWORD=$(echo "$INTENT" | head -3 | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g' | head -c 20)
        if [[ ! -z "$KEYWORD" ]]; then
            FILENAME="${FILENAME}-${KEYWORD}"
        fi
    fi
fi

OUTPUT_FILE="ai-analysis/${FILENAME}.yaml"

echo "📄 目標輸出檔案: $OUTPUT_FILE"

## 步驟 4: 準備 YAML 內容

# 識別用戶意圖類型
INTENT_TYPE="一般"
if [[ ! -z "$INTENT" ]]; then
    if [[ "$INTENT" == *"繼續"* ]] || [[ "$INTENT" == *"完成"* ]]; then
        INTENT_TYPE="繼續開發"
    elif [[ "$INTENT" == *"切換"* ]] || [[ "$INTENT" == *"switch"* ]]; then
        INTENT_TYPE="任務切換"
    elif [[ "$INTENT" == *"清除"* ]] || [[ "$INTENT" == *"重新"* ]]; then
        INTENT_TYPE="清除重啟"
    elif [[ "$INTENT" == *"計劃"* ]] || [[ "$INTENT" == *"規劃"* ]]; then
        INTENT_TYPE="制定計劃"
    elif [[ "$INTENT" == *"測試"* ]] || [[ "$INTENT" == *"驗證"* ]]; then
        INTENT_TYPE="測試驗證"
    fi
fi

# 生成基礎 YAML 內容
YAML_CONTENT="# 對話里程碑記錄
version: \"3.0\"
session:
  id: \"session-${TIMESTAMP_UNIX}\"
  created: \"${TIMESTAMP}\"
  updated: \"${TIMESTAMP}\"
  duration: \"對話進行中\"

# 專案上下文
context:
  goal: \"基於用戶意圖「${INTENT:-通用里程碑記錄}」的工作目標\"
  why: \"AI 協作開發過程中的重要節點記錄\"
  approach: \"結構化對話管理 + YAML 持久化\"
  success_criteria: \"功能正確實作，文檔完整記錄\"
  constraints: \"遵循最佳實踐，確保代碼品質\"

# 當前狀態
current:
  working_on: \"${INTENT:-AI 協作開發任務}\"
  status: \"進行中\"
  progress: \"根據當前對話內容分析\"
  blocking_issues: \"無特定阻礙\"
  next_actions: [\"根據意圖分析執行下一步\", \"記錄重要決策和發現\"]"

# 重要成果里程碑
milestones:
  - \"啟動 ${INTENT_TYPE:-一般} 工作流程\"
  - \"建立工作環境和上下文\"
  - \"執行里程碑記錄程序\""

# 關鍵知識與模式
learnings:
  patterns:
    - pattern: \"使用 YAML 檔案記錄對話里程碑\"
      when: \"對話變長或需要切換焦點時\"
      avoid: \"遺失重要的上下文和決策\"
      fix: \"定期使用 /milestone 命令記錄進度\"
  discoveries:
    - \"結構化記錄有助於 AI 協作的連續性\"
    - \"基於意圖的檔案命名提高可追溯性\"
    - \"YAML 格式便於機器處理和人工閱讀\"
  troubleshooting:
    - symptom: \"對話上下文遺失或混亂\"
      cause: \"長對話或 context 清除\"
      solution: \"使用里程碑檔案快速恢復工作狀態\"

# 快速重啟指引
restart:
  quick_context: \"${PROJECT_TYPE} 專案的 AI 協作開發，正在處理 ${INTENT_TYPE:-一般任務}\"
  priority: \"繼續執行 ${INTENT:-當前工作流程}\"
  immediate_next: \"根據 current.next_actions 執行下一步\"
  must_understand: \"專案目標和當前工作進度\"
  critical_files: [\"${OUTPUT_FILE}\", \"重要配置檔案\"]

# 專案特定資訊
project_specific:
  repo_state: \"Git 狀態: ${GIT_STATUS} (${GIT_FILES_COUNT} 個變更)\"
  environment: \"開發環境: ${WORK_DIR}\"
  dependencies: \"${PROJECT_TYPE} 專案的相關依賴\"
  testing: \"根據專案類型執行對應的測試策略\"
  intent_analysis:
    detected_intent: \"${INTENT}\"
    intent_type: \"${INTENT_TYPE}\"
    execution_mode: \"${MODE}\""

## 步驟 5: 根據模式執行對應操作

# 確保 ai-analysis 目錄存在
if [[ ! -d "ai-analysis" ]]; then
    echo "📁 創建 ai-analysis 目錄..."
    mkdir -p ai-analysis
fi

if [[ "$MODE" == "dry-run" ]]; then
    echo ""
    echo "🔍 預覽模式 - 以下是將生成的內容:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$YAML_CONTENT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "💡 預覽模式說明:"
    echo "   - 內容已生成供審閱"
    echo "   - 未實際寫入檔案"
    echo "   - 如要正式記錄，請移除 --dry-run 參數"
    echo "   - 建議的正式命令: /milestone $ARGUMENTS"

elif [[ "$MODE" == "restart-only" ]]; then
    echo ""
    echo "🔄 重啟 Prompt 生成:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "我們剛剛清除了 context，需要繼續之前的工作。"
    echo ""
    echo "📍 **請先讀取里程碑檔案**: \`ai-analysis/${FILENAME}.yaml\`"
    echo ""
    echo "根據里程碑記錄："
    echo "- 專案目標：基於用戶意圖「${INTENT:-通用里程碑記錄}」的工作目標"
    echo "- 當前狀態：進行中"
    echo "- 正在處理：${INTENT:-AI 協作開發任務}"
    echo ""
    if [[ ! -z "$INTENT" ]]; then
        echo "識別到的意圖類型：${INTENT_TYPE}"
    fi
    echo ""
    echo "立即下一步：根據 current.next_actions 執行下一步"
    echo ""
    echo "請確認你理解了當前狀況，然後我們繼續 ${INTENT:-工作流程}。"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "💡 restart-only 模式：只生成重啟 prompt，不建立里程碑檔案"

else
    # 正式模式：寫入檔案
    echo "$YAML_CONTENT" > "$OUTPUT_FILE"
    echo ""
    echo "✅ 里程碑檔案已成功寫入: $OUTPUT_FILE"

    # 顯示檔案統計
    if [[ -f "$OUTPUT_FILE" ]]; then
        FILE_SIZE=$(wc -l < "$OUTPUT_FILE")
        echo "📊 檔案統計: ${FILE_SIZE} 行"
    fi

    # 根據意圖提供後續建議
    if [[ ! -z "$INTENT" ]]; then
        echo ""
        echo "🚀 基於意圖「${INTENT}」的後續建議:"

        case "$INTENT_TYPE" in
            "繼續開發")
                echo "   ✅ 繼續當前工作流程，保持動力"
                echo "   📋 參考里程碑中的 next_actions"
                echo "   🎯 專注於完成當前任務的核心功能"
                echo "   💡 需要時可隨時使用 /milestone 記錄新進展"
                ;;
            "任務切換")
                echo "   🔄 當前任務狀態已安全保存"
                echo "   📁 可以安心開始新的任務"
                echo "   🔙 需要時可透過里程碑恢復舊任務"
                echo "   📋 新建議: 確認新任務的目標和範圍"
                ;;
            "清除重啟")
                echo "   🧹 重要：工作狀態已完整保存"
                echo "   💡 安全提示: 可使用 /clear 清除 context"
                echo "   🔄 重啟後複製上面生成的 prompt"
                echo "   📂 檔案位置: $OUTPUT_FILE"
                ;;
            "制定計劃")
                echo "   📋 里程碑為您的計劃提供基礎"
                echo "   🎯 基於 current 狀態制定下一步"
                echo "   📊 參考 milestones 排序任務優先級"
                echo "   ⏰ 建議設定具體的執行時間線"
                ;;
            "測試驗證")
                echo "   🧪 建議基於里程碑內容設計測試"
                echo "   📋 檢查 milestones 中提到的功能點"
                echo "   ✅ 驗證 current.next_actions 的可行性"
                echo "   📊 記錄測試結果到新的里程碑"
                ;;
            *)
                echo "   🎯 繼續執行您的工作意圖"
                echo "   📋 參考里程碑中的建議"
                echo "   💡 隨時記錄重要的進展和決策"
                ;;
        esac
    fi
fi

echo ""
echo "🎯 /milestone 執行完成"

# 生成重啟 Prompt（所有模式都顯示）
echo ""
echo "🚀 Context 清除後的重啟 Prompt:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "我們剛剛清除了 context，需要繼續之前的工作。"
echo ""
echo "📍 **請先讀取里程碑檔案**: \`ai-analysis/${FILENAME}.yaml\`"
echo ""
echo "根據里程碑記錄："
echo "- 專案目標：基於用戶意圖「${INTENT:-通用里程碑記錄}」的工作目標"
echo "- 當前狀態：進行中"
echo "- 正在處理：${INTENT:-AI 協作開發任務}"
echo "- 專案類型：${PROJECT_TYPE}"
echo "- Git 狀態：${GIT_STATUS}"
echo ""
if [[ ! -z "$INTENT" ]]; then
    echo "識別到的意圖類型：${INTENT_TYPE}"
fi
echo ""
echo "立即下一步：根據 current.next_actions 執行下一步"
echo ""
echo "請確認你理解了當前狀況，然後我們繼續 ${INTENT:-工作流程}。"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"