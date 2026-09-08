# Instruction 分層：Codex 哲學的完整調查與我方處方

> 來源：Codex 官方文檔鏡像（`ref-docs/harness/codex/`）`guides/agents-md.md`、`concepts/customization.md`、`learn/best-practices.md`、`config-advanced.md`、`config-reference.md`、`skills.md`、`memories.md`，對照 Muse（`ref-docs/harness/meta/muse-code/configuration.md`）與自家 loader 實測（`~/.local/share/muse/sessions/` diagnostics＋`cli-*.log`）。
> 問題起點：muse user-rules 64KiB 靜默截斷（backlog draft-3 載體；lane 語義已於 09-08 以機械證據定案為串接）。

## 一句話結論

Codex 官方哲學＝**小主檔＋引用＋skills＋memory＋MCP 五層互補**（`customization.md` 原話 "complementary, not competing"），配可調 knob。Muse 無文檔、無 knob，只能硬瘦；Codex 可調 knob，已於 09-08 調至 100KiB 根治。剩餘工作＝muse 變體（A 案先行）＋三條 rule 下沉＋per-target gate。

## 現況量測（09-08 實測值）

- 四家部署檔皆 79,315B（同一 bundle：guide 10,588＋neutral 16 檔 67,786＋markers/sentinel）。
- muse session（ai-rules workspace）：`rendered_bytes=92,962`（user 79,315＋project 鏈 13,647）→ `text_bytes=65,535`，載入率 70.5%。切口：quality-constraints @63,956 只活 1,579B；tool-discipline @71,597 整檔陣亡；project AGENTS.md（12,550B）0 bytes。
- 上限特性（機械驗證）：65,536B＋UTF-8 字界 backoff（今晨切口前一字節為 CJK 字首 `e4`，退一格得 65,535；昨日 ASCII 切口得 65,536 整）。
- 順序 user-first（project 後串接、超 cap 即餓死）；untrusted workspace 跳過 project（`skipped_untrusted=1`），user 照載。

## 四家機制對照

| | 上限 | 性質 | 我方下場 | 逃生艙 |
|---|---|---|---|---|
| ZCode | 100KiB | hardcode（`zcode.cjs`），無 knob | 79KB 全載 ✅ | 無（只能瘦） |
| Muse | 64KiB | 未記載、靜默、無 knob | user 尾切＋project 全滅 ❌ | 無（只能瘦） |
| Codex | 32KiB 預設 | 有記載（`project_doc_max_bytes`），combined，**可調** | 原 32K 切比 muse 更狠 ❌❌ | ✅ 調 knob（已調 102400，見下） |
| OpenCode | 未驗 | 文檔無 AGENTS.md 上限條款 | 未知 | 未驗 |

Codex chain（`guides/agents-md.md`）：global（`~/.codex/AGENTS.md`，`AGENTS.override.md` 優先獨佔）＋root→cwd 逐層各一檔，串接，combined 達 `project_doc_max_bytes` 即停。官方處方原文："Raise the limit or split instructions across nested directories"。另有 `AGENTS.override.md`（臨時覆蓋不刪底檔，probe 可借用）、`project_doc_fallback_filenames`、`CODEX_HOME` 分身。

Codex skills（`skills.md`）：progressive disclosure——初始僅 name＋description＋path（全表上限 2% context 或 8K chars），選中才讀全文。與我方 rule+skill 分層（8 組先例）同構。

Codex memory（`memories.md`）：自動生成（extraction／consolidation 雙模型，`~/.codex/memories/`，`/memories` 管）。對照：muse 手寫 index（MEMORY.md＋路徑≤48 檔，按需讀，observer 可插 note；untrusted 照載）、ZCode 治理 memory（一句話測試＋rank＋蒸餾）。三家三制，**memory 是獨立 lane，不進 rules_file 預算**。

## 哲學映射：五層 → 我方現況 → 缺口

1. **小主檔（Keep it small）**：`customization.md` 只准「每次必守」（build/test、review 期待、repo 慣例、目錄指示），feedback loop（犯兩次才 codify）。我方 bundle 79KB 是其 2.5 倍（以 Codex 預設計）——超標確認。
2. **引用（reference task-specific md）**：Codex best-practice 明示；muse 不支援 `@` 展開（Claude 專用；muse 載入清單固定，09-07 探針證 `~/.agents/AGENTS.md` 都不讀）。我方等價物＝skills 按需讀＋memory index。結論：**下沉只能走 skills，不走引用**。
3. **skills**：三家機制皆支援（muse skills_catalog 31.6KB 全未截；codex progressive disclosure）。我方已有 8 組分層，路徑成熟。
4. **memory**：三家獨立 lane，不占 rules 預算；muse 在 ai-rules repo 內唯讀（project AGENTS.md 明文），寫入端規範對 muse 是死重。
5. **MCP**：本議題無關（code-reality 等工具面，不占 instruction 預算）。

## 處方

### 已執行（09-08）

- Codex knob：`~/.codex/config.toml` 加 `project_doc_max_bytes = 102400`（文件無上載明白款，type `number`；TOML 解析通過）。79,315＋12,550＝91.9KB＜100K，Codex 側根治，bundle 不動。未驗證：CLI 版本是否認得該鍵（需一次真實 codex session 覆述尾端 sentinel 驗）。

### 待裁定／待執行（muse 側）

- **A 案先行**：muse 專用變體，排除 lsp-navigation（4,529B，muse 無 CR/LSP 工具）＋model-routing（4,476B，tier 派發是 spawner 職責）＋instruction-writing（2,575B，muse 不寫 instruction 檔）＝11,536B → 變體約 67.8KB。誠實標註：此為縮水版 A（tool-discipline＋context-management 經 09-08 逐條覆核後保留，見下），project 載入約 0／12,550B——仍是 project 全滅，但 user 全載（今晨是兩頭滅）。
- **保留理由（覆核 draft-3）**：tool-discipline 僅「背景執行」節（約 0.7KB）真正 harness-mechanical，其餘（uv run、sed 禁令、Read-before-Edit、批次化、no-pipe-gate、Read 紀律）通用且當 session 在用；context-management 通用核（糾正策略、落盤原則）對 backlog/EP 工作有效，死重僅 `/clear`／STATE.md／memory 寫入端（ai-rules 對 muse 唯讀政策背書）。
- **下沉 follow-up（根治，約 220 行／14.8KB）**：acceptance-evidence（57 行 7KB）、collaboration-constraints（81 行 6.8KB）、outward-action-consent（100 行 5.6KB）三條各下沉一半（rule 留核心＋pointer，深層進 SKILL.md）。密度：bundle 1,169 行／79,315B ≈ 68B/行。
- **per-target gate**：`BUNDLE_MAX_BYTES` 拆四檔（muse 64K 硬／codex 100K 軟（跟 knob 走）／zcode 100K 硬／opencode 未驗先沿用 90K 並標 unverified）＋註解修正（「只有 ZCode 截斷」已過時）＋`rg "90KiB|BUNDLE_MAX"` 引用面同步（`rules/AGENTS.md` 部署紀律段等 11 處命中）。

### 驗收探針（由 user／主 session 執行，本 session 不碰 muse）

1. muse：部署變體後 ai-rules 新 session `rules_file text_bytes == 檔案大小`。
2. codex：新 session 覆述 `<!-- bundle-end -->`（knob 生效驗）。
3. （選）concat 內容面：小 marker user 檔＋同時引用 project 內容，釘死串接順序。
4. （選）`@` 展開：probe file 放 `@路徑`＋要求覆述，釘死不展開（預期）。

## 未驗證項

- OpenCode 上限（文檔無條款）。
- Codex CLI 版本是否接受 `project_doc_max_bytes`（TOML 過≠runtime 認）。
- muse 65,536 上限在 mosaic 級 project 鏈（42KB）下的行為（out of scope：任何 user 變體都裝不下，只保 ai-rules 本家 12.5KB）。
- rendered 與 text 約 1KB 級殘差（per-source framing 推測，未釘死；已吸收進 margin）。
