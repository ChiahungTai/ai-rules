# EP: Memory 生命周期治理——審查修正弧（hardening）

> **ep_type**: implementation
> **baseline**: b48fe63c865fb123daa660d429b91736be08a43d
> **來源**: arch-thinking 挑戰審查（2026-08-30，3 🔴 / 6 🟡 findings）＋ 主任務（memory 生命周期固化，已完成、未 commit、在工作樹）
> **規模**: standard（跨檔、含 .py 邏輯變更與 invariant 語意變更；非 docs mode——`rg "^def |^class "` 於變更範圍非 0）

## 實作總覽

主任務（本弧前段，同一 working tree 未 commit）已落地：generator 資產化（`skills/memory-audit/scripts/generate_index.py`）、雙 hook 腳本（`hooks/block-memory-index-write.py`、`hooks/memory-index-regen.py`）、三處接線（zcode-registration.json / live `~/.zcode/cli/config.json` / settings.json 換軌 repo script）、rule 擴修（context-management.md「Memory 生命周期規範」）、memory-audit SKILL.md 層 1 增補、55 tests 綠、ai-rules 池索引重生成（41KB→20.6KB）。

本 EP 吸收 arch-thinking 審查的修正項：**S1** generator 併發安全＋雙單位 gate；**S2** config 回滾路徑文件化；**S3** zcode live parity invariant（F8 形狀的機械防線）；**S4** memory-audit 層 3 邊界掃描；**S5** 部署收尾＋全套機械驗證（吸收主任務未跑的 deploy）。

**明確不做**（審查列為可接受/follow-up，防 scope creep）：
- 條目重複的機械防護（池衛生＝audit skill 週期性，人工層）——Backlog 記卡不入本弧
- hook non-firing 自動 tripwire（偵測機制過度工程；S5 驗證清單 + S3 parity invariant 覆蓋可觀測面）
- `modified` frontmatter 欄位 audit lite（前提不成立：兩池 0/91、0/139 命中，已機械否證）

## UC 盤點（meta 專案變體）

### 掃描範圍
- `AGENTS.md` 專案結構（hooks/、skills/、rules/ 職責描述）、`rules/context-management.md`、`skills/memory-audit/SKILL.md`、`.kanban/`

### 受影響能力（無 Capabilities 表格——元專案以「受影響命令/rules」代替）
| 能力 | 狀態 | 來源 | 影響 | 說明 |
|------|------|------|------|------|
| Memory 生命周期工具鏈（generator 投影＋雙 hook＋rule 四問） | 🟡（主任務落地未 commit） | 本 session 主任務 | 更新 | S1 強化 generator 語意；S3 增部署防線 |
| single-source invariant 檢查 | ✅ | `skills/scan-project/scripts/check_single_source.py` | 更新 | S3 新增 zcode live parity 條目 |

### Backlog 關聯
- `.kanban/Backlog/` 無既有相關卡；本 EP 建立追蹤卡 1 張（見段落後建卡）＋「條目重複機械防護」deferred 卡 1 張

### SYSTEM-MAP 影響
- 無 SYSTEM-MAP.md（元專案，正當跳過）

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 條目檔更新後索引刷新 | 寫/改條目檔→turn 結束 Stop hook | generator 冪等重生成，資產與部署副本 byte-identical | cmp 三方；失敗=回退資產重部署 | 生命周期工具鏈 |
| SM-2 | 雙 harness 並行 turn 結束 | Claude＋ZCode session 同時 Stop 於同一 pool | 兩 generator process 均成功、索引完整（unique tmp，無固定檔名搶寫） | 併發 smoke test 兩 process exit 0 | 生命周期工具鏈 |
| SM-3 | CJK 重池 bytes 超限 | 索引生成後 >24,000 bytes（chars gate 內） | fail-loud exit 1 不寫入（新 byte gate；防 bytes 解讀 harness 尾部截斷） | byte-gate 測試 | 生命周期工具鏈 |
| SM-4 | template 接線未部署 live | zcode-registration.json 新增 hook、live config 缺 | check_single_source critical（F8 形狀：註冊≠fire） | parity fixture 測試 + 本機實跑 | invariant 檢查 |
| SM-5 | 非 ZCode 機器跑 checker | live config 缺場 | skip 不 false positive（claude_only 先例同型） | live 缺場測試 | invariant 檢查 |
| SM-6 | 新 session 實測失敗需回滾 | 換軌後 Claude gate/regen 異常 | 按 rollback note 逐字還原 inline 指令（原字串留存於 tracked 檔） | rg 對照 rollback note 與 config | 生命周期工具鏈 |
| SM-7 | rule 修改後部署 | context-management.md 已改、bundle stale | deploy 後三端 byte-identical＋rg spot check 含新段落 | check_single_source deploy_bundle_freshness | 部署 |
| SM-8 | crash 後 stale tmp 殘留 | generator 中斷留下 `MEMORY.md.<pid>.tmp` | 下次 regen 起手清除同 pattern 殘檔 | stale-cleanup 測試 | 生命周期工具鏈 |

## 段落 0：全域研究摘要

**研究執行方式聲明**：本 session 前段已完成第一手全域研究（檔案讀取＋機械量測＋pipe-test，證據內嵌各段），優於 fresh Explore agent 轉手掃描；不重複 spawn（浪費）。遺漏風險由 /ep-review 獨立 agents 補（外部視角查本 EP 未覆蓋處）。

**可複用基礎設施**：
- `tests/conftest.load_module`（非 package 腳本載入器）——S1/S3 測試直接用
- `check_single_source.py` 既有 INVARIANTS 架構（ Registrations/claude_only/skip-if-absent 慣例，`check_hook_registration` lines 298-334）——S3 沿用同型
- generator asset 本體（`skills/memory-audit/scripts/generate_index.py`，行數以 `wc -l` 為準——S1 擴充後靜態行數會漂，不寫死）——S1 就地修改

**依賴關係與關鍵約束**（機械證據）：
- 兩池索引現值：mosaic 21,482 bytes/16,371 chars/112 行；ai-rules 20,601 bytes/15,358 chars/102 行（`Path.read_text` 量測，2026-08-30 15:47）——**GATE_BYTES=24,000 兩池皆過且低於 bytes 解讀極限 24,985**
- live dispatch 部分實證：ai-rules 池 15:42 `zcode-hooks-porting.md` 條目與 MEMORY.md 同秒重生成——Claude 端 Stop regen 在真實 dispatch 運作中（並行 session 產生）；gate 腿與 ZCode 端仍未驗（config snapshot，須新 session）
- template↔live drift 實例（今日）：`block-python-file-write.py` 在 template、live 缺席直到人工補——S3 的防護對象

**風險假設**：
| # | 假設 | 等級 | 驗證歸屬 |
|---|------|------|---------|
| A1 | mosaic 池 bytes 超新 gate | 低（已量測 21,482<24,000） | S1 驗證（部署後兩池 regen 冪等） |
| A2 | Claude 端 25KB 以 bytes 計 | 中 | 雙 gate 緩解（不消除）；S5 新 session 清單驗證 |
| A3 | ZCode exit-2 stderr 回饋直達模型 | 中（未證） | S5 新 session 清單第一項 |
| A4 | live config JSON 手改壞 | 低 | S3 checker 容錯（parse 失敗→important finding 非 crash） |

無致命等級假設（全部可回退：資產/規則/接線三層皆單檔可逆）。

---

## EP Review Findings

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| R1 | 🔴 必須修正 | S1 | stale-cleanup 起手全刪 `MEMORY.md.*.tmp` 會誤殺並行 process 的 in-flight tmp（對方 replace 撲空）——與 SM-2「兩 process 均成功」自相矛盾，併發 smoke 有 flake 風險 | cleanup 加 mtime>60s age gate＋僅寫入模式執行（--check 零副作用） | implemented |
| Y1 | 🟡 建議 | S1/S4 | 錨點錯置：rule 無「17,000 字元」句（rg rules/ 0 hits）——gate 數值同步點實為 SKILL.md:33＋tests docstring | 依賴錨點/S4 成功標準改為可實際命中的清單 | implemented |
| Y2 | 🟡 建議 | S4 | 掃描範圍漏 tests/（test_memory_lifecycle.py:3 docstring 含 gate 數值，S1 後過時） | 掃描範圍擴 rules/ skills/ tests/ | implemented |
| Y3 | 🟡 建議 | S2 | rollback 字串唯一來源是 session transcript（settings.json gitignored 無 git fallback），跨 session 執行 EP 時不可得 | 原始字串逐字內嵌 EP（消除單點） | implemented（後由 build review C5① 收斂：單一留存處改 `hooks/memory-hooks-rollback.md`，S2 改 pointer） |
| Y4 | 🟡 建議 | S3 | template 檔缺席會讓 checker 整體 crash（read_text 無保護；先例 :243-244 對 source 缺席回 important） | template 缺席→important finding | implemented |
| I1 | ℹ️ 提醒 | S1 | cleanup 在 --check 模式也執行，違反「--check 只驗證不寫入」契約 | --check 跳過 cleanup（併入 R1 修法） | implemented |
| I2 | ℹ️ 提醒 | S1 | cp 刷新部署副本非原子——覆寫瞬間並行 Stop hook 可能讀到截斷腳本（fail-loud 一次、無腐蝕） | cp 到暫存名＋mv（rename 原子） | implemented |
| I3 | ℹ️ 提醒 | S3/收尾 | invariant 命名不一致：kanban 卡 `zcode_hooks_live_parity` vs EP `zcode_live_parity` | 統一為 `zcode_live_parity`（卡同步） | implemented |
| I4 | ℹ️ 提醒 | S4 | SKILL.md:37「25,000 bytes」與新 GATE_BYTES=24,000 兩個「雙解讀安全」數並存需調和 | 調和句：25,000=未裝池軟目標、24,000=generator 池硬 gate | implemented |
| I5 | ℹ️ 提醒 | S1/S2 | 行數差一（asset 87 非 88；settings.json 433 非 434） | 修正 | implemented |
| I6 | ℹ️ 提醒 | S1 | hook runtime 是系統 python3 3.9（無 PEP 604）；tests 跑 uv ≥3.10 會遮蔽部署副本的 3.9 破壞 | S1 加語言層約束（禁 3.10+ 語法） | implemented |

> 審查者自證附記（agent 實測）：兩部署副本與資產 cmp identical ✓；live config parity 完整（template 6 basenames 全在 live、enabled=true）✓；兩池量測值逐位吻合 ✓；`~/.zcode/AGENTS.md` 確實 stale（S5 前提為真）✓；byte-gate fixture 可構造性確認（~60 條 CJK 條目 chars 內/bytes 破 24,000）✓。

## S1: generator 併發安全＋雙單位 gate

### Context
- **背景**：審查 🔴-2——generator 寫 `MEMORY.md.tmp` 固定檔名（`generate_index.py:79-81`），雙 harness 並行 Stop 時兩 process 搶同一 tmp（一方 replace 撲空吃 OSError 被吞）。審查 🟡-6——gate 只有 chars 維度（`:11` `GATE_CHARS=17_000`），CJK 重內容 17,000 chars≈51KB bytes，若 harness 以 bytes 計（Claude 未證，A2）尾部截斷靜默回歸——silent-corruption path。
- **UC 引用**：更新「Memory 生命周期工具鏈」。
- **依賴關係**：S5（部署副本刷新與冪等驗證）；gate 數值的文檔同步點＝SKILL.md 層 1 注記＋tests docstring（Y1 勘誤：**rule 不含 gate 數值**，rule 只載 harness 上限與軟上限 150 行）——S4 一併掃。
- **語義約束**：與 S4 共享「gate 數值單一源在 generator 註解」；部署副本（mosaic/ai-rules 池 `_generate_index.py`）必須與資產 byte-identical（cmp 驗證）。
- **基礎設施盤點**：`conftest.load_module`；subprocess E2E 模式（test_memory_lifecycle.py 既有 `make_pool`）。
- **依賴錨點**：`GATE_CHARS` → 定義 `skills/memory-audit/scripts/generate_index.py:11` / 消費 `:73`（gate 判斷）；gate 數值文檔同步點＝generator 註解＋`skills/memory-audit/SKILL.md` 層 1 注記＋`tests/test_memory_lifecycle.py` docstring（Y1 勘誤：rule 無 gate 數值）。`tmp` 寫入 → 定義 `:79-81` / 消費 無外部（檔案系統效應）。
- **技術選型**：tmp 檔名 `MEMORY.md.<pid>.tmp`（process 內唯一即足夠——並行單位是 process；不加 uuid，YAGNI）；stale 清除加 **age gate（僅刪 mtime>60s 殘檔，且只在寫入模式——`--check` 零檔案系統副作用）**，避免誤殺並行 process 的 in-flight tmp（R1/I1）；byte gate `len(content.encode("utf-8"))`；**語言層約束：generator 與 hooks 腳本跑在系統 python3 3.9（hook runtime 實測）——禁 PEP 604（`X | None`）等 3.10+ 語法**（I6；PEP 585 `list[str]`/`set[Path]` 3.9 可用）。
- **成功標準**：併發 smoke 兩 process exit 0；byte-gate 測試 fail-loud；兩池部署後 `--check` 過且 cmp 三方 identical。

### Invariant Impact
- **受影響 domain invariant**：索引「載入全量可見」invariant（尾部截斷=靜默丟失 recall，silent-corruption path 非會計）。
- **critical path 觸及**：silent-corruption（bytes 解讀下尾部截斷無聲）。
- **驗證對齊**：byte-gate 突破測試（SM-3）→ 對應 §4 測試計畫「gate 雙單位」項。

### 核心實作要點
1. `GATE_BYTES = 24_000` 常數＋註解（harness 上限 24.4KiB≈24,985——chars 或 bytes 兩種讀法同值；ZCode 實證以 chars 計；兩池現值 21,482/20,601 bytes 留 11-14% 餘量）。
2. gate 判斷加 bytes 維度；`[FAIL]` 訊息同時印兩維度實測值。
3. tmp 改 `here / f"MEMORY.md.{os.getpid()}.tmp"`；寫入路徑（gate 通過後、`--check` 分支之後）清除 **mtime>60s** 的 `MEMORY.md.*.tmp` 殘檔——age gate 保住並行 process 的 in-flight tmp（SM-2/R1）；`--check` 不碰檔案系統（I1）；SM-8 由下次寫入模式 regen 吸收。
4. 同步 gate 敘述雙單位（「17,000 字元/190 行」→「17,000 字元/24,000 bytes/190 行」）——同步點＝SKILL.md 層 1＋tests docstring（Y1：rule 無此數值），S4 段執行，此處登記依賴。

### Pseudo Code
```
GATE_CHARS = 17_000   # 既有
GATE_BYTES = 24_000   # 新增：bytes 解讀（Claude 未證）下仍低於 24,985 上限

def main():
    ...（掃描/投影不變）
    n_chars, n_lines = len(content), content.count("\n")
    n_bytes = len(content.encode("utf-8"))                       # 新維度
    if n_chars > GATE_CHARS or n_lines > GATE_LINES or n_bytes > GATE_BYTES:
        print(f"[FAIL] gate 超限: {n_chars} chars / {n_bytes} bytes / {n_lines} lines ...")
        return 1
    if check_only: print 統計; return 0                           # I1：--check 零副作用
    for stale in here.glob("MEMORY.md.*.tmp"):                   # SM-8：只清 aged 殘檔
        if time.time() - stale.stat().st_mtime > 60: stale.unlink()
    tmp = here / f"MEMORY.md.{os.getpid()}.tmp"                  # SM-2：unique tmp
    tmp.write_text(content); tmp.replace(here / "MEMORY.md")
```
（import 增加 `os`、`time`；兩者皆 3.9 安全）

### 驗證策略
- **測試計畫**（tests/test_memory_lifecycle.py 擴充）：
  - 併發 smoke（SM-2）：fixture 池、`subprocess.Popen` ×2 同時啟動、兩者 returncode 0、索引含條目（unique tmp 使交錯無害——此測試同時是修復的行為證明）
  - byte gate（SM-3）：CJK 長 description 條目群（chars gate 內、bytes 突破 24,000）→ exit 1 ＋ `[FAIL]` 含 bytes 值＋ MEMORY.md 不寫入
  - stale tmp 清除（SM-8/R1）：預置 mtime>60s 的 `MEMORY.md.999.tmp`（`os.utime` 回撥）→ 寫入模式跑 generator → 殘檔消失；預置**新鮮** tmp → 不被刪（in-flight 保護）；`--check` 模式兩者皆不碰
  - 既有 16 測試不改綠（`test_generator_e2e_gate_fail_loud` 的 200 條目路徑走 lines 維度，仍成立）
- **完成檢查**：`uv run pytest tests/ -q` 全綠；資產→兩部署副本以 **cp 到暫存名＋`mv`（rename 原子）** 刷新（I2——避免覆寫瞬間並行 Stop hook 讀到截斷腳本）＋三方 `cmp` identical；兩池 `_generate_index.py --check` 過（A1 驗證）。
- **已知未覆蓋**：真實雙 harness 並行 dispatch（S5 新 session 清單）；os.getpid 重複（同 process 序列重入——不存在，Stop 每 turn 單次）。

---

## S2: config 回滾路徑文件化

### Context
- **背景**：審查 🔴-3——settings.json（gitignored）與 live `~/.zcode/cli/config.json`（repo 外）被我換軌/接線，無版本控制、無 .bak；原始 inline 指令只存在本 session transcript。
- **UC 引用**：更新「Memory 生命周期工具鏈」（可回滾性）。
- **依賴關係**：無（獨立）。**語義約束**：無。
- **基礎設施盤點**：無可複用（純文檔）。**依賴錨點**：無符號（文檔；錨 `hooks/zcode-registration.json` 全檔＋settings.json hooks 區段行號快照於文檔內）。
- **技術選型**：tracked 純文檔 `hooks/memory-hooks-rollback.md`（無 secret；git 版本控制即回滾保障），不採 .bak 檔（全檔 433 行重寫有 CJK 轉錄風險——只留存**差異**：兩條原始 inline 字串逐字＋ZCode 移除步驟）。
- **成功標準**：rollback note 逐字含原始指令；按 note 操作可機械執行（rg 可對照）。

### 核心實作要點（docs mode 裁剪：修改要點）
1. Claude 端：兩條原始 inline command 逐字留存在 `hooks/memory-hooks-rollback.md`（**單一留存處**——build review C5① 收斂，該檔 tracked、任何 session 可執行，消除 transcript 單點〔Y3 目標不變〕）＋還原步驟見該檔。
2. ZCode 端：移除步驟（live config 刪 `Edit|Write|NotebookEdit` group 與 Stop 第二 hook；`block-python-file-write` 保留——template parity 屬既有意圖非本弧）。
3. 觸發條件敘述：新 session 兩條實測任一失敗時使用。

### 驗證策略（文檔驗證）
- rg 對照：note 中原始字串 `rg -F` 於本 session 上下文外**不存在於任何現行 config**（證明是「回滾目標」非現值）；還原步驟的目標行號/鍵名 rg 現行 config 可命中。
- 跨檔一致性：zcode-registration.json 不受 rollback 影響（template 是 repo 資產，回滾僅 live）。

---

## S3: zcode live parity invariant

### Context
- **背景**：審查 🟡-4——`check_single_source.py` 的 `hook_registration`（lines 101-113, 298-334）只驗「檔名出現在某註冊處」，不驗 live config 部署；今日實例 block-python-file-write template 有 live 無，無人察覺（F8 形狀：註冊≠fire）。
- **UC 引用**：更新「single-source invariant 檢查」。
- **依賴關係**：S5（checker 全套實跑）；hooks/zcode-registration.json 為 template 真相源。
- **語義約束**：與 `hook_registration` 共享「以檔名為穩定鍵、文字比對」慣例；skip-if-absent 語義與 `claude_only` 先例一致（SM-5）。
- **基礎設施盤點**：`check_single_source.py` INVARIANTS 架構＋`main()` 分派（lines 337-346）；`tests/conftest.load_module`＋既有 `monkeypatch.setattr(css, "REPO_ROOT", tmp_path)` 模式。
- **依賴錨點**：`INVARIANTS` → 定義 `check_single_source.py:29` / 消費 `main():339`；`check_hook_registration` → 定義 `:298` / 消費 `:345`（新增函數同位接入）。
- **技術選型**：新 INVARIANTS 條目 `type: "zcode_live_parity"`——從 template 文字 regex 撈 hook 腳本 basename（`[A-Za-z0-9_-]+\.(?:py|sh)`，排除 registration 檔自身），word-boundary 查 live 文字；live `hooks.enabled != true` 另報 critical（fire 前提）。**方向單向**：template→live（live 多 UI-added hooks 不誤報——coverage 語義同 `skill_allowlist_coverage` 先例）。
- **成功標準**：fixture 測試三態（缺接線 critical / 齊全 [] / live 缺場 []）；本機實跑 critical=0。

### Invariant Impact
- **受影響 domain invariant**：checker 自身是新防線（非觸碰既有 invariant-bearing 模組）；寫「無」以外的說明：本段**建立** invariant（template↔live 部署一致性），無修改既有會計/風控類。
- **critical path 觸及**：無。
- **驗證對齊**：三態 fixture 測試 ↔ §4。

### 核心實作要點
1. INVARIANTS 新條目（id/type/template/live 檔名 + note 含 2026-08-30 實例）。
2. `check_zcode_live_parity(inv, live_path=None)`：template 缺席→important（Y4——INVARIANTS 路徑手誤不炸全部檢查，先例 `check_source_contains` :243-244）；live 缺場→[]；live parse 失敗→important（A4）；enabled 非 true→critical；template basenames 逐一 word-boundary 查 live 文字，缺→critical。
3. `main()` 分派接入。

### Pseudo Code
```
def check_zcode_live_parity(inv, live_path=None) -> list[tuple]:
    live = Path(live_path or Path.home() / ".zcode/cli/config.json")
    if not live.exists(): return []                        # SM-5 非 ZCode 機器
    tpl = REPO_ROOT / inv["template"]
    if not tpl.exists(): return [(id, "important", "template 檔不存在（INVARIANTS 路徑 typo？）")]
    tpl_text = read_text(tpl)
    basenames = set(re.findall(r"([A-Za-z0-9_-]+\.(?:py|sh))", tpl_text)) - {registration 自身}
    live_text = read_text(live)                            # parse 失敗由 json.load try 拆 important
    out = []
    if json.loads(live_text).get("hooks", {}).get("enabled") is not True:
        out.append((id, "critical", "live config hooks.enabled 非 true——所有 ZCode hook 不 fire"))
    for b in sorted(basenames):
        if not re.search(rf"\b{re.escape(b)}\b", live_text):
            out.append((id, "critical", f"{b} 在 template 未部署到 live——註冊≠fire（F8 形狀）"))
    return out
```

### 驗證策略
- **測試計畫**（tests/test_check_single_source.py 擴充）：fixture template（含 ok.py）＋三態 live（缺 ok.py→1 critical / 含→[] / 缺場→[]）＋ enabled:false→critical＋ live 非 JSON→important。`live_path` 參數注入 tmp fixture。
- **完成檢查**：`uv run python skills/scan-project/scripts/check_single_source.py` 全綠（本機 live 已含全部接線＋enabled:true）。
- **已知未覆蓋**：Claude 端 settings.json 無 template 第二源，parity 不可檢（gitignored local-only，claude_only 豁免先例）——如實記錄非假裝覆蓋。

---

## S4: memory-audit 層 3 邊界掃描（rule↔skill 殘留矛盾）

### Context
- **背景**：審查 🟡-6——SKILL.md 層 3 仍有「索引精簡原則：一行 = 主題 + 一個鉤子」手寫索引時代語言，與 generator 池（禁手寫）矛盾；層 1「目標 <25,000 bytes」與 gate 雙單位需對齊。
- **UC 引用**：更新「Memory 生命周期工具鏈」（文檔面）。
- **依賴關係**：S1（gate 敘述同步）。**語義約束**：與 rule「資產源在 ai-rules repo」句互指不重複（rule 留紀律、skill 留操作）。
- **基礎設施盤點**：無。**依賴錨點**：SKILL.md 層 3「索引精簡原則」行（rg 定位）；`rules/context-management.md` gate 敘述行。
- **技術選型**：雙模式改寫（generator 池=description 品質精簡；非 generator 池=原則保留）。
- **成功標準**：`rg "索引精簡原則|一行 = 主題"` 命中處已雙模式語境；`rg "17,000"` 命中處（SKILL.md 層 1＋tests docstring；rule 無此數值——Y1）皆雙單位一致。

### 核心實作要點（docs mode：修改要點）
1. 層 3 該行改：「索引精簡（generator 池=修 description 而非索引行；未裝=一行主題+鉤子）」。
2. 層 1 generator 注記的 gate 敘述補 bytes 維度（隨 S1）。
3. ripple 語義反向撈：`rg "25,000|17,000|190 行" rules/ skills/ tests/`（Y2——tests docstring 也是數值載體）全面對齊單一硬數值源（generator 註解）；調和句一併落地：**25,000 bytes＝未裝 generator 池的層 1 軟目標、24,000 bytes＝generator 池硬 gate**（I4）。

### 驗證策略（文檔驗證）
- rg 殘留：矛盾語句 0 命中；數值三處（generator/rule/skill）一致。
- 跨檔一致性：與 rule「寫入四問」互指（rg 各自命名可達）。

---

## S5: 部署收尾＋全套機械驗證（吸收主任務未跑項）

### Context
- **背景**：rule 已改、bundle stale（`deploy_bundle_freshness` 會 critical）；主任務驗收要求 deploy＋新鮮度比對；新 session live 驗證清單需成形文件。
- **UC 引用**：全部能力的部署驗證。
- **依賴關係**：S1-S4 全部完成後執行（最終態驗證）。**語義約束**：deploy 順序=S4 文檔定稿後單次執行（避免重複 deploy）。
- **基礎設施盤點**：`scripts/deploy_agents.py`；`check_single_source.py`（含 S3 新條目）；`.githooks/pre-commit`（pytest tests/）。
- **依賴錨點**：`deploy_bundle_freshness` → 定義 `check_single_source.py:90` / 消費 `check_deploy_freshness():256`。
- **技術選型**：機械驗證組合單命令批次（tool-discipline）。
- **成功標準**：下方清單全綠＋清單文件落地。

### 核心實作要點
1. `uv run python scripts/deploy_agents.py` → 三端部署＋`rg "Memory 生命周期規範" ~/.zcode/AGENTS.md` spot check。
2. `uv run python skills/scan-project/scripts/check_single_source.py` 全綠（含新 parity 條目）。
3. `uv run pytest tests/ -q` 全綠。
4. 兩池 `_generate_index.py --check` 冪等＋三方 cmp。
5. **新 session live 驗證清單**寫入完成報告（deferred 驗收，不阻塞 commit）：
   a. 新 ZCode session（ai-rules）：手寫 MEMORY.md → PreToolUse 擋＋**stderr 指引可見於模型回應**（A3 驗證）
   b. 同 session 結束 turn → `~/.zcode/cli/log/zcode-*.jsonl` 有 hook.run 記錄＋索引重生成
   c. 新 Claude session：同 a/b（Claude 端）
   d. 失敗→按 `hooks/memory-hooks-rollback.md` 回滾（SM-6）

### 驗證策略
- 全部機械命令列於完成檢查；清單 a-d 為跨 session deferred（本 session 無法執行——config snapshot 語義）。
- 已知未覆蓋：新 session 行為面（如實標注 deferred，不以「應該會過」宣稱）。

## 整合策略

- 段落順序：S1→S2→S3→S4（S2/S3/S4 無相互依賴，可平行批次）→S5 收尾。
- baseline `b48fe63`（主任務變更在 working tree、與本 EP 一併 commit——EP 是主任務的 hardening 弧；**單一 commit 收口**：hardening 逐輪 refine 的是未 commit 主任務的同批檔案，hunk 級拆分成本＞bisect 價值〔原拆兩 commit 計畫作廢，記錄於此〕；deploy 於 S5 覆蓋最終態）。
- 部署副本刷新僅 S1 觸點（byte-identical cmp 為 gate）。

## 收尾步驟

1. **模組 instruction 檔**：rule/skill 已於主任務＋S4 反映；`skills/CLAUDE.md` 工作流索引檢查 memory-audit description 是否需帶「generator 池」（rg 對照，過時才改）。
2. **Kanban**：EP 追蹤卡（Backlog→In-Progress→Done）＋「條目重複機械防護」deferred 卡留 Backlog。
3. **SYSTEM-MAP**：無（元專案跳過）。
4. **/audit-test**：對 S1/S3 新測試跑稽核（併發 smoke 的確定性、byte-gate 邊界、parity 三態）。

## Agent Review Findings（build 階段 4——3-perspective ＋ judge）

| ID | 嚴重度 | 裁決 | 摘要 | 狀態 |
|----|--------|------|------|------|
| C1①/F1② | critical/important | ✅ | 資產於部署後被 ruff format 重排、副本未重刷——byte-identical 破產 | implemented（重刷＋三方 md5 identical；根因=部署後工具改寫，收斂程序=最終態再刷） |
| C6③ | important | ✅ | parity 以文字存在性比對有 false negative（`.bak` 殘字樣通過、掛錯 matcher 通過） | implemented（改結構比對 event/matcher/檔名三元組＋negative lookahead＋2 新攻擊面測試） |
| C1③/C2③/C3③/C5③ | suggestion | ✅ | tool_input null／regen 非 object JSON／CRLF frontmatter／live hooks 結構異常的 crash-adjacent 路徑 | implemented（`or {}`／isinstance guard／startswith tuple／isinstance+UnicodeDecodeError） |
| C3①/C7③ | suggestion | ✅ | INVARIANTS `live` 鍵死資料 | implemented（函數改讀 `inv["live"]` expanduser） |
| C2①/C7①/C8① | suggestion | ✅ | 測試名誤導（ok_ 前綴掛 violation 案）/ASSET 路徑雙寫/byte_gate fixture 重複 | implemented（改名/ASSET_REL/make_pool desc 參數化） |
| C4① | suggestion | ✅ | rule↔skill 部署細節重複敘述（違 EP S4 分工約束） | implemented（rule 留紀律＋pointer 到 skill） |
| C5① | suggestion | ✅ | rollback 字串 EP/doc 雙份無機械比對 | implemented（單一留存 rollback doc，EP S2 改 pointer） |
| C6① | suggestion | ✅ | 簡體「恢复」混入 | implemented（恢復） |
| F2② | suggestion | ✅ | EP 行數 87 已過時（S1 擴充後實為 116） | implemented（改 wc -l 口徑不寫死） |
| F3② | suggestion | ✅ | I6 3.9 約束僅 prose——F1 示範部署後工具改寫風險 | implemented（.githooks/pre-commit 加 `python3 -m py_compile` hooks/＋generator 資產） |
| F4② | suggestion | ✅ | skills/CLAUDE.md memory-audit description 未反映 generator 池 | implemented（補 --check 投影驗證半句） |
| C4③ | suggestion | ❌ | replace FileNotFoundError fallback——寫入→replace 暫停 >60s 窗口下重寫可回退並行 run 的新索引（stale 覆寫風險＞消一次 exit-1 噪音收益） | rejected |
| C8③ | suggestion | ❌ | NotebookEdit notebook_path fallback——notebook 不會命名 MEMORY.md，死分支 YAGNI（agent 自評「維持現狀即可」） | rejected |
| C9① | suggestion | ❌ | harness 上限「200 行/25KB」五處複述——描述性事實各讀者語境需要，非 gate 執行數值；指針鏈傷局部可讀性 | rejected |
| F5② | — | 免改 | 兩池量測快照漂移（池是活的，後續條目寫入） | noted |

## Post-Build Review Findings（dual-context——fresh-eyes＋primed）

| ID | 嚴重度 | 裁決 | 摘要 | 狀態 |
|----|--------|------|------|------|
| F1① | 🟡 | ✅ | `_wiring` 漏看 per-hook `enabled: false`——單條停用仍算已部署（F8 第三形態，審查者機械重現） | implemented（skip disabled＋攻擊面測試） |
| F2① | 🟡 | ✅ | Stop 自動執行記憶目錄 generator 的信任邊界未設防——poisoned 條目→惡意 generator→每 turn 執行鏈 | implemented（ASSET_SOURCE byte 比對，不符跳過＋note；docstring 信任邊界；tamper 測試） |
| F3① | 🟢 | ✅ | ZCode 端 stderr 送達模型未證——註解限定 | implemented（docstring 覆蓋邊界段） |
| F4① | 🟢 | ✅ | regen 失敗不可見（Stop stdout 不進 context）——索引 stale 無錨點 | implemented（`_regen-failed` marker 寫入/清除＋SKILL 層 1 注記＋測試） |
| F5① | 🟢 | ✅ | 部署副本 freshness 無機械流程 | implemented（SKILL 層 1 cmp 先刷新；F2 防護反向強化） |
| F6① | 🟢 | ✅ | gate 覆蓋邊界（Bash redirect 不攔）未註明 | implemented（docstring；Bash matcher 擴充留 backlog） |
| F-1② | 🟡 | ✅ | generator frontmatter 違規分支零測試 | implemented（E2E 行為錨） |
| F-2② | ℹ️ | ✅ | rollback doc 雙份時代殘留句 | implemented（已刪） |
| F-3② | ℹ️ | noted | rules/AGENTS.md 索引行更新＝正向 drift（EP 未提但職責 ripple 一致） | noted |

## Live 驗證收案補記（2026-08-30 晚——跨 session 收口）

雙 harness 兩池全腿通過：Gate 擋寫（exit 2＋**stderr 指引送達模型**——A3 已證）／self-gating opt-in／Stop dispatch（mosaic 池 mtime 與 CC turn 邊界**秒級吻合**）／regen **add→remove 完整週期**（兩池各有直接觀察：ai-rules line 85 在→不在、mosaic line 91 在→自癒剔除）／兩池 `--check` 全綠（91＋97 entries）、無 `_regen-failed`。Rollback 備而未用。時效語義更正一筆：CC session「watcher 熱載入」宣稱為誤歸因——該 session 於 config 定稿（15:34）後啟動，屬新 session 預期路徑，「需新 session」假設未被推翻。

**協調面教訓（CC 驗證 session 回報，非 memory 材料）**：並行清理 race 掉了進行中驗證的觀察窗口——清理清單與驗證 session 的完成回報之間缺同步點；本次證據靠 19:21 regen 恰好落在寫入與刪除之間才救回（運氣非設計）。未來同類雙 session 協作：清理動作前先與進行中驗證 session 對時序，或驗證觀察點以 mtime/log 快照先行落底。

**深夜 relay 三項裁決（2026-08-30 收案後證據補強）**：
1. **A2 降級 ✅採納**：Claude 端 25KB 單位已實證＝**chars**——超限警示對 42,110 chars／56,604 bytes 的檔案報「at 41KB」，41K 只能對上 chars（bytes 口徑為 55.3KB）。雙 harness chars 口徑一致；bytes gate 保留為縱深防禦（成本零、防未來版本改口徑）。
2. **「watcher 熱載入」❌拒絕**：relay 宣稱「編輯 settings 的同一 session 內被攔」——transcript 查證不成立：該 session 19:01:04 啟動（settings 定稿於 15:34）、全程零 settings 編輯、gate 測試在 19:08/19:12。屬「config 定稿後新 session」預期路徑。「需新 session」假設維持（ZCode 有官方文檔；Claude 端熱載入未證）。
3. **多池清理維度 ✅採納**：清理/殘留掃描的維度是「檔名 × 池」——雙 harness 共用腳本跨多池後，每個 pool 都要 rg（本次 mosaic 池同名測試條目即漏件實例）。已補入 memory-audit SKILL 層 3。
