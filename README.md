# 🎓 UDA Auto Grader Pro v3.3

Tool tự động nhập điểm cho hệ thống quản lý điểm của Đại học Đông Á (UDA).

## 📋 Tính năng

- ✅ Tự động đăng nhập vào hệ thống UDA
- ✅ Nhập điểm hàng loạt từ file Excel
- ✅ Xóa điểm hàng loạt
- ✅ Hỗ trợ nhiều loại điểm: KTTX, CCAN, GHP, TDNH, THTN, TLDA, THI1
- ✅ Giao diện đẹp với CustomTkinter
- ✅ Hỗ trợ Windows, macOS, Linux

## 🛠️ Yêu cầu hệ thống

- Python 3.9+ (để build)
- Google Chrome hoặc Chromium browser (để chạy)
- ChromeDriver (tự động tải khi chạy Selenium)

---

## 🚀 Build Cross-Platform với GitHub Actions (Khuyến nghị)

Cách đơn giản nhất để build cho cả 3 hệ điều hành từ 1 lần push code:

### Bước 1: Push code lên GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Bước 2: GitHub tự động build

Sau khi push, GitHub Actions sẽ tự động:

- ✅ Build cho **Windows** (`.exe`)
- ✅ Build cho **macOS**
- ✅ Build cho **Linux**

### Bước 3: Download artifacts

1. Vào tab **Actions** trên GitHub repository
2. Click vào workflow run mới nhất
3. Scroll xuống phần **Artifacts**
4. Download file cho từng hệ điều hành:
   - `UDA_Auto_Grader-windows-x64.exe`
   - `UDA_Auto_Grader-macos-x64`
   - `UDA_Auto_Grader-linux-x64`

### Bước 4: Tạo Release (Optional)

Để tự động tạo Release với tất cả các file:

```bash
git tag v3.3.0
git push origin v3.3.0
```

---

## 🔧 Build thủ công (Local)

### Yêu cầu trước khi build

#### Ubuntu/Debian

```bash
sudo apt-get install -y python3-tk
```

#### macOS

```bash
# Thường đã có sẵn, nếu thiếu:
brew install python-tk@3.11
```

#### Windows

- Tkinter thường được cài sẵn với Python từ python.org

### Chuẩn bị môi trường

#### Linux/macOS

```bash
# Tạo virtual environment
python3 -m venv .venv

# Kích hoạt venv
source .venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

#### Windows

```cmd
# Tạo virtual environment
python -m venv .venv

# Kích hoạt venv
.venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Build ứng dụng

#### Cách 1: Sử dụng Python script

```bash
python build.py
```

#### Cách 2: Sử dụng shell script

**Linux/macOS:**

```bash
chmod +x build.sh
./build.sh
```

**Windows:**

```cmd
build.bat
```

### Kết quả build

| Platform | Output File                | Kích thước |
| -------- | -------------------------- | ---------- |
| Windows  | `dist/UDA_Auto_Grader.exe` | ~22 MB     |
| macOS    | `dist/UDA_Auto_Grader`     | ~22 MB     |
| Linux    | `dist/UDA_Auto_Grader`     | ~22 MB     |

---

## 🎯 Hướng dẫn sử dụng

1. **Chạy ứng dụng** từ thư mục `dist/`

2. **Nhập thông tin đăng nhập**:

   - Tài khoản giảng viên
   - Mật khẩu

3. **Chọn môn học**:

   - Copy value môn học từ trang nhập điểm UDA
   - Ví dụ: `Kỹ năng số (1tc)/OK//93190/7481/KL24A`

4. **Chọn file Excel**:

   - Sử dụng file mẫu hoặc tạo file riêng
   - File phải có cột `IDSV` (bắt buộc)

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
├── .github/
│   └── workflows/
│       └── build.yml           # GitHub Actions workflow
├── tool_nhap_diem_uda.py       # Source code chính
├── template.xlsx               # File mẫu Excel
├── requirements.txt            # Dependencies
├── build.py                    # Script build (Python)
├── build.sh                    # Script build (Linux/macOS)
├── build.bat                   # Script build (Windows)
├── .gitignore                  # Git ignore file
└── README.md                   # Hướng dẫn này
```

---

## ⚠️ Lưu ý quan trọng

1. **Chrome/Chromium**: Đảm bảo đã cài đặt Google Chrome hoặc Chromium
2. **Kết nối mạng**: Cần kết nối internet để truy cập UDA
3. **Điểm hợp lệ**: Điểm phải là số từ 0 đến 10
4. **Backup**: Luôn backup dữ liệu trước khi thao tác

---

## 🔧 Troubleshooting

### Lỗi "No module named 'tkinter'"

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk@3.11
```

### Lỗi "ChromeDriver not found"

- Selenium 4+ tự động quản lý ChromeDriver
- Đảm bảo Chrome đã được cài đặt

### Build thất bại

- Đảm bảo đã kích hoạt virtual environment
- Kiểm tra đã cài đủ dependencies: `pip install -r requirements.txt`

---

## 📄 License

MIT License - Sử dụng tự do cho mục đích giáo dục.

## 👨‍💻 Tác giả

Developed for UDA (Đại học Đông Á)
