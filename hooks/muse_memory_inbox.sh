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
  local reason=${1//\\/\\\\}
  reason=${reason//\"/\\\"}
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
  exit 0
}

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
GOVERNANCE_REPO=$(cd "$SCRIPT_DIR/.." && pwd)
export GOVERNANCE_ORIGIN=registered
export GOVERNANCE_REPO

DEFAULT_HOME=${HOME:-}
CORE=""
INSTALL_ROOT=${MUSE_MEMORY_GOVERNANCE_HOME:-}
if [ -z "$INSTALL_ROOT" ] && [ -n "$DEFAULT_HOME" ]; then
  INSTALL_ROOT=$DEFAULT_HOME/.local/share/muse-memory-governance
fi
if [ -n "$INSTALL_ROOT" ]; then
  CAND=$INSTALL_ROOT/current/hooks/muse_memory_governance.sh
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
if [ -z "$CORE" ]; then
  deny "memory-governance launcher: shared core unresolvable (install point and repo-local copy both missing); memory write denied (fail-closed). See muse-plugins/memory-governance/README.md"
fi

if ! "$CORE"; then
  deny "memory-governance launcher: shared core failed (exit != 0); memory write denied (fail-closed)"
fi
exit 0
