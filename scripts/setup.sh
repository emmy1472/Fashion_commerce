#!/usr/bin/env bash
# Bash setup script for the project.
# Creates a virtual environment named env1, activates it, and installs pinned requirements.
# Usage: ./scripts/setup.sh [--dev]

set -euo pipefail

INSTALL_DEV=false
if [ "${1-}" = "--dev" ]; then
  INSTALL_DEV=true
fi

if ! command -v python >/dev/null 2>&1; then
  echo "Python not found in PATH. Install Python 3.11+ and retry."
  exit 1
fi

VENV_DIR=env1
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment '$VENV_DIR'..."
  python -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if [ "$INSTALL_DEV" = true ]; then
  if [ -f requirements-dev.txt ]; then
    python -m pip install -r requirements-dev.txt
  else
    echo "requirements-dev.txt not found; skipping dev deps"
  fi
fi

echo "Setup complete. To activate the venv in future: source env1/bin/activate"
echo "To run tests: python socialcom/manage.py test -v 2"
