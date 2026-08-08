import os
import requests
 
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
 
URLS = {
    "Camping CHILL": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=a&price=all#tickets",
    "Camping RELAX": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=b&price=all#tickets",
    "WITHOUT camping": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=n&price=all#tickets"
}
 
 
def send_telegram(message):
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False
        },
        timeout=15
    )
 
    print(f"Telegram status: {response.status_code}")
    print(response.text)
 
 
# ----------------------------------------------------
# TEST MESSAGE
# Remove this block after the first successful test
# ----------------------------------------------------
 
send_telegram("✅ Pukkelpop bot test successful")
 
# ----------------------------------------------------
# TICKET CHECK
# ----------------------------------------------------
 
for camping_type, url in URLS.items():
 
    html = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=15
    ).text
 
    if "No tickets available." in html:
 
        print(f"NO TICKETS ({camping_type})")
 
    else:
 
        alert_message = f"""
🚨🚨🚨 PUKKELPOP SATURDAY TICKET FOUND 🚨🚨🚨
 
Camping option:
{camping_type}
 
Open immediately:
 
{url}
"""
 
        print(alert_message)
 
        # Send multiple notifications
        for _ in range(3):
            send_telegram(alert_message)
