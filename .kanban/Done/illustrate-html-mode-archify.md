# [tag:skills] illustrate html 輸出模式（archify 整合）

## 目標
/illustrate 新增第三輸出模式 HTML（opt-in）：委派 archify 渲染引擎產展示級互動圖，服務分享/demo/re-onboard/drift 審查。Console/MD 角色不變（受眾分流非取代）。

## 相關
- EP：`ai-analysis/execution-plans/_done/ep-illustrate-html-mode.md`
- Pilot 證據：`ai-analysis/reports/archify-pilot-report.md`（四圖型 showcase+visual-check 全過；vision agent 裁定有條件價值）
- 外部依賴：archify（`~/Github/archify` clone 優先——npx skills add 會穿 skills symlink 寫進本 repo，不建議）

## 驗收標準
- opt-in 觸發（明示 `html` / mode D 增益建議 / A/C city map 映射）；Console 永不 inline
- 偵測兩級（skills 任一根 → clone）+ doctor 首跑 + 降級 MD Mermaid 不靜默失敗
- 輪數 guard：單圖 12 止損 / session 總預算 18 / 無改善即停
- JSON IR tracked 為再生源頭；HTML/截圖 sidecar 依 .gitignore 排除
- 跨檔映射單一源（illustrate-html-mode.md）；/consistency 過

## 備註
2026-08-30 完成（EP review 13 findings + build review 9 findings 全數吸納）。
