---
harness-scope: neutral
---

# Commit 同意約束

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

---

## 核心原則

**LLM 絕對不執行 git commit，除非用戶明確同意。**

---

## 強制規則

- **展示再確認**：commit 前展示變更摘要和建議的 commit message
- **等待確認**：用戶必須明確回覆「commit」「確認」「OK」等肯定詞
- **未確認不 commit**：未收到確認 → 不執行 git commit，不繼續下一步
- **適用所有場景**：包含 build、review、fix 等任何可能觸發 commit 的流程

---

## 適用範圍

此約束適用於所有可能觸發 git commit 的場景：

| 場景 | 正確行為 |
|------|---------|
| 任務段落完成（如 build） | 展示結果，不 auto-commit |
| review 後發現問題並修正 | 展示修正，等待用戶確認 |
| 採納 review 建議 | 展示變更，等待用戶確認 |
| 用戶主動要求 commit | 展示 message，等待用戶確認 |

---

## 例外

無。所有 commit 都需要用戶同意。

---

完整 commit 流程定義在各自 harness 的 commit 命令文檔（Claude: `commands/commit.md`）。
