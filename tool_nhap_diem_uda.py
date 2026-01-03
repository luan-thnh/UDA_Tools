import customtkinter as ctk
from tkinter import filedialog, messagebox
import time
import threading
import os
import shutil
import openpyxl
import sys
import json
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

# =====================================================
# ============== CẤU HÌNH LOGGING =====================
# =====================================================
LOG_DIR = os.path.join(os.path.expanduser("~"), ".uda_grader")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'app.log'), encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

# =====================================================
# ============== HÀM HỖ TRỢ PYINSTALLER ===============
# =====================================================
def resource_path(relative_path):
    """ 
    Lấy đường dẫn tuyệt đối tới tài nguyên, dùng được cho cả lúc chạy dev 
    và lúc đã build thành file .exe (PyInstaller)
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =====================================================
# ============== CẤU HÌNH HỆ THỐNG ====================
# =====================================================
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

DEFAULT_TITLES = ["KTTX", "CCAN", "GHP", "THI1"]
ALL_TITLES = ['CCAN', 'KTTX', 'GHP', 'TDNH', 'THTN', 'TLDA', 'THI1']

EXCEL_MAP = {
    "KTTX": "KTTX", "CCAN": "CCAN", "GHP": "GHP",
    "TDNH": "TDNH", "THTN": "THTN", "TLDA": "TLDA", "THI1": "THI1"
}

NHAP_DIEM_URL = "https://uda.edu.vn/cbgv/gv_nhapdiem"
CONFIG_FILE = os.path.join(LOG_DIR, "config.json")
VERSION = "3.6.0"

# =====================================================
# ============== AUTO DETECT CHROME ===================
# =====================================================
def detect_chrome_path():
    """Tu dong tim Chrome/Chromium tren he thong"""
    candidates = []
    
    if sys.platform == "win32":
        # Windows paths
        candidates = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        ]
    elif sys.platform == "darwin":
        # macOS paths
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    else:
        # Linux paths
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/brave-browser",
            "/usr/bin/microsoft-edge",
            "/snap/bin/chromium",
        ]
    
    for path in candidates:
        if os.path.exists(path):
            return path
    
    return None

# =====================================================
# ============== QUAN LY CAU HINH =====================
# =====================================================
def load_config():
    """Load cau hinh da luu"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Loi load config: {e}")
    return {}

def save_config(config):
    """Luu cau hinh"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Loi save config: {e}")

# =====================================================
# ============== LOGIC XỬ LÝ (BACKEND) ================
# =====================================================

def safe_score(val):
    """Chuyển đổi giá trị thành điểm hợp lệ"""
    try:
        if val is None:
            return "0.0"
        score = float(str(val).replace(",", "."))
        if score < 0:
            score = 0
        elif score > 10:
            score = 10
        return "{:.1f}".format(score)
    except (ValueError, TypeError):
        return "0.0"

def read_excel_openpyxl(filepath):
    """Đọc file Excel và trả về danh sách sinh viên"""
    try:
        logger.info(f"Đọc file Excel: {filepath}")
        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet = wb.active 
        rows = list(sheet.iter_rows(values_only=True))
        
        if not rows:
            raise ValueError("File Excel rỗng!")

        header_raw = rows[0]
        headers = [str(h).strip().upper() if h is not None else "" for h in header_raw]
        
        if "IDSV" not in headers:
            raise ValueError("File Excel thiếu cột 'IDSV'!")

        idsv_index = headers.index("IDSV")
        data_list = []
        
        for row in rows[1:]:
            if len(row) <= idsv_index or row[idsv_index] is None:
                continue
            row_data = {"IDSV": str(row[idsv_index]).strip()}
            for i, cell_val in enumerate(row):
                if i < len(headers):
                    col_name = headers[i]
                    if col_name in EXCEL_MAP:
                        row_data[col_name] = cell_val
            data_list.append(row_data)
        
        logger.info(f"Đọc được {len(data_list)} sinh viên từ Excel")
        return data_list
    except Exception as e:
        logger.error(f"Lỗi đọc Excel: {e}")
        raise ValueError(f"Lỗi đọc file Excel: {str(e)}")

def run_tool(username, password, monhoc, excel_file, selected_titles, 
             status_callback, progress_callback=None, is_delete_mode=False, 
             headless=False, chrome_path=None):
    """
    Ham chinh thuc hien nhap/xoa diem
    
    Args:
        username: Tai khoan dang nhap
        password: Mat khau
        monhoc: Ma mon hoc
        excel_file: Duong dan file Excel
        selected_titles: Danh sach cot diem duoc chon
        status_callback: Callback cap nhat trang thai
        progress_callback: Callback cap nhat progress bar (0-100)
        is_delete_mode: True neu xoa diem, False neu nhap diem
        headless: True neu chay an browser
        chrome_path: Duong dan toi Chrome/Chromium (optional, tu dong detect neu de trong)
    """
    action_name = "XÓA" if is_delete_mode else "NHẬP"
    driver = None
    
    try:
        # Đọc Excel
        status_callback("📖 Đang đọc file Excel...")
        if progress_callback:
            progress_callback(5)
        student_data_list = read_excel_openpyxl(excel_file)
        student_map = {item['IDSV']: item for item in student_data_list}

        # Khoi dong browser
        status_callback("Dang khoi dong trinh duyet...")
        if progress_callback:
            progress_callback(10)
            
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Xac dinh Chrome path: custom > auto-detect > de Selenium tu tim
        browser_path = chrome_path
        if not browser_path:
            browser_path = detect_chrome_path()
        
        if browser_path and os.path.exists(browser_path):
            options.binary_location = browser_path
            logger.info(f"Su dung browser: {browser_path}")
        
        if headless:
            options.add_argument("--headless=new")
            status_callback("Dang khoi dong trinh duyet (an)...")
        
        # Selenium 4+ tu dong quan ly ChromeDriver
        driver = webdriver.Chrome(options=options)
        
        driver.set_page_load_timeout(30)
        wait = WebDriverWait(driver, 20)

        # Đăng nhập
        status_callback("🔐 Đang đăng nhập...")
        if progress_callback:
            progress_callback(15)
        driver.get("https://uda.edu.vn/default")
        wait.until(EC.presence_of_element_located((By.NAME, "User"))).send_keys(username)
        driver.find_element(By.NAME, "Password").send_keys(password)
        driver.find_element(By.ID, "Lnew1").click()
        time.sleep(1)
        
        logger.info(f"Đăng nhập thành công với user: {username}")

        # Truy cập trang nhập điểm
        status_callback("🔗 Đang truy cập trang nhập điểm...")
        if progress_callback:
            progress_callback(20)
        driver.get(NHAP_DIEM_URL)

        # Chọn môn học
        status_callback("🎓 Đang chọn môn học...")
        if progress_callback:
            progress_callback(25)
        select = wait.until(EC.presence_of_element_located((By.NAME, "ctl00$MainContent$Dmonlop")))
        select.click()
        time.sleep(0.5)
        
        try:
            driver.find_element(By.XPATH, f'//option[@value="{monhoc}"]').click()
        except Exception:
            raise ValueError(f"Không tìm thấy môn học: {monhoc}")
        
        time.sleep(0.5)
        driver.find_element(By.ID, "MainContent_Lopen").click()
        time.sleep(1.5)

        # Phân tích bảng điểm
        status_callback("🔍 Phân tích bảng điểm...")
        if progress_callback:
            progress_callback(30)
        tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        WEB_INDEX = {}
        IDSV_INDEX = None
        header_row_idx = None

        for r_idx, row in enumerate(rows):
            cells = row.find_elements(By.XPATH, ".//th|.//td")
            if not cells:
                continue
            texts = [c.text.strip().upper() for c in cells]
            for i, t in enumerate(texts):
                if "IDSV" in t or "MSSV" in t:
                    IDSV_INDEX = i
            if IDSV_INDEX is None:
                continue
            for i, t in enumerate(texts):
                for key in selected_titles:
                    if key in t:
                        WEB_INDEX[key] = i
            if WEB_INDEX:
                header_row_idx = r_idx
                break

        if header_row_idx is None:
            raise ValueError("Không tìm thấy header bảng điểm")
        
        missing = [k for k in selected_titles if k not in WEB_INDEX]
        if missing:
            raise ValueError(f"Web thiếu cột: {missing}")

        # Thực hiện nhập/xóa điểm
        status_callback(f"⚡ Đang {action_name} ĐIỂM...")
        errors = []
        count = 0
        data_rows = rows[header_row_idx + 1:]
        total_students = len(data_rows)
        matched_count = 0

        for i, row in enumerate(data_rows):
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) <= IDSV_INDEX:
                continue
            idsv_web = tds[IDSV_INDEX].text.strip()
            
            if idsv_web not in student_map:
                continue
            
            matched_count += 1
            student_info = student_map[idsv_web]

            for key, idx in WEB_INDEX.items():
                td = tds[idx]
                inputs = td.find_elements(By.TAG_NAME, "input")
                if not inputs:
                    errors.append(f"SV {idsv_web}: Cột {key} không có input")
                    continue
                
                target_value = "" if is_delete_mode else safe_score(student_info.get(EXCEL_MAP[key], 0))
                current_val = inputs[0].get_attribute('value')
                
                if current_val != target_value:
                    inputs[0].clear()
                    if target_value != "":
                        inputs[0].send_keys(target_value)
            
            count += 1
            
            if progress_callback:
                progress = 30 + int((count / max(matched_count, len(student_map))) * 60)
                progress_callback(min(progress, 90))
            
            if count % 5 == 0 or count == matched_count:
                status_callback(f"Đã {action_name.lower()}: {count}/{matched_count} sinh viên...")

        if errors:
            logger.warning(f"Có {len(errors)} lỗi: {errors[:5]}")

        # Lưu
        status_callback("💾 Đang lưu...")
        if progress_callback:
            progress_callback(95)
        save_btn = wait.until(EC.presence_of_element_located((By.ID, "MainContent_Lsave")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(1)
        
        if progress_callback:
            progress_callback(100)
        status_callback("✅ Hoàn tất!")
        
        logger.info(f"Hoàn tất {action_name} điểm cho {count} sinh viên")
        messagebox.showinfo("Thành công", 
            f"Đã {action_name.lower()} điểm cho {count} sinh viên!\n"
            f"(Khớp {matched_count}/{len(student_map)} SV từ Excel)")

    except TimeoutException:
        status_callback("❌ Timeout!")
        logger.error("Timeout khi chờ phản hồi từ server")
        messagebox.showerror("Lỗi", "Timeout! Server phản hồi quá chậm.")
    except WebDriverException as e:
        status_callback("❌ Lỗi Browser!")
        logger.error(f"WebDriver error: {e}")
        messagebox.showerror("Lỗi", f"Lỗi trình duyệt: {str(e)[:200]}")
    except ValueError as e:
        status_callback("❌ Lỗi!")
        logger.error(f"Value error: {e}")
        messagebox.showerror("Lỗi", str(e))
    except Exception as e:
        status_callback("❌ Lỗi!")
        logger.error(f"Unexpected error: {e}")
        messagebox.showerror("Lỗi", str(e))
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Đã đóng browser")
            except Exception:
                pass

# =====================================================
# ============== CUA SO CAI DAT =======================
# =====================================================
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, on_save_callback):
        super().__init__(parent)
        
        self.cfg = config.copy()
        self.on_save_callback = on_save_callback
        
        # Auto detect Chrome
        self.detected_chrome = detect_chrome_path()
        
        self.title("Cai dat trinh duyet")
        self.geometry("600x350")
        self.resizable(False, False)
        
        # Build UI first
        self._build_ui()
        
        # Then configure window
        self.transient(parent)
        self.grab_set()
        
        # Center
        self.update()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 350) // 2
        self.geometry(f"600x350+{x}+{y}")
        
        self.lift()
        self.focus_force()
    
    def _build_ui(self):
        # Detected Chrome info
        detect_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray25"))
        detect_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        if self.detected_chrome:
            detect_text = f"Da phat hien: {self.detected_chrome}"
            detect_color = "green"
        else:
            detect_text = "Khong tim thay Chrome/Chromium tu dong!"
            detect_color = "red"
        
        ctk.CTkLabel(detect_frame, text=detect_text, 
                     text_color=detect_color,
                     font=ctk.CTkFont(size=11)).pack(padx=15, pady=8)
        
        # Frame for inputs
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=10)
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Chrome path - custom override
        ctk.CTkLabel(input_frame, text="Custom Path:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.chrome_entry = ctk.CTkEntry(input_frame, placeholder_text="De trong = dung path da phat hien")
        self.chrome_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        ctk.CTkButton(input_frame, text="...", width=40, 
                      command=self._browse_chrome).grid(row=0, column=2, padx=10, pady=10)
        
        # Load saved custom value
        if self.cfg.get("chrome_path"):
            self.chrome_entry.insert(0, self.cfg["chrome_path"])
        
        # Help text
        help_text = """HUONG DAN:
- Neu da phat hien Chrome tu dong, ban co the de trong Custom Path
- Chi nhap Custom Path neu muon dung browser khac (Brave, Edge...)
- ChromeDriver se duoc Selenium 4+ tu dong tai ve, khong can cai dat

VD duong dan:
  Windows: C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe
  Linux: /usr/bin/brave-browser
  macOS: /Applications/Brave Browser.app/Contents/MacOS/Brave Browser"""
        
        help_lbl = ctk.CTkLabel(self, text=help_text, justify="left",
                                 font=ctk.CTkFont(size=11))
        help_lbl.pack(fill="x", padx=20, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(btn_frame, text="Luu", width=100,
                      fg_color="green", command=self._save).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Huy", width=100,
                      fg_color="gray", command=self.destroy).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Xoa cai dat", width=100,
                      fg_color="orange", command=self._clear).pack(side="right", padx=5)
    
    def _browse_chrome(self):
        if sys.platform == "win32":
            ft = [("Executable", "*.exe"), ("All", "*.*")]
        else:
            ft = [("All", "*")]
        f = filedialog.askopenfilename(title="Chon Chrome/Browser", filetypes=ft)
        if f:
            self.chrome_entry.delete(0, "end")
            self.chrome_entry.insert(0, f)
    
    def _clear(self):
        self.chrome_entry.delete(0, "end")
        self.cfg.pop("chrome_path", None)
        messagebox.showinfo("OK", "Da xoa cai dat! Se dung Chrome tu dong.")
    
    def _save(self):
        cp = self.chrome_entry.get().strip()
        
        if cp and not os.path.exists(cp):
            messagebox.showerror("Loi", f"Path khong ton tai:\n{cp}")
            return
        
        if cp:
            self.cfg["chrome_path"] = cp
        else:
            self.cfg.pop("chrome_path", None)
        
        # Remove old chromedriver_path if exists
        self.cfg.pop("chromedriver_path", None)
        
        self.on_save_callback(self.cfg)
        messagebox.showinfo("OK", "Da luu cai dat!")
        self.destroy()

# =====================================================
# ============== GIAO DIỆN NGƯỜI DÙNG (GUI) ===========
# =====================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"UDA Auto Grader Pro v{VERSION}")
        self.geometry("800x800")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # Load config đã lưu
        self.config = load_config()

        # Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "gray20"))
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        header_inner = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            header_inner, 
            text="TOOL QUẢN LÝ ĐIỂM UDA", 
            font=ctk.CTkFont(family="Roboto", size=24, weight="bold"), 
            text_color="#1F6AA5"
        ).pack(side="left", pady=5)
        
        # Settings button
        self.btn_settings = ctk.CTkButton(
            header_inner, text="⚙️ Cài đặt", width=100,
            fg_color="gray", hover_color="gray40",
            command=self.open_settings
        )
        self.btn_settings.pack(side="right", pady=5)

        # Body
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.body_frame.grid_columnconfigure(0, weight=1)

        # Info Frame
        self.info_frame = ctk.CTkFrame(self.body_frame)
        self.info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.info_frame, 
            text="THÔNG TIN CẤU HÌNH", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=10)

        # Username
        ctk.CTkLabel(self.info_frame, text="Tài khoản:").grid(row=1, column=0, sticky="w", padx=15, pady=5)
        self.user_entry = ctk.CTkEntry(self.info_frame, placeholder_text="Nhập tài khoản giảng viên")
        self.user_entry.grid(row=1, column=1, sticky="ew", padx=15, pady=5)
        if self.config.get("username"):
            self.user_entry.insert(0, self.config["username"])

        # Password
        ctk.CTkLabel(self.info_frame, text="Mật khẩu:").grid(row=2, column=0, sticky="w", padx=15, pady=5)
        self.pass_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.pass_frame.grid(row=2, column=1, sticky="ew", padx=15, pady=5)
        self.pass_entry = ctk.CTkEntry(self.pass_frame, placeholder_text="Nhập mật khẩu", show="•")
        self.pass_entry.pack(side="left", fill="x", expand=True)
        self.btn_toggle_pass = ctk.CTkButton(
            self.pass_frame, text="👁", width=30, 
            fg_color="gray", hover_color="gray40", 
            command=self.toggle_password
        )
        self.btn_toggle_pass.pack(side="right", padx=(5, 0))

        # Môn học
        ctk.CTkLabel(self.info_frame, text="Mã môn học:").grid(row=3, column=0, sticky="w", padx=15, pady=5)
        self.sub_entry = ctk.CTkEntry(
            self.info_frame, 
            placeholder_text="Value môn học (VD: Kỹ năng số (1tc)/OK//93190/7481/KL24A)"
        )
        self.sub_entry.grid(row=3, column=1, sticky="ew", padx=15, pady=5)
        if self.config.get("last_subject"):
            self.sub_entry.insert(0, self.config["last_subject"])

        # File điểm
        ctk.CTkLabel(self.info_frame, text="File điểm:").grid(row=4, column=0, sticky="w", padx=15, pady=5)
        self.file_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.file_frame.grid(row=4, column=1, sticky="ew", padx=15, pady=5)
        self.file_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Vui lòng chọn file...", state="disabled")
        self.file_entry.pack(side="left", fill="x", expand=True)
        
        self.btn_template = ctk.CTkButton(
            self.file_frame, text="⬇ Mẫu", width=60, 
            fg_color="#555555", hover_color="#333333", 
            command=self.download_template
        )
        self.btn_template.pack(side="right", padx=(5, 0))
        self.btn_browse = ctk.CTkButton(
            self.file_frame, text="📂 Chọn", width=60, 
            command=self.browse_file
        )
        self.btn_browse.pack(side="right", padx=(10, 0))

        # Options Frame
        self.options_frame = ctk.CTkFrame(self.body_frame)
        self.options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        ctk.CTkLabel(
            self.options_frame, 
            text="TÙY CHỌN", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=10)
        
        self.options_inner = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.options_inner.pack(fill="x", padx=15, pady=(0, 10))
        
        self.headless_var = ctk.BooleanVar(value=False)
        self.headless_check = ctk.CTkCheckBox(
            self.options_inner, 
            text="🔇 Chạy ẩn (Headless)", 
            variable=self.headless_var
        )
        self.headless_check.pack(side="left", padx=10)
        
        self.save_config_var = ctk.BooleanVar(value=True)
        self.save_config_check = ctk.CTkCheckBox(
            self.options_inner, 
            text="💾 Nhớ tài khoản", 
            variable=self.save_config_var
        )
        self.save_config_check.pack(side="left", padx=20)
        
        # Browser status label
        self.browser_status = ctk.CTkLabel(
            self.options_inner,
            text=self.get_browser_status_text(),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.browser_status.pack(side="right", padx=10)

        # Columns Frame
        self.cols_frame = ctk.CTkFrame(self.body_frame)
        self.cols_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        ctk.CTkLabel(
            self.cols_frame, 
            text="CỘT ĐIỂM CẦN THAO TÁC", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=10)
        
        self.mode_var = ctk.StringVar(value="default")
        self.radio_frame = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.radio_frame.pack(fill="x", padx=15)
        ctk.CTkRadioButton(
            self.radio_frame, text="Mặc định", 
            variable=self.mode_var, value="default", 
            command=self.refresh_checkbox_area
        ).pack(side="left", padx=10)
        ctk.CTkRadioButton(
            self.radio_frame, text="Tùy chọn", 
            variable=self.mode_var, value="custom", 
            command=self.refresh_checkbox_area
        ).pack(side="left", padx=20)
        
        self.chk_container = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.chk_container.pack(fill="x", padx=15, pady=10)
        self.checkbox_vars = {} 
        self.refresh_checkbox_area()

        # Progress Bar
        self.progress_frame = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.progress_frame.grid(row=3, column=0, sticky="ew", pady=5)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.pack(fill="x", padx=15)
        self.progress_bar.set(0)

        # Action Frame
        self.action_frame = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.action_frame.grid(row=4, column=0, sticky="ew", pady=10)
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)
        
        self.btn_import = ctk.CTkButton(
            self.action_frame, text="📥 NHẬP ĐIỂM", height=50, 
            font=ctk.CTkFont(size=15, weight="bold"), 
            fg_color="#009933", hover_color="#007722", 
            command=lambda: self.start_thread(is_delete=False)
        )
        self.btn_import.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_delete = ctk.CTkButton(
            self.action_frame, text="🗑 XÓA ĐIỂM", height=50, 
            font=ctk.CTkFont(size=15, weight="bold"), 
            fg_color="#CC0000", hover_color="#990000", 
            command=lambda: self.start_thread(is_delete=True)
        )
        self.btn_delete.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Status Label
        self.status_label = ctk.CTkLabel(self.body_frame, text="Sẵn sàng...", text_color="gray")
        self.status_label.grid(row=5, column=0, pady=5)
    
    def get_browser_status_text(self):
        """Lấy text hiển thị trạng thái browser"""
        chrome_path = self.config.get("chrome_path", "")
        if chrome_path:
            return f"🌐 Custom: {os.path.basename(chrome_path)}"
        return "🌐 Chrome: Tự động"
    
    def open_settings(self):
        """Mở cửa sổ cài đặt"""
        SettingsWindow(self, self.config, self.on_settings_save)
    
    def on_settings_save(self, new_config):
        """Callback khi lưu settings"""
        self.config = new_config
        save_config(self.config)
        self.browser_status.configure(text=self.get_browser_status_text())

    def toggle_password(self):
        if self.pass_entry.cget("show") == "•":
            self.pass_entry.configure(show="")
            self.btn_toggle_pass.configure(text="🔒")
        else:
            self.pass_entry.configure(show="•")
            self.btn_toggle_pass.configure(text="👁")

    def browse_file(self):
        initial_dir = self.config.get("last_folder", os.path.expanduser("~"))
        filename = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if filename:
            self.file_entry.configure(state="normal")
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)
            self.file_entry.configure(state="disabled")
            self.config["last_folder"] = os.path.dirname(filename)

    def download_template(self):
        source_file = resource_path("template.xlsx")
        
        if not os.path.exists(source_file):
            messagebox.showerror(
                "Lỗi File", 
                f"Không tìm thấy file mẫu!\nĐường dẫn: {source_file}"
            )
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", 
            filetypes=[("Excel Files", "*.xlsx")], 
            initialfile="Mau_Nhap_Diem_UDA.xlsx", 
            title="Lưu file mẫu Excel"
        )

        if save_path:
            try:
                shutil.copy(source_file, save_path)
                messagebox.showinfo("Thành công", f"Đã lưu file mẫu:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

    def refresh_checkbox_area(self):
        for widget in self.chk_container.winfo_children():
            widget.destroy()
        self.checkbox_vars.clear()
        
        mode = self.mode_var.get()
        titles = DEFAULT_TITLES if mode == "default" else ALL_TITLES
        state = "disabled" if mode == "default" else "normal"
        default_val = mode == "default"
        
        for idx, title in enumerate(titles):
            var = ctk.BooleanVar(value=default_val)
            chk = ctk.CTkCheckBox(self.chk_container, text=title, variable=var, state=state)
            chk.grid(row=idx // 4, column=idx % 4, sticky="w", padx=10, pady=8)
            self.checkbox_vars[title] = var

    def update_status(self, text):
        self.status_label.configure(text=text)
        self.update_idletasks()
    
    def update_progress(self, value):
        self.progress_bar.set(value / 100)
        self.update_idletasks()

    def set_buttons_state(self, state):
        for btn in [self.btn_import, self.btn_delete, self.btn_browse, self.btn_template, self.btn_settings]:
            btn.configure(state=state)

    def start_thread(self, is_delete):
        if is_delete:
            if not messagebox.askyesno("Xác nhận", "Bạn chắc chắn muốn XÓA điểm?"):
                return
        threading.Thread(target=self.run_process, args=(is_delete,), daemon=True).start()

    def run_process(self, is_delete):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        subject = self.sub_entry.get().strip()
        filepath = self.file_entry.get()
        
        if not all([username, password, subject, filepath]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin!")
            return
            
        if not os.path.exists(filepath):
            messagebox.showerror("Lỗi", "File không tồn tại!")
            return
        
        selected = [t for t, v in self.checkbox_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("Lỗi", "Chưa chọn cột điểm!")
            return

        # Lưu config nếu được chọn
        if self.save_config_var.get():
            self.config["username"] = username
            self.config["last_subject"] = subject
            save_config(self.config)

        self.set_buttons_state("disabled")
        self.progress_bar.set(0)
        
        try:
            run_tool(
                username, password, subject, filepath, 
                selected, self.update_status, self.update_progress,
                is_delete_mode=is_delete,
                headless=self.headless_var.get(),
                chrome_path=self.config.get("chrome_path")
            )
        finally:
            self.set_buttons_state("normal")
            self.update_status("Sẵn sàng.")
            self.progress_bar.set(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()