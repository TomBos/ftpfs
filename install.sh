#!/bin/bash

set -e

INSTALL_DIR="$HOME/.local/share/FTPFS"
BIN_DIR="$HOME/.local/bin"
WRAPPER="$BIN_DIR/FTPFS"

echo "[*] Installing FTPFS to $INSTALL_DIR..."

mkdir -p "$INSTALL_DIR"
cp -r ./src/* "$INSTALL_DIR"

echo "[*] Creating wrapper script at $WRAPPER..."
mkdir -p "$BIN_DIR"

cat > "$WRAPPER" <<EOF
#!/bin/bash
python3 "$INSTALL_DIR/FTPFS.py" "\$@"
EOF

chmod +x "$WRAPPER"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "[!] ~/.local/bin not in PATH"
    echo "    Add this line to your shell profile (e.g. ~/.bashrc):"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
else
    echo "[✓] Installed successfully. You can now run: FTPFS"
fi

