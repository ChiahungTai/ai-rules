---
name: mermaid
description: 實用主義的 Mermaid 圖表生成工具，使用預設配置確保最大相容性
allowed-tools:
  - Read
  - Write
  - Edit
---

# Mermaid 圖表生成

## 核心原則

**不加任何 `%%{init: {...}}%%` 配置。** 預設主題已足夠通用，自定義配置會造成 Dark/Light Theme 相容性問題。

## Style 規範

### 硬限制

- `fill` + `color` 必須同時指定（缺一不可）
- 最多 **3 個組件**使用 style
- 註解只用 `%%`，必須獨占一行，不與程式碼同行

### 安全配色

| 狀態 | fill | color | 用途 |
|------|------|-------|------|
| 成功 | `#10b981` | `#ffffff` | 完成節點 |
| 失敗 | `#ef4444` | `#ffffff` | 錯誤節點 |
| 警告 | `#f59e0b` | `#000000` | 注意節點 |
| 資訊 | `#3b82f6` | `#ffffff` | 處理中 |

禁止：`#000000`（Dark 消失）、`#ffffff`（Light 消失）、`#808080`（對比不足）。

### Emoji 優先

用 Emoji 減少顏色依賴。含 Emoji 的節點名稱必須用引號：`A["🚀 開始"]`。

## 範例

```mermaid
flowchart TD
    A["🚀 開始"] --> B["📋 檢查數據"]
    B --> C{"❓ 驗證通過?"}
    C -->|是| D["🎉 成功"]
    C -->|否| E["❌ 失敗"]

    style D fill:#10b981,color:#ffffff
    style E fill:#ef4444,color:#ffffff
```
