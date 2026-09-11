# Illustrate 使用範例

> **引用情境**: 需要理解 `/illustrate` 各模式的實際輸出格式和效果時參考。

---

## 範例 1: 單一概念解釋（Console 模式）

```bash
/illustrate Docker 容器化
```

輸出：

```
【核心概念】
Docker 將應用程式打包成輕量級、可移植的容器
┌─────────┐    ┌──────────┐    ┌─────────┐
│ 應用程式 │ →  │ Docker   │ →  │ 容器運行│
│ + 依賴   │    │ 打包     │    │ 任何環境│
└─────────┘    └──────────┘    └─────────┘

【關鍵優勢】
• 環境一致性：開發、測試、生產環境完全相同
• 快速部署：秒級啟動，資源占用少
• 版本管理：映像檔版本控制，易於回滾
```

---

## 範例 2: 目錄智能分析（多檔案，自動並行）

```bash
/illustrate @src/ @config/ @docs/
```

系統檢測到 15+ 檔案，自動啟動多個 Tasks 並行處理。

### 結構分析結果（Task structure-analyzer）

```
┌─────────────┐
│  Presentation│ ← @src/components/
└─────────────┘
       ↓
┌─────────────┐
│   Business  │ ← @src/services/
└─────────────┘
       ↓
┌─────────────┐
│    Data     │ ← @src/models/
└─────────────┘
```

### 內容分析結果（Task content-analyzer）

識別核心服務：
- AuthService：JWT 認證機制
- PaymentService：第三方支付整合
- NotificationService：郵件/簡訊通知

### 上下文分析結果（Task context-analyzer）

分析 Git 歷史：
- 2 個月前從 monolithic 重構為 microservices
- 最近活躍開發：PaymentService 功能擴充

---

## 範例 3: MD 檔案深度分析

```bash
/illustrate md @architecture/ @database-schema.sql
```

輸出完整 Markdown 報告，結構如下：

```markdown
# 系統架構分析報告

## 一、整體架構概覽
（Mermaid 架構圖：Frontend → Backend → Data Layer）

## 二、資料庫設計分析
### 2.1 核心表結構
（Mermaid ER 圖：資料表關聯）

## 三、組件交互分析
（Mermaid 序列圖：API 呼叫流程）

## 四、建議與總結
（改進建議和架構優化方向）
```

MD 模式與 Console 模式的關鍵差異：
- 使用 Mermaid 圖表取代 ASCII 圖表
- 多層次展開而非精簡摘要
- 自動儲存為 `ai-analysis/reports/` 下的檔案

## 範例 4: HTML 報告殼輸出（opt-in）

```bash
/illustrate html @src/components/     # mode B：artifact 選型 → 概念→載體映射（判準見 diagram-selection）
/illustrate html 微服務架構            # mode D：主題 → 報告殼（mermaid/HTML 塊）
/illustrate html @ai-analysis/_tasks/<task>/ep.md  # Report Shell：EP 導讀殼（@任務家/<task>/ep.md——repo 任務家探測見「html 報告殼」段）
```

產出形態（細節見 [illustrate-html-mode.md](illustrate-html-mode.md)）：
- grounding 事實 → 殼（template 複製＋填 slot）＋章節敘事＋mermaid 圖（srcdoc lazy render／`diagram-*.svg`）或 HTML 塊
- 殼 `index.html` 落任務家（流程 brief）或 `ai-analysis/<域>/`（按需視覺/決策 viewport），**進 git**；`.mmd` 源＋`diagram-*` 渲染（svg）全進 git（AIR-74）
- 渲染工具缺場 → 降級 MD Mermaid＋回報
