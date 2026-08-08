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

# TEST MESSAGE
send_telegram("Pukkelpop bot test successful")

for camping_type, url in URLS.items():

    html = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    ).text

    if "No tickets available." in html:
        print(f"NO TICKETS ({camping_type})")

    else:
        alert_message = (
            "PUKKELPOP SATURDAY TICKET FOUND\n\n"
            f"Camping option: {camping_type}\n\n"
            f"{url}"
        )

        print(alert_message)

        for i in range(5):
            send_telegram(alert_message)
