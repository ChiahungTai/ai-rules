# EP: standup command → skill + nightly-sequence 整合

> **ep_type**: implementation

## 實作總覽

將 `commands/standup.md`(扁平 command)升級為 `skills/standup/`(目錄制 skill + `scripts/aggregate_sessions.py`),讓 mosaic_alpha 的 nightly-sequence 以 op4 整合(append `## 📝 昨日活動` 進 daily-report),取代目前 05:30 寫孤兒 log 的 `com.mosaic.claude-standup` job。

**核心價值**:standup 獨有「昨日活動 digest」(JSONL 跨 worktree session 敘事 + commit/kanban/SYSTEM-MAP transition)是 nightly-sequence(daily-maintain/test-regression/audit-test)100% 機器狀態產出**完全未覆蓋**的人類活動層。現行產出寫進沒人讀的 log(價值歸零);整合進 daily-report 讓價值落地。

**三個 user 拍板決策**:
1. skill **無雙模式**——只產一份 **body**(無 `## ` header);delivery(`## 📝 昨日活動` header 由 nightly op4 echo + append 進 daily-report / 直接 `/standup` 在 chat 顯示 body)是 invoker 的事(EP review A1-F1 修正:原 S2 宣稱 skill 輸出含 header section,與 S4 op4 echo header 重疊→改 skill 只輸出 body)
2. section append 在 daily-report **最末**
3. `aggregate_sessions.py` **不加測試**(nightly-sequence 每晚觸發 → daily-report → 人讀 = observation loop;套用 [[feedback_check-trigger-before-adding-tests]] 教訓)

---

## UC 盤點

### Backlog 關聯
- ai-rules `.kanban/Backlog/`:無 standup 相關卡 → **自動建卡**(下方「新增 UC」)
- mosaic_alpha `.kanban/`:無 standup 卡(整合改動在 deploy/,非能力 UC)

### SYSTEM-MAP 影響
- ai-rules 無 SYSTEM-MAP.md → 跳過
- **mosaic_alpha SYSTEM-MAP.md**:S4 退役 `com.mosaic.claude-standup` 排程 + nightly-sequence 加 op4 → **須同步**(standup 列改退役、nightly-sequence 列 op 描述加 standup)。EP review A3-F2 修正:原 S5 只跳過 ai-rules,漏 mosaic 側。

### 掃描範圍
- `commands/standup.md`(現行 command)、`commands/CLAUDE.md`(命令索引 + doctrine 範例句)、`skills/scan-project/`(鏡射 pattern)、`skills/maintain/SKILL.md`(Phase 4 clobber 修正)、`skills/CLAUDE.md`(skill 索引);mosaic_alpha `deploy/scripts/run-nightly-sequence.sh` + `run-standup.sh` + `launchd/com.mosaic.claude-standup.plist` + `deploy/install.sh`(PLISTS 陣列)+ `deploy/README.md` + `AGENTS.md` + `SYSTEM-MAP.md`

### 新增 UC

| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 昨日活動 digest(跨 worktree session 聚合 + commit/kanban/SYSTEM-MAP transition) | 📋 | `skills/standup/`(SKILL.md + `scripts/aggregate_sessions.py`) |

### 自動建卡
- `ai-rules/.kanban/Backlog/`:為上述新 UC 建 1 張卡(`[tag:skills]` / 目標=standup skill 產昨日活動 digest / 相關=本 EP / 驗收=nightly-sequence op4 append 進 daily-report)
- 為本 EP 建追蹤卡(引用上述能力)

---

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | nightly 正常跑 | nightly-sequence op4 | aggregate_sessions.py 聚合 3 wt 昨日 session → body append(op4 echo header)進當日 daily-report 最末 | 無 | 昨日活動 digest |
| SM-2 | 互動呼叫 | user `/standup`(in-chat) | body 直接在 chat 顯示(無 `## ` header,自描述內容) | 無 | 昨日活動 digest |
| SM-3 | 昨日無活動 | user 整日未工作 / 無 session event 落在昨日(local tz) | aggregate 回空 sessions → S2 empty-sessions 分支輸出 body「昨日無對話活動」(不崩潰) | 無 | 昨日活動 digest |
| SM-4 | worktree 改名 drift | session dir 用 hyphen、wt 用 underscore(trading_lab 實況) | normalize(`_`≡`-`)比對 → 仍匹配 hyphen dir,不漏 wt | 無 | 昨日活動 digest |
| SM-5 | 單 worktree 消費端 | 非 mosaic 的消費者只有 1 wt(如 ai-rules 本身) | `git worktree list` 返回 1 → aggregate 仍正常 | 無 | 昨日活動 digest |
| SM-6 | JSONL 損壞行 | session 檔某行 malformed JSON | skip 該行繼續(line-by-line,不崩潰) | 無 | 昨日活動 digest |
| SM-7 | Phase 4 re-run clobber | 日間手動重跑 daily-maintain | Phase 4 merge:重寫 top title+intro+🔥/✅/📈(owned),保留 `## test-regression`/`## audit-test`/`## 📝 昨日活動`(foreign) | 無 | — |
| SM-8 | 大型 session 檔 | 單一 .jsonl 數 MB | line-by-line stream + timestamp 早退,秒級完成 | 無 | 昨日活動 digest |
| SM-9 | op4 失敗 | `claude -p '/standup'` exit≠0 或 body 空 | op4 append `## 📝 昨日活動` 下 `- ❌ standup 失敗` section,序列繼續(同 op2/op3 失敗隔離) | 無 | — |
| SM-10 | 跨日邊界 / 時區 | nightly 00:00 local 觸發;session event 跨 UTC 換日 | timestamp **先轉 local tz 再取 date**(非 UTC date),local 昨日 window 正確涵蓋凌晨/深夜 event | 無 | 昨日活動 digest |

---

## 段落劃分原則

依賴順序(每段獨立可驗證):
- **S1**(aggregate_sessions.py)→ **S2**(SKILL.md 引用 S1 腳本)→ **S3**(Phase 4 merge,獨立修債 + 是 S4 prerequisite)→ **S4**(mosaic op4 + 完整退役)→ **S5**(收尾:索引 + Capabilities + Kanban + 跨 repo 文檔)

跨 repo:ai-rules(S1/S2/S3/S5 ai-rules 部分)+ mosaic_alpha(S4 + S5 mosaic 部分)。**S4 跨 repo 寫入由主 session 執行**(非 worktree agent——collaboration-constraints)。

---

## 段落 0:全域研究摘要(已執行)

### 可複用基礎設施
- `scan_project.py` CLI/output pattern(`skills/scan-project/scripts/scan_project.py:748-787`):argparse `--project-root` + `--output` + `--init`,JSON stdout 預設、`--output` 寫檔 + summary。**aggregate_sessions.py 鏡射此 contract**。
- nightly-sequence append-to-daily-report fragment pattern(mosaic_alpha `run-nightly-sequence.sh` op2/op3):`echo '## <section>' >> $REPORT_PATH` + `cat <body> >> $REPORT_PATH`。**op4 第三 instance,沿此 pattern(invoker echo header + cat skill body)**。
- maintain skill 4-phase(`skills/maintain/SKILL.md`):Phase 4 寫晨報檔,現為盲覆蓋。

### 已驗證事實(grounding)
- **Claude session dir 編碼**:path 的 `/` → `-`(`/Users/ctai/Github/ai-rules` → `-Users-ctai-Github-ai-rules` 實證)
- **JSONL event schema**:top-level `timestamp`(ISO-8601 UTC `Z`,如 `2026-07-07T09:43:48.613Z`);conversational type = `user`/`assistant`;`type:assistant` 的 `message.content[]` block 用 `type` 鍵分 `text`/`tool_use`/`thinking`;`type:user` 的 `message.content` 是 str(真輸入)或 list(tool_result wrapper,過濾 `type==text`)
- **worktree drift**:mosaic_alpha 3 wt(underscore)但 session dir 同時有 hyphen + underscore 版(trading_lab 只有 hyphen 版)→ normalize 比對
- **實際 daily-report 結構**(mosaic_alpha `2026-07-07.md`):top `# Daily Briefing` title + `> blockquote` intro + `## 🔥` / `## ✅ 已自動處理（你不用管）` / `## 📈` + `## test-regression`。**✅ header 含括號**(EP review A2-F2 關鍵)。
- **退役範圍**(`rg "claude-standup" mosaic_alpha/` 命中 7 處):`deploy/install.sh` PLISTS 陣列、`deploy/README.md`、`SYSTEM-MAP.md`、`AGENTS.md`、plist 自身、`run-standup.sh` 自身、歷史日報

### 風險假設(對應段落驗證)
- aggregate_sessions.py worktree→session-dir 匹配(SM-4 drift)→ S1 dogfood 驗 3 wt 含 trading_lab hyphen dir
- Phase 4 merge 不破壞 report 結構(SM-7)→ S3 dogfood 對含 blockquote 的 daily-report 跑 merge

---

## S1: aggregate_sessions.py(機械 session 萃取器)

### Context
- **UC 引用**:實作「昨日活動 digest」的機械萃取半
- **依賴**:無(S1 是 S2 輸入源)
- **語義約束**:與 S2 共享「session digest JSON schema」(下方定義);**skill 只消費 S1 JSON 寫 body,header 由 invoker 加**(A1-F1)
- **基礎設施盤點**:鏡射 `scan_project.py:748-787` CLI/output;無既有 session 聚合工具(net-new)
- **技術選型**:純 stdlib(argparse/json/datetime/subprocess/pathlib)
- **成功標準**:`uv run python aggregate_sessions.py --project-root <mosaic_alpha>` 產結構化 JSON,涵蓋 3 wt 昨日 session(含 trading_lab hyphen dir);**timestamp 過濾用 local tz date**(SM-10)

### 核心實作要點
- **範圍界定**(drift-tolerant):`git -C <repo_root> worktree list --porcelain` 取 wt path → encode(`/`→`-`)→ normalize(`_`≡`-`, lower)→ 與 `~/.claude/projects/*` 全列表 normalize 比對。**非** naive encode。
- **時間過濾**(SM-10 fix):line-by-line 讀 .jsonl,每行 `json.loads` 取 top-level `timestamp`(ISO-8601 `Z`)→ parse 為 UTC-aware → **`astimezone(LOCAL_TZ)` 轉 local** → 比對 `ts_local.date() == target_date`(target_date = local昨日)。**非 UTC date、非 mtime**。`LOCAL_TZ = datetime.now().astimezone().tzinfo`(系統 local,-generic)。
- **素材萃取**:type in (`user`,`assistant`);user content=str 直取 / list 過濾 `type==text`;assistant 取 `type==text`(結論)+ `type==tool_use`(name + input.file_path/description,去重)
- **韌性**:malformed JSON line → skip;無 event 落在昨日 → 該 session 不入結果
- **CLI**(鏡射 scan_project.py):`--project-root`(Path,預設 `.`)、`--output`(Path,預設 None=stdout)、`--date`(str,預設 `yesterday`)
- **已知限制**(A2-F8 文件化):encode `path.replace("/", "-")` 不處理 `.`/空格等特殊字元;現消費端 path 均為乾淨 alnum/底線,若未來消費端 path 含特殊字元需擴 encode(non-blocking)

### Pseudo Code

```
aggregate_sessions.py
├── LOCAL_TZ = datetime.now().astimezone().tzinfo   # 系統 local (generic)
├── git_worktree_paths(repo_root) -> list[Path]
│     git -C repo_root worktree list --porcelain → parse "worktree <path>"
├── encode(path) -> str            # path.replace("/", "-")
├── normalize(s) -> str            # s.lower().replace("_", "-")
├── match_session_dirs(worktrees, projects_dir=~/.claude/projects) -> dict[Path, Path]
│     wt_norms = {normalize(encode(p)): p for p in worktrees}
│     for d in projects_dir.iterdir(): if normalize(d.name) in wt_norms: matched[d]=wt_norms[norm]
│     return matched
├── extract_events(jsonl_path, target_date) -> list[dict]   # line-by-line, SM-10 local tz
│     for line in open(jsonl_path):
│         try: d = json.loads(line)
│         except JSONDecodeError: continue
│         if d.get("type") not in ("user","assistant"): continue
│         ts_utc = datetime.fromisoformat(d["timestamp"].replace("Z","+00:00"))
│         ts_local = ts_utc.astimezone(LOCAL_TZ)            # ← 轉 local (非 UTC date)
│         if ts_local.date() != target_date: continue
│         keep d
├── digest_session(jsonl_path, events, worktree_name) -> dict
│     user_msgs/tool_calls/conclusions (見核心實作要點)
├── main()
│     args = argparse(--project-root, --output, --date="yesterday")
│     repo_root = args.project_root.resolve()
│     target_date = (datetime.now(LOCAL_TZ).date() - timedelta(1)) if args.date=="yesterday" else parse(args.date)
│     wts = git_worktree_paths(repo_root)
│     session_dirs = match_session_dirs(wts)
│     sessions = [digest_session(...) for each jsonl if events non-empty]
│     result = {date, repo, worktrees, sessions}
│     json.dumps → stdout or --output + summary
```

### 驗證策略
- **dogfood(L4)**:`uv run python aggregate_sessions.py --project-root /Users/ctai/Github/mosaic_alpha --output /tmp/standup-test.json` → 確認:worktrees 含 3 個;sessions 涵蓋 trading_lab(drift);timestamp 過濾用 local date(挑一個當地凌晨/深夜 event 驗歸屬正確,SM-10)
- **single-wt dogfood(SM-5,A2-F7)**:`--project-root /Users/ctai/Github/ai-rules` → 確認單 wt 消費端正常(`git worktree list` 返回 1)
- **無測試檔**(決策 C);nightly observation loop 覆蓋

---

## S2: skills/standup/SKILL.md(工作流)+ retire commands/standup.md

### Context
- **UC 引用**:實作「昨日活動 digest」(LLM 消費 S1 JSON 寫敘事)
- **依賴**:S1
- **語義約束**:**skill 輸出 body(無 `## ` header)**——header `## 📝 昨日活動` 由 invoker 加(S4 op4 echo;A1-F1)。body 自描述(以 `### 昨日 Commits` 等子段開頭),chat 直顯亦通(SM-2)
- **基礎設施盤點**:現行 `commands/standup.md` section 結構可沿用;`fd` 粗掃由 S1 腳本取代
- **成功標準**:`claude -p '/standup'` 產出 body(跨 wt session 敘事 + commit/transition digest,**無 `## 📝` header**);in-chat `/standup` body 直顯(SM-2)

### 核心實作要點
- **frontmatter**:`name: standup`、`description`+`when_to_use`(觸發詞:晨間簡報/昨日活動/standup;含跨 worktree)、無 `paths`
- **workflow**:
  1. `aggregate_sessions.py --project-root .` → JSON
  2. commit 敘事:`git log --since="yesterday 00:00" --until="today 00:00" --oneline --stat`
  3. uncommitted:`git status --porcelain` + `git diff --stat`
  4. **empty-sessions 分支(A2-F6)**:若 JSON `sessions` 空 → output body「昨日無對話活動」+ 僅 commit/uncommitted/今日建議(仍 output,不空白)
  5. per-session 摘要(LLM)+ cross-session 主題
  6. transition digest:`git log -p --since="yesterday" -- "**/AGENTS.md" "**/CLAUDE.md" ".kanban/**/*.md" "SYSTEM-MAP.md"`
  7. 今日建議
  8. **輸出 body**(子段:`### 昨日 Commits` / `### 進行中` / `### Session 敘事` / `### 主題` / `### Transition` / `### 今日建議`;**無頂層 `## ` header**)
- **retire**:`commands/standup.md` 刪除(skill 取代;`/standup` 由 skill 目錄制自動註冊)

### Pseudo Code(SKILL.md workflow 綱要)
```
1. bash aggregate_sessions.py → 讀 JSON (sessions[])
2. IF sessions 空 → output body「昨日無對話活動」+ commit/uncommitted/建議; DONE (A2-F6)
3. bash git log/status → commit/uncommitted 敘事
4. LLM: per-session 2-3 句(消費 JSON) + cross-session 主題
5. bash git log -p on AGENTS.md/.kanban/SYSTEM-MAP.md → transition digest
6. format → body (### 子段, 無 ## header)
```

### 驗證策略
- **dogfood(L4)**:`cd mosaic_alpha && claude -p '/standup'` → 確認產出**無 `## 📝` header**(body only)、含 3 wt session 敘事
- **SM-2 in-chat dogfood(A2-F5)**:interactive session 跑 `/standup` → 確認 body 直接 render chat(自描述,不需 header)
- **SM-3 empty-sessions dogfood(A2-F6)**:挑一個無昨日活動的 repo 跑 → 確認 empty-sessions 分支輸出「昨日無對話活動」body
- 無測試檔(決策 C)

---

## S3: maintain Phase 4 merge(修 clobber 債)

### Context
- **UC 引用**:維護 daily-report 晨報——Phase 4 盲覆蓋改 merge,保留其他 op append 的 section
- **依賴**:獨立修債(既有 test-regression/audit-test append 已被盲覆蓋);S4 prerequisite
- **語義約束**:Phase 4 owned = top `# Daily Briefing` title + pre-first-h2 intro(含 blockquote)+ `## 🔥`/`## ✅`/`## 📈`;foreign = 其餘 `## ` section(test-regression/audit-test/📝 昨日活動)。**✅ header 含括號變體**(`## ✅ 已自動處理（你不用管）`)→ 用 prefix match 非 `in`(A2-F2)
- **基礎設施盤點**:`maintain/SKILL.md` Phase 4(L70-79)+ 晨報檔格式(L237-264);現盲覆蓋(L264)
- **成功標準**:Phase 4 re-run 後,top title+intro+🔥/✅/📈 反映最新 scan,test-regression/audit-test/📝 昨日活動 section 原樣保留

### 核心實作要點
- **merge 邏輯**(寫進 maintain SKILL.md Phase 4,LLM 執行):
  1. target = `ai-analysis/daily-report/YYYY-MM-DD.md`
  2. new_briefing = **top `# Daily Briefing` title + intro(含 blockquote)+ 🔥/✅/📈**(Phase 4 重新生成全部 owned 內容,含 title 與 intro)
  3. **若 target 存在**:讀現檔 → `split_h2` 切出所有 `## ` section → foreign = 不以 owned prefix 開頭的 section → merged = new_briefing + foreign sections → 寫回
  4. **若 target 不存在**:直接寫 new_briefing
- **section 邊界**(A2-F2/F3/F4 修正):
  - `split_h2` 切 `## `(不含 `# ` top title 與 pre-first-h2 intro——這些是 Phase 4 owned,隨 new_briefing 重新生成)
  - OWNED 用 **prefix match**:`section.header.startswith(("🔥", "✅ 已自動處理", "📈"))`(容忍 ✅ 括號變體)
  - foreign = `## ` section 且 header 不 startwith 任何 owned prefix
- **blockquote 處置(A2-F4)**:blockquote 屬 Phase 4 pre-first-h2 intro(描述該次 run context)→ **每次 re-run 重新生成**(隨 new_briefing 覆蓋),非外來、不需保留舊版
- **更新 SKILL.md 文案**:L79「同日覆蓋」→「同日 merge(重寫 title+intro+🔥/✅/📈,保留外來 section)」;L264 同步

### Pseudo Code(merge 段,LLM 執行指令綱要)
```
OWNED_PREFIXES = ("🔥", "✅ 已自動處理", "📈")   # prefix match (A2-F2: ✅ 含括號變體)

Phase 4 write(target, new_briefing):    # new_briefing 含 top title + intro + 🔥/✅/📈
  if not target.exists(): write(new_briefing); return
  existing = read(target)
  h2_sections = split_h2(existing)       # 只切 ## , 不含 # title / pre-first-h2 intro
  foreign = [s for s in h2_sections
             if not any(s.header.startswith(p) for p in OWNED_PREFIXES)]
  merged = new_briefing + "\n\n" + "\n\n".join(foreign)
  write(target, merged)
```

### 驗證策略
- **dogfood(L4)**:取 `mosaic_alpha/ai-analysis/daily-report/2026-07-07.md`(含 blockquote + test-regression section)→ 模擬 Phase 4 re-run(塞假 🔥 變化)→ 確認:title+intro+🔥/✅/📈 更新、**test-regression section 原樣保留**、blockquote 隨 new_briefing 正確重生(非丟失,SM-7)
- 無測試檔(skill 是 LLM 執行,merge 是指令)

---

## S4: mosaic_alpha nightly-sequence op4 + 完整退役

### Context
- **UC 引用**:整合「昨日活動 digest」進 nightly-sequence(op4 echo header + append body 進 daily-report)
- **依賴**:S2(skill 存在)+ S3(merge 不 clobber)。**跨 repo——主 session 執行**
- **語義約束**:op4 沿用 op2/op3 append fragment pattern(**invoker echo `## 📝 昨日活動` header + cat skill body**——A1-F1);op4 **每日無條件執行**,位置在 op3 if-block 之後(無論 op3 skip 與否,A2-F9);section 順序最末(決策 B)
- **基礎設施盤點**:`run-nightly-sequence.sh` op1-3 + 收尾 commit;`run-standup.sh`(刪);`com.mosaic.claude-standup.plist`(刪);**`deploy/install.sh` PLISTS 陣列(A3-F1 Critical)**;`deploy/README.md` + `AGENTS.md` + `SYSTEM-MAP.md`(退役同步)
- **成功標準**:nightly 跑後 daily-report 最末有 `## 📝 昨日活動`;**05:30 job 完整退役——`rg "claude-standup" mosaic_alpha/` 0 命中(歷史日報引用除外)+ `launchctl list | grep standup` 空**

### 核心實作要點

**op4(加在 op3 if-block 之後、收尾 commit 之前,每日跑)**:
```
# Op 4: standup 昨日活動 digest (每日; invoker echo header + cat skill body)
STANDUP_OUT=$(mktemp)
SU_EXIT=0
claude -p '/standup' --output-format stream-json --allowedTools Read,Bash,Glob,Grep 2>/dev/null \
  | python3 -c '<stream-json 抽 assistant text = body>' > "$STANDUP_OUT" || SU_EXIT=$?
echo '' >> "$REPORT_PATH"
echo '## 📝 昨日活動' >> "$REPORT_PATH"      # invoker 加 header (A1-F1)
if [ $SU_EXIT -eq 0 ] && [ -s "$STANDUP_OUT" ]; then
  cat "$STANDUP_OUT" >> "$REPORT_PATH"        # skill body (無 header)
  echo '[OK] op4 standup appended' >> "$LOG"
else
  echo "- ❌ standup 失敗（exit=$SU_EXIT），見 log" >> "$REPORT_PATH"   # SM-9 失敗隔離
  echo "[FAIL] op4 standup exit=$SU_EXIT" >> "$LOG"
fi
rm -f "$STANDUP_OUT"
```

**退役(完整,順序敏感——A3-F1/F2/F3/F5/F6 + A2-F9/F10)**:
1. `bash deploy/install.sh --uninstall`(在 PLISTS 仍列時)→ `launchctl bootout` + rm symlink(乾淨 unload,A3-F6)
2. 從 `deploy/install.sh` 的 `PLISTS` 陣列移除 `"com.mosaic.claude-standup.plist"`(**A3-F1 Critical——防 --reload / 新機部署 resurrect**)
3. `rm deploy/launchd/com.mosaic.claude-standup.plist deploy/scripts/run-standup.sh`
4. 更新 `deploy/README.md`:移除 standup 排程表列(A3-F3)
5. 更新 `AGENTS.md`:散文 plist 清單移除 `claude-standup`(A3-F3)
6. 更新 `SYSTEM-MAP.md`:standup 排程列改退役/移除;nightly-sequence 列 op 描述加 standup(A3-F2)
7. 更新 `deploy/launchd/com.mosaic.nightly-sequence.plist` 註解 + `run-nightly-sequence.sh` 頂部註解:op 序列加 standup(A3-F5)
8. **驗證**:`rg "claude-standup" mosaic_alpha/` → 0命中(歷史 daily-report 引用除外,可接受);`launchctl list | grep standup` → 空

### 驗證策略
- **op4 dogfood(L4)**:本地手跑 op4 段(獨立,不跑完整 nightly)→ 確認 `## 📝 昨日活動` header + body append 進當日 daily-report 最末
- **退役驗證**:步驟 8 的 rg + launchctl list 雙確認
- **readiness 說明(A2-F11 文件化)**:op4 受 nightly-sequence readiness gate 保護(network/docker/postgres/redis),readiness 失敗時連同 op1-3 不跑;op4 本身只依賴 file system + claude binary
- 無測試檔(shell 整合)

---

## S5: 收尾

### 成功標準(A2-F12)
- `skills/CLAUDE.md` skill 索引含 standup
- `commands/CLAUDE.md` 命令索引移除 standup **+ L33 doctrine 範例句移除 `/standup`**(A3-F4)
- `ai-rules/.kanban/Backlog/` 建 standup 卡
- mosaic_alpha 退役文件(SYSTEM-MAP/README/AGENTS/install.sh)同步完成
- EP 歸檔

### 1. instruction 檔 / 索引更新(ai-rules)
- `skills/CLAUDE.md` skill 索引:加 `standup`(昨日活動 digest,跨 wt session 聚合)
- `commands/CLAUDE.md` **兩處**(A3-F4):
  - (a) 命令索引(L100):移除 standup
  - (b) doctrine 範例句(L33「單檔 command(`/standup`、`/commit`)無私有支援檔需求」):移除 `/standup`(改留 `/commit` 單獨,或換真單檔 command)——本 EP 因 aggregate_sessions.py 命中 doctrine L29「私有支援檔」觸發而轉 skill,範例句須同步否則自打臉
- `skills/standup/SKILL.md`:新 instruction 檔(導航優先、signal/noise、無元資訊)
- maintain `SKILL.md` Phase 4 文案(S3 已更新)

### 2. Kanban
- `ai-rules/.kanban/Backlog/`:新建 standup skill 卡
- build 階段 5a:S1-S4 全完成 → 卡搬 `.kanban/Done/`

### 3. Capabilities
- ai-rules 無 library Capabilities 表 → 跳過

### 4. SYSTEM-MAP
- ai-rules 無 → 跳過
- **mosaic_alpha SYSTEM-MAP**:S4 步驟 6 已同步(跨 repo 責任,非 S5 重做)

### 5. /audit-test
- 決策 C 不加測試 → N/A

---

## 整合策略

- **build 順序**:S1 → S2 → S3 → S4 → S5(依賴序)
- **跨 repo 寫入**:S4 + S5 mosaic 部分(mosaic_alpha)由**主 session** 執行(collaboration-constraints);S1/S2/S3/S5 ai-rules 部分正常 build
- **整合點測試**:S4 完成後 op4 段 dogfood;S3 完成後 Phase 4 merge dogfood(含 blockquote 的 report)
- **退役一致性**:S4 步驟 8 `rg "claude-standup" mosaic_alpha/` 0 命中 + launchctl list 空

---

## EP Review(3-agent review 已完成,judge 全數採納,修正已寫入各段落)

| ID | 嚴重度 | 段落 | 問題 | 建議 | 信心 | 決策 |
|----|--------|------|------|------|------|------|
| A3-F1 | 🔴 Critical | S4 退役 | install.sh PLISTS 陣列仍列 standup → --reload/新機部署 resurrect 05:30 job | S4 退役步驟 2:從 PLISTS 移除 | confirmed | ✅ 採納(寫入 S4) |
| A3-F2 | 🟡 Important | S5/SYSTEM-MAP | mosaic SYSTEM-MAP 仍標 standup 🏃 Active | S4 步驟 6 + S5 SYSTEM-MAP 段補 mosaic 跨 repo | confirmed | ✅ 採納 |
| A3-F3 | 🟡 Important | S4 退役 | README.md + AGENTS.md 仍列 standup 有效排程 | S4 退役步驟 4/5 | confirmed | ✅ 採納 |
| A3-F4 | 🟡 Important | S5 索引 | commands/CLAUDE.md:33 doctrine 範例句用 /standup 當「無私有支援檔」例,轉 skill 後自打臉 | S5 雙更:命令索引 + doctrine 範例句 | confirmed | ✅ 採納 |
| A3-F5 | 🟢 Suggestion | S4 op4 | nightly-sequence plist + run-nightly-sequence.sh 註解 op 序列缺 standup | S4 退役步驟 7 | confirmed | ✅ 採納 |
| A3-F6 | 🟢 Suggestion | S4 退役 | launchctl unload 路徑未釘死 | S4 退役步驟 1:收斂 install.sh --uninstall | evidence-based | ✅ 採納 |
| A1-F1 | 🟡 Important | S2/S4 | `## 📝` header 責任 S2/S4 重疊(雙 header + 違決策 A) | skill 輸出 body,op4 echo header | confirmed | ✅ 採納(改寫 S2/S4) |
| A2-F1 | 🟡 Important | S1 時間 | timestamp UTC `ts.date()` vs local target_date,跨日邊界漏抓 | `astimezone(LOCAL_TZ).date()` | evidence-based | ✅ 採納(改寫 S1 pseudo) |
| A2-F2 | 🟡 Important | S3 merge | OWNED_HEADERS `in` 精確比對 vs ✅ header 含括號 → 誤判 foreign → 雙 ✅ 段 | prefix match (`startswith`) | evidence-based | ✅ 採納(改寫 S3 pseudo) |
| A2-F3 | 🟡 Important | S3 merge | new_briefing top title 結構未定義;split_h2 與 `# title` 條件不一致 | new_briefing 含 title+intro+🔥✅📈;split_h2 只切 ## | evidence-based | ✅ 採納 |
| A2-F4 | 🟡 Important | S3 merge | blockquote / pre-first-h2 處置未定義 | blockquote 屬 Phase 4 owned intro,每次 re-run 重生 | evidence-based | ✅ 採納 |
| A2-F5 | 🟡 Important | S2 驗證 | SM-2 in-chat /standup 缺獨立驗收 | S2 加 in-chat dogfood | evidence-based | ✅ 採納 |
| A2-F6 | 🟡 Important | S2 邊界 | SM-3 empty-sessions,S2 無分支文案 | S2 workflow 加 empty-sessions 分支 | evidence-based | ✅ 採納 |
| A2-F7 | 🟢 Suggestion | S1 驗證 | SM-5 單 worktree 未實證 | S1 加 single-wt dogfood(ai-rules) | evidence-based | ✅ 採納 |
| A2-F8 | 🟢 Suggestion | S1 encode | encode 不處理 `.`/空格特殊字元 | 文件化為已知限制 | evidence-based | ✅ 採納(寫入 S1 限制段) |
| A2-F9 | 🟢 Suggestion | S4 op4 | op4 每日與否、位置(op3 skip 時)未明 | S4 標註每日無條件,op3 if-block 之後 | evidence-based | ✅ 採納 |
| A2-F10 | 🟢 Suggestion | S4 退役 | plist unload 責任歸屬未明 | 合併 A3-F6(install.sh --uninstall) | evidence-based | ✅ 採納 |
| A2-F11 | 🟢 Suggestion | S4 readiness | op4 與 readiness gate 關係未分析 | S4 文件化:op4 受 gate 保護 | evidence-based | ✅ 採納(寫入 S4 驗證) |
| A2-F12 | 🟢 Suggestion | S5 | S5 無成功標準 | S5 加 success criteria | evidence-based | ✅ 採納 |

**無 ❌ reject**(所有 finding 皆 grounded、無 sycophancy 接納——timezone/OWNED_HEADERS/install.sh 三個是真 bug,build 必踩)。Reviewer 結構健全性正面確認(依賴方向 consumer→generic、無 consumer-specific 洩漏、bounded context 清楚)採納為設計依據。

### 第二輪:獨立 code-review(build 後 + 07-08 nightly 實跑驗證)

build 完成 + nightly 首跑後跑獨立 code-review(context 獨立抓自審盲點)。7 findings:

| ID | 嚴重度 | 決策 | 問題 + 修法 |
|----|--------|------|------|
| F1 | 🟡 Important | ✅ 採納 | `skills/standup/SKILL.md:26` `${SKILL_DIR}`→`${CLAUDE_SKILL_DIR}`(7 處慣例,唯 standup 錯名);**今晚 nightly 前必修**(op4 是唯一 standup 路徑) |
| F2 | 🟡 Important | ✅ 採納 | `commands/audit-test.md:37/340/349` 引用已刪 `/standup` step 5→改「nightly-sequence op3 direct-append `## audit-test`」(test-quality 走 op3,DRY 非取捨) |
| F3 | 🟡 Important | ✅ 採納 | `AGENTS.md:85` 移除 `/standup`(EP S5 漏 AGENTS.md) |
| F4 | 🟢 Suggestion | ✅ 採納 | `com.mosaic.nightly-sequence.plist:15` 註解加 `→ standup(每日)`(.sh 改了 plist 漏) |
| F5 | 🟢 Suggestion | ✅ 採納 | SKILL.md session-敘事 step 加「過濾 system slash-commands」(修在 SKILL.md 非 script——保持腳本機械) |
| F6 | 🟢 Suggestion | ❌ 不採納 | `--date` 無效 crash→YAGNI(dev 工具,manual 誤用 traceback 可接受;nightly 路徑永不 hit) |
| F7 | 🟢 Suggestion | ✅ 採納 | `skills/kanban-board/SKILL.md:109` `/standup 整合` 段描述 drift→更新對齊新 skill transition digest |

**根因教訓**:F2/F3/F7 共通 = EP S0 未做**全 repo `rg standup`** 盤點(只掃已知索引檔)。**遷移/退役類 EP,S0 必做全 repo 引用盤點**。

**實跑驗證副產物**:07-08 nightly op4 首跑——LLM 過程獨白滲進 body(text capture 抓所有 assistant block)。SKILL.md 加 `## 🔴 輸出紀律` 段修正(S2)。
