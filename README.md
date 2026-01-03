# 🚀 UDA Tools Pro v4.0

All-in-one tool suite cho giảng viên Đại học Đông Á (UDA).

## ✨ Tính năng

### Tab 1: Nhập Điểm UDA

- ✅ Tự động đăng nhập vào hệ thống UDA
- ✅ Nhập/Xóa điểm hàng loạt từ file Excel
- ✅ Hỗ trợ: KTTX, CCAN, GHP, TDNH, THTN, TLDA, THI1
- ✅ Auto-detect Chrome/Chromium/Brave/Edge
- ✅ Chế độ Headless (chạy ẩn)
- ✅ Nhớ tài khoản

### Tab 2: HRM Auto Check-in

- ✅ Tự động check-in công việc hàng ngày
- ✅ **Random nội dung** từ danh sách (mỗi ngày khác nhau!)
- ✅ Hỗ trợ **Cronjob** (Ubuntu, Windows, macOS)
- ✅ Xem **lịch sử** hoạt động
- ✅ Chế độ Headless

---

## 🛠️ Yêu cầu

- **Trình duyệt**: Chrome, Brave, Edge, hoặc Chromium
- **ChromeDriver**: Tự động quản lý bởi Selenium 4+

---

## 📥 Cài đặt

### Tải từ Releases

Download file phù hợp với OS:

- **Windows**: `UDA_Tools_Pro-windows-x64.exe`
- **macOS**: `UDA_Tools_Pro-macos-x64`
- **Linux**: `UDA_Tools_Pro-linux-x64`

### Chạy từ source

```bash
# Clone repo
git clone https://github.com/luan-thnh/UDA_Auto_Grader.git
cd UDA_Auto_Grader

# Cài dependencies
pip install -r requirements.txt

# Chạy
python uda_tools.py
```

---

## 🔄 Cronjob - Tự động chạy hàng ngày

### 🐧 Ubuntu/Linux

```bash
# Mở crontab
crontab -e

# Thêm dòng (chạy lúc 8:00 sáng)
0 8 * * * /usr/bin/python3 /path/to/uda_tools.py --hrm-auto

# Kiểm tra
crontab -l
```

### 🪟 Windows (Task Scheduler)

1. Mở **Task Scheduler** (`taskschd.msc`)
2. **Create Basic Task...**
3. Trigger: **Daily**, lúc 8:00 AM
4. Action: **Start a program**
   - Program: `python.exe`
   - Arguments: `C:\path\to\uda_tools.py --hrm-auto`

### 🍎 macOS (launchd)

```bash
# Tạo file ~/Library/LaunchAgents/com.uda.hrm.plist

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.uda.hrm</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/uda_tools.py</string>
        <string>--hrm-auto</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>

# Load
launchctl load ~/Library/LaunchAgents/com.uda.hrm.plist
```

---

## 📁 Cấu trúc

```
📦 UDA_Tools_Pro/
├── 📄 uda_tools.py           # Main app (GUI + CLI)
├── 📄 build.py               # Build script
├── 📄 requirements.txt       # Dependencies
├── 📄 template.xlsx          # Excel template
├── 📁 .github/workflows/     # CI/CD
└── 📄 README.md
```

---

## 🔧 Build

### GitHub Actions (Khuyến nghị)

Push lên GitHub → Actions tự động build → Download từ Releases

### Build thủ công

```bash
# Cài dependencies
pip install -r requirements.txt

# Build
python build.py
```

Kết quả: `dist/UDA_Tools_Pro` (hoặc `.exe` trên Windows)

---

## 📊 Random Content

Trong tab HRM, nhập nhiều nội dung công việc (mỗi dòng 1 nội dung):

```
Soạn nội dung thực hành
Hỗ trợ sinh viên
Chấm bài tập
Soạn đề thi
Chuẩn bị slide bài giảng
```

Mỗi lần chạy, tool sẽ **random chọn 1 nội dung** → Không bị trùng lặp!

---

## 📂 Vị trí lưu dữ liệu

```
~/.uda_tools/
├── config.json    # Cấu hình
├── history.json   # Lịch sử
└── app.log        # Log
```

---

## 🐛 Troubleshooting

### Lỗi "Chrome not found"

1. Click **Cài đặt** ở góc trên phải
2. Nhập đường dẫn tới Chrome/Brave/Edge
3. Hoặc để trống nếu đã cài Chrome mặc định

### Lỗi "Timeout"

- Kiểm tra kết nối mạng
- Tăng timeout trong code nếu server chậm

### HRM không check-in

- Kiểm tra email/password
- Chạy thử với Headless = OFF để debug

---

## 📄 License

MIT License

## 👨‍💻 Author

Developed for UDA (Đại học Đông Á)
