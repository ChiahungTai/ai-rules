---
harness-scope: neutral
---

# 工具紀律

## 工具選擇原則

符號→code-reality、型別→bridge、文字→rg、檔案→fd（詳 [symbol-query-routing.md](symbol-query-routing.md)）。視覺判讀用 vision-review agent，禁主 session 直接 Read 圖（圖片佔滿主 context）；verdict 規範見 agent 定義。spawn prompt 必指定工具（如 LSP hover、rg），不能只說讀取/驗證。

## Skill 調用紀律

意圖對應既有 skill，主 session 先讀並遵循再動手/派發；可把 skill 路徑注入 agent prompt。換 agent 不換方法論。真實案例：裸派 EP 跳過 execution-plan skill，導致 hook 殼與 post-build 銜接物全缺。

## Python 命令執行

一律 `uv run python`／`uv run pytest`，禁 python/python3/PYTHONPATH=$PWD。多行 python -c 不寫換行後 # 註解（部分 harness 觸發權限確認）；改乾淨單行或 .py。

## zsh 動態 flag 組合（陣列、禁純量）

zsh 未引號變數不 word-split；用 `args=(--flag 1)`＋`cmd "${args[@]}"`，禁把 `"--flag 1"` 純量交 cmd（真實案例：`--primary 1` 純量被當單參數，argparse 拒絕）。≤2 種組合可寫分支，單 flag 用 --flag=1；禁 setopt shwordsplit／${=var}。

## 檔案修改禁令

- 禁止 sed 修改 .py/.md/.yaml/.json/.toml（不理解語法結構）；僅能過濾流，不改源檔。
- Edit/Write 前先 Read；外部改動後重新 Read。共享檔先 rg 自己行的唯一錨點，old_string 不包他人行；搬移拆精準 Edit。
- old_string 連續兩次 not found，改用 Python repr 檢查 bytes 並重組，禁第三次盲試。

## 背景執行（不阻塞對話）

pytest 背景跑（依 harness 機制，不臆造工具），短測試可併機械驗證命令；spawn 預設背景；長命令（>10 分）背景跑是預設。spawn agent 不是繞 Bash timeout 的手段（約束誤判實證）——真實案例：bridge 轉發形態以為 Bash 只能 600s（實際 run_in_background 從頭可用）→轉發沉澱 memory、wrapper 存在讓形態顯得官方，成本＝agent 開銷＋間接層＋收斂路徑變長。

先做獨立前台工作，無前台工作就回報進行中、結束 turn 等通知；禁 TaskOutput(block=true) 長等（主對話中斷時 agent 連帶 killed、產出遺失）；前台/block=true 僅結果立即依賴的 <30s 短 probe。

## 閘門命令禁 pipe 到 tail/grep

pipe 預設回最後程序 exit，會把失敗偽裝綠燈；gate 輸出重導檔案再 Read，或 set -o pipefail 保留失敗。不可憑 tail/grep exit 宣稱驗證通過。

## Read 紀律（context 佔用）

已完整讀過的檔案重查用 rg 定位片段或 offset/limit，禁再全讀；未讀大檔若只答具體問題，也先定位。首次理解/小檔可全讀。真實案例：86KB 檔重讀十九次，重複佔滿 context。

## 獨立呼叫批次化

獨立 Read/搜尋/git/LSP/不重疊 Edit 同 block 發，避免每 call 重送 context；只有下步需本步結果才算依賴。lint/type/test 可組單命令，各自重導輸出並標失敗段再 Read；遵守 exit code 保護，避開不必要 $ 展開。

## 輸出慣例

繁體中文＋英文術語。
