from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.alert import Alert
import time

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def close_alert():
    try:
        alert = Alert(driver)
        alert.accept()
    except:
        pass

# الخطوة 1 — افتح الموقع
driver.get("https://booking.privilegetours.net/")
time.sleep(2)
close_alert()
time.sleep(2)

# الخطوة 2 — سجّل دخول
try:
    email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    email.send_keys("betouristtravel@gmail.com")
    time.sleep(1)
    password = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    password.send_keys("AutoPass5613")
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    close_alert()
    print("Logged in!")
except Exception as e:
    print("Login error:", e)

# الخطوة 3 — روح لصفحة البرامج
driver.get("https://booking.privilegetours.net/programmes_details.php")
time.sleep(3)
close_alert()
time.sleep(2)

# الخطوة 4 — جيب البيانات
try:
    rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
    for row in rows:
        print(row.text)
except Exception as e:
    print("Error:", e)

input("Press Enter to close...")
driver.quit()

