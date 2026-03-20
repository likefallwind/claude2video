#!/usr/bin/env bash
# claude2video environment setup
# Installs system dependencies (Cairo, Pango, ffmpeg, LaTeX) and Python packages.
# Usage: bash setup.sh [--no-latex]

set -e

NO_LATEX=false
for arg in "$@"; do
  [[ "$arg" == "--no-latex" ]] && NO_LATEX=true
done

# ── Detect platform ──────────────────────────────────────────────────────────
OS="$(uname -s)"
echo "==> Detected OS: $OS"

install_system_deps() {
  if [[ "$OS" == "Linux" ]]; then
    # Debian / Ubuntu (including WSL2)
    if command -v apt-get &>/dev/null; then
      echo "==> Installing system packages via apt-get..."
      sudo apt-get update -qq
      sudo apt-get install -y \
        libcairo2-dev libpango1.0-dev \
        ffmpeg python3-dev pkg-config \
        build-essential
      if [[ "$NO_LATEX" == false ]]; then
        echo "==> Installing LaTeX (texlive-full, ~800 MB). Pass --no-latex to skip."
        sudo apt-get install -y texlive-full
      fi

    # Fedora / RHEL
    elif command -v dnf &>/dev/null; then
      echo "==> Installing system packages via dnf..."
      sudo dnf install -y \
        cairo-devel pango-devel \
        ffmpeg python3-devel pkgconfig gcc
      if [[ "$NO_LATEX" == false ]]; then
        sudo dnf install -y texlive-scheme-full
      fi

    else
      echo "WARN: Unknown Linux distro — install Cairo, Pango, ffmpeg, and (optionally) LaTeX manually."
    fi

  elif [[ "$OS" == "Darwin" ]]; then
    if ! command -v brew &>/dev/null; then
      echo "ERROR: Homebrew not found. Install it from https://brew.sh and re-run."
      exit 1
    fi
    echo "==> Installing system packages via Homebrew..."
    brew install cairo pango ffmpeg pkg-config
    if [[ "$NO_LATEX" == false ]]; then
      echo "==> Installing MacTeX (~4 GB). Pass --no-latex to skip."
      brew install --cask mactex
    fi

  else
    echo "WARN: Windows detected (non-WSL). Install Cairo, Pango, ffmpeg, and LaTeX manually."
    echo "      See: https://docs.manim.community/en/stable/installation/windows.html"
  fi
}

# ── Python package installer ─────────────────────────────────────────────────
install_python_deps() {
  echo "==> Installing Python packages..."
  if command -v uv &>/dev/null; then
    echo "    (using uv)"
    uv pip install -r requirements.txt
  else
    python3 -m pip install --upgrade pip
    pip3 install -r requirements.txt
  fi
}

# ── Verify ───────────────────────────────────────────────────────────────────
verify() {
  echo ""
  echo "==> Verifying installation..."
  local ok=true

  check() {
    if command -v "$1" &>/dev/null; then
      echo "  [OK] $1 found: $(command -v "$1")"
    else
      echo "  [FAIL] $1 not found"
      ok=false
    fi
  }

  check manim
  check ffmpeg
  check edge-tts
  python3 -c "import manim" 2>/dev/null \
    && echo "  [OK] manim importable" \
    || { echo "  [FAIL] manim not importable"; ok=false; }

  if [[ "$NO_LATEX" == false ]]; then
    check latex
  fi

  echo ""
  if [[ "$ok" == true ]]; then
    echo "All checks passed. Run a quick smoke test:"
    echo "  manim render -ql .agents/skills/claude2video/example_section.py"
  else
    echo "Some checks failed. Review the output above and install missing components."
    exit 1
  fi
}

# ── Main ─────────────────────────────────────────────────────────────────────
install_system_deps
install_python_deps
verify
