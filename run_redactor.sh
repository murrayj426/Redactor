#!/bin/bash
# Portable launcher for the Redactor GUI without Docker.
# Creates/uses a local virtual environment in .venv if not already active.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
	if [[ ! -d .venv ]]; then
		echo "📦 Creating virtual environment (.venv)..."
		python3 -m venv .venv
	fi
	echo "🔧 Activating virtual environment..."
	# shellcheck disable=SC1091
	source .venv/bin/activate
fi

if [[ ! -f requirements.txt ]]; then
	echo "❌ requirements.txt not found in $SCRIPT_DIR" >&2
	exit 1
fi

echo "⬇️  Ensuring dependencies are installed..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "🚀 Launching Streamlit app..."
exec streamlit run gui.py
