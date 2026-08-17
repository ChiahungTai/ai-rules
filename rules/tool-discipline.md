---
harness-scope: neutral
---

# 工具紀律

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

> 違反 = 閘門失效或工具誤用。每次都遵守。

## 工具選擇原則

- 語義查詢用 LSP（goToDefinition / findReferences / hover），文字搜尋用 `rg`，檔案搜尋用 `fd`（決策樹見 [lsp-navigation.md](lsp-navigation.md)）
- **Agent prompt 必須指定工具**：spawn agent 時，根據任務性質在 prompt 中明確寫「用 LSP hover/ goToDefinition 查簽名」或「用 rg 搜文字」。禁止 agent prompt 只寫「讀取/驗證」不指定工具

## Python 命令執行

- 所有 Python 命令用 `uv run` 前綴（`uv run python script.py`、`uv run pytest`）
- 禁止：`python`、`python3`、`PYTHONPATH=$PWD`

## 檔案修改禁令

- 禁止 `sed` 修改 `.py`/`.md`/`.yaml`/`.json`/`.toml`（sed 不理解程式碼或 Markdown 語法，批次替換常破壞縮排、誤改字串/註解、毀損多行結構）
- sed 唯一允許用途：過濾日誌輸出、處理純文字資料流（不修改原始檔）
- **Edit/Write 前目標檔必須已 Read**（harness 硬規則）：未 Read 直接改 = 工具失敗；Read 後檔案又被外部改（linter/hook/另 session）= 過時失敗 → re-Read 再改。批次修改前把目標檔 Read 放同批前置（真實案例：五天實測 142 次 Edit 失敗，其中 120 次是「未 Read 先改」48 次 + 「Read 過時」72 次）

## 背景執行（不阻塞對話）

- `pytest` 用背景跑（Claude: `run_in_background: true`；其他 harness 用各家背景機制）；例外：併入機械驗證組合命令的段級短測試（單檔、秒級）隨組合命令跑（見下「獨立呼叫批次化」）
- **Subagent spawn 預設背景**：Agent tool 呼叫帶背景參數（ZCode: `run_in_background: true`——runtime 實測有效（2026-08-14），官方文檔未記載此參數、僅說前台/後台由主 Agent 決定；Claude 2.1.198+ 已預設背景免動作）。主對話回報「進行中」後結束 turn——使用者可繼續對話，subagent 完成後結果自動回到主對話接手
- 例外（前台）：結果是當前步驟立即依賴且預期 <30s 的短 probe（如載入驗證）
- 為什麼：前台 spawn 佔住主對話 turn，使用者無法插話——長任務（review、大範圍 research）前台 = 對話卡死；背景不改變結果可用性，只改變等待方式
- 注意（ZCode）：背景執行的 Explore 強制唯讀（安全設計）；subagent 定義檔**不支援** `background` 欄位（Claude 支援——frontmatter `background: true` 在 Claude 端有效、ZCode 靜默忽略）——ZCode 端背景化是 spawn 端行為，定義檔控制不到

## 閘門命令禁 pipe 到 tail/grep

> **核心原則**：exit code 是閘門依據，pipe 會被最後一環蓋掉。

`uv run mypy . 2>&1 | tail -15` 回報的是 `tail` 的 exit 0，不是 mypy 的 7 errors → 誤判「全綠」。

- 需看 output 用重導檔案再 Read（`uv run mypy . > /tmp/mypy.log` 再 Read）
- 或 `set -o pipefail` 讓 pipe exit = 最後一個非 0 退出碼

## 獨立呼叫批次化

> **核心原則**：獨立無依賴的工具呼叫在**同一個 block 一次發出**——每個獨立 call 各耗一個 model request，逐一發純浪費。

- **依賴判準**：下一步需要本步**結果**才是依賴；「同類操作」不是依賴。多個 Read、rg/fd、git 查詢、LSP 查不同 anchor、跨檔 Edit、同檔不同位置（old_string 不重疊）的 Edit——皆獨立，同 block 發。**順序依賴**（Edit 前的 Read——需要的是 read-state 註冊非輸出值）可同 block：block 內按序執行（實測），Read 放批內 Edit 前
- **機械驗證序列**（lint/type/test）組成單一命令一次 call：輸出重導檔案再 Read + 失敗段標記（`uv run cmd1 > out 2>&1 || echo "cmd1:FAIL"; uv run cmd2 > out2 2>&1 || echo "cmd2:FAIL"`——無 FAIL 行 = 全綠；遵守上方 no-pipe-tail、避開 `$?` 展開）
- **Edit 批次化**：先規劃整批修改點再一次 block 發出；同檔鄰近的一行式小修優先合併為單一較大 Edit
- 實測（2026-08 五天 ZCode）：~3/4 request 只帶 1 tool call、8 成 Bash 秒級完成、1/3 Edit 為單行——批次化的節省即來自這些

## 輸出慣例

- 輸出使用繁體中文 + 英文術語
