# corrections-2026-09 — 糾正模式月檔（corrections-weekly skill 產出）

> 週週 append；分類語義見 skill。08-30 基線：~30 糾正/2 週（方向錯 8＞重複 6＞遺漏 5）。

## 09-05 ~ 09-12 週報（09-12 23:10 排程 run 產出；09-06 首跑靜默空轉，由本窗補採——原標「手動觸發」係 run 自身誤標，DB 投遞紀錄證實為排程）

- 計數：方向錯 7／過度工程 3／驗推用戶 1／其他（溝通清晰度）1／疑似 1（候選 188、真糾正 ~17、噪音 ~171＝91%）
- Top 引述：
  - [09-08 04:05] sess_64b24ccc「你判讀的時候知道是要判 anchor point 那一天之前的 label 吧，不要看到未來資料」——look-ahead bias（資料洩漏險進 model；quant 鐵律相關，質重）
  - [09-08 05:42] sess_f34ad4bc「９．５ 是不是漲跌停板的原因啊，這種你不能改誒……這種 venue 相關不要搞混弄進來」——venue 邊界參數泛化（domain grounding 缺）
  - [09-06 07:09~07:15] sess_5ad68a25 三連：「是不是應該指導寫入不要這麼多廢話」「寫入前想一下要寫啥，不要無腦寫一堆廢話」——memory 寫入端精簡紀律（治理設計層，已觸發 AIR-40 軌道）
- vs 前週：方向錯仍居首（結構與 08-30 基線相似）；**噪音佔比暴增是本週新形態**（見訊號①）
- 訊號：
  1. **新湧現：排程普及後 cron prompt 成為候選噪音主體**（🔴 排程接續／【每晚 memory 收斂波】等 user-role 機器注入 ~90% 候選；另有 TodoWrite 提醒、compact 續讀摘要、Read replay 殘留）——建議 mine_corrections.py 排除清單下輪擴（cron prompt 特徵＋continuation 摘要頭）
  2. **memory 寫入端紀律為本週新主題**（5ad68a25 糾正群＋telemetry 實證：單條目 13 次寫入累計 97K chars——見下方 Memory 段），AIR-40 已承接，驗收看下週 top_entries 是否收斂
  3. **「rule 在檔、session 未遵守」兩實證**：`from __future__ import annotations`（python-standards 明文禁）×2、legacy 支援（edit-discipline 明文預設不保留）——rule 存在但 mosaic 端 session 未遵守（跨 repo 傳遞或 context 壓力），屬規則衰減的訊號但非 rule 缺失

### CR 使用（R5 換軌後形態）

- 健康診斷：CR skill 1 session；CR MCP callers **34 sessions**／refs 19／impact_radius 14／snapshot 13（對照 08-30 基線滲透 4-5%——白名單 rollout＋接線後大幅成長，無滲透退化）；對照 Bash rg 11,976 parts
- KPI：略（本週未取材 negative-claim／rename-delete 弧）
- 事件觸發註記：本週 wiring 變更＝R5 換軌（09-10，CR 段量測語義改版）＋identity gotcha doc（09-05）；本報告即事件數字來源

### Memory 寫入（AIR-40）

- successful 261（**errors 58 如實報**／aliases 32／ambiguous 0／unknown_actors 0）
- top actors（皆 subagent——抽驗線索）：sess_ffbc2596 6 次×74K chars、sess_29cb35e0 11 次×43K、sess_13e2faa2 2 次×14K
- top entries：**project_cr-live-faces-roadmap.md 13 次×97K chars**（單條目錘擊＝寫入精簡紀律的實證缺口，呼應本週糾正群）、agents-registry-split-design 7 次×31K、memory-cc-alignment-diagnosis 8 次×9K
- index_delta：首輪 baseline 已建（`ai-analysis/memory-telemetry/baselines/`）
- evidence：ai-analysis/memory-telemetry/weekly-20260912.json

---

**判讀**：本月首週——兩個具體建議：①mine_corrections.py 排除清單擴 cron prompt/續讀特徵（噪音 91% 虛胖判讀負擔，一處 regex 修正）；②memory 寫入端精簡（糾正群＋telemetry 實證同向）已在 AIR-40 軌道，下週看 top_entries 收斂。其餘無需動作。
