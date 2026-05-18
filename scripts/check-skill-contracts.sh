#!/usr/bin/env bash
# check-skill-contracts.sh
# Verifies that each platform implements all Required contract skills.
# Exits non-zero if any gaps are found — safe to run in CI.
#
# Usage:
#   software-dev-agentic/scripts/check-skill-contracts.sh
#   software-dev-agentic/scripts/check-skill-contracts.sh --platform=flutter

set -euo pipefail

SUBMODULE="$(cd "$(dirname "$0")/.." && pwd)"
CONTRACT_DIR="$SUBMODULE/docs/contract"
PLATFORMS_DIR="$SUBMODULE/lib/platforms"

PLATFORM=""
for arg in "$@"; do
  case "$arg" in
    --platform=*) PLATFORM="${arg#--platform=}" ;;
  esac
done

# ── Collect Required skills from all *-skill-contract.md files ────────────────

required_skills=()
while IFS= read -r skill; do
  [[ -n "$skill" ]] && required_skills+=("$skill")
done < <(grep -h '| Yes' "$CONTRACT_DIR"/*-skill-contract.md | awk -F'`' '{print $2}')

if [[ ${#required_skills[@]} -eq 0 ]]; then
  echo "No required skills found in $CONTRACT_DIR — check contract files."
  exit 1
fi

# ── Determine platforms to check ──────────────────────────────────────────────

platforms=()
if [[ -n "$PLATFORM" ]]; then
  if [[ ! -d "$PLATFORMS_DIR/$PLATFORM" ]]; then
    echo "Error: platform '$PLATFORM' not found at $PLATFORMS_DIR/$PLATFORM"
    exit 1
  fi
  platforms=("$PLATFORM")
else
  while IFS= read -r p; do
    platforms+=("$p")
  done < <(ls "$PLATFORMS_DIR")
fi

# ── Check each platform ───────────────────────────────────────────────────────

pass=0
fail=0

for platform in "${platforms[@]}"; do
  contract_dir="$PLATFORMS_DIR/$platform/skills/contract"
  gaps=()
  for skill in "${required_skills[@]}"; do
    [[ ! -d "$contract_dir/$skill" ]] && gaps+=("$skill")
  done

  if [[ ${#gaps[@]} -eq 0 ]]; then
    echo "✓  $platform"
    pass=$((pass + 1))
  else
    echo "✗  $platform — ${#gaps[@]} missing:"
    for gap in "${gaps[@]}"; do
      echo "     - $gap"
    done
    fail=$((fail + 1))
  fi
done

echo ""
echo "$pass passed · $fail failed · ${#required_skills[@]} required skills"
[[ $fail -eq 0 ]]
