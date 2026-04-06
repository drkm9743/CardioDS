#!/usr/bin/env python3
"""Probe cubeupload URLs to find which card images exist."""
import urllib.request
import ssl
import concurrent.futures

ctx = ssl.create_default_context()

# Candidate URLs based on the naming pattern observed
candidates = [
    # Amex Personal
    ("amexcenturion", "Centurion", "American Express", "US", "Amex"),
    ("amexcenturion2", "Centurion 2", "American Express", "US", "Amex"),
    ("amexblack", "Black Card", "American Express", "US", "Amex"),
    ("amexgold", "Gold Card", "American Express", "US", "Amex"),
    ("amexrosegold", "Rose Gold", "American Express", "US", "Amex"),
    ("amexplat", "Platinum", "American Express", "US", "Amex"),
    ("amexplatinum", "Platinum (alt)", "American Express", "US", "Amex"),
    ("amexgreen", "Green Card", "American Express", "US", "Amex"),
    ("amexeveryday", "EveryDay", "American Express", "US", "Amex"),
    ("amexeverydaypreferred", "EveryDay Preferred", "American Express", "US", "Amex"),
    ("amexbluecash", "Blue Cash", "American Express", "US", "Amex"),
    ("amexbluecasheveryday", "Blue Cash Everyday", "American Express", "US", "Amex"),
    ("amexbluecashpreferred", "Blue Cash Preferred", "American Express", "US", "Amex"),
    ("amexdelta", "Delta", "American Express", "US", "Amex"),
    ("amexdeltagold", "Delta Gold", "American Express", "US", "Amex"),
    ("amexdeltaskymilesblu", "Delta SkyMiles Blue", "American Express", "US", "Amex"),
    ("amexdeltaskymilespla", "Delta SkyMiles Platinum", "American Express", "US", "Amex"),
    ("amexdeltaskymilesgol", "Delta SkyMiles Gold", "American Express", "US", "Amex"),
    ("amexdeltaskymilesres", "Delta SkyMiles Reserve", "American Express", "US", "Amex"),
    ("amexhiltonhonors", "Hilton Honors", "American Express", "US", "Amex"),
    ("amexhiltonsurpass", "Hilton Surpass", "American Express", "US", "Amex"),
    ("amexhiltonaspire", "Hilton Aspire", "American Express", "US", "Amex"),
    ("amexmarriottbonvoy", "Marriott Bonvoy", "American Express", "US", "Amex"),
    ("amexmarriottbonvoybr", "Marriott Bonvoy Brilliant", "American Express", "US", "Amex"),
    ("amexmarriottbonvoybu", "Marriott Bonvoy Business", "American Express", "US", "Amex"),
    ("amexcobalt", "Cobalt", "American Express", "US", "Amex"),
    ("amexcash", "Cash Magnet", "American Express", "US", "Amex"),
    ("amexcashmagnet", "Cash Magnet", "American Express", "US", "Amex"),
    # Amex Business  
    ("amexbizplat", "Business Platinum", "American Express", "US", "Amex"),
    ("amexbizgold", "Business Gold", "American Express", "US", "Amex"),
    ("amexbusinessgreen", "Business Green", "American Express", "US", "Amex"),
    ("amexbluebizplus", "Blue Business Plus", "American Express", "US", "Amex"),
    ("amexbluebusinesscash", "Blue Business Cash", "American Express", "US", "Amex"),
    ("amexamazonbusinesspr", "Amazon Business Prime", "American Express", "US", "Amex"),
    ("amexbizcenturion", "Business Centurion", "American Express", "US", "Amex"),
    ("amexbusinesscenturio", "Business Centurion (alt)", "American Express", "US", "Amex"),

    # Chase
    ("chasesapphirepreferr", "Sapphire Preferred", "Chase", "US", "Chase"),
    ("chasesapphirereserve", "Sapphire Reserve", "Chase", "US", "Chase"),
    ("chasefreedom", "Freedom", "Chase", "US", "Chase"),
    ("chasefreedomflex", "Freedom Flex", "Chase", "US", "Chase"),
    ("chasefreedomunlimite", "Freedom Unlimited", "Chase", "US", "Chase"),
    ("chasefreedomrise", "Freedom Rise", "Chase", "US", "Chase"),
    ("chaseamazonprime", "Amazon Prime", "Chase", "US", "Chase"),
    ("chaseamazon", "Amazon", "Chase", "US", "Chase"),
    ("chaseunitedexplorer", "United Explorer", "Chase", "US", "Chase"),
    ("chaseunitedquest", "United Quest", "Chase", "US", "Chase"),
    ("chaseunitedclub", "United Club Infinite", "Chase", "US", "Chase"),
    ("chaseunitedgateway", "United Gateway", "Chase", "US", "Chase"),
    ("chaseinkpreferred", "Ink Business Preferred", "Chase", "US", "Chase"),
    ("chaseinkcash", "Ink Business Cash", "Chase", "US", "Chase"),
    ("chaseinkunlimited", "Ink Business Unlimited", "Chase", "US", "Chase"),
    ("chaseslate", "Slate", "Chase", "US", "Chase"),
    ("chaseslateedge", "Slate Edge", "Chase", "US", "Chase"),
    ("chasemarriottbonvoy", "Marriott Bonvoy Bold", "Chase", "US", "Chase"),
    ("chasemarriottbonvoyb", "Marriott Bonvoy Boundless", "Chase", "US", "Chase"),
    ("chasemarriottboundless", "Marriott Boundless", "Chase", "US", "Chase"),
    ("chasesouthwest", "Southwest", "Chase", "US", "Chase"),
    ("chasesouthwestpriori", "Southwest Priority", "Chase", "US", "Chase"),
    ("chasesouthwestplus", "Southwest Plus", "Chase", "US", "Chase"),
    ("chasesouthwestpremie", "Southwest Premier", "Chase", "US", "Chase"),
    ("chasebusinessunlimit", "Ink Business Unlimited", "Chase", "US", "Chase"),
    ("chasedisney", "Disney Visa", "Chase", "US", "Chase"),
    ("chasedisneypartner", "Disney Premier", "Chase", "US", "Chase"),
    ("chaseihg", "IHG One Rewards", "Chase", "US", "Chase"),
    ("chaseihgpremier", "IHG Premier", "Chase", "US", "Chase"),
    ("chasehyatt", "World of Hyatt", "Chase", "US", "Chase"),
    ("chaseaeroplan", "Aeroplan", "Chase", "US", "Chase"),
    ("chasebrit", "British Airways", "Chase", "US", "Chase"),
    ("chaseba", "British Airways", "Chase", "US", "Chase"),
    ("chasetotalchecking", "Total Checking", "Chase", "US", "Chase"),
    ("chasedebit", "Debit Card", "Chase", "US", "Chase"),

    # Capital One
    ("quicksilver", "Quicksilver", "Capital One", "US", "Capital One"),
    ("venture", "Venture", "Capital One", "US", "Capital One"),
    ("cap1venture", "Venture", "Capital One", "US", "Capital One"),
    ("venturex", "Venture X", "Capital One", "US", "Capital One"),
    ("cap1venturex", "Venture X", "Capital One", "US", "Capital One"),
    ("cap1ventureone", "VentureOne", "Capital One", "US", "Capital One"),
    ("savor", "Savor", "Capital One", "US", "Capital One"),
    ("cap1savor", "Savor", "Capital One", "US", "Capital One"),
    ("cap1savorone", "SavorOne", "Capital One", "US", "Capital One"),
    ("savorone", "SavorOne", "Capital One", "US", "Capital One"),
    ("quicksilverone", "Quicksilver One", "Capital One", "US", "Capital One"),
    ("cap1spark", "Spark", "Capital One", "US", "Capital One"),
    ("cap1sparkcash", "Spark Cash", "Capital One", "US", "Capital One"),
    ("cap1sparkcashplus", "Spark Cash Plus", "Capital One", "US", "Capital One"),

    # Citi
    ("citidoublecash", "Double Cash", "Citi", "US", "Citi"),
    ("citipremier", "Premier", "Citi", "US", "Citi"),
    ("citicustomcash", "Custom Cash", "Citi", "US", "Citi"),
    ("citistrata", "Strata Premier", "Citi", "US", "Citi"),
    ("citistratapremier", "Strata Premier", "Citi", "US", "Citi"),
    ("citirewards", "Rewards+", "Citi", "US", "Citi"),
    ("citiaadvantage", "AAdvantage", "Citi", "US", "Citi"),
    ("citiaaplatinum", "AAdvantage Platinum", "Citi", "US", "Citi"),
    ("citiaaexecutive", "AAdvantage Executive", "Citi", "US", "Citi"),
    ("citidiamond", "Diamond Preferred", "Citi", "US", "Citi"),
    ("citidiamondpreferred", "Diamond Preferred", "Citi", "US", "Citi"),
    ("citicostco", "Costco Anywhere", "Citi", "US", "Citi"),
    ("citicostcoanywhere", "Costco Anywhere", "Citi", "US", "Citi"),
    ("citiprestige", "Prestige", "Citi", "US", "Citi"),
    
    # Discover
    ("discoverit", "Discover It", "Discover", "US", "Discover"),
    ("discover", "Discover", "Discover", "US", "Discover"),
    ("discoveritcash", "Discover It Cash Back", "Discover", "US", "Discover"),
    ("discovermiles", "Discover Miles", "Discover", "US", "Discover"),
    ("discoverchrome", "Discover It Chrome", "Discover", "US", "Discover"),
    ("discoveritstudent", "Discover It Student", "Discover", "US", "Discover"),
    ("discoveritstudentcas", "Discover It Student Cash", "Discover", "US", "Discover"),
    
    # Bank of America
    ("boacashrewards", "Cash Rewards", "Bank of America", "US", "Bank of America"),
    ("boapremiumrewards", "Premium Rewards", "Bank of America", "US", "Bank of America"),
    ("boacustomizedcash", "Customized Cash", "Bank of America", "US", "Bank of America"),
    ("boatravelrewards", "Travel Rewards", "Bank of America", "US", "Bank of America"),
    ("boaunlimitedcash", "Unlimited Cash", "Bank of America", "US", "Bank of America"),
    ("boaalaskamileage", "Alaska Mileage Plan", "Bank of America", "US", "Bank of America"),
    ("boaalaska", "Alaska Airlines", "Bank of America", "US", "Bank of America"),
    ("boapremiumrewardsel", "Premium Rewards Elite", "Bank of America", "US", "Bank of America"),
    
    # Wells Fargo
    ("wellsfargosignify", "Signify Business", "Wells Fargo", "US", "Wells Fargo"),
    ("wellsfargoactive", "Active Cash", "Wells Fargo", "US", "Wells Fargo"),
    ("wellsfargocash", "Active Cash", "Wells Fargo", "US", "Wells Fargo"),
    ("wellsfargoreflect", "Reflect", "Wells Fargo", "US", "Wells Fargo"),
    ("wellsfargoautograph", "Autograph", "Wells Fargo", "US", "Wells Fargo"),
    ("wellsfargobilt", "Bilt", "Wells Fargo", "US", "Wells Fargo"),
    ("wellsfargopropel", "Propel", "Wells Fargo", "US", "Wells Fargo"),
    ("wellsfargoautographj", "Autograph Journey", "Wells Fargo", "US", "Wells Fargo"),
    
    # US Bank
    ("usbankaltitude", "Altitude Connect", "US Bank", "US", "US Bank"),
    ("usbankaltitudeconnec", "Altitude Connect", "US Bank", "US", "US Bank"),
    ("usbankaltitudereserv", "Altitude Reserve", "US Bank", "US", "US Bank"),
    ("usbankcashplus", "Cash+", "US Bank", "US", "US Bank"),
    
    # Barclays
    ("barclaysarrival", "Arrival+", "Barclays", "US", "Barclays"),
    ("barclaysarrivalprem", "Arrival Premier", "Barclays", "US", "Barclays"),
    ("barclaysaviator", "AAdvantage Aviator", "Barclays", "US", "Barclays"),
    ("barclaysaviatorred", "Aviator Red", "Barclays", "US", "Barclays"),
    ("barclaysjetblue", "JetBlue", "Barclays", "US", "Barclays"),
    ("barclaysjetblueplus", "JetBlue Plus", "Barclays", "US", "Barclays"),
    ("barclayschoice", "Choice Privileges", "Barclays", "US", "Barclays"),
    ("barclayswyndham", "Wyndham Earner", "Barclays", "US", "Barclays"),
    
    # Other US
    ("applecard", "Apple Card", "Apple", "US", "Other US"),
    ("paypal", "PayPal", "PayPal", "US", "Other US"),
    ("venmo", "Venmo Credit Card", "Venmo", "US", "Other US"),
    ("sofi", "SoFi", "SoFi", "US", "Other US"),
    ("bilt", "Bilt Mastercard", "Bilt", "US", "Other US"),
    ("biltmastercard", "Bilt Mastercard", "Bilt", "US", "Other US"),
    ("brex", "Brex", "Brex", "US", "Other US"),
    ("usaa", "USAA", "USAA", "US", "Other US"),
    ("penfed", "PenFed", "PenFed", "US", "Other US"),
    ("affinity", "Affinity Cash Rewards", "Affinity", "US", "Other US"),
    
    # Also try cubelin uploader  
    # ("AMEXBizGold", "Business Gold (cubelin)", "American Express", "US", "Amex", "cubelin"),
    
    # Canada
    ("amexplatca", "Platinum", "American Express", "CA", "Amex CA"),
    ("amexgoldca", "Gold", "American Express", "CA", "Amex CA"),
    ("amexcobalt", "Cobalt", "American Express", "CA", "Amex CA"),
    ("cibcaeroplan", "Aeroplan", "CIBC", "CA", "CIBC"),
    ("tdaeroplan", "Aeroplan", "TD", "CA", "TD"),
    ("scotiamomentum", "Momentum", "Scotiabank", "CA", "Scotiabank"),
    ("scotiagold", "Gold", "Scotiabank", "CA", "Scotiabank"),
    ("bmoworld", "World Elite", "BMO", "CA", "BMO"),
    
    # UK
    ("amexplatuk", "Platinum", "American Express", "UK", "Amex UK"),
    ("amexgolduk", "Gold", "American Express", "UK", "Amex UK"),
]

base_url = "https://u.cubeupload.com/ccbackground/"

def check_url(item):
    name, display, issuer, country, category = item
    url = f"{base_url}{name}.png"
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        status = resp.getcode()
        length = resp.headers.get("Content-Length", "?")
        return (name, display, issuer, country, category, status, length)
    except Exception as e:
        return (name, display, issuer, country, category, 0, str(e)[:50])

print("Probing cubeupload URLs...")
found = []
not_found = []

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as exe:
    for result in exe.map(check_url, candidates):
        name, display, issuer, country, category, status, length = result
        if status == 200:
            found.append(result)
            print(f"  OK  {name}.png  ({display} - {issuer}) size={length}")
        else:
            not_found.append(result)

print(f"\n=== FOUND: {len(found)} cards ===")
for r in found:
    name, display, issuer, country, category, status, length = r
    print(f'    CommunityCard(id: "{name}", name: "{display}", issuer: "{issuer}", country: "{country}", category: "{category}", imageURL: "{base_url}{name}.png", author: nil),')

print(f"\n=== NOT FOUND: {len(not_found)} ===")
for r in not_found:
    name = r[0]
    print(f"  MISS {name}.png")
