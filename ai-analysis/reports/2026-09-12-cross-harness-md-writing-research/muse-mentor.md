# Muse Code 提取覆核報告（codex mentor，job job-mtyhndge-pzaqok）

## 1. 總判：提取可信度**高**（核心機制 claim 與鏡像逐字吻合；一處偽陰性屬掃描範圍判定過窄）

## 2. confirmed（抽驗通過，10 條）

- `muse-code/configuration.md:41,43,46,93` — OK（walk-up 載入＋.git boundary＋四檔順序 first-wins；project 勝 user；trust 語義；memory 三 scope）
- `muse-code/extending.md:55,33,94,29` — OK（skill 定義；agent tree 8／capacity 1-64／ultra 64；hook 13 事件＋SessionEnd observational；workflow 使用情境清單）
- `muse-code/workflows.md:68` — OK（bounded responsibility＋final deliverable）
- `muse-code/changelog.md:154` — OK（instruction 變更 rollback 實證）

## 3. corrected（一處語意收斂）

- 「configuration.md 對怎麼寫 AGENTS.md 零指導」**過度絕對化**——configuration.md:32 有 `muse init seeds your project's agent rules`（生成與載入機制說明存在）。修正：「未找到 AGENTS.md 內容撰寫規範/格式建議/最佳實踐；鏡像僅涵蓋生成與載入機制」

## 4. missing

- `muse-code/workflows.md:66-89`——workflow prompt 寫法補充：「This prompt gives Muse Code enough structure while leaving implementation details to the workflow author」（結構夠用就好、實作細節留給 author）；isolation 前提失敗會 reject 不 fallback
- `muse-code/permissions.md:71`——trust state persistence：「Muse Code remembers this trust for each workspace root」（per-workspace-root 記憶）
- `muse-code/extending.md:94`——hook schema 核心契約：「A hook binds to exactly one event.」（一 hook 綁一事件）

## 5. 偽陰性

- 軸 1「AGENTS.md 內容層寫法指導零指導」——**部分推翻**（muse init 生成行為屬官方說明）：「沒有內容品質/結構寫作指導」成立；「沒有任何指導」不成立
- 其餘抽查未找到反例：instruction size/truncation、rules 獨立格式、memory write governance API、SKILL.md frontmatter schema、settings.json 完整 schema
