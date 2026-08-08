import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URLS = {
    "Camping CHILL": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=a&price=all#tickets",
    "Camping RELAX": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=b&price=all#tickets",
    "WITHOUT camping": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=n&price=all#tickets"
}

CHECK_INTERVAL_SECONDS = 60

previous_state = {}

def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False
        },
        timeout=15
    )

print("Saturday monitor started")

while True:

    for camping_type, url in URLS.items():

        try:

            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30
            )

            response.raise_for_status()

            html = response.text

        except Exception as e:

            print(f"ERROR ({camping_type}): {e}")
            continue

        ticket_found = "No tickets available." not in html

        if camping_type not in previous_state:
            previous_state[camping_type] = ticket_found

        if ticket_found and not previous_state[camping_type]:

            message = (
                "🚨🚨🚨 PUKKELPOP SATURDAY TICKET FOUND 🚨🚨🚨\n\n"
                f"Camping option: {camping_type}\n\n"
                f"{url}"
            )

            for i in range(5):
                send_telegram(message)

        previous_state[camping_type] = ticket_found

        print(
            f"{camping_type}: "
            f"{'TICKET FOUND' if ticket_found else 'NO TICKETS'}"
        )

    time.sleep(CHECK_INTERVAL_SECONDS)
