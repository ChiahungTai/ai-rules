---
harness-scope: neutral
---

# 文檔自洽性檢查規範

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

## 核心檢查原則

在撰寫或修改 instruction 檔（AGENTS.md source；Claude 端另有 CLAUDE.md wrapper）時，必須確保文檔的自洽性。

## 必要檢查項目

### 1. 術語一致性
- **術語定義統一**: 相同概念使用相同術語
- **大小寫一致**: 專業術語（如 API、CLI、HTTP）大小寫統一
- **編碼格式一致**: 檔案路徑、變數名稱使用一致格式

### 2. 章節結構
- **章節編號連續**: 標題層級正確（`#` → `##` → `###`）
- **目錄對應**: 目錄中的章節標題實際存在
- **層級合理**: 不跳級（如 `#` 之後直接 `###`）

### 3. 引用完整性
- **內部引用**: 引用目標存在（Claude 端 `@path` transclusion、各家 markdown link）
- **外部引用**: 連結檢查可訪問
- **交叉引用**: 章節間引用相互對應
- **single-source drift 防護（修改紀律）**: 改「定義源」（review-engine 共通邏輯 / 跨命令引用的 rule / 模式判定表）時，**強制 rg 掃所有引用該定義的命令/skill**，逐檔同步 — 否則「定義改了，引用沒跟」（drift regression）。實證：改 review-engine mode 表（移除 Main LLM）漏 build.md/ep-review.md 引用；改 human-review 命令漏 AGENTS 表/路徑 — 兩次 code-review 都抓到 drift。**機械步驟**：改定義後 `rg "<單一關鍵詞>" commands/ skills/ rules/`（如 `rg "Main LLM"`,或 alternation `rg "Workflow|Agent Tool"` — **禁用 `/` 當 alternation**,rg 的 `/` 是字面字元,會 false negative）→ 逐檔確認引用一致（rg 只 surface 候選,需人工 triage 合法引用 vs 過時引用）。code-review agent 跨檔查 drift 是兜底（事後），此紀律是事前防。已註冊的 single-source invariant 另有 `/sync-sources` 機械閘門長期保護（recurring invariant 應登記 `check_single_source.py` REGISTRY）；本紀律補未註冊的 ad-hoc case。

### 4. 前後邏輯
- **無矛盾陳述**: 前文說明與後文不衝突
- **範例與說明一致**: 程式碼範例符合文字描述
- **約束無衝突**: 不同約束條款可以同時滿足

### 5. 格式規範
- **程式碼區塊**: 語言標籤正確（```bash、```python）
- **表格格式**: Markdown 表格語法正確
- **列表格式**: 項目符號/縮排一致

## 快速自檢清單

完成 instruction 檔修改後，檢查：
- [ ] 所有引用（Claude `@path` / markdown link）目標存在
- [ ] 改定義源（review-engine/共通 rule/模式表）後，rg 掃所有引用該定義的命令，逐檔同步（single-source drift 防護）
- [ ] 章節編號連續無跳級
- [ ] 術語使用統一（無同義多詞）
- [ ] 程式碼範例可執行
- [ ] 無矛盾說明或規則
