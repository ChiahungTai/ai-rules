---
name: kanban-board
description: backlog board（Backlog.md）機制單一源——命令合約、結案兩步、ref 規則、precheck；execution-plan/implement/metadata-sync 消費端引用此處
---

# kanban-board — backlog board（Backlog.md）機制單一源

> **繼承**: `@../CLAUDE.md`。UC-Driven 方法論見全局 guide。本 skill 是 **backlog board 的機制單一源**（命令合約、ref 規則、結案流程、UI 入口）——execution-plan／implement／metadata-sync 等消費端引用此處，不自帶定義。

## 定位

**board = view not container**：任務卡是 `backlog/` 下的 plain markdown（frontmatter＋段落標記），CLI 與 AI session 直接讀寫檔案，board 只是渲染層。`.kanban/` 四 lane 目錄制已退役（2026-09-02）——`mkdir .kanban/` 是錯誤動作。

## 初始化（repo 首次採用）

```bash
backlog init "<project>" --agent-instructions none
```

- `--agent-instructions none`：不注入 CRITICAL_INSTRUCTION 區塊（與本 repo AGENTS.md 治理／元資訊禁令衝突）
- config.yml 關鍵鍵：`statuses`（建議三欄 To Do/In Progress/Done）、`task_prefix`（repo 識別前綴，如 mosaic=`mos`、ai-rules=`air`）、`auto_commit: false`（外部 git 紀律——CLI 只改檔）

## 命令合約（消費端引用本段）

**建卡**（execution-plan UC 盤點）：
```bash
backlog task create "<標題>" -l <labels> -d <目標一句> [--ac "<驗收條件>"]
git add backlog/    # 建卡即 staged（autoCommit=false 下 CLI 不 commit）
```
**建卡 desc gate**（跨 session To Do 卡必過；session 內即辦豁免）：`desc` 須含三必有——①`baseline`（`〔baseline：<repo> <hash>〕`）②`已決策勿重辯`（`〔已決策勿重辯：①…〕`）③`驗收`（`〔驗收：…〕`）；語義在場即可，標記形式不限。軟自查：`rg -c "baseline|已決策|驗收" backlog/tasks/<卡>.md` 應 ≥3（豁免卡除外）。

**建卡前去重**（中）：`backlog search <關鍵詞>` + 查 `ai-analysis/_inbox/pending-decisions.md`（與同域 `open-items.md`；例：mosaic 側 `marking/open-items.md`）待處理段，命中則復用/連結既有指針，不重複承諾（一行指針 ≠ 承諾，`backlog` 卡 = 承諾）。

**開工——起手式五步**（凡要動某卡的 session——implement 階段 1 是標準入口；automation／監控／report 等衍生 session 不走 implement 亦同）：
```bash
# ① 第一動——平行 session 可見
backlog task edit <id> -s "In Progress"   # 🔴 必是動卡的第一個動作
# ② 讀卡三層：frontmatter → desc → notes → references
# ③ 讀卡知形態：references 有無 EP——承諾時已定（不重判）；scope 遠超 desc → 先升 EP 再動工
# ④ 新鮮度核對：desc baseline vs `git log --oneline <baseline>..HEAD` 非空→對照 desc 範圍；notes relay 宣稱→機械驗證當前狀態
# ⑤ 開工雙 ref
backlog task edit <id> --ref "<http URL>,<repo 相對路徑>"
```

**🔴 雙 ref 內建合約**：references 只對 http(s) 前綴渲染可點連結（`TaskDetailsModal.tsx:1362-1375`）——**相對路徑單獨出現＝board 上不可點＝錯誤形態**。兩值都要掛：
- `http URL`＝report server 上的 Report Shell／md preview 位址（**repo 慣例**——如 mosaic `http://127.0.0.1:6421/<wt>/<任務路徑>/index.html`；殼未建前的過渡形態指中央 md viewer `http://127.0.0.1:6421/viewer/_md-viewer.html?p=/<route>/<任務路徑>/ep.md`——**viewer 單一源**版控於 ai-rules `report-assets/`，`fetch(?p=)` 同源絕對路徑可渲染任一 route 的 md，raw `.md` 直連永遠是原檔；hook 1 建殼後更新為殼 URL）
- `repo 相對路徑`＝AI session／VSCode 消費形態

**結案兩步**（build 5a / post-build；URL 生命週期隨任務目錄遷 `done/` 變更）：
```bash
backlog task edit <id> -s Done --final-summary "<一句>"
backlog task edit <id> --ref "<done/ 新URL>,<相對路徑>"   # --ref 整組替換
```
**弧結案蒸餾（第三動，同時機）**：owning session 將本弧 project_/feedback_ memory 條目重寫為終態 facts——刪日期/session id/進度流水與 git 可推導內容，留決策教訓與終態結論，敘事指向 repo 檔案（EP/卡）；無相關條目明示無。規則細節＝[memory-audit](../memory-audit/SKILL.md)「寫入端紀律」（含 desc 三不）。

結案後**卡留 board Done 欄**（官方預設工作流——Done 欄可見＝完成工作可見）；`task complete <id>`（搬 `completed/`）是清場動作，延後到 board 清理批次（maintain 週期）或 user 指示，不隨結案當場執行。

**🔴 清理前跨線掃描**（凡 `task complete`／歸檔／清板之前，強制先跑；結案兩步本身不需 precheck——結案 Done 留板可見）：
```bash
bash <skills 根>/kanban-board/scripts/backlog_precheck.sh [卡id ...]   # skills 根：ZCode ~/.zcode/skills、Claude ~/.claude/skills（symlink 同源）；無參=掃全部 To Do 卡；exit 1 = 停手
```
腳本檢查：①`status=In Progress` 卡永不可清；②跨線訊號 `git log --all --not HEAD --grep <卡id>`——「有 commit 提及此卡、但當前 branch 不包含」＝真平行線訊號（裸 `--all --grep` 會命中本線建卡 commit，永遠誤報）。exit 1 → 停手先協調，不就地清（真實案例：分岔 branch commit 標題含卡 id、平行 session 對同卡各自結案，此檢查可攔下）。

**掃描**：
- AI 消費：`backlog task list --plain`（非互動 canonical 輸出）
- 機械消費：`--json`（**僅 list/view/task/search 四指令支援**）
- 想法池：`backlog draft create "<想法>"` → Drafts 頁累積 → 拍板 `backlog draft promote <id>`（想法→承諾）

**遠期卡治理（draft vs archive vs Icebox）**（實證 2026-09-03，例：mosaic `MOS-2/3/7 → DRAFT-1/2/3` 後 `To Do: MOS-10/16 + Done 7`；決策見 [Backlog.md 治理設計](../../ai-analysis/_tasks/09-03-backlog-governance-design/design.md)）：
| 情境 | 動作 | 命令 | 版面效果 |
|------|------|------|----------|
| 遠期研究/暫緩（`To Do` 噪音） | **demote → draft**（官方停車場） | `backlog task demote <id>` → `backlog/drafts/draft-*.md` | board 完全隱形；`backlog draft list --plain`/`view DRAFT-x --plain`/`browser /drafts` 可見；`search`/`board` 不撈 |
| 廢棄/永不做 | **archive** | `backlog task archive <id>` → `backlog/archive/` | 同上隱形，但語義為廢棄 |
| 想保留 To Do 可見性 | **不加 Icebox 欄** | 維持 `statuses [To Do, In Progress, Done]` 三欄，遠期用 `draft` 替代 | 加 `Icebox` 仍多一欄、噪音未根除；`To Do` 應只留可開工承諾 |

- 起手式：`backlog draft list --plain` 巡 `drafts` → `backlog draft view DRAFT-x --plain` 看內容 → `backlog draft promote DRAFT-x` 回 `backlog/tasks`（遠期如 `ECPPE` 可先記 `ai-analysis/_projects/<線>/open-items.md` 一行指針，熬到可開工才 `task create`，避免先佔承諾池）

**註記追加**（消費場景等）：`backlog task edit <id> --append-notes "<文字>"`

## 卡即 handoff（卡拼裝＝self-contained）

卡 `desc`＋`notes`＋`references`＋`EP`（若有）四件拼裝即 handoff——接手 session 讀卡即接手，不重辯已定事。分工：`desc`=決策層（baseline／已決策勿重辯／範圍／驗收，不變共識）／`EP`=規劃層（怎麼做）／`notes`=留言層（接手指針，過程不沉澱）。兩層判定承諾時已定（見 [execution-plan](../execution-plan/SKILL.md) 規模分級，不新造）：small 不建 EP 直行、standard+ 建 EP。決策層變更（scope／驗收校準）→同步回寫卡 `desc`。

## UI 入口

| 形態 | 命令 | 說明 |
|------|------|------|
| Web board | `backlog browser` | `127.0.0.1:6420`（config `default_port`）；WebSocket 雙向 live——CLI/AI 改檔→瀏覽器秒更、拖卡→frontmatter 變更 |
| TUI | `backlog board` | 終端互動板（fs.watch live）；CJK 寬度有測試釘住，邊角字形留意 |

## 與官方工作流的差異宣告（兩條）

1. **PLAN 不寫進卡**——實作計畫唯一源＝EP（任務家 `<task>/ep.md`）；卡用 `references` 指回 EP/殼（EP 深度＝baseline hash/Report Shell/post-build 鏈，是卡 PLAN 欄位的超集）
2. **不掝 per-task branch**——任務與分支解耦（多 worktree 紀律由各 repo 自訂）；spawned／automation session 的 owning-WT 約束單一源＝[collaboration-constraints rule](../../rules/collaboration-constraints.md)「Agent 派發與產出回收」（always-load 層—— spawned session 不載本 skill 也約束得到）

## 容錯

無 `backlog/` 目錄 → 卡片動作整項跳過不報錯（board 是 repo opt-in 層；任務追蹤退化為任務目錄存在性）。
