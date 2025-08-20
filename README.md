# DXWorld2HamAlert

- Scrape the DXWorld monthly timeline for dxpeditions. 
- Extract the callsigns compare with existing Hamalert triggers.
- If new callsign create new rule
- Delete last months rules

You just need to run this once a month, use a suitable chron agent or windows task scheduler to fully automate your DX hunts!

## Install

### Linux / OSX
```
git clone https://github.com/868meshbot/DXWorld2HamAlert
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
### Windows
```
git clone https://github.com/868meshbot/DXWorld2HamAlert
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```
 ➜  python ./DX2HamAlert.py -u username -p 'password'
________  ____  _____      __            .__       .___ ________
\______ \ \   \/  /  \    /  \___________|  |    __| _/ \_____  \
 |    |  \ \     /\   \/\/   /  _ \_  __ \  |   / __ |   /  ____/
 |    `   \/     \ \        (  <_> )  | \/  |__/ /_/ |  /       \
/_______  /___/\  \ \__/\  / \____/|__|  |____/\____ |  \_______ \
        \/      \_/      \/                         \/          \/
  ___ ___                    _____  .__                 __
 /   |   \_____    _____    /  _  \ |  |   ____________/  |_
/    ~    \__  \  /     \  /  /_\  \|  | _/ __ \_  __ \   __\
\    Y    // __ \|  Y Y  \/    |    \  |_\  ___/|  | \/|  |
 \___|_  /(____  /__|_|  /\____|__  /____/\___  >__|   |__|
       \/      \/      \/         \/          \/

DXWorld->Hamalert Importer script
Version 0.1 (c)2025 868Meshbot

This script will import call-sign triggers from DXWorld into HamAlert.
It logs into the site, posts trigger update requests for each callsign, and
prints friendly status updates so you can quickly see which callsigns were
accepted and which require attention.

[+] Found 50 existing records.
[+] Found 0 previous records from last month.
[+] FOUND: Call Signs: 12
[!] Removing any duplicates...
[+] NEW: Call Signs: 12
[+] T88GF & T88XD
[+] TY2AA
[+] E51KEE
[+] 3G1P
[+] 5H1UM
[+] YJ0CA
[+] K9HEI
[+] OJ0MN
[+] KT8X
[+] OG0C
[+] SP9FIH
[+] T30TTT
# Spinning up HamAlert...
[+] T88GF & T88XD ✔
[+] TY2AA ✔
[+] E51KEE ✔
[+] 3G1P ✔
[+] 5H1UM ✔
[+] YJ0CA ✔
[+] K9HEI ✔
[+] OJ0MN ✔
[+] KT8X ✔
[+] OG0C ✔
[+] SP9FIH ✔
[+] T30TTT ✔
```
