---
harness-scope: neutral
---

# 編輯紀律

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

## 核心原則

**優先編輯現有檔案，品質優先於向後相容。**

## 必須遵守的約束

- **優先編輯現有檔案**：必須優先編輯現有檔案而非創建新檔案
- **品質優先**：可以大幅重構來改善架構品質
- **快速迭代**：優先正確性和清晰度
- **架構優先**：預設不考慮向後相容，優先考慮架構品質
- **依賴方向**：import 必須遵循依賴層級（library → scripts（demo 入口））；scripts 不反向依賴 library 內部，可複用邏輯一旦累積須上抽進 library，不讓 scripts 變第二個 library
- **單一職責（SRP）**：一個 class/function 一個改變理由 — 改 A 不該順便碰 B；職責多時拆分而非堆疊
- **依賴向內（DIP）**：高層不依賴低層細節，依賴透過 interface（定義在內層）反轉；新增依賴先問「能否透過內層 interface」
- **不洩漏實作細節**：公開介面不暴露內部資料結構/型別；消費者不該知道實作
- **SOLID 指標**：SRP/OCP/LSP（子型替換）/ISP/DIP 實作時遵循（頂層總綱見 ai-development-guide「架構設計紀律」段；source 在 ai-rules repo）

---

## 衝突寫法處理（禁止混合）

> **核心原則**：程式庫中存在兩種矛盾寫法時，選擇一種，不要混合。

### 強制規則

- **禁止混合寫法**：兩種矛盾寫法「各照顧一點」的結果比任何一種原始寫法都更難維護
- **選擇並說明**：選擇較新或測試較完整的寫法，說明理由，標記另一種待清理
- **發現就標記**：遇到矛盾寫法時主動回報，不要默默自行融合

### 範例

```python
# ❌ 錯誤：混合兩種錯誤處理風格（部份用 try/except，部份用 assert）
def process(data):
    assert data is not None
    try:
        result = transform(data)
    except ValueError:
        return None
    assert result > 0
    return result

# ✅ 正確：統一使用一種風格（此處選擇 crash-only，符合專案哲學）
def process(data):
    assert data is not None
    result = transform(data)
    assert result > 0
    return result
```

---

## 向後相容確認機制

只有影響以下情況時才需要確認向後相容：
- 外部系統整合
- 數據處理流程
- 部署環境
- 用戶明確要求

---

## 變更範圍紀律

- **價值驅動，不投機**：可以加 validation / logging / config，但每個新增都必須能回答「解決什麼具體問題」
- **修 bug 與架構重構分開**：修 bug 只改必要的行；架構改善在重構段一次改好
- **清理自己的孤兒**：自己的改動造成的 dead import/variable 必須清理；預先存在的 dead code 只標記不刪

---

## ❌ 常見錯誤模式

### 為了向後相容而保留壞味道的設計

```python
# ❌ 錯誤：保留舊的、有問題的實作
def old_api():
    # 舊的、有問題的實作
    pass

def new_api():
    # 新的、更好的實作
    pass

# ✅ 正確：在測試保護下重構，移除舊 API
def refactored_api():
    # 重構後的乾淨實作
    pass
```

---

## 原理說明

- **修改現有檔案保持程式碼組織的一致性**
- **架構品質優先避免技術債務累積**
- **測試保護下的重構是安全的，長期收益大於短期遷移成本**
