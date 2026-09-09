---
harness-scope: neutral
---

# 修改後必須執行驗證

## 核心原則

語法正確不代表邏輯正確；建立/修改每個可執行 Python/script/demo/POC/example 後，必須 uv run python <file> 實跑，不能只讀碼、ast.parse 或說理論可行就報完成。

## 強制規則

修改→立即執行→觀察成功/失敗與錯誤→調整重跑；多個可執行檔都須跑。測試改後 uv run pytest <test>；新增測試先 RED 再實作，綠後確認確實測到聲稱行為。

POC 是暫時產物，到所屬 EP 段落 build＋commit 為止；build 將驗證行為提煉正式測試，commit 2.7 確認承接後清除。test docstring/EP 結論/量測文件任一完整固化即可刪；量測外部世界者不強迫轉 test。

### 例外（可跳過執行）

純文檔/instruction（rules/skills md、Claude 端 wrapper；內含不可執行範例仍是文檔）、純註解、ruff 自動 import 排序；配置與可執行碼不屬純文檔。

## 為什麼

真實案例：psycopg COPY、浮點轉整數/FK、跨模組循環 import、多標的 .item() 錯誤，都需要實跑揭露；ast.parse 無法證明 runtime。
