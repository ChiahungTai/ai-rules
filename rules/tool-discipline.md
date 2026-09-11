---
harness-scope: neutral
---

# 工具紀律

## 工具選擇原則

符號→code-reality、型別→bridge、文字→rg、檔案→fd（詳 [symbol-query-routing.md](symbol-query-routing.md)）。視覺判讀用 vision-review agent，禁主 session 直接 Read 圖（佔滿主 context），verdict 見 agent 定義；spawn prompt 必指定工具（如 LSP hover、rg），不能只寫「讀取/驗證」。

## Skill 調用紀律

意圖對應既有 skill 時，主 session 先讀再動手/派發；換 agent 不換方法論。真實案例：裸派 EP 跳過 execution-plan skill，導致 hook 殼與 post-build 銜接物全缺。

## Python 命令執行

一律 `uv run python`/`uv run pytest`，禁 python/python3/PYTHONPATH=$PWD。多行 `python -c` 禁換行後 `#` 註解；改單行或 .py。

## zsh 動態 flag 組合（陣列、禁純量）

zsh 未引號變數不 word-split；動態 flags 用 `args=(--flag 1)`＋`cmd "${args[@]}"`，禁 `"--flag 1"` 純量（真實案例：`--primary 1` 被當單參數而 argparse 拒絕）。≤2 組合可分支、單 flag 用 `--flag=1`；禁 `setopt shwordsplit`/`${=var}`。

## 檔案修改禁令

- 禁 sed 修改 .py/.md/.yaml/.json/.toml；只可過濾流。
- Edit/Write 前先 Read；外部改動後重讀。共享檔先 rg 自己的唯一錨點，old_string 不包他人行；搬移拆精準 Edit。
- old_string 連續兩次 not found → 用 Python repr 查 bytes 並重組，禁第三次盲試。

## 背景執行

pytest/長命令、spawn 背景預設、背景等待禁長等（harness-specific 工具有名差異——行為契約見 **agent-workflow skill「Spawn 預設背景」**）；<30s 前台例外與「spawn 不可繞 Bash timeout」真實案例已下沉同處；依 harness 機制執行，禁臆造工具。

## 閘門命令禁 pipe 到 tail/grep

pipe 預設回最後程序 exit，會把失敗偽裝綠燈；gate 輸出重導再 Read，或 `set -o pipefail`。禁憑 tail/grep exit 宣稱通過。

## Read 紀律（context 佔用）

已完整讀過的檔案重查用 rg/offset/limit，禁再全讀；大檔具體問題先定位，首次理解/小檔可全讀。真實案例：86KB 檔重讀十九次，重複佔滿 context。

## 獨立呼叫批次化

獨立 Read/搜尋/git/LSP/不重疊 Edit 同 block 發；只有下步需本步結果才算依賴。lint/type/test 可組單命令，各自重導並標失敗段再 Read；保護 exit code，避開不必要 `$` 展開。

## 輸出慣例

繁體中文＋英文術語。
