#!/usr/bin/env python3
"""Second batch: try alternative naming patterns and cubelin uploader."""
import urllib.request, ssl, concurrent.futures

ctx = ssl.create_default_context()

candidates = []

# Try cubelin uploader for Amex cards  
cubelin_names = [
    "AMEXBizGold", "AMEXCenturion", "AMEXCenturion2", "AMEXPlatinum",
    "AMEXGold", "AMEXGreen", "AMEXBlack", "AMEXCobalt",
    "AMEXDeltaGold", "AMEXDeltaReserve", "AMEXHiltonAspire",
    "AMEXBlueCashPreferred", "AMEXBlueCashEveryday", "AMEXEverydayPreferred",
    "AMEXCashMagnet", "AMEXMarriottBonvoyBusiness", "AMEXBlueBizCash",
    "amexcenturioncard", "amexblackcard",
]
for n in cubelin_names:
    candidates.append(("cubelin", n, f"https://u.cubeupload.com/cubelin/{n}.png"))

# Try ccbackground with more patterns for Centurion
centurion_patterns = [
    "amexcenturioncard", "amexblackcard", "amexcent", "centurion",
    "amexcenturionpersona", "amexcenturionperson", "amexcenturioncardap",
    "amexgoldcard", "amexgoldnew", "amexplatinumnew", "amexplat2", "amexplat2023",
    "amexpersonalcenturio", "amexbuscenturion", "amexblue", 
    "amexhiltonaspirecard", "amexaspire", "amexhiltonaspirecrd",
    "amexdeltareserve", "amexdeltagold", "amexdeltaskymilesgol", "amexdeltaskymilesres",
    "amexdeltaskymilesgol", "amexdeltareservecard",
    "amexbluecashpreferred", "amexbluecashprefer",
    "amexbluecasheveryday", "amexbluecashevery",
    "amexeverydaypref", "amexeverydaypreferred", "amexeverydaypreferr",
    "amexcashmagnet", "amexcash",
    "amexmarriottbonvoybu", "amexmarriottbonvoybi",
]
for n in centurion_patterns:
    candidates.append(("ccbackground", n, f"https://u.cubeupload.com/ccbackground/{n}.png"))

# Chase extras
chase_extras = [
    "chaseunitedquest", "chaseunitedclub", "chaseunitedclubbiz", "chaseunitedclubinfi",
    "chasesouthwest", "chasesouthwestplus", "chasesouthwestpriori",
    "chasesapphire", "chasedisneyvisa", "chasedisneypremier",
    "chaseihg", "chaseihgonerewards", "chaseihgpremier", "chaseihgpremiercard",
    "chaseinkbusiness", "chaseinkunlimitedcar",
    "chaseaeroplan", "chaseaeroplancard", "chaseba", "chasebritish",
    "chaseslate", "chaseslateedge", "chasechecking",
    "chasefreedomrise", "chasefreedomrisecred",
    "chasefreedomstudent",
]
for n in chase_extras:
    candidates.append(("ccbackground", n, f"https://u.cubeupload.com/ccbackground/{n}.png"))

# Capital One extras
cap1_extras = [
    "venture", "ventureone", "venturex", "capitaloneventure", "capitalonesavor",
    "capitalonesavorone", "capitaloneventurex", "capitaloneventureone",
    "capitalonequicksilve", "capitaloneplatinum", "capitalonewalmart",
    "cap1venture", "cap1venturex", "cap1savorone",
]
for n in cap1_extras:
    candidates.append(("ccbackground", n, f"https://u.cubeupload.com/ccbackground/{n}.png"))

# Citi extras
citi_extras = [
    "citicustomcash", "citicustomcashcard", "citistrata", "citistratapremier",
    "citiaaplatselect", "citiaamileup", "citiaaplat", "citiaaexec",
    "citidiamond", "citicostco", "citicostcoanywhere", "citiprestige",
    "citiaaadvantage", "citiaaadvantageexec", "citiaaadvantageexecu",
    "citiaaadvantageworld", "citirewardsplus",
]
for n in citi_extras:
    candidates.append(("ccbackground", n, f"https://u.cubeupload.com/ccbackground/{n}.png"))

# Discover, WF, BoA, USB, Barclays, Bilt
others = [
    "discoverit", "discovercashback", "discoveritcashback", "discovermiles",
    "wellsfargoactivecash", "wellsfargoreflect", "wellsfargoautograph",
    "boacustomizedcash", "boatravelrewards", "boaalaska", "boatravel",
    "usbankaltitudeconnec", "usbankcash", "usbaltitude",
    "barclaysaviator", "barclaysjetblue", "barclayschoice",
    "bilt", "biltrewards", "biltmastercard",
    "venmo", "venmocard", "venmocredit",
    "sofi", "soficredit",
    "paypal", "paypalcashback",
    "goldman", "goldmansachs",
]
for n in others:
    candidates.append(("ccbackground", n, f"https://u.cubeupload.com/ccbackground/{n}.png"))

def check_url(item):
    uploader, name, url = item
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        return (uploader, name, url, resp.getcode())
    except:
        return (uploader, name, url, 0)

print("Probing batch 2...")
found = []
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as exe:
    for r in exe.map(check_url, candidates):
        if r[3] == 200:
            found.append(r)
            print(f"  OK  {r[0]}/{r[1]}.png")

print(f"\n=== FOUND: {len(found)} additional cards ===")
for r in found:
    print(f"  {r[2]}")
