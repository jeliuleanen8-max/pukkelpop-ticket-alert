import requests

URLS = {
    "Camping CHILL": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=a&price=all#tickets",
    "Camping RELAX": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=b&price=all#tickets",
    "WITHOUT camping": "https://tickets.pukkelpop.be/en/meetup/demand/?type=day2&camping=n&price=all#tickets"
}

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
    print("")
    print("############################################")
    print(f"TICKET FOUND ({camping_type})")
    print(url)
    print("############################################")
    print("")
