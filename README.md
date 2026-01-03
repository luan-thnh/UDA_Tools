# 🎓 UDA Auto Grader Pro v3.5

Tool tự động nhập điểm cho hệ thống quản lý điểm của Đại học Đông Á (UDA).

## 📋 Tính năng

- ✅ Tự động đăng nhập vào hệ thống UDA
- ✅ Nhập điểm hàng loạt từ file Excel
- ✅ Xóa điểm hàng loạt
- ✅ Hỗ trợ nhiều loại điểm: KTTX, CCAN, GHP, TDNH, THTN, TLDA, THI1
- ✅ Giao diện đẹp với CustomTkinter
- ✅ Hỗ trợ Windows, macOS, Linux
- ✅ **Cấu hình browser tùy chỉnh** (Chrome, Brave, Edge, Chromium...)
- ✅ Chế độ chạy ẩn (Headless mode)
- ✅ Nhớ tài khoản và cấu hình

## 🛠️ Yêu cầu hệ thống

- **Python 3.9+** (để build)
- **Trình duyệt Chromium-based**:
  - Google Chrome (khuyến nghị)
  - Chromium
  - Microsoft Edge
  - Brave Browser
  - Vivaldi
- **ChromeDriver** (tự động tải khi chạy Selenium 4+)

---

## 🆕 Tính năng mới v3.5

### ⚙️ Cài đặt Browser tùy chỉnh

Click nút **"⚙️ Cài đặt"** ở góc trên phải để cấu hình:

- **Chrome/Chromium Path**: Đường dẫn tới file thực thi của browser
- **ChromeDriver Path**: Đường dẫn tới ChromeDriver (tùy chọn)

#### Đường dẫn phổ biến:

| Browser  | Windows                                                              | macOS                                                            | Linux                       |
| -------- | -------------------------------------------------------------------- | ---------------------------------------------------------------- | --------------------------- |
| Chrome   | `C:\Program Files\Google\Chrome\Application\chrome.exe`              | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`   | `/usr/bin/google-chrome`    |
| Brave    | `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe` | `/Applications/Brave Browser.app/Contents/MacOS/Brave Browser`   | `/usr/bin/brave-browser`    |
| Edge     | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`       | `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge` | `/usr/bin/microsoft-edge`   |
| Chromium | -                                                                    | `/Applications/Chromium.app/Contents/MacOS/Chromium`             | `/usr/bin/chromium-browser` |

---

## 🚀 Build Cross-Platform với GitHub Actions (Khuyến nghị)

### Bước 1: Push code lên GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/luan-thnh/UDA_Auto_Grader.git
git push -u origin main
```

### Bước 2: GitHub tự động build

Sau khi push, GitHub Actions sẽ tự động build cho:

- ✅ **Windows** (`.exe`)
- ✅ **macOS**
- ✅ **Linux**

### Bước 3: Download artifacts

1. Vào tab **Actions** trên GitHub
2. Click vào workflow run mới nhất
3. Download file từ phần **Artifacts**

### Bước 4: Tạo Release

```bash
git tag v3.5.0
git push origin v3.5.0
```

---

## 🔧 Build thủ công (Local)

### Yêu cầu

#### Ubuntu/Debian

```bash
sudo apt-get install -y python3-tk upx-ucl
```

#### macOS

```bash
brew install upx
```

#### Windows

```cmd
choco install upx -y
```

### Build

```bash
# Tạo và kích hoạt venv
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# hoặc .venv\Scripts\activate trên Windows

# Cài dependencies
pip install -r requirements.txt

# Build
python build.py
```

### Kết quả

| Platform | Output                     | Size      |
| -------- | -------------------------- | --------- |
| Windows  | `dist/UDA_Auto_Grader.exe` | ~12-15 MB |
| macOS    | `dist/UDA_Auto_Grader`     | ~12-15 MB |
| Linux    | `dist/UDA_Auto_Grader`     | ~12-15 MB |

---

## 🎯 Hướng dẫn sử dụng

1. **Chạy ứng dụng**

2. **Cấu hình browser** (nếu cần):

   - Click ⚙️ **Cài đặt**
   - Chọn đường dẫn Chrome/Browser

3. **Nhập thông tin**:

   - Tài khoản giảng viên
   - Mật khẩu
   - Mã môn học (copy từ web UDA)

4. **Chọn file Excel** (phải có cột IDSV)

5. **Chọn cột điểm** cần nhập/xóa

6. **Nhấn NHẬP ĐIỂM hoặc XÓA ĐIỂM**

---

## 📝 Định dạng file Excel

| Cột  | Mô tả                 | Bắt buộc |
| ---- | --------------------- | -------- |
| IDSV | Mã số sinh viên       | ✅       |
| KTTX | Kiểm tra thường xuyên | ❌       |
| CCAN | Chuyên cần            | ❌       |
| GHP  | Giữa học phần         | ❌       |
| TDNH | Thảo luận nhóm        | ❌       |
| THTN | Thực hành/Thí nghiệm  | ❌       |
| TLDA | Tiểu luận/Đồ án       | ❌       |
| THI1 | Thi lần 1             | ❌       |

---

## 📁 Cấu trúc thư mục

```
Nhap diem/
├── .github/workflows/build.yml  # GitHub Actions
├── tool_nhap_diem_uda.py        # Source code chính
├── template.xlsx                # File mẫu Excel
├── requirements.txt             # Dependencies
├── build.py                     # Script build
├── build.sh                     # Build script (Linux/macOS)
├── build.bat                    # Build script (Windows)
├── .gitignore
└── README.md
```

---

## 🔧 Troubleshooting

### Lỗi "No module named 'tkinter'"

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk@3.11
```

### Lỗi "WebDriver" / "Chrome not found"

1. Click ⚙️ **Cài đặt**
2. Chọn đường dẫn tới Chrome/Browser của bạn
3. Lưu và thử lại

### Lỗi "ChromeDriver version mismatch"

- Selenium 4+ tự động quản lý ChromeDriver
- Nếu vẫn lỗi, tải ChromeDriver phù hợp và cấu hình trong Cài đặt

### Muốn dùng Brave/Edge thay Chrome

1. Click ⚙️ **Cài đặt**
2. Nhập đường dẫn tới Brave/Edge executable
3. Lưu

---

## 📂 Vị trí lưu cấu hình

Cấu hình được lưu tại:

- **Windows**: `C:\Users\<username>\.uda_grader\config.json`
- **macOS/Linux**: `~/.uda_grader/config.json`

---

## 📄 License

MIT License - Sử dụng tự do cho mục đích giáo dục.

## 👨‍💻 Tác giả

Developed for UDA (Đại học Đông Á)
