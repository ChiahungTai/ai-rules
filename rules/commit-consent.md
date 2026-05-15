# Commit 同意約束

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

---

## 核心原則

**LLM 絕對不執行 git commit，除非用戶明確同意。**

---

## 強制規則

- **展示再確認**：commit 前展示變更摘要和建議的 commit message
- **等待確認**：用戶必須明確回覆「commit」「確認」「OK」等肯定詞
- **未確認不 commit**：未收到確認 → 不執行 git commit，不繼續下一步
- **適用所有命令**：包含 `/build`、`/code-review`、`/verify-review`、`/lint-fix` 等

---

## 適用範圍

此約束適用於所有可能觸發 git commit 的場景：

| 場景 | 正確行為 |
|------|---------|
| `/build` 段落完成 | 展示結果，不 auto-commit |
| `/code-review` 發現問題並修正 | 展示修正，等待用戶確認 |
| `/verify-review` 採納建議 | 展示變更，等待用戶確認 |
| `/commit` 用戶主動觸發 | 展示 message，等待用戶確認 |

---

## 例外

無。所有 commit 都需要用戶同意。

---

完整 commit 流程定義在 [commit.md](../../commands/commit.md)。
