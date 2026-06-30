# skills/commands listing 與載入紀律優化

用 Claude Code 官方控制桿整頓 skills/commands 載入行為。非急迫 budget 問題（/doctor 乾淨、skillListingBudgetFraction 已 0.05）—— 主動衛生 + 語意正確性。

**EP**：[ep-skill-loading-discipline.md](../../ai-analysis/execution-plans/ep-skill-loading-discipline.md)（docs mode，EP Review + Dry Run 已完成）

## 三個槓桿 + settings 修正（B 已於 dry run 後移除）
- **A（S1）**：`skills/CLAUDE.md` frontmatter 規範解鎖 — description 上限 1024→1536（對齊 `skill-cleaner.ts:49` 真相源）+ 補齊官方欄位文件 + 決策指引（**disable-model-invocation 預設不設** — dry run 實證會斷 AI 自主流程）+ claude-writing.md 指向單一源
- ~~**B（S2）**~~：**已移除** — dry run 掃 732 session 實證 11/22 個 disable 集命令被 AI 高頻 auto-invoke（execution-plan/spec/build/commit…），設了打斷 EP→build→commit 自主鏈；consent 已在 skill 層確保
- **C（S3）**：skill 拆分與 description 修正（**拆分優先、蒸餾僅限噪音**）— python-type-gap（578 行）拆 reference.md + paths；arch-thinking + review-engine description 觸發詞前置（dry-run 高頻 auto-invoke）；nt-query 驗上限（保持全域）
- **D（S4）**：新增 dependency-upgrade-watch skill（paths: pyproject.toml 等；偵測 NT/SJ 版本漂移主動建議 /upgrade-nt|/upgrade-sj + 收盤提醒；只建議不執行）—— **dry run 強驗證的主價值**
- **S5**：settings.json `batch-task→sequential-batch` 正名 drift 修正 + 新 skill 索引/allow 同步

## 關鍵決策（discussed-and-agreed）
- trading skills 不搬進 mosaic（抵觸 ai-rules 共用家決策 + /doctor 乾淨）
- nt-query 維持全域（跨專案依賴）
- lever B 整支移除（dry run 實證會斷自主流程）

## EP Review + Dry Run 關鍵 finding
- **Dry Run（決定性）**：22 disable 集中 11 個被 AI 高頻 auto-invoke（732 session 實證）→ lever B 整支移除
- `settings.json` 仍 `Skill(batch-task)` 舊名 → S5 正名同步 sequential-batch
- S4 補齊 pinned==latest 靜默 / 離線退化 / scope 限制三個行為分支；dry run 強驗證 dep-watch 填真實缺口（升級命令 0 auto-invoke，drift 59-80% session 發生）

## 驗收標準
- ~~22 個 command 設 disable-model-invocation~~（B 已移除）
- skills/CLAUDE.md frontmatter 規範完整（1024→1536 + 欄位 + 決策指引）
- python-type-gap SKILL.md < 500 行
- dependency-upgrade-watch skill 可運作（SM-4/4b/5/5-offline 情境）
- settings.json batch-task→sequential-batch 正名同步
- `/doctor` 複驗 listing
