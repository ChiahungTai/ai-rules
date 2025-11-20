已經都# AI Skills - 智能技能系統

## 🎯 模組用途

這個目錄包含自定義的 Claude Code Skills，提供專業化的技能和工具能力。所有 skills 都會透過 symbolic link 連結到 `~/.claude/skills/` 目錄，讓 Claude Code 可以調用這些專業技能執行特定任務。

## 📁 目錄結構

```
ai-analysis/skills/
├── CLAUDE.md                     # 本說明文件
├── mermaid/                      # Mermaid 圖表生成技能
│   └── SKILL.md                  # Mermaid 技能配置
└── [其他技能]/                   # 未來擴展的技能
    └── SKILL.md                  # 技能配置文件
```

## 🛠️ 核心 Skills

### mermaid - 專業圖表生成技能
- **功能**: 生成 Dark/Light 模式相容的 Mermaid 圖表
- **特色**: 高對比度配色、WCAG 可讀性標準、自動品質檢查
- **用途**: 技術文檔、系統架構圖、流程圖、時序圖
- **調用方式**: `skill: "mermaid"`

## 🏗️ 核心設計

### 技能標準化結構
每個技能都遵循統一的結構：
```
skill_name/
├── SKILL.md                      # 技能配置和說明
├── [實現文件]                    # 技能實現邏輯
└── [測試文件]                    # 技能測試用例
```

### 技能配置規範
每個 SKILL.md 必須包含：
- **name**: 技能名稱
- **description**: 功能描述
- **allowed-tools**: 可用工具列表
- **使用方式**: 詳細使用說明
- **最佳實踐**: 使用建議和注意事項

### 高可讀性標準
所有技能都必須符合：
- **文字對比度**: ≥ 7:1 (WCAG AAA 標準)
- **線條對比度**: ≥ 4.5:1 (WCAG AA 標準)
- **模式相容**: Dark/Light 模式都清晰可見
- **品質檢查**: 內建自動化檢查機制

## ⚠️ 重要注意事項

### 技能調用原則
- **明確調用**: 使用 `skill: "skill_name"` 語法
- **參數傳遞**: 清楚描述所需參數和期望結果
- **工具限制**: 只能使用 allowed-tools 中指定的工具
- **錯誤處理**: 優雅處理錯誤情況

### 色彩配置約束
- **棄用配置**: #374151, #94a3b8 (對比度不足)
- **推薦配置**: #111827, #475569 (高對比度)
- **強調色彩**: #059669, #dc2626, #d97706, #2563eb
- **自動驗證**: 技能內建色彩可讀性檢查

### 品質保證機制
- **生成前檢查**: 使用前驗證配置正確性
- **渲染後驗證**: 確保結果符合預期
- **模式測試**: Dark/Light 模式都測試過
- **文檔同步**: 配置變更同步更新文檔

## 🔗 相關模組

- **ai-analysis/agents**: Agents 可能調用這些 Skills
- **commands/**: Slash commands 可能使用這些 Skills
- **~/.claude/skills**: Claude Code 技能目錄 (symbolic link)
- **ai-analysis/reports/**: Skills 輸出的分析報告

## 🚀 使用方式

### 安裝 Skills
```bash
# 建立 symbolic link 到 Claude Code skills 目錄
ln -s /Users/ctai/Github/ai-rules/ai-analysis/skills/* ~/.claude/skills/
```

### 基本技能調用
```python
# 調用 Mermaid 技能生成圖表
skill: "mermaid"
"生成一個系統架構圖，包含前端、後端、資料庫三層"
```

### 在 Agents 中使用
```python
# Agent 配置中指定可用技能
allowed-tools: [Read, Write, Edit, "skill:mermaid"]

# 在 Agent 執行過程中調用
skill: "mermaid"
"根據分析結果生成視覺化圖表"
```

### 在 Commands 中使用
```markdown
# MD 模式命令中調用技能
skill: "mermaid"
# 生成專業技術圖表
```

## 📋 最佳實踐

### 技能設計原則
1. **單一職責**: 每個技能專注於特定功能
2. **標準接口**: 統一的調用方式和參數格式
3. **錯誤處理**: 優雅的錯誤處理和回饋
4. **文檔完整**: 詳細的使用說明和範例

### 技能使用建議
1. **按需調用**: 只在需要時調用對應技能
2. **參數明確**: 提供清楚的需求描述
3. **結果驗證**: 檢查技能輸出是否符合預期
4. **性能考慮**: 避免不必要的重複調用

### 擴展開發指南
1. **目錄結構**: 遵循標準技能目錄結構
2. **配置文件**: 完整的 SKILL.md 配置
3. **工具限制**: 明確 allowed-tools 列表
4. **測試覆蓋**: 提供完整的測試用例

## 🔧 技能開發模板

### 新技能目錄結構
```
new_skill/
├── SKILL.md
├── README.md          # 可選：詳細說明
├── examples/          # 可選：使用範例
│   └── example.md
└── tests/             # 可選：測試文件
    └── test_cases.md
```

### SKILL.md 模板
```markdown
---
name: new_skill
description: 技能功能描述
allowed-tools: [Read, Write, Edit, Grep]
---

# 技能名稱

## 功能描述
詳細說明技能的功能和用途

## 使用方式
```bash
skill: "new_skill"
"技能調用參數描述"
```

## 配置選項
- 選項1: 說明
- 選項2: 說明

## 最佳實踐
1. 使用建議1
2. 使用建議2

## 注意事項
- 注意事項1
- 注意事項2
```

---

*這個技能系統確保所有圖表和工具輸出都符合專業標準，在任何環境下都能提供最佳的視覺體驗。*