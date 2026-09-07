# AIR-41 — 覆蓋限定的 Memory body Read 觀測

> **ep_type**: implementation
> **parent**: ai-analysis/_tasks/09-07-memory-governance/ep.md
> **baseline**: f03d3460c9c157e1dc6079ccdfb7acd680bbe25a
> **depends-on**: AIR-40 正式 reader 與首跑證據
> **status**: 計畫；目前只有範圍有限的前期 POC

## 實作總覽

新增 `memory_telemetry.py reads` 投影，量測明確成功的條目本體 Read，分開工作／維護／未知用途，產生可觀測窗內未見Read候選。90日為requested window；不宣稱從未讀、無用、可刪。不把零Read轉cold，不刪改memory/rank，不建立常駐排程。資料缺失要可見，零候選/全部保留合法。

## UC 盤點

新增UC：body Read觀測與覆蓋限定候選（AIR-41，母卡AIR-42）；更新既有memory-audit內容核實的證據入口。已有卡不新增。依賴AIR-40 Event/Coverage；掃描root AGENTS、skills/CLAUDE、memory-audit、standup read_hotspots、backlog search。元專案無library Capabilities或對應SYSTEM-MAP。

同主題memory清單：feedback_memory-failsoft-importance-ordering.md、project_memory-desc-loop-posture-pending.md；先驗只列，不審改共享池。候選不是結案蒸餾授權。

## Scenario Matrix

| ID | 觸發 | 預期行為 | Checkpoint | UC |
|---|---|---|---|---|
| R1 | 雙源成功Read | join result後計body讀取，保留range | evidence | Read觀測 |
| R2 | error/unmatched/只索引/rg | 不計body成功；盲區顯示 | diagnostics | Read觀測 |
| R3 | audit或蒸餾讀遍全池 | 維護Read與工作Read分開 | purpose ledger | 用途判讀 |
| R4 | 缺來源、malformed、保留期不足 | observed-window/partial，不能產全域零讀結論 | coverage | 覆蓋 |
| R5 | zeroRead但hot/近30日/活躍弧 | 豁免候選；豁免原因仍可觀測 | exclusions | 候選 |
| R6 | owner未知、rename/刪除重建不明 | HOLD，不自動合併身分 | inventory identity | 候選 |
| R7 | 全保留/零候選 | 合法驗收，不要求處置 | advisory | 候選 |
| R8 | 只有description已足夠 | body metric維持零，但不推無用 | limitation | 用途判讀 |
| R9 | Codex/Muse或Bash讀取不在collector | 明列harness/tool缺席，不能稱全使用率 | manifest | 覆蓋 |
| R10 | 大窗/掃描中新writer/重跑 | streaming、固定上界、inventory hash，變動標stale | receipt | 覆蓋 |

## 段落0 — 研究與假設

[母家POC](../evidence/README.md)已證實現存ZCode/本次CC範圍不足90日，且維護Read未分類。raw zero-body-Read數不是可刪候選數。origin非operation actor；沿用AIR-40 identity，不另寫去重器。

既有錨點（source/rg）：`read_hotspots.main` 在 `skills/standup/scripts/read_hotspots.py:31`，由standup skill讀取熱點流程消費；不直接複用其 compact-JSON LIKE 或未判成功的counts。`memory-audit/SKILL.md:45` 內容核實是本卡consumer，`:59`治理三分離、`:95`狀態戳。rank來源 `generate_index.py:98 parse_rank`，本卡只讀不改；直接引用目前輸出或解析受支持frontmatter，不增加第二套rank政策。

CR查詢缺index，bridge無refs；source-read僅提供結構先例，不等於runtime驗收。依賴AIR-40新collector是planned，開工需先讀其最終程式/測試與卡Done證據。若其schema變更，先更新本EP錨點與fixture，不猜欄位。沒有完整retention manifest時，不補造歷史覆蓋。

## S1：Read與coverage投影

Context：實作UC「body Read觀測／覆蓋」。依賴AIR-40成功結果join、path normalization、lineage去重；共享Event/Coverage，不重讀standup摘要。Invariant Impact：無交易domain invariant；分析約束＝unknown不變零、維護不冒充工作、工具成功不冒充知識被使用。

檔案：修改 `skills/memory-audit/scripts/memory_telemetry.py`，新增 `tests/test_memory_read_observation.py`。CLI `reads --pool --zcode-db --cc-root`（重複可列多目錄）、`--since/--until`（預設90日）、`--output`；沿用AIR-40輸入/輸出路徑邊界。

```python
events, coverage = collect_normalized_events(args)
inventory = snapshot_entries_with_hash_rank_mtime(args.pool)
reads = select_successful_body_reads(events)
report = project_reads_by_entry_and_source(reads, inventory, coverage)
```

Read覆蓋粒度：部分Read也計明確body接觸，但不宣稱全文讀完；record range/partial可得就保留。index、系統底線檔不算entry。日界用UTC aware半開窗，mtime只用豁免不當creation。coverage列請求期間、各源observed bounds、掃描目錄、excluded roots、read/parse errors、未知shape與instrumented harness/tool清單。observed bounds不是連續保留證明；缺一源則partial，不把另一源零命中寫全域零。

CC掃描根明確列出現存/已移除worktree歷史目錄的發現與漏失；當前worktree list不足以保證所有歷史。允許CLI顯式追加來源root。無rename映射時按現存canonical path觀测，不把舊名零命中當新條目無用；重建同名歷史混淆標identity_unknown。所有候選附scope，不自稱全harness召回率。

驗證：沿用真正SQLite/JSONL CLI fixture，success/error/out-of-order/unmatched/partialRead/indexOnly/alias/relativePath/removedWT/emptyReadable/missing/malformed；缺源須partial與非零診斷狀態，不能「成功零讀」。穩定fixture重跑一致、來源hash不變。正式live首跑必重新產，不能沿用前期POC raw counts。

## S2：用途判讀、候選與豁免

Context：實作UC「用途判讀／候選」。依賴S1 observation report與當次inventory，不依description語義猜owner，不使用mtime推讀取時間。LLM可讀有限原始session context判讀，但collector不輸出整段對話。

用途帳以report中的event/session source_ref為鍵：work/maintenance/unknown＋一行證據。known maintenance來源如明確audit/mem-distill委派上下文；不能只靠title包含audit就自動定性，也不能把整session所有Read視為同用途。unknown不自動轉work。

候選輸出分兩表：① observed-window未見任何成功body Read；② 有維護Read但未見已確認work Read。第二表與未知用途僅作人工調查，不冒充零Read。共同豁免 hot、近30天mtime、活躍弧；owner無法確認、identity未知、來源盲區重要時HOLD，仍可顯示受限觀测事實。

```python
for entry in inventory:
    observation = report.for_entry(entry)
    decision = apply_exemptions_or_hold(entry, owner_evidence)
    emit_observation_and_advisory(observation, decision, purpose_evidence)
```

不把零Read當cold，不隨collector修改rank；AIR-39保留目前語義。條目description已足夠、低頻重大約束、其他工具讀取均是保留理由。缺失資料可以導致全HOLD，仍可完成觀測能力驗收。

驗證：fixture覆蓋三豁免、owner未知、mtime邊界/未來時間、rename、只維護Read、未知用途、描述足夠。live首跑人工抽實際候選（不足則全取，零候選以受控fixture驗候選路徑），每項回查雙源與coverage；允許全部保留。不能以>=1處置作完成條件。

## S3：接入memory-audit與收尾

Context：更新既有audit內容核實UC。修改 `skills/memory-audit/SKILL.md` lite/full入口與內容層、`skills/CLAUDE.md`索引。先消費已產report，缺資料才按需調reads；不新建cron、不每輪強制重掃所有transcripts。

修改要點：觀测是內容核實的取樣線索；full/lite仍需對repo查真值。advisory→核可→執行不變，本卡只交候選與判讀，不跨池寫入。新用途欄不變成另一份權威memory，只是本輪報告。

驗證：按skill走一次reads→用途判讀→advisory，三份輸出source_refs可追；`rg '死亡|從沒被讀|未觀測|memory_telemetry' skills/`逐項判歷史vs活規範；不改歷史archive。targeted pytest覆蓋AIR-40+本卡測試、ruff、audit-test、獨立review/judge；無配置mypy記適用性。不以字符串測試冒充live evidence。

## 整合與收尾

baseline: f03d3460c9c157e1dc6079ccdfb7acd680bbe25a

AIR-40之後順序build，同script衝突先re-read。更新skills描述、索引與殼證據；元專案無library Capabilities/SYSTEM-MAP變更。AIR-41達行為驗收才結案兩步；母家活躍時保留子目錄位置，母卡歸檔統一更新refs。memory/shared configs不寫。結案蒸餾只列owner候選，不自動改其他弧條目。

## EP review

待獨立 review 與裁決。
