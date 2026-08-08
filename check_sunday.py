import os
import time
import re
import html as html_module
import requests

TOKEN = os.getenv("SISTER_TELEGRAM_TOKEN")
CHAT_ID = os.getenv("SISTER_TELEGRAM_CHAT_ID")

URLS = {
    "Camping CHILL": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=a&price=all#tickets",
    "Camping RELAX": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=b&price=all#tickets",
    "WITHOUT camping": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=n&price=all#tickets"
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


def extract_ticket_section(page_html):

    decoded = html_module.unescape(page_html)

    if "Available tickets" in decoded:
        return decoded.split("Available tickets", 1)[1]

    return decoded


def extract_price(ticket_section):

    prices = re.findall(
        r"€\s*\d+(?:[.,]\d{1,2})?",
        ticket_section
    )

    if prices:
        return prices[0]

    prices_alt = re.findall(
        r"EUR\s*\d+(?:[.,]\d{1,2})?",
        ticket_section,
        re.IGNORECASE
    )

    if prices_alt:
        return prices_alt[0]

    return "Price not found"


print("Sunday monitor started")

while True:

    for camping_type, url in URLS.items():

        try:

            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30
            )

            response.raise_for_status()

            page_html = response.text

        except Exception as e:

            print(f"ERROR ({camping_type}): {e}")
            continue

        ticket_section = extract_ticket_section(page_html)

        ticket_found = (
            "No tickets available." not in ticket_section
        )

        price = extract_price(ticket_section)

        if camping_type not in previous_state:
            previous_state[camping_type] = ticket_found

        if ticket_found:

            print("TICKET SECTION PREVIEW:")
            print(ticket_section[:2000])

        if ticket_found and not previous_state[camping_type]:

            message = (
                "🚨🚨🚨 PUKKELPOP SUNDAY TICKET FOUND 🚨🚨🚨\n\n"
                f"Camping option: {camping_type}\n"
                f"Price: {price}\n\n"
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
