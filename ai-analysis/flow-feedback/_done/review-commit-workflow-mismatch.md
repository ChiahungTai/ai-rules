# .review/ 機制與工作流不符 + commit 結算模型（POC/scripts session 發現）

> 來源：以 docs mode 執行 POC/scripts 治理 EP 後，跑 `/code-review` + 討論 commit 流程時發現。皆為 type-2（review/commit 流程的設計缺陷），已於本次 session 當場修正，記錄供 `/flow-review`。

## 縫隙 1：.review/ 的 status 機制靠 LLM 更新會漏

- **情境**：F7/F8 finding 處置了（改了 code），但 `.review/main.md` 的 status 仍 `open` ——「改 code」和「更新 .review/ status」是兩個動作，LLM 改了主任務（code）漏了元動作（status）。commit 2.6 掃 `open` Critical 誤報（finding 實際處置了但 status 失真）。
- **為何漏**：status 更新是「元動作」（code 之外的筆記更新），無機械強制，靠 LLM 記得。違反 repo 核心哲學「機械閘門 > LLM 自覺」。
- **type-2 建議**：finding 追蹤不該靠 LLM 平時更新 status。改為 commit 結算時一次性處置 —— 人對照 diff 判讀（B 軸 viewport），不靠 status 機械追蹤。
- **本次處置**：commit 2.6 從「掃 status 找 open Critical 閘門」降為「optional 提醒」；code-review finding 預設留對話供 `/copy`，`.review/` 降 optional。

## 縫隙 2：.review/ 為 feature branch 設計，trunk-based 下累積污染

- **情境**：`.review/<branch>.md` 以 branch 為隔離單位，隱含假設「一 branch = 一變更」（feature branch workflow，merge 後 branch 刪、.review/ 自然清理）。trunk-based（main 一直用）下，多變更的 finding 全累積在 `.review/main.md`（實測 F1-F8 三輪混雜、8KB）。
- **為何漏**：`.review/` 的隔離單位（branch）假設了 feature branch 工作流，沒考慮 trunk-based。用戶實際靠 `/copy` 在 review session 對話裡即時搬運 finding，不靠 `.review/` 長期保存。
- **type-2 建議**：`.review/` 的生命週期該綁「變更結算點（commit）」而非「branch」。commit 後清除 —— `.review/` 只代表「uncommitted 變更」的 finding。
- **本次處置**：commit 階段 6 成功後 `rm -rf .review/`（同 POC 生命週期哲學：工作過程產物，commit 結算後清除）。

## 縫隙 3：commit 結算模型的確立

- **情境**：討論中確立 **commit = 一次開發週期的結算點**。進 git 的（主變更 + EP + flow-feedback）一起進；清除的（`.review/`）清掉；不靠 status 追蹤（靠人 `/copy` + commit 確認對照 diff）。
- **type-2 價值**：這個模型讓 review/commit 流程跟 trunk-based + `/copy` 工作流自洽，且符合「機械閘門 > LLM 自覺」—— **檔案級產物（POC/demo）用機械閘門（commit 2.7 掃 poc/ + demo_*.py 強制歸類），對話級產物（finding）用人 viewport（commit 確認對照 diff）**。兩軸分工，不靠收緊機制把對話級也塞進機械閘門。
- **本次處置**：commit.md（2.6 降 optional、階段 6 納入 flow-feedback + 清 `.review/`）+ code-review.md（finding 留對話）+ workflow-review-pattern.md（`.review/` optional + status 非可靠閘門）。

## 共通根因

三縫隙同一根因：**`.review/` 機制（status 追蹤 + branch 隔離 + 持久化）假設的工作流（feature branch + 多命令自動化協作 + 跨 session 長期追蹤）與實際工作流（trunk-based + `/copy` 即時搬運 + 人主導）不符**。`.review/` 的複雜度（status 生命週期、join key）在實際工作流下沒有讀者，且靠 LLM 維護會漏。

改善原則：**機制要匹配實際工作流；對話級產物（finding）靠人 viewport，檔案級產物（POC/demo）靠機械閘門**。本次的 commit 結算模型是這個原則的體現。

## 觀察點（供 /flow-review 追蹤）

- `.review/` 降為 optional 後，跨命令自動化場景（`/judge-review`/`/followup-review`）是否仍有人用 —— 若長期不用，可考慮進一步移除 status 機制。
- commit 結算模型（commit 後清 `.review/`）在長期使用下是否造成 finding 追蹤缺口 —— 若發現「commit 後才想到有 finding 沒處置」，可能要在 commit 前（階段 5 確認）加 finding 提醒。
- docs mode 對 `/code-review` 的六軸適配（Security/Performance 對文檔 N/A）尚未正式化 —— 跟 docs mode 寫回 `/execution-plan`+`/build` 同類，是下一個待補的 docs mode 適配點。
