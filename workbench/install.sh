#!/usr/bin/env bash
# One-step setup for the local agent workbench on Linux (Ubuntu, Omarchy) and macOS.
#   1. Checks Python 3.10+.
#   2. Installs the workbench and its optional helpers for the current user.
#   3. Checks for Ollama; asks before running the official install script if it is missing.
#   4. Pulls the recommended local model(s) for the chosen task profile.
#   5. Sets up the bundled skills and runs the doctor.
# Nothing is sent to a cloud provider. Cloud keys stay optional (python3 -m lawb keys set ...).
#
# Usage: ./install.sh [--profile coding|math|literature|general|all|none] [--cloud] [--dry-run]
set -euo pipefail

PROFILE="coding"
CLOUD=0
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --cloud) CLOUD=1; shift ;;
    --dry-run) DRY=1; shift ;;
    *) echo "unknown option: $1"; exit 2 ;;
  esac
done
case "$PROFILE" in coding|math|literature|general|all|none) ;; *) echo "bad --profile: $PROFILE"; exit 2 ;; esac

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step() { printf '\n==> %s\n' "$1"; }
run() { echo "    $*"; if [ "$DRY" -eq 0 ]; then "$@"; fi; }

step "Checking Python 3.10 or later"
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "Python 3.10+ not found. Install it with your package manager and re-run."; exit 1; }
echo "    using $PY ($("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])'))"

step "Installing the workbench and helpers for the current user"
run "$PY" -m pip install --user --upgrade "$ROOT" pymupdf pypdf keyring
[ "$CLOUD" -eq 1 ] && run "$PY" -m pip install --user --upgrade anthropic openai

if [ "$PROFILE" != "none" ]; then
  step "Checking Ollama (local model server)"
  if ! command -v ollama >/dev/null 2>&1; then
    answer="n"
    [ "$DRY" -eq 0 ] && read -r -p "Ollama is not installed. Run the official installer from ollama.com now? [y/N] " answer
    if [[ "$answer" =~ ^[Yy] ]]; then
      run sh -c "curl -fsSL https://ollama.com/install.sh | sh"
    else
      echo "    Skipped. Install Ollama from https://ollama.com/download, then run: $PY -m lawb models install --task $PROFILE"
    fi
  fi
  if command -v ollama >/dev/null 2>&1; then
    step "Pulling the recommended model(s) for: $PROFILE"
    if [ "$DRY" -eq 1 ]; then "$PY" -m lawb models install --task "$PROFILE" --dry-run; else "$PY" -m lawb models install --task "$PROFILE"; fi
  fi
fi

step "Setting up the bundled skills"
run "$PY" -m lawb setup

step "Checking the environment"
"$PY" -m lawb doctor || true

printf '\nDone. Try: %s -m lawb skills list    and    %s -m lawb models recommend\n' "$PY" "$PY"
