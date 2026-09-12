#!/usr/bin/env bash
# muse memory inbox hook — thin launcher (AIR-79 S1; mechanism origin AIR-54).
#
# Intercepts muse memory writes, saves the raw tool_input JSON to the repo
# inbox (atomic temp+rename), and denies with the inbox location — the gate
# semantics live in the shared governance core; consolidation (memory-audit
# skill, nightly wave) applies frontmatter/six-question checks before pool
# entry. Pure mechanical diversion: no semantic decisions here.
#
# This shim is the registered-origin wrapper kept during the migration
# window: it resolves the shared core, then hands over with
# GOVERNANCE_ORIGIN=registered (core diverts unconditionally — identical
# gate semantics to the pre-refactor legacy hook, so pre-marker repos keep
# their gate) and GOVERNANCE_REPO pinned to this repo root (explicit, zero
# stdin/$PWD dependence — EP review F8).
#
# Core resolution order (EP S1 要點3, 09-12 開工修訂):
#   ① $MUSE_MEMORY_GOVERNANCE_HOME (default ~/.local/share/muse-memory-
#      governance) under the `current` symlink -> hooks/muse_memory_governance.sh
#   ② repo-local copy <repo>/muse-plugins/memory-governance/hooks/
#      muse_memory_governance.sh (deployment-window fallback — present in
#      the plugin source home)
#   ③ both unresolvable -> static deny (fail-closed; a naked exec failure
#      would leave muse fail-open, EP review F5)
set -euo pipefail
umask 077

deny() {
  # jq-free deny emission; JSON-string-safe escaping (review R1/C-C2): map
  # \n \r \t to JSON escapes, strip remaining control chars (<0x20).
  local reason=${1//\\/\\\\}
  reason=${reason//\"/\\\"}
  reason=${reason//$'\n'/\\n}
  reason=${reason//$'\r'/\\r}
  reason=${reason//$'\t'/\\t}
  STRIPPED=$(printf '%s' "$reason" | tr -d '\000-\037' 2>/dev/null) && reason=$STRIPPED
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
  exit 0
}

# cd failures under set -e would be a naked exit != 0 -> muse fail-open
# (review R2); deny instead (fail-closed to the launcher layer).
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd) \
  || deny "memory-governance launcher: cannot resolve script directory (fail-closed)"
GOVERNANCE_REPO=$(cd "$SCRIPT_DIR/.." && pwd) \
  || deny "memory-governance launcher: cannot resolve repo root (fail-closed)"
export GOVERNANCE_ORIGIN=registered
export GOVERNANCE_REPO

# Core resolution order (EP S1 要點3, review C-C5/R3 reorder):
#   ① $MUSE_MEMORY_GOVERNANCE_HOME/current — explicit env override
#      (tests / debugging a specific install point)
#   ② repo-local copy <repo>/muse-plugins/memory-governance/hooks/
#      muse_memory_governance.sh — the source home's canonical core; a
#      stale install point must never shadow it
#   ③ default fixed install point ~/.local/share/muse-memory-governance/
#      current (generated launchers in other repos / fallback registration)
#   ④ unresolvable -> static deny (fail-closed; a naked exec failure would
#      leave muse fail-open, EP review F5)
CORE=""
CAND=${MUSE_MEMORY_GOVERNANCE_HOME:-}
if [ -n "$CAND" ]; then
  CAND=$CAND/current/hooks/muse_memory_governance.sh
  if [ -f "$CAND" ] && [ -x "$CAND" ]; then
    CORE=$CAND
  fi
fi
if [ -z "$CORE" ]; then
  CAND=$GOVERNANCE_REPO/muse-plugins/memory-governance/hooks/muse_memory_governance.sh
  if [ -f "$CAND" ] && [ -x "$CAND" ]; then
    CORE=$CAND
  fi
fi
if [ -z "$CORE" ] && [ -n "${HOME:-}" ]; then
  CAND=$HOME/.local/share/muse-memory-governance/current/hooks/muse_memory_governance.sh
  if [ -f "$CAND" ] && [ -x "$CAND" ]; then
    CORE=$CAND
  fi
fi
if [ -z "$CORE" ]; then
  deny "memory-governance launcher: shared core unresolvable (repo-local copy and install point both missing); memory write denied (fail-closed). See muse-plugins/memory-governance/README.md"
fi

if ! "$CORE"; then
  deny "memory-governance launcher: shared core failed (exit != 0); memory write denied (fail-closed)"
fi
exit 0
