# Multi-harness 文檔鏡像

各 harness 官方文檔的 local 鏡像，作為跨 harness（Claude Code / OpenCode / ZCode）契約的 ground truth，供設計 harness-neutral 規則、跨 harness adapter、或撰寫中性指令時離線查證。

> 搭配 [`contracts.md`](contracts.md)（各 harness 契約對照表）與 [`manifest.json`](manifest.json)（每頁 url / path / sha256 / status）一起用。

## 來源與抓取方式

| harness | 來源站 | 發現機制 | 內容取得 | status |
|---------|--------|---------|---------|--------|
| **claude-code** | code.claude.com | `/llms.txt`（含 Docs + Changelog，給 `.md` 直連）+ `/blog` 索引 | 抓 `.md`；blog 無 `.md` 時 HTML 抽取 | `ok`（verbatim md） |
| **opencode** | opencode.ai | `/sitemap.xml` | url 補 `.md` 結尾 | `ok`（verbatim md）；無 `.md` 匯出的頁（多為各語系 policies/references + section 根）標 `fail` |
| **zcode** | zcode.z.ai | 從 `/cn/docs/welcome` SSR nav 抽連結（該站是 Next.js SPA，`/sitemap.xml`/`/llms.txt` 回傳假 shell，不可用） | SSR-HTML 抽取純文字 | `extracted-html`（含 sidebar nav chrome，非 verbatim） |

> 三站**都不需 Playwright**：claude/opencode 有 markdown 端點，zcode 雖 CSR 但 doc 路由有 SSR 內容 + nav。

## 目錄結構

```
ref-docs/harness/
├── README.md          # 本檔
├── contracts.md       # 各 harness 契約對照表（memory 檔/skill/agent/command/hook/MCP/settings）
├── manifest.json      # 每頁 url/path/sha256/status（refresh 時偵測變化）
├── crawl.py           # 爬蟲（見下）
├── claude-code/       # docs/en/... + blog/...
├── opencode/          # docs/<locale>/...
└── zcode/             # cn/docs/...
```

## Refresh

```bash
uv run python ref-docs/harness/crawl.py                            # 全三站
uv run python ref-docs/harness/crawl.py --source claude-code       # 單站（merge 進既有 manifest，不 clobber 其他）
uv run python ref-docs/harness/crawl.py --source zcode --limit 3   # smoke test
```

- **Deterministic**：只在 sha256 改變時才寫檔 → refresh 只動真的變的頁，diff 最小。
- **manifest merge**：`--source X` 只更新 X，保留其他 source 條目；頂層 `generated_at` 每次刷新。
- zcode 若日後改版導致 nav 抽不到連結，會印 `[WARN] zcode: seed ... unreachable`——屆時檢查 nav 結構是否變動。

## Provenance / 版權

本目錄內容為各 harness**官方公開文檔的本地鏡像**，僅供離線查證：

- 版權歸各原作者（Anthropic / OpenCode / Z.ai 智譜）。鏡像非官方認可、非再授權。
- `claude-code`、`opencode` 為 verbatim markdown；`zcode` 為 SSR-HTML 抽取的純文字（非 verbatim，含少量 nav chrome）——以 `manifest.json` 的 `status` 欄區分。
- 文檔會 stale。**有疑問以原站為準**；refresh 後 manifest 的 `sha256` 變化可用來追蹤各頁何時變動。
