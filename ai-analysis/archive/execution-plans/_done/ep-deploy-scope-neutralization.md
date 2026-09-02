# EP: deploy_agents.py scope 分類機制改善 + 斷 ref 全修

> **ep_type**: implementation（大型變更，14 檔）
> **parent spec**: [deploy-scope-neutralization-spec.md](../specs/deploy-scope-neutralization-spec.md)

## 動機（self-contained 背景）

`deploy_agents.py` 的 scope 分類是**二元模型**（neutral vs claude-specific），假設「一條 rule 全通用或全 Claude 專屬」。但實測 5 條 claude-specific rules 中，**4 條標錯**（通用比例 70-98%），導致：

1. **斷 ref**：3 條 neutral rules（instruction-writing / llm-output-convention / _ai-behavior-constraints）引用 claude-specific rules，ZCode 讀者拿到死鏈
2. **通用知識消失**：code-edit-constraints 的 70% 通用編輯原則在非 Claude harness 完全讀不到
3. **skills 斷 ref**：review-engine / arch-thinking 引用 claude-specific 的 lsp-navigation
4. **無檢測**：deploy_agents.py 不檢測 neutral → claude-specific 的斷 ref

**修法**：(1) scope default 從 claude-specific 反轉為 neutral；(2) 4 條標錯的 rule 改 neutral 或拆雙檔；(3) deploy 加斷 ref error 檢測；(4) skills 引用 model-routing 改括號註。用 LSP / bash-hard-rules / hooks 三個 case 驗證。

**Scope out**：
- commands/ 層不動（Claude-only，之前查證確認健康）
- hooks 機制不動（已在 04 報告文件化）
- model-routing 不動（標對了，~10% 通用可接受）
- rules/ 的 neutral 中性化規範結構不動（只補跨 harness 載體對照 pattern）

---

## 實作總覽

| 段落 | 職責 | 依賴 | 風險 |
|------|------|------|------|
| **S1** | deploy_agents.py 改 default=neutral + 加斷 ref error 檢測 | 無 | 🟡 改 deploy 邏輯 |
| **S2** | lsp-navigation.md 改 neutral + Claude 段括號註 + 補跨 harness 載體對照 | S1（default 改後驗證） | 🟢 純文檔 |
| **S3** | modern-cli-preference.md 改 neutral + Why 段括號註 | S1 | 🟢 純文檔 |
| **S4** | bash-hard-rules.md 拆雙檔 → tool-discipline.md (neutral) + bash-hard-rules.md (瘦身) | S1 | 🟡 拆分語義 |
| **S5** | code-edit-constraints.md 拆雙檔 → edit-discipline.md (neutral) + code-edit-constraints.md (瘦身) | S1 | 🟡 拆分語義 |
| **S6** | rules/AGENTS.md scope 表更新 + 補跨 harness 載體對照 pattern | S2-S5（所有 rule 改完後） | 🟢 索引同步 |
| **S7** | skills/ 斷 ref 修復（model-routing 引用改括號註） | 無 | 🟢 純文檔 |
| **S8** | 04 報告 §7 事實修訂 + deploy + 驗證 | S1-S7（全部完成後） | 🟡 整合驗證 |

8 段，序列（S1 先改 deploy → S2-S5 改 rules → S6 索引 → S7 skills → S8 驗證）。

---

## UC 盤點（大型變更，docs mode — 元專案無 Capabilities 表格）

### 掃描範圍
- `scripts/deploy_agents.py`（deploy 邏輯）
- `rules/*.md`（19 條，5 條 claude-specific 中 4 條要改）
- `skills/review-engine/SKILL.md`、`skills/arch-thinking/SKILL.md`（斷 ref）
- `skills/agent-workflow/SKILL.md`（model-routing 引用）
- `rules/AGENTS.md`（scope 表 + 中性化規範）
- `ai-analysis/reports/superpowers/04-multi-harness機制對照.md` §7

### 受影響 UC（無新 UC，皆為既有狀態修訂）
| 項目 | 現況 | 目標 |
|------|------|------|
| deploy scope default | claude-specific | neutral |
| lsp-navigation scope | claude-specific | neutral |
| modern-cli-preference scope | claude-specific | neutral |
| bash-hard-rules | claude-specific（Hybrid 85% 通用） | 拆：tool-discipline (neutral) + bash-hard-rules (瘦身 claude-specific) |
| code-edit-constraints | claude-specific（Hybrid 70% 通用） | 拆：edit-discipline (neutral) + code-edit-constraints (瘦身 claude-specific) |
| deploy 斷 ref 檢測 | 無 | error（阻塞） |
| skills model-routing 引用 | 裸 ref | 括號註 (Claude: ...) |

---

## Scenario Matrix（大型變更，docs mode 文檔語境）

| SM | 情境 | 觸發 | 預期行為 | 恢復點 | UC |
|----|------|------|---------|--------|----|
| SM-1 | 新 rule 不標 scope | 新增 rule | default = neutral → 進 bundle（安全預設） | 加 `harness-scope: claude-specific` 排除 | S1 |
| SM-2 | neutral rule 引用 claude-specific rule | 編輯 neutral rule 時 | deploy **error 阻塞** + 印斷 ref 位置 | 修 ref 或改被引用方 scope | S1 |
| SM-3 | ZCode LLM 需 LSP 決策樹 | 符號查詢情境 | lsp-navigation 已進 bundle → 讀到決策樹 + 知道用 lsp-python MCP | 無 | S2 |
| SM-4 | ZCode LLM 需 pipe-exit 原則 | 閘門命令執行 | tool-discipline 已進 bundle → 讀到 pipe-exit 原則 | 無 | S4 |
| SM-5 | ZCode LLM 需編輯紀律 | code 編輯情境 | edit-discipline 已進 bundle → 讀到 SRP/DIP/變更紀律 | 無 | S5 |
| SM-6 | Claude LLM 讀 lsp-navigation | Claude session | 決策樹 + Claude `LSP` tool 參數都讀到（括號註不影響 Claude 端） | 無 | S2 |
| SM-7 | deploy 跑斷 ref 檢測 | 修改 rules 後 deploy | 全部 ref 修完 → 0 error → deploy 成功 | 無 | S8 |
| SM-8 | hooks 確認不進 bundle | deploy 後 | grep bundle 無 hooks | 無 | S8 |

---

## S1: deploy_agents.py 改 default=neutral + 斷 ref error 檢測

### Context
- **背景**：`deploy_agents.py:59` 的 `read_scope()` default 是 `"claude-specific"`——新 rule 不標 scope 就不進 bundle。這是安全保守的預設，但違反「通用知識預設跨 harness」的精神。
- **同時**：deploy 無斷 ref 檢測——neutral rule 可以引用 claude-specific rule 而不被告警。
- **UC 引用**：SM-1（default neutral）、SM-2（斷 ref error）

### 核心實作要點
1. **`read_scope()` default 改 `"neutral"`**（line 59, 62, 68 三處 fallback 值）
2. **加 `check_broken_refs()` 函式**：
   - 掃所有 neutral rules 的 markdown link（pattern：`[text](rule-name.md)` 或裸 `rule-name.md`）
   - 若 link target 是 claude-specific rule → 收集為 broken ref
   - 若有 broken refs → 印具體位置 + `return 1`（阻塞 deploy）
3. **`main()` 加 `check_broken_refs()` 呼叫**（在 `build_bundle` 之前）
4. **docstring 更新**：default 改 neutral + 說明斷 ref 檢測

### Pseudo Code（Python）
```python
def read_scope(path: pathlib.Path) -> str:
    """Extract harness-scope. Default: neutral."""
    # ... (三處 fallback 改 "neutral")

def check_broken_refs(rules_dir, target_scopes) -> list[tuple[str, str, str]]:
    """Scan neutral rules for refs to claude-specific rules. Return broken refs."""
    neutral_rules = discover_rules(rules_dir, {"neutral"})
    claude_rules = discover_rules(rules_dir, {"claude-specific"})
    claude_names = {p.stem for p in claude_rules}
    broken = []
    for nrule in neutral_rules:
        content = nrule.read_text()
        for link_target in re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', content):
            target_stem = pathlib.Path(link_target[1]).stem
            if target_stem in claude_names:
                broken.append((nrule.name, link_target[1], target_stem))
        # 也掃裸 rule-name.md 引用
        for match in re.finditer(r'`([a-z-]+\.md)`', content):
            target_stem = match.group(1).replace('.md', '')
            if target_stem in claude_names:
                broken.append((nrule.name, match.group(1), target_stem))
    return broken

# main() 加：
broken = check_broken_refs(RULES_DIR, target_scopes)
if broken:
    print("[FAIL] Broken refs: neutral rules referencing claude-specific rules:")
    for src, target, name in broken:
        print(f"  {src} -> {target} ({name} is claude-specific)")
    return 1
```

### 驗證策略
- **S1 專屬**：`uv run python scripts/deploy_agents.py --dry-run` 跑（但斷 ref 會 error——S2-S5 修完後才能跑通）
- **單元測試**：製造一個 neutral rule 引用 claude-specific rule → deploy 應阻塞 + 印位置
- **驗證閘門**：S8 整合驗證時 deploy 跑通 0 error

---

## S2: lsp-navigation.md 改 neutral + Claude 段括號註

### Context
- **背景**：lsp-navigation.md 98% 內容跨 harness 通用（決策樹、反例、與 rg/fd 分工、驗證 workflow、輸出格式）。僅 line 74「Claude Code 內建 `LSP` tool（native，非 MCP）。參數：`operation`, `filePath`, `line`, `character`」是 Claude 專屬。
- **斷 ref 修復**：改 neutral 後，7+ 處引用（instruction-writing / llm-output-convention / modern-cli-preference / review-engine / arch-thinking / judge-review / illustrate-structure-viewport）自動修復。
- **UC 引用**：SM-3（ZCode 讀到決策樹）、SM-6（Claude 仍讀到完整）

### 核心實作要點
1. **frontmatter `harness-scope:` 改 `neutral`**
2. **載入機制註記**：改用 rules/AGENTS.md 標準 neutral 載入機制註記（取代現有的 claude-specific 載入描述）
3. **line 74 Claude 專屬段括號註隔離**：
   - 改為：「Claude 端：Claude Code 內建 `LSP` tool（native，非 MCP），參數 `operation`/`filePath`/`line`/`character`。其他 harness 的 LSP 載體見下方對照表。」
4. **補「跨 harness LSP 載體對照」段**（新增）：
   ```
   ## 跨 harness LSP 載體對照

   | harness | LSP 機制 | 呼叫方式 |
   |---------|---------|---------|
   | Claude Code | 原生 plugin（12 lang）| `LSP` tool（operation: hover/findReferences/...）|
   | ZCode | 自建 lsp-python MCP（per-project）| `mcp__lsp-python__hover` 等（mosaic_alpha 參考實作）|
   | OpenCode | 原生 LSP | （官方文檔說有，未實測）|
   | 未來無 native | 用 MCP server 支援 | mosaic_alpha lsp-python 為 reference impl |
   ```
5. **line 87「編輯後自動 diagnostics」加括號註**：「(Claude: 每次檔案編輯後 LSP 自動推送 diagnostics；其他 harness 機制不同)」

### 驗證策略
- **rg 殘留**：`rg "claude-specific" rules/lsp-navigation.md` → 無命中
- **括號註檢查**：`rg "Claude:" rules/lsp-navigation.md` → Claude 專屬段都有括號註
- **`/consistency`**：跑 lsp-navigation.md

---

## S3: modern-cli-preference.md 改 neutral

### Context
- **背景**：modern-cli-preference.md 90% 通用（fd/rg 語法速查、隱藏檔陷阱、alternation 陷阱、搜尋策略）。僅 line 25-26「find -exec/grep -r 是 Claude 硬限制 + auto-allow」是 Claude 專屬。
- **斷 ref 修復**：改 neutral 後，llm-output-convention.md:17 引用修復 + modern-cli-preference:19 的 `@`-transclusion 指向 lsp-navigation（S2 改 neutral 後）也修復。
- **UC 引用**：SM-3（ZCode 讀到 CLI 速查）

### 核心實作要點
1. **frontmatter `harness-scope:` 改 `neutral`**
2. **載入機制註記**：改用標準 neutral 載入機制註記
3. **line 25-26 Why 段括號註隔離**：
   - 改為：「(Claude: `find -exec`、`grep -r` 是 Claude Code 系統層級硬限制，無法被 allow 規則覆蓋；`fd`/`rg` 預設可被 auto-allow)」
4. **line 19 `@`-transclusion 改 markdown link**：`@~/Github/ai-rules/rules/lsp-navigation.md` → `[lsp-navigation.md](lsp-navigation.md)`（neutral rule 禁 `@`）

### 驗證策略
- **rg 殘留**：`rg "claude-specific|@~" rules/modern-cli-preference.md` → 無命中

---

## S4: bash-hard-rules.md 拆雙檔

### Context
- **背景**：bash-hard-rules.md 85% 通用（pipe-exit / uv run / 禁 sed / pytest 背景跑 / agent prompt 指定工具 / 語義 LSP 摘要），15% Claude 專屬（`python -c` 換行 `#` 觸發權限 / `$VAR`/`$(cmd)` 展開偵測）。
- **拆分**：通用 → 新 `rules/tool-discipline.md`（neutral）；Claude 專屬 → 留 `rules/bash-hard-rules.md`（claude-specific，瘦身）。
- **斷 ref 修復**：_ai-behavior-constraints.md:36 引用 bash-hard-rules → 改指 tool-discipline。
- **commands 引用**：commit.md / lint-fix.md / build.md 引用 bash-hard-rules 的通用部分（pipe-exit）→ 這些是 Claude-only commands，不改（仍指向 bash-hard-rules.md 即可，因 Claude 端 symlink 讀到兩檔）。
- **UC 引用**：SM-4（ZCode 讀到 pipe-exit）

### 核心實作要點
1. **新 `rules/tool-discipline.md`（neutral）**：
   - frontmatter `harness-scope: neutral`
   - 搬入通用部分：語義 LSP / 文字 rg / 檔案 fd 分工（摘要，指 lsp-navigation 補細節）+ agent prompt 必須指定工具 + `uv run` 前綴 + 禁 `sed` 修改 + pytest 背景跑 + **閘門命令禁 pipe 到 tail/grep**（exit code 被覆蓋）+ 繁中 + 英文術語
2. **`rules/bash-hard-rules.md` 瘦身（claude-specific）**：
   - 保留 Claude 專屬：`python -c` 禁換行 `#` 註解 + `$VAR`/`$(cmd)` 禁展開 + 權限提示語境
   - 加一行引用：「通用工具紀律（uv run / pipe-exit / 禁 sed）見 `tool-discipline.md`（neutral）」
3. **`_ai-behavior-constraints.md:36` 改指 tool-discipline**：「Claude 端完整 Bash 硬限制見 `bash-hard-rules.md`（claude-specific）」→ 改「通用工具紀律見 `tool-discipline.md`；Claude 端 `python -c` / `$` 展開限制見 `bash-hard-rules.md`（claude-specific）」

### 驗證策略
- **rg 確認拆分**：`rg "pipe.*exit\|pipefail" rules/tool-discipline.md` → 命中；`rg "pipe.*exit" rules/bash-hard-rules.md` → 不命中（已搬出）
- **bundle 檢查**：deploy 後 grep bundle 含 tool-discipline

---

## S5: code-edit-constraints.md 拆雙檔

### Context
- **背景**：code-edit-constraints.md 70% 通用（SRP/DIP/變更紀律/禁混合寫法/衝突處理/向後相容/反例），30% Claude 專屬（Edit 前 Read / old_string 精確匹配 / 多位元組降級 Write / 自檢清單）。
- **拆分**：通用 → 新 `rules/edit-discipline.md`（neutral）；Claude 專屬 → 留 `code-edit-constraints.md`（claude-specific，瘦身）。
- **斷 ref**：無 neutral rule 引用 code-edit-constraints（0 外部引用），但通用原則在非 Claude 完全消失。
- **UC 引用**：SM-5（ZCode 讀到編輯紀律）

### 核心實作要點
1. **新 `rules/edit-discipline.md`（neutral）**：
   - frontmatter `harness-scope: neutral`
   - 搬入通用部分：核心原則（優先編輯現有檔案/品質優先/SRP/DIP/不洩漏實作）+ 衝突寫法處理（禁混合兩種矛盾寫法）+ 向後相容確認 + 變更範圍紀律（修 bug 與重構分開/清理孤兒）+ 反例
2. **`rules/code-edit-constraints.md` 瘦身（claude-specific）**：
   - 保留 Claude 專屬：Edit 工具使用約束（Edit 前 Read / old_string 精確匹配 / 連續失敗改 Write）+ 多位元組降級 + 自檢清單
   - 加引用：「通用編輯紀律（SRP/DIP/變更紀律）見 `edit-discipline.md`（neutral）」
3. **SOLID 段**：code-edit-constraints.md:123 的「SRP/OCP/LSP（子型替換）/ISP/DIP」屬通用 → 搬入 edit-discipline.md

### 驗證策略
- **rg 確認拆分**：`rg "SRP\|DIP\|變更紀律" rules/edit-discipline.md` → 命中
- **bundle 檢查**：deploy 後 grep bundle 含 edit-discipline

---

## S6: rules/AGENTS.md scope 表更新 + 補跨 harness 載體對照 pattern

### Context
- **背景**：rules/AGENTS.md:40-45 的 scope 表需反映 S2-S5 的改動。同時加「跨 harness 載體對照」寫作 pattern 到中性化規範。
- **UC 引用**：SM-1（default neutral 說明）

### 核心實作要點
1. **scope 表更新**：
   - `lsp-navigation` 🔴 → 🟢 neutral（說明改「符號導航決策樹 + 跨 harness LSP 載體對照」）
   - `modern-cli-preference` 🔴 → 🟢 neutral（說明改「fd/rg CLI 速查（Claude 權限段括號註）」）
   - `bash-hard-rules` 🔴 → 🔴 claude-specific（瘦身，說明改「Claude 權限（`#`/`$` 偵測）」）
   - 新增 `tool-discipline` 🟢 neutral（通用工具紀律）
   - 新增 `edit-discipline` 🟢 neutral（通用編輯紀律）
   - `code-edit-constraints` 🔴 → 🔴 claude-specific（瘦身，說明改「Claude Edit 工具 API」）
   - default 說明改：「default = neutral（rule 需顯式標 claude-specific 才不進 bundle）」
2. **中性化規範補「跨 harness 載體對照」pattern**：
   - 在「通用模式：括號註隔離 Claude 機制」段後加：
     ```
     ### 跨 harness 載體對照（當工具呼叫方式跨 harness 不同時）

     當一個概念跨 harness 通用但呼叫方式不同時（如 LSP），用對照表表達：
     | harness | 工具 | 呼叫方式 |
     |---------|------|---------|
     | Claude | ... | ... |
     | ZCode | ... | ... |
     ```

### 驗證策略
- **scope 表一致性**：表中的 scope 與各 rule 實際 frontmatter 一致
- **`/consistency`**：跑 rules/AGENTS.md

---

## S7: skills/ 斷 ref 修復（model-routing 引用改括號註）

### Context
- **背景**：skills/agent-workflow 引用 model-routing 4 處、skills/review-engine 引用 model-routing 2 處。model-routing 確實是 claude-specific（model 階層是 Claude 特有），不改 scope。修法：skills 的引用改括號註。
- **lsp-navigation 引用**：review-engine + arch-thinking 引用 lsp-navigation → S2 改 neutral 後自動修復，不需動 skills。
- **UC 引用**：無新 UC

### 核心實作要點
1. **`skills/agent-workflow/SKILL.md`** 4 處 model-routing 引用改括號註：
   - 裸 ref `model-routing.md` → `(Claude: rules/model-routing.md)`
2. **`skills/review-engine/SKILL.md`** 2 處 model-routing 引用改括號註（同上）
3. **lsp-navigation 引用不動**（S2 改 neutral 後自動修復）

### 驗證策略
- **rg 殘留**：`rg "model-routing" skills/agent-workflow/ skills/review-engine/` → 只在括號註 `(Claude: ...)` 內

---

## S8: 04 報告 §7 事實修訂 + deploy + 整合驗證

### Context
- **背景**：04 報告 §7 的 LSP 結論需從「無統一載體」改為「分層策略」。同時跑 deploy 驗證所有改動。
- **UC 引用**：SM-7（deploy 0 error）、SM-8（hooks 不進 bundle）

### 核心實作要點
1. **04 報告 §7 啟示 4 修訂**：
   - 原：「LSP 跨 harness **無統一載體**」
   - 改：「LSP 跨 harness **分層策略**——Claude/OpenCode 原生內建；ZCode 用自建 MCP server（mosaic_alpha lsp-python）；未來無 native 的 harness 用 MCP server 支援。deploy scope neutral 化後，LSP 決策樹（lsp-navigation.md）已跨 harness 進 bundle。」
2. **跑 `uv run python scripts/deploy_agents.py`**：
   - 驗證：0 斷 ref error
   - 驗證：bundle 含 lsp-navigation + tool-discipline + edit-discipline + modern-cli-preference
   - 驗證：bundle **不含** hooks 相關 rule
   - 驗證：bundle **不含** Claude 專屬段（`#` 觸發權限 / Edit old_string / model 階層）
3. **部署確認**：deploy 寫入 ~/.zcode/AGENTS.md、~/.config/opencode/AGENTS.md、~/.codex/AGENTS.md

### 驗證策略
- **deploy 0 error**：`uv run python scripts/deploy_agents.py` exit 0
- **bundle 內容檢查**：
  - `rg "lsp-navigation\|tool-discipline\|edit-discipline\|modern-cli-preference" ~/.zcode/AGENTS.md` → 全命中
  - `rg "python -c.*#\|old_string\|opus.*sonnet.*haiku" ~/.zcode/AGENTS.md` → 不命中（Claude 專屬段被排除）
- **`/consistency`**：跑 04 報告

---

## 收尾步驟

1. **rules/AGENTS.md 部署紀律**：確認「編輯 rule 後跑 deploy」流程仍有效
2. **04 報告 §7**：反映 deploy scope neutral 化的結果
3. **CLAUDE.md（root wrapper）**：確認雙檔模式的 agents/hooks 條目不需同步（本次不動 agents/hooks 目錄結構）
4. **commit**：14 檔變更 + 2 新檔，type=refactor（結構重整，行為等價或改善）

---

## 風險與降級

| 風險 | 機率 | 降級路徑 |
|------|------|---------|
| S1 斷 ref 檢測誤報（括號註內的引用被誤判） | 中 | `check_broken_refs` 排除括號註 `(Claude: ...)` 內的引用 |
| S4/S5 拆分時通用內容漏搬或重複 | 中 | rg 確認拆分後兩檔不重複 + build 階段 /consistency |
| S2 lsp-navigation 改 neutral 後 Claude 端行為變化 | 低 | Claude 端仍透過 symlink 讀到完整檔（括號註不影響 Claude 讀者） |
| deploy default 改 neutral 後，未標 scope 的舊 rule 進 bundle | 低 | repo 所有 rules 都已顯式標 scope（掃描確認） |
| bundle 膨脹（新增 4 條 neutral rules） | 中 | deploy --dry-run 看 token 估算；必要時用 bundle:skip 標記 |

---

## 驗證策略（docs mode + Python script 變更）

- **rg 閘門**：
  - `rg "claude-specific" rules/lsp-navigation.md rules/modern-cli-preference.md` → 無命中（scope 已改）
  - `rg "pipe.*exit\|pipefail" rules/tool-discipline.md` → 命中（拆分成功）
  - `rg "SRP\|DIP\|變更紀律" rules/edit-discipline.md` → 命中
  - `rg "model-routing" skills/agent-workflow/ skills/review-engine/` → 只在括號註內
- **deploy 閘門**：
  - `uv run python scripts/deploy_agents.py` → exit 0（0 斷 ref error）
  - `uv run python scripts/deploy_agents.py --dry-run` → bundle 含新 neutral rules
- **`/consistency`**：跑 rules/AGENTS.md + lsp-navigation.md + 04 報告
- **Python 驗證**：`uv run python scripts/deploy_agents.py --dry-run`（執行 script 本身驗證無語法錯誤）
