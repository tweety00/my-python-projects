import smtplib
import schedule
import time
from datetime import datetime

def send_email():
    day = datetime.now().weekday()
    if day in [4, 5]:
        print("Holiday, no email sent!")
        return

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("betouristtravel@gmail.com", "your_app_password")

        subject = "Greeting"
        body = "How are you today, I'm just asking about you"
        message = f"Subject: {subject}\n\n{body}"

        server.sendmail("betouristtravel@gmail.com", "khiro.kade@gmail.com", message)
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print("Error:", e)

schedule.every().day.at("07:00").do(send_email)
print("Bot is running...")

while True:
    schedule.run_pending()
    time.sleep(60)