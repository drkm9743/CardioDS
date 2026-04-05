#!/bin/bash
# setup_xpf.sh — Download XPF and libgrabkernel2 dylibs from lara's repo
#
# Run this before building CardioDS to pull the required native libraries.
# These dylibs must be added to the Xcode project:
#   1. Drag lib/ folder into Xcode
#   2. In Build Phases → Link Binary With Libraries, add both dylibs
#   3. In Build Phases → Embed Libraries, add both dylibs (Embed & Sign)
#   4. In Build Settings → Library Search Paths, add $(PROJECT_DIR)/card-test/lib
#   5. In Build Settings → Header Search Paths, add $(PROJECT_DIR)/card-test/kexploit

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$SCRIPT_DIR/card-test/lib"

LARA_BASE="https://github.com/rooootdev/lara/raw/main/lara"

mkdir -p "$LIB_DIR"

echo "==> Downloading libgrabkernel2.dylib..."
curl -L -o "$LIB_DIR/libgrabkernel2.dylib" "$LARA_BASE/lib/libgrabkernel2.dylib"

echo "==> Downloading libxpf.dylib..."
curl -L -o "$LIB_DIR/libxpf.dylib" "$LARA_BASE/lib/libxpf.dylib"

echo ""
echo "Done! Libraries saved to: $LIB_DIR"
echo ""
echo "Next steps in Xcode:"
echo "  1. Drag the 'lib' folder into your Xcode project navigator"
echo "  2. Select CardioDS target → Build Phases → Link Binary With Libraries"
echo "     Add: libgrabkernel2.dylib, libxpf.dylib"
echo "  3. Build Phases → Embed Libraries (or Copy Files → Frameworks)"
echo "     Add both dylibs with 'Code Sign On Copy' enabled"
echo "  4. Build Settings → Library Search Paths:"
echo "     \$(PROJECT_DIR)/card-test/lib"
echo "  5. Build Settings → Header Search Paths:"
echo "     \$(PROJECT_DIR)/card-test/kexploit"
echo ""
echo "If downloads fail, manually copy from:"
echo "  https://github.com/rooootdev/lara/tree/main/lara/lib"
