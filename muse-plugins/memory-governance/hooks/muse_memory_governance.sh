#!/usr/bin/env bash
# muse memory governance hook (AIR-79 S1; divert semantics origin AIR-54).
# Shared core for the muse-memory-governance plugin: PreToolUse gate for
# add_memory/edit_memory with per-repo marker three-state opt-in.
#
# Contract (09-09 experiments, AIR-54; unchanged):
# - stdin: {"tool_name": "...", "tool_input": {scope, path, content}}
# - deny via CC-style hookSpecificOutput; allow = silent exit 0.
# - Deny emission is jq-free (printf template + minimal escaping) so a
#   degraded jq still yields a legal deny schema (EP review C3).
#
# Origins (EP S1 要點2/3):
# - plugin origin (no governance env): resolve repo per call
#   (GOVERNANCE_REPO > stdin workspace field [provisional seam, S2 P-WS
#   freezes] > git $PWD upward), structured legacy-owner surrender, marker
#   three-state, inbox containment check, fail-closed divert.
# - registered origin (thin launcher sets GOVERNANCE_ORIGIN=registered +
#   GOVERNANCE_REPO=<repo root>): skips repo resolution / legacy-owner /
#   marker — the registered gate diverts unconditionally, gate semantics
#   identical to the pre-refactor legacy hook (migration-window contract:
#   pre-marker repos must not silently lose the gate, EP review C1).
#
# Decision order (EP pseudo code skeleton; each step exits early):
#   empty stdin -> crude self-filter -> jq availability -> precise
#   tool_name filter -> repo resolve -> legacy-owner surrender (plugin
#   origin) -> marker three-state (plugin origin) -> inbox symlink
#   containment (all origins) -> divert (atomic, CAS lexical gates,
#   fail-closed) -> deny with inbox path.
set -euo pipefail
umask 077

deny() {
  # jq-free deny emission; minimal JSON escaping for reason strings.
  local reason=${1//\\/\\\\}
  reason=${reason//\"/\\\"}
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
  exit 0
}

deny_degraded() {
  deny "memory-governance tooling degraded: jq unavailable or unusable, cannot evaluate the repo governance state; conservatively denying the memory write (fail-closed). Install jq (e.g. 'brew install jq') and retry."
}

IN=$(cat)
[ -n "$IN" ] || exit 0   # SM-13 empty stdin: nothing to divert

# Self-filter, fast path: crude bash string match on memory-tool features
# (superset — plugin hooks have no matcher; the precise check below needs jq).
case "$IN" in
  *add_memory*|*edit_memory*) : ;;
  *) exit 0 ;;
esac

# jq availability: without jq we cannot parse tool_name or the marker, so
# the opt-out state is unevaluable -> conservative deny (EP ⑦ taxonomy).
command -v jq >/dev/null 2>&1 || deny_degraded

# Precise self-filter: a crude hit may be innocent text mentioning the tool
# names; only actual memory tools are gated (EP ①: tool_name not in
# {add_memory, edit_memory} -> exit 0). jq failing here is the same
# "cannot parse tool_name" degraded family as above.
TOOL=$(printf '%s' "$IN" | jq -r '.tool_name // empty' 2>/dev/null) || deny_degraded
case "$TOOL" in
  add_memory|edit_memory) : ;;
  *) exit 0 ;;
esac

# Repo resolution: env (launcher/fallback injection) > stdin host workspace
# field (candidate order is a provisional seam — S2 P-WS freezes it;
# absence tolerated) > git rev-parse upward from $PWD.
REPO=""
if [ -n "${GOVERNANCE_REPO:-}" ]; then
  REPO=$GOVERNANCE_REPO
else
  REPO=$(printf '%s' "$IN" | jq -r '.workspace // .cwd // .host_workspace // empty' 2>/dev/null || true)
fi
if [ -z "$REPO" ]; then
  # git-binary-missing vs explicit not-a-repo are distinct branches (EP ⑦):
  # both allow native, but tests pin each arrival path separately.
  if ! command -v git >/dev/null 2>&1; then
    exit 0   # git binary missing: repo unresolvable, marker unobservable
  fi
  REPO=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0   # SM-11 not a repo
fi

# Legacy coexistence (plugin origin only, EP ④): a WORKING legacy owner
# keeps full authority (SM-5). Structured criteria — all four must hold:
# hooks.json parses; a PreToolUse entry's matcher covers add_memory AND
# edit_memory; the command file exists and is executable; its realpath
# differs from this script (self-exclusion — own registration must not
# no-op itself, EP review C1). Malformed/stale/wrong/partial -> keep gating.
if [ "${GOVERNANCE_ORIGIN:-}" != registered ]; then
  SELF_REAL=$(realpath "$0" 2>/dev/null) || SELF_REAL=$0
  OWNER_CMDS=$(jq -r '
    .hooks.PreToolUse[]?
    | select(((.matcher // "") | test("add_memory")) and ((.matcher // "") | test("edit_memory")))
    | .hooks[]?.command // empty
  ' "$REPO/.muse/hooks.json" 2>/dev/null) || OWNER_CMDS=""
  SURRENDER=0
  while IFS= read -r CMD; do
    [ -n "$CMD" ] || continue
    if [ -f "$CMD" ] && [ -x "$CMD" ]; then
      CMD_REAL=$(realpath "$CMD" 2>/dev/null) || CMD_REAL=""
      if [ -n "$CMD_REAL" ] && [ "$CMD_REAL" != "$SELF_REAL" ]; then
        SURRENDER=1
        break
      fi
    fi
  done <<<"$OWNER_CMDS"
  if [ "$SURRENDER" = 1 ]; then
    exit 0
  fi
fi

# Marker three-state (plugin origin; registered origin diverts
# unconditionally per the migration-window contract, EP S1 要點3).
# jq numeric equality reads 1.0 as 1 — JSON has a single number type.
if [ "${GOVERNANCE_ORIGIN:-}" != registered ]; then
  MARKER=$REPO/.agents/memory-governance.json
  if [ ! -e "$MARKER" ] && [ ! -L "$MARKER" ]; then
    exit 0   # SM-2 absent: allow native (determined non-governed)
  fi
  # Integer 1 is the only valid protocol; everything else (parse failure,
  # missing field, 0, -1, "1", null, true, false, >1) denies without
  # landing — a declared governance state must not fail open (SM-3/SM-4).
  if ! jq -e '.protocol == 1' "$MARKER" >/dev/null 2>&1; then
    deny "memory-governance marker malformed/unsupported: $MARKER (protocol must be integer 1)"
  fi
fi

# Inbox containment (all origins, A7): lstat each path segment — any
# existing symlink component denies without landing (SM-12); ENOENT
# segments are safe (the hook creates them below).
for SEG in "$REPO" "$REPO/.agents" "$REPO/.agents/memory-inbox"; do
  if [ -L "$SEG" ]; then
    deny "memory-governance: inbox path fails symlink/containment check: $SEG"
  fi
done

# Divert — legacy-equivalent semantics (AIR-54): atomic tmp+rename,
# filename = timestamp + pid + content hash (no model-supplied basename),
# CAS enrichment behind the T3-1/T4-2 lexical gates. Every internal
# failure denies (fail-closed, EP ⑦ — muse itself is fail-open).
TS=$(date +%Y%m%d-%H%M%S) || deny "memory-governance: divert failed (governed repo fail-closed): timestamp unavailable"
INBOX=$REPO/.agents/memory-inbox
SUM=$(printf '%s' "$IN" | shasum -a 256 | cut -c1-12) || deny "memory-governance: divert failed (governed repo fail-closed): checksum unavailable"
OUT=$INBOX/${TS}-$$-${SUM}.json
TMP=$INBOX/.tmp-${TS}-$$-${SUM}
mkdir -p "$INBOX" || deny "memory-governance: divert failed (governed repo fail-closed): cannot create $INBOX"

PAYLOAD=$IN
# jq parse failure must NOT kill the script (set -e) — P falls back to
# empty -> no-enrichment path -> deny+land still happens (AIR-54 review F1).
P=$(printf '%s' "$IN" | jq -r '.tool_input.path // empty' 2>/dev/null || true)
# T3-1 lexical gate: P is unverified model input — never dereference it
# before this gate. T4-2: consolidation only takes pool-root basenames,
# so any P with a slash (absolute or nested) skips enrichment; trailing
# symlink targets are excluded by the [ ! -L ] check below.
SAFE_P=""
case "$P" in
  *.md)
    case "$P" in /*|*/*) : ;; *) SAFE_P=$P ;; esac
    ;;
esac
if [ -n "$SAFE_P" ] \
  && [ -f "$REPO/.agents/memory/$SAFE_P" ] \
  && [ ! -L "$REPO/.agents/memory/$SAFE_P" ]; then
  H=$(shasum -a 256 "$REPO/.agents/memory/$SAFE_P" 2>/dev/null | cut -d' ' -f1) || H=""
  if [ -n "$H" ]; then
    PAYLOAD=$(jq -c --arg p "$SAFE_P" --arg h "$H" \
      '. + {_inbox_meta:{base_path:$p, base_sha256:$h}}' <<<"$IN" 2>/dev/null) || PAYLOAD=$IN
  fi
fi

if ! printf '%s' "$PAYLOAD" > "$TMP" 2>/dev/null; then
  rm -f "$TMP" 2>/dev/null || true
  deny "memory-governance: divert failed (governed repo fail-closed): cannot write $TMP"
fi
if ! mv -f "$TMP" "$OUT" 2>/dev/null; then
  rm -f "$TMP" 2>/dev/null || true
  deny "memory-governance: divert failed (governed repo fail-closed): cannot finalize $OUT"
fi

deny "已代存 inbox: ${OUT}（consolidation 站將處理入池）"
