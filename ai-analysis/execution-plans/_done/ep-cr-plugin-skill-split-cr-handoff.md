# CR Handoff — plugin skill 擴充吸收（EP S1 交付物）

> 貼到 code-reality repo session（工作目錟 `~/Github/code-reality`）。單一寫入者拓撲：本 handoff 的所有改動都在 CR repo；ai-rules 端隨回執另做（S2），勿代做。**產出內容（skill/README 文字）一律英文**——公開 repo 慣例（comments/docstrings/README/commit message）。

## 任務

把 ai-rules `skills/code-reality/SKILL.md` 中「任何 standalone 用戶都需要」的工具事實與坑，吸收進 `plugin/skills/code-reality/SKILL.md`。**本次 bump 同版出清**：L30 slot 路徑已由 data-plane 弧翻轉為 in-repo 並 commit（`ec7952c`）——本任務十項吸收與其同版發佈，順帶清償「SKILL.md 內容變更未 bump」的 post-build 擱置項（同版本出貨約束自然滿足；PyPI 0.2.0 仍為翻轉前版）。分層準則：工具的「是什麼、怎麼跑、有什麼坑」→ 本 repo（plugin skill，隨發版走）；消費端生態的「何時跑、接線、紀律」→ ai-rules（不搬）。

## Baseline 與環境（2026-08-29 relay 後現況；開工前仍以 `git status`／`git log` 現場確認）

- data-plane unification 已終結（主弧 `ec7952c`、EP 歸檔鏈至 `4b46717`）——README 已乾淨入庫，**A2 的 README 同步項可用**
- 並行：另一 session 實作 `ep-snapshot-zero-files-fix`（snapshot／transition／bridge 測試檔）——與本任務檔案範圍（`plugin/`＋marketplace jsons＋README）**零重疊**
- 版本協調：CC session 正實驗 plugin 軸「一次搞定」作法——執行前對齊版本號避免兩邊各自 bump 打架（user 裁決執行者後此項自然消解）

## 執行序

1. `git status` 確認並行 session（見環境段）＋與 CC session 對齊版本號
2. Read 本規格＋ai-rules 源檔 → 逐項 A1-A9 搬遷（A1 敘事以 in-repo slot 拓撲撰寫；A3 帶量測時間戳；A5 併 in-repo 語義）
3. **plugin skill 檔頭加漂移紀律行**（英文）：`Operational facts here mirror tool behavior; update this file and version-bump whenever tool behavior changes.`——雙源防腐：沒有這行，十項事實雙源必然慢性腐爛
4. 三處版本 bump lockstep＋`scripts/dist-marketplace.sh`
5. 跑驗收 rg＋產回執

## 源材料（唯讀——不改 ai-rules 檔案）

- 搬遷源：`/Users/ctai/Github/ai-rules/skills/code-reality/SKILL.md`（只讀）
- 搬遷清單權威版＋逐塊切割表：`/Users/ctai/Github/ai-rules/ai-analysis/execution-plans/ep-cr-plugin-skill-split.md` 附錄 A

## 搬遷清單（十項；源行號屬 ai-rules skill）

| # | 內容 | 源錨點 | 要點 |
|---|---|---|---|
| A1 | rustup proxy 直呼教訓 | L47 | **最高優先**——regenerating SCIP index 必須直呼 repo-pin `rust-analyzer` binary 完整路徑：rustup proxy 依 cwd 解析 toolchain，從非 repo cwd 呼叫會**靜默**換 toolchain 產泛型渲染/覆蓋面漂移（NT 實案：降到 default 1.96.0、repo pin 1.97.1，+322/−5 假差）。**敘事範例以 in-repo slot 拓撲撰寫**（`<repo>/.code-reality/scip/`；教訓本體不變） |
| A2 | 單跑 pyrefly-index 後直接 build 亦安全 | L59 | 寫 `index.scip` 後自動失效舊 sidecar＋build 端對 lsp cache 舊於 index.scip 有 mtime 閘門 fail-loud（commit `2442692`）——**plugin skill Prerequisites 現為舊時序敘述**（"stamp/build-cache as usual"），同步修正；repo README 同句可選同步 |
| A3 | refs 密度語義（預期管理） | L61 | pyrefly refs 密度遠低於 LSP golden（屬一個數量級：attribute 成員存取差異＋cache ingest 濾非 fn 形態＋constructor call 經 dunder 崩縮落 `__init__`）——非 bug。**行文帶量測時間戳**（measured ~12.7× at absorption time, 2026-08），勿釘死裸數字；跨 producer 對帳用 `golden_corpus.py --normalize` |
| A4 | scip-python fallback 專屬坑 | L63 | workspace 以 cwd 解析（誤用**靜默 index 錯 repo 且 exit 0**）；fatal 時 partial index 照樣寫出（exit code 才是失敗訊號） |
| A5 | slot 約束＋sidecar 時序 | L47/L59/L65 | 不同 producer 不混用同槽；lsp-harvest cache 在場時 SCIP index 被優先短路**靜默忽略**；時序＝生成→`--stamp-meta`→`--build-cache`。**吸收版併 in-repo 語義**：slot 位於 `<repo>/.code-reality/`（`~/.mosaic` 已退役）；舊 slot 以 `code-reality sidecar_migrate --repo <repo>` 搬遷（缺索引錯誤自動提示過渡橋） |
| A6 | 邊 kind 拆分 | L67 | `graph_db build` 產邊分 **CALLS vs REFERENCES**（build 端語法推導：ruff parse `.py`；dunder constructor 經 class 段回退）。**in-flight 注記**：snapshot EP 若先落地（kind 語義變動中），行文對齊新語義；未落地照現況寫——content-only bump 便宜，不需排序等待 |
| A7 | profile schema＋authoring 程序 | L69-109 **逐塊切割** | 搬 L101-102（無 profile fallback：頂層目錄 module、exclude 僅 `.venv/`、claims 恆 NONE、boundary crash-only、hazard registry 規則不命中）＋L104-109 authoring 四步（欄位語義教學在步驟內）；**L71-100 三個示例塊（mosaic/NT/hazard_registry，含欄位註解）不搬**——留 ai-rules 當領域示例，英文重寫帶通用示例 |
| A8 | 口徑限制（claims 抽取） | L111-113 | claims regex 由 `[[module]]` prefixes 衍生；不符前綴恆 NONE＝「未提供對照」非「EP 無宣稱」；delta_tour 三態語義；相對路徑 mention 經 prefix 下目錄存在性驗證可正規化命中 |
| A9 | boundary 已知形狀假設 | L115-117 | `pyi_module` 推導要求路徑含 `nautilus_trader` 段＝NT 結構假設；非 NT 佈局 crash=loud 設計；新 repo 消費先 smoke |
| A10 | 新舊自報（僅校對） | L17 | `plugin/README.md` freshness 段已有（`--version` 嵌 rev、stale WARN 雙信號）——**校對即可，勿重複** |

## L47 切割示意（A1/A5 手術邊界）

ai-rules L47（`scip_refs` 職責欄）是行內多主題：職責句＋slot 時序＋rustup 教訓。搬 A1/A5 後 ai-rules 端保留形態＝職責句＋slot 時序精簡＋`[SRC]` 語義；rustup 教訓全文（英文）進 plugin skill。handoff 執行時不需動 ai-rules——此示意供對照，確保搬走的是教訓而非職責。

## 版本紀律（必做——content-only 變更不 bump 則快取不可見）

三處版本 bump lockstep：`plugin/.claude-plugin/plugin.json`（plugin manifest）＋repo root `marketplace.json`（ZCode entry）＋`.claude-plugin/marketplace.json`（CC entry），並重跑 `scripts/dist-marketplace.sh`（local-path marketplace 用乾淨 slice）。版本比較讀 marketplace entry 為 "latest"——**stale entry 靜默抑制更新提示**。詳見 `plugin/README.md`「Updating the plugin」段。

## 驗收（CR 端，全綠才算完成）

1. `rg 'rust-analyzer' plugin/skills/code-reality/SKILL.md` → 命中直呼 repo-pin binary 教訓句（非僅輸出路徑描述）
2. `rg 'mtime' plugin/skills/code-reality/SKILL.md` → 命中（A2 閘門語義）
3. `rg 'density' plugin/skills/code-reality/SKILL.md` → 命中（A3 預期管理；比值帶時間戳勿釘死）
4. `rg 'partial index' plugin/skills/code-reality/SKILL.md` → 命中（A4）
5. `rg '/implement|/debrief|/post-build|crg-query' plugin/skills/` → **0 hits**（ai-rules 命令引用零洩漏——slash 形態判準，bare 英文動詞不計）
6. 全文英文；三處版本一致；`scripts/dist-marketplace.sh` 已跑
7. 既有測試綠（`uv run` / cargo test 慣例照舊）

## 回執格式（貼回 ai-rules session 觸發 S2）

```
commit: <hash>
version: 0.1.x → 0.1.y（三處一致）
files: <變更檔清單>
evidence: <上述 rg 驗收 1-5 的實際輸出>
tests: <綠燈證據>
```
