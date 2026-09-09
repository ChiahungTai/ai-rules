#!/usr/bin/env bash
# muse memory inbox hook (AIR-54 S3): PreToolUse gate for add_memory/edit_memory.
#
# Intercepts muse memory writes, saves the raw tool_input JSON to the inbox
# (atomic temp+rename), and denies with the inbox location — consolidation
# (memory-audit skill, nightly wave) applies frontmatter/six-question checks
# before pool entry. Pure mechanical diversion: no semantic decisions here.
#
# Contract (09-09 experiments, .agent-tmp/muse-hooks-findings.md):
# - stdin: {"tool_name": "...", "tool_input": {scope, path, content}}
# - deny via CC-style hookSpecificOutput; reason is non-empty (required).
# - muse is fail-open on hook failure (exit != 0 or bad schema -> tool runs):
#   keep this script minimal and dependency-light (bash + coreutils + jq).
# - For edit_memory payloads with an existing pool target, attach
#   _inbox_meta.base_sha256 so consolidation can do CAS (delayed lost update).
# - File name = timestamp + pid + content hash (no model-supplied basename).
set -euo pipefail
umask 077

REPO=$(cd "$(dirname "$0")/.." && pwd)
INBOX="$REPO/.agents/memory-inbox"

IN=$(cat)
[ -n "$IN" ] || exit 0   # empty stdin: nothing to divert (no landing, no deny)
TS=$(date +%Y%m%d-%H%M%S)
SUM=$(printf '%s' "$IN" | shasum -a 256 | cut -c1-12)
OUT="$INBOX/${TS}-$$-${SUM}.json"
TMP="$INBOX/.tmp-${TS}-$$-${SUM}"
mkdir -p "$INBOX"

PAYLOAD="$IN"
# jq parse failure must NOT kill the script (set -e) — that turns the whole
# diversion fail-open (muse would write straight into the pool). P falls
# back to empty -> no-enrichment path -> deny+land still happens (review F1).
P=$(printf '%s' "$IN" | jq -r '.tool_input.path // empty' 2>/dev/null || true)
# T3-1 lexical gate: P is unverified model input — never dereference it
# before this gate. Absolute / parent-escape / backslash / non-.md /
# symlink targets skip CAS enrichment (deny+land still happens below,
# so the gate itself stays fail-open for the diversion function).
SAFE_P=""
case "$P" in
  *.md)
    # T4-2: consolidation 只收池根 basename（generator/watch-seed 只看頂層）——
    # 含 slash 的子目錄請求跳過 enrichment（deny+land 照走，合約端明確 rejected）。
    # absolute/slash 已覆蓋全部 escape 面；`..` 與 `\` 在無 slash 時是合法 basename
    # 字元、無路徑語義（review F3——誤傷 `note..md` 類既有條目的 CAS）。
    case "$P" in /*|*/*) : ;; *) SAFE_P="$P" ;; esac
    ;;
esac
# 單段 basename 無 intermediate component——T3-1b 的逐段 walk 已被 slash 規則取代；
# 尾段 symlink（foo.md -> 站外）仍由 [ ! -L ] 擋。
if [ -n "$SAFE_P" ] \
  && [ -f "$REPO/.agents/memory/$SAFE_P" ] \
  && [ ! -L "$REPO/.agents/memory/$SAFE_P" ]; then
  H=$(shasum -a 256 "$REPO/.agents/memory/$SAFE_P" | cut -d' ' -f1)
  PAYLOAD=$(jq -c --arg p "$SAFE_P" --arg h "$H" \
    '. + {_inbox_meta:{base_path:$p, base_sha256:$h}}' <<<"$IN")
fi

printf '%s' "$PAYLOAD" > "$TMP" && mv "$TMP" "$OUT"

jq -nc --arg p "$OUT" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:("已代存 inbox: "+$p+"（consolidation 站將處理入池）")}}'
