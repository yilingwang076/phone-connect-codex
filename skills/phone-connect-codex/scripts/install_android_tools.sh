#!/bin/bash
# Install only missing Android mirroring tools on a local Mac.
set -euo pipefail

mode="${1:---check}"
if [[ "$mode" != "--check" && "$mode" != "--install" ]]; then
  echo "Usage: $0 --check|--install" >&2
  exit 2
fi
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS only." >&2
  exit 2
fi

find_brew() {
  if command -v brew >/dev/null 2>&1; then
    command -v brew
  elif [[ -x /opt/homebrew/bin/brew ]]; then
    echo /opt/homebrew/bin/brew
  elif [[ -x /usr/local/bin/brew ]]; then
    echo /usr/local/bin/brew
  fi
}

brew_bin="$(find_brew)"
echo "Homebrew: ${brew_bin:-missing}"
echo "ADB: $(command -v adb || echo missing)"
echo "scrcpy: $(command -v scrcpy || echo missing)"

if [[ "$mode" == "--check" ]]; then
  exit 0
fi
if command -v adb >/dev/null 2>&1 && command -v scrcpy >/dev/null 2>&1; then
  echo "ADB and scrcpy are already installed; nothing to install."
  exit 0
fi

if [[ -z "$brew_bin" ]]; then
  if [[ ! -t 0 ]]; then
    echo "Homebrew installation needs an interactive local terminal." >&2
    exit 2
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "curl is unavailable; cannot download the official Homebrew installer." >&2
    exit 2
  fi
  installer="$(mktemp "${TMPDIR:-/tmp}/homebrew-install.XXXXXX")"
  trap 'rm -f "$installer"' EXIT
  curl --proto '=https' --tlsv1.2 -fsSL \
    https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o "$installer"
  echo "Running the official Homebrew installer; respond to its local prompts."
  /bin/bash "$installer"
  brew_bin="$(find_brew)"
  if [[ -z "$brew_bin" ]]; then
    echo "Homebrew installer finished, but brew was not found in standard locations." >&2
    exit 2
  fi
fi

export PATH="$("$brew_bin" --prefix)/bin:$PATH"
if ! command -v adb >/dev/null 2>&1; then
  "$brew_bin" install --cask android-platform-tools
fi
if ! command -v scrcpy >/dev/null 2>&1; then
  "$brew_bin" install scrcpy
fi
hash -r
if ! command -v adb >/dev/null 2>&1 || ! adb version >/dev/null 2>&1; then
  echo "ADB is still unavailable after installation." >&2
  exit 2
fi
if ! command -v scrcpy >/dev/null 2>&1 || ! scrcpy --version >/dev/null 2>&1; then
  echo "scrcpy is still unavailable after installation." >&2
  exit 2
fi
echo "Verified ADB: $(command -v adb)"
echo "Verified scrcpy: $(command -v scrcpy)"
