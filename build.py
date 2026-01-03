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
import io

# Fix encoding cho Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# =====================================================
# =============== CẤU HÌNH BUILD ======================
# =====================================================

APP_NAME = "UDA_Auto_Grader"
MAIN_SCRIPT = "tool_nhap_diem_uda.py"
VERSION = "3.4.0"

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

# Cac module khong can thiet - loai bo de giam size
EXCLUDES = [
    # Test frameworks
    "pytest", "unittest", "doctest", "test",
    # Khong can cac browser khac
    "selenium.webdriver.firefox",
    "selenium.webdriver.edge", 
    "selenium.webdriver.safari",
    "selenium.webdriver.ie",
    "selenium.webdriver.remote",
    "selenium.webdriver.webkitgtk",
    "selenium.webdriver.wpewebkit",
    # Khong can debugging tools
    "pdb", "profile", "cProfile",
    # Email/network khong can
    "email", "html.parser", "ftplib", "imaplib", "smtplib",
    # Packages khong su dung
    "numpy", "pandas", "matplotlib", "scipy",
    "PIL.ImageQt", "PIL.ImageTk",
    "asyncio", "concurrent",
    "multiprocessing",
    "xmlrpc", "curses",
]

# Su dung UPX de nen (neu co)
USE_UPX = True

# =====================================================
# =============== HAM HO TRO ==========================
# =====================================================

def get_os_name():
    """Lay ten he dieu hanh"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system

def get_icon_path():
    """Lay duong dan icon phu hop voi OS"""
    system = platform.system().lower()
    if system == "windows" and os.path.exists(ICON_WIN):
        return ICON_WIN
    elif system == "darwin" and os.path.exists(ICON_MAC):
        return ICON_MAC
    elif system == "linux" and os.path.exists(ICON_LINUX):
        return ICON_LINUX
    return None

def check_package_installed(package_name):
    """Kiem tra package da duoc cai dat bang pip show"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package_name],
        capture_output=True,
        text=True,
        check=False
    )
    return result.returncode == 0

def check_dependencies():
    """Kiem tra cac dependencies can thiet"""
    print("[*] Checking dependencies...")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"    [OK] PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("    [X] PyInstaller not installed!")
        print("    [!] Run: pip install pyinstaller")
        return False
    
    # Check cac package khac bang pip show (tranh loi import GUI)
    packages = ["customtkinter", "openpyxl", "selenium"]
    
    for pkg in packages:
        if check_package_installed(pkg):
            print(f"    [OK] {pkg}")
        else:
            print(f"    [X] {pkg} not installed!")
            return False
    
    return True

def check_files():
    """Kiem tra cac file can thiet"""
    print("\n[*] Checking files...")
    
    if not os.path.exists(MAIN_SCRIPT):
        print(f"    [X] Main script not found: {MAIN_SCRIPT}")
        return False
    print(f"    [OK] Main script: {MAIN_SCRIPT}")
    
    # Check template file
    if not os.path.exists("template.xlsx"):
        print("    [!] template.xlsx not found - will be skipped")
    else:
        print("    [OK] Template file: template.xlsx")
    
    return True

def get_customtkinter_path():
    """Lay duong dan thu vien CustomTkinter bang pip show"""
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
    """Xoa cac folder build cu"""
    print("\n[*] Cleaning old builds...")
    
    folders_to_clean = ["build", "dist", f"{APP_NAME}.spec"]
    for folder in folders_to_clean:
        if os.path.exists(folder):
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            else:
                os.remove(folder)
            print(f"    [OK] Removed: {folder}")

def build_app():
    """Build ung dung voi PyInstaller"""
    os_name = get_os_name()
    print(f"\n[*] Building for {os_name.upper()}...")
    print(f"    Version: {VERSION}")
    
    # Base command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",            # Dong goi thanh 1 file duy nhat
        "--windowed",           # Khong hien console window
        "--clean",              # Xoa cache cu
        "--noconfirm",          # Khong hoi xac nhan
        "--strip",              # Strip debug symbols (giam size)
    ]
    
    # Them UPX neu duoc bat va co san
    if USE_UPX:
        if shutil.which("upx"):
            print("    [OK] UPX compression: ENABLED")
        else:
            cmd.append("--noupx")
            print("    [!] UPX not installed, skipping compression")
    else:
        cmd.append("--noupx")
    
    # Add excludes de giam size
    for exc in EXCLUDES:
        cmd.extend(["--exclude-module", exc])
    print(f"    [OK] Excluding {len(EXCLUDES)} unnecessary modules")
    
    # Add icon if exists
    icon_path = get_icon_path()
    if icon_path:
        cmd.extend(["--icon", icon_path])
        print(f"    [OK] Icon: {icon_path}")
    
    # Add hidden imports
    for imp in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", imp])
    
    # Add CustomTkinter data (required for theming)
    ctk_path = get_customtkinter_path()
    if ctk_path:
        cmd.extend(["--add-data", f"{ctk_path}{os.pathsep}customtkinter"])
        print(f"    [OK] CustomTkinter path: {ctk_path}")
    
    # Add data files
    for src, dest in DATA_FILES:
        if os.path.exists(src):
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
            print(f"    [OK] Data file: {src} -> {dest}")
    
    # Add main script
    cmd.append(MAIN_SCRIPT)
    
    print("\n[*] Building... (this may take a few minutes)")
    
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
        
        print(f"\n[SUCCESS] BUILD COMPLETED!")
        print(f"    Output: {os.path.abspath(output_file)}")
        
        # Get file size
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"    Size: {size_mb:.2f} MB")
        
        return True
    else:
        print(f"\n[FAILED] BUILD FAILED!")
        print(f"    Return code: {result.returncode}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("UDA AUTO GRADER - BUILD TOOL")
    print(f"    Version: {VERSION}")
    print(f"    OS: {platform.system()} {platform.release()}")
    print(f"    Python: {platform.python_version()}")
    print("=" * 60)
    
    # Check all requirements
    if not check_dependencies():
        print("\n[X] Please install all dependencies!")
        print("    Run: pip install -r requirements.txt")
        sys.exit(1)
    
    if not check_files():
        print("\n[X] Missing required files!")
        sys.exit(1)
    
    # Clean old builds
    clean_build()
    
    # Build
    success = build_app()
    
    if success:
        print("\n" + "=" * 60)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nUsage:")
        print("    1. Find the executable in 'dist/' folder")
        print("    2. Copy to desired location")
        print("    3. Run the application")
        print("\nNote:")
        print("    - Chrome/Chromium browser must be installed")
        print("    - ChromeDriver will be downloaded automatically")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
