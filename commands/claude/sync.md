---
description: "檢查 CLAUDE.md 與程式碼的同步性"
usage: "/claude:sync [目錄路徑] [選項]"
argument-hint: "預設檢查當前目錄，可指定目錄或檔案"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
permission-mode: "acceptEdits"
---

# CLAUDE.md Sync - 程式碼同步檢查工具

你是 CLAUDE.md 同步檢查專家，負責驗證 CLAUDE.md 與實際程式碼的一致性和涵蓋性。

## 🎯 核心目標

**CLAUDE.md 必須與實際程式碼保持同步**：
- **程式碼一致性**: 文檔描述的 API/模組/規範是否與實際一致
- **廣泛涵蓋性**: 重要程式碼模組是否被文檔涵蓋
- **實際驗證**: 開啟相關程式碼確認，而非只檢查文檔本身

---

## 🚀 檢查項目

### 角度一：程式碼一致性

| 檢查項目 | 說明 | 驗證方式 |
|---------|------|----------|
| 檔案路徑引用 | 文檔中的路徑是否存在 | `Bash test -f` |
| 類別/函數簽名 | 描述的簽名是否正確 | `Grep` 搜索實際定義 |
| 行為描述 | 描述的行為是否與實際一致 | `Read` 程式碼內容比對 |
| 目錄結構 | 描述的結構是否正確 | `Bash ls` 驗證 |

### 角度二：涵蓋性檢查

| 檢查項目 | 說明 | 驗證方式 |
|---------|------|----------|
| 重要模組遺漏 | 核心模組是否被記錄 | 掃描目錄結構 |
| API 完整性 | 公開 API 是否都有記錄 | `Grep` 搜索 `def`/`class` |
| 規範覆蓋 | 重要規範是否被記錄 | 檢查配置檔案 |

### 角度三：元資訊檢查（--clean 選項）

| 檢查項目 | 說明 |
|---------|------|
| 版本號 | 移除版本資訊 |
| 更新日期 | 移除日期資訊 |
| 歷史變更 | 移除歷史章節 |
| 統計資訊 | 移除行數/字數 |

---

## 🔧 命令介面設計

### 基本用法

```bash
# 1. 檢查當前目錄的 CLAUDE.md
/claude:sync

# 2. 檢查指定檔案
/claude:sync src/core/CLAUDE.md

# 3. 檢查指定目錄（僅該目錄層級）
/claude:sync src/core

# 4. 遞歸檢查所有子目錄的 CLAUDE.md
/claude:sync --recursive
/claude:sync -r

# 5. 遞歸檢查 + 清理元資訊
/claude:sync --recursive --clean
/claude:sync -rc

# 6. 完整處理（檢查 + 清理 + 蒸餾）
/claude:sync --all
/claude:sync -a

# 7. 預覽模式（不實際修改）
/claude:sync --dry-run
/claude:sync --recursive --dry-run
```

### 參數說明

| 參數 | 說明 |
|------|------|
| **無參數** | 檢查當前目錄的 `CLAUDE.md` |
| **檔案路徑** | 檢查指定的 `CLAUDE.md` 檔案 |
| **目錄路徑** | 檢查指定目錄下的 `CLAUDE.md`（僅該層） |
| **--recursive, -r** | 遞歸檢查所有子目錄的 `CLAUDE.md` |
| **--clean** | 檢查後清理元資訊（版本、日期等） |
| **--all, -a** | 完整處理（檢查 + 清理 + 蒸餾） |
| **--dry-run** | 預覽模式，顯示結果但不執行修改 |
| **--verbose** | 顯示詳細檢查過程 |

---

## 📋 執行流程

### 步驟 1: 發現 CLAUDE.md

```bash
# 單檔案模式
Read $TARGET_CLAUDE_MD

# 遞歸模式
Glob "**/CLAUDE.md" $TARGET_DIR
```

### 步驟 2: 掃描程式碼結構

```bash
# 識別重要檔案和目錄（使用括號包裝 -o 條件）
find $TARGET_DIR \( -name "*.py" -o -name "*.pyx" -o -name "*.pxd" \) -type f | head -20
find $TARGET_DIR -type d -maxdepth 2

# 掃描公開 API（分別指定 --include 或使用 find）
grep -r "^def " $TARGET_DIR --include="*.py" --include="*.pyx" --include="*.pxd"
grep -r "^class " $TARGET_DIR --include="*.py" --include="*.pyx" --include="*.pxd"
```

### 步驟 3: 提取文檔引用

```python
# 從 CLAUDE.md 提取引用
def extract_references(content: str) -> dict:
    """提取文檔中的引用"""

    references = {
        "file_paths": [],      # 檔案路徑
        "class_names": [],     # 類別名稱
        "function_names": [],  # 函數名稱
        "modules": [],         # 模組名稱
    }

    # 提取檔案路徑
    import re
    file_patterns = r'`[\w/.-]+/[\w/.-]+\.(py|yaml|toml)`|`[\w/.-]+/`'
    references["file_paths"] = re.findall(file_patterns, content)

    # 提取類別名稱
    class_patterns = r'\*\*[\w]+\*\*|`[\w]+`[\s]*類|class\s+[\w]+'
    references["class_names"] = re.findall(class_patterns, content)

    # 提取函數名稱
    func_patterns = r'`[\w]+\(\)`|function\s+[\w]+|函數\s+[\w]+'
    references["function_names"] = re.findall(func_patterns, content)

    return references
```

### 步驟 4: 驗證一致性

```bash
# 驗證檔案路徑
for path in "${references[file_paths]}"; do
    if [ -f "$path" ]; then
        echo "✅ $path"
    else
        echo "❌ $path 不存在"
    fi
done

# 驗證類別/函數（分別指定 --include）
for name in "${references[class_names]}"; do
    if grep -r "class $name" $TARGET_DIR --include="*.py" --include="*.pyx" --include="*.pxd"; then
        echo "✅ $name"
    else
        echo "⚠️  $name 未找到"
    fi
done
```

### 步驟 5: 命令涵蓋性檢查

```bash
# 重要！掃描所有命令檔案，檢查是否被記錄
ALL_COMMAND_FILES=$(find $TARGET_DIR -name "*.md" -type f | grep -v "CLAUDE.md")

for cmd_file in $ALL_COMMAND_FILES; do
    # 推導命令名稱
    # e.g., "worktree/status.md" -> "/worktree:status"
    # e.g., "claude/clean.md" -> "/claude:clean"
    cmd_name=$(echo "$cmd_file" | sed "s|$TARGET_DIR||" | sed 's|\.md$||' | sed 's|^/|/|')

    # 檢查是否在 CLAUDE.md 中
    if grep -q "$cmd_name" "$CLAUDE_MD"; then
        echo "✅ $cmd_name 已記錄"
    else
        echo "❌ $cmd_name 未記錄"
    fi
done
```

### 步驟 6: 程式碼涵蓋性檢查

```bash
# 如果目錄中有程式碼檔案，檢查是否被記錄
CODE_FILES=$(find $TARGET_DIR \( -name "*.py" -o -name "*.pyx" -o -name "*.pxd" \) -type f 2>/dev/null)
if [ -n "$CODE_FILES" ]; then
    echo ""
    echo "### 程式碼檔案涵蓋性檢查"
    for code_file in $CODE_FILES; do
        filename=$(basename "$code_file")
        if grep -q "$filename" "$CLAUDE_MD"; then
            echo "✅ $filename 已記錄"
        else
            echo "⚠️  $filename 未記錄"
        fi
    done
fi
```

### 步驟 7: 清理元資訊（--clean 選項）

```bash
# 呼叫 /claude:clean 功能
# 移除版本號、日期、統計等元資訊
```

### 步驟 8: 蒸餾（--all 選項）

```bash
# 呼叫 /claude:distill 功能
# 蒸餾精簡 CLAUDE.md
```

---

## 📊 輸出格式

### 單檔案檢查輸出

```
## CLAUDE.md 同步檢查報告

檔案: /path/to/CLAUDE.md（範例）

### 📋 程式碼一致性檢查

#### 檔案路徑引用
- ✅ src/core/engine.py
- ✅ src/core/config.py
- ❌ src/legacy/old_module.py（檔案不存在）

#### 類別/函數簽名
- ✅ DataEngine
- ✅ process_data()
- ⚠️  validate_input()（簽名已變更：現在需要 config 參數）

#### 行為描述
- ⚠️  "DataEngine 會自動重連" → 實際程式碼沒有自動重連邏輯

### 📂 涵蓋性檢查

#### 重要模組檢查
掃描目錄: /path/to/src/
- ✅ src/core/CLAUDE.md
- ⚠️  src/api/（未記錄在主文檔）
- ⚠️  src/utils/（未記錄在主文檔）

#### 公開 API 檢查
發現 N 個公開函數，文檔記錄 M 個
- ⚠️  遺漏: helper_function(), validate_config(), get_status()

### 🧹 元資訊檢查
- ❌ 發現版本號: vX.Y
- ❌ 發現更新日期: YYYY-MM-DD
- 💡 建議執行 `/claude:sync --clean` 清理

### 📊 總結
- 一致性: X%（需要改進）
- 涵蓋性: Y%（需要改進）
- 元資訊: 需要清理

建議優先處理：
1. 移除不存在的檔案引用
2. 更新變更的 API 簽名
3. 補充遺漏的模組說明
4. 清理元資訊
```

### 遞歸模式輸出

```
## 遞歸同步檢查報告

目錄: /path/to/project
發現 CLAUDE.md: 5 個

### 🔴 Critical（專案根目錄）
**檔案**: CLAUDE.md
- 一致性: ✅ 90%
- 涵蓋性: ⚠️ 75%
- 元資訊: ❌ 需要清理

### 🟠 High（主要模組）
**檔案**: src/CLAUDE.md
- 一致性: ✅ 95%
- 涵蓋性: ✅ 90%
- 元資訊: ✅ 乾淨

**檔案**: src/core/CLAUDE.md
- 一致性: ⚠️ 80%（2 個 API 簽名變更）
- 涵蓋性: ✅ 85%
- 元資訊: ❌ 有版本號

### 🟡 Medium（子模組）
**檔案**: src/core/utils/CLAUDE.md
- 一致性: ✅ 100%
- 涵蓋性: ⚠️ 70%（遺漏 helper 函數）
- 元資訊: ✅ 乾淨

### 🟢 Low（測試）
**檔案**: tests/CLAUDE.md
- 一致性: ✅ 95%
- 涵蓋性: ✅ 90%
- 元資訊: ✅ 乾淨

### 📊 整體統計
- 檔案數量: 5 個
- 平均一致性: 90%
- 平均涵蓋性: 82%
- 需要清理: 2 個
- 需要蒸餾: 1 個

建議執行: `/claude:sync --recursive --clean`
```

### 執行清理後輸出

```
## CLAUDE.md 同步檢查 + 清理完成

檔案: /path/to/CLAUDE.md（範例）

### ✅ 檢查完成
- 一致性: X%（已報告問題）
- 涵蓋性: Y%（已報告遺漏）

### 🧹 清理完成
- 移除版本號: vX.Y
- 移除更新日期: YYYY-MM-DD
- 移除歷史章節: 無
- 移除統計資訊: 無

### 📄 處理結果
- 原始行數: N 行
- 清理後: M 行 (-Z%)
- 備份檔案: CLAUDE.md.backup
```

### --all 完整處理輸出

```
## CLAUDE.md 完整處理（檢查 + 清理 + 蒸餾）

檔案: /path/to/CLAUDE.md（範例）

### 步驟 1: 同步檢查
- 一致性問題: N 項
- 涵蓋性遺漏: M 項
- 元資訊問題: K 項

### 步驟 2: 清理元資訊
- 移除版本號、日期
- 移除統計資訊
- X 行 → Y 行

### 步驟 3: 蒸餾精簡
- 識別精華: N 個核心原則
- 移除冗餘: M 個實作細節
- Y 行 → Z 行

### ✅ 最終結果
- 原始: X 行
- 處理後: Z 行 (-P%)
- 備份: CLAUDE.md.backup (原始)
- 備份: CLAUDE.md.pre-distill.md (清理後)
```

---

## 🎯 執行約束

### 同步檢查專屬約束
- **實際驗證**: 必須開啟程式碼檔案確認，不猜測
- **引用來源**: 報告問題時標註具體位置和證據（檔案:行號）
- **涵蓋性掃描**: 檢查命令檔案和程式碼檔案是否被記錄
- **報告先行**: 先報告發現，再詢問是否執行清理或蒸餾

### 遞歸處理約束
- **分類處理**: 按重要性分類（Critical/High/Medium/Low），優先報告關鍵問題
- **進度報告**: 每處理一個檔案報告進度
- **錯誤處理**: 單一檔案失敗不影響其他檔案
- **統計彙總**: 提供整體統計和建議

### 整合選項約束
- **--clean**: 檢查後執行清理，建立備份
- **--all**: 順序執行（檢查 → 清理 → 蒸餾），每步驟建立備份
- **--dry-run**: 預覽所有操作，不實際修改

---

## 💡 使用建議

### 定期檢查
1. **每週執行**: `/claude:sync --recursive` 檢查同步性
2. **每月清理**: `/claude:sync --recursive --clean` 清理元資訊
3. **每季蒸餾**: `/claude:sync --all` 完整處理

### 觸發時機
- 新增多個程式碼檔案後
- 重構 API 介面後
- 發現文檔描述與實際不符時
- 版本發布前

### 最佳實踐
1. **先預覽**: 使用 `--dry-run` 先看結果
2. **分批處理**: 大型專案可分目錄處理
3. **版本控制**: 執行前先 commit，方便回滾
4. **記錄問題**: 將發現的同步問題記錄到待辦清單

---

## 🎯 品質檢查清單
- [ ] 發現了所有 CLAUDE.md 檔案（遞歸模式）
- [ ] 掃描了程式碼結構和重要檔案（Python/Cython）
- [ ] 提取了文檔中的所有引用（檔案路徑、類別、函數）
- [ ] 驗證了檔案路徑存在性
- [ ] 驗證了類別/函數簽名正確性（實際讀取程式碼確認）
- [ ] 檢查了命令涵蓋性（.md 檔案是否被記錄）
- [ ] 檢查了程式碼涵蓋性（.py/.pyx/.pxd 檔案是否被記錄）
- [ ] 檢查了元資訊（--clean 選項）
- [ ] 執行了清理（--clean 或 --all）
- [ ] 執行了蒸餾（--all）
- [ ] 提供了完整的檢查報告（含具體位置和證據）
- [ ] 建立了備份檔案

---

> 💡 **同步哲學**: CLAUDE.md 是活文檔，必須與程式碼同步演進。定期檢查同步性，確保 AI 協作時獲得準確的資訊，避免過時文檔導致誤導。

> 🔍 **涵蓋性價值**: 完整的文檔涵蓋讓 AI 更全面理解專案，減少「不知道有這個功能」的情況，提升開發效率和準確性。

> 🧹 **清理價值**: 移除對 AI 無意義的元資訊，減少 token 消耗，讓 AI 專注於核心規則和約束。

> ⚡ **整合價值**: 一次命令完成檢查、清理、蒸餾，大幅提升文檔維護效率，特別適合定期維護場景。
