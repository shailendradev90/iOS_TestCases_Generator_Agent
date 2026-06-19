#!/bin/bash
# Build script for iOS Test Generator Agent

set -e  # Exit on error

echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Clean complete"
echo ""

echo "📦 Installing build dependencies..."
python3 -m pip install --upgrade build twine

echo ""
echo "🔨 Building package..."
python3 -m build

echo ""
echo "✅ Build complete!"
echo ""

echo "🔍 Checking package..."
twine check dist/*

echo ""
echo "📊 Build artifacts:"
ls -lh dist/

echo ""
echo "✅ Package is ready for distribution!"
echo ""
echo "Next steps:"
echo "  1. Test locally: pip install dist/*.whl"
echo "  2. Test on TestPyPI: twine upload --repository testpypi dist/*"
echo "  3. Publish to PyPI: twine upload dist/*"

# Made with Bob
