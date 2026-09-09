---
harness-scope: neutral
---

# 工具紀律

## 工具選擇原則

符號→code-reality、型別→bridge、文字→rg、檔案→fd，詳 [symbol-query-routing.md](symbol-query-routing.md)。

視覺判讀用 **vision-review agent**（視覺錨點＋verdict 格式＋read-only），禁主 session 直接 Read 圖；圖片會佔滿主 context。agent loop 須可裁切/跨圖佐證，畫面無法證明的就標無從核實，不能用單發 image-analysis 代替。spawn prompt 必指定工具（如 LSP hover 查簽名、rg 搜文字），不能只說讀取/驗證。

## Skill 調用紀律（意圖→skill 先載入）

意圖對應既有 skill，主 session 先讀並遵循，再動手/派發；可把 skill 路徑注入 agent prompt。換 agent 不換方法論。真實案例：裸派 EP 跳過 execution-plan skill，導致 hook 殼與 post-build 銜接物全缺，下游合法跳過。

## Python 命令執行

一律 `uv run python`／`uv run pytest`，禁 python/python3/PYTHONPATH=$PWD。多行 python -c 不寫換行後 # 註解，部分 harness 會觸發權限確認；改乾淨單行或 .py（Claude 特例見 bash-hard-rules）。

## zsh 動態 flag 組合（陣列、禁純量）

zsh 未引號變數不 word-split；用 `args=(--flag 1)`＋`cmd "${args[@]}"`，禁把 `"--flag 1"` 純量交 cmd。≤2 種組合可寫分支，單 flag 用 --flag=1；禁 setopt shwordsplit 或 ${=var} 改語義。真實案例：NT chain_tour 的 --primary 1 純量被當單參數，argparse 拒絕。

## 檔案修改禁令

- **禁止 sed 修改 .py/.md/.yaml/.json/.toml**，它不理解語法結構；僅能過濾 log/純文字流而不改源檔。
- Edit/Write 前先 Read；外部改動後重新 Read。共享檔先 rg 自己行的唯一錨點，old_string 不包他人行；搬移拆精準 Edit，改後重讀對照。
- old_string 連續兩次 not found，改用 Python repr 檢查 bytes 並重組，禁第三次盲試。

## 背景執行（不阻塞對話）

以下依 harness 可用機制執行，不臆造工具：pytest 背景跑（Claude run_in_background），短測試可併機械驗證命令。spawn 預設背景（ZCode 顯式 run_in_background；Claude 原生預設），Explore 背景唯讀，定義檔 background 欄位僅 Claude 有效。

先做獨立前台工作，無前台工作就回報進行中、結束 turn 等通知；禁 TaskOutput(block=true) 長等，以免主對話被中斷時 agent 連帶 killed、產出遺失。前台/block=true 僅結果立即依賴的 <30s 短 probe。

## 閘門命令禁 pipe 到 tail/grep

pipe 預設回最後程序 exit，會把失敗偽裝綠燈。gate 輸出重導檔案再 Read，或 set -o pipefail 保留失敗；不可憑 tail/grep exit 宣稱驗證通過。

## Read 紀律（context 佔用）

已完整讀過的檔案重查用 rg 定位片段或 offset/limit，禁再全讀；未讀大檔若只答具體問題，也先定位。首次整體理解、小檔可全讀。真實案例：86KB 檔重讀十九次，重複佔滿 context。

## 獨立呼叫批次化

獨立 Read/搜尋/git/LSP/不重疊 Edit 同 block 發，避免每 call 重送 context；只有下步需本步結果才算依賴。Read→Edit 可同 block 但須依序先讀；同檔鄰近小改合併精準 Edit。

lint/type/test 可組單命令，各自重導輸出並標失敗段，再 Read；遵守 exit code 保護，避開不必要 $ 展開。

## 輸出慣例

繁體中文＋英文術語。
