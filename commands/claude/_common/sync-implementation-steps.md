# Sync 實作步驟詳細定義

> **載入時機**: 僅在 `/claude:sync` 執行時按需讀取。本檔案定義步驟 0.5-10.5 的詳細實作邏輯。

---

## 步驟 0.5: Snapshot 載入

> **觸發條件**：專案根目錄存在 `.project-snapshot.json` 時執行。無 snapshot 時跳過，所有 snapshot 相關步驟降級為獨立模式。

從 `.project-snapshot.json` 載入預計算的知識快照，供後續步驟使用：

```
1. 偵測專案根目錄是否有 .project-snapshot.json
2. 如果存在：
   a. 讀取 JSON
   b. 驗證 schema_version >= 2（否則視為舊格式，只取 modules/edges）
   c. Staleness 檢查：如果 scan_timestamp 超過 24 小時，
      記錄警告 "[WARN] snapshot is stale, recommend /scan-project first"，
      不阻塞後續步驟（資料可能過時但仍有參考價值）
   d. 提取以下資料供後續步驟使用：
      - modules + edges → 步驟 1.5 依賴鏈擴展（精確取代 naive grep）
      - claude_md_registry → 步驟 4 驗證一致性（預計算的模組邊界）
      - uc_registry → 步驟 10.5 交叉驗證（UC ID 集合）
      - cross_validation → 步驟 10.5（預計算的 X6/X7/X-path 問題）
3. 如果不存在：記錄 "running without snapshot"，後續步驟用傳統方式
```

**Snapshot 資料消費對照**：

| 步驟 | 消費的 snapshot 資料 | 取代的傳統方式 |
|------|---------------------|---------------|
| 1.5 依賴鏈擴展 | `edges[]` | naive grep import chain |
| 4 驗證一致性 | `claude_md_registry[]` | 逐一 Read CLAUDE.md |
| 10.5 交叉驗證 | `cross_validation[]` + `uc_registry[]` | 無（新增能力） |

---

## 步驟 1: 遞歸發現 CLAUDE.md 檔案

遞歸發現邏輯: [recursive-discovery.md](./recursive-discovery.md)

---

## 步驟 1.5: 依賴鏈擴展

> **觸發條件**：目標目錄中有 `git diff` 變更的 `.py` 檔案時執行。或使用 `--changed-since` 參數。

從變更的程式碼出發，追蹤 import 鏈，將消費端目錄的 CLAUDE.md 加入檢查清單：

```
1. git diff --name-only 提取變更的 .py 檔案
   - 無 --changed-since → git diff HEAD
   - 有 --changed-since → git log --since="$SINCE" --name-only --pretty=format:
2. 對每個變更檔案，搜尋消費端：
   - 有 snapshot → 直接查 edges[]（精確、快速）
   - 無 snapshot → Grep 搜尋整個專案中 import 該模組的檔案
3. 從消費端檔案路徑推導其所屬目錄
4. 檢查消費端目錄是否有 CLAUDE.md → 有的話加入檢查清單
5. 去重，合併到步驟 1 發現的 CLAUDE.md 清單
```

**--changed-since 增量模式**：

當指定 `--changed-since` 時，步驟 1 只掃描 git 變更涉及的目錄，而非全部目錄。這大幅縮小檢查範圍，適合 daily-maintain 的 Phase 1 使用。

```
增量模式流程：
1. git log --since="$SINCE" --name-only --pretty=format: → 取得變更檔案清單
2. 過濾 .py 和 .md 檔案
3. 映射到所屬模組目錄
4. 只對這些目錄執行 sync 檢查
5. 步驟 1.5 的依賴鏈擴展仍然執行（確保消費端也被檢查）
```

---

## 步驟 1.6: Sub-doc 擴展

> **觸發條件**：CLAUDE.md 中引用了同目錄或相鄰目錄的 `.md` 子文件時執行。

從 CLAUDE.md 的 markdown link 引用出發，發現子文件並分類，將「說明文檔」加入檢查清單：

```
1. 從 CLAUDE.md 提取所有 markdown link 引用的 .md 檔案
   - 格式: [描述](path/to/doc.md) 或 [描述](doc.md)
   - 排除外部 URL（http/https）
   - 排除 @ transclusion（已強制載入，不需額外檢查）
2. 驗證引用的 .md 檔案是否存在
3. 分類為「說明文檔」或「設計文檔」：
   - 說明文檔：描述 API、資料結構、流程、call stack → 加入檢查清單
   - 設計文檔：描述概念、提案、未來計畫 → 跳過
4. 合併到檢查清單，標記為 sub-doc（優先級同父 CLAUDE.md）
```

**Sub-doc 檢查範圍**：對說明文檔執行角度二（程式碼一致性）和角度六（內部品質），不重複涵蓋性檢查（由父 CLAUDE.md 統一負責）。

---

## 步驟 2: 掃描程式碼結構

```bash
# 識別重要檔案和目錄
fd -e py -e pyx -e pxd . $TARGET_DIR | head -20
fd -t d . $TARGET_DIR --max-depth 2

# 掃描公開 API
rg "^def " -t py $TARGET_DIR
rg "^class " -t py $TARGET_DIR
```

---

## 步驟 3: 提取文檔引用

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

---

## 步驟 4: 驗證一致性

```bash
# 驗證檔案路徑
for path in "${references[file_paths]}"; do
    if [ -f "$path" ]; then
        echo "✅ $path"
    else
        echo "❌ $path 不存在"
    fi
done

# 驗證類別/函數
for name in "${references[class_names]}"; do
    if rg -q "class $name" -t py $TARGET_DIR; then
        echo "✅ $name"
    else
        echo "⚠️  $name 未找到"
    fi
done
```

---

## 步驟 5: 命令涵蓋性檢查

```bash
# 重要！掃描所有命令檔案，檢查是否被記錄
ALL_COMMAND_FILES=$(fd -e md . $TARGET_DIR --exclude CLAUDE.md)

for cmd_file in $ALL_COMMAND_FILES; do
    # 推導命令名稱
    # e.g., "worktree/status.md" -> "/worktree:status"
    # e.g., "claude/clean.md" -> "/claude:clean"
    cmd_name=$(echo "$cmd_file" | sed "s|$TARGET_DIR||" | sed 's|\.md$||' | sed 's|^/|/|')

    # 檢查是否在 CLAUDE.md 中
    if rg -q "$cmd_name" "$CLAUDE_MD"; then
        echo "✅ $cmd_name 已記錄"
    else
        echo "❌ $cmd_name 未記錄"
    fi
done
```

---

## 步驟 6: 程式碼涵蓋性檢查

```bash
# 如果目錄中有程式碼檔案，檢查是否被記錄
CODE_FILES=$(fd -e py -e pyx -e pxd . $TARGET_DIR)
if [ -n "$CODE_FILES" ]; then
    echo ""
    echo "### 程式碼檔案涵蓋性檢查"
    for code_file in $CODE_FILES; do
        filename=$(basename "$code_file")
        if rg -q "$filename" "$CLAUDE_MD"; then
            echo "✅ $filename 已記錄"
        else
            echo "⚠️  $filename 未記錄"
        fi
    done
fi
```

---

## 步驟 7: 清理元資訊（--clean 選項）

```bash
# 呼叫 /claude:clean 功能
# 移除版本號、日期、統計等元資訊
```

---

## 步驟 8: 蒸餾（--all 選項）

```bash
# 呼叫 /claude:distill 功能
# 蒸餾精簡 CLAUDE.md
```

---

## 步驟 9: 內部品質檢查（品質層，--quality）

### 五維度檢查流程

**9.1 自洽性檢查**
- 術語使用是否統一（相同概念是否用相同詞彙）
- 前後描述是否一致
- 定義與使用是否吻合

**9.2 矛盾性檢查**
- 是否存在互相矛盾的陳述
- 規則之間是否有衝突
- 範例與說明是否矛盾

**9.3 順序檢查**
- 章節編號是否連續
- 標題層級是否正確（`#` → `##` → `###`，不跳級）
- 內容組織是否合理

**9.4 自包含檢查**
- 引用的檔案/路徑是否存在（已在前面的步驟驗證）
- 外部依賴是否可獲取
- 讀者是否需要額外資訊才能理解

**9.5 精準度檢查**
- 技術描述是否正確
- 程式碼範例是否可執行
- 連結是否有效

---

## 步驟 10: 導航有效性檢查（核心層，最重要）

> 導航是 sync 最核心的檢查。其他步驟發現的問題（路徑不存在、簽名不對）最終都轉化為導航修復。

```
1. 從 CLAUDE.md 抽取 3-5 個關鍵概念
2. 驗證每個概念是否有指向具體檔案、class 或 function 的導航路徑
3. 對照職責描述與檔案結構，驗證每項職責有對應的檔案指引
4. 檢查跨模組依賴是否具體到 class/function（不只是模組名）
5. 對多步驟流程驗證 step 間 input/output 可追蹤性（無流程標 N/A）
6. 執行導航 Decoder Test：不查源碼，嘗試回答 3 個導航問題
7. 對每個導航缺口產出 ACTION 修改建議（見 Sync Summary ACTION）
```

---

## 步驟 10.5: 交叉驗證（vs Snapshot）

> **觸發條件**：`.project-snapshot.json` 存在時執行。無 snapshot 時跳過。

消費步驟 0.5 載入的 snapshot 資料，執行跨 artifact 交叉驗證（角度 10-12）。

```
1. 消費 cross_validation[] 中的預計算結果：
   - X-path 問題：UC 路徑不存在 → 轉為角度 2（程式碼一致性）的具體案例
   - X6 問題：模組缺 CLAUDE.md → 轉為角度 11（模組覆蓋缺口）
   - X7 問題：斷裂 UC 引用 → 轉為角度 12（幽靈 UC 引用）的佐證
   - X-unique 問題：重複 UC ID → 標記為 critical

2. 角度 10：dep-graph 矛盾（X1）
   - 遍歷 claude_md_registry[]
   - 對每個有 declared_not_depend_on 的 CLAUDE.md
   - 比對 edges[] 中是否有對應的 import edge
   - 有矛盾 → 標記 [X1] critical

3. 角度 11：模組覆蓋缺口（X6）
   - 遍歷 modules[]（file_count >= 3）
   - 檢查 claude_md_registry[] 中是否有對應模組
   - 缺少 CLAUDE.md → 標記 [X6] important

4. 角度 12：幽靈 UC 引用（X8）
   - 收集 uc_registry[] 中所有 uc_id 形成有效集合
   - 遍歷 claude_md_registry[].referenced_uc_ids
   - 引用的 UC ID 不在有效集合中 → 標記 [X8] important
   - 額外檢查：搜尋 _archive/ 中是否有匹配的 UC（已歸檔）
```

**輸出格式**：

```markdown
### Cross-Validation (vs Snapshot)

- [X1] data/CLAUDE.md 宣告 "Does NOT depend on strategies" 但 edges 有 data→strategies
- [X6] Module 'services' (12 files) 缺少 CLAUDE.md
- [X8] root/CLAUDE.md 引用 TE-01，但 uc_registry 中不存在（可能在 _archive/）
- [X-path] D-15 路徑 data/fetchers/industry.py 不存在
```
