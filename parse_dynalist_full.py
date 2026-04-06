#!/usr/bin/env python3
"""Full extraction: parse dynalist HTML to get card name, URL, and hierarchy."""
import re, json

with open(r"D:\CardioSword\Apple Pay High Res (or paypal low res) Card Backgrounds - Dynalist.htm", "r", encoding="utf-8", errors="replace") as f:
    html = f.read()

# Extract direct <a> links with title attribute pointing to cubeupload
# Pattern: <a title="CARD NAME" href="CUBEUPLOAD_URL" ...>
link_pattern = r'<a\s+title="([^"]+)"\s+href="(https?://u\.cubeupload\.com/[^"]+)"[^>]*>'
matches = re.findall(link_pattern, html)

# Deduplicate by URL (keep first occurrence)
seen_urls = set()
unique_cards = []
for name, url in matches:
    if url not in seen_urls:
        seen_urls.add(url)
        unique_cards.append((name.strip(), url))

print(f"Found {len(unique_cards)} unique cards with cubeupload links\n")

# Now we need to figure out the hierarchy (country + issuer)
# The nodes are nested in the HTML. Let's find the hierarchy by looking at 
# the node structure. Each node has a parent chain.

# Find all Node elements and their nesting level
# The dynalist HTML uses nested divs with class "Node-children"
# Let's track the hierarchy by finding headings before card entries

# Alternative: parse the DOM structure to find parent categories
# Let's find all text content in order and track indentation/hierarchy

# Find all "Node-self" elements which contain the actual content
node_pattern = r'<div[^>]*class="[^"]*Node-self[^"]*"[^>]*data-id="([^"]*)"[^>]*>.*?<div[^>]*class="[^"]*Node-renderedContent[^"]*"[^>]*>(.*?)</div>'
nodes = re.findall(node_pattern, html, re.DOTALL)
print(f"Found {len(nodes)} node elements")

# Build a sequential list of entries
entries = []
for node_id, content in nodes:
    # Strip HTML tags to get text
    text = re.sub(r'<[^>]+>', '', content).strip()
    text = re.sub(r'\s+', ' ', text)
    # Check if this node has a cubeupload link
    url_match = re.search(r'https?://u\.cubeupload\.com/[^\s"\'<>\)]+', content)
    url = url_match.group() if url_match else None
    # Check for other image links (forum, etc)
    other_url = re.search(r'https?://forum\.uscreditcardguide\.com/[^\s"\'<>\)]+', content)
    if not url and other_url:
        url = other_url.group()
    entries.append({"id": node_id, "text": text, "url": url})

# Now find the hierarchy by looking at the nesting structure
# Let's find parent-child relationships using Node-children containers
# Each Node has children in a "Node-children" div

# Alternative simpler approach: since nodes appear in order, track section headings
# The main sections are: "United States", "Canada", "United Kingdom", etc.
# Sub-sections: "American Express", "Chase", etc.
# Sub-sub-sections: "Business", "Personal", etc.

# Let's find the known hierarchy markers
country_names = ["United States", "Canada", "United Kingdom", "Japan", "China", 
                 "Hong Kong", "South Korea", "Australia", "Singapore", "Taiwan",
                 "Europe", "Germany", "Netherlands", "France", "Spain", "Italy",
                 "India", "Brazil", "Mexico", "New Zealand", "Malaysia", "Thailand",
                 "Others", "Other"]
country_map = {
    "United States": "US", "Canada": "CA", "United Kingdom": "UK", "Japan": "JP",
    "China": "CN", "Hong Kong": "HK", "South Korea": "KR", "Australia": "AU",
    "Singapore": "SG", "Taiwan": "TW", "Europe": "EU", "Germany": "DE",
    "Netherlands": "NL", "France": "FR", "Spain": "ES", "Italy": "IT",
    "India": "IN", "Brazil": "BR", "Mexico": "MX", "New Zealand": "NZ",
    "Malaysia": "MY", "Thailand": "TH", "Others": "XX", "Other": "XX"
}

issuer_names = ["American Express", "Chase", "Capital One", "Citi", "Discover",
                "Bank of America", "Wells Fargo", "US Bank", "Barclays", 
                "HSBC", "PNC", "TD", "BMO", "CIBC", "Scotiabank", "RBC",
                "Goldman Sachs", "Synchrony", "Other"]

current_country = "US"
current_country_code = "US"
current_issuer = "Unknown"
current_subcategory = ""

cards_with_hierarchy = []

for entry in entries:
    text = entry["text"]
    
    # Check if this is a country header
    for cn in country_names:
        if text == cn or text.startswith(cn + " "):
            current_country = cn
            current_country_code = country_map.get(cn, "XX")
            current_issuer = "Unknown"
            current_subcategory = ""
            break
    
    # Check if this is an issuer header
    for iss in issuer_names:
        if text == iss:
            current_issuer = iss
            current_subcategory = ""
            break
    
    # Check for subcategory (Business, Personal, etc.)
    if text in ["Business", "Personal", "Debit", "Prepaid", "Co-branded"]:
        current_subcategory = text
    
    # If this entry has a cubeupload URL, it's a card
    if entry["url"] and "cubeupload.com" in (entry["url"] or ""):
        # Clean up card name
        card_name = text
        # Remove "low res", "jpeg", etc markers
        card_name = re.sub(r'\s*(low res|jpeg|new|updated|v2|v3|2020|2021|2022|2023|2024|2025)\s*$', '', card_name, flags=re.IGNORECASE).strip()
        
        cards_with_hierarchy.append({
            "name": card_name,
            "url": entry["url"],
            "country": current_country_code,
            "country_name": current_country,
            "issuer": current_issuer,
            "subcategory": current_subcategory,
        })

# Print results by country and issuer
print(f"\n=== {len(cards_with_hierarchy)} cards with hierarchy ===\n")

by_country = {}
for c in cards_with_hierarchy:
    key = (c["country"], c["issuer"])
    by_country.setdefault(key, []).append(c)

for (country, issuer), cards in sorted(by_country.items()):
    print(f"\n--- {country} / {issuer} ({len(cards)} cards) ---")
    for c in cards:
        is_png = c["url"].endswith(".png")
        marker = "" if is_png else " [JPEG]"
        print(f'  {c["name"]}: {c["url"]}{marker}')

# Generate Swift code
print("\n\n=== SWIFT CATALOG CODE ===\n")
for (country, issuer), cards in sorted(by_country.items()):
    # Create a category name
    if country == "US":
        category = issuer if issuer in ["American Express", "Chase", "Capital One", "Citi", "Discover", "Bank of America", "Wells Fargo", "US Bank", "Barclays"] else "Other US"
    else:
        category = issuer if issuer != "Unknown" else f"Other {country}"
    
    category_short = category.replace("American Express", "Amex")
    
    print(f'    // ── {country} ── {issuer} ──')
    for c in cards:
        # Generate a safe ID
        safe_id = re.sub(r'[^a-z0-9]', '-', c["name"].lower()).strip('-')
        safe_id = re.sub(r'-+', '-', safe_id)
        safe_id = f'{country.lower()}-{safe_id}'
        
        # Escape any quotes in name
        name = c["name"].replace('"', '\\"')
        
        print(f'    CommunityCard(id: "{safe_id}", name: "{name}", issuer: "{issuer}", country: "{country}", category: "{category_short}", imageURL: "{c["url"]}", author: nil),')
    print()
