import os
import requests

TOKEN = os.getenv("SISTER_TELEGRAM_TOKEN")
CHAT_ID = os.getenv("SISTER_TELEGRAM_CHAT_ID")

print("TOKEN FOUND:", TOKEN is not None)
print("CHAT_ID FOUND:", CHAT_ID is not None)

URLS = {
    "Camping CHILL": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=a&price=all#tickets",
    "Camping RELAX": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=b&price=all#tickets",
    "WITHOUT camping": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=n&price=all#tickets"
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

    print("Telegram status:", response.status_code)
    print(response.text)

# TEST MESSAGE
send_telegram("✅ SUNDAY BOT TEST")

for camping_type, url in URLS.items():

    try:
        html = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        ).text

    except Exception as e:
        print(f"ERROR ({camping_type}): {e}")
        continue

    if "No tickets available." in html:

        print(f"NO TICKETS ({camping_type})")

    else:

        alert_message = f"""
🚨🚨🚨 PUKKELPOP SUNDAY TICKET FOUND 🚨🚨🚨

Camping option:
{camping_type}

Open immediately:

{url}
"""

        print(alert_message)

        for i in range(5):
            send_telegram(alert_message)
