#!/bin/bash

# Script para forzar la compilación del código corregido
# Este script se ejecuta antes de PyInstaller para asegurar que el código está correcto

set -e

echo "=== Pre-build validation and fixes ==="

# Verificar que app.py tiene la configuración correcta
if ! grep -q "log_file_candidates" app.py; then
    echo "❌ ERROR: app.py doesn't have the corrected logging configuration"
    echo "Expected to find 'log_file_candidates' in setup_logging function"
    exit 1
fi

# Verificar que no hay paths hardcodeados problemáticos
if grep -n "/var/log/quipu\.log" app.py | grep -v "candidates\|#\|Legacy location"; then
    echo "❌ ERROR: Found hardcoded problematic log path in app.py"
    echo "This will cause the deployment to fail"
    exit 1
fi

# Verificar imports necesarios
if ! grep -q "from pathlib import Path" app.py; then
    echo "❌ ERROR: Missing required import 'from pathlib import Path' in app.py"
    exit 1
fi

# Mostrar información del código que se va a compilar
echo "✅ Code validation passed"
echo "📋 Current setup_logging function:"
sed -n '/def setup_logging/,/^def\|^class\|^$/p' app.py | head -20

echo "✅ Ready for PyInstaller compilation"
