# [cr-dist] PyPI 首發後的 ai-rules 安裝面翻轉（cargo→uv tool install）

## 目標

CR 分發軸改 PyPI platform wheels（`ep-pypi-wheel-distribution.md`，maturin／ruff-pyrefly 模式）首發落地後，ai-rules 端安裝面文檔從 cargo 敘述翻轉為消費者面 `uv tool install`。

## 觸發條件（未滿足前本卡不動）

- CR repo `ep-pypi-wheel-distribution.md` 的 **S3（PyPI 首發）落地**——執行前先查該 EP 進度；未落地則留 Backlog。

## 內容（CR 2026-08-28 告知的三項）

1. `skills/code-reality/SKILL.md` 安裝段：`cargo install` 三條降為 **developer face**；消費者面改 `uv tool install`（三 dist：code-reality／pyrefly-producer／code-reality-lsp-bridge）＋`uvx` 免裝路徑
2. `rules/lsp-navigation.md`／`rules/tool-discipline.md` 若規則文本提及安裝方式，同步翻轉（含存在性偵測段的 cargo 敘述）
3. 翻轉時對齊 CR repo README Quickstart（EP S4 已處理 CR 側）

## 驗收標準

- `rg 'cargo install' skills/ rules/` 命中僅剩 developer-face 語境
- bundle redeploy 3/3；消費者面敘述與 CR Quickstart 一致

## 備註

- 已生效部分（無需本卡動作）：plugin 0.1.3 CC 相容化（`9f25969`——`.claude-plugin/` manifest 單源＋雙市場檔）
- 相關裁定：CRG 式 setup 子命令＝另開薄弧；私有 index＝YAGNI

## Grounding 掃描（2026-08-28 W6 session 記錄——觸發複查時可跳過重掃）

- 觸發狀態：**未滿足**——CR repo 無 `crates/*/pyproject.toml`、無 `.github/workflows/`、git log 無分發軸 commit（HEAD `9f25969` 僅 plugin 0.1.3）→ 本卡留 Backlog
- 翻轉面盤點：`rg 'cargo install|cargo run --release|uv tool install|uvx' skills/ rules/ agents/` 僅命中 `skills/code-reality/SKILL.md` 三處（L17 存在性偵測段＋L55-56 pyrefly-index）——上列第 2 項（rules 端）**空集合**：lsp-navigation.md 唯一 install 提及是「pyright-langserver 不可解除安裝」（非安裝方式敘述），tool-discipline.md 零命中
- W6（語法層互補 producer 評估）互動：W6 證據傾向不建→不增 dist、零影響；若裁決「建」→ S1（多一份 pyproject）/S2（CI matrix）/S3（首發範圍）各加一列——EP 在 S1 前修改成本近零

## Grounding 補記（2026-08-29 S2 修剪）

拆遷 EP S2 修剪 `skills/code-reality/SKILL.md`（刪已搬 CR 的工具事實塊＋錨點化）——L17 存在性偵測段與 pyrefly 安裝行**內容不變但行號漂移**；flip 觸發時重 `rg 'cargo install'` 定位，勿沿用舊行號。
