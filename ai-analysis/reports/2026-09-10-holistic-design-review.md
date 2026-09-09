# 整體設計審視——AI coding 開發主軸×強化方案（2026-09-10）

> 方法：user 拍板「先從整個 ai coding 開發角度看整體、dry run use case，不再看一個解一個」。材料＝今天全天實戰（8 UC 走查）＋雙軸衝突矩陣（blueprint-execution-order-0910.md）＋UC6/7 紙上推演（.agent-tmp/dryrun-uc67.md）＋斷點根源分析。

## 主軸（八站）與強化定案

```
①想法 → ②規劃 → ③開工 → ④實作 → ⑤驗證 → ⑥收斂 → ⑦沉澱 → ⑧運維
```

| 站 | 斷點（實證） | 強化定案 | 卡歸屬 |
|---|---|---|---|
| ①想法 | 建卡撞號×2（59、63/64）——id 無機械 gate | kanban SKILL 建卡段補 id 預掃一行（ls max+1 對時） | **併 AIR-70 段二**（已動 kanban SKILL） |
| ②規劃 | research 證據載體缺 | R3 research.md（EP 同層機械可驗收） | AIR-67 段二 ✓ |
| ③開工 | **relay 過時×6**、S6 基線漂移——跨 session 通訊全靠 user 轉貼 | rehydration 單一源＋at 先結算＋授權失效條款 | **AIR-60 主修** ✓ |
| ④實作 | wrapper 氫濫用（41%）、query 教錯 | 直呼化退役＋五步 ladder | AIR-68 ✓＋AIR-67 段一 ✓ |
| ⑤驗證 | negative verdict 用 rg 冒充 | negative-claim gate 語義化 | AIR-67 段二 ✓ |
| ⑥收斂 | **session 收尾漏項×2**（AIR-54 靠 CC 補收） | 收尾 checklist 機械化（卡收尾步驟欄位化＋session 結束前核對） | **併 AIR-60**（同接續域） |
| ⑦沉澱 | memory 教錯×2、層級判準缺 | v2 判準表＋先鋒 8 條＋雙池 audit | AIR-70 段二 ✓ |
| ⑧運維 | **9 項無覆蓋**（見下）＋排程殘留靠人記 | fresh machine 重建 runbook 弧（新）＋殘留清理 | **新開一卡**＋順手 |

## ⑧站細節：fresh machine 盲區（UC6/7 dry run 實證）

**核心 5 項**（災難重建跑不起來）：
1. 統一 onboarding 文檔缺（repo 無 README；工具鏈 uv/node/backlog CLI 安裝零記載）
2. skills 對 `~/.zcode/skills`・`~/.agents/skills` 部署＝82 目錄實體複製，無腳本無 runbook
3. **ZCode cron prompt 本體無 verbatim 備份**——registry 只錄 id＋職責，重建無法逐字（三次 CronUpdate 修訂散多檔）
4. launchd 啟用命令（launchctl bootstrap/load）無現行文檔
5. CC settings.json（API keys）無恢復源提示

**邊緣 4 項**（損失面小/有部分覆蓋）：Claude/agents symlink 建立程序未串接；memory-spine 池外無 bundle（現值僅 index.md）；memory-audit 無新池 bootstrap 段；muse hooks.json per-repo 採用步驟無文檔。

**UC7 觀察**：新 repo onboarding 覆蓋好（4/6 ✅）——擴張已 skill 化；缺口全在機器本地態。

## 卡整併定案（總量：5 線＋2 獨立 → 不變，+1 新卡）

- **不新增碎片卡**：根源 D（id gate）→70 段二；根源 E（收尾 checklist）→60；第四軸（消費對等）→70 段三
- **新開一張**：**fresh machine 重建 runbook 弧**（⑧ 站核心 5 項一弧——MULTI-MACHINE.md 擴充為完整 runbook＋cron prompt verbatim 備份機制〔如 registry 附錄 prompt 全文或 CronList 定期匯出〕＋skills 部署腳本）——9 項同主題真缺口，不是碎片，自足弧
- 波次插入：排 AIR-70 後（hooks/skills 文檔面小重疊）或平行（檔案面以 MULTI-MACHINE.md 為主）

## 沿軸視角的最終判斷

今天 15+ 張卡的「碎片感」根源不是開太多，是**它們缺一條主軸敘事**——掛回八站後：③⑥（AIR-60）、⑦①（AIR-70）、②④⑤（AIR-67）、④（AIR-68）各站有主，⑧ 補新卡後全站覆蓋。**AI-58（顧問化）與 AIR-63（視圖）在軸外**（外部能力/UX 縱切面）——獨立合理。

藍圖波次不變：L6 隨時平行（跨 repo）→ 58 → 70（含新段三）→ 67 → 60 → 63；新 runbook 卡排 70 後。
