#!/bin/bash

echo "=== Forcing fresh build - no cache ==="

# Display current code version
echo "📋 Current commit: $(git rev-parse HEAD)"
echo "📋 Current timestamp: $(date)"

# Remove any potential build cache
rm -rf build/ dist/ *.spec __pycache__/ 2>/dev/null || true

# Display current app.py setup_logging function to verify it's correct
echo "📋 Current setup_logging function in app.py:"
echo "============================================"
sed -n '/def setup_logging/,/^def\|^class\|^$/p' app.py | head -30
echo "============================================"

# Verify we have the corrected code
if grep -q "log_file_candidates" app.py; then
    echo "✅ Confirmed: Using corrected logging code"
else
    echo "❌ ERROR: Still using old logging code!"
    exit 1
fi

echo "✅ Ready for fresh PyInstaller build"
