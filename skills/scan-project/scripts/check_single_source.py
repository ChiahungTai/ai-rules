#!/usr/bin/env python3
"""Single-source invariant checker for ai-rules.

機械驗證 ai-rules 的「唯一/單一源/真相源」宣稱沒被 drift。

背景：2026-06 的 code-review 發現 review-engine 重構「正確診斷、不足處方」——
single-source 宣稱用散文維護，靠 AI 紀律 + 手動 rg，沒有機械力把「定義源」與
「schema 源」綁住（信心水準就是第一個受害者：review-engine 定義了，DimensionVerdict
schema 卻沒欄位）。本檔是當初少開的那張處方：把 single-source 變成可機械檢查的登記。

Run: uv run python skills/scan-project/scripts/check_single_source.py
Exit: non-zero if any critical/important finding（未來可掛 commit gate）。
"""
import re
import sys
from pathlib import Path

# scripts/ -> scan-project -> skills -> repo root
REPO_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# REGISTRY —— 每個「唯一/單一源/真相源」宣稱一筆。
# 新增 single-source 宣稱 = 在此加一筆 = 宣告單一源本來該付的成本。
# （本檔出現前，散文宣稱是欠了這成本沒付 → drift 必然。）
# ---------------------------------------------------------------------------
INVARIANTS = [
    {
        "id": "severity",
        "type": "enum",
        "source": "skills/review-engine/SKILL.md",  # 唯一定義源
        "values": ["critical", "important", "suggestion"],
        "enforced_by": {
            "file": "commands/claude/_common/workflow-review-pattern.md",
            "schema": "DimensionVerdict",
        },
        "note": "review-engine 是嚴重度唯一定義源；DimensionVerdict schema 必須含 severity 欄位",
    },
    {
        "id": "confidence",  # 信心水準
        "type": "enum",
        "source": "skills/review-engine/SKILL.md",  # 定義源
        "values": ["confirmed", "evidence-based", "inferred"],
        "enforced_by": {
            "file": "commands/claude/_common/workflow-review-pattern.md",
            "schema": "DimensionVerdict",
        },
        "note": "review-engine 宣稱『每個 finding 必須標信心水準』；DimensionVerdict 必須含 "
                "confidence 欄位，否則 Workflow 模式（唯一有 schema 強制的模式）結構性丟棄此訊號",
    },
    {
        "id": "audience_self_declare",
        "type": "classification",
        "source": "CLAUDE.md",  # 受眾模型（外部分類源）
        "commands": ["commands/illustrate.md", "commands/deliverable-review.md"],  # layer 3 人類 viewport
        "must_contain_any": ["layer 3", "人類 viewport", "B 軸", "受眾"],
        "note": "CLAUDE.md 分類為 layer 3 的命令本體必須自標受眾 —— 與 /code-review axis 3 "
                "共用 arch-thinking skill 的消歧對稱（外部分類 + 命令不自知 = drift 溫床）",
    },
    {
        "id": "skill_allowlist_coverage",
        "type": "coverage",
        "source_glob": "skills/*/SKILL.md",  # 定義源：每個 skill 的 frontmatter name
        "source_field": "name",
        "enforced_by": {
            "file": "settings.json",
            "extract": r"Skill\(([^)]+)\)",  # 從 allow-list 提取已授權 skill name 集合
        },
        "note": "skills/*/SKILL.md 的 name 是 skill 唯一定義源；settings.json allow-list 必須覆蓋每個 "
                "Skill(<name>) — rename 後新名缺 allow-list = drift（memory code-review-settings-sync "
                "反覆性，靠機械閘門根治）。單向：只抓 missing；dead entry（舊名殘留）因 settings 含 "
                "commands/built-in/plugin 需分類不抓，危害僅 noise 且 rename 必伴隨 missing 觸發修復。",
    },
    {
        "id": "base_perspective",
        "type": "source_contains",
        "source": "skills/review-engine/SKILL.md",
        "must_contain_any": ["預設 3 agent", "3-perspective"],
        "note": "review-engine base 點 4 定義 3-perspective（clean/UC/Correctness）為單一源 —— "
                "防未來 drift 回 2-perspective。消費者反向（活躍文檔 rg 2-perspective 應 0 hits）"
                "靠 rg + EP Review 兜底（消費者引用形態不一，機械反向 check 留未來）",
    },
]


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT))


def extract_schema_block(text: str, schema_name: str) -> str | None:
    """回傳 '### <schema_name>' 標題下的第一個 ```json block 內容；找不到回 None。"""
    pat = re.compile(
        r"^#{2,4}\s.*?" + re.escape(schema_name) + r".*?$.*?```(?:json)?\n(.*?)\n```",
        re.DOTALL | re.MULTILINE,
    )
    m = pat.search(text)
    return m.group(1) if m else None


def check_enforced_by(inv: dict) -> list[tuple[str, str, str]]:
    """定義在 source、強制 schema 在 enforced_by.file → schema 必須真的含該欄位。

    抓「定義源 / schema 源分離」的 drift：review-engine 定義了信心水準，
    但 DimensionVerdict schema 沒欄位 → 高規格 Workflow 審查結構性丟棄該訊號。
    """
    if inv.get("type") != "enum":
        return []  # check_enforced_by 是 enum 專屬（定義 values + schema 強制欄位）；coverage 的 enforced_by 語意不同（extract pattern），由 check_coverage 處理
    eb = inv.get("enforced_by")
    if not eb:
        return []
    f = REPO_ROOT / eb["file"]
    if not f.exists():
        return [(inv["id"], "critical", f"enforced_by 檔案不存在: {eb['file']}")]
    text = read_text(f)
    field = inv["id"]
    schema_name = eb.get("schema")
    if schema_name:
        block = extract_schema_block(text, schema_name)
        if block is None:
            return [(inv["id"], "important",
                     f"{eb['file']} 找不到 schema 區段 '{schema_name}'（標題或 ```json 格式變了？）")]
        if f'"{field}"' not in block:
            return [(inv["id"], "critical",
                     f"{eb['file']} 的 {schema_name} schema 缺少 '{field}' 欄位 —— "
                     f"定義在 {inv['source']} 卻未反映在強制 schema（定義源/schema 源分離 drift）")]
    else:
        if f'"{field}"' not in text:
            return [(inv["id"], "critical", f"{eb['file']} 缺少 '{field}'")]
    return []


def check_classification(inv: dict) -> list[tuple[str, str, str]]:
    """source（如 CLAUDE.md）分類的 commands，本體必須自標受眾。"""
    if inv.get("type") != "classification":
        return []
    must = inv["must_contain_any"]
    out = []
    for cmd in inv.get("commands", []):
        p = REPO_ROOT / cmd
        if not p.exists():
            out.append((inv["id"], "important", f"分類命令不存在: {cmd}"))
            continue
        text = read_text(p)
        if not any(t in text for t in must):
            out.append((inv["id"], "important",
                        f"{cmd} 被 {inv['source']} 分類但本體未自標受眾（需含其一: {must}）"))
    return out


def check_coverage(inv: dict) -> list[tuple[str, str, str]]:
    """source_glob 下每個檔案的 source_field（frontmatter name）必須被 enforced_by 的 extract 覆蓋。

    抓「定義源目錄 ↔ 執行源 allow-list」覆蓋 drift：skills/ 定義 skill name，settings.json
    allow-list 漏了 → 顯式呼叫觸發權限提示（rename 後最常見）。

    單向（定義源 → 執行源）：只抓 missing；不抓 dead entry（執行源有定義源無的）——
    settings 含 commands/built-in/plugin，精確判 dead 需 external allowlist，危害僅 noise，
    且 rename 必伴隨 missing 觸發修復。
    """
    if inv.get("type") != "coverage":
        return []
    src_files = sorted(REPO_ROOT.glob(inv["source_glob"]))
    field_pat = re.compile(rf"^{re.escape(inv['source_field'])}:\s*(.+?)\s*$", re.MULTILINE)
    defined: dict[str, str] = {}
    for f in src_files:
        m = field_pat.search(read_text(f))
        if m:
            defined[m.group(1).strip().strip('"').strip("'")] = rel(f)
    eb = inv["enforced_by"]
    ef = REPO_ROOT / eb["file"]
    if not ef.exists():
        return []  # enforced_by 檔不存在（settings.json 是 local/gitignored）→ skip，不 false positive
    allowed = set(re.findall(eb["extract"], read_text(ef)))
    return [
        (inv["id"], "important",
         f"skill '{name}'（{src}）未在 {eb['file']} allow-list 找到 "
         f"（缺 Skill({name}) — rename 後新名未同步 allow-list？）")
        for name, src in defined.items()
        if name not in allowed
    ]


def check_source_contains(inv: dict) -> list[tuple[str, str, str]]:
    """source 檔必須含 must_contain_any 之一（定義源自身驗證，防 drift 回非預期值）。"""
    if inv.get("type") != "source_contains":
        return []
    src = REPO_ROOT / inv["source"]
    if not src.exists():
        return [(inv["id"], "important", f"source 檔不存在: {inv['source']}")]
    if not any(t in read_text(src) for t in inv["must_contain_any"]):
        return [(inv["id"], "critical",
                 f"{inv['source']} 缺少定義源應含的: {inv['must_contain_any']} —— drift 回非預期值？")]
    return []


def main() -> int:
    findings: list[tuple[str, str, str]] = []
    for inv in INVARIANTS:
        findings += check_enforced_by(inv)
        findings += check_classification(inv)
        findings += check_coverage(inv)
        findings += check_source_contains(inv)

    crit = [f for f in findings if f[1] == "critical"]
    imp = [f for f in findings if f[1] == "important"]

    print(f"=== single-source check（{len(INVARIANTS)} invariants）===")
    print(f"critical: {len(crit)}  important: {len(imp)}")
    print()
    for inv_id, sev, msg in findings:
        print(f"[{sev.upper():9}] {inv_id}: {msg}")
    if not findings:
        print("✅ 所有 single-source invariant 通過")
    return 1 if (crit or imp) else 0


if __name__ == "__main__":
    sys.exit(main())
