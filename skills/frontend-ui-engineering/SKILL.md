---
name: frontend-ui-engineering
description: Builds production-quality UIs with Panel/Bokeh. Use when building or modifying interactive dashboards, data visualization apps, or any Panel/Bokeh-based interface. Use when creating Panel components, implementing reactive layouts, managing param state, or optimizing Bokeh rendering performance.
---

# Panel / Bokeh UI Engineering

基於 Panel + Bokeh 的互動式數據視覺化應用開發規範。

## Component Architecture

- 繼承 `pn.viewable.Viewer`（不是 `param.Parameterized`），透過 `__panel__()` 支援 `.servable()` 直接部署
- Widget **不能宣告為 class-level attribute**（所有 instance 共用同一個 widget）
- 用 `pn.Param(self)` 或 `widget.from_param(self.param.x)` 從 param 自動生成 widget，確保雙向綁定

## Reactive Programming

- **綁定 `.param.x`（reference）不是 `.x`（value）**— 後者永遠不會更新
- 偏好 `pn.rx()` reactive expressions 進行鏈式反應
- 用 `pn.rx.when(button)` 控制 transient events（按鈕點擊）
- Side-effect-only callbacks：用 `watch=True` 或 `button.on_click()`
- **更新 `.object` 而非重建 Panel 物件** — 重建會閃爍且低效

## Performance

- `@pn.cache` 自動 memoization
- `pn.state.as_cached('key', loader_func)` 跨 session 資料快取
- `pn.extension(defer_load=True, loading_indicator=True)` 延遲載入
- Slider 用 `value_throttled`（不是 `value`）避免頻繁觸發
- `hv.DynamicMap` 包裹 HoloViews plots，更新時保留 zoom/axis 範圍

## Layout

- `pn.FlexBox` 優於 `Column`/`Row`（響應式自動換行）
- Templates（`FastListTemplate`、`FastGridTemplate`）用於 polished dashboards
- `sizing_mode="stretch_both"` / `"stretch_width"` 響應式尺寸

## State Management (param)

- `obj.param.update()` 批次更新多個 param（atomic change）
- `@param.depends('x', watch=True)` 聲明式依賴

## Common Pitfalls

| 問題 | 症狀 | 修正 |
|------|------|------|
| 綁定 `.x` 非 `.param.x` | 靜默失敗，不更新 | 改用 `.param.x` |
| Widget 當 class attribute | 多 instance 共用狀態 | 在 `__init__` 中建立 |
| 重建 Panel 物件 | 閃爍 + 低效 | 更新 `.object` |
| `col.objects[0] = 'x'` | 不觸發 watcher | 用 `col[0] = 'x'` |

## Deployment

```bash
panel serve app.py                          # 單進程
panel serve app.py --num-procs 4            # 多進程
panel serve app.py --auth-provider oauth    # 認證
```

- `pn.state.onload()` 初始化 session
- `pn.state.on_session_destroyed()` 清理資源
