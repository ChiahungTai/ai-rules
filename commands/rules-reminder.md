---
description: "快速提醒 LLM 最常忘記的規則 — 避免權限提示卡關"
when_to_use: "Remind the LLM of rules most frequently violated: no # in python -c, use rg/fd not grep/find, always uv run, no sed for code, split pipe commands."
usage: "/rules-reminder"
allowed-tools: ["Read"]
---

# /rules-reminder — 最常被忘記的規則

載入 `rules-reminder` skill，提供 LLM 最常犯的六條規則。

## 📚 委託 Skills

- **`rules-reminder`** — `#` 是毒藥、`grep`/`find` 是禁區、`uv run` 是王道、`sed` 是地雷、`|` 是陷阱、簡體字是違規
