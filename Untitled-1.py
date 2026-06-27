import smtplib
import schedule
import time
from datetime import datetime

def send_email():
    day = datetime.now().weekday()
    if day in [4, 5]:
        print("اليوم عطلة، ما نرسلوش!")
        return

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login("betouristtravel@gmail.com", "ecxb qhus esoy kmci")

        subject = "Greeting"
        body = "How are you today, I'm just asking about you"
        message = f"Subject: {subject}\n\n{body}"

        server.sendmail("betouristtravel@gmail.com", "khiro.kade@gmail.com", message)
        server.quit()

        print("✅ الإيميل تبعث بنجاح!")

    except Exception as e:
        print("❌ خطأ:", e)

schedule.every().day.at("07:00").do(send_email)

print("البوت شغال وينتظر...")

while True:
    schedule.run_pending()
    time.sleep(60)

import pywhatkit
import time

phone = "+213549573865"
message = "Hello! This is an automatic message from Python!"

print("البوت شغال، راح يرسل 5 رسائل كل دقيقة!")

for i in range(5):
    print(f"إرسال الرسالة {i+1} من 5...")
    
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min + 1
    
    if minute >= 60:
        minute = 0
        hour += 1
    
    pywhatkit.sendwhatmsg(phone, f"Message {i+1}: {message}", hour, minute)
    
    print(f"✅ الرسالة {i+1} تبعثت!")
    time.sleep(60)

print("✅ كمّلنا! 5 رسائل تبعثو بنجاح!")
