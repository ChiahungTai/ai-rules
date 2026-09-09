# EP：跨池記憶主體遷移——muse project memory 一等公民（AIR-54）

> **ep_type**: implementation
> baseline: 48d0590

## 實作總覽

把 ai-rules 記憶池主體從 CC 私有路徑（`~/.claude/projects/-Users-ctai-Github-ai-rules/memory/`）遷到 repo 內 muse project memory 合約路徑（`<repo>/.agents/memory/`），CC 端原路徑換目錄 symlink 透明讀寫、ZCode 既有鏈雙跳、muse 原生 scope 零適配讀。寫入流：muse `add_memory`/`edit_memory` 被 PreToolUse hook 攔截代存 inbox，CC/ZCode 側 consolidation（補 frontmatter＋六問）後入池。mosaic 同形態移植。

**驅動**：muse 是可預見未來 CP 最高的 runtime——架構讓主力零適配（主體=muse 原生 scope），CC/ZCode 經最穩定的 POSIX symlink 透明語義。09-09 實驗鏈已把核心技術未知數全部消滅（注入/deny 契約/裸寫行為/symlink 拒絕全實測）。

## UC 盤點

### Backlog 關聯

- **AIR-54**（本卡，To Do）——EP 追蹤卡
- **AIR-52**（To Do）——S4 段「memory B 形態跟進」改 23:40 cron prompt 口徑；本弧 S2 會改同一 cron 的 `git -C <pool>` 路徑——**動作面重疊登記**：兩弧各改各的欄位，先落地者贏，後者 rebase 對帳。**追加共檔面（review F8）**：AIR-52 S2 動 `ai-analysis/schedule-registry.md` 與本弧 S2 的池路徑改動同檔
- **AIR-50**（To Do）——S9「memory-audit 統一定義表補 wrapper 誤置條目」與本弧 S4 同編 `skills/memory-audit/SKILL.md`（review F8）——AIR-50 先動（排序在前），本弧 S4 後動對帳
- **AIR-48**（In Progress，P4 dogfood）——本弧 S3 品質閘引用其三判準（純機械/單入口/無語義例外）；平行推進（user 09-09 拍板）
- **draft-2**（muse-grok telemetry 探測）——探測目標已被 09-09 實驗完成（session.jsonl 即記錄面）；歸因前提（「muse 不用自家 memory」）被本弧翻轉——本弧 S5 標記 draft-2 探測完成＋註記前提變更，接線部分留 draft
- **draft-3 / AIR-53**（muse bundle 治理）——正交（rules lane 64KiB），無動作

### SYSTEM-MAP 影響

無 SYSTEM-MAP.md（元專案，正當跳過）。

### 掃描範圍

- `AGENTS.md`（觀察池路由段、「Muse memory 唯讀」段）
- `skills/memory-audit/SKILL.md`＋`skills/memory-audit/scripts/generate_index.py`（generator 資產源）
- `hooks/block-memory-index-write.py`（CC 池寫入閘，邏輯移植參考）
- `rules/context-management.md`（memory 生命週期 pointer）
- `~/.agents/memory-spine/index.md`（認養表 muse 腿）
- `skills/corrections-weekly/SKILL.md`（`--pool` 實體路徑示例——review F7 補列）＋`ai-analysis/schedule-registry.md`（池路徑×2 處——F7；夜波 scope 定義源）
- memory 條目：`project_muse-memory-mechanism-divergence`（pending 收斂）、`reference_muse-code-cli-facts`（09-09 已更新）、`project_memory-cc-alignment-diagnosis-0905`（symlink 拓撲段）

### 同主題 memory 條目（結案蒸餾範圍）

- `project_muse-memory-mechanism-divergence`——「要用先重設計」pending 由本弧實現，結案蒸餾為終態
- `reference_muse-code-cli-facts`——09-09 已吸收實驗事實（hooks 契約/add_memory/symlink 拒絕），隨弧補搬遷後形態；已超 12K，本弧結案蒸餾時收斂
- `project_memory-cc-alignment-diagnosis-0905`——symlink 拓撲段隨 S5 更新（CC 端目錄 symlink 新形態）

### 既有 UC 狀態

| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| auto-memory 池治理（generator/hook/audit/夜間波） | ✅ | memory-audit skill | 更新 | 池路徑變更，治理資產隨主體搬遷＋路徑同步 |
| muse 唯讀掛載 | ✅ | AGENTS.md | 更新 | 升級為受約束寫入者（inbox 流） |
| copy 投影腿（09-09 POC） | 🟢 | .agent-tmp/poc_muse_projection.py | 退役 | 主體遷入後投影目錄被主體取代 |

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 跨池共享記憶主體（CC/ZCode/muse 三端等距「讀」；寫＝CC/ZCode 直寫、muse 經 inbox 收斂——SM-14） | 📋 | `<repo>/.agents/memory/`＋CC 目錄 symlink＋muse hooks inbox |
| muse 寫入流（inbox→consolidation→池） | 📋 | `.muse/hooks.json`＋`hooks/muse_memory_inbox.py`＋夜間波 inbox 步驟 |

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | CC session 開場 | 新 CC session 於 ai-rules | 經 symlink 載入主體 MEMORY.md 索引如常（B 形態常駐面） | 池 git restore＋移除 symlink | 三端主體 |
| SM-2 | ZCode session 開場 | 新 ZCode session | 雙跳 symlink 讀到同 inode 內容 | 同上 | 三端主體 |
| SM-3 | muse task 開場 | bridge task / 互動 session | project scope 注入 MEMORY.md 全文＋清單（已實測形態） | — | 三端主體 |
| SM-4 | muse 想寫記憶 | add_memory/edit_memory 呼叫 | PreToolUse hook 攔截：content 代存 inbox，deny reason 告知已存位置 | 清 inbox | muse 寫入流 |
| SM-5 | bridge headless task 寫記憶 | 同上 | 同 SM-4——**bridge task 實測 trusted（user-config）且 hook 生效**（第三輪攔截實證：session 01a08405 `tool blocked by hook`）；真實缺口＝未 trust 的 workspace（新 clone）headless task 不載 hooks——工單紀律兜底 | 同上 | muse 寫入流 |
| SM-6 | consolidation | 夜間波 / 手動 | inbox 逐條六問→補 frontmatter→寫主體→regen→清 inbox | — | muse 寫入流 |
| SM-7 | 夜間收斂波 | 23:40 cron | `git -C <主體新路徑>` 波程序正常（marker/baseline/差異歸屬） | marker 留存程序 | 池治理 |
| SM-8 | 池 gate FAIL | 條目違規/超限 | generator 照寫出＋fail-loud（AIR-27 語義不變） | — | 池治理 |
| SM-9 | hook 腳本故障 | inbox hook 崩潰 | fail-open：muse 直寫主體（退回無閘狀態，非資料遺失）；夜波掃尾收斂 | 修 hook | muse 寫入流 |
| SM-10 | muse 升版 | binary 更新 | project scope 合約路徑（repo 內）不受影響；注入機制若變＝probe 偵測（開場 snapshot 自查） | — | 三端主體 |
| SM-11 | 手術回滾 | S1 驗證失敗 | 無遷移後寫入：`rm symlink＋mv 回去`；已有寫入：**差異歸屬**（池 git diff/status 逐檔確認，禁整體 restore——波次 marker 同思路）；S2 已改 cron 則回滾含 cron 還原（否則夜波指向退役路徑靜默失效） | — | 全部 |
| SM-12 | mosaic 多 worktree | mosaic 移植 | owning 線（main worktree）放實體；其餘 worktree 的 `.agents/memory/` 與 CC project dir memory 皆 symlink 指實體；**次 worktree muse 腿視目錄層 symlink 實測結果（F2）** | — | mosaic 移植 |
| SM-13 | codex 第四端讀取 | codex session 檢索池 | 檔案級 Read 穿透如常；**目錄級 rg/glob 遍歷行為改變**（rg 預設不跟目錄 symlink）——AGENTS.md 觀察池路由段補 `-L` 或直指主體路徑指引 | — | 三端主體 |
| SM-14 | muse 寫後讀 lag | muse 寫 inbox→同日再讀 | **非即時**：deny reason 告知位置，池要等 consolidation——設計使然（UC 措辭＝三端等距「讀」、寫經 inbox 收斂非等距） | — | muse 寫入流 |

## 段落 0：全域研究摘要（09-09 實驗鏈先驗）

**可複用基礎設施**：
- `.agent-tmp/poc_muse_projection.py`——copy 投影腳本（搬遷程序參考；過渡形態）
- `skills/memory-audit/scripts/generate_index.py`——B 形態 generator（ASSET_SOURCE `__file__`-relative byte 比對——隨主體搬遷後相對結構不變）
- `hooks/block-memory-index-write.py`——CC 寫入閘（deny 邏輯移植 muse hooks 參考）
- `.agent-tmp/muse-hooks-findings.md`——deny 契約＋實驗矩陣＋能力面（stdin tool_name/tool_input、updatedInput、additionalContext）

**依賴關係**：
- 池 git（AIR-49 local repo）——.git 隨主體搬遷，歷史連續
- B 形態（AIR-48 P3）——`_resident-set.md` 凍結 12 條；主體遷移不改投影語義
- 夜間收斂 cron（AIR-52 S4 互動——見 UC 盤點）
- ZCode memory symlink（既有鏈 `~/.zcode/cli/memories/.../memory → CC projects/<encoded>/memory`）——CC 端換 symlink 後自動雙跳

**風險假設清單**（等級｜狀態）：
1. muse project scope 注入機制——**已驗**（14 檔 copy 投影實測：MEMORY.md 全文＋清單 13 檔）
2. hooks deny 契約——**已驗**（hookSpecificOutput/permissionDecisionReason，擋 add_memory 實證；bridge task trusted 下生效）
3. muse memory 拒 symlink——**已驗**（read_memory 報錯）——主體必須實體檔
4. add_memory 裸寫零 frontmatter——**已驗**——inbox 流的必要性依據
5. CC 原生載入器對自身 memory 目錄為 symlink——未直接驗（**中**）：ZCode 目錄 symlink 是既有在用形態（本弧規劃 session 活證）、mosaic 三 dir 共指同 inode 既有；CC 載入器不同實作但 POSIX 語義透明——S1 程序內建（側備份＋rmdir 併發 guard＋即時三端驗證＋回滾），不做獨立先驗段
6. generator/hook 於新路徑執行——低（review F14 源碼核實）：generator 無資產比對（glob 自身目錄、路徑無關）；byte 比對在 repo 端 `hooks/memory-index-regen.py`（`__file__`-relative 指回 repo skills/，與池位置正交）；部署副本 cp -a 後 byte 不變——S1 後真 session 覆蓋
7. muse 注入清單 48 檔截斷規則（主體 142 條時截哪些；`_` 前綴治理檔排前）——未驗（中）→ S1 後實測記錄；治理檔收子目錄為緩解選項（muse 是否掃子目錄未知，實測）
8. muse 對 project scope 的 add_memory 行為——未驗（中；personal_project 已驗，機制應同）→ S3 實測

## 段落劃分原則

依賴序：S1（手術，程序內建先驗與回滾——review 定案砍除獨立 S0：CC 載入器無乾淨測試介面，S0 空轉〔F14/F16〕）→ S2（路徑同步）→ S3（muse 閘+inbox）→ S4（consolidation，**需 S2 後**——同檔面：23:40 cron prompt 與 memory-audit SKILL.md 兩處〔F6〕）→ S5（文檔）→ S6（mosaic）。S3 可與 S2 平行（無檔案重疊，已驗）；S6 獨立可後延。語義約束：主體路徑常數 `AGENT_MEM=/Users/ctai/Github/ai-rules/.agents/memory`、inbox＝`$AGENT_MEM-inbox/`（hook 腳本內以 `dirname $0` 推導絕對路徑，**不依賴 cwd**〔F3——bridge task cwd 未契約保證〕）；CC 端介面路徑 `CC_MEM=~/.claude/projects/-Users-ctai-Github-ai-rules/memory`（不變——它是 symlink）。

---

## S1：主體搬遷手術（ai-rules）

### Context
UC 引用：實作「跨池共享記憶主體」。依賴：無前置段（先驗內建本段程序）。語義約束：AGENT_MEM 主體、CC_MEM 為 symlink 介面（語義不變）、`$POOL.bak` 側備份路徑＝`~/.claude/projects/-Users-ctai-Github-ai-rules/memory.bak`。

### 核心實作要點
0. **時序防護（F11）**：手術避開 23:40±30min 夜波窗口；開工前確認無活躍 memory writer（並發偵測兜底＝rmdir guard，見下）
1. **側置備份（F1）**：`cp -a $POOL $POOL.bak`（mtime 保留——rank mtime 排序防護）；`_trash-0908/` 與 `_decay-candidates.*` 不隨遷——mv 進 `$POOL.bak`（muse 可見面清潔〔F15〕）
2. 清空過渡投影：`rm -rf $AGENT_MEM`（14 檔 copy——主體即將進駐）
3. `mv $POOL/. $AGENT_MEM/`（含隱藏檔；池目錄清空）
4. **併發 guard**：`rmdir $POOL`——非空＝mv 後有新寫入（並發 session）→ **停手**：將新檔 mv 進主體後重試 rmdir；連續兩次失敗→中止手術回報
5. `ln -s $AGENT_MEM $POOL`
6. ZCode 端不動（既有 symlink 經 CC_MEM 雙跳）——驗 `readlink -f` 到 AGENT_MEM
7. `.gitignore` 補 `.agents/memory/`＋`.agents/memory-inbox/`
8. **三端讀驗證**：CC 新 session 開場、ZCode 新 session 開場、muse bridge task `read_memory(scope=project, path=MEMORY.md)`
9. generator regen：`python3 $AGENT_MEM/_generate_index.py --check`
10. **驗證全綠後**才刪 `$POOL.bak`（快照生命週期顯式化）

### Pseudo Code
```
POOL=~/.claude/projects/-Users-ctai-Github-ai-rules/memory
AGENT_MEM=$PWD/.agents/memory
# 時序檢查：date '+%H%M' 避開 2320-2410；不然中止
cp -a "$POOL" "$POOL.bak"                        # 側備份（驗證全綠後刪）
mv "$POOL/_trash-0908" "$POOL/_decay-candidates."* "$POOL.bak/" 2>/dev/null || true
rm -rf "$AGENT_MEM"                              # 過渡投影退役
mkdir -p "$AGENT_MEM"
mv "$POOL/." "$AGENT_MEM/"                       # 池清空（含 .git/.隱藏檔）
rmdir "$POOL" || { echo "CONCURRENT-WRITE: $(ls -A "$POOL")"; exit 1; }  # 併發 guard
ln -s "$AGENT_MEM" "$POOL"
printf '.agents/memory/\n.agents/memory-inbox/\n' >> .gitignore
# 驗證：三端開場＋--check＋readlink -f
# 全綠 → rm -rf "$POOL.bak"
```

### 驗證策略
- SM-1/2/3（三端開場）；`--check` PASS；`ls -la $CC_MEM` 顯示 symlink；inode 一致（`stat`）
- **回滾（F9 強化）**：S1 驗證失敗且尚未有遷移後寫入→`rm $POOL && mv $AGENT_MEM/. $POOL/ && rmdir $AGENT_MEM`；已有遷移後寫入→**禁整體 restore**——列 `git -C $AGENT_MEM diff <snapshot HEAD> --stat`＋`status --porcelain` 差異歸屬（波次 marker 同思路），逐檔確認後才還原；若 S2 已改 cron 路徑→回滾含 cron 還原（否則隔晚夜波指向已退役路徑靜默失效）
- **48 截斷實測**（風險 7）：muse task 開場回報清單內容——記錄截斷形態；若治理檔灌滿清單→緩解＝治理檔收 `_governance/` 子目錄（先實測 muse 掃不掃子目錄）

---

## S2：治理路徑同步

### Context
UC 引用：更新「auto-memory 池治理」。依賴：S1。語義約束：**CC_MEM 路徑是 harness 介面——出現在 transcript/telemetry 的路徑不變**；要改的是「治理工具 hardcode 池實體路徑」處。

### 核心實作要點
1. **機械盤點**：`rg -l 'projects/-Users-ctai-Github-ai-rules' <repo> ~/.zcode/cli/config.json ~/.claude/settings.json`＋夜間 cron 定義（CronList）＋ZCode hook config——分類：介面路徑（留）vs 實體路徑依賴（改指 AGENT_MEM）
2. 夜間 23:40 cron prompt 的 `git -C <pool>` → AGENT_MEM（AIR-52 互動：只改路徑欄，口徑欄歸 AIR-52）
3. Stop hook regen：hook 以記憶目錄內 generator 為準（`__file__`-relative）——驗證即可，預期零改
4. telemetry：CC 側路徑模式不變（Read 事件路徑＝CC_MEM）——零改，記錄理由
5. memory-audit skill 文檔內路徑示例同步

### Pseudo Code
盤點清單表（路徑→分類→動作），全綠後 `rg '<舊實體路徑字串>' --hidden` 掃 config/cron/skill 零殘留（介面路徑除外，附列舉）。

### 驗證策略
- 夜間波手動觸發一次（或等當晚）——波程序完整跑（marker/baseline/差異歸屬在 AGENT_MEM 上運作）
- rg 殘留掃描輸出附報告

---

## S3：muse hooks 品質閘＋inbox 流

### Context
UC 引用：實作「muse 寫入流」。依賴：S1。基礎設施：`hooks/`（跨 harness 單一源慣例）、`block-memory-index-write.py`（判準參考）、muse-hooks-findings.md（契約）。語義約束：AIR-48 三判準——本閘為**純機械導流**（攔截＋代存），語義判斷（六問/frontmatter 補全）全留 consolidation 站，閘不做語義。

### 核心實作要點
1. `hooks/muse_memory_inbox.sh`（或 .py）：讀 stdin JSON（`tool_input.content/path/scope`）→ 落 `${AGENT_MEM}-inbox/<YYYYMMDD-HHMMSS>-<path basename>`（**frontmatter 補 name stub＋raw content 原樣保存**——只加最小 provenance 標頭，語義修補留 consolidation）→ stdout 輸出 deny JSON（permissionDecisionReason＝「已代存 inbox：<檔名>；將由 consolidation 站處理入池」）
2. `.muse/hooks.json`：PreToolUse matcher `add_memory|edit_memory` → 上述腳本（絕對路徑）
3. **fail-open 約束**：腳本故障＝閘開（muse 直寫主體）——腳本保持極簡（無網路、無外部依賴、`set -euo pipefail`）；edit_memory 的 deny 會擋合法編輯嗎？——**第一版全導流**（user「先 inbox 看看」），觀察誤傷率後再議 allowlist
4. muse 對 project scope add_memory 實測（風險 8）：確認導流前路徑行為
5. hooks.json 進 repo（版控）——gitignore 排除 inbox 不排除 hooks.json

### Pseudo Code（hook 腳本核心——F3/F13 修正版）
```bash
#!/usr/bin/env bash
set -euo pipefail
REPO=$(cd "$(dirname "$0")/.." && pwd)     # 腳本在 <repo>/hooks/——絕對路徑推導，不依賴 cwd
INBOX="$REPO/.agents/memory-inbox"
IN=$(cat)                                  # stdin: {tool_name, tool_input:{scope,path,content}}
TS=$(date +%Y%m%d-%H%M%S)
BASE=$(echo "$IN" | jq -r '.tool_input.path // "unnamed" | split("/") | last')
OUT="$INBOX/${TS}-$$-${BASE}.md"           # $$ 防同秒互吞；path 缺席 fallback
mkdir -p "$INBOX"
{ echo "---"; echo "muse-inbox: ${TS} pid=$$"; echo "---"
  echo '```json'; echo "$IN"; echo '```'    # 完整 stdin 原樣保存——scope/path provenance（F13c）
} > "$OUT"
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"已代存 inbox: %s（consolidation 站將處理入池）"}}' "$OUT"
```
（consolidation 站從 stdin JSON 區塊取 content 與完整 path——edit_memory 的「對條目 X 的編輯」可重建）

### 驗證策略
- SM-4/5：muse task 呼叫 add_memory → deny reason 含 inbox 路徑＋inbox 檔落地（content 原樣）
- SM-9：腳本故障模擬（PATH 砍 jq）→ fail-open 行為記錄（muse 直寫主體——確認非資料遺失形態）
- 邊界：content 含 frontmatter 樣態、path 含子目錄、空 content

---

## S4：consolidation 站

### Context
UC 引用：完成「muse 寫入流」。依賴：S3。語義約束：寫入六問單一源＝memory-audit skill（不重述）；consolidation 是 LLM 面非機械面。

### 核心實作要點
1. **掛點**：夜間收斂波第一步（波前二分之後）加 inbox 掃描段＋memory-audit skill 補「inbox 消費」小節（手動觸發路徑：本 skill session）——**S4 需在 S2 後執行**（兩處同檔面：23:40 cron prompt、SKILL.md——F6）
2. 流程：inbox 非空 → 逐檔讀（stdin JSON 區塊取 content/path/scope）→ 六問 → 合格：補/修 frontmatter（name/description/type，desc 文法五條）→ 寫主體條目 → regen；不合格（任務終態/repo 可推導/未定案）：記錄去卡或棄置理由 → 刪 inbox 檔
3. cron prompt 補一行 inbox 步驟（與 AIR-52 S4 同檔互動——已登記）
4. **逾期 inbox 語義（F5 修正）**：夜掃三 dot-area（`.agent-tmp`/`.at-contexts`/`.review`）**不含** `.agents/`——逾期 inbox **不被靜默清**，它是 consolidation 停擺的警訊（波次報告列 prominent；連續兩晚逾期→升級處置，比照 marker 停波邏輯）

### Pseudo Code
流程文檔形態（LLM 步驟，非腳本）；夜波 prompt 增量。

### 驗證策略
- SM-6：人工放測試 inbox 條目（合格/不合格各一）→ 跑 consolidation → 池條目落地＋regen＋inbox 清空；不合格者有去處記錄

---

## S5：過渡投影退役＋文檔/條目同步

### Context
UC 引用：更新「muse 唯讀掛載」→「受約束寫入者」。依賴：S1-S4 全綠。注：投影退役已提前併 S1 步驟 2（主體進駐即退役）；本段收尾文檔面。

### 核心實作要點
1. `AGENTS.md`：「Muse memory 唯讀」段改寫——muse 讀主體（read_memory project scope／read_file）＋寫經 inbox（hook 導流）＋禁止直寫條目與索引（品質閘承載）；「觀察池路由」段補新路徑事實
2. memory 條目：divergence 條目收斂（pending 已實現）；cc-alignment 條目 symlink 拓撲段補「CC 端目錄 symlink→repo 內主體」新形態
3. `~/.agents/memory-spine/index.md` 認養表：muse 腿註記「池主體直連（AIR-54）」；ZCode registry 待辦腿維持（後議，不擴 scope）
4. draft-2 標記：探測完成（session.jsonl）＋歸因前提變更註記
5. `.agent-tmp/poc_muse_projection.py`＋`muse-hooks-findings.md`：吸收進 EP 後由夜掃清理（POC 生命週期慣例）

### 驗證策略
- docs mode 驗證：rg 舊敘述殘留（「唯讀」字樣對 muse 段落）零誤引；跨檔路徑一致（AGENTS.md vs skill vs spine index）

---

## S6：mosaic 移植

### Context
UC 引用：橫展「跨池共享記憶主體」。依賴：S1-S5 定型（ai-rules 為模板）。獨立可後延。

### 核心實作要點
1. mosaic 池主體 → mosaic repo（owning 線 main worktree）`.agents/memory/`；mosaic `.gitignore`
2. mosaic 的 CC project dir（多個，多 worktree 對應）memory 逐一換 symlink 指實體
3. 其餘 worktree 的 `.agents/memory/` → symlink 指 main worktree 實體——**F2 未驗點**：muse 拒檔案層 symlink 已實證，**目錄層**拒絕與否未驗；S6 第一步先實測（次 worktree 開 muse task read_memory 經目錄 symlink）。若目錄層也拒→**顯性降級**：muse 僅在 owning worktree 一等，次 worktree 的 muse 讀池走 read_file 絕對路徑（已驗穿透）＋AGENTS.md 註明
4. mosaic 側 hooks.json＋AGENTS.md 同步（參數化移植）
5. mosaic 夜間波/telemetry 路徑比照 S2

### 驗證策略
- SM-12：mosaic 三端開場＋worktree 間 inode 一致性；mosaic 夜波一輪

---

## 整合策略

- 順序閘：S1 三端驗證任一 fail → SM-11 回滾（差異歸屬程序）後修因再手術；CC 載入器拒 symlink（風險 5 成真）→ EP 回退決策點（回退 copy 投影形態，回報 user）
- S2 與 AIR-52 的 cron 同檔互動：先落地者贏、後者對帳（兩弧 UC 盤點互指已登記）
- S3 hooks.json 進版控（repo 資產）；inbox gitignore（durable 不入版控——**逾期 inbox＝consolidation 停擺警訊非垃圾，夜掃三 dot-area 不含 `.agents/`、不靜默清**〔F5 修正——原宣稱的夜掃規則不存在〕；S4 驗證含逾期模擬）
- baseline: 48d0590

## 收尾步驟

1. Capabilities/文檔：AGENTS.md 已於 S5；`skills/CLAUDE.md` 工作流索引檢查是否需補 memory 主體新路徑指引
2. 卡結案：AIR-54 兩步（`-s Done --final-summary` → `--ref` 換 done/ URL）＋弧結案蒸餾第三動（同主題 memory 條目三條——見 UC 盤點）
3. SYSTEM-MAP：不存在，跳過
4. instruction 檔同步檢查：`rules/context-management.md` pointer 面驗證（路徑語義未變則零改）
5. /audit-test：S3 hook 腳本若有可測邏輯（jq 解析/落檔）提煉最小測試；手術程序類段落以驗證報告代替

## EP Review 紀錄（09-09，獨立 context Explore agent＋主 session judge）

16 findings（6 P1＋10 P2）；judge：15 ✅ 採納、F4 ⚠️ 部分採納（review 引 findings 檔過時推導；實測第三輪攔截即在 bridge task 生效——修 findings 檔而非 EP SM-5，SM-5 補證據錨）。全數已 apply：

| # | finding（摘要） | 判決 | 落點 |
|---|------|------|------|
| F1 | S1 cp/rdir 互斥恆失敗 | ✅ | S1 重寫：mv＋側備份＋rmdir 併發 guard |
| F2 | S6 次 worktree 目錄 symlink vs muse 拒 symlink 未驗 | ✅ | S6 補目錄層實測＋顯性降級聲明；SM-12 |
| F3 | inbox 相對路徑＋hook cwd 未保證 | ✅ | S3 pseudo：dirname $0 絕對路徑推導 |
| F4 | 「bridge task trusted」與 findings 檔矛盾 | ⚠️ | findings 檔修正（實測反證舊記載）；SM-5 補 session 錨＋未 trust 缺口註 |
| F5 | 夜掃 `.agents/` 規則不存在 | ✅ | S4/整合策略改「逾期＝停擺警訊非垃圾」 |
| F6 | S4 與 S2 同檔面未登記 | ✅ | 依賴序改「S4 需 S2 後」 |
| F7 | 掃描範圍漏 corrections-weekly/schedule-registry | ✅ | UC 盤點掃描範圍補列 |
| F8 | 真實共檔面＝SKILL.md/schedule-registry | ✅ | UC 盤點補 AIR-50 S9／AIR-52 S2 共檔登記 |
| F9 | 回滾未涵蓋遷移後寫入與 cron 副作用 | ✅ | S1 驗證策略＋SM-11 差異歸屬＋cron 還原 |
| F10 | 缺 codex 第四端場景（rg 不跟目錄 symlink） | ✅ | 補 SM-13＋S5 路由段指引 |
| F11 | 缺並發/時序防護 | ✅ | S1 要點 0（避 23:40 窗口）＋rmdir guard |
| F12 | 寫後讀 lag 未顯性化 | ✅ | 補 SM-14＋UC 措辭校準（等距讀、寫收斂） |
| F13 | hook 腳本細部缺陷（覆蓋/null/provenance/stub drift） | ✅ | S3 pseudo 重寫（$$／fallback／stdin 全存） |
| F14 | ASSET_SOURCE 歸屬錯（比對在 regen hook 非 generator） | ✅ | 風險 6 重寫（源碼核實） |
| F15 | `_trash-0908` 隨遷灌爆清單 | ✅ | S1 要點 1（trash 進 .bak 不隨遷） |
| F16 | S0 對致命假設空轉 | ✅ | S0 段砍除（與 user 09-09 討論定案一致）；風險 5 降級中、S1 內建 |
