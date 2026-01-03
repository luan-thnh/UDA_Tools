#!/usr/bin/env python3
import schedule
import time
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CẤU HÌNH ---
BASE_URL = "https://hrm.donga.edu.vn"
LOGIN_URL = f"{BASE_URL}/nhan-vien/dang-nhap"
TASK_URL = f"{BASE_URL}/social/home/congviecngay"

USERNAME = "luanlt@donga.edu.vn"
PASSWORD = "uda.33xvnt"
WAIT_TIMEOUT = 15  # Tăng timeout cho ổn định

# Selectors
USERNAME_INPUT = (By.ID, "username")
PASSWORD_INPUT = (By.ID, "password")
LOGIN_BUTTON = (By.XPATH, '//*[@id="form"]/button')
FORM_TASK_BUTTON = (By.XPATH, '//*[@id="bscv"]/div/div/div/div[2]/div/button')
TASK_INPUT = (By.ID, "congviec")
DATE_INPUT = (By.ID, "thoigian")
DETAIL_INPUT_IFRAME = (By.CSS_SELECTOR, "iframe[title='Bộ soạn thảo văn bản có định dạng, baocao']")
SAVE_BUTTON = (By.CSS_SELECTOR, "input[value='Lưu']")

# --- LOGGING ---
LOG_DIR = "/home/luanthnh/Public/Workspaces/me/tools/hrm/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"hrm_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(message)s', '%H:%M:%S'))
logging.getLogger().addHandler(console)

# --- HÀM CHÍNH ---
def open_website():
    logging.info("="*60)
    logging.info("BẮT ĐẦU TÁC VỤ TỰ ĐỘNG HRM")
    logging.info(f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    date_str = datetime.now().strftime('%d/%m/%Y')
    driver = None

    try:
        # Cấu hình Chrome (Thorium) - Headless
        options = webdriver.ChromeOptions()
        options.binary_location = "/opt/chromium.org/thorium/thorium-browser"
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Tự động tải ChromeDriver phù hợp
        service = Service(ChromeDriverManager(driver_version="130.0.6723.69").install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

        # 1. Đăng nhập
        logging.info("Truy cập trang đăng nhập...")
        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located(USERNAME_INPUT)).send_keys(USERNAME)
        driver.find_element(*PASSWORD_INPUT).send_keys(PASSWORD)
        driver.find_element(*LOGIN_BUTTON).click()
        logging.info("Đã gửi thông tin đăng nhập.")

        # Chờ chuyển hướng sau login
        wait.until(EC.url_contains("/social/home"))
        logging.info("Đăng nhập thành công.")

        # 2. Mở trang công việc
        driver.get(TASK_URL)
        logging.info("Đã mở trang công việc ngày.")

        # 3. Mở form
        wait.until(EC.element_to_be_clickable(FORM_TASK_BUTTON)).click()
        logging.info("Đã mở form nhập công việc.")

        # 4. Điền dữ liệu
        wait.until(EC.presence_of_element_located(TASK_INPUT)).send_keys("Soạn nội dung thực hành")
        driver.find_element(*DATE_INPUT).clear()
        driver.find_element(*DATE_INPUT).send_keys(date_str)
        logging.info(f"Đã điền ngày: {date_str}")

        # 5. Điền chi tiết trong iframe
        iframe = wait.until(EC.presence_of_element_located(DETAIL_INPUT_IFRAME))
        driver.switch_to.frame(iframe)
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        body.clear()
        body.send_keys("Soạn nội dung thực hành môn reactjs")
        driver.switch_to.default_content()
        logging.info("Đã điền nội dung chi tiết.")

        # 6. Lưu
        save_btn = wait.until(EC.element_to_be_clickable(SAVE_BUTTON))
        driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
        time.sleep(1)
        save_btn.click()
        logging.info("ĐÃ LƯU THÀNH CÔNG công việc ngày hôm nay!")

        # Chờ xác nhận lưu
        time.sleep(3)

    except Exception as e:
        logging.error(f"LỖI: {str(e)}")
        if driver:
            screenshot_path = os.path.join(LOG_DIR, f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            try:
                driver.save_screenshot(screenshot_path)
                logging.info(f"Đã chụp màn hình lỗi: {screenshot_path}")
            except:
                pass
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        logging.info("ĐÃ ĐÓNG TRÌNH DUYỆT.")
        logging.info(f"KẾT THÚC TÁC VỤ - {datetime.now().strftime('%H:%M:%S')}")
        logging.info("="*60 + "\n")

# --- CHẠY NGAY (khi chạy thủ công) ---
if __name__ == "__main__":
    open_website()