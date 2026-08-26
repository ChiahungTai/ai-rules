# EP：code-reality 獨立 repo＋統一 MCP（v0）

> **ep_type**: implementation
> **spec**: [ai-analysis/specs/code-reality-repo-mcp-spec.md](../specs/code-reality-repo-mcp-spec.md)（五決策／UC×7／SM×10／邊界／成功條件真相源——**已鎖決策本 EP 不重辯**）
> **研究背景**: [ai-analysis/reports/rust-precision-ecosystem-research.md](../reports/rust-precision-ecosystem-research.md)（caller 邊機制 96.9% E2E＋生態掃描＋§7 方法論限制）
> baseline: `3e985dc`（EP 建立當下 ai-rules HEAD）
> **POC**: `.agent-tmp/repo-poc/`（2026-08-25 L4 已驗——段 1 參考其 pyproject）

## 實作總覽

把 `code_reality/`（20 .py＋scip.proto，6,208 行）與 `tests/`（24 test 檔＋conftest＋fixtures/，381 個 test function）**big-bang 搬進新 repo**，加兩個新能力（caller 邊＋closure；MCP 薄殼），消費端 relay 切換，最終 **ai-rules 零殘留**。

| 段 | 內容 | 新增/搬遷 | UC |
|----|------|----------|-----|
| S1 | 新 repo 骨架＋一次性搬遷 | 搬遷（零邏輯改動） | UC-1/UC-4 隨遷 |
| S2 | caller 邊模式＋closure | 新增 | UC-2（核心）、UC-4 口徑強化 |
| S3 | MCP 薄殼＋launchd＋ZCode 掛接 | 新增 | UC-5（核心） |
| S4 | 消費端切換 relay＋ai-rules 舊碼刪除 | 刪除＋文檔 | 全部收斂 |

**v0 範圍外**（見「v1 展望」）：圖層＋SCIP 注入（UC-3/UC-6 資料源升級）、B1/B2 裁決、CRG MCP 退役、發佈形態（UC-7）、lsp_mcp home 遷移。

**硬約束（全段共用）**：NT 治理鉤子 CLI 契約（`--json`／exit codes／stdout 位元組）**永不破壞**——搬遷後工具碼原樣、輸出 byte-identical，唯一變更＝`--project` 呼叫路徑（relay 項）。lsp_mcp 與 CRG MCP（PyPI @2.3.8）v0 期不動（並行雙活）。每回應帶 `[SRC]`（無證據不輸出——loud error 回應本質無 `[SRC]`，屬此條款邊界允許）。

**成功條件**（spec 五條，v0 達成①②③④；⑤=v1 末）：①單一 MCP 完成語義面 UC（refs/callers/call_edges/closure/audit——call_edges 由 `--callers` 輸出的邊集〔caller→callee＋site 清單〕承接，見 S2）；②E2E 三源一致（`EventStoreLifecycle.open`：SCIP containment＝LSP `incomingCalls`＝closure 起點，17 callers 基準）；③NT 鉤子搬遷前後 byte-identical（query＋audit＋`graph_audit --json` 三面）；④搬遷測試全綠＋v0 範圍 SM 全覆蓋。

---

## UC 盤點

### 掃描範圍
- ai-rules `AGENTS.md` 專案結構（code_reality/tests 條目）、`skills/CLAUDE.md`（crg-query／code-reality 索引行）
- `.kanban/Backlog/` 9 卡全掃：無直接對應卡（`crg-shared-server-followups.md` 是 CRG server 面後續，與本 EP 正交——v0 雙活不動它）
- SYSTEM-MAP.md 不存在（提醒：本 repo 無此檔，非本 EP 義務）

### 既有 UC 狀態

| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| 符號真相查詢（refs/defs，trait 消歧）＝UC-1 | ✅（住 ai-rules） | `code_reality/scip_refs.py` | **搬家** | 能力原樣遷新 repo，Capabilities 表格落新 repo AGENTS.md |
| 完整度治理（audit＋`[SRC]`）＝UC-4 | ✅（住 ai-rules） | `scip_refs --audit`＋`graph_audit` | **搬家＋口徑強化** | S2 caller 口徑（refs/callers 機械分離）補進工具輸出與文檔 |
| 可刪判斷安全網（hub_refs/hazard）＝UC-6 | ✅（住 ai-rules） | `hub_refs --hazard` | **搬家＋S4 relay 切路徑** | hub_refs/hazard 工具隨 S1 遷、mosaic 消費命令 S4 換 `--project`；資料源升級（graph.db←SCIP 注入）=v1 S6 副作用 |
| CRG 共享 server 接線 | ✅ | `hooks/require-crg-repo-root.py`＋zcode-registration | 無影響 | v0 雙活不動 |

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| UC-2 caller 邊查詢（callers/call_edges/closure） | 📋 | 新 repo `code_reality/caller_edges.py`＋`scip_refs.py` 模式擴充（S2） |
| UC-5 單一 MCP 接口（缺差驅動路由內化） | 📋 | 新 repo `code_reality/mcp_server.py`（S3） |

### Backlog 關聯＋建卡結果
- 自動建卡（本 EP 產出時執行）：EP 追蹤卡 `ep-code-reality-repo-mcp.md`＋能力卡 `code-reality-caller-edges.md`（UC-2）＋`code-reality-mcp-server.md`（UC-5），共 3 張新建於 `.kanban/Backlog/`。

---

## Scenario Matrix（spec SM×10＋段對應）

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力/段 |
|---|------|------|---------|------------|------------|
| SM-1 | 查 trait impl 方法引用 | callers on `Type.method` | 兩符號形態消歧＋caller 歸屬＋`[SRC]` | 無 | UC-2／S2 |
| SM-2 | transitive 影響盤點 | closure depth=N | BFS 過 caller 邊＋環偵測＋`[SRC]` | visited set | UC-2／S2 |
| SM-3 | 索引過期下查詢 | code 前進、index 舊 | 查詢照答＋drift WARN＋雙 sha 顯示（不擋） | 無 | 既有隨遷（pytest：drift WARN 測試）＋S1 L4 抽跑 |
| SM-4 | 無索引 repo 首次查詢 | 無 scip index | loud error＋生成指引（不自動跑 ~8 分生成） | 無 | 既有隨遷（pytest：無索引 loud 測試）＋S1 L4 抽跑 |
| SM-5 | 缺 repo/workspace 參數 | MCP 呼叫漏參 | loud error 帶修正指引（lsp_mcp 同型） | 無 | UC-5／S3 |
| SM-6 | 巨集生成 fn 內呼叫 | caller 歸屬 | single-line span 支援（≥35 顆反例不誤殺——研究報告 §2.2） | 無 | UC-2／S2（必測） |
| SM-7 | NT 治理鉤子夜跑 | CLI `--json`＋exit codes | 搬遷前後位元組級不變 | 無 | 硬約束／S1 並跑＋S4 NT 驗收（query/audit/graph_audit 三面 cmp） |
| SM-8 | Python repo 圖查詢 | mosaic graph.db | B1 形態下 CRG 資產行為不變 | 無 | v1／S6 |
| SM-9 | hub symbol closure 效能 | 195KB 級 refs | 秒級（sqlite 0.06s 級路徑）＋按檔聚合 | 無 | UC-2／S2 |
| SM-10 | MCP 常駐吃舊碼 | 工具迭代後 | 保鮮策略生效（**EP 決策＝薄殼 spawn**，見 S3） | 無 | UC-5／S3 |

---

## 段落 0：全域研究摘要

### 可複用基礎設施（搬遷主體＝最大複用）

- `code_reality/scip_refs.py`（835 行）：SCIP 查詢面全套——兩符號形態 matcher（`_matcher`＋`FN_TAIL_RE`，長在 `defs(query)` 路徑）、face 層（`ProtobufFace`／`SqliteFace`——**現況：`refs()` 回傳格式化字串 `dict[str, list[str]]`（`rel_path:line`），S2 需新增結構化存取器**，SQL 只縮候選、語義單一真相源在 Python）、slot 解析（`DEFAULT_INDEX_ROOT`＋`default_index_path`）、`--stamp-meta` sidecar＋`source_line()`／`[SRC]`、衍生 sqlite 三表＋meta schema 版本守衛（`SCHEMA_VERSION`／`_stale_reason`）＋三守衛自動重建（mtime/head/schema）、exit 0/1/2 家族、`--audit` 走 subprocess 兩遍式。S2 全部複用。
- `code_reality/graph_audit.py`（301 行）：`--json` 鍵為 NT 治理鉤子契約（**勿改**——docstring 已記）；v0 維持 CLI 形態（S3 audit 工具走 `scip_refs --audit`——其內部既有 subprocess 兩遍式會呼叫 graph_audit，無需 MCP 直連）。
- `code_reality/common.py`（`_meta` 慣例／`connect_ro` WAL fallback）、`profile.py`（`load_profile` crash-only／`HazardRegistry`／`module_of`）、`hazard.py`（六規則純函數）。
- `tests/`：conftest（`Path(__file__).parent` 相對路徑——無 ai-rules 硬編碼）＋`fixtures/`（`crg_db.py`/`delegation_driver.py`/`make_trace.py`/`profile_repo.py`）；integration 測試路徑全指 repo 外（NT/mosaic checkout＋sidecar home）——搬遷不斷（已驗）。S2 新測試沿用 fixture 形態（`test_scip_refs.py` 85 tests 為 POC 已驗搬遷態）。
- MCP 套路（repo 外參考，唯讀）：lsp_mcp＝`/Users/ctai/Github/mosaic_alpha/tools/lsp_mcp/`——**官方 SDK 形態**（`from mcp.server.fastmcp import FastMCP`、`mcp.run(transport="streamable-http")`、host/port 走 constructor——server.py 註解明言），S3 抄此棧與「launchd HTTP 常駐」套路，**不抄 workspace pool**；CRG plist＝`com.user.crg-mcp.plist`（uvx serve --http、中性 WorkingDirectory、KeepAlive/ThrottleInterval 10、`FASTMCP_LOG_LEVEL=WARNING`——log 124MB 教訓）。
- 機械強制 hook 前例：`hooks/require-crg-repo-root.py`（58 行，PreToolUse 攔 `mcp__code-review-graph__*` 缺 repo_root）。**S3 不需要同款 hook**——CRG hook 存在是因為 PyPI @2.3.8 server 端不可改；新 server 端自己 loud error（SM-5）即可。

### 依賴關係與關鍵約束

- 消費端現況：NT 治理鉤子消費**兩面**——`graph_audit --json`（430/233/861，NT 機器基準）＋`scip_refs` query/audit（byte-identical＋138/861）；mosaic 消費 `hub_refs --hazard`（profile `[[hazard_registry]]` 兩條）；兩者 profile 都在**被掃 repo root**（repo 事實歸 repo，搬遷不動 profile）。
- sidecar home 凍結：`~/.mosaic/code-reality/`（SKILL.md 明言延續）——含 scip slot `<repo-basename>/index.scip(.db/.meta.json)`。搬遷**不改** sidecar home。**現場注意**：本地 NT 真索引（stamp 76213ffd）目前在 slot home **根目錄**（legacy 位置，①之前的路徑），repo-keyed slot `scip/nautilus_trader/` 尚未存在——S1 L4 前置「索引歸位」處理。
- ai-rules 內引用面（S4 改寫清單；**符號錨非行號**——執行前 `rg "uv run --project ~/Github/ai-rules" --type md` 重掃定全集，防並行 session 漂移）：`AGENTS.md` 專案結構（code_reality/tests 兩條目）、`skills/code-reality/SKILL.md`（frontmatter description「住 ~/Github/ai-rules」＋when_to_use 存在性偵測＋「工具在 ~/Github/ai-rules」定位句＋消費形態模板＋存在性述語）、`skills/CLAUDE.md`（crg-query/code-reality 兩索引行）、`skills/implement/SKILL.md`（階段 1 snapshot／階段 6 transition）、`skills/code-review/SKILL.md`（模式 B 弧模式）、`skills/post-build/SKILL.md`（transition 提及＋tour_validate）、`skills/debrief/SKILL.md`（段 3/5 機械底稿）、`skills/blueprint-bootstrap/SKILL.md`（boundary 補錨＋chain_tour 自測）、`skills/tour-bootstrap/SKILL.md`（chain_tour 命令）。rules/hooks/scripts/agents/ **零引用**（已驗）。**掃描豁免**：`skills/zcode-session-query/SKILL.md` 的 `--project ~/Github/ai-rules` 是借 ai-rules venv 跑自家腳本（非 code_reality 消費）——零殘留掃描列豁免、不改。
- 環境事實：port 5555（CRG）/8000（lsp）已佔，**8200 空閒**（已查 LISTEN）；ZCode user-level MCP 形態＝`{"type":"http","url":...}`（config.json `.mcp.servers`，子樹 merge 非整檔覆蓋）；ZCode MCP 工具面 per-session 快照（新 session 才見新工具）。

### 風險假設清單

| 等級 | 假設 | 驗證 |
|------|------|------|
| 致命｜✅ 已驗 | 新 repo 獨立消費可行（外部 cwd／packaged build／85 tests） | POC L4（`.agent-tmp/repo-poc/`） |
| 致命｜✅ 已驗 | caller 邊機制（DEF-enc containment，96.9% 歸屬＋17 callers LSP 交叉） | 研究報告 §2（reviewer 獨立重跑複現） |
| 高 | 本地 NT 索引在 legacy slot 根目錄——`--repo` slot 解析會落空 | S1 L4 前置「索引歸位」（驗 meta.json 歸屬後 mv 進 slot——①⑤ docstring 搬遷提示同款警語） |
| 高 | sqlite schema 演化（fn_defs 新表）與既有三守衛互動——機制存在（meta `schema` 版本鍵＋`_stale_reason`），舊 db 須自動重建不改輸出 | S2 驗證 |
| 高 | 3 元素 single-line span（巨集生成 fn）不支援則 ≥35 顆誤殺 | S2 必測（SM-6） |
| 高 | editable install 保鮮：`uv run --project` 消費＝讀工作樹最新碼（ai-rules 形態實證；POC 用 packaged build——**兩者行為不同，S1 須顯式驗證 editable 形態**） | S1/S3 freshness probe |
| 中 | 搬遷完整性（漏檔） | S1 機械對帳（diff -r） |
| 中 | MCP SDK 在新 repo venv 的 HTTP 啟動（lsp_mcp 前例同棧已驗，殘餘＝依賴安裝與版本） | S3 V1（`uv add mcp` 落步驟） |
| 中 | NT relay 後契約 | S4 NT 側 byte compare（自足式基準） |

### callstack 菜單積壓
無（repo 無 `ai-analysis/blueprint/callstack-plan.md`）。

---

## 段落劃分原則

- **依賴序**：S1（repo 存在）→ S2（工具長能力）→ S3（服務化）→ S4（切換＋刪除）。S1/S2 可同 repo 連續 build；S3 依賴 S2 的 callers/closure CLI；S4 依賴 S1-S3 全驗。
- **垂直切片**：每段獨立可驗證（S1＝搬遷等價、S2＝CLI 驗收、S3＝MCP 驗收、S4＝relay＋零殘留）。
- **雙 repo 工作紀律**：S1-S3 主戰場在新 repo（路徑 `~/Github/code-reality`）；S4 回 ai-rules。**不 cd**——跨 repo 用完整路徑＋`git -C`。
- **Ask First 閘門**：①repo 命名＝**已定案 `code-reality`**（2026-08-25 user 拍板，S1 開工免再問）；②S4 刪碼前 NT＋mosaic 驗收回報＋user 確認（D1「切換確認前舊碼留」）；③所有 git commit（consent 規則）。

---

## 段 1：新 repo 骨架＋一次性搬遷

### Context

**背景**：D1 一次性搬遷——整組 `code_reality/`＋`tests/` big-bang 進新 repo，**零邏輯改動**（唯一改動＝pyproject 相依歸位：protobuf 從 dev group 移 runtime）。切換確認前舊碼留 ai-rules（S4 才刪）。

**UC 引用**：搬遷 UC-1（符號真相查詢）＋UC-4（完整度治理）＋UC-6 工具面（hub_refs/hazard）——能力原樣換家（UC-6 的 mosaic 消費切換在 S4）。

**依賴關係**：後續 S2/S3 都在新 repo 上長；ai-rules 側本 S1-S3 期間不動（消費端零風險）。

**語義約束**：與 S4 共享「舊碼留到切換確認」；與 S2/S3 共享「sidecar home `~/.mosaic/code-reality/` 凍結、slot/stamp 慣例不變」。

**基礎設施盤點**：POC pyproject（`protobuf>=7.35.1` runtime＋setuptools＋`packages=["code_reality"]`）已驗；ai-rules `pyproject.toml`（dev group `ruff>=0.16.3`/`pytest>=8.4`/`protobuf>=7.35.1`、pytest `integration` marker、ruff `extend-exclude`＝`*.md`＋`code_reality/scip_pb2.py`）為 parity 來源。

**依賴錨點**（搬遷對象，定義端）：
- `code_reality/`（20 .py＋`scip.proto`）→ 定義 `~/Github/ai-rules/code_reality/`；消費＝`tests/` 24 test 檔＋`tests/fixtures/delegation_driver.py`（import）
- `tests/`（conftest＋fixtures＋24 test 檔，381 test functions，7 個 `*_integration.py` 檔走 `integration` marker）→ integration 測試消費 repo 外真實路徑（NT/mosaic checkout＋sidecar home；conftest 用 `Path(__file__).parent` 相對路徑）——搬遷不斷（已驗）

**技術選型**：uv project（`uv sync`/`uv run`）＋setuptools backend——與 ai-rules 及 POC 同形；Python `>=3.12`。`.python-version` 檔：可選（ai-rules 無此檔、單機消費 YAGNI；多機消費出現再釘）。

**成功標準**：新 repo 全套測試綠（對齊 ai-rules 現行基準——先在 ai-rules 跑一次記基準數）；外部 cwd L4（query/audit/graph_audit 三面並跑等價）；editable freshness probe 過。

### Invariant Impact

- **受影響 domain invariant**：NT CLI 契約（`--json`／exit codes／stdout 位元組）——silent corruption 全下游（治理鉤子誤判）。
- **critical path 觸及**：搬遷不改碼＝契約面唯一變數是環境（venv／protobuf 版本）。
- **驗證對齊**：§4「並跑雙實現等價」——ai-rules 版與新 repo 版對同一 NT 索引跑 query＋audit＋`graph_audit --json`，`cmp` 逐位（A3/d9c9315 同型驗證形態，明示替代 fresh-eyes 靜態 diff）。

### 核心實作要點

1. **repo 命名已定案**（2026-08-25 user 拍板＝`code-reality`）→ `mkdir ~/Github/code-reality`＋`git init`。
2. pyproject（POC 版＋ai-rules parity 項）：
   - `dependencies = ["protobuf>=7.35.1"]`（**runtime**——POC 發現；S3 會加 `mcp` 成第二項）
   - dev group：`ruff>=0.16.3`＋`pytest>=8.4`
   - `[tool.setuptools] packages = ["code_reality"]`；pytest `integration` marker；ruff `extend-exclude = ["*.md", "code_reality/scip_pb2.py"]`
3. 檔案搬運：`cp -R code_reality/ tests/` → 機械對帳 `diff -r`（排除 `__pycache__`/`.venv`）零差異。
4. repo 衛生：`.gitignore`（`.venv/`/`__pycache__/`/`.agent-tmp/`）＋README（定位一句＋消費形態＋授權結論一段：CRG/scip.proto notices 義務載明——spec 授權節）＋根 `AGENTS.md`（最小：專案定位＋Capabilities 表格〔v0 收尾填 ✅，涵蓋隨遷工具族＋新能力〕＋消費形態）。
5. `uv sync`→`uv run pytest`（**背景跑**；先在 ai-rules 跑基準，再新 repo 對齊）→`uv run ruff check .`。

### Pseudo Code

```
~/Github/code-reality/
├── AGENTS.md            # 最小（定位＋Capabilities 空 表＋消費形態）
├── README.md            # 一段授權 notices 預留（發佈時擴）
├── pyproject.toml       # POC 版＋ruff/pytest parity
├── .gitignore
├── code_reality/        # 20 .py＋scip.proto 原樣（diff -r 零差異）
└── tests/               # conftest＋fixtures＋24 test 檔原樣
```

### 驗證策略

- **測試計畫**：全套 pytest（ai-rules 基準數對齊，允許 1 skipped 既有）＋ruff 乾淨。既有 381 test functions 已覆蓋工具邏輯，本段零新測試（搬遷不改碼）。
- **L4 前置「索引歸位」**：本地 NT 真索引（stamp 76213ffd）在 legacy slot 根目錔 `~/.mosaic/code-reality/scip/index.scip(.db/.meta.json)`——先驗 `meta.json` 的 `repo` 歸屬＝`/Users/ctai/Github/nautilus_trader`（不符即停，①⑤ docstring 搬遷提示同款警語：**僅當索引生成自該 repo**），`mkdir -p ~/.mosaic/code-reality/scip/nautilus_trader && mv` 三件進 slot。NT 機器側不動（NT 有自己的索引與 slot 慣例）。
- **L4（外部 cwd，NT repo 下）**：
  1. `uv run --project ~/Github/code-reality python -m code_reality.snapshot --help` exit 0
  2. 並跑等價（三面）：ai-rules 版 vs 新 repo 版對 NT slot 真索引——query（兩符號形態）＋`--audit --repo`＋`graph_audit --json --repo`——各 `cmp` 逐位元組相同＋exit codes 一致（本地 graph.db 缺席時兩版同樣 fail-loud 亦為有效等價；138/861/430/233/861 數字屬 NT 機器基準，S4 NT 側驗）
  3. SM-4 抽跑：對無 slot 索引的 repo 查詢→loud error 文案＋exit 2；SM-3 抽跑（可選）：`meta.json` head 暫改→查詢 drift WARN→還原
- **freshness probe（editable 驗證）**：`uv run --project <new-repo> python -c "import code_reality.scip_refs as m; print(m.__file__)"` → 指向新 repo 工作樹（editable）；暫時加一行 marker print→subprocess 呼叫反映→還原。**此 probe 決定 S3 保鮮設計的前提**。
- **git initial commit**：user consent gate。
- 已知未覆蓋：`uv.lock` 由 `uv sync` 生成（POC lock 不搬——環境鍵不同）。

---

## 段 2：caller 邊模式＋closure

### Context

**背景**：D2——caller 邊模式（DEF-enc containment，已證 96.9% 歸屬覆蓋）納入 v0。機制：ref occ 行 → 同檔最內層含它的 fn DEF（enc＝body span）→ caller symbol；callee 已是編譯器級消歧符號（研究報告 §2.1）。

**UC 引用**：實作 UC-2（caller 邊查詢——callers/call_edges/closure。**call_edges 承接說明：`--callers` 輸出即邊集**——caller 行＋其下逐 site 行 `rel_path:line`，caller→callee×site 三元組完整在場，無獨立 `--call-edges` 模式）；UC-4 口徑強化（refs/callers 機械分離：item-level 落點＝非呼叫 refs 的自然過濾器）。

**依賴關係**：長在 S1 新 repo 的 `scip_refs.py` face 層上；S3 MCP 的 callers/closure 工具 subprocess 本段 CLI；v1 S6 圖層注入重用本段推導。

**語義約束**：與 S3 共享「CLI 介面＝MCP 唯一後端」（薄殼不重寫邏輯）；與 S1 共享「既有 query/audit 輸出一律不動」（NT 契約）；與 v1 S6 共享「fn_defs 表 schema＝日後圖層注入的邊材料」。**依賴方向**：`caller_edges.py` 純演算法零 import scip_refs（`FN_TAIL_RE` 過濾等由 scip_refs 側組裝時注入/前置）——依賴單向 scip_refs → caller_edges，無循環。

**基礎設施盤點**：`scip_refs.py` 既有——face 抽象（**`refs()` 回格式化字串——本段需新增結構化存取器 `refs_rows()`，禁止解析格式化字串當捷徑**：`rel_path:?` 歧義＋違「SQL 只縮候選、語義單一真相源」紀律）、`_matcher`/`FN_TAIL_RE` 兩形態消歧（`defs(query)` 路徑）、`source_line()`/`[SRC]`、`SCHEMA_VERSION` meta 版本鍵＋`_stale_reason` 三守衛、exit 0/1/2 家族、模式 mutex（`is not None` 檢查——②F7 教訓）。`test_scip_refs.py`（85 tests）fixture 形態沿用。

**依賴錨點**：
- `ProtobufFace`/`SqliteFace` → 定義 `code_reality/scip_refs.py`（face 層；`refs()` 介面現況如上）；消費＝同檔 query 路徑＋新 callers/closure 路徑（經新增 `refs_rows()`/`fn_spans()` 存取器）
- `--build-cache` 三表＋`SCHEMA_VERSION` → 定義 `code_reality/scip_refs.py`；消費＝fn_defs 新表建表處
- 研究腳本（歸屬演算法參考實作）→ `.agent-tmp/research/scip_caller_e2e.py`（一次性，可清）

**技術選型**：推導層獨立模組（純函數，無 I/O、無 scip_refs import）＋CLI 模式擴充（複用 face/`[SRC]`/exit 家族）——不開新工具檔入口（`python -m code_reality.scip_refs` 單入口維持）。

**成功標準**：spec 成功條件②——`EventStoreLifecycle.open` callers＝**17 callers**（trait impl `open()` 委派＋16 測試 fn）＝LSP `incomingCalls`（三源一致）；SM-6（single-line span）測試過；SM-9 closure 秒級＋按檔聚合。

### Invariant Impact

- **受影響 domain invariant**：既有 scip_refs 輸出不變（query/audit 路徑 byte-identical）＋sqlite schema 演化安全（舊 db 自動重建不改輸出）。
- **critical path 觸及**：silent-corruption 類——歸屬錯誤（巨集 fn 誤殺、tie 誤歸）會靜默污染 caller 集合 → 可刪判斷誤導。
- **驗證對齊**：§4「既有路徑回歸 cmp」＋「三源一致 L4」＋單元測試釘住 tie/single-span 歸屬語意。

### 核心實作要點

1. **face 介面擴充**（scip_refs.py，兩 face 各一）：`refs_rows(symbols) -> dict[str, list[tuple[rel_path, line]]]`（結構化——protobuf 面直取 occ 欄位；sqlite 面 SQL `WHERE symbol IN (...)` 回 rows，與既有 `refs()` 共用候選縮小邏輯）＋`fn_spans() -> dict[rel_path, list[FnSpan]]`（protobuf 面：DEF occ enc 即時建；sqlite 面：fn_defs 表載入）。兩形態解析：query symbol 先 `face.defs(query)`（既有 matcher）得 symbol set 再 `refs_rows`。
2. **新模組 `code_reality/caller_edges.py`**（純演算法層）：
   - `FnSpan(rel_path, symbol, start_line, end_line)`（**1-based inclusive**——SCIP enc 行號 0-based，組裝時 +1 轉換與 refs 座標系對齊）
   - `attribute(line, spans)`：innermost containment（含該行的 span 中 `(寬度, 來源序)` 最小者；同寬 tie 先見者勝——**行級粒度已知誤差源，docstring 明記**）
   - `callers(refs_rows, spans_by_doc)`：refs 逐筆歸屬 → `{caller: [sites]}`＋**item-level remainder**（無含入 fn 的 refs——use/const/屬性層，輸出計數與清單分離標注，非靜默丟棄）
   - `closure(seed, expand, depth)`：BFS（level k callers 聯集＝level k+1 frontier；`expand`＝呼叫端注入的 face 查詢包裝）＋visited set 環偵測（SM-2）＋按檔聚合（SM-9）
   - span 建構（含 `FN_TAIL_RE` 過濾＋4/3 元素 span 解析＋0-based 轉換）住 scip_refs 側組裝層——caller_edges 收純資料
3. **sqlite schema 演化**：新表 `fn_defs`（見 pseudo code——**`seq INTEGER PRIMARY KEY` 比照 occurrences**：VACUUM 不重編隱式 rowid，tie 先見者依據才穩定）＋doc 索引；meta `SCHEMA_VERSION` **bump**（既有守衛：不符→過期→自動重建——機制已驗）；innermost 判定留 Python（語義單一真相源紀律）。
4. **CLI 模式**（`scip_refs.py` 擴充，既有 mutex 家族併入）：
   - `scip_refs <symbol> --callers --repo <repo>` → `[SRC]` 首行＋每 caller 一行（symbol＋site 數）＋**其下逐 site 行 `rel_path:line`**（＝call_edges 邊集）＋item-level 摘要行
   - `scip_refs <symbol> --closure [--depth N] --repo <repo>`（depth 預設 2）→ per-depth 按檔聚合＋環偵測報告
   - exit codes 對齊既有（0 命中／1 符號未命中／2 錯誤）；protobuf face 與 sqlite face 皆可答（sqlite 自動優先）
5. **文檔**：SKILL.md scip_refs row 補 callers/closure＋口徑 clause（refs＝所有 non-DEF occ、不可當呼叫數解讀；callers＝歸屬子集）——種子 2 制度化落點（stdout 不動＝保 NT 契約）。

### Pseudo Code

```python
# code_reality/caller_edges.py（新——純演算法：零 I/O、零 scip_refs import）
@dataclass(frozen=True)
class FnSpan:
    rel_path: str; symbol: str; start_line: int; end_line: int  # 1-based inclusive

def attribute(line: int, spans: list[FnSpan]) -> FnSpan | None:
    # candidates = [s for s in spans if s.start_line <= line <= s.end_line]
    # min(key=(end_line - start_line, 來源序))——innermost；None -> item-level

def callers(refs_rows: dict[str, list[tuple[str, int]]],
            spans_by_doc: dict[str, list[FnSpan]]) -> CallersResult:
    # per (callee, rel_path, line): caller = attribute(...) -> edges[caller].append(site)

def closure(seed: str, expand: Callable[[str], CallersResult], depth: int) -> ClosureResult:
    # BFS + visited 環偵測 + 按檔聚合；expand 由 scip_refs 側包裝 face 查詢注入
```

```python
# code_reality/scip_refs.py 側擴充（組裝層）
class ProtobufFace:  # SqliteFace 同介面
    def refs_rows(self, symbols) -> dict[str, list[tuple[str, int]]]: ...  # 結構化存取器（新）
    def fn_spans(self) -> dict[str, list[FnSpan]]: ...  # protobuf: DEF occ enc 即時建（含 0-based→+1）；sqlite: fn_defs 載入

def build_fn_spans(doc_occ) -> dict[str, list[FnSpan]]:  # scip_refs 側（用 FN_TAIL_RE 過濾）
    # 4 元素 [sl,sc,el,ec] -> (sl+1, el+1)；3 元素 [sl,sc,ec] -> (sl+1, sl+1)  # SM-6 single-line
```

```sql
-- scip_refs.py --build-cache 增表（SCHEMA_VERSION bump）
CREATE TABLE fn_defs(
  seq INTEGER PRIMARY KEY,            -- 比 occurrences：VACUUM 不重編——tie 先見者依據
  rel_path TEXT NOT NULL, symbol TEXT NOT NULL,
  start_line INTEGER NOT NULL, end_line INTEGER NOT NULL
);
CREATE INDEX idx_fn_defs_doc ON fn_defs(rel_path, start_line, end_line);
```

### 驗證策略

- **測試計畫**（`test_caller_edges.py` 新檔＋`test_scip_refs.py` 增模式測試）：
  - 單元：span 建構（4/3 元素兩形態＋0-based 轉換）、innermost 歸屬（巢狀 fn、同寬 tie、邊界行）、item-level 分離、BFS（depth 截斷、環偵測、按檔聚合）、`refs_rows` 兩 face 一致、schema bump 後舊 db 過期重建（既有三守衛測試形態沿用）
  - 整合：fixture 索引（`test_scip_refs.py` 既有 fixture 形態）端到端 callers/closure
  - 回歸：既有 query/audit 輸出 cmp 不變（NT 契約）
- **L4（NT 真索引，三源一致＝spec 成功條件②）**：
  1. `--callers EventStoreLifecycle.open --repo <NT>` → **17 callers**；判準＝計數＋分解吻合（17＝trait impl `open()`＋16 test fn）＋**名單級核對＝CLI 輸出 vs LSP 輸出兩活清單直接比對**
  2. LSP 對帳：curl `127.0.0.1:8000/mcp` `incomingCalls`（同標的）→ 同名單（lsp server 常駐已在；研究報告 §2.4 有同型前例）
  3. `--closure EventStoreLifecycle.open --depth 2` 起點一致＋環偵測正常
  4. SM-9 效能：closure 查詢秒級（sqlite 路徑）；protobuf/sqlite 兩 face 輸出一致
- **可選交叉**：scip-callgraph 對 NT 索引跑一輪對帳（研究報告建議 3，零工程——不作 gate）
- 已知未覆蓋：巨集展開體內歸屬正確性（ra 給展開後位置，歸屬到巨集叫用處所在 fn——研究報告 §5 判讀為語義合理，抽驗非全量）；96.9% 是歸屬覆蓋非全量正確率（§7 限制繼承）。

---

## 段 3：MCP 薄殼＋launchd＋ZCode user-level 掛接

### Context

**背景**：UC-5——缺差驅動路由內化進 server：LLM 用單一 MCP 接口完成語義面 UC（refs/callers/call_edges/closure/audit）。v0 工具面＝SCIP 家族四工具；snapshot/transition/hub_refs/tour 家族維持 CLI（skills subprocess 消費，freshness 免費）——**YAGNI，v1 圖層再擴**。

**UC 引用**：實作 UC-5；UC-1/UC-2/UC-4 的 MCP 化消費面。

**依賴關係**：subprocess S2 的 CLI（callers/closure）；plist 套路抄 `com.user.crg-mcp.plist`＋`com.mosaic.lsp-mcp.plist`（唯讀參考）；ZCode 掛接抄 lsp-python entry 形態。

**語義約束**：與 S2 共享「CLI＝唯一後端」（薄殼零工具邏輯）；與 S4 共享「server 名/URL/path 定稿即為 relay 文檔與 SKILL.md 的引用對象」。

**基礎設施盤點**：**官方 MCP SDK**（`mcp` 套件——`from mcp.server.fastmcp import FastMCP`、`mcp.run(transport="streamable-http")`、host/port 走 constructor：lsp_mcp `server.py` 同棧實證；**非**獨立 `fastmcp` 2.x 套件）；ZCode user-level MCP 註冊形態已驗（config.json `.mcp.servers` `{"type":"http","url":...,"timeoutMs":60000}`）；CRG 共享 server 驗證閉環 V1-V6 形態可抄。

**依賴錨點**：
- `scip_refs` CLI 介面 → 定義 `code_reality/scip_refs.py`（argparse 進入點）；消費＝mcp_server subprocess
- plist 慣例 → 定義 `~/Library/LaunchAgents/com.user.crg-mcp.plist`（KeepAlive/ThrottleInterval/log 路徑慣例）；消費＝新 plist 抄形態
- ZCode 掛接 → 定義 `~/.zcode/cli/config.json` `.mcp.servers`（**子樹 merge 非整檔覆蓋**——hooks 移植教訓：整檔覆蓋毀 config）

**技術選型**：官方 SDK HTTP server（lsp_mcp 同棧）；**工具呼叫形態＝每次 subprocess spawn**（`sys.executable -m code_reality.scip_refs ...`）——SM-10 保鮮決策：spawn 保鮮免 kickstart（editable→讀工作樹最新碼；代價 ~1s spawn，治理/錨定查詢可接受——**互動導航本就走 lsp_mcp，不搶這 1s**）。kickstart 僅 `mcp_server.py` 自身變更需要。

**成功標準**：四工具經 MCP 可用（`[SRC]` 透傳）＋SM-5（缺 repo_root loud error）＋SM-10（freshness probe）＋新 session 工具可見。

### Invariant Impact

- **受影響 domain invariant**：`[SRC]` 契約（無證據不輸出——subprocess 逐字透傳，薄殼不加不減；loud error 回應〔SM-4/SM-5〕本質無 `[SRC]`，屬 Always 條款邊界允許）；exit code 透傳（1/2 不偽裝成 0）。
- **critical path 觸及**：stderr 訊息（WARN/漂移/stamp 提示）必須可見——回應附 `[STDERR]` 段（管理訊息走 stderr 的既有設計延伸到 MCP 面）。
- **驗證對齊**：§4 V2（`[SRC]`＋18 refs）＋V3（缺參 loud）＋V4（freshness）。

### 核心實作要點

1. **依賴安裝**：`uv add mcp`（runtime deps 第二項——S1 pyproject 起步僅 protobuf）。
2. **新檔 `code_reality/mcp_server.py`**（薄殼：協議層＋subprocess，零工具邏輯）：
   - 工具：`refs(symbol, repo_root)`／`callers(symbol, repo_root)`／`closure(symbol, repo_root, depth=2)`／`audit(repo_root)`——**`repo_root` 必填**（SM-5：缺→loud error 帶修正指引文案，lsp_mcp payload 路由同型）
   - `_run(args)`：`[sys.executable, "-m", "code_reality.scip_refs", ...]`；timeout 上限（audit/重建場景）；回傳＝stdout 逐字＋非空 stderr 附 `[STDERR]` 段＋exit code 非 0 標注
   - index 參數：`--repo` 走 slot 解析（既有慣例），MCP 面不暴露 `--index` 顯式路徑（路由內化的具體化）
3. **launchd**：`~/Library/LaunchAgents/com.user.code-reality-mcp.plist`——`<new-repo>/.venv/bin/python -m code_reality.mcp_server`（host/port 在 code 內 constructor 定 `127.0.0.1:8200`）；WorkingDirectory＝新 repo root；KeepAlive＋ThrottleInterval 10＋`FASTMCP_LOG_LEVEL=WARNING`；log `~/.mosaic/logs/launchagent-code-reality-mcp.log`
4. **ZCode user-level 掛接**：config.json `.mcp.servers` 加 `"code-reality": {"type": "http", "url": "http://127.0.0.1:8200/mcp", "timeoutMs": 60000}`（merge 紀律；**工具面 per-session 快照——新 session 生效**）
5. Claude 端掛接：**v0 optional**（同 URL 一行；SKILL.md 記形態即可，不掛也行——skeleton 指定 ZCode）
6. **不做**：require-repo-root hook（server 端自己 loud——CRG hook 是 PyPI 不可改的補償，新 server 無此約束）；workspace pool（無狀態工具不需要——與 lsp_mcp 的架構差異點）

### Pseudo Code

```python
# code_reality/mcp_server.py（新——薄殼）
from mcp.server.fastmcp import FastMCP   # 官方 SDK——lsp_mcp server.py 同棧
mcp = FastMCP("code-reality", host="127.0.0.1", port=8200)  # host/port 走 constructor（lsp_mcp 註解明言）

def _run(args: list[str]) -> str:
    # subprocess.run([sys.executable, "-m", "code_reality.scip_refs", *args],
    #                capture_output=True, text=True, timeout=...)
    # return stdout + ("\n[STDERR]\n" + stderr if stderr else "") + exit≠0 標注

@mcp.tool
def refs(symbol: str, repo_root: str) -> str:
    """SCIP def/refs 查詢（兩符號形態消歧）。回應首行 [SRC]（有 stamp 時）。"""
    if not repo_root: raise ValueError("repo_root 必填——CRG 同型路由紀律（SM-5）")
    return _run([symbol, "--repo", repo_root])

@mcp.tool
def callers(symbol: str, repo_root: str) -> str: ...   # --callers（輸出含 site 行＝call_edges）
@mcp.tool
def closure(symbol: str, repo_root: str, depth: int = 2) -> str: ...  # --closure
@mcp.tool
def audit(repo_root: str) -> str: ...                  # --audit --repo（內部兩遍式含 graph_audit）

if __name__ == "__main__":
    mcp.run(transport="streamable-http")   # lsp_mcp 同款 transport 字面值
```

### 驗證策略

- **測試計畫**：`test_mcp_server.py`——`_run` 透傳（stdout/stderr/exit）、缺 repo_root loud、timeout 路徑（mock subprocess）。工具邏輯零測試負擔（薄殼；後端已有 S1/S2 測試）。
- **L4（CRG V1-V6 形態）**：
  - V1：`launchctl load` → curl `:8200/mcp` tools/list 四工具
  - V2：refs `EventStoreLifecycle.open`＋NT → `[SRC]`＋18 refs；callers → 17 callers（與 S2 CLI 同輸出）
  - V2b：closure via MCP → 與 CLI `--closure` 同輸出
  - V3：缺 repo_root → loud error 帶修正指引
  - V4（SM-10）：工作樹暫改 scip_refs 輸出 marker → 下一呼叫反映 → 還原（spawn 保鮮驗證）
  - V6：audit via MCP → 與 CLI 同輸出＋`[SRC]`＋`[STDERR]` WARN 可見
  - V7：server crash 後 KeepAlive 自起（launchctl kill 測）
- **跨 session 抽查（L6、非本 session L4——執行者＝user 或下一 session 首個動作）**：V5 新 session 見 `mcp__code-reality__*` 工具（per-session 快照；本 session 以 curl 代測）
- 已知未覆蓋：Claude 端掛接（v0 optional）；多 repo 併發查詢負載（單人使用形態，非風險）。

---

## 段 4：消費端切換 relay＋ai-rules 舊碼刪除

### Context

**背景**：D1 尾端——relay 消費端切換呼叫路徑（唯一變更＝`--project ~/Github/ai-rules`→`--project ~/Github/code-reality`），**切換確認後**刪 ai-rules 舊碼（最終零殘留）。

**UC 引用**：全部 UC 的消費面收斂；新 repo AGENTS.md Capabilities 涵蓋隨遷工具族（九工具）＋新能力（UC-1/UC-2/UC-4/UC-5＋hub_refs 安全網 UC-6 消費面）。

**依賴關係**：S1-S3 全驗後才啟動；NT/mosaic 是 repo 外 session（跨 repo 變更走 user relay——session 拓撲單一寫入者紀律：ai-rules 檔案只由 ai-rules session 改，NT/mosaic 端由各自 session 配合）。

**語義約束**：與 S1 共享「舊碼留到切換確認」；sidecar home 凍結（relay 須講明：slot/stamp/db 路徑全不變，只換 `--project`）。

**基礎設施盤點**：ai-rules 引用面＝段落 0 符號錨清單（執行前 `rg "uv run --project ~/Github/ai-rules" --type md` 重掃定全集）。**repo 外文檔面**（relay 一併交代、各 session 自改）：NT＝`nautilus_trader/ai-analysis/blueprint/AGENTS.md` 兩處命令字串＋`AGENTS.md` 的「ai-rules 的 code_reality」敘述；mosaic＝`tools/AGENTS.md`（呼叫形態＋「已遷 ai-rules」敘述）、`AGENTS.md`（boundary 命令）、`.code-reality.toml` 註解。rules/hooks/scripts/agents 零引用（已驗，無需動）。

**依賴錨點**：改寫對象＝段落 0 引用面清單（消費端）；定義端＝S1 新 repo。執行前重掃（防並行 session 新增引用——工作樹並行是常態）。

**技術選型**：relay 一次打包（A6 前例：多通知分次發＝過時快照溫床——一次發、含驗收命令＋文檔面同步清單）；刪碼前 gate＝回報＋user 確認。

**成功標準**：NT byte-identical（新路徑，三面）；mosaic hazard 驗收命令過；ai-rules 路徑導向零殘留（主判準，見要點 4）；consistency formal gate 過。

### Invariant Impact

- **受影響 domain invariant**：NT 契約最終確認（byte-identical 經新路徑）；ai-rules 刪碼後**消費端零斷裂**（所有活引用已改）。
- **critical path 觸及**：刪除路徑（git rm code_reality/ tests/＋pyproject entries）——刪錯時機＝消費端未切完即刪（D1 gate 防）。
- **驗證對齊**：§4 路徑導向零殘留掃＋consistency gate＋NT 側三面 byte compare 回報。

### 核心實作要點

1. **relay 一次打包**（user 轉傳，兩包，命令全形內嵌）：
   - **NT**：①治理鉤子內命令 `--project` 改新路徑；②sidecar/slot/stamp/db 路徑全不變；③**文檔面同步清單**（blueprint/AGENTS.md 兩處命令字串等）；驗收（自足式）＝舊路徑先跑存基準（query 兩形態＋`--audit`＋`graph_audit --json`）→切新路徑→逐項 `cmp`（138/861 與 430/233/861 為 NT 機器既有基準）＋（可選）MCP 面抽查
   - **mosaic**：①`hub_refs --hazard` 驗收命令新路徑（`uv run --project ~/Github/code-reality python -m code_reality.hub_refs ConsolidationCondition --repo .`）；②profile／hazard_registry 不動（repo 事實歸 repo）；③文檔面同步清單（tools/AGENTS.md、AGENTS.md、.code-reality.toml 註解）
2. **ai-rules 內部切換**（本 session 直改）：段落 0 引用面路徑改寫＋`AGENTS.md` 專案結構（code_reality/tests 條目改為「已遷 `~/Github/code-reality`」指向）＋SKILL.md 補 MCP 接口段（server URL＋工具清單＋repo_root 紀律）。
3. **新 repo 工具碼路徑字串 docs-fix**（獨立 commit，搬遷等價 commit 之後）：工具碼內 8 處 `~/Github/ai-rules` 字串（`scip_refs.py` docstring×5、`graph_audit.py` docstring、`boundary_build.py` 的 `[LOG]` stdout 查詢指引）→新路徑。**非 NT `--json` 契約面**（graph_audit `--json` 鍵不動；`boundary_build` stdout 非 NT 契約消費面），可改。
4. **刪碼（gate 後）**：`git rm -r code_reality/ tests/`＋pyproject 清理（`packages` 條目、dev protobuf、pytest 與 `integration` marker、ruff `extend-exclude` 的 `code_reality/scip_pb2.py` 死條目；build-system 處置＝移除 packages 後改非 package 形態（`[tool.uv] package = false` 或刪 `[build-system]`——實作時按 uv 行為驗證 `uv run scripts` 仍可用）；ruff 本體保留〔scripts/ 仍 lint〕）＋`uv lock` 重生。
5. **零殘留驗證**：**主判準（路徑導向）**＝`rg "uv run --project ~/Github/ai-rules" --type md` → 0（**豁免清單**：`skills/zcode-session-query/SKILL.md` 借 venv 跑自家腳本，非 code_reality 消費，不改）；輔判準＝`rg "code_reality" --type md` 人工判讀（活 skills 的 `python -m code_reality.<tool>` 工具名**必然存在**——非殘留信號；僅歷史文檔〔reports/specs/_done EP〕記載豁免）。
6. **consistency formal gate**（三檔：code-reality SKILL/CLAUDE/debrief——改動輻射處）＋bundle 部署。
7. `.agent-tmp/repo-poc/` 清理（真 repo 已取代 scratch；互動模式列清單詢問）。

### Pseudo Code

```
S4 執行序（gate 分明）：
1. relay 兩包組裝（含文檔面同步清單）→ user 轉傳
2. ai-rules 引用面路徑改寫＋AGENTS.md/SKILL.md 更新（本 session）
   └─ 此時 ai-rules skills 指新路徑；舊碼仍在（雙保險——新路徑壞可瞬間回頭）
3. 新 repo 工具碼 docs-fix commit（8 處路徑字串）
4. 〔gate：NT＋mosaic 回報 OK＋user 確認〕
5. git rm code_reality/ tests/ ＋ pyproject 清理 ＋ uv lock
6. 零殘留掃（主判準＋豁免）＋consistency gate＋POC 清理
7. commit（consent gate）
```

### 驗證策略

- **L4**：新路徑本地全工具抽跑（snapshot/transition/hub_refs/scip_refs/graph_audit 各一發——skills 存在性述語新路徑 exit 0）；NT 側三面 byte-identical 回報；mosaic hazard 命中回報。
- **文檔驗證**：主判準 rg 0 殘留（豁免清單核對）；`/consistency` formal（writer bias 防——memory 紀律：收尾必跑 formal gate 非 optional）。
- 已知未覆蓋：NT/mosaic 側執行細節（repo 外 session 職權——relay 驗收命令已內嵌回報格式）。

---

## 整合策略

- **跨段整合點**：S2 的 CLI＝S3 MCP 唯一後端；S1 的 editable freshness＝S3 spawn 保鮮前提；S4 relay 引用 S1-S3 定稿的 repo 名/路徑/URL。
- **baseline**: `3e985dc`（`/post-build`／`/code-review` 任務弧審查範圍邊界；implement 階段 1 補記工作樹實態）。
- **雙 repo 紀律**：S1-S3 commit 落新 repo（含 S4 前置的 docs-fix commit）；S4 的 skills/AGENTS.md 改動＋刪碼落 ai-rules（同 commit 帶走 finalization——build 階段 5a 結算）。
- **回退路徑**：S4 gate 前全程雙活（舊碼在、消費端未切）；gate 後回退＝git revert 刪碼 commit＋路徑改寫 commit（雙向門）。

## v1 展望（另行 EP，本 EP 不實作）

| 段 | 內容 | gate |
|----|------|------|
| S5 | B1（CRG 當內部圖引擎）vs B2（自建圖層）完整研究→決策報告 | **user 拍板（單向門）**；v0 圖層契約按 DIP 先定（兩實作都塞得進） |
| S6 | 圖層＋SCIP 邊源注入 graph.db（驗收＝NT graph_audit 861 缺差→0）＋impact/communities/hub/dead-code 上 MCP；UC-6 資料源升級（hub_refs 吃正確 Rust 邊） | S5 裁決後 |
| S7 | CRG MCP 退役＋crg-query skill 收斂（三路由文件→二） | S6 驗收後＋退役評估 |
| 遠期 | UC-7 發佈形態（plugin market：marketplace.json＋MCP 啟動命令一條——薄殼天然滿足）；**lsp_mcp home 遷移**（見下） | 發佈前 review 授權 notices |

**lsp_mcp home 遷移（2026-08-25 評估，候選卡）**：D4 的「進程分離」維持（thin-shell spawn 保鮮與 LSP 常駐 workspace 狀態本質互斥——統包成一進程會破壞 SM-10 保鮮決策且失敗域綁死）；但 lsp_mcp 的 **code home** 從 `mosaic_alpha/tools/lsp_mcp/`（泛化機械住消費端 repo＝層級倒置）遷入新 repo 作第二 module（獨立 plist、port 8000 不動、ZCode entry 零改）——層級歸位＋部署一條龍＋UC-7 plugin 未來同包。時點 v1+（多語言版 08-25 才 commit、Rust 層僅機制驗證，先穩定；與 v0 段 1-4 零耦合可獨立做）。**Ask First：user 拍板後開卡**。

## 收尾步驟（build 階段 5 執行）

1. **Capabilities＋Kanban**：新 repo `AGENTS.md` Capabilities 表格涵蓋**隨遷工具族全員＋新能力**（工具表對齊 skills/code-reality SKILL.md 工具表：snapshot/transition/hub_refs/runtime_edges/boundary 族/tour 族/graph_audit/scip_refs＋新 callers·closure＋MCP 接口——各附入口 CLI＋MCP 工具名＋✅；從 SM 提煉「消費場景」自包含一句話入備註）；ai-rules `.kanban/` 卡片搬 Done/（EP 追蹤卡＋兩能力卡）；EP 歸檔 `_done/`。
2. **SYSTEM-MAP.md**：不適用（本 repo 無此檔）。
3. **instruction 檔**：新 repo AGENTS.md（S1 建、收尾補 Capabilities）；ai-rules `AGENTS.md` 專案結構＋`skills/code-reality/SKILL.md`（工具表＋MCP 段＋路徑）＋`skills/CLAUDE.md` 索引行 description 同步——S4 已改，收尾核對。
4. **/audit-test**：對 S2/S3 新增測試跑品質稽核（mock 健康度——`_run` 的 subprocess mock 是否 vacuous；歸屬語意測試是否測行為非實作）。

## EP Review Record

2026-08-25 四軌獨立審查（結構／完整性遺漏／UC 覆蓋／合規兜底——fresh eyes Explore agents，全部 findings 已 judge）。**採納 31 項全修**（摘要）：

| 軌 | 關鍵 findings（已修入上文） |
|----|------|
| 結構 | 🔴P1 `face.find_refs()` 介面不存在（`refs()` 回格式化字串）→ S2 補 `refs_rows()`/`fn_spans()` 結構化存取器宣告＋禁解析字串捷徑；循環 import 風險 → caller_edges 零 scip_refs import、span 組裝住 scip_refs 側；MCP 框架＝官方 SDK 非 fastmcp 套件＋`uv add mcp` 落步驟；S4 零殘留判準字面不可達 → 改路徑導向主判準；fn_defs 補 seq PK（VACUUM 坑）；enc 行號 0-based→+1 轉換 |
| 完整性 | 計數勘誤（20 .py／24 test 檔／integration 數字程序化）；工具碼內 8 處 ai-rules 路徑字串 → S4 docs-fix commit；SKILL.md 引用漏 description/定位句 → 符號錨清單；ruff extend-exclude 死條目、build-system 處置 → S4 清理清單；NT/mosaic 文檔面命令字串 → relay 包補同步清單 |
| UC 覆蓋 | call_edges 有名無實（雙軌命中）→ `--callers` 輸出含 site 行＝邊集承接＋成功條件①對應；UC-6 盤點「無影響」與 S4 relay 矛盾 → 改「搬家＋切路徑」；graph_audit `--json` 缺 byte-compare（SM-7 主輸入）→ S1 並跑＋S4 NT 驗收三面 cmp；段落 0 graph_audit 離群句修；SM-3/4 錨改 pytest＋S1 抽跑；17 callers 判準改「計數＋分解＋兩活清單直接比」；closure MCP 實測 V2b；v1 補 dead-code；收尾 Capabilities 補隨遷全員 |
| 合規 | 本地 NT 索引在 legacy slot 根目錄（實證）→ S1 L4 前置「索引歸位」（驗 meta.json 歸屬後 mv）；zcode-session-query 假陽性（雙軌命中）→ 零殘留豁免清單；S4 NT 驗收基準來源未定義 → 自足式（舊路徑存基準→切新→cmp）；V5 分離為跨 session 抽查（L6）；pytest 背景跑；loud error 無 `[SRC]` 邊界允許明文化 |

**不採納 1 項**：spec「400+ tests」數字過時（實際 381）——EP 已以「S1 實跑記基準數」程序取代絕對數字，不回改 spec（決策真相源檔案，數字修訂非本 EP 職權）。
