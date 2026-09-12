---
harness-scope: neutral
---

# 工具紀律

## 工具選擇原則

符號→code-reality、型別→bridge、文字→rg、檔案→fd（詳 [symbol-query-routing.md](symbol-query-routing.md)）。視覺判讀用 vision-review agent，禁主 session 直接 Read 圖（佔滿主 context），verdict 見 agent 定義；spawn prompt 必指定工具（如 LSP hover、rg），不能只寫「讀取/驗證」。

## Skill 調用紀律

意圖對應既有 skill 時，主 session 先讀再動手/派發；換 agent 不換方法論。真實案例：裸派 EP 跳過 execution-plan skill，導致 hook 殼與 post-build 銜接物全缺。

## Python 命令執行（canonical，單一源）

一律 `uv run python`/`uv run pytest` 前綴，禁 `python`/`python3`/`PYTHONPATH`（含 `=$PWD` 形式）。多行 `python -c` 禁換行後 `#` 註解；改單行或 .py。pytest 背景跑（見「背景執行」）；另禁外部 `timeout`/`gtimeout`（macOS 無此命令；需逾時控制的替代法見 debugging-and-error-recovery skill）。ModuleNotFoundError 等環境/依賴錯誤的處置見 debugging-and-error-recovery skill。

## zsh 動態 flag 組合（陣列、禁純量）

zsh 未引號變數不 word-split；動態 flags 用 `args=(--flag 1)`＋`cmd "${args[@]}"`，禁 `"--flag 1"` 純量（真實案例：`--primary 1` 被當單參數而 argparse 拒絕）。≤2 組合可分支、單 flag 用 `--flag=1`；禁 `setopt shwordsplit`/`${=var}`。

## 檔案修改禁令

- 禁 sed 修改 .py/.md/.yaml/.json/.toml；只可過濾流。
- Edit/Write 前先 Read；外部改動後重讀。共享檔先 rg 自己的唯一錨點，old_string 不包他人行；搬移拆精準 Edit。

## Edit 失敗處置階梯（canonical）

Edit 失敗 → 先 re-Read 取得當前狀態；第二次同型 not found 後停止盲試（禁第三次）。文字肉眼在場卻配不上 → 用 Python repr 唯讀診斷 bytes（唯讀查證，不違反 sed/Python 替換禁令）。接著縮小 old_string（多位元組字元跨行匹配常是肇因）；仍失敗才 full Read＋Write 整檔覆寫——前提：剛完成完整 Read 且確認無並行變更（整檔覆寫放大 blast radius）。

## 背景執行

pytest/長命令、spawn agent 背景執行：spawn **一律明帶 `run_in_background: true`**（各端皆安全；ZCode 原生預設前台——省略即前台阻塞主對話，user 插話中斷會連帶殺 agent），spawn 後回報進行中即結束 turn 等完成通知；**ZCode 端 Agent 派發有背景 gate（rewrite 式）：省略參數不再等於前景——自動補背景，真要前景須 prompt 開頭帶 `[fg]`**；背景等待禁長等（行為契約見 **agent-workflow skill「Spawn 預設背景」**）；<30s 前台短 probe 例外（現須配 `[fg]` 逃生口）與「spawn 不可繞 Bash timeout」真實案例已下沉同處；依 harness 機制執行，禁臆造工具。

## 閘門命令禁 pipe 到 tail/grep

pipe 預設回最後程序 exit，會把失敗偽裝綠燈；gate 輸出重導再 Read，或 `set -o pipefail`。禁憑 tail/grep exit 宣稱通過。

## Read 紀律（context 佔用）

已完整讀過的檔案重查用 rg/offset/limit，禁再全讀；大檔具體問題先定位，首次理解/小檔可全讀。真實案例：86KB 檔重讀十九次，重複佔滿 context。

## 獨立呼叫批次化

獨立 Read/搜尋/git/LSP/不重疊 Edit 同 block 發；只有下步需本步結果才算依賴。lint/type/test 可組單命令，各自重導並標失敗段再 Read；保護 exit code，避開不必要 `$` 展開。

## 輸出慣例

繁體中文＋英文術語。
