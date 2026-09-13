# superpowers（obra/superpowers）測試做法研究——AIR-85 借鑑

> spec-miner 挖掘 2026-09-13；clone 副本 .agent-tmp/superpowers-inspect/（用畢可刪）。逐字引用與 file:line 見原始回報（本檔為提煉版＋AIR-85 應用）。

## 核心發現：雙層測試架構

- `tests/`＝**機制層**（無 LLM：bash/node/python——plugin 載入、sync、utility）
- `evals/`＝**行為層**（真 LLM session——drill harness 驅動 tmux 的 CC/Codex/Gemini，LLM actor＋verifier 判 skill compliance；住外部 repo superpowers-evals，unverified 內部）
- bash 行為測試（headless `claude -p`＋stream-json grep）**全部 CC-only**；非 CC 行為測試在他們 repo 無現成答案

## 可直接借的四個模式

1. **「Behavior, not text」**（writing-good-tests.md L47-52）：斷言產物含某行只證「source 是 source」——測消費端行為（skill loader/agent 觸發），勿 grep 自家產物
2. **present/missing 雙場景對稱**（test-bootstrap-caching.mjs）：SKILL.md 搬走斷言零注入且 negative 也被 cache——負向場景同等公民
3. **premature-action check**（run-test.sh L102-115）：第一個 Skill 呼叫之前不得有實質 tool_use——「先載入再動工」的機械判準
4. **真實註冊路徑測試**（opencode setup.sh）：symlink 註冊「what OpenCode actually reads」——測 deploy 後的消費端視角布局，非 source tree

## Flaky LLM 測試手段（全套）

統計重複而非 retry（`RUNS` 參數；worktree test 實證 50/50 zero failures）／CLI exit code 不參與判準（`|| true`，只看 log 行為）／prose 寬容匹配（case-insensitive＋alternation 吸收措辭變異）／預算上限（per-run 120-300s、`--max-turns 2-3`）／不進 CI（規劃 tiered：PR fast subset＋nightly full）／環境隔離（mktemp project、export HOME、每 run git init；haiku 測試反向注入真實 CLAUDE.md 製造可控干擾）／四態分類（PASS/FAIL/[UNEXPECTED]/INCONCLUSIVE——非預期行為不與目標失敗混淆）

## 對 AIR-85 的應用

### S6（CC unknown-keys probe）
- 雙場景：(1) 含 projection unknown keys 的 rule 在 CC 端 matching Read 仍注入（probe load_reason=path_glob_match）；(2) 對照組正常注入
- 判準＝注入成功＋無 loader 錯誤；**勿只驗 source 含 key**

### pointer 行為測試（非 CC 端）——兩層
- **機制層（pytest，快）**：marker 字串模式（借 PERSONAL_SKILL_MARKER）——斷言投影後 bundle 內容正確＋目標 skill 在三端 canonical root 可達＋**deploy 重跑冪等**（無變更時零寫入——借 cache 計數斷言）
- **行為層（真 session，慢）**：headless session＋自然語言 prompt「我要改 AGENTS.md...」→ 斷言 skill 載入（premature-action check 借鑑）＋多輪變體（extended conversation 後跳過是實測失敗模式）。**載具**：CC 端 `claude -p`（他們模式可搬）；**ZCode 端有 headless runtime**（delegate-bridge GLM 委派同機制——isolated carrier home）——可自動化，不需 user 手跑
- **description-recall vs behavior 區分**：驗「skill 內容出現在 transcript」只是召回，不證觸發——判準要分開標

### 機制測試哲學
- 語言不借（他們 bash/node 因 SUT 是 JS plugin；我們 pytest 不變）
- 借：真實註冊路徑＋冪等零寫入斷言＋deletion gate（行為測試取代機制測試須逐斷言覆蓋證明 default keep）＋real validation not just code review
