#!/bin/bash
# =====================================================
# Build script for Linux and macOS
# =====================================================

set -e  # Exit on error

echo "========================================"
echo "🚀 UDA Auto Grader - Build Script"
echo "   Platform: $(uname -s)"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

# Check Python
echo ""
echo "📦 Kiểm tra Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo -e "${RED}❌ Python không được cài đặt!${NC}"
    exit 1
fi

echo -e "${GREEN}   ✅ Python: $($PYTHON --version)${NC}"

# Create virtual environment (optional but recommended)
if [ "$1" == "--venv" ]; then
    echo ""
    echo "🔧 Tạo virtual environment..."
    $PYTHON -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}   ✅ Virtual environment đã được kích hoạt${NC}"
fi

# Install dependencies
echo ""
echo "📦 Cài đặt dependencies..."
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install -r requirements.txt

# Run build script
echo ""
echo "🔨 Bắt đầu build..."
$PYTHON build.py

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================"
    echo "✅ BUILD THÀNH CÔNG!"
    echo "========================================${NC}"
    
    # Show output location
    if [ -f "dist/UDA_Auto_Grader" ]; then
        echo ""
        echo "📦 File output: $(pwd)/dist/UDA_Auto_Grader"
        
        # Make executable
        chmod +x dist/UDA_Auto_Grader
        echo -e "${GREEN}   ✅ Đã cấp quyền thực thi${NC}"
    fi
    
    echo ""
    echo "📋 Để chạy ứng dụng:"
    echo "   ./dist/UDA_Auto_Grader"
else
    echo ""
    echo -e "${RED}❌ BUILD THẤT BẠI!${NC}"
    exit 1
fi
