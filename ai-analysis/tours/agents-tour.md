# agents/ 目錄走讀（repo tour）

## 這個目錄是什麼

`agents/` 收納跨 harness 的 subagent 定義檔（markdown + YAML frontmatter，正文 = 系統提示詞）。部署＝registry 視圖：`~/.zcode/agents` symlink → `agents/zcode/`、`~/.claude/agents` → `agents/claude/`——`shared/` 是 authoring 單一源（跨 harness 角色定義），zcode/＋claude/ 各持 `shared/` 檔的**實檔拷貝**（registry 不載 file-level symlink）＋ per-harness 專屬實體檔（zcode/ 的 tier-pinned 家族：lite-verify／spec-miner／vision-review——pins 單一源＝model-routing skill 解析表〔`rules/model-routing.md` 留角色→tier 骨架〕）。subagent 在兩家 harness 都是「目錄載入點」，所以頂層目錄 symlink 成立（對比 hooks/ 是 config 絕對路徑引用、不能 symlink）。ZCode 設定 UI 的新建/編輯穿頂層 symlink 寫入 `agents/zcode/`（= 產生 repo working tree diff，屬預期行為）。

**誰消費它**：主 agent 在需要獨立 context 的專家任務時 spawn 這些 subagent——典型情境是 Writer/Reviewer 分離的 code review（主 agent 剛寫完 code，審查委派給持有不同 context 的 reviewer agent）。frontmatter `description` 是主 agent 決定「何時委派」的依據，所以要把觸發時機寫清楚。

## 走讀動線

### 第一站：agents/AGENTS.md（入口慣例）

目錄總覽與定義檔慣例的單一真相源，新寫或修改 subagent 定義前必讀。四個重點：

- **「定義檔慣例 / 欄位相容策略」**：必填欄位兩家同為 `name` / `description`；欄位分成五類——直接共用（`tools` 只列 built-in 共通名）、省略共用（`model` 省略 → 兩家皆 inherit 主 session）、可寫但 ZCode 安全忽略（Claude 專屬欄位）、禁寫進共用檔（ZCode 專屬欄位）、語義有差（`mcpServers`——同名 server user-level 蓋 project-level）
- **「tools 清單陷阱（ZCode）」**：自訂 tools 清單會排除 user-config MCP 工具，補救是手寫 `mcp__<server>__<tool>` 全名（萬用 `mcp__server__*` 無效靜默忽略）；`Grep`/`Glob` 寫進 tools 行在 ZCode 不注入但不報錯 → 共用定義可列兩家 union，ZCode 端文字/檔案搜尋由 Bash rg/fd 承擔；未連線 server 的全名則 spawn 直接報錯——專案層 server 全名不可寫進共用 user-level 定義，需要時另建 fork 檔；需要 MCP 的角色 tools 留空繼承全部
- **「背景執行」**：`background: true` 在 Claude 端強制始終背景執行；ZCode 不認識此欄位（靜默忽略），ZCode 端背景化是 spawn 端行為（Agent tool 的 `run_in_background: true` runtime 實測有效）
- **「ZCode 限制 / Claude 限制」**：共用定義的邊界——子智能體內不能再派子智能體（共用提示詞不可依賴 spawn 下屬）、定義修改不熱更新（快照在 session 啟動時建立）、內建 `general-purpose` / `Explore` 名稱在 ZCode 不可複用

### 第二站：agents/shared/code-reviewer.md（fresh eyes）

獨立程式碼審查者，Writer/Reviewer 分離的 fresh-eyes 側：與變更作者不同 context，不被作者的設計意圖綁住。自我定位是「findings 非定論，可被下層（judge-review / 實作查證）推翻」；read-only——不修改任何檔案，Bash 僅用於 git diff / git log、rg、jq 等唯讀查證。

正文核心是「方法論」章（每個 finding 必遵守）：嚴重度 3 級（🔴 Critical / 🟡 Important / 🟢 Suggestion）、信心水準 3 級（confirmed / evidence-based / inferred，**Critical 禁止 inferred**）、審查者自證義務（每個 claim 必查證，宣稱 dead code 須全消費端驗證）、自我否證義務（「找不到」≠「不存在」，0 hits 禁標「不存在」）、對外部系統宣稱需 grounding、Loud→silent regression lens（raise→return None、crash→filter 等視為潛在 silent-corruption 引入）。另有 Bash 查證規則（rg 禁 grep -r、fd 禁 find -exec、python -c 禁註解、不用 `$` 展開）與輸出格式（findings 表 + 審查者自證清單：實際跑過的驗證命令與無法驗證項目明列）。

**tools 清單特色**：明列 Read / Grep / Glob / Bash / WebFetch / WebSearch 加 context7、zread 的 MCP 工具全名——正是 AGENTS.md「tools 清單陷阱」手寫全名補救的實際應用例；並帶 `background: true`。

**適用時機**：任何 code review、diff 審查、變更驗證、findings 產出的場合。委派 prompt 只需給審查範圍與關注軸——方法論自帶。

### 第三站：agents/shared/code-reviewer-primed.md（context-primed 方向審查）

與 code-reviewer 配對的 primed 側：**持有意圖與結構合約**（EP、delta_tour 對照、Capabilities、dependency-graph），負責「這個 diff 是不是要做的方向」；fresh-eyes 負責實作層真相。明言「不被 diff 自身的自洽性說服——diff 內部邏輯再通順，方向錯就是錯」。

通用方法論（嚴重度分級、信心水準、自證、否證、Loud→silent lens）與 code-reviewer 相同，正文刻意不重抄——委派 prompt 會附、或自查 `agents/shared/code-reviewer.md`。獨有職責是「方向審查 lens」四項：

1. **意圖對齊**：diff 是否實作 EP 說的事？EP 承諾但沒做的、做了但 EP 沒提的都 flag——後者不一定是錯（實作層發現真相可偏離 EP）但必須顯性標出供 judge 裁決
2. **架構契合**：新東西落在依賴規則哪層？有無跨 bounded context 直取 `_private`？（arch-thinking skill 三主線視角）
3. **測試精簡且完整**：過度側（mock 假設即 bug 的同義反覆測試、重複覆蓋）與不足側（EP Scenario Matrix 邊界場景沒測）兩側都 flag
4. **完整度光譜**：YAGNI（沒消費者的抽象）↔ 過度工程（為假想需求加層），判斷依據用 Capabilities 的實際消費者、不用 diff 自述

輸出格式與 code-reviewer 相同，另加兩項：意圖偏離項標 `intent-drift`（EP 說 X / diff 做 Y / 偏離理由查證結果）；與材料矛盾處明引來源（EP 段落 / delta_tour 對照列 / Capabilities 行 / dependency-graph 條目）。tools 清單與 `background: true` 和 code-reviewer 完全一致。

### 兩個 reviewer 如何配對

dual-context 審查：對同一個 diff，code-reviewer（fresh eyes）與 code-reviewer-primed（primed）**平行審查**——前者抓實作層真相（bug、邏輯錯誤），後者判方向層正確性（意圖對齊、架構契合）。fresh-eyes 的獨立 context 補「審查自己剛寫的 code 有 bias」；primed 的 context 補「審查者不知道意圖就無從判方向」。兩份 findings 交 judge-review 裁決（含 primed 標出的 intent-drift 項）。primed 的 context 由呼叫端餵：diff + EP + delta_tour 對照（若有）+ 模組 AGENTS.md Capabilities + dependency-graph.md。

## frontmatter 欄位慣例摘要

以本目錄兩個定義檔的實際 frontmatter 與 agents/AGENTS.md「欄位相容策略」章為準：

| 欄位 | 目錄現況 | 慣例 |
|------|---------|------|
| `name` | 兩檔皆填 | 必填；主 agent 委派的識別名 |
| `description` | 兩檔皆填，含觸發時機與配對關係說明 | 必填；主 agent 依此決定何時委派，寫清楚觸發時機 |
| `tools` | 兩檔皆列 built-in 共通名 + context7/zread MCP 全名 | 只列兩家 union（`Grep`/`Glob` 在 ZCode 靜默忽略）；MCP 全名只對 user-level server 安全，專案層 server 全名 spawn 報錯不可寫進共用定義 |
| `background` | 兩檔皆 `true` | review/research 類長任務建議加；Claude 端強制背景，ZCode 靜默忽略（背景化靠 spawn 端 `run_in_background: true`） |
| `model` | 兩檔皆省略 | 省略 → 兩家皆 inherit 主 session（Claude 別名 sonnet/opus 在 ZCode 無效）；例外＝zcode/ tier-pinned 家族實檔有 pin（單一源＝model-routing skill 解析表） |

Claude 專屬欄位（`permissionMode` / `skills` / `hooks` / `memory` / `isolation` / `effort` / `initialPrompt`）可寫、ZCode 官方明說靜默忽略；ZCode 專屬欄位（`thoughtLevel` / `injectAgentsMd`）禁寫進共用檔（Claude 對未知欄位容忍度未明）——需要 per-harness 差異時另建 fork 檔。
