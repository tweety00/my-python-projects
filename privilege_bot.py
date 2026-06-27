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

# افتح الموقع
driver.get("https://booking.privilegetours.net/")
time.sleep(2)

# أغلق الـ Alert
try:
    alert = Alert(driver)
    alert.accept()
except:
    pass

time.sleep(2)

# ابحث عن خانة الإيميل وكلمة السر
try:
    email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    email.send_keys("betouristtravel@gmail.com")
    time.sleep(1)
    
    password = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    password.send_keys("AutoPass5613")
    time.sleep(1)
    
    # كلك على Login
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    
    print("Logged in!")
except Exception as e:
    print("Error:", e)

input("Press Enter to close...")
driver.quit()