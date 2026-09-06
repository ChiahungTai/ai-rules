---
harness-scope: neutral
---

# 工具紀律

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

> 違反 = 閘門失效或工具誤用。每次都遵守。

## 工具選擇原則

- 工具四路路由（符號→code-reality、型別→bridge、文字→rg、檔案→fd）見 [lsp-navigation.md](lsp-navigation.md)；本檔載紀律與陷阱
- **視覺判讀（截圖/圖表/證據影像/UI 驗收）→ vision-review agent**（合約式 dispatch：視覺錨點＋verdict 格式＋read-only），**禁主 session 直接 Read 圖檔**——圖像 token 全量駐留主 context、多張即灌爆（GLM 5.3 實測），agent 在自身 context 消化、主 session 只收文字 verdict；亦非單發 image-analysis MCP——差距在 agent loop 的查證迴路＋合約紀律（截切、跨圖佐證、「畫面內無 X 則宣稱無從核實」），非模型能力
- **Agent prompt 必須指定工具**：spawn agent 時，根據任務性質在 prompt 中明確寫「用 LSP hover/ goToDefinition 查簽名」或「用 rg 搜文字」。禁止 agent prompt 只寫「讀取/驗證」不指定工具

## Skill 調用紀律（意圖→skill 先載入）

> **核心原則**：意圖對應到既有 skill 時，主 session 必須**先載入該 skill 並按其流程執行**，才分派或動手。skill 是**編排者的方法論**，agent 是執行載體——「用 agent 做 X」只換載體、不換方法論：載入 skill 後再分派（自寫遵循，或把 skill 路徑注入 agent prompt 令其先讀再做）。

- 繞過 skill 的失敗形態是**流程產物整線靜默缺席**（hook 殼、delta tour、post-build 銜接物）——下游步驟看到前置物不存在會「合法跳過」，事後不可見
- 真實案例：agent 裸寫 EP、主 session 未載 execution-plan skill → hook 殼與 post-build 階段 5 整線合法跳過——問題在編排者跳過方法論，不在載體

## Python 命令執行

- 所有 Python 命令用 `uv run` 前綴（`uv run python script.py`、`uv run pytest`）
- 禁止：`python`、`python3`、`PYTHONPATH=$PWD`

## Bash `python -c` 禁止寫註解

> **`python -c` 是 AI 自用驗證，不需人類可讀註解。** 多行 `python -c` 中換行後接 `#` 註解會觸發部分 harness 的權限確認（Claude CLI 無法判斷跨行 `#` 是否被注入惡意內容，每次需人工確認）。要驗證想法就寫乾淨單行，或落成 `.py` 檔（Claude: `bash-hard-rules.md`）。

## zsh 動態 flag 組合（陣列、禁純量）

> **harness shell 是 zsh——未引號變數不做 word-split（與 bash 慣性相反）**：bash 慣性的 `cmd $extra` 在 zsh 把 `--flag 1` 整串當單一參數，argparse 報 `unrecognized arguments`。

- 迴圈/條件組動態 CLI flags：❌ `extra="--flag 1"; cmd $extra`；✅ `args=(--flag 1); cmd "${args[@]}"`（bash/zsh 同語義）
- 組合 ≤2 直接寫死分支命令；單一 flag 用 `--flag=1` 單 word 形式
- 禁 `setopt shwordsplit`（全局語義突變）與 `${=var}`（zsh 專屬不可攜）
- 真實案例：2026-08-26 NT chain_tour 批次重產 `--primary 1` 純量整串傳入 → `unrecognized arguments`

## 檔案修改禁令

- 禁止 `sed` 修改 `.py`/`.md`/`.yaml`/`.json`/`.toml`（sed 不理解程式碼或 Markdown 語法，批次替換常破壞縮排、誤改字串/註解、毀損多行結構）
- sed 唯一允許用途：過濾日誌輸出、處理純文字資料流（不修改原始檔）
- **共享檔案 Edit 邊界**：多 session 並行寫入檔 Edit 前先 rg 定位自己行的唯一錨點——old_string 誤包他人行＝靜默刪除他人內容（搬移拆兩個精準 Edit、編後重讀對照行數）；old_string 連續兩次 not found＝context 渲染與實際 bytes 有出入——改以 python repr 讀目標行重組，禁第三盲重試。

- **Edit/Write 前目標檔必須已 Read**（harness 硬規則）：未 Read 直接改 = 工具失敗；Read 後檔案又被外部改（linter/hook/另 session）= 過時失敗 → re-Read 再改。批次修改前把目標檔 Read 放同批前置（實測：142 次 Edit 失敗中 120 次屬此二形態）

## 背景執行（不阻塞對話）

- `pytest` 用背景跑（Claude: `run_in_background: true`；其他 harness 用各家背景機制）；例外：併入機械驗證組合命令的短測試隨組合命令跑（見下「獨立呼叫批次化」）
- **Subagent spawn 預設背景**：Agent tool 呼叫帶 `run_in_background: true`（ZCode 實測有效；Claude 已預設背景）。主對話回報「進行中」後結束 turn——subagent 完成後自動回到主對話
- **背景 agent 的收法**：spawn 後**結束 turn 等完成通知**，禁用 `TaskOutput(block=true)` 長阻等——阻等卡住主對話且被中斷時 agent 連帶被殺（status=killed，結果遺失）。`block=true` 僅限 <30s 短 probe；有前台工作先做，通知到再接手
- 前台與背景取捨：前台佔住主對話 turn 使長任務卡死，背景不改結果可用性；例外（前台）為結果立即依賴的短 probe，Explore 背景強制唯讀，定義檔 `background` 欄位僅 Claude 有效

## 閘門命令禁 pipe 到 tail/grep

> **核心原則**：exit code 是閘門依據，pipe 會被最後一環蓋掉。

`uv run mypy . 2>&1 | tail -15` 回報的是 `tail` 的 exit 0，不是 mypy 的 7 errors → 誤判「全綠」。

- 需看 output 用重導檔案再 Read（`uv run mypy . > /tmp/mypy.log` 再 Read）
- 或 `set -o pipefail` 讓 pipe exit = 最後一個非 0 退出碼

## Read 紀律（context 佔用）

- **同 session 已完整讀過的檔案，重查細節禁再無參數全讀**——每次全讀 = 同內容全量重複注入 context（實測：86KB 檔單 session 重讀 19 次、每次 25-30K tokens）。重查改用：`rg -n -C 10 "關鍵詞" <file>`（回片段）或片段 Read（`offset`/`limit`——已實測滿足 Edit 的 read-state 前置，可同 block，順序依賴見下「獨立呼叫批次化」）
- 為回答**具體問題**而讀未讀過的大檔 → 先 `rg -n` 定位再讀片段；首次為**整體理解**全讀可接受（浪費在重讀，不在首讀）
- 小檔（數 KB 內）全讀無妨；重查本來就是 1 request，換成輸出小兩個數量級的形態——request 數不變、context 大減

## 獨立呼叫批次化

> **核心原則**：獨立無依賴的工具呼叫在**同一個 block 一次發出**——每個獨立 call 各耗一個 model request（各帶全 context 重送），逐一發是 token/延遲/退化的三重浪費，與計費模型無關。

- **依賴判準**：下一步需要本步**結果**才是依賴；「同類操作」不是依賴。多個 Read、rg/fd、git 查詢、LSP 查不同 anchor、跨檔 Edit、同檔不同位置（old_string 不重疊）的 Edit——皆獨立，同 block 發。**順序依賴**（Edit 前的 Read——需要的是 read-state 註冊非輸出值）可同 block：block 內按序執行（實測），Read 放批內 Edit 前
- **機械驗證序列**（lint/type/test）組成單一命令一次 call：輸出重導檔案再 Read + 失敗段標記（`uv run cmd1 > out 2>&1 || echo "cmd1:FAIL"; uv run cmd2 > out2 2>&1 || echo "cmd2:FAIL"`——無 FAIL 行 = 全綠；遵守上方 no-pipe-tail、避開 `$?` 展開）
- **Edit 批次化**：先規劃整批修改點再一次 block 發出；同檔鄰近的一行式小修優先合併為單一較大 Edit
- 實測：~3/4 request 只帶 1 tool call——批次化的節省即來自這些

## 輸出慣例

- 輸出使用繁體中文 + 英文術語
