#!/bin/bash
# Install assistant_ai_api from GitHub repository

set -e

API_REPO="https://github.com/sunshine-walker-93/assistant_ai_api.git"
INSTALL_DIR="${HOME}/.local/share/assistant_ai_api"

# Detect Python command (use venv python if available)
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="python3"
fi

echo "Cloning/updating assistant_ai_api repository..."
if [ -d "$INSTALL_DIR" ]; then
    echo "Repository exists, updating..."
    cd "$INSTALL_DIR"
    git pull --depth 1 || git fetch --depth 1 && git reset --hard origin/main
else
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --depth 1 "$API_REPO" "$INSTALL_DIR"
fi

PYTHON_DIR="$INSTALL_DIR/python"

if [ ! -d "$PYTHON_DIR" ]; then
    echo "Error: python directory not found in repository"
    exit 1
fi

# Add to Python path by creating a .pth file
SITE_PACKAGES=$($PYTHON_CMD -c "import site; print(site.getsitepackages()[0])")
PTH_FILE="$SITE_PACKAGES/assistant_ai_api.pth"

echo "$PYTHON_DIR" > "$PTH_FILE"
echo "Installed assistant_ai_api to Python path via $PTH_FILE"
echo "Python directory: $PYTHON_DIR"

echo "Installation complete!"

