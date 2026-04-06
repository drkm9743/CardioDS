#!/usr/bin/env python3
"""
Complete dynalist parser: extracts ALL card images (cubeupload, uscardforum, etc.)
with full hierarchy (country, issuer, subcategory, card name).
Outputs Swift CommunityCard entries ready to paste.
"""
import re, json, sys
from html.parser import HTMLParser

with open(r"D:\CardioSword\Apple Pay High Res (or paypal low res) Card Backgrounds - Dynalist.htm", "r", encoding="utf-8", errors="replace") as f:
    html = f.read()

# 1. Find all image domains
all_img_urls = re.findall(r'https?://[^\s"<>\)\']+\.(?:png|jpe?g|webp)', html)
from urllib.parse import urlparse
domains = set()
for u in all_img_urls:
    try:
        domains.add(urlparse(u).netloc)
    except:
        pass

# Filter to only card-related domains (exclude dynalist assets, favicons etc)
card_domains = [d for d in sorted(domains) if d not in [
    "dynalist.io", "www.dynalist.io", "fonts.googleapis.com",
] and "google" not in d and "gstatic" not in d]

print("Card image domains:")
for d in card_domains:
    count = sum(1 for u in all_img_urls if d in u)
    print(f"  {d}: {count} URLs")
print(f"Total card image URLs: {len(all_img_urls)}")

# 2. Pattern for image URLs we care about
IMG_PATTERN = re.compile(
    r'https?://(?:'
    r'u\.cubeupload\.com|'
    r'asset-cdn\.uscardforum\.com|'
    r'www-cdn\.uscardforum\.com|'
    r'forum\.uscreditcardguide\.com|'
    r'i\.imgur\.com'
    r')/[^\s"<>\)\']+\.(?:png|jpe?g|webp)',
    re.IGNORECASE
)

# 3. Parse the HTML structure. Dynalist renders as nested divs.
# Each "Node" has:
#   - A "Node-self" div containing "Node-renderedContent" with the text
#   - Optionally "Node-children" containing child nodes
# The nesting level tells us the hierarchy.

# Let's find nodes by looking for the rendered content divs
# The key structure: <div class="Node ... is-currentRoot">
#   -> children at different nesting levels

# Strategy: Walk through the HTML and extract content at each nesting depth
# Use a simpler approach: find all <a> tags with title attr pointing to image URLs,
# AND find all text nodes that are section headers.

# Let's extract ordered content by finding all Node-renderedContent blocks
# with their nesting depth (counted by parent Node-children divs)

# Simpler: find all content blocks in order and track hierarchy markers
# Let's look for lines of interest between <div class="Node-renderedContent..."> tags

content_blocks = []
# Match Node-renderedContent divs and extract inner HTML
pattern = r'<div[^>]*class="[^"]*Node-renderedContent[^"]*node-line[^"]*"[^>]*>(.*?)</div>\s*</div>'
for m in re.finditer(pattern, html, re.DOTALL):
    inner = m.group(1)
    # Get plain text
    text = re.sub(r'<[^>]+>', '', inner).strip()
    text = re.sub(r'\s+', ' ', text)
    # Get image URL if present
    url_match = IMG_PATTERN.search(inner)
    url = url_match.group() if url_match else None
    # Get link title if present
    title_match = re.search(r'<a\s+title="([^"]+)"', inner)
    title = title_match.group(1) if title_match else None
    
    content_blocks.append({
        "text": text,
        "url": url,
        "title": title,
        "raw_len": len(inner),
    })

print(f"\nExtracted {len(content_blocks)} content blocks")
if not content_blocks:
    # Try alternative pattern
    pattern2 = r'class="Node-renderedContent[^"]*"[^>]*>(.*?)</div>'
    for m in re.finditer(pattern2, html, re.DOTALL):
        inner = m.group(1)
        text = re.sub(r'<[^>]+>', '', inner).strip()
        text = re.sub(r'\s+', ' ', text)
        url_match = IMG_PATTERN.search(inner)
        url = url_match.group() if url_match else None
        title_match = re.search(r'<a\s+title="([^"]+)"', inner)
        title = title_match.group(1) if title_match else None
        content_blocks.append({"text": text, "url": url, "title": title, "raw_len": len(inner)})
    print(f"  (alt pattern) Extracted {len(content_blocks)} content blocks")

# Print first 30 blocks to understand structure
print("\nFirst 40 content blocks:")
for i, b in enumerate(content_blocks[:40]):
    marker = " [IMG]" if b["url"] else ""
    print(f"  {i:3d}: {b['text'][:80]}{marker}")

# 4. Now walk through blocks and assign hierarchy
COUNTRIES = {
    "United States": "US", "Canada": "CA", "United Kingdom": "UK", 
    "Japan": "JP", "China": "CN", "Hong Kong": "HK", "South Korea": "KR",
    "Australia": "AU", "Singapore": "SG", "Taiwan": "TW",
    "Europe": "EU", "Germany": "DE", "Netherlands": "NL", "France": "FR",
    "Spain": "ES", "Italy": "IT", "India": "IN", "Brazil": "BR",
    "Mexico": "MX", "New Zealand": "NZ", "Malaysia": "MY", "Thailand": "TH",
    "Philippines": "PH", "Indonesia": "ID", "Vietnam": "VN", "Russia": "RU",
    "Turkey": "TR", "UAE": "AE", "Saudi Arabia": "SA", "Israel": "IL",
    "South Africa": "ZA", "Ireland": "IE", "Switzerland": "CH",
    "Belgium": "BE", "Portugal": "PT", "Austria": "AT", "Poland": "PL",
    "Czech Republic": "CZ",
}

ISSUERS = {
    "American Express", "Chase", "Capital One", "Citi", "Discover",
    "Bank of America", "Wells Fargo", "US Bank", "Barclays", "HSBC",
    "PNC", "TD", "BMO", "CIBC", "Scotiabank", "RBC", "Goldman Sachs",
    "Synchrony", "Fidelity", "Navy Federal", "PenFed", "USAA",
    "Citizens", "Regions", "Fifth Third", "KeyBank", "M&T Bank",
    "First Republic", "Schwab", "SoFi", "Ally", "Marcus",
    "Other Banks", "Debit Cards", "FinTech", "Misc", "Other",
    "Cardless",
}

current_country = "US"
current_country_code = "US"  
current_issuer = "Other"
current_subcategory = ""

cards = []

for block in content_blocks:
    text = block["text"]
    
    # Check for country
    for cname, ccode in COUNTRIES.items():
        if text == cname:
            current_country = cname
            current_country_code = ccode
            current_issuer = "Other"
            current_subcategory = ""
            break
    
    # Check for issuer
    if text in ISSUERS or text.rstrip(":") in ISSUERS:
        current_issuer = text.rstrip(":")
        current_subcategory = ""
        continue
    
    # Check for subcategory
    if text in ["Business", "Personal", "Debit", "Prepaid", "Co-branded", "Student", "Secured"]:
        current_subcategory = text
        continue
    
    # If block has image URL -> it's a card
    if block["url"]:
        card_name = block["title"] or text
        # Clean markers
        card_name = re.sub(r'\s*(low res|jpeg|new|updated|v\d|201\d|202\d)\s*$', '', card_name, flags=re.I).strip()
        card_name = re.sub(r'!\[.*?\]\(.*?\)\s*', '', card_name).strip()  # remove markdown images
        if not card_name:
            card_name = text
            card_name = re.sub(r'!\[.*?\]\(.*?\)\s*', '', card_name).strip()
            card_name = re.sub(r'\s*(low res|jpeg)\s*$', '', card_name, flags=re.I).strip()
        
        if card_name:
            cards.append({
                "name": card_name,
                "url": block["url"],
                "country": current_country_code,
                "country_name": current_country,
                "issuer": current_issuer,
                "subcategory": current_subcategory,
            })

# Deduplicate by URL
seen = set()
unique_cards = []
for c in cards:
    if c["url"] not in seen:
        seen.add(c["url"])
        unique_cards.append(c)
cards = unique_cards

print(f"\n=== {len(cards)} unique cards extracted ===\n")

# Print by country/issuer
by_key = {}
for c in cards:
    key = (c["country_name"], c["issuer"])
    by_key.setdefault(key, []).append(c)

for (country, issuer), group in sorted(by_key.items()):
    print(f"\n--- {country} / {issuer} ({len(group)}) ---")
    for c in group:
        ext = "PNG" if c["url"].lower().endswith(".png") else "JPG"
        print(f'  [{ext}] {c["name"]}: {c["url"]}')

# 5. Generate Swift code
print("\n\n// ============= SWIFT CommunityCard CATALOG =============\n")
print("private let builtInCards: [CommunityCard] = [")

for (country_name, issuer), group in sorted(by_key.items()):
    country_code = COUNTRIES.get(country_name, "XX")
    
    # Determine category
    if country_code == "US":
        if issuer in ["American Express"]:
            cat = "Amex"
        elif issuer in ["Chase", "Capital One", "Citi", "Discover"]:
            cat = issuer
        elif issuer in ["Bank of America"]:
            cat = "Bank of America"
        elif issuer in ["Wells Fargo"]:
            cat = "Wells Fargo"
        elif issuer in ["US Bank"]:
            cat = "US Bank"
        elif issuer in ["Barclays"]:
            cat = "Barclays"
        else:
            cat = "Other US"
    else:
        cat = f"{issuer} {country_code}" if issuer != "Other" else f"Other {country_code}"
    
    print(f'    // ── {country_name} ── {issuer} ──')
    for c in group:
        safe_id = re.sub(r'[^a-z0-9]', '-', c["name"].lower()).strip('-')
        safe_id = re.sub(r'-+', '-', safe_id)[:30]
        safe_id = f'{country_code.lower()}-{safe_id}'
        name = c["name"].replace('"', '\\"').replace("'", "'")
        
        print(f'    CommunityCard(id: "{safe_id}", name: "{name}", issuer: "{issuer}", country: "{country_code}", category: "{cat}", imageURL: "{c["url"]}", author: nil),')
    print()

print("]")
