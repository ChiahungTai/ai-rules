# tour_validate 中文目錄 bug 重現紀錄（S7）

- 日期：2026-09-09；binary：code-reality（本機當前版）
- 反饋宣稱症狀（mosaic handoff ④，09-08 登記、09-09 重申）：`tour_validate --manifest` 報「有 corpus 目錄但零 .tour 匹配」；`--tours-dir .tours/arch` 顯式亦炸；疑似中文目錄名掃描問題；mosaic 側靠手修 callstack 錨繞過
- 重現結果：**不重現**（文件化調用形態）
  - `code-reality tour_validate --manifest --repo /Users/ctai/Github/mosaic_alpha` → `[OK] tour validate: 205 tours | links=0 filelinks=0 | fails=17`，exit 1
  - `code-reality tour_validate --tours-dir .tours/arch --repo /Users/ctai/Github/mosaic_alpha` → 同上（205 tours、fails=17）
  - 中文目錄（`.tours/arch/資料組裝與擴充/` 等）**正常被掃描與驗證**——FAIL 行正來自中文目錄內的 tours；無零匹配症狀
- 17 個 fails 全部為真錨債：`mosaic_alpha/datasets/future_labels.py` 已刪檔的 stale 錨（05/06.tour 多步）——corpus 債非工具 bug；屬 mosaic 側 post-build 修復閉環範圍
- 處置：S7 降級結案——無可移交 bug（09-08 症狀可能在後續 code-reality 版本已修，或原症狀環境相依——重現僅驗證文件化 `--repo` 形態）；本紀錄留作 code-reality 版本史對照
