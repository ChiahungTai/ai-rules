# Spec：code-reality 獨立 repo＋統一 MCP（facts facade 具體化）

> **定位**：`/execution-plan` 的需求層輸入（自足）。來源弧＝2026-08-25 deep-work
> 生態研究＋其後 spec 對齊（本檔收斂所有已鎖決策）。
> **事實錨**：ai-rules HEAD `3e985dc`；研究報告
> `ai-analysis/reports/rust-precision-ecosystem-research.md`（未 commit）；
> memory `project_code-reality-tri-track.md`（08-25 二次翻案段起）；
> POC scratch `.agent-tmp/repo-poc/`。

## User Story

作為 solo 開發者＋AI 協作，我想要一個自有的 code-reality 服務（獨立 repo、
單一 MCP 接口），統一 SCIP 語義層（refs/callers/call edges）與圖查詢層
（transitive/impact/communities），讓 LLM 用一個接口、每個回應帶 `[SRC]`
溯源，拿到全部結構事實。

**痛點**：三接口（CRG fork 的 MCP＋scip_refs CLI＋三份路由文件）把路由
負擔壓在 LLM 認知上；CRG（tree-sitter）的 Rust 符號層有不可修的語法級
缺陷（NT 實測 861 顆同鍵假空）；改 CRG fork 需自行發版才能上 server
（現行 launchd 跑 PyPI @2.3.8 非 fork）。

## 已鎖決策（勿重辯）

| # | 決策 | 內容 |
|---|------|------|
| D1 | **一次性搬遷** | 整組 `code_reality/`（九工具＋400+ tests）big-bang 進新 repo；切換確認前舊碼留 ai-rules（最終態零殘留） |
| D2 | **v0＝現在作法搬遷＋薄殼＋caller 邊** | v0 不含圖演算法；caller 邊模式（DEF-enc containment，已證 96.9%）納入 v0 |
| D3 | **git path 起步** | `uv run --project ~/Github/<new-repo>` 消費＋launchd 常駐（抄 lsp_mcp 套路）；PyPI/plugin market 為遠期。**ZCode 市場機制已確認**（官方文檔 https://zcode.z.ai/cn/docs/plugin，2026-08-25）：本地路徑可為市場源（開發迴圈＝改碼→市場源面板刷新→重裝觸發驗證）、GitHub repo 可為團隊分發源；`marketplace.json`＋`plugins[].source` 相對路徑；官方建議**純 skill 起步，跑通後再加命令/Hooks/MCP**——新 repo 可自身兼市市場 repo（root marketplace.json＋plugin dir），開發/git path/市場三消費形態共存 |
| D4 | **LSP 排除** | `lsp_mcp`（互動層）維持獨立不納入——簡單互動查詢它自足 |
| D5 | **B1/B2 研究排 v1 前置** | B1（CRG 當內部圖引擎）vs B2（自建圖層）完整研究＝EP v1 段落的研究任務＋單向門裁決（user 拍板）；v0 圖層契約按 DIP 先定（兩實作都塞得進） |

**硬約束**：NT 治理鉤子的 CLI 契約（`--json`／exit codes／stdout 位元組）
**永不破壞**——搬遷後工具碼原樣、輸出 byte-identical；唯一變更＝呼叫路徑
（`--project` 指新 repo），屬 relay 項（NT 側配合改）。lsp_mcp / CRG MCP
（PyPI @2.3.8）在 v0 期不動（並行雙活）。

## UC 定位

- **UC-1 符號真相查詢**（refs/defs，trait 消歧）📦 scip_refs 隨遷
- **UC-2 caller 邊查詢**（callers/call_edges/closure）📋 機制已證（96.9%＋3 元素 span 修正）
- **UC-3 圖級查詢**（impact/communities/hub/dead-code）📋 v1（B 裁決＋SCIP 注入後）
- **UC-4 完整度治理**（audit＋`[SRC]` 溯源）📦 graph_audit 隨遷強化
- **UC-5 單一 MCP 接口**（缺差驅動路由內化進 server）📋 核心
- **UC-6 可刪判斷安全網**（hub_refs/hazard 消費 caller 邊）📦 升級資料源
- **UC-7 發佈形態**（plugin 打包＋ZCode/Claude plugin market）📋 遠期（v2+）——**兩家市場機制均已確認**（ZCode：本地路徑/GitHub repo 市場源＋MCP 支援，官方文檔如上；Claude：plugin manifest＋marketplace git repo）；MCP 啟動命令須為「可寫進 plugin manifest 的一條命令」（薄殼形態天然滿足）；分階段＝純 skill plugin 起步→加 MCP。**安全語義**：啟用 plugin＝授予本地執行信任（可執行進程、讀 Agent 環境變數）——對外發佈時 README 須載明此風險與授權 notices

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 |
|---|------|------|---------|
| SM-1 | 查 trait impl 方法引用 | callers on `Type.method` | 兩符號形態消歧＋caller 歸屬＋`[SRC]` |
| SM-2 | transitive 影響盤點 | closure depth=N | BFS 過 caller 邊＋環偵測＋`[SRC]` |
| SM-3 | 索引過期下查詢 | code 前進、index 舊 | 查詢照答＋drift WARN＋雙 sha 顯示（不擋） |
| SM-4 | 無索引 repo 首次查詢 | 無 scip index | loud error＋生成指引（不自動跑 ~8 分生成） |
| SM-5 | 缺 repo/workspace 參數 | MCP 呼叫漏參 | loud error 帶修正指引（lsp_mcp 同型） |
| SM-6 | 巨集生成 fn 內呼叫 | caller 歸屬 | single-line span 支援（≥35 顆反例不誤殺——研究報告 §2.2） |
| SM-7 | NT 治理鉤子夜跑 | CLI `--json`＋exit codes | 搬遷前後位元組級不變 |
| SM-8 | Python repo 圖查詢 | mosaic graph.db | B1 形態下 CRG 資產行為不變 |
| SM-9 | hub symbol closure 效能 | 195KB 級 refs | 秒級（sqlite 0.06s 路徑）＋按檔聚合 |
| SM-10 | MCP 常駐吃舊碼 | 工具迭代後 | 保鮮策略生效（薄殼 spawn vs kickstart，EP 決策） |

## 邊界

**Always**：單一 MCP 接口、每回應帶 `[SRC]`；NT CLI 契約位元組級相容；
圖層契約先於 B 決策（DIP）；85+ tests 隨遷全綠；lsp_mcp 獨立不動。
**Ask First**：B1/B2 裁決（研究報告→user 拍板）；repo 命名；CRG MCP 退役
時點；任何 NT 契約相關介面演化；發佈前 review 授權 notices。
**Never**：破壞 NT `--json`/exit codes；把 LSP 包進來；回應無 `[SRC]`；
靜默歸錯換速度；搬遷完成後 ai-rules 留殘留副本。

## 成功條件

①v0 後 LLM 用單一 MCP 完成語義面 UC（refs/callers/call_edges/closure/
audit）；②E2E 三源一致：NT `EventStoreLifecycle.open` 的 SCIP 歸屬＝
LSP `incomingCalls`＝closure 查詢起點（17 callers 基準）；③NT 鉤子搬遷
前後 byte-identical；④400+ 搬遷測試全綠＋SM 全覆蓋；⑤CRG MCP 可退役
（v1 末評估）。

## POC 證據（2026-08-25，L4）

`.agent-tmp/repo-poc/`（scratch：最小 pyproject＋複製 code_reality＋
conftest/fixtures/test_scip_refs）：
- 外部 cwd（NT repo）`--help` exit 0（venv 自建＋packaged build）
- 真查詢 `[SRC]`＋兩形態＋18 refs exit 0（與 ai-rules 版一致）
- `pytest tests/test_scip_refs.py` **85 passed 0.36s**
- **發現**：protobuf 需從 dev group 移 **runtime dependencies**（唯一
  第三方相依；ai-rules 靠 uv run 本地含 dev 才工作）

## EP 段落骨架（建議）

```
段1  新 repo 骨架＋一次性搬遷（tests 全綠；參考 repo-poc pyproject）
段2  caller 邊模式＋closure（新 repo；驗收＝18 refs 三源一致）
段3  MCP 薄殼＋launchd＋ZCode user-level 掛接（SM-5/SM-10）
段4  消費端切換 relay（NT 呼叫路徑＋mosaic profile＋ai-rules skill 路徑）＋刪舊碼
──── v1 ────
段5  B1/B2 完整研究 → 決策報告 → user 裁決
段6  圖層＋SCIP 注入（驗收＝NT graph_audit 861 缺差→0）＋impact/communities 上 MCP
段7  CRG MCP 退役＋crg-query skill 收斂
```

## 授權結論（已查證，2026-08-25）

CRG＝MIT（Tirth Kanani）；rust-analyzer＝MIT/Apache；scip.proto＝Apache-2.0；
protobuf＝BSD-3；NT＝資料消費非程式連結；ai-rules 全 repo AGPL 假檔頭已清零。
**無 copyleft 鏈傳導**；發佈（market）義務僅＝保留 CRG/scip.proto notices。

## 參考

- 研究報告（caller 邊機制＋生態掃描＋方法論限制）：
  `ai-analysis/reports/rust-precision-ecosystem-research.md`
- 前份評估（2026-08-21 baseline）：mosaic
  `ai-analysis/reports/code-reality-tools-evaluation.md`
- memory：`project_code-reality-tri-track.md`（A6/④enc 二次翻案/spec 決策弧）
- 消費形態慣例：`skills/code-reality/SKILL.md`（EP 段 4 路徑更新對象）
