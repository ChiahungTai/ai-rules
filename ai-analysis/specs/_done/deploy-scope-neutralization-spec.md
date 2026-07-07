# Spec: deploy_agents.py scope 分類機制改善

> 用 LSP / bash-hard-rules / hooks 三個 case 驗證。

## User Story

**作為** ai-rules 維護者，
**我要**修正 `deploy_agents.py` 的 scope 分類機制——
1. 把 scope default 從 `claude-specific` 反轉為 `neutral`（讓通用知識預設跨 harness）
2. 修正 4 條已標錯的 claude-specific rules（通用內容被鎖住）
3. deploy 加斷 ref 檢測（error 級別，阻塞）
**以消除**「neutral rules 引用 claude-specific rules 形成斷 ref」的結構性缺陷。

## 痛點（現況）

### 核心矛盾

`deploy_agents.py` 的 scope 分類是**二元模型**（neutral vs claude-specific），假設「一條 rule 的內容要嘛全通用要嘛全 Claude 專屬」。但實測 5 條 claude-specific rules 中：

| rule | 真相 | 通用比例 | 斷 ref 風險 |
|------|------|---------|------------|
| lsp-navigation | 🟢 **標錯** | ~98% | 極高（7+ 處 neutral 引用） |
| modern-cli-preference | 🟢 **標錯** | ~90% | 中（邏輯斷 ref） |
| bash-hard-rules | 🟡 **Hybrid** | ~85% | 高（3 commands 引用通用 pipe-exit） |
| code-edit-constraints | 🟡 **Hybrid** | ~70% | 高（70% 通用原則 0 外部觸及） |
| model-routing | 🔴 標對 | ~10% | 低 |

### 具體危害

1. **斷 ref**：3 條 neutral rules（instruction-writing / collaboration-constraints / rules/AGENTS.md）引用 lsp-navigation.md（claude-specific），ZCode 讀者拿到死鏈
2. **通用知識消失**：code-edit-constraints 的 70% 通用編輯原則（SRP/DIP/變更紀律/禁混合寫法）在非 Claude harness 完全讀不到
3. **無檢測**：deploy_agents.py 不檢測 neutral → claude-specific 的斷 ref

## 範圍

### Always（必做）

1. **deploy_agents.py scope default 反轉**：default 從 `claude-specific` → `neutral`（`read_scope()` line 59 的 fallback 值）
2. **deploy_agents.py 加斷 ref 檢測**（error 級別）：掃 neutral rules 的 markdown link，若指向 claude-specific rule → 阻塞 deploy + 印具體斷 ref 位置
3. **lsp-navigation.md 改 neutral**：scope 改 + Claude 專屬呼叫語法（line 74 `LSP` tool 參數）用 `(Claude: ...)` 括號註隔離 + 補跨 harness LSP 載體對照（Claude native / ZCode lsp-python MCP / OpenCode 原生）
4. **modern-cli-preference.md 改 neutral**：scope 改 + Why 段 Claude 硬限制用括號註隔離 + 補 ZCode 對應
5. **bash-hard-rules.md 拆雙檔**：
   - 通用部分（pipe-exit / uv run / 禁 sed / pytest 背景跑 / agent prompt 指定工具 / 語義 LSP 摘要）→ 新 `rules/tool-discipline.md`（neutral）
   - Claude 專屬部分（`python -c` 換行 `#` 觸發權限 / `$VAR`/`$(cmd)` 展開偵測）→ 留 `bash-hard-rules.md`（claude-specific，瘦身）
6. **code-edit-constraints.md 拆雙檔**：
   - 通用編輯原則（SRP/DIP/變更紀律/禁混合寫法/衝突處理/向後相容）→ 新 `rules/edit-discipline.md`（neutral）
   - Claude Edit/Write 工具 API（Edit 前 Read / old_string 精確匹配 / 多位元組降級 Write / 自檢清單）→ 留 `code-edit-constraints.md`（claude-specific，瘦身）
7. **rules/AGENTS.md 更新**：scope 表反映新狀態（4 改 + 2 新 neutral + default 說明改）+ 加跨 harness 載體對照寫作 pattern
8. **04 報告 §7 事實修訂**：LSP 結論從「無統一載體」改為「分層策略」（Claude/OpenCode 原生；ZCode 用 MCP server；未來無 native 者用 MCP）

### Never（不做）

- ❌ 不刪 scope 機制（保留 frontmatter 顯式標記）
- ❌ 不改 bundle 格式（仍 guide + rules concatenated）
- ❌ 不拆 lsp-navigation 為雙檔（用括號註隔離即可，98% 通用不需拆）
- ❌ 不動 model-routing（標對了，~10% 通用可接受被鎖）
- ❌ 不為 hooks 建 rules/ 條目（hooks 是 settings.json 配置，已在 04 報告文件化）
- ❌ 不改 commands/（Claude-only，LSP 假設正確，之前查證確認健康）

## 邊界案例

| 案例 | 處理 |
|------|------|
| 新 rule 忘標 scope | default = neutral（安全：預設進 bundle） |
| claude-specific rule 被 neutral rule 引用 | deploy error 阻塞（強制修） |
| claude-specific rule 內含 `<!-- bundle: skip -->` 段 | 不適用（claude-specific 不進 bundle，skip marker 無意義） |
| neutral rule 內含 Claude 專屬段 | 用 `<!-- bundle: skip-start -->` 標記（不進 bundle，Claude 端透過 symlink 讀到） |
| lsp-navigation 改 neutral 後 Claude `LSP` tool 參數段 | 用括號註 `(Claude: ...)` 或 bundle:skip 隔離 |

## 成功條件（可驗證）

| # | 條件 | 驗證方式 |
|---|------|---------|
| 1 | deploy_agents.py default = neutral | 新 rule 不標 scope → 進 bundle |
| 2 | 斷 ref 檢測 error 級別 | 製造 neutral → claude-specific 引用 → deploy 阻塞 |
| 3 | lsp-navigation 進 bundle 且 ZCode 讀者拿到決策樹 | deploy 後 grep bundle 含 lsp-navigation |
| 4 | bash-hard-rules 拆分後通用部分進 bundle | deploy 後 grep bundle 含 tool-discipline |
| 5 | code-edit-constraints 拆分後通用部分進 bundle | deploy 後 grep bundle 含 edit-discipline |
| 6 | 無斷 ref | deploy 跑完 0 error |
| 7 | LSP case 驗證：ZCode LLM 讀到 lsp-navigation 決策樹 | 新 session 觸發 LSP 查詢情境，LLM 知道用 LSP |
| 8 | bash-hard-rules case 驗證：pipe-exit 原則在 ZCode bundle | grep bundle 含 pipe-exit |
| 9 | hooks case 驗證：hooks 仍只在 Claude | hooks 不在 bundle（無 neutral rule 提 hooks 為跨 harness） |

## 驗證 cases（3 個）

### Case 1: LSP（hybrid 80/20）
- **測什麼**：lsp-navigation 改 neutral 後，通用決策樹進 bundle、Claude 專屬呼叫語法被隔離
- **預期**：ZCode 讀者拿到完整決策樹（符號查詢用 LSP、反例、分工表）+ 知道自己用 lsp-python MCP
- **驗證**：deploy → grep bundle 含 lsp-navigation 決策樹 + 不含 Claude `LSP` tool 參數段

### Case 2: bash-hard-rules（hybrid 85/15）
- **測什麼**：拆雙檔後通用 pipe-exit 進 bundle、Claude 權限 `#`/`$` 留 claude-specific
- **預期**：ZCode 讀者拿到 pipe-exit / uv run / 禁 sed / pytest 背景跑；不拿到 Claude 權限系統
- **驗證**：deploy → grep bundle 含 tool-discipline + 不含 `#` 觸發權限

### Case 3: hooks（全 Claude 專屬）
- **測什麼**：hooks 不進 bundle（無 neutral rule）
- **預期**：ZCode bundle 完全無 hooks 相關 rule（hooks 是 Claude settings.json 配置，不是 rules/ 範疇）
- **驗證**：deploy → grep bundle 無 hooks

## UC 定位

ai-rules 無 Capabilities 表 → 本 spec 的 UC 是「跨 harness 部署機制」本身：
- **消費者**：非 Claude harness 的 LLM（ZCode / OpenCode / Codex）
- **行為**：讀到通用 rules（含 LSP 決策樹、pipe-exit、編輯紀律），不讀到 Claude 專屬機制
- **入口**：`deploy_agents.py` 生成的 `~/.{zcode,config/opencode,codex}/AGENTS.md`

## 後續

spec 完成後 → `/execution-plan`（大型變更，需完整段落劃分 + Scenario Matrix）→ `/ep-validate` → `/ep-review` → `/build`

## 不在範圍

- commands/ 層 → 不動（Claude-only，之前查證確認健康）
- hooks 機制 → 不動（已在 04 報告文件化）

## 斷 ref 修復清單（「趁這次把 ref 出問題都修好」）

### Layer 1: rules/ neutral → claude-specific（deploy 後 ZCode 死鏈）

| 斷 ref | 修法 | 連帶效果 |
|--------|------|---------|
| `instruction-writing.md:201` → lsp-navigation | lsp-navigation 改 neutral → 自動修復 | 7+ 處引用同時修 |
| `llm-output-convention.md:17` → lsp-navigation + modern-cli-preference | 兩條都改 neutral → 自動修復 | 2 處修 |
| `_ai-behavior-constraints.md:36` → bash-hard-rules | bash-hard-rules 拆出 tool-discipline (neutral) → 改指 tool-discipline | 1 處修 |
| `modern-cli-preference.md:19` → lsp-navigation（@-transclusion）| lsp-navigation 改 neutral → 兩條都 neutral，@ 變有效引用 | 1 處修 |

### Layer 2: skills/ → claude-specific rules（skills 跨 harness 讀）

| 斷 ref | 修法 | 連帶效果 |
|--------|------|---------|
| `skills/review-engine/SKILL.md` → lsp-navigation | lsp-navigation 改 neutral → 自動修復 | 1 處修 |
| `skills/arch-thinking/SKILL.md` → lsp-navigation | lsp-navigation 改 neutral → 自動修復 | 3 處修 |
| `skills/agent-workflow/SKILL.md` → model-routing | **model-routing 維持 claude-specific**（標對了）→ skill 引用改括號註 `(Claude: rules/model-routing.md)` | 4 處改括號註 |
| `skills/review-engine/SKILL.md` → model-routing | 同上 | 2 處改括號註 |

### Layer 3: commands/ → claude-specific（**不修**——Claude-only，健康）

| 引用方 | 被引用 | 狀態 |
|---|---|---|
| commit / lint-fix / build | bash-hard-rules | ✅ 健康（Claude-only）|
| deep-work / ep-review / execution-plan | code-edit-constraints | ✅ 健康 |
| judge-review / illustrate-structure-viewport | lsp-navigation | ✅ 健康 |
| 多 commands | model-routing | ✅ 健康 |

### 修復統計

- **自動修復**（rule 改 neutral 連帶）：lsp-navigation 7+ 處、modern-cli-preference 2 處、bash-hard-rules 1 處
- **手動修復**（skill 引用改括號註）：model-routing 在 agent-workflow 4 處 + review-engine 2 處 = 6 處
- **不修**：commands/ 全部（Claude-only 健康）
