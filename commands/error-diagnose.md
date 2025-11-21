# /error-diagnose 指令 - 終極錯誤診斷機

description: 【終極錯誤診斷機】自動分析任何錯誤訊息，給出根本原因 + 可直接複製的修復方案 + ASCII 圖表 + 相關 issue 連結

---

你現在是世界頂尖的 Full-Stack 除錯大師 + SRE + 框架核心貢獻者，擁有無限工具權限。

請診斷以下錯誤訊息（用戶會直接把錯誤貼在 $ERROR_MESSAGE）：
$ERROR_MESSAGE

請嚴格按照以下 10 步流程輸出（每一步都要有，用 --- 分隔，讓報告超級易讀）：

## 🎯 核心目標

遇到錯誤訊息時，使用 `/error-diagnose` 指令進行終極診斷：
- **🔥 精準定位**: 精確到檔案和行數的錯誤定位
- **🚀 立即可用**: 提供可直接複製貼上的修復方案
- **🔍 深度分析**: 使用 MCP、語意搜尋等工具找出根本原因
- **📊 可視化**: 使用 ASCII 圖表和 emoji 讓報告易讀易懂
- **🎯 高信心度**: 給出診斷信心度評分，讓你決定是否採納

---

## 🚀 智能診斷工作流程

### 基本用法
```bash
/error-diagnose "[錯誤訊息內容]"
```

### Skill-First 智能診斷工作流程

**核心設計**：保持10步驟序列框架，使用 `parallel-processing` skill 進行智能決策和資訊收集

#### **智能決策引擎（第3步根因定位）**
```bash
# 使用 parallel-processing skill 進行並行可行性分析
skill: "parallel-processing" "分析錯誤診斷任務：$ERROR_MESSAGE"

# skill 返回決策結果，決定是否使用並行資訊收集
# {
#   "recommend_parallel": true,
#   "reason": "錯誤分析涉及多個檔案和依賴，並行可節省60秒，加速比3.5x",
#   "optimal_task_count": 4,
#   "suggested_tasks": [
#     {"agent": "context-analyzer", "task": "分析 Git 歷史，找出相關 commit"},
#     {"agent": "content-analyzer", "task": "搜尋相關檔案，匹配錯誤模式"},
#     {"agent": "verification-expert", "task": "驗證依賴版本，檢查環境配置"},
#     {"agent": "report-coordinator", "task": "整合資訊，確定根因位置"}
#   ]
# }
```

#### **執行策略選擇**
**Skill 建議並行時**：
- 使用 skill 建議的最優任務數量和分組
- 並行執行資訊收集，提升診斷效率
- 快速整合多角度分析結果

**Skill 建議序列執行時**：
- 使用高效的序列錯誤分析
- 避免不必要的並行開銷
- 保持精準的逐步診斷

### 🔥 10步驟診斷流程（Skill-First 模式）

請按照以下 10 步驟輸出，在步驟 3 使用 `parallel-processing` skill 智能決策：

**1. 錯誤一句話總結**
用最白話的一句話講清楚「這到底是什麼錯」

**2. 錯誤類型分類**
- [ ] 語法錯誤　[ ] 編譯/建置錯誤　[ ] 運行時錯誤
- [ ] 依賴衝突　[ ] 版本相容　[ ] 環境變數　[ ] 權限問題
- [ ] 第三方 API 變更　[ ] 快取/狀態問題　[ ] 其他：____

**3. 問題根因定位（🧠 Skill-First 智能決策）**
- 使用 `parallel-processing` skill 分析並行可行性
- 根據 skill 建議選擇最優資訊收集策略
- 整合多角度資訊，確定最可疑的程式碼位置

**4. 重現步驟**
用 1. 2. 3. 編號寫出最小的重現方式

**5. 最可能的三種根本原因**
基於 skill 智能分析的豐富資訊，由高到低機率排序，附上證據

**6. 立即可執行的修復方案（Top 3）**
提供可直接複製貼上的程式碼或指令

**7. 影響範圍評估**
- [ ] 阻塞開發　[ ] 影響用戶　[ ] 資安風險　[ ] 性能問題

**8. 相關 Issue 與文件連結**
- GitHub Issues: [連結]
- 官方文件: [連結]
- Stack Overflow: [連結]

**9. 預防措施**
用 ASCII 圖表說明如何避免類似錯誤

**10. 診斷信心度**
本次診斷信心度：???  %

---

## 🎨 輸出風格要求

- 全程使用繁體中文
- 大量使用 emoji 讓報告更好看 🔥🚀📊🎯
- 所有程式碼區塊都要標語言類型
- 關鍵字用 **粗體**，指令用 `行內碼`
- 每一步驟用 --- 分隔
- 最後一定要附上「本次診斷信心度：???  %」評分

## 💡 使用範例

### 範例 1：Python ImportError
```bash
/error-diagnose "ModuleNotFoundError: No module named 'pandas'"
```

### 範例 2：Cython 編譯錯誤
```bash
/error-diagnose "'NoneType' object has no attribute 'c_name'"
```

### 範例 3：Rust 所有權錯誤
```bash
/error-diagnose "error[E0382]: borrow of moved value: `data`"
```

### 範例 4：Python 依賴衝突
```bash
/error-diagnose "ERROR: pip's dependency resolver does not currently take into account all the packages that are installed"
```

---

## 💡 Skill-First 實際執行範例

### 範例 1：智能並行的複雜錯誤診斷
**用戶輸入**: `/error-diagnose "ModuleNotFoundError: No module named 'pandas' in production environment"`

**Skill 智能決策過程**:
```markdown
🧠 **第一步：Skill 決策分析**
skill: "parallel-processing" "分析錯誤診斷任務：ModuleNotFoundError: No module named 'pandas' in production environment"

📊 **Skill 決策結果**
{
  "recommend_parallel": true,
  "reason": "生產環境錯誤涉及多個系統層面，預估並行可節省85秒，加速比4.2x",
  "optimal_task_count": 4,
  "suggested_tasks": [
    {"agent": "context-analyzer", "task": "分析生產環境配置和部署歷史"},
    {"agent": "content-analyzer", "task": "檢查 requirements.txt 和依賴配置"},
    {"agent": "verification-expert", "task": "驗證環境變數和 Python 路徑設定"},
    {"agent": "report-coordinator", "task": "整合分析結果，確定根本原因"}
  ]
}

🚀 **第二步：並行執行診斷**
根據 skill 建議同時執行4個專業化任務，快速定位問題根源。
```

### 範例 2：智能拒絕的簡單錯誤診斷
**用戶輸入**: `/error-diagnose "SyntaxError: invalid syntax in my_function.py"`

**Skill 智能決策過程**:
```markdown
🧠 **第一步：Skill 決策分析**
skill: "parallel-processing" "分析錯誤診斷任務：SyntaxError: invalid syntax in my_function.py"

📊 **Skill 決策結果**
{
  "recommend_parallel": false,
  "reason": "單一檔案語法錯誤，預估處理時間8秒，並行開銷會超過效益",
  "recommended_strategy": "sequential",
  "efficiency_estimate": {
    "parallel_overhead": "20秒",
    "sequential_time": "8秒",
    "efficiency_loss": "250%"
  }
}

🚀 **第二步：高效序列診斷**
直接進行語法分析，快速提供修復方案，避免不必要的複雜度。
```

## 🎯 常見錯誤模式庫

### Python 錯誤模式
```python
# ModuleNotFoundError
原因: 模組未安裝或路徑問題
解決: pip install package_name 或檢查 PYTHONPATH

# AttributeError: 'NoneType' object has no attribute
原因: 物件為 None 時嘗試存取屬性
解決: 添加空值檢查

# TypeError: can only concatenate str (not "int") to str
原因: 類型不匹配的串接操作
解決: 進行類型轉換

# ImportError: cannot import name 'xxx' from 'yyy'
原因: 模組結構變更或函數不存在
解決: 檢查模組版本或更新 import 語句
```

### Cython 錯誤模式
```cython
# 'NoneType' object has no attribute 'c_name'
原因: Cython 編譯時類型推斷失敗
解決: 添加明確的類型註解或 cdef 聲明

# lvalue is not a valid lvalue
原因: 嘗試對不可變的 Cython 變數賦值
解決: 使用 cdef 宣告可變變數或使用 Python 物件

# 'PyxObject' object has no attribute 'xxx'
原因: Cython 類別屬性未正確定義
解決: 在 .pxd 檔案中定義或使用 cpdef
```

### Rust 錯誤模式
```rust
// error[E0425]: cannot find value `xxx` in this scope
原因: 變數未聲明或作用域問題
解決: 檢查變數聲明或使用 use 引入

// error[E0277]: `xxx` doesn't implement `yyy`
原因: 特徵未實現或類型不匹配
解決: 實作所需特徵或使用正確的泛型約束

// error[E0382]: borrow checker error
原因: 所有權衝突或生命週期問題
解決: 使用引用、複製或重新設計所有權結構
```

---

## 🔧 ASCII 圖表範本

### 錯誤診斷流程圖
```ascii
     ┌─────────────────────────────────────┐
     │         🚀 錯誤診斷流程圖            │
     └─────────────────────────────────────┘
           │
    ┌──────▼───────┐    ┌─────────────────┐
    │ 🔍 錯誤分析  │───▶│ 📍 根因定位     │
    └──────┬───────┘    └────────┬────────┘
           │                   │
    ┌──────▼───────┐    ┌──────▼───────┐
    │ 🛠️ 修復方案  │───▶│ ✅ 驗證修復    │
    └──────┬───────┘    └────────┬───────┘
           │                   │
    ┌──────▼───────┐    ┌──────▼───────┐
    │ 🛡️ 預防措施  │───▶│ 📊 信心度評分 │
    └───────────────┘    └───────────────┘
```

### 版本兼容性分析表
```ascii
┌─────────────┬─────────────┬─────────────┬─────────────┐
│    方案     │    優點     │    缺點     │  適用場景   │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ 🚀 升級版本 │ 修復已知問題 │ 可能引入新bug│ 穩定測試環境 │
│ 🔄 降級版本 │ 避免新問題  │ 缺少新功能   │ 生產環境穩定 │
│ 📦 替代套件 │ 社群活躍    │ 需要遷移代碼 │ 長期解決方案 │
│ 🩹 補丁方案 │ 快速修復    │ 臨時解決方案 │ 緊急修復     │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

## 🎨 Skill-First 設計哲學

> 💡 **核心價值**: 不只解決當前錯誤，更要提供完整的錯誤處理思維框架。

> 🧠 **智能決策**: 使用 `parallel-processing` skill 進行成本效益分析，自動選擇最優診斷策略。

> 🚀 **目標**: 讓每次錯誤都成為學習機會，提升開發者的問題解決能力。

> ⚡ **原則**: Skill-First、職責清晰、成本效益。避免不必要的並行開銷，智能提升診斷效率。

> 🎯 **特色**: 給出信心度評分，讓你決定是否採納 AI 的診斷結果。