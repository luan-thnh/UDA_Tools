import customtkinter as ctk
from tkinter import filedialog, messagebox
import time
import threading
import os
import shutil
import openpyxl
import sys # <--- Bắt buộc có thư viện này

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =====================================================
# ============== HÀM HỖ TRỢ PYINSTALLER ===============
# =====================================================
def resource_path(relative_path):
    """ 
    Lấy đường dẫn tuyệt đối tới tài nguyên, dùng được cho cả lúc chạy dev 
    và lúc đã build thành file .exe (PyInstaller)
    """
    try:
        # PyInstaller tạo ra thư mục tạm _MEIPASS khi chạy exe
        base_path = sys._MEIPASS
    except Exception:
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

# =====================================================
# ============== LOGIC XỬ LÝ (BACKEND) ================
# =====================================================

def safe_score(val):
    try:
        if val is None: return "0.0"
        return "{:.1f}".format(float(str(val).replace(",", ".")))
    except:
        return "0.0"

def read_excel_openpyxl(filepath):
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet = wb.active 
        rows = list(sheet.iter_rows(values_only=True))
        
        if not rows: raise Exception("File Excel rỗng!")

        header_raw = rows[0]
        headers = [str(h).strip().upper() if h is not None else "" for h in header_raw]
        
        if "IDSV" not in headers: raise Exception("File Excel thiếu cột 'IDSV'!")

        idsv_index = headers.index("IDSV")
        data_list = []
        
        for row in rows[1:]:
            if len(row) <= idsv_index or row[idsv_index] is None: continue
            row_data = {"IDSV": str(row[idsv_index]).strip()}
            for i, cell_val in enumerate(row):
                if i < len(headers):
                    col_name = headers[i]
                    if col_name in EXCEL_MAP:
                        row_data[col_name] = cell_val
            data_list.append(row_data)
        return data_list
    except Exception as e:
        raise Exception(f"Lỗi đọc file Excel: {str(e)}")

def run_tool(username, password, monhoc, excel_file, selected_titles, status_callback, is_delete_mode=False):
    action_name = "XÓA" if is_delete_mode else "NHẬP"
    status_callback(f"📖 Đang đọc file Excel...")
    student_data_list = read_excel_openpyxl(excel_file)
    student_map = {item['IDSV']: item for item in student_data_list}

    status_callback("🌏 Đang khởi động trình duyệt...")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        status_callback("🔐 Đang đăng nhập...")
        driver.get("https://uda.edu.vn/default")
        wait.until(EC.presence_of_element_located((By.NAME, "User"))).send_keys(username)
        driver.find_element(By.NAME, "Password").send_keys(password)
        driver.find_element(By.ID, "Lnew1").click()
        time.sleep(1)

        status_callback("🔗 Đang truy cập trang nhập điểm...")
        driver.get(NHAP_DIEM_URL)

        status_callback(f"🎓 Đang chọn môn: {monhoc}...")
        select = wait.until(EC.presence_of_element_located((By.NAME, "ctl00$MainContent$Dmonlop")))
        select.click()
        time.sleep(0.5)
        try:
            driver.find_element(By.XPATH, f'//option[@value="{monhoc}"]').click()
        except:
            raise Exception(f"Không tìm thấy môn học value: {monhoc}")
        time.sleep(0.5)
        driver.find_element(By.ID, "MainContent_Lopen").click()
        time.sleep(1.5)

        status_callback("🔍 Phân tích bảng điểm...")
        tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        WEB_INDEX = {}
        IDSV_INDEX = None
        header_row_idx = None

        for r_idx, row in enumerate(rows):
            cells = row.find_elements(By.XPATH, ".//th|.//td")
            if not cells: continue
            texts = [c.text.strip().upper() for c in cells]
            for i, t in enumerate(texts):
                if "IDSV" in t or "MSSV" in t: IDSV_INDEX = i
            if IDSV_INDEX is None: continue
            for i, t in enumerate(texts):
                for key in selected_titles:
                    if key in t: WEB_INDEX[key] = i
            if WEB_INDEX:
                header_row_idx = r_idx
                break

        if header_row_idx is None: raise Exception("Không tìm thấy header bảng")
        missing = [k for k in selected_titles if k not in WEB_INDEX]
        if missing: raise Exception(f"Web thiếu cột: {missing}")

        status_callback(f"⚡ Đang {action_name} ĐIỂM...")
        errors = []
        count = 0
        data_rows = rows[header_row_idx + 1:]
        total_students = len(data_rows)

        for i, row in enumerate(data_rows):
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) <= IDSV_INDEX: continue
            idsv_web = tds[IDSV_INDEX].text.strip()
            
            if idsv_web not in student_map: continue
            student_info = student_map[idsv_web]

            for key, idx in WEB_INDEX.items():
                td = tds[idx]
                inputs = td.find_elements(By.TAG_NAME, "input")
                if not inputs:
                    errors.append(f"SV {idsv_web}: Cột {key} lỗi")
                    continue
                
                target_value = "" if is_delete_mode else safe_score(student_info.get(EXCEL_MAP[key], 0))
                current_val = inputs[0].get_attribute('value')
                
                if current_val != target_value:
                    inputs[0].clear()
                    if target_value != "": inputs[0].send_keys(target_value)
            
            count += 1
            if count % 5 == 0 or count == total_students:
                status_callback(f"Đã {action_name.lower()}: {count}/{total_students} sinh viên...")

        if errors: raise Exception("\n".join(errors[:5]))

        status_callback("💾 Đang lưu...")
        save_btn = wait.until(EC.presence_of_element_located((By.ID, "MainContent_Lsave")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", save_btn)
        
        status_callback("✅ Hoàn tất!")
        messagebox.showinfo("Thành công", f"Đã {action_name.lower()} điểm xong!")

    except Exception as e:
        status_callback("❌ Lỗi!")
        messagebox.showerror("Lỗi", str(e))

# =====================================================
# ============== GIAO DIỆN NGƯỜI DÙNG (GUI) ===========
# =====================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UDA Auto Grader Pro v3.3 (Bundled)")
        self.geometry("800x700")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "gray20"))
        self.header_frame.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(self.header_frame, text="TOOL QUẢN LÝ ĐIỂM UDA", font=ctk.CTkFont(family="Roboto", size=24, weight="bold"), text_color="#1F6AA5").pack(pady=15)

        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.body_frame.grid_columnconfigure(0, weight=1)

        self.info_frame = ctk.CTkFrame(self.body_frame)
        self.info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.info_frame, text="THÔNG TIN CẤU HÌNH", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=10)

        ctk.CTkLabel(self.info_frame, text="Tài khoản:").grid(row=1, column=0, sticky="w", padx=15, pady=5)
        self.user_entry = ctk.CTkEntry(self.info_frame, placeholder_text="Nhập tài khoản giảng viên")
        self.user_entry.grid(row=1, column=1, sticky="ew", padx=15, pady=5)

        ctk.CTkLabel(self.info_frame, text="Mật khẩu:").grid(row=2, column=0, sticky="w", padx=15, pady=5)
        self.pass_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.pass_frame.grid(row=2, column=1, sticky="ew", padx=15, pady=5)
        self.pass_entry = ctk.CTkEntry(self.pass_frame, placeholder_text="Nhập mật khẩu", show="•")
        self.pass_entry.pack(side="left", fill="x", expand=True)
        self.btn_toggle_pass = ctk.CTkButton(self.pass_frame, text="👁", width=30, fg_color="gray", hover_color="gray40", command=self.toggle_password)
        self.btn_toggle_pass.pack(side="right", padx=(5, 0))

        ctk.CTkLabel(self.info_frame, text="Mã môn học:").grid(row=3, column=0, sticky="w", padx=15, pady=5)
        self.sub_entry = ctk.CTkEntry(self.info_frame, placeholder_text="Value môn học (VD: Kỹ năng số (1tc)/OK//93190/7481/KL24A))")
        self.sub_entry.grid(row=3, column=1, sticky="ew", padx=15, pady=5)

        ctk.CTkLabel(self.info_frame, text="File điểm:").grid(row=4, column=0, sticky="w", padx=15, pady=5)
        self.file_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.file_frame.grid(row=4, column=1, sticky="ew", padx=15, pady=5)
        self.file_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Vui lòng chọn file...", state="disabled")
        self.file_entry.pack(side="left", fill="x", expand=True)
        
        # Nút Download Template sử dụng hàm resource_path
        self.btn_template = ctk.CTkButton(self.file_frame, text="⬇ Mẫu", width=60, fg_color="#555555", hover_color="#333333", command=self.download_template)
        self.btn_template.pack(side="right", padx=(5, 0))
        self.btn_browse = ctk.CTkButton(self.file_frame, text="📂 Chọn", width=60, command=self.browse_file)
        self.btn_browse.pack(side="right", padx=(10, 0))

        self.cols_frame = ctk.CTkFrame(self.body_frame)
        self.cols_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        ctk.CTkLabel(self.cols_frame, text="CỘT ĐIỂM CẦN THAO TÁC", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=10)
        self.mode_var = ctk.StringVar(value="default")
        self.radio_frame = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.radio_frame.pack(fill="x", padx=15)
        ctk.CTkRadioButton(self.radio_frame, text="Mặc định", variable=self.mode_var, value="default", command=self.refresh_checkbox_area).pack(side="left", padx=10)
        ctk.CTkRadioButton(self.radio_frame, text="Tùy chọn", variable=self.mode_var, value="custom", command=self.refresh_checkbox_area).pack(side="left", padx=20)
        self.chk_container = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.chk_container.pack(fill="x", padx=15, pady=10)
        self.checkbox_vars = {} 
        self.refresh_checkbox_area()

        self.action_frame = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)
        self.btn_import = ctk.CTkButton(self.action_frame, text="📥 NHẬP ĐIỂM", height=50, font=ctk.CTkFont(size=15, weight="bold"), fg_color="#009933", hover_color="#007722", command=lambda: self.start_thread(is_delete=False))
        self.btn_import.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.btn_delete = ctk.CTkButton(self.action_frame, text="🗑 XÓA ĐIỂM", height=50, font=ctk.CTkFont(size=15, weight="bold"), fg_color="#CC0000", hover_color="#990000", command=lambda: self.start_thread(is_delete=True))
        self.btn_delete.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.status_label = ctk.CTkLabel(self.body_frame, text="Sẵn sàng...", text_color="gray")
        self.status_label.grid(row=3, column=0, pady=5)

    def toggle_password(self):
        if self.pass_entry.cget("show") == "•":
            self.pass_entry.configure(show="")
            self.btn_toggle_pass.configure(text="🔒")
        else:
            self.pass_entry.configure(show="•")
            self.btn_toggle_pass.configure(text="👁")

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if filename:
            self.file_entry.configure(state="normal")
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)
            self.file_entry.configure(state="disabled")

    def download_template(self):
        # --- ĐÂY LÀ PHẦN QUAN TRỌNG ĐỂ TÌM FILE TRONG EXE ---
        # Sử dụng hàm resource_path đã định nghĩa ở đầu
        source_file = resource_path("template.xlsx")
        
        if not os.path.exists(source_file):
            messagebox.showerror("Lỗi File", f"Không tìm thấy file mẫu trong hệ thống!\nĐường dẫn: {source_file}")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], initialfile="Mau_Nhap_Diem_UDA.xlsx", title="Lưu file mẫu Excel")

        if save_path:
            try:
                shutil.copy(source_file, save_path)
                messagebox.showinfo("Thành công", f"Đã lưu file mẫu tại:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

    def refresh_checkbox_area(self):
        for widget in self.chk_container.winfo_children(): widget.destroy()
        self.checkbox_vars.clear()
        mode = self.mode_var.get()
        titles = DEFAULT_TITLES if mode == "default" else ALL_TITLES
        state = "disabled" if mode == "default" else "normal"
        default_val = True if mode == "default" else False
        for idx, title in enumerate(titles):
            var = ctk.BooleanVar(value=default_val)
            chk = ctk.CTkCheckBox(self.chk_container, text=title, variable=var, state=state)
            chk.grid(row=idx // 4, column=idx % 4, sticky="w", padx=10, pady=8)
            self.checkbox_vars[title] = var

    def update_status(self, text):
        self.status_label.configure(text=text)
        self.update_idletasks()

    def set_buttons_state(self, state):
        for btn in [self.btn_import, self.btn_delete, self.btn_browse, self.btn_template]:
            btn.configure(state=state)

    def start_thread(self, is_delete):
        if is_delete and not messagebox.askyesno("Xác nhận", "Bạn chắc chắn muốn XÓA điểm?"): return
        threading.Thread(target=self.run_process, args=(is_delete,), daemon=True).start()

    def run_process(self, is_delete):
        info = [self.user_entry.get(), self.pass_entry.get(), self.sub_entry.get(), self.file_entry.get()]
        if not all(info): return messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin!")
        if not os.path.exists(info[3]): return messagebox.showerror("Lỗi", "File không tồn tại!")
        
        selected = [t for t, v in self.checkbox_vars.items() if v.get()]
        if not selected: return messagebox.showwarning("Lỗi", "Chưa chọn cột điểm!")

        self.set_buttons_state("disabled")
        try:
            run_tool(*info, selected, self.update_status, is_delete_mode=is_delete)
        finally:
            self.set_buttons_state("normal")
            self.update_status("Sẵn sàng.")

if __name__ == "__main__":
    app = App()
    app.mainloop()