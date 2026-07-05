# 04 — Multi-harness 機制對照（sp vs ai-rules）

> **為什麼有這份**：`02` 在「ai-rules 只用 Claude Code」前提下決定「不借結構類」。其後 ai-rules 完成 multi-harness 轉型（`431a1d9` → `160a807` → `077753c`），現在實際部署到 zcode / opencode / codex（`deploy_agents.py` 生成單一 bundle 寫三家全域 AGENTS.md）。使用者問「sp 怎樣支援 multi harness，有沒有可參考改進的」—— 本檔用 arch-thinking 視角 + 結構機械查證，**精確定位兩家機制差異的根本原因**，並回頭檢驗 `02` 的「不借結構類」在轉型後是否仍然成立。
> 接續 [`02-sp借鑒到ai-rules.md`](02-sp借鑒到ai-rules.md)；結構全貌見 [`01-結構理解與診斷.md`](01-結構理解與診斷.md)。

---

## TL;DR

1. **sp 與 ai-rules 的 multi-harness 分歧是「內容性質」決定的，不是工程選擇**。sp 的 skill 是**指令性動作**（"dispatch a subagent" → 要翻譯成各家 tool name），所以**必須**有三層（skill ← tool mapping ← bootstrap）。ai-rules 的 rule 是**宣告式約束**（"禁止 python -c 註解"、"修改後必須執行"），所有 harness 讀起來一字不差 → **不需要 tool mapping 層**。`02` 的「不借結構類」從根上是對的，原因比「scope 邊界」更深：**宣告式內容跨 harness 零翻譯成本**。
2. **可借的不是「機制」，是 sp 機制解決的「問題清單」**。sp 為 multi-harness 付出複雜度解了 5 類問題（bootstrap 必載 / tool 翻譯 / 安裝機制 / 靜默失敗偵測 / 雙處同步），其中 ai-rules **只該關注 2 類**（靜默失敗偵測、安裝機制可攜性），另 3 類對宣告式 rule 無意義。借「問題意識」不借「解法」。
3. **ai-rules 當前真正的 multi-harness 缺口不在 bundle 層**（`deploy_agents.py` 的 harness-scope 分類已落地），在**下游消費側**：skills/commands 仍 Claude-only（43 skills + 30+ commands 0 家跨 harness）、各家對 AGENTS.md 的**載入語意差異未驗證**（`@`-include 是否展開、frontmatter 是否被消費、rules auto-load 是否等價）。這是 sp 用 acceptance test + marker test 防住、而 ai-rules 還沒有機械保證的地方。
4. **最高 ROI 借鑒：sp 的「unique-marker test」手法**。不是引進它的 bootstrap 機制，是把它的**驗證哲學**搬過來——「宣稱跨 harness 可攜就要有 marker 證明真的被讀到」。ai-rules 的 multi-harness 目前是「deploy 成功 = 寫到檔案」，缺「read-back 證明 harness 真的載入且語意正確」這一環。

---

## 1. 機制對照（兩家 multi-harness 怎麼做）

### 1.1 三軸差異全景

| 維度 | superpowers | ai-rules |
|------|-------------|----------|
| **內容性質** | 指令性動作（skill 描述 "做什麼動作"） | 宣告式約束（rule 宣告 "不可妥協的規則"） |
| **跨 harness 翻譯需求** | 🔴 高 —— 動作詞彙要 map 到各家 tool name | 🟢 零 —— 約束文字跨 harness 一字不差 |
| **source 真相層** | `skills/`（harness-agnostic） | `rules/`（neutral scope）+ `ai-development-guide.md` |
| **adapter 層** | `references/<harness>-tools.md`（per-harness tool 翻譯） | 無（不需要） |
| **bootstrap 層** | session-start injector（Shape A/B/C） | 無（依賴各家 AGENTS.md auto-load 慣例） |
| **分發機制** | per-harness plugin manifest（`.claude-plugin/` 等 dotdir）+ marketplace | `deploy_agents.py` 生成單一 bundle → 寫 3 家全域 AGENTS.md |
| **Claude 端差異處理** | 與其他 harness 同走 plugin 機制（`hooks/hooks.json`） | **例外**：symlink 到 slim guide + `~/.claude/rules/` auto-load（**不**走 bundle） |
| **驗收方式** | acceptance test（live tmux：`brainstorming` 自動觸發）+ marker test | 無（deploy 寫檔成功即視為完成） |

### 1.2 sp 的三層（為什麼必須三層）

sp 的 skill 寫 "dispatch a subagent"（`skills/using-superpowers/SKILL.md` 動作詞彙），這句話在 Claude Code = `Task(subagent_type)`，在 Codex = `spawn_agent`（需 config 開 `multi_agent`），在 Antigravity = `invoke_subagent`（且 task tracking 要 fallback 成 file artifact 因為無 todo tool）。**不翻譯 = model 看得到 skill 卻呼叫不出 tool**。

這就是 sp `docs/porting-to-a-new-harness.md` Part 1 rule 1「Skills name actions, not tools; porting 只編輯 tool mapping，絕不 reach into SKILL.md」的**結構必然性**：因為動作詞彙隨 harness 變，但 skill body 不能變，所以**必須**有中介翻譯層。三層不是 over-engineering，是指令性內容跨 harness 的**最小可行結構**。

### 1.3 ai-rules 的單層（為什麼一層就夠）

ai-rules 的 rule 寫「禁止 `python -c` 多行換行後接 `#` 註解」（`rules/bash-hard-rules.md`）、「修改後必須 `uv run` 實際執行」（`rules/must-execute-before-complete.md`）。這些是**宣告式約束**——描述「什麼是對的」，不是「呼叫哪個 tool 來做」。

同一句「修改後必須執行」在 Claude Code / ZCode / OpenCode / Codex 讀起來**完全相同**，model 自己會用它當下的 tool（Bash / 哪家都叫類似名字）去滿足約束。**不需要中介翻譯層**，因為沒有東西需要翻譯。

這就是 `deploy_agents.py` 能用「單一 bundle 寫三家」的原因：neutral rules 的**語意跨 harness 不變**，差異只在「檔案落在哪個全域路徑」（zcode `~/.zcode/AGENTS.md` / opencode `~/.config/opencode/AGENTS.md` / codex `~/.codex/AGENTS.md`），那是**檔案系統部署差異**不是**內容翻譯差異**。

> **arch-thinking 視角**：兩家都符合「依賴向內」（source 不認識 harness）。差別在 **source 的抽象層次**：sp 的 source 抽象到「動作」（仍需 adapter 具象化），ai-rules 的 source 抽象到「原則」（本身即具象，跨 harness 讀取等價）。抽象層次越高，下游 adapter 越薄——ai-rules 的 adapter 薄到不存在。

---

## 2. sp 機制解的 5 類問題，哪些 ai-rules 該關注

把 sp 的 multi-harness 機制拆成它**實際解的問題**，再逐類判斷對 ai-rules 是否有意義：

### 2.1 問題清單（sp 解了什麼）

| # | sp 解的問題 | sp 的解法 | 對 ai-rules 是否成立 |
|---|-----------|-----------|---------------------|
| 1 | **bootstrap 必須每 session 強制載入** | session-start injector（Shape A/B/C）+ `<EXTREMELY_IMPORTANT>` wrapper | ❌ **不成立** —— ai-rules 的 rules 走各家 AGENTS.md auto-load 慣例（每 session 自動讀），不需要 injector 強制；強制載入與 ai-rules 的 on-demand 省 context 哲學衝突（見 `02` 不借結構類理由） |
| 2 | **動作詞彙翻譯成各家 tool name** | `references/<harness>-tools.md` per-harness | ❌ **不成立** —— ai-rules 是宣告式 rule，無動作詞彙需翻譯（見 1.3） |
| 3 | **安裝機制可攜性（不編輯 user config）** | per-harness plugin manifest + marketplace，rule 2「只走 install mechanism」 | 🟡 **部分成立** —— ai-rules 的 `deploy_agents.py` 直接寫 user 全域目錄（`~/.zcode/` 等），**違反 sp 的 rule 2**（但 ai-rules 是個人 rules repo 非 plugin，定位不同；見 §3 討論） |
| 4 | **靜默失敗偵測（bootstrap 沒載入不報錯）** | acceptance test（live tmux）+ unique-marker test | ✅ **完全成立** —— ai-rules 的 bundle 寫到檔案 ≠ harness 真的載入且語意正確；目前無 read-back 驗證 |
| 5 | **雙處同步（mapping 兩處）** | 靠紀律（sp 的 Pi dual-maintenance 是已知結構債） | 🟡 **類比成立** —— ai-rules 有 Claude vs non-Claude 的**邏輯雙軌**（symlink+auto-load vs bundle），雙軌語意一致性靠 `deploy_agents.py` 紀律，無機械保證 |

### 2.2 為什麼 #1、#2 對 ai-rules 無意義

`02` 的「不借結構類」涵蓋了 bootstrap（#1）和 adapter（#2），但理由寫的是「與 on-demand 省 context 衝突」和「要重寫才有」。**轉型後可以更精確地說**：這兩層對宣告式 rule **結構上無作用**——

- bootstrap 層的存在前提是「source 不會被 harness 自動載入，要強制注入」。ai-rules 的 neutral rules 各家 AGENTS.md 本來就 auto-load（這是 AGENTS.md 慣例的保證，不是 ai-rules 要解的問題）。**bootstrap 解的問題 ai-rules 不存在**。
- tool-mapping 層的存在前提是「source 含動作詞彙，要翻譯」。ai-rules 的 rule 是宣告式，無動作詞彙。**tool-mapping 解的問題 ai-rules 不存在**。

所以這不是「借不借」的取捨，是「**解的問題不存在，借了是空殼**」。比 `02` 的「scope 邊界」論證更根本。

### 2.3 為什麼 #4、#5 是 ai-rules 真實缺口

這是轉型後才浮現的、`02` 寫作時 ai-rules 還沒到的階段：

**#4 靜默失敗偵測**：`deploy_agents.py` 寫檔成功只證明「檔案落到磁碟」，**不證明**：
- ZCode 真的 auto-load `~/.zcode/AGENTS.md`（而非只讀專案層）
- OpenCode 真的讀 `~/.config/opencode/AGENTS.md`（它的 fallback 鏈：`AGENTS.md` > `CLAUDE.md`，若使用者也有 `~/.claude/CLAUDE.md` symlink，讀序可能交互）
- Codex 真的讀 `~/.codex/AGENTS.md`（而非只讀 `~/.codex/config.toml`）
- bundle 內的 frontmatter（`harness-scope: neutral`）被各家**忽略**而非誤消費
- bundle 內的 markdown link / `@`-notation 在各家語意正確（AGENTS.md 的 `@`-include 語意因 harness 而異，見 `02` instruction-writing.md 警告）

sp 用 acceptance test（`docs/porting-to-a-new-harness.md` Part 3：live session 問 model「describe your superpowers」，marker 沒到 = bootstrap 沒載）防這類靜默失敗。**ai-rules 目前完全沒有對等驗證**——「deploy 成功」被當成「跨 harness 可攜成功」，但中間缺了「harness 真的讀到且讀對」這一步。

**#5 邏輯雙軌同步**：Claude 端走 symlink（`~/.claude/CLAUDE.md` → slim guide）+ `~/.claude/rules/` symlink auto-load（**完整 rule 內容含 frontmatter**）；non-Claude 端走 bundle（`deploy_agents.py` 抽 neutral rules、slim bundle-skip 段、寫單一檔）。**兩軌的內容語意是否等價**目前靠 `deploy_agents.py` 的 scope 分類紀律，無 read-back diff 驗證。sp 的 Pi dual-maintenance 是同一類問題（兩處須手動同步）的結構債——ai-rules 的雙軌目前是「靠紀律」，還沒變成結構債，但隨規則演化會 drift。

---

## 3. sp 機制的「rule 2」（不編輯 user config）—— 要不要遵守？

sp 最強的硬約束之一（`docs/porting-to-a-new-harness.md` Part 1 rule 2）：**「一切走 harness 的 install mechanism，絕不編輯 user 全域/個人 config」**。理由：plugin 該自包含，編輯 user config 是越界。

ai-rules 的 `deploy_agents.py` **直接違反這條**——它寫 `~/.zcode/AGENTS.md`、`~/.config/opencode/AGENTS.md`、`~/.codex/AGENTS.md`，還把 Claude 的 `~/.claude/CLAUDE.md` 設成 symlink。

但這**不是缺陷，是定位差異**：

| 定位 | sp | ai-rules |
|------|----|---------|
| 產品型態 | **plugin**（給不特定 user install） | **個人 rules repo**（作者自用 + dogfood） |
| 「user config」是誰的 | **別人的**（plugin user） | **自己的**（repo owner） |
| 編輯自己 config 是否越界 | — | 不（就像改自己的 `.bashrc`） |
| 分發對象 | marketplace 的不特定安裝者 | 作者本人的多機器 + 極少數手動跟隨者 |

**所以 sp 的 rule 2 對 ai-rules 不適用**——但 sp 的**問題意識**適用：如果 ai-rules 未來要分發給不特定 user（例如開源別人 install），就**必須**改成 plugin 模式（走各家 install mechanism），否則 install 腳本編輯別人全域 config 是越界。目前 ai-rules 還在「個人 repo」階段，`deploy_agents.py` 寫自己全域目錄是合理的；但要認知這是**分發模式的限制**，不是長期方案。

---

## 4. ai-rules 真正的 multi-harness 缺口（轉型後才浮現）

把鏡頭從「sp 借什麼」轉回「ai-rules 自己缺什麼」。以下是用 arch-thinking 結構機械（`rg` + 部署狀態查證）盤點的、`02` 寫作時不存在的缺口：

### 4.1 下游消費側的 Claude-only 壟斷

`deploy_agents.py` 只處理 **rules 的 bundle 部署**（source: `ai-development-guide.md` + `rules/<scope: neutral>` → target: 3 家 AGENTS.md）。但 ai-rules 還有兩大載體**完全沒跨 harness**：

| 載體 | 數量 | Claude 路徑 | 跨 harness? |
|------|------|------------|-------------|
| skills | 43 | `~/.claude/skills/` auto-load（SKILL.md 開放標準） | 🟡 部分 —— `.agents/skills/` 是 Codex+OpenCode 共讀路徑，但 `~/.zcode/skills/` 是 ZCode，**目前是否 deployed 未驗證** |
| commands | 30+ | `~/.claude/commands/` slash command | ❌ Claude-only —— ZCode/OpenCode/Codex 各自路徑不同，且 Codex 已棄用 custom-prompts → skills（見 `cross-harness-commands-skills-deployment.md`） |

`cross-harness-commands-skills-deployment.md` 已指出 commands 路徑家家分歧、無共用路徑。但**那篇是設計提案**（「待決策，非實作」），`deploy_agents.py` 只解了 rules 的 bundle，skills/commands 的跨 harness 部署**還在設計階段未落地**。

### 4.2各家 AGENTS.md 載入語意差異未驗證

「寫到 `~/.zcode/AGENTS.md`」假設了一個前提：各家對 AGENTS.md 的**載入語意等價**。但這未經 marker test 驗證：

- **`@`-include 語意**：CLAUDE.md 的 `@path` 是 Claude Code 專用展開；AGENTS.md 的 `@` 語意各家不同（有的展開、有的當 hint）。bundle 內若殘留 `@`-notation 會在某些 harness 斷裂。`rules/instruction-writing.md` 警告了這點，但 `deploy_agents.py` **沒有機械檢查 bundle 是否含殘留 `@`**。
- **frontmatter 消費**：bundle 保留每個 rule 的 `---\nharness-scope: neutral\n---` frontmatter。各家是否（a）忽略（理想）、（b）誤消費為指令、（c）洩漏給 model 當噪音——未驗證。
- **auto-load 等價性**：Claude 的 `~/.claude/rules/*.md` auto-load 是逐檔載入；bundle 是**單一巨大 AGENTS.md**。兩者對 model context 的**注意力分配**不同（單檔 80KB+ vs 多檔分散），可能影響 rule 被讀到的優先序——這是 LLM 行為層差異，純檔案部署驗不出來。

### 4.3 缺 acceptance test（sp 有、ai-rules 沒有的最關鍵一塊）

sp 的 multi-harness 「Definition of Done」（`docs/porting-to-a-new-harness.md` Part 3）核心是 **acceptance test**：clean session 問 model「describe your superpowers」，marker 沒到 = 沒載入。這是 sp 防「bootstrap 靜默失敗」的唯一機械保證。

ai-rules 的 multi-harness **完全沒有對等驗證**：
- `deploy_agents.py` 的成功條件 = 檔案寫到磁碟（`[OK] deployed to N/3`）
- 沒有「在 ZCode 開 clean session 問 model『你有讀到 must-execute-before-complete 嗎』」這類 read-back
- 沒有 marker test 證明 bundle 真的進了 model context

這是 **ai-rules 多 harness 最該補的缺口**——不是補 sp 的機制（bootstrap/adapter），是補 sp 的**驗證哲學**：「宣稱跨 harness 可攜，就要有證據證明 harness 真的讀到且讀對」。

---

## 5. 可借鑒清單（只取「問題意識」與「驗證手法」，不借機制）

基於 §2 的問題分類與 §4 的缺口盤點，重新檢驗 `02` 的「不借結構類」——**結論不變，但理由可以精確化**：

| 借鑒 | 來源 sp 概念 | ai-rules 落點 | 衝突 | 與 `02` 關係 |
|------|-------------|--------------|------|-------------|
| **marker test 驗證手法** | sp 的 unique-marker test（`docs/porting-to-a-new-harness.md` Part 4 Step 3） | `deploy_agents.py` 加 `--verify`：deploy 後在每家 harness 跑 marker query 證明 bundle 進 context；或寫進 `scripts/` 當獨立驗證腳本 | 無 | **強化 `02`** —— `02` 說「不借 bootstrap」，但沒說「借 bootstrap 的驗證手法」；這填補 §4.3 缺口 |
| **bundle 殘留 `@` lint** | sp 的「Shape C `@`-include 不展開就 inline」問題意識 | `deploy_agents.py` 加檢查：bundle 不得含 `@path`（除合法 markdown link）；含 `@`-include 警告 | 無 | **填補 §4.2** —— 語意斷裂的機械預防 |
| **雙軌 read-back diff** | sp 的 Pi dual-maintenance 警告（`.pi/CLAUDE.md:49-53`） | 寫腳本比對 Claude 端（guide + rules/ neutral）與 non-Claude bundle 的**語意等價性**（rule-by-rule diff，非全文 diff——bundle 有 slim） | 無 | **填補 §4.1 #5** —— 雙軌 drift 的機械偵測 |
| **「不借」的精確理由** | — | 更新 `02`：bootstrap/tool-mapping 不是「scope 邊界」不借，是「**解的問題對宣告式 rule 不存在**」不借 | 無 | **修正 `02` 論證**（見 §2.2） |

### 不借的（確認 `02` 仍成立）

| sp 機制 | 為何仍不借（轉型後不變） |
|--------|------------------------|
| **session-start bootstrap injector** | 解「source 不會 auto-load」問題；ai-rules 的 neutral rules 走 AGENTS.md 慣例 auto-load，問題不存在（§2.2 #1） |
| **per-harness tool mapping** | 解「動作詞彙要翻譯」問題；ai-rules 是宣告式 rule 無動作詞彙（§2.2 #2） |
| **per-harness plugin manifest + marketplace** | 解「給不特定 user 分發」問題；ai-rules 是個人 repo（§3），未來若開源再評估 |
| **drill eval harness（LLM verifier）** | `02` 已決不借（B 軸人類 viewport 提示 eval 該人機混合） |

---

## 6. 決策建議（給「現在要不要動」的答案）

**短期（驗證補強，低門檻高 ROI）**：
- 補 §4.3 的 marker test：在 ZCode / OpenCode 各開一個 clean session，問 model 是否讀到特定 rule（如 must-execute-before-complete 的關鍵句），手動跑一次確認 bundle 真的進 context。這是 sp acceptance test 的精神，不是機制。1-2 次手動驗證即可建立信心。
- 補 §4.2 的 bundle `@` lint：`deploy_agents.py` 加一行檢查（bundle 內 `@`-include 計數 > 預期就警告）。純防禦，無副作用。

**中期（缺口落地，需設計）**：
- §4.1 的 skills/commands 跨 harness 部署：`cross-harness-commands-skills-deployment.md` 已是設計提案，決策後落實。重心是 `.agents/skills/` 共讀路徑（Codex+OpenCode 最大槓桿）+ ZCode 的 skills 路徑驗證。
- §4.1 #5 的雙軌 diff 腳本：寫 `scripts/verify_bundle_parity.py`，比對 Claude 端 rules/ 與 bundle 的 rule-by-rule 語意等價。

**不建議**：
- 引進 sp 的 bootstrap / adapter / plugin 機制——解的問題 ai-rules 不存在（§2.2），借了是空殼，且與 on-demand 省 context 哲學衝突（`02` 已決）。
- 為了「像 sp 一樣 multi-harness」而把 rules 改成指令性動作——這會破壞 ai-rules 的宣告式約束本質，是**為了借機制而改變內容性質**，本末倒置。

---

## 7. ZCode 權限模型實測（2026-07-05）

> **位置說明**：本節是 AGENTS.md `hooks/` 條目的實測證據源（AGENTS.md = 索引、本節 = 詳細實測），為任務過程的副產品，與 §1-6 sp 機制對照無直接關係。

### 結論

ZCode 3.2.5（build 2316）**沒有等價於 Claude `permissions.allow` 的宣告式白名單**。「自動編輯」GUI 模式只放行 Write/Edit，Bash 一律彈窗；唯一可程式化的 PermissionRequest hook 在 3.2.5 binary **未被實作**。ai-rules 場景（純文檔 + 唯讀查詢為主）採用「完全訪問」(yolo) GUI 模式 + 人工把關。

### 跨 harness 權限模型差異

| 機制 | Claude Code | ZCode 3.2.5 |
|------|-------------|-------------|
| **宣告式白名單** | `~/.claude/settings.json` 的 `permissions.allow`（125+ 條 `Bash(...)` glob 規則） | **無** |
| **GUI 模式** | `defaultMode`: `auto` / `plan` / `acceptEdits` 等 | 5 種：默認 / 變更前確認 / **自動編輯** / 計劃 / **完全訪問**（GUI 選單，非 config） |
| **per-operation 記憶** | runtime 累積進 `permissions.allow` | 「始終允許本項目」存 SQLite `local_setting` table（`ruleContent` = **完整命令字串精確匹配**，非 glob） |
| **可程式化 hook** | 無需（宣告式已足夠） | **PermissionRequest hook 在 3.2.5 不支援**（見下方 issue） |

### configuration-file hooks 不支援（官方確認）

`diagnosing-hooks` skill 描述的 spec（`~/.zcode/cli/config.json` top-level `hooks.events.<Event>`）在 ZCode 3.2.5 binary **未被實作**：

- 實測：加 `hooks.enabled: true` + 正確 schema + 重啟 → log 全天 `hook.*` 事件 = 0
- 官方 issue：[`zai-org/feedback#32`](https://github.com/zai-org/feedback/issues/32)「Native ZCode Agent does not trigger hooks configured in ~/.zcode/cli/config.json」— 開於 2026-06-22，priority **P2 open**，作者連 plugin hooks 也測過同樣無效，**官方至今無回覆**
- 相關 issue：[`#42`](https://github.com/zai-org/feedback/issues/42)「權限選項增加 Auto review」（用戶要求 Agent 自判放行）、[`#18`](https://github.com/zai-org/feedback/issues/18)「是否有 hooks 机制」、[`#44`](https://github.com/zai-org/feedback/issues/44)「PreToolUse hook 支持改写工具输入」

### 決策

對 ai-rules 場景（純文檔 repo、大量唯讀查詢、無生產數據）採 **yolo GUI 模式 + 人工把關**：
- 破壞性操作（rm/git push/git reset --hard/sudo）由 AI 主動揭露 + 用戶人工確認，不靠 GUI 彈窗
- 此決策只在 ai-rules 場景成立；mosaic 量化交易 repo 不適用（會動到回測數據、DB、生產配置）

### 跨 harness 對照啟示

1. **`diagnosing-hooks` skill 是 spec 不是 binary**：未來用 skill 文檔設計時必須實測驗證，不能假設文檔與 binary 一致（acceptance-evidence L4+ 精神 — 文檔宣稱不算證據）
2. **跨 harness 對照需附版本**：「ZCode 支援 hooks」這句話在 3.2.5 為假，未來版本可能成真 — 紀錄時附 `CFBundleShortVersionString` 才準確
3. **若未來要用 hook**：等 #32 修復，或包成 marketplace plugin（但 #32 作者測試 plugin hooks 也無效，未必可行）

> **§7 資料來源**：`ref-docs/harness/zcode/cn/docs/safety-confirm.md:36,50`、`~/.claude/settings.json` permissions 區塊、`~/.zcode/cli/log/zcode-2026-07-{04,05}.jsonl`（全天 `hook.*` 計數=0；`tool.permission.resolved` 98 個事件 context 只有 `decision`/`mode`/`reason` 等 GUI 模式決策欄位，**無 ruleId 等 rule-based 白名單欄位**）、`~/.zcode/cli/db/db.sqlite` `local_setting` table schema、`zai-org/feedback` issues #18/#32/#42/#44、`/Applications/ZCode.app/Contents/Info.plist` CFBundleShortVersionString=3.2.5 build 2316。

---

## 附錄：與既有報告的關係

| 報告 | 與本檔關係 |
|------|-----------|
| [`README.md`](README.md) | 決策摘要；本檔補強 `02` 的「不借結構類」論證，§7 補 ZCode 3.2.5 權限模型實測（README 同步） |
| [`01`](01-結構理解與診斷.md) | sp 三層全貌；本檔 §1.2 引用其 1.1 三層架構，補「為什麼必須三層」的內容性質論證 |
| [`02`](02-sp借鑒到ai-rules.md) | **本檔直接接續**——轉型後回頭檢驗其「不借結構類」；結論不變但理由精確化（§2.2），並補 `02` 寫作時不存在的下游缺口（§4） |
| [`03`](03-OpenCode退路.md) | OpenCode 退路；本檔 §4.2 的 `@`-include 語意差異是其「CC 相容 fallback」的延伸驗證點 |
| [`cross-harness-commands-skills-deployment.md`](../cross-harness-commands-skills-deployment.md) | commands/skills 跨 harness 設計提案；本檔 §4.1 引用其「家家分歧」結論，指出 `deploy_agents.py` 只解了 rules 沒解 skills/commands |

> **§1-6 資料來源**：superpowers fork checkout（`~/Github/superpowers`）實讀——`docs/porting-to-a-new-harness.md`（Part 1-8 + Appendix）、`hooks/session-start`、`hooks/hooks.json`、各家 `plugin.json`/`marketplace.json`、`skills/using-superpowers/SKILL.md` + `references/*.md`；ai-rules 側——`scripts/deploy_agents.py`、`rules/*.md` frontmatter、`~/.{zcode,config/opencode,codex,claude}/` 部署狀態實證、git log `431a1d9`→`077753c`。
