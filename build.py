#!/usr/bin/env python3
"""
Cross-platform build script for UDA Auto Grader Tool
Supports: Windows, macOS, Linux
"""

import subprocess
import sys
import os
import platform
import shutil

# =====================================================
# =============== CẤU HÌNH BUILD ======================
# =====================================================

APP_NAME = "UDA_Auto_Grader"
MAIN_SCRIPT = "tool_nhap_diem_uda.py"
VERSION = "3.3.0"

# Icon files (optional - create these if you have icons)
ICON_WIN = "icon.ico"      # Windows icon
ICON_MAC = "icon.icns"     # macOS icon
ICON_LINUX = "icon.png"    # Linux icon

# Additional data files to bundle
DATA_FILES = [
    ("template.xlsx", "."),  # (source, destination in bundle)
]

# Hidden imports that PyInstaller might miss
HIDDEN_IMPORTS = [
    "customtkinter",
    "PIL._tkinter_finder",
    "openpyxl",
    "selenium",
    "selenium.webdriver",
    "selenium.webdriver.chrome",
    "selenium.webdriver.chrome.service",
    "selenium.webdriver.chrome.options",
    "selenium.webdriver.common.by",
    "selenium.webdriver.support.ui",
    "selenium.webdriver.support.expected_conditions",
]

# Các module không cần thiết - loại bỏ để giảm size
EXCLUDES = [
    # Test frameworks
    "pytest", "unittest", "doctest", "test",
    # Không cần các browser khác
    "selenium.webdriver.firefox",
    "selenium.webdriver.edge", 
    "selenium.webdriver.safari",
    "selenium.webdriver.ie",
    "selenium.webdriver.remote",
    "selenium.webdriver.webkitgtk",
    "selenium.webdriver.wpewebkit",
    # Không cần debugging tools
    "pdb", "profile", "cProfile",
    # Email/network không cần
    "email", "html.parser", "ftplib", "imaplib", "smtplib",
    # Packages không sử dụng
    "numpy", "pandas", "matplotlib", "scipy",
    "PIL.ImageQt", "PIL.ImageTk",
    "asyncio", "concurrent",
    "multiprocessing",
    "xmlrpc", "curses",
]

# Sử dụng UPX để nén (nếu có)
USE_UPX = True

# =====================================================
# =============== HÀM HỖ TRỢ ==========================
# =====================================================

def get_os_name():
    """Lấy tên hệ điều hành"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system

def get_icon_path():
    """Lấy đường dẫn icon phù hợp với OS"""
    system = platform.system().lower()
    if system == "windows" and os.path.exists(ICON_WIN):
        return ICON_WIN
    elif system == "darwin" and os.path.exists(ICON_MAC):
        return ICON_MAC
    elif system == "linux" and os.path.exists(ICON_LINUX):
        return ICON_LINUX
    return None

def check_package_installed(package_name):
    """Kiểm tra package đã được cài đặt bằng pip show"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package_name],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def check_dependencies():
    """Kiểm tra các dependencies cần thiết"""
    print("📦 Kiểm tra dependencies...")
    
    # Check PyInstaller (có thể import được)
    try:
        import PyInstaller
        print(f"   ✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("   ❌ PyInstaller chưa được cài đặt!")
        print("   💡 Chạy: pip install pyinstaller")
        return False
    
    # Check các package khác bằng pip show (tránh lỗi import GUI)
    packages = ["customtkinter", "openpyxl", "selenium"]
    
    for pkg in packages:
        if check_package_installed(pkg):
            print(f"   ✅ {pkg} OK")
        else:
            print(f"   ❌ {pkg} chưa được cài đặt!")
            return False
    
    return True

def check_files():
    """Kiểm tra các file cần thiết"""
    print("\n📁 Kiểm tra files...")
    
    if not os.path.exists(MAIN_SCRIPT):
        print(f"   ❌ Không tìm thấy file chính: {MAIN_SCRIPT}")
        return False
    print(f"   ✅ File chính: {MAIN_SCRIPT}")
    
    # Check template file
    if not os.path.exists("template.xlsx"):
        print("   ⚠️  Không tìm thấy template.xlsx - Sẽ bỏ qua file này")
    else:
        print("   ✅ Template file: template.xlsx")
    
    return True

def get_customtkinter_path():
    """Lấy đường dẫn thư viện CustomTkinter bằng pip show"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "customtkinter"],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if line.startswith('Location:'):
                location = line.split(':', 1)[1].strip()
                return os.path.join(location, 'customtkinter')
    return None

def clean_build():
    """Xóa các folder build cũ"""
    print("\n🧹 Dọn dẹp build cũ...")
    
    folders_to_clean = ["build", "dist", f"{APP_NAME}.spec"]
    for folder in folders_to_clean:
        if os.path.exists(folder):
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            else:
                os.remove(folder)
            print(f"   🗑️  Đã xóa: {folder}")

def build_app():
    """Build ứng dụng với PyInstaller"""
    os_name = get_os_name()
    print(f"\n🔨 Bắt đầu build cho {os_name.upper()}...")
    print(f"   📌 Phiên bản: {VERSION}")
    
    # Base command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",            # Đóng gói thành 1 file duy nhất
        "--windowed",           # Không hiện console window
        "--clean",              # Xóa cache cũ
        "--noconfirm",          # Không hỏi xác nhận
        "--strip",              # Strip debug symbols (giảm size)
    ]
    
    # Thêm UPX nếu được bật và có sẵn
    if USE_UPX:
        if shutil.which("upx"):
            print("   🗜️  UPX compression: ENABLED")
        else:
            cmd.append("--noupx")
            print("   ⚠️  UPX không được cài đặt, bỏ qua compression")
    else:
        cmd.append("--noupx")
    
    # Add excludes để giảm size
    for exc in EXCLUDES:
        cmd.extend(["--exclude-module", exc])
    print(f"   🚫 Loại bỏ {len(EXCLUDES)} modules không cần thiết")
    
    # Add icon if exists
    icon_path = get_icon_path()
    if icon_path:
        cmd.extend(["--icon", icon_path])
        print(f"   🎨 Icon: {icon_path}")
    
    # Add hidden imports
    for imp in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", imp])
    
    # Add CustomTkinter data (required for theming)
    ctk_path = get_customtkinter_path()
    if ctk_path:
        cmd.extend(["--add-data", f"{ctk_path}{os.pathsep}customtkinter"])
        print(f"   📚 CustomTkinter path: {ctk_path}")
    
    # Add data files
    for src, dest in DATA_FILES:
        if os.path.exists(src):
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
            print(f"   📄 Data file: {src} -> {dest}")
    
    # Add main script
    cmd.append(MAIN_SCRIPT)
    
    print("\n⏳ Đang build... (có thể mất vài phút)")
    
    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=False, check=False)
    
    if result.returncode == 0:
        # Get output file
        if os_name == "windows":
            output_file = f"dist/{APP_NAME}.exe"
        elif os_name == "macos":
            output_file = f"dist/{APP_NAME}.app"
        else:
            output_file = f"dist/{APP_NAME}"
        
        if os.path.exists(output_file.replace(".app", "")):
            output_file = output_file.replace(".app", "")
        
        print(f"\n✅ BUILD THÀNH CÔNG!")
        print(f"   📦 Output: {os.path.abspath(output_file)}")
        
        # Get file size
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"   📊 Kích thước: {size_mb:.2f} MB")
        
        return True
    else:
        print(f"\n❌ BUILD THẤT BẠI!")
        print(f"   Return code: {result.returncode}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print(f"🚀 UDA AUTO GRADER - BUILD TOOL")
    print(f"   Version: {VERSION}")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {platform.python_version()}")
    print("=" * 60)
    
    # Check all requirements
    if not check_dependencies():
        print("\n❌ Vui lòng cài đặt đầy đủ dependencies!")
        print("   Chạy: pip install -r requirements.txt")
        sys.exit(1)
    
    if not check_files():
        print("\n❌ Thiếu file cần thiết!")
        sys.exit(1)
    
    # Clean old builds
    clean_build()
    
    # Build
    success = build_app()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 HOÀN TẤT!")
        print("=" * 60)
        print("\n📋 HƯỚNG DẪN SỬ DỤNG:")
        print("   1. Tìm file trong thư mục 'dist/'")
        print("   2. Copy file đến nơi cần sử dụng")
        print("   3. Chạy chương trình")
        print("\n⚠️  LƯU Ý:")
        print("   - Cần có Chrome/Chromium browser đã cài đặt")
        print("   - ChromeDriver sẽ tự động được tải khi chạy")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
