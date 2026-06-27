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