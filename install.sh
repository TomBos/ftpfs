#!/bin/bash

set -e

REPO_URL="https://github.com/TomBos/FTPFS"
INSTALL_DIR="$HOME/.local/share/FTPFS"
BIN_DIR="$HOME/.local/bin"
WRAPPER="$BIN_DIR/FTPFS"
TMP_DIR=$(mktemp -d)

echo "[*] Downloading FTPFS from $REPO_URL..."
git clone --depth=1 "$REPO_URL" "$TMP_DIR" >/dev/null 2>&1

echo "[*] Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$TMP_DIR/src/"* "$INSTALL_DIR"

echo "[*] Creating wrapper at $WRAPPER..."
mkdir -p "$BIN_DIR"

cat > "$WRAPPER" <<EOF
#!/bin/bash
python3 "$INSTALL_DIR/FTPFS.py" "\$@"
EOF

chmod +x "$WRAPPER"
rm -rf "$TMP_DIR"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "[!] ~/.local/bin not in PATH"
    echo "    Add this to your ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
else
    echo "[✓] Installed! Run with: FTPFS"
fi
