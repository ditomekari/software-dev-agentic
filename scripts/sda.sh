#!/usr/bin/env bash
# sda.sh — CLI entry point for software-dev-agentic setup and sync.
#
# Usage:
#   scripts/sda.sh                               # interactive menu
#   scripts/sda.sh setup --platform=ios          # first-time Claude Code wiring
#   scripts/sda.sh sync                          # pull latest from main
#   scripts/sda.sh add-ai --ai=copilot --platform=ios
#   scripts/sda.sh remove-ai --ai=gemini

set -euo pipefail

SCRIPTS="$(cd "$(dirname "$0")" && pwd)"

# ── Helpers ───────────────────────────────────────────────────────────────────

bold()  { printf '\033[1m%s\033[0m' "$*"; }
dim()   { printf '\033[2m%s\033[0m' "$*"; }

print_header() {
  echo ""
  echo "$(bold 'software-dev-agentic')"
  echo "$(dim '─────────────────────')"
  echo ""
}

ask_ai() {
  echo "  AI assistant:"
  echo "    1) copilot  — GitHub Copilot (.github/copilot-instructions.md)"
  echo "    2) gemini   — Gemini CLI (GEMINI.md)"
  echo ""
  printf "  Choice: "
  read -r choice
  case "$choice" in
    1|copilot) AI="copilot" ;;
    2|gemini)  AI="gemini"  ;;
    *) AI="$choice" ;;
  esac
  echo ""
}

ask_platform() {
  echo "  Platform:"
  echo "    1) ios"
  echo "    2) web"
  echo "    3) flutter"
  echo "    4) flutter-qontak"
  echo "    5) other"
  echo ""
  printf "  Choice: "
  read -r choice
  case "$choice" in
    1) PLATFORM="ios" ;;
    2) PLATFORM="web" ;;
    3) PLATFORM="flutter" ;;
    4) PLATFORM="flutter-qontak" ;;
    5)
      printf "  Platform name: "
      read -r PLATFORM
      ;;
    *) PLATFORM="$choice" ;;
  esac
  echo ""
}

# ── Parse command + passthrough args ─────────────────────────────────────────

COMMAND=""
PASSTHROUGH=()

for arg in "$@"; do
  case "$arg" in
    setup|sync|add-ai|remove-ai) COMMAND="$arg" ;;
    *) PASSTHROUGH+=("$arg") ;;
  esac
done

# ── Interactive menu (no command given) ───────────────────────────────────────

if [ -z "$COMMAND" ]; then
  print_header
  echo "  What do you want to do?"
  echo ""
  echo "    1) $(bold Setup)      — first-time Claude Code wiring into a project"
  echo "    2) $(bold Sync)       — pull latest from main"
  echo "    3) $(bold Add AI)     — set up Copilot or Gemini alongside Claude"
  echo "    4) $(bold Remove AI)  — clean up a Copilot or Gemini config"
  echo ""
  printf "  Choice [1-4]: "
  read -r choice
  echo ""
  case "$choice" in
    1|setup)     COMMAND="setup"     ;;
    2|sync)      COMMAND="sync"      ;;
    3|add-ai)    COMMAND="add-ai"    ;;
    4|remove-ai) COMMAND="remove-ai" ;;
    *)
      echo "Invalid choice. Exiting."
      exit 1
      ;;
  esac
fi

# ── Detect platform and ai from passthrough args ──────────────────────────────

PLATFORM=""
AI=""
for arg in "${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}"; do
  case "$arg" in
    --platform=*) PLATFORM="${arg#--platform=}" ;;
    --ai=*)       AI="${arg#--ai=}" ;;
  esac
done

# ── Run ───────────────────────────────────────────────────────────────────────

case "$COMMAND" in
  setup)
    if [ -z "$PLATFORM" ]; then
      ask_platform
      PASSTHROUGH+=("--platform=$PLATFORM")
    fi
    exec "$SCRIPTS/setup-symlinks.sh" "${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}"
    ;;
  sync)
    if [ -z "$PLATFORM" ]; then
      ask_platform
      PASSTHROUGH+=("--platform=$PLATFORM")
    fi
    exec "$SCRIPTS/sync.sh" "${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}"
    ;;
  add-ai)
    if [ -z "$AI" ]; then
      ask_ai
      PASSTHROUGH+=("--ai=$AI")
    fi
    if [ -z "$PLATFORM" ]; then
      ask_platform
      PASSTHROUGH+=("--platform=$PLATFORM")
    fi
    exec "$SCRIPTS/setup-ai.sh" "${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}"
    ;;
  remove-ai)
    if [ -z "$AI" ]; then
      ask_ai
      PASSTHROUGH+=("--ai=$AI")
    fi
    exec "$SCRIPTS/clean-ai.sh" "${PASSTHROUGH[@]+"${PASSTHROUGH[@]}"}"
    ;;
  *)
    echo "Unknown command: $COMMAND"
    echo "Usage: $0 [setup|sync|add-ai|remove-ai]"
    exit 1
    ;;
esac
