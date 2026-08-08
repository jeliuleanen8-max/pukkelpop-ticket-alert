import os
import time
import re
import html as html_module
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
    LOCAL_TIMEZONE = ZoneInfo("Europe/Brussels")
except Exception:
    LOCAL_TIMEZONE = None

import requests

TOKEN = os.getenv("SISTER_TELEGRAM_TOKEN")
CHAT_ID = os.getenv("SISTER_TELEGRAM_CHAT_ID")

CHECK_INTERVAL_SECONDS = 60
RECAP_INTERVAL_SECONDS = 5 * 60 * 60
HISTORY_WINDOW_SECONDS = 5 * 60 * 60

TARGETS = [
    {
        "ticket_type": "Saturday",
        "camping": "Camping CHILL",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=a&price=all#tickets"
    },
    {
        "ticket_type": "Saturday",
        "camping": "Camping RELAX",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=b&price=all#tickets"
    },
    {
        "ticket_type": "Saturday",
        "camping": "WITHOUT camping",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=n&price=all#tickets"
    },
    {
        "ticket_type": "Sunday",
        "camping": "Camping CHILL",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=a&price=all#tickets"
    },
    {
        "ticket_type": "Sunday",
        "camping": "Camping RELAX",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=b&price=all#tickets"
    },
    {
        "ticket_type": "Sunday",
        "camping": "WITHOUT camping",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day3&camping=n&price=all#tickets"
    },
    {
        "ticket_type": "Combi",
        "camping": "Camping CHILL",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=combi&camping=a&price=all#tickets"
    },
    {
        "ticket_type": "Combi",
        "camping": "Camping RELAX",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=combi&camping=b&price=all#tickets"
    },
    {
        "ticket_type": "Combi",
        "camping": "WITHOUT camping",
        "url": "https://tickets.pukkelpop.be/en/meetup/demand/?type=combi&camping=n&price=all#tickets"
    }
]

history = []
previous_prices_by_target = {}
last_recap_time = time.time()


def now_local():
    if LOCAL_TIMEZONE is not None:
        return datetime.now(LOCAL_TIMEZONE)

    return datetime.now()


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


def extract_ticket_section(page_html):
    decoded = html_module.unescape(page_html)

    if "Available tickets" in decoded:
        return decoded.split("Available tickets", 1)[1]

    return decoded


def extract_prices(ticket_section):
    prices = re.findall(
        r"€\s*\d+(?:[.,]\d{1,2})?",
        ticket_section
    )

    if prices:
        return normalize_price_list(prices)

    prices_alt = re.findall(
        r"EUR\s*\d+(?:[.,]\d{1,2})?",
        ticket_section,
        re.IGNORECASE
    )

    if prices_alt:
        return normalize_price_list(prices_alt)

    return []


def normalize_price_list(prices):
    normalized = []

    for price in prices:
        cleaned = price.strip()
        cleaned = cleaned.replace("EUR", "€")
        cleaned = cleaned.replace("eur", "€")
        cleaned = re.sub(r"\s+", " ", cleaned)

        if cleaned not in normalized:
            normalized.append(cleaned)

    return normalized


def price_to_number(price_text):
    cleaned = price_text.upper()
    cleaned = cleaned.replace("EUR", "")
    cleaned = cleaned.replace("€", "")
    cleaned = cleaned.replace(" ", "")
    cleaned = cleaned.replace(",", ".")

    match = re.search(r"\d+(?:\.\d+)?", cleaned)

    if not match:
        return None

    return float(match.group())


def fetch_page(url):
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    return response.text


def cleanup_old_history():
    global history

    cutoff = now_local() - timedelta(seconds=HISTORY_WINDOW_SECONDS)

    history = [
        item for item in history
        if item["seen_at"] >= cutoff
    ]


def add_sighting(ticket_type, camping, price_text, url):
    seen_at = now_local()
    price_number = price_to_number(price_text)

    history.append(
        {
            "seen_at": seen_at,
            "ticket_type": ticket_type,
            "camping": camping,
            "price_text": price_text,
            "price_number": price_number,
            "url": url
        }
    )

    print(
        "Added sighting: "
        f"{ticket_type} | {camping} | {price_text} | "
        f"{seen_at.strftime('%H:%M:%S')}"
    )


def format_average(ticket_type):
    values = [
        item["price_number"]
        for item in history
        if item["ticket_type"] == ticket_type
        and item["price_number"] is not None
    ]

    if not values:
        return "No price data"

    avg = sum(values) / len(values)

    return f"€{avg:.2f}"


def format_section(ticket_type):
    items = [
        item for item in history
        if item["ticket_type"] == ticket_type
    ]

    if not items:
        return (
            f"{ticket_type}\n"
            f"Average: No price data\n"
            f"Count: 0\n"
            f"No sightings in the last 5 hours.\n"
        )

    lines = []
    lines.append(ticket_type)
    lines.append(f"Average: {format_average(ticket_type)}")
    lines.append(f"Count: {len(items)}")
    lines.append("Sightings:")

    for item in items:
        lines.append(
            f"- {item['seen_at'].strftime('%H:%M')} | "
            f"{item['camping']} | {item['price_text']}"
        )

    return "\n".join(lines) + "\n"


def send_recap():
    cleanup_old_history()

    total_count = len(history)

    message = (
        "📊 PUKKELPOP PRICE RECAP\n"
        "Last 5 hours\n\n"
        f"Total sightings: {total_count}\n\n"
        f"{format_section('Saturday')}\n"
        f"{format_section('Sunday')}\n"
        f"{format_section('Combi')}\n"
    )

    send_telegram(message)


def process_target(target):
    ticket_type = target["ticket_type"]
    camping = target["camping"]
    url = target["url"]

    target_key = f"{ticket_type}|{camping}"

    try:
        page_html = fetch_page(url)

    except Exception as e:
        print(f"ERROR ({ticket_type} | {camping}): {e}")
        return

    ticket_section = extract_ticket_section(page_html)

    ticket_found = "No tickets available." not in ticket_section

    if not ticket_found:
        print(f"{ticket_type} | {camping}: NO TICKETS")
        previous_prices_by_target[target_key] = set()
        return

    prices = extract_prices(ticket_section)

    if not prices:
        print(f"{ticket_type} | {camping}: TICKET FOUND, PRICE NOT FOUND")
        print("TICKET SECTION PREVIEW:")
        print(ticket_section[:2000])

        previous_prices = previous_prices_by_target.get(target_key, set())

        if "Price not found" not in previous_prices:
            add_sighting(
                ticket_type=ticket_type,
                camping=camping,
                price_text="Price not found",
                url=url
            )

        previous_prices_by_target[target_key] = {"Price not found"}
        return

    current_prices = set(prices)
    previous_prices = previous_prices_by_target.get(target_key, set())

    new_prices = current_prices - previous_prices

    if new_prices:
        print(
            f"{ticket_type} | {camping}: NEW PRICE(S) FOUND | "
            f"{', '.join(sorted(new_prices))}"
        )

        for price in sorted(new_prices):
            add_sighting(
                ticket_type=ticket_type,
                camping=camping,
                price_text=price,
                url=url
            )

    else:
        print(
            f"{ticket_type} | {camping}: TICKET STILL AVAILABLE | "
            f"Prices unchanged: {', '.join(prices)}"
        )

    previous_prices_by_target[target_key] = current_prices


print("Recap monitor started")

send_telegram("📊 Pukkelpop recap monitor started")

while True:

    cleanup_old_history()

    for target in TARGETS:
        process_target(target)

    current_time = time.time()

    if current_time - last_recap_time >= RECAP_INTERVAL_SECONDS:
        send_recap()
        last_recap_time = current_time

    time.sleep(CHECK_INTERVAL_SECONDS)
