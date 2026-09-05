#!/usr/bin/env python3
r"""
PreToolUse hook（matcher Edit|Write|NotebookEdit）: memory 寫入治理（兩層）。

① MEMORY.md 手寫攔截——索引是 _generate_index.py 的機械投影（條目檔
   frontmatter = 單一寫入點），手寫必漂移：索引載入＝200 行或 25,000 字元
   先到為準，超限截斷（附 WARNING，尾端條目不載）→ cluster 查重漏同主題
   → 近重複寫入正回授（2026-08-30 mosaic 56.6KB 實證）。
② 條目檔寫入檢查（2026-09-01 寫入治理）——對應 rules/context-management.md
   寫入五問 Q1/Q2/Q4：
   - frontmatter description >100 chars → 擋（索引行原料＝寫入紀律值，
     name×2 重複已佔索引行 40% 開銷，desc 是主要槓桿）
   - desc 含 commit hash 形態（`\bcommit[s]?\s+(?=[0-9a-fA-F]*[0-9])[0-9a-fA-F]{7,}`，
     09-05 S2/AIR-25＋同日 digit-lookahead 補強）→ 擋：
     hash 屬 git log 可推導（官方 skip-derivable），desc＝觸發詞＋一句鉤子。
     邊界：\b 擋 "recommit" 誤傷；複數/大寫 hex 涵蓋；digit-lookahead 排除
     「commit feedback/facade/defaced」類純字母 hex 偽陽性（mosaic 實戰案例）；
     只查 desc 不查 body（body 引 hash 是歷史合法引用，另有 12K 膨脹治理）。
   - 條目檔膨脹 >12,000 chars → 擋（Write 看 content 全長；Edit 只擋
     「變大且超限」方向——收斂型編輯放行，不卡 audit 收縮既有肥檔）。
     超額內容多屬 repo 可推導（EP 進度/git log），該住 EP 檔而非 memory。
Self-gating：同目錄無 _generate_index.py 的專案不攔（裝 script 即 opt-in）。
對應 rule: rules/context-management.md「Memory 生命周期規範」。
覆蓋邊界：僅攔 Edit/Write 工具面的 file_path——Bash redirect（echo >>/tee）不攔
（紀律面處理）；**subagent 寫入不觸發本 hook**（ZCode 實證 2026-09-01：subagent
Write 16,154 chars 落地無攔）——治理範圍＝主 session，寫入型 subagent（如
mem-distill）的上限是 prompt 紀律非機械強制。ZCode 端 exit 2 產生 deny 已證
（官方文檔）；stderr 指引送達模型未證（EP A3 deferred）——失敗跡象＝無解釋重試，
回滾按 memory-hooks-rollback.md。
hook crash（非 0 非 2 exit）為非阻斷，工具仍執行。
hook runtime python 3.9——禁 3.10+ 語法。
desc 量測近似已知形態（品質洞非完整性洞，不修）：YAML folded scalar（`>-`——
量到摺疊符號本身，超長 desc 放行；generator flat-parse 同不展開，索引不膨脹）；
`description :`（冒號前空格——Edit 偵測 startswith 漏，generator k.strip() 讀得到）。
Write 收斂豁免：content 比既有檔短即放行（與 Edit delta 豁免對稱——部分收斂
結果仍 >12K 但方向正確，不擋）。
"""

import json
import re
import sys
from pathlib import Path

GENERATOR_NAME = "_generate_index.py"
DESC_LIMIT = 100  # frontmatter description 硬上限（＝寫入紀律值；09-03 P1 對齊）
BODY_LIMIT = 12_000  # 條目檔總長上限（chars）
NEW_ENTRY_LIMIT = 3_000  # 新建條目上限——寫入當下即蒸後形（cur=0 時 12K 膨脹治理無約束力，此閘補真空）
HASH_RE = re.compile(
    r"\bcommit[s]?\s+(?=[0-9a-fA-F]*[0-9])[0-9a-fA-F]{7,}"
)  # desc 禁 commit hash（09-05 S2；digit-lookdown 排除純字母 hex 形態——實戰偽陽性「commit feedback」〔feedbac 恰 7 hex〕，真 hash 7+ 碼全字母機率≈0.01%）


def is_index_violation(file_path: str, has_generator: bool) -> bool:
    """寫入目標名為 MEMORY.md，且同目錄裝有 generator（opt-in 條件）。"""
    return Path(file_path).name == "MEMORY.md" and has_generator


def is_entry_file(file_path: str, has_generator: bool) -> bool:
    """寫入目標是治理池內的條目檔（.md、非 MEMORY.md、非底線系統檔）。"""
    p = Path(file_path)
    return (
        has_generator
        and p.suffix == ".md"
        and p.name != "MEMORY.md"
        and not p.name.startswith("_")
    )


def extract_desc(text: str) -> str:
    """從 Write content 抽 frontmatter description 值（單行值＋縮排續行近似）。"""
    lines = text.splitlines()
    in_fm = False
    for i, line in enumerate(lines):
        if line.strip() == "---" and not in_fm:
            in_fm = True
            continue
        if in_fm and line.strip() == "---":
            break
        if in_fm and line.startswith("description:"):
            val = line.partition(":")[2].strip().strip("'\"")
            j = i + 1
            while (
                not val
                and j < len(lines)
                and (lines[j].startswith(" ") or lines[j].startswith("\t"))
            ):
                val += lines[j].strip().strip("'\"")
                j += 1
            return val
    return ""


def desc_from_edit(new_string: str) -> str:
    """Edit 的 new_string 含 description: 行時，回傳該（新）值；否則空字串。"""
    for line in new_string.splitlines():
        if line.startswith("description:"):
            return line.partition(":")[2].strip().strip("'\"")
    return ""


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"[block-memory-index-write] stdin parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)
    gen = Path(file_path).parent / GENERATOR_NAME
    has_generator = gen.exists()

    # ① 索引手寫攔截（原有行為，不變）
    if is_index_violation(file_path, has_generator):
        print(
            "[Hook Blocked] MEMORY.md 是 generator 投影，禁手寫。\n"
            "原因：索引由條目檔 frontmatter 機械投影；手寫必漂移"
            "（載入截斷 → 查重漏 → 近重複寫入）。\n"
            "修正方式：改條目檔（frontmatter name/description/type）後執行:\n"
            f"  python3 {gen}（Stop hook 也會自動重生成）",
            file=sys.stderr,
        )
        sys.exit(2)

    # ② 條目檔寫入檢查（寫入治理）
    if not is_entry_file(file_path, has_generator):
        sys.exit(0)
    target = Path(file_path)
    if tool == "Write":
        content = tool_input.get("content", "") or ""
        desc = extract_desc(content)
        if len(desc) > DESC_LIMIT:
            print(
                f"[Hook Blocked] 條目 description {len(desc)} chars > {DESC_LIMIT}。\n"
                "description 是索引行的投影原料（索引行 = name×2 重複 + desc，desc 佔一半 chars）。\n"
                "修正方式：精簡到主題＋一個鉤子（紀律 ≤100 chars），細節寫進 body。",
                file=sys.stderr,
            )
            sys.exit(2)
        if HASH_RE.search(desc):
            print(
                "[Hook Blocked] 條目 description 含 commit hash——desc＝觸發詞＋一句鉤子。\n"
                "hash 屬 git log 可推導（官方 skip-derivable），不進索引行。\n"
                "修正方式：desc 去掉 hash（收案錨點留 body 或指向 repo 檔案）。",
                file=sys.stderr,
            )
            sys.exit(2)
        cur = len(target.read_text(encoding="utf-8")) if target.exists() else 0
        if cur == 0 and len(content) > NEW_ENTRY_LIMIT:
            print(
                f"[Hook Blocked] 新建條目 {len(content):,} chars > {NEW_ENTRY_LIMIT:,}——寫入當下就該是蒸後形。\n"
                "新條目直寫敘事流水（timeline 過程/commit 清單/findings 計數）是池膨脹主入口——\n"
                "超額內容住 EP/卡/repo，不是「先寫再等 audit 壓」（09-06 user 拍板）。\n"
                "修正方式：lesson-first 一行一事實（教訓＋實證錨一行），壓縮後重寫；\n"
                "既有條目覆寫（cluster merge 收斂）不受此閘，走 12K 膨脹治理。",
                file=sys.stderr,
            )
            sys.exit(2)
        if len(content) > BODY_LIMIT and len(content) >= cur:
            print(
                f"[Hook Blocked] 條目檔 {len(content):,} chars > {BODY_LIMIT:,}。\n"
                "超大條目多屬 repo 可推導內容（EP 進度/git log/弧線流水）——該住 EP 檔，memory 收教訓。\n"
                "修正方式：只留決策與教訓（收案後一次性蒸餾），現況細節回 EP 檔。",
                file=sys.stderr,
            )
            sys.exit(2)
    elif tool == "Edit":
        new_string = tool_input.get("new_string", "") or ""
        old_string = tool_input.get("old_string", "") or ""
        desc = desc_from_edit(new_string)
        if len(desc) > DESC_LIMIT:
            print(
                f"[Hook Blocked] 新 description {len(desc)} chars > {DESC_LIMIT}。\n"
                "修正方式：精簡到主題＋一個鉤子（紀律 ≤100 chars），細節寫進 body。",
                file=sys.stderr,
            )
            sys.exit(2)
        if desc and HASH_RE.search(desc):
            print(
                "[Hook Blocked] 新 description 含 commit hash——desc＝觸發詞＋一句鉤子，\n"
                "hash 屬 git log 可推導。修正方式：desc 去掉 hash。",
                file=sys.stderr,
            )
            sys.exit(2)
        cur_text = target.read_text(encoding="utf-8") if target.exists() else ""
        # replace_all 置換全部 occurrences——膨脹 = 單次 delta × 出現次數（old 空時 count 無意義退單次）
        occurrences = (
            cur_text.count(old_string)
            if tool_input.get("replace_all") and old_string
            else 1
        )
        delta = (len(new_string) - len(old_string)) * occurrences
        if delta > 0 and len(cur_text) + delta > BODY_LIMIT:
            print(
                f"[Hook Blocked] 條目檔將膨脹到 {len(cur_text) + delta:,} chars > {BODY_LIMIT:,}。\n"
                "膨脹主因＝進行中弧線每 session 追加（實證：單檔 98 次 Edit 養到 84KB）。\n"
                "修正方式：弧線進度住 EP 檔；此檔收案後一次性蒸餾。收斂方向（縮小）的編輯不受限。",
                file=sys.stderr,
            )
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
