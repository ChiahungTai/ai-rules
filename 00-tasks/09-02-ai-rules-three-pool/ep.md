# ai-rules-three-pool — ai-rules 自家分析側三池對齊（full domain）

> 級別：simple 清單任務（git mv＋引用 sweep＋README——無程式邏輯）
> line: —（本 repo 基礎設施）
> baseline：動工當下 `git rev-parse HEAD` 補記
> 設計脈絡：user 2026-09-02 裁定「我是要 full domain」——ai-rules 自家也採 `ai-analysis/_tasks/` 任務家，與 mosaic 一致；探測規則文字不動（跨專案 skill 需 fallback 給無 ai-analysis 樹的 repo），但 **user 的 repo 群逐一採結構後，實踐上全域一致**（mosaic ✓、ai-rules 本任務、未來 code-reality/codetour 可複製本模式）。

## 🔴 前置 gate（動 S2 前必查）

`git status --porcelain -- 00-tasks/` 必須乾淨——**muse-plugin-cc session（09-02）正在飛**（ep.md＋build-acceptance.md 有未 commit 修改）。樹清才動遷移（並行弧時機 gate 教訓：大批 uncommitted 遷移會污染並行 session 的 diff triage、搬目錄斷其引用）。非 0 → 停，等它收尾。

## 清單

- [ ] **S1 建構**：`mkdir -p ai-analysis/{_tasks,archive}`
- [ ] **S2 任務家遷入（含本任務自遷）**：`git mv 00-tasks ai-analysis/_tasks`；repo root 的 `00-tasks/` 消失；`fd '00-tasks' . -d 2` 零命中。之後探測規則在 ai-rules 解析到 `_tasks`——新 `/spec --write`、`/execution-plan` 自動落對地方（S9 已接線，無需改 skill）
- [ ] **S3 退役清債**：`git mv ai-analysis/execution-plans ai-analysis/archive/execution-plans`；`git mv ai-analysis/specs ai-analysis/archive/specs`（skills 明文宣告退役的兩慣例，實體卻還在自家——本任務消滅這個矛盾）
- [ ] **S4 flow-feedback 決策（已定）**：**保留原名不動**——有 skill 接線（flow-feedback skill＋metadata-sync 歸檔項引用路徑）與既有 `_done/` 慣例，改名 churn > 一致性收益；其「回饋 inbox」角色寫進 S5 的 README 定義。日後要併 `_inbox/` 另案
- [ ] **S5 放置規則單一源**：寫 `ai-analysis/README.md`——目錄表（`_tasks/`=任務家〔MM-DD-name，done/ 歸檔〕、`archive/`=唯一歸檔根、`flow-feedback/`=回饋 inbox、`reports/`/`prompts/`/`tours/` 職責各一行）＋「本 repo 亦消費 ai-rules skills——放置規則衝突時以 skills 探測為準」
- [ ] **S6 引用面 sweep**：`rg -n "00-tasks" .` ——**預期合法殘留**：skills 內「否則 repo-root `00-tasks/`」探測條款（那是給其他 repo 的文字，保留）＋歷史報告/memory 引用（白名單）；活層引用（本 repo 檔案指 00-tasks 實體路徑者）逐一改 `_tasks`。`rg -n "ai-analysis/execution-plans|ai-analysis/specs"` 活層改指 `archive/`（skills 內「慣例退役」的敘述句保留——歷史事實）
- [ ] **S7 .gitignore 檢查**：查 root `.gitignore` 有無 `00-tasks/**/diagram-*` 條目——有則改 `ai-analysis/_tasks/**`（無則跳過；本 repo 任務殼目前無 diagram 產物，預防性條目可加）
- [ ] **S8 結算**：memory 池更新——`project_task-flow-restructure-00-tasks` 等引用 ai-rules 自家 00-tasks 路徑的條目改新路徑（歷史敘述不動）＋跑 `_generate_index.py`；`.kanban/` 不在本任務範圍（現況使用度另案）

## 驗收

- `fd '00-tasks' . -d 2` 零命中；`ls ai-analysis/` 含 `_tasks/`、`archive/`，不含 `execution-plans/`、`specs/`
- 新 session 跑 `/spec --write` 落 `ai-analysis/_tasks/<MM-DD-name>/spec.md`（探測解析正確）
- S6 sweep 白名單外零命中
- commit（user 確認；單一 commit 即可——變更原子性：結構＋引用＋README 同 commit）
