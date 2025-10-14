# Execution Plan Command - 段落式實作計畫書生成器

為量化交易專案生成**段落式實作計畫書**，執行 Phase 3 的分段實作與品質保證，專為功能實現、Examples驅動開發和品質保證設計。

**🚨 重要**: 此命令生成實作執行專精計畫書，專注於Phase 3的段落式實作方法論。系統分析請使用 `/analysis-plan`，系統設計請使用 `/design-plan`。

## 使用方式
```bash
/execution-plan "實作任務描述" [可選：PROMPT檔案路徑]
```

## 🎯 Execution Plan 段落式實作計畫書定位

### **主要受眾**
- **主要受眾**: AI執行Phase 3段落式實作
- **次要受眾**: `/impl` + Module Expert協作、功能實作Review

### **核心價值**
- **Self-Contained分段實作**: 每個功能段落獨立完整，應對context限制
- **Examples驅動開發**: 以可執行範例驗證功能，確保用戶體驗
- **強制Review機制**: 每段落完成後USER REVIEW，確保品質
- **生產就緒交付**: 輸出可部署的功能實作、完整Examples、測試套件

## 📚 專業知識庫 (強制自動載入)

🚨 **必須按順序載入以下核心文檔：**
1. CLAUDE.md - 基礎行為準則與環境約束
2. docs/plans/session_notes.md - 當前任務狀態
3. docs/ai_support/core/developer_comprehensive_guide.md - Examples驅動開發指導

## 🎯 段落式實作方法論核心

### **Phase 3的戰略地位**
Phase 3在故事驅動開發中是**功能實現的品質保證**：

- **Examples驅動驗證**: Examples是核心驗證機制，不只是輔助工具
- **Self-Contained執行**: 每個功能段落獨立執行，context效率最大化
- **強制Review品質**: 每段完成後USER REVIEW，避免累積品質債務
- **生產就緒標準**: 輸出可直接部署的高品質功能實作

### **🚨 強制分段實作原則**
**絕對禁止**: 一次完成複雜功能，必須按功能段落分段進行
**執行策略**: 功能段落1 → USER REVIEW → 功能段落2 → USER REVIEW → ...

## 🧠 智能設計分析與自動補強指導

### **🔍 執行前強制SD設計分析**
**執行 /execution-plan 時，AI 基於完整SD設計進行智能分析：**

#### **Step 1: SD設計基礎確認**
確認SD設計文檔包含實作必需資訊：
- **檔案結構**: 檔案樹展示和修改清單
- **Pseudo Code**: 完整的程式碼設計藍圖
- **API設計**: 方法簽名和參數定義
- **Call Stack**: 函數調用關係展示
- **架構決策**: 設計原因和技術考量

#### **Step 2: 實作導向智能分析**
基於完整的SD設計，AI 進行實作導向的智能分析：

**檔案影響分析**:
- 基於SD設計和現有代碼，分析實際需要修改的檔案
- 評估模組間依賴關係和整合複雜度
- 識別高風險變更和向後相容性問題

**實作模板生成**:
- 將SD設計的Pseudo Code轉換為具體實作框架
- 補強實作細節和方法調用關係
- 生成可直接參考的程式碼模板

**實作規範分析**:
- 分析API方法簽名的實作要求
- 明確錯誤處理和驗證策略
- 確保實作符合專案約束

#### **Step 3: Self-Contained段落智能生成**
基於SD設計和智能分析，生成真正獨立完整的功能段落：
- **Context獨立**: 每個段落包含完整實作資訊
- **實作就緒**: 提供可直接使用的程式碼框架
- **品質保證**: 整合Examples驗證和Review機制

## 🏗️ Execution Plan 計畫書標準結構

### **1. 實作任務概要 (基於智能分析)**
- **實作目標**: 基於Phase 2設計的具體實作目標
- **SD設計基礎**: 依據哪些SD設計文檔進行實作
- **智能補強摘要**: 自動分析發現的設計不足和補強策略
- **分段策略**: 功能分段的策略和Review節點
- **品質標準**: 每個段落的完成標準和驗收條件

### **2. Self-Contained分段執行設計**

#### **Self-Contained設計原則**
**目標**: 每個功能段落都是self-contained，AI只需讀取該段落就能獨立完成實作

#### **功能段落標準格式**
每個功能段落必須包含以下完整資訊：

**功能段落X: [功能名稱]**

#### 📋 段落概要 (Context獨立性)
- **功能描述**: [具體要實作的功能，1-2句話說明]
- **預期成果**: [完成後的具體成果和可驗證的輸出]
- **前置條件**: [執行前需要確認的條件和依賴]
- **預估時間**: [實作預估時間，幫助規劃]

#### 🎯 核心實作要點 (智能分析結果)
- **關鍵檔案**: [基於檔案影響分析的修改清單，最多3-5個]
- **核心邏輯**: [從SD設計提取並補強的實作邏輯，2-3個要點]
- **API設計**: [自動補強的介面規範和參數設計]
- **錯誤處理**: [驗證策略的具體應用]
- **Call Stack**: [自動分析的函數調用關係和執行順序]

#### 💻 程式碼指導 (智能生成的實作模板)
```python
# 基於SD設計智能生成的實作框架
class EnhancedImplementation:
    def core_method(self, params: SpecificType) -> ResultType:
        """
        智能補強的實作指導
        Call Stack: [自動分析的調用鏈]
        設計依據: [來自SD設計的具體依據]
        """
        # Step 1: [具體實作步驟，基於設計分析]
        # Step 2: [整合策略，基於依賴分析]
        # Step 3: [錯誤處理，基於驗證原則]
        pass
```

#### 🧪 Examples驗證 (功能驗證)
- **Examples檔案**: [對應的examples檔案名稱]
- **驗證場景**: [需要驗證的使用場景，2-3個]
- **執行命令**: [驗證examples的具體命令]

#### ✅ 完成檢查清單 (明確驗收)
- [ ] 核心功能實作完成且可運行
- [ ] Examples可正常執行並展示功能
- [ ] 錯誤處理邏輯驗證通過
- [ ] API介面符合設計規範
- [ ] 與現有系統整合無衝突

#### 🔗 下一段落銜接 (流程連貫)
- **交付物**: [本段落完成後的交付物]
- **下段前置**: [下一段落開始前需要的準備]

#### **Context限制應對策略**
**🚨 資訊濃縮原則** (最關鍵的創新點):

1. **一段落一功能**: 每個段落只專注一個明確功能，避免複雜性
2. **關鍵資訊優先**: 實作必需的資訊優先，細節可後補
3. **檔案引用最小化**: 每段落引用檔案數量控制在3-5個
4. **模板化指導**: 提供程式碼框架，減少從零開始的context消耗

#### **功能段落優先級設計**
- **P0核心段落** (必須完成):
  - 核心API實作
  - 基礎Examples驗證
  - 關鍵錯誤處理

- **P1重要段落** (重要功能):
  - 進階功能實作
  - 整合測試驗證
  - 效能優化

- **P2增值段落** (可選功能):
  - 輔助工具
  - 詳細文檔
  - 額外Examples

### **3. Examples驅動開發策略**

#### **Examples核心價值重新定位**
Examples在故事驅動開發中是**核心驗證機制**，具備4個關鍵角色：

1. **設計驗證器**: Examples展示API設計是否直覺易用
2. **功能完整性檢查**: Examples必須涵蓋90%以上的實際使用場景
3. **用戶接受度測試**: Examples代表真實用戶的實際操作流程
4. **測試設計參考**: Examples內容可作為編寫自動化測試的設計參考

#### **Examples目錄結構標準**
**檔案命名規則**:
- `basic_{功能}_usage.py` - 基礎使用 (P0: 最重要)
- `advanced_{功能}.py` - 進階功能 (P1)
- `{功能}_integration.py` - 跨模組整合 (P1)
- `migration_from_{舊API}.py` - 遷移指南 (P2)
- `troubleshooting_{功能}.py` - 問題排解 (P2)

#### **Examples品質標準**
- ✅ **可執行性**: 所有examples在乾淨環境中可直接執行
- ✅ **完整性**: 涵蓋90%以上的實際使用場景
- ✅ **易學性**: 新用戶能通過examples在20分鐘內完成基本操作
- ✅ **實用性**: Examples直接解決真實世界的問題
- ✅ **維護性**: Examples程式碼簡潔清晰，註解充分

#### **Examples開發優先級**
1. **P0**: basic_usage.py - 最核心的使用方式
2. **P1**: integration.py - 與其他模組的整合使用
3. **P2**: advanced_features.py - 進階功能展示
4. **P3**: migration_guides.py - 遷移和升級指南
5. **P4**: troubleshooting.py - 問題排解和最佳實踐

### **4. 測試策略與品質保證**

#### **測試分工明確化**
- **Examples職責**: 展示使用方式、驗證用戶體驗、提供測試設計參考
- **Tests職責**: 自動化回歸測試、邊界條件測試、性能測試

#### **品質保證檢查清單**
- **功能正確性**: 核心功能符合設計規範
- **API易用性**: 通過Examples驗證API設計直覺性
- **錯誤處理**: 邊界條件和異常情況的處理
- **整合穩定性**: 與現有系統的整合測試
- **代碼品質**: 符合專案代碼規範和風格

### **5. 實作段落模板範例**

#### **範例1: 核心功能段落模板**
```markdown
## 功能段落1: DataGateway數據載入核心實作

### 📋 段落概要 (Context獨立性)
- **功能描述**: 實作DataGateway的統一數據載入介面，支援多數據源整合
- **預期成果**: 可運行的DataGateway類別，支援主要數據源和本地檔案數據載入
- **前置條件**: 資料模組結構已建立，基礎配置檔案存在
- **預估時間**: 4-6小時

### 🎯 核心實作要點 (濃縮精華)
- **關鍵檔案**:
  - `data/gateway/data_gateway.py` (核心實作)
  - `data/providers/base_provider.py` (基礎介面)
  - `examples/data/basic_data_loading.py` (驗證範例)
- **核心邏輯**:
  1. 統一數據載入介面設計 (load_data方法)
  2. 多提供者策略模式實作 (Provider Pattern)
  3. 數據驗證和錯誤處理機制
- **API設計**: `DataGateway.load_data(symbol, start_date, end_date, provider='default')`
- **錯誤處理**: 數據來源異常、日期範圍驗證、數據格式錯誤

### 💻 程式碼指導 (實作模板)
```python
class DataGateway:
    def __init__(self, config: Dict):
        self.providers = {}  # 數據提供者註冊
        self.cache_enabled = config.get('cache_enabled', True)

    def load_data(self, symbol: str, start_date: datetime,
                  end_date: datetime, provider: str = 'default') -> pd.DataFrame:
        # 1. 參數驗證
        assert isinstance(symbol, str), "Symbol must be string"
        assert start_date < end_date, "Invalid date range"

        # 2. 提供者選擇和數據載入
        provider_instance = self.providers[provider]
        data = provider_instance.fetch_data(symbol, start_date, end_date)

        # 3. 數據驗證和回傳
        return self._validate_data(data)
```

### 🧪 Examples驗證 (功能驗證)
- **Examples檔案**: `examples/data/basic_data_loading.py`
- **驗證場景**:
  1. 主要數據源數據載入 (熱門商品, 最近30天)
  2. 錯誤處理驗證 (無效商品代碼)
  3. 日期範圍邊界測試
- **執行命令**: `python examples/data/basic_data_loading.py`

### ✅ 完成檢查清單 (明確驗收)
- [ ] DataGateway類別實作完成且可實例化
- [ ] load_data方法可正常載入主要數據源數據
- [ ] Examples可正常執行並展示數據載入結果
- [ ] 錯誤處理邏輯通過邊界測試
- [ ] API介面符合設計規範 (參數類型、回傳格式)

### 🔗 下一段落銜接 (流程連貫)
- **交付物**: 可運行的DataGateway和basic_data_loading.py範例
- **下段前置**: DataGateway基礎功能驗證通過，準備擴充快取機制
```

#### **範例2: 整合功能段落模板**
```markdown
## 功能段落3: DataGateway與Strategy系統整合

### 📋 段落概要 (Context獨立性)
- **功能描述**: 整合DataGateway到現有Strategy系統，實現策略回測數據來源統一
- **預期成果**: 所有Strategy類別可透過DataGateway取得統一格式數據
- **前置條件**: DataGateway核心功能完成，BaseStrategy類別存在
- **預估時間**: 3-4小時

### 🎯 核心實作要點 (濃縮精華)
- **關鍵檔案**:
  - `strategy/base_strategy.py` (修改基礎類別)
  - `strategy/trend_following.py` (範例策略更新)
  - `examples/strategy/integrated_backtest.py` (整合驗證)
- **核心邏輯**:
  1. BaseStrategy注入DataGateway依賴
  2. 統一數據介面替換現有分散數據載入
  3. 向後相容性確保 (暫時保留舊介面)
- **API設計**: `BaseStrategy.__init__(data_gateway: DataGateway)`
- **錯誤處理**: 數據載入失敗時的策略降級處理

### 💻 程式碼指導 (實作模板)
```python
class BaseStrategy:
    def __init__(self, data_gateway: DataGateway, config: Dict):
        self.data_gateway = data_gateway
        self.config = config

    def load_strategy_data(self, symbol: str, period: str) -> pd.DataFrame:
        # 統一透過DataGateway載入數據
        start_date, end_date = self._calculate_period_range(period)
        return self.data_gateway.load_data(symbol, start_date, end_date)

    def backtest(self, symbols: List[str]) -> Dict:
        # 整合回測邏輯，使用統一數據來源
        results = {}
        for symbol in symbols:
            data = self.load_strategy_data(symbol, self.config['backtest_period'])
            results[symbol] = self._run_strategy(data)
        return results
```

### 🧪 Examples驗證 (功能驗證)
- **Examples檔案**: `examples/strategy/integrated_backtest.py`
- **驗證場景**:
  1. 趨勢策略使用DataGateway執行回測
  2. 多商品組合策略驗證
  3. 與舊版本結果一致性檢查
- **執行命令**: `python examples/strategy/integrated_backtest.py`

### ✅ 完成檢查清單 (明確驗收)
- [ ] BaseStrategy成功整合DataGateway
- [ ] 現有策略 (trend_following) 遷移成功
- [ ] Examples執行結果與預期一致
- [ ] 向後相容性確認 (舊版本策略仍可運行)
- [ ] 整合測試涵蓋多種數據來源場景

### 🔗 下一段落銜接 (流程連貫)
- **交付物**: 完整整合的Strategy系統和驗證範例
- **下段前置**: 所有核心功能整合完成，準備進行系統效能優化
```

## 🚨 專案特定約束模板

### **實作執行專用約束範例**
> **注意**: 以下約束需要根據實際專案的 CLAUDE.md 進行客製化

- **驗證策略**: 定義專案的驗證機制（如：assert優先、fail fast策略）
- **向後相容性**: 定義專案的相容性政策（如：允許破壞性變更）
- **Examples優先**: 先讓examples能跑，再完善內部實作
- **實際運行驗證**: 修改代碼後必須立即執行相關測試或範例程式

### **執行環境約束範例**
> **注意**: 需根據專案實際環境配置

- **Python環境**: 專案使用的Python版本和虛擬環境路徑
- **環境變數**: 必要的環境變數設定（如：PYTHONPATH）
- **工作目錄**: 執行命令時的標準工作目錄
- **路徑管理**: 專案的統一路徑管理工具或模組

### **文檔輸出約束範例**
> **注意**: 需根據專案文檔結構定義

- **儲存路徑**: Execution Plan 文檔的標準儲存位置
- **Self-Contained要求**: 每個功能段落獨立完整
- **強制Review**: 每個段落完成後必須USER REVIEW

## 📋 Execution Plan 計畫書品質檢查

### **Self-Contained設計驗證**
- [ ] **獨立性**: 不讀取其他段落也能理解要做什麼
- [ ] **完整性**: 包含所有執行必需的資訊 (檔案、邏輯、驗證)
- [ ] **可驗證**: 有明確的完成標準和檢查方法
- [ ] **精華濃縮**: 資訊密度高，context使用最小化
- [ ] **實作導向**: 提供具體程式碼框架，而非抽象描述

### **Examples驅動設計品質**
- [ ] Examples涵蓋90%以上使用場景
- [ ] 基礎Examples (P0) 完整設計
- [ ] 整合Examples (P1) 跨模組驗證
- [ ] Examples可執行性和易學性保證

### **分段執行合理性**
- [ ] 功能段落劃分合理且相對獨立
- [ ] 每個段落有明確的目標和交付物
- [ ] Review檢查點設計清晰可執行
- [ ] 段落間的依賴關係和銜接明確

## 🔧 輸出和後續行動

Execution Plan生成完成後：

### **直接輸出**
1. **計畫書路徑**: 提供完整的Execution Plan檔案位置
2. **智能分析報告**: SD設計基礎確認和實作導向分析結果
3. **實作範圍摘要**: 分段實作的核心範圍和功能
4. **SD設計對應**: 與Phase 2 SD設計的對應關係說明
5. **分段執行提醒**: 強調功能段落分段執行和Review機制

### **後續行動建議**
- **開始執行**: 使用 `/impl` + Module Expert基於此計畫書執行Phase 3實作
- **SD設計基礎**: 確認SD設計文檔完整且準確
- **功能段落執行**: 按P0→P1→P2順序逐段執行，每段完成後USER REVIEW
- **Examples優先**: 每段都先實現Examples可執行，再完善內部實作

### **session_notes更新**
- 記錄Execution Plan生成結果和分段實作規劃
- 更新功能段落執行順序和Review檢查點
- 記錄Examples驅動開發策略和品質標準

---

**重要**: 此命令專注於段落式實作計畫書生成，為Phase 3執行提供詳細指導。SA分析規劃請使用 `/analysis-plan`，SD設計規劃請使用 `/design-plan`。

**🚨 強制要求**:
- **🧠 必須執行智能設計分析**: 基於完整SD設計進行實作導向分析
- **📁 必須進行檔案影響分析**: 基於SD設計和現有代碼分析實際修改檔案
- **💻 必須生成實作模板**: 將SD設計轉換為具體可執行的程式碼框架
- **🔗 必須展示Call Stack**: 分析和展示函數調用關係和執行順序
- 必須設計Self-Contained功能段落，應對context限制
- 必須設計強制Review機制，每段完成後USER REVIEW
- 必須包含完整的Examples驅動開發策略
- Examples必須可執行且涵蓋90%使用場景
- 實作必須基於SD設計和智能分析結果
