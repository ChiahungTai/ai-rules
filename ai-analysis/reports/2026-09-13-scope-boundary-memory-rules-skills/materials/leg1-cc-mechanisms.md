# 腿 1：Claude Code（2.1.263）rules/CLAUDE.md/memory/skills 機制——官方鏡像＋binary 逆向

> 產出者：spec-miner（glm-5.3-flash），2026-09-13。材料＝`ref-docs/harness/claude-code/docs/en/`（crawl 2026-09-05, commit aba8f1f）＋binary `/Users/ctai/.local/share/claude/versions/2.1.263`（Bun 打包 JS bundle，199MB）＋`~/.claude/` 側證。`memory.md` 等短名＝docs/en/ 下同名檔。

## Q1：`~/.claude/rules/` auto-load——**官方機制（成立）**

- memory.md:259-261「User-level rules / Personal rules in `~/.claude/rules/` apply to every project on your machine.」；memory.md:269「User-level rules are loaded before project rules, giving project rules higher priority.」
- project 側 `.claude/rules/` v2.0.64（2025-12-10）引入（changelog.md:5295+5300）；user 側引入版本 changelog 無獨立條目〔unverified〕
- 發現規則：memory.md:187「All `.md` files are discovered recursively」；memory.md:199 無 `paths` 的 rules launch 時載（優先序同 `.claude/CLAUDE.md`）；有 `paths` 者在讀到匹配檔時觸發（memory.md:220）
- symlink 官方支援：memory.md:250「Symlinks are resolved and loaded normally, and circular symlinks are detected and handled gracefully.」
- binary：user rules＝config dir/rules（`fge(){return Ve(be(),"rules")}`）；掃描鏈 `gpe({rulesDir:xe,type:"User"})` 受 `--setting-sources` gate
- 〔unverified〕user-level rules 是否支援 `paths:` 條件載入（binary 混淆難斷）

## Q2：CLAUDE.md 階層——四層 concatenate 不覆蓋

- 載入序（memory.md:56-61）：Managed policy（macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`）→ User `~/.claude/CLAUDE.md` → Project `./CLAUDE.md`／`./.claude/CLAUDE.md` → Local `./CLAUDE.local.md`
- memory.md:157「concatenated into context rather than overriding each other... ordered from the filesystem root down to your working directory」
- ancestor 目錄 launch 載、**子目錄 on-demand**（memory.md:63）
- `@path` import：launch 展開、遞迴上限 4 hops（memory.md:95-97）；code span/fenced block 內 `@` 不展開（:99）；外部 import 首次要批准 dialog——**user-scope 檔（`~/.claude/CLAUDE.md`、`~/.claude/rules/`）豁免**（memory.md:122）
- `claudeMdExcludes` glob 排除（:329-336）

## Q3：AGENTS.md——**CC 不原生讀**

- memory.md:129「Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md`... create a `CLAUDE.md` that imports it」
- 接觸三途：`/init` 掃描（`CLAUDE_CODE_NEW_INIT=1` 下）、`/import` 一次性複製（v2.1.213+）、官方建議 `@AGENTS.md` import／symlink
- binary：`AGENTS.md` 僅 6 處，全在 /import 與 /init 語境

## Q4：載入時點與計量

- session 啟動一次性注入；**CLAUDE.md 以 user message 形態接在 system prompt 後**、計入 context window（memory.md:79,433）
- `/compact` 後 project-root CLAUDE.md 從磁碟重讀重注入（memory.md:462）；`paths:` rules 與子目錄 CLAUDE.md 讀到匹配檔時 reload
- 單檔 4 MiB 上限（超過整檔 skip 非截斷）（memory.md:405）；MEMORY.md 每場前 200 行或 25KB（:401）
- 可審計：`InstructionsLoaded` hook（changelog 2.1.69）；可停：env `CLAUDE_CODE_DISABLE_CLAUDE_MDS`

## Q5：Skills 觸發——description listing 由 model 自判，無向量匹配

- binary（Skill tool description 逐字）：「Available skills appear in a system-reminder listing with one-line descriptions. When the task at hand is one a listed skill covers, call this tool first」——**model 讀描述自行判斷**；文檔與 binary 皆無 embedding 證據
- skills.md:337 `description`＋`when_to_use` 合併截 1,536 字元（binary `var N=1536`）；listing 預算 ~1% context window，溢出截斷且 routing 退化（binary）
- compact 後 listing 不重注入（context-window.md:57）；invoke 後全文跨 turn 常駐、compact 後每 skill 前 5,000 tokens／合計 25,000 tokens 預算（skills.md:516-520）
- `disable-model-invocation: true` → 描述不進 context 僅 `/name` 手動（skills.md:506）
- 〔unverified〕SKILL.md 大小 skip 的 byte 值（binary 有字串、常數混淆）

## Q6：Memory——官方 auto memory 預設開

- memory.md:357「Auto memory is on by default」（binary 證實預設 true；`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` 可停）
- 位置 `~/.claude/projects/<project>/memory/`——`<project>` 由 git repo 推導，**同 repo worktree 共用**（memory.md:369）
- MEMORY.md 每場載、**topic files 不開場載按需 Read**（:407）；寫入＝Claude 標準檔案工具（無專屬 API），超限寫入回 error；目錄排除在 `cleanupPeriodDays` 清掃外（:397）；寫入補 `modified` frontmatter（v2.1.214+）

## 與 ai-rules 部署的對照含義（七項判定）

1. **核心依賴成立**：`~/.claude/rules/` 官方 user-level rules、recursive 掃描、symlink 正常、user-scope import 免 dialog——終端 CC session 部署假設全部成立。
2. **Cowork 例外（部署邊界）**：memory.md:124——**Cowork desktop session 跳過「symlinked `~/.claude/CLAUDE.md`... and a symlinked `~/.claude/rules/` directory or rule file that points outside the working directory」**。本機兩 symlink 都指 `~/Github/ai-rules`——Cowork 場景整組 rules＋全域指南不載。終端/IDE 不受影響。
3. **`paths:` 在 CC 是活機制**：repo rules 的 `instruction-writing.md`（`paths: ["**/*.md"]`）與 `llm-output-convention.md`（`["**/*.py"]`）被 CC 當官方 path-scoped rule——只在讀到匹配檔時載；**CC 端這兩 rule 非 always-on，與 ZCode bundle 全量常駐行為分歧**。`harness-scope:` 是 CC 不認的自訂 key（deploy_agents.py 消費）。
4. **`rules/AGENTS.md` 也被 CC 載**：rules 掃描只認 `.md` 遞迴不限檔名——rules/AGENTS.md（12KB 索引）作為一條 user-level rule 開場載入（機制語義 vs 檔名語義落差）。
5. **CC 端無 bundle 截斷線**：90KiB gate/100KiB 截斷是 ZCode/Muse 側約束；CC 硬限制僅 4 MiB skip＋<200 行建議——CC 端超裁是 adherence 退化非機制截斷。
6. **AGENTS.md 雙檔策略＝官方建議模式**（memory.md:129-147）；root CLAUDE.md `@AGENTS.md` wrapper 實測在場。
7. **MEMORY.md 投影設計與 CC 預算對齊**（resident set 索引＋routing 貼合 200 行/25KB；repo 側條目不受清掃影響）。
