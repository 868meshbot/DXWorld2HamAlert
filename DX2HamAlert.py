"""
DXWorld --> HamAlert Importer script
(c)2025 868Meshbot
"""

import argparse
import datetime
import re

import httpx
import pyfiglet
import requests
from dateutil.relativedelta import relativedelta

DEBUG = 0

CSI = "\033["
RESET = CSI + "0m"
BOLD = CSI + "1m"
GREEN = CSI + "32m"
YELLOW = CSI + "33m"
RED = CSI + "31m"
CYAN = CSI + "36m"
MAGENTA = CSI + "35m"


login_url = "https://hamalert.org/login"
triggers_url = "https://hamalert.org/ajax/triggers"
update_url = "https://hamalert.org/ajax/trigger_update"
delete_url = "https://hamalert.org/ajax/trigger_delete"
dxworld_url = "https://www.hamradiotimeline.com/timeline/dxw_timeline_1_1.php"

current_date = datetime.datetime.now()
last_month_date = current_date - relativedelta(months=1)
last_month = last_month_date.strftime("%B %Y")
last_update = current_date.strftime("%B %Y")


def figlet_header(text):
    # Try pyfiglet if available for a fancier header
    try:
        f = pyfiglet.Figlet(font="graffiti")
        return f.renderText(text)
    except Exception:
        # fallback simple ASCII (keeps layout predictable)
        return "DXWorld 2 Hamalert"


def print_header():
    print(CYAN + figlet_header("DXWorld 2 HamAlert") + RESET)
    print(BOLD + "DXWorld->Hamalert Importer script" + RESET)
    print("Version 0.1 (c)2025 868Meshbot\n")
    print(
        """This script will import call-sign triggers from DXWorld into HamAlert.
It logs into the site, posts trigger update requests for each callsign, and
prints friendly status updates so you can quickly see which callsigns were
accepted and which require attention."""
    )
    print()


# Function to clean and extract callsigns
def clean_callsign(call_sign):
    # Remove everything before and including the first slash (e.g., FP/M0ABC -> M0ABC, TJ/M0ABC -> M0ABC)
    if "/" in call_sign:
        call_sign = call_sign.split("/")[1]  # Keep part after the first '/'

    # Ensure the callsign is valid (3 or more characters)
    if len(call_sign) >= 3:
        return call_sign
    return None  # Invalid callsign


headers_before = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://hamalert.org",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://hamalert.org/login",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
}

headers_trigger = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://hamalert.org",
    "referer": "https://hamalert.org/triggers",
    "x-requested-with": "XMLHttpRequest",
}

params = {
    "_": "1755547001215",
}

# Start
print_header()

parser = argparse.ArgumentParser(description="Login and grab Hamalert cookie")
parser.add_argument("-u", "--username", required=True, help="Username")
parser.add_argument("-p", "--password", required=True, help="Password")
args = parser.parse_args()

creds = {"username": args.username, "password": args.password}
# Perform login and validate PHPSESSID
try:
    response = requests.post(login_url, headers=headers_before, data=creds)
    if DEBUG:
        print(response.headers)
except:
    print(RED + "[!] No internet connection" + RESET)
    exit(0)

try:

    with httpx.Client(http2=True) as client:
        response = client.post(login_url, data=creds)

        # Extract Set-Cookie header
        set_cookie = response.headers.get("set-cookie")

        # Parse cookie key=value
        cookie_value = set_cookie.split(";")[0]

        cookie_name, cookie_value = cookie_value.split("=", 1)
        cookies = {cookie_name: cookie_value}

        if DEBUG:
            print("Raw Set-Cookie:", set_cookie)
            print("Parsed cookie:", cookie_value)
            print("Cookie dict:", cookies)

except Exception as e:
    print("Error: No Cookie... " + str(e))
    # exit(0)

# Get user_id and any existing hamalerts
try:
    response = requests.get(
        triggers_url,
        params=params,
        cookies=cookies,
        headers=headers_before,
    )
except Exception as e:
    print("[!]Error: " + str(e))

try:
    data = response.json()
except Exception as e:
    print(RED + "[!]Error: " + str(e) + RESET)
    print(response.status_code)
    print(response.text)

# Extract user_id from the first element (they're all the same anyway)
try:
    user_id = data[0]["user_id"]
except:
    print("No user id found")
    exit(0)
try:
    ids_last_month = [item["_id"] for item in data if item.get("comment") == last_month]
    ids_this_month = [
        item["_id"] for item in data if item.get("comment") == last_update
    ]
    prev_callsigns = [
        item["conditions"]["callsign"] for item in data if item.get("conditions", {})
    ]
    print("[+] Found " + str(len(ids_this_month)) + " existing records.")
    print(
        "[+] Found " + str(len(ids_last_month)) + " previous records from last month."
    )
except:
    print(RED + "[-] No existing hamalerts found. " + RESET)

if DEBUG:
    print("User ID:", user_id)
    print(str(len(prev_callsigns)))
    print(prev_callsigns)

# Fetch the webpage content of the dxworld timeline
response = requests.get(dxworld_url)


# Extract the call signs from the JavaScript code in the page
pattern = r"var labels = \[([^\]]+)\];"  # Regex to extract the labels array
match = re.search(pattern, response.text)

if match:
    # Get the part of the text containing the call signs (inside the array)
    raw_labels = match.group(1)

    # Clean the call signs and split them into a list
    callsigns = [clean_callsign(cs.strip().strip("'")) for cs in raw_labels.split(",")]

    # Filter out None values (invalid callsigns)
    callsigns = list(filter(None, callsigns))

    # Output the cleaned list of callsigns
    if len(prev_callsigns) > 0:
        print(YELLOW + "[+] FOUND: Call Signs: " + str(len(callsigns)) + RESET)
        print("[!] Removing any duplicates...")
        normalized_prev_callsigns = [
            " & ".join(c) if isinstance(c, list) else c for c in prev_callsigns
        ]
        callsigns = list(set(callsigns) - set(normalized_prev_callsigns))
    print(GREEN + "[+] NEW: Call Signs: " + str(len(callsigns)) + RESET)
    for callsign in callsigns:
        print("[+] " + callsign)

    # Loop through each callsign and generate the corresponding curl command
    current_date = datetime.datetime.now()
    last_update = current_date.strftime("%B %Y")

    if len(callsigns) > 0:
        print(GREEN + "# Spinning up HamAlert..." + RESET)

        for callsign in callsigns:
            # curl_command = curl_template.format(callsign=callsign, last_update=last_update)
            if "&" in callsign:
                calls = [c.strip() for c in callsign.split("&")]
            else:
                calls = callsign
            payload = {
                "user_id": user_id,
                "conditions": {
                    "callsign": calls,
                    "spotterDxcc": [
                        209,
                        223,
                        245,
                        114,
                        122,
                        265,
                        279,
                        294,
                    ],
                    "mode": ["ssb", "psk", "ft8", "ft4"],
                    "notSpotter": [
                        "2E0INH",
                        "G4IRN",
                        "GM4WJA",
                    ],
                    "band": [
                        "80m",
                        "60m",
                        "40m",
                        "30m",
                        "20m",
                        "17m",
                        "15m",
                        "12m",
                        "10m",
                    ],
                },
                "actions": ["app"],
                "comment": last_update,
                "matchCount": 0,
                "options": {},
            }
            response = requests.post(
                update_url,
                cookies=cookies,
                headers=headers_trigger,
                json=payload,
            )

            if response.status_code == 200:
                print(f"[+] {callsign} {GREEN}\u2714{RESET}")  # green tick ✔
            else:
                print(f"[+] {callsign} {RED}\u2718{RESET}")  # red cross ✘
else:
    print(
        RED + "ERROR: Something went wrong? Call signs not found in the page." + RESET
    )


if len(ids_last_month) > 0:

    print(RED + "[-] Deleting old records." + RESET)

    for id in ids_last_month:
        payload = f"id={id}"
        response = requests.post(
            delete_url,
            cookies=cookies,
            headers=headers,
            data=payload,
        )
        if DEBUG:
            if response.text.strip() == "true":
                print(f"[+] {id} {GREEN}\u2714{RESET}")  # green tick ✔
            else:
                print(f"[+] {id} {RED}\u2718{RESET}")

print(GREEN + "#Done!" + RESET)
