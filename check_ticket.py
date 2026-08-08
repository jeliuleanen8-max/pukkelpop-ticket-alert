import requests
URLS = [
    "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=a&price=all#tickets",
    "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=b&price=all#tickets",
    "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=n&price=all#tickets",
]
for url in URLS:
    html = requests.get(url).text
    if "No tickets available." in html:
        print(f"NO TICKETS: {url}")
    else:
        print(f"POSSIBLE TICKET FOUND: {url}")
