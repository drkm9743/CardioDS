#!/usr/bin/env python3
"""
Fix the issuer misassignment from parse_dynalist_v2.py output.
Reads the raw Swift CommunityCard entries and reassigns issuers
based on card name/URL patterns. Deduplicates and generates clean output.
"""
import re, sys

# Map of (name_pattern, url_pattern) → (issuer, category)
# Order matters: first match wins
RULES = [
    # Bank of America
    (r'\bbo[aA]\b|Bank of America|BankAmericard|Better Balance', r'boa', 'Bank of America', 'Bank of America'),
    # Chase
    (r'Sapphire|Freedom|Ink\b|United Mileage|Southwest|Disney|Star Wars|Hyatt|J\.P\.Morgan|Private Client|Ritz.Carlton|Amazon.*\b(Prime|not prime)|Marriott Bonvoy Bold|Marriott Bonvoy Boundless|IHG|^Debit Card$|^Frozen$', r'chase', 'Chase', 'Chase'),
    # Citi
    (r'Citigold|Double Cash|Dividend|Costco|AAdvantage|CitiBusiness|^Premier$|Premier Pre|Prestige|Rewards\+|Thank You|^COCO$|Strat[ea]|^Debit$', r'citi', 'Citi', 'Citi'),
    # Amex (already mostly correct, but catch stragglers)
    (r'Amex|Centurion|Hilton|Delta|Plum|Blue Cash|Blue Sky|Blue Business|Schwab|Every Day|Marriott Bonvoy(?! Bold| Boundless)|Rose Gold|White Gold|^Gold$|^Gold JP$|^Green JP$|^Platinum$|^Platinum (?:x |Pre|Morgan|Schwab)|Companion|Business Gold|Business Platinum|Business Green|Business Cash|Amazon Business Prime|Additional Card|^debit$|^Blue Cash |^Bunisess Platinum$', r'amex', 'American Express', 'Amex'),
    # Discover
    (r'^Rose Quartz$|^Ocean$|^Iridescent$|^Blue$|^Garnet$|^Mountain$|^City$|^wolf$|^mixtape$|^Husky$|^Polar Bear$|^Cat$|^Tiger$|^New York Skyline$|^old$|^Cashback Debit$', r'discover', 'Discover', 'Discover'),
    # Capital One
    (r'Capital One|Quick Silver|Venture X|Venture$|SavorOne', r'capital.?one|quicksilver|venture', 'Capital One', 'Capital One'),
    # Barclays
    (r'Uber|Arrival|Avios|AAdvantage Aviator|JetBlue|Barclays', r'barclay', 'Barclays', 'Barclays'),
    # US Bank
    (r'Altitude|Leverage|Kroger|Ralphs|^Go$|Business Triple Cash|Cash Plus|US National Flag|Second Wave', r'usbank', 'US Bank', 'US Bank'),
    # HSBC
    (r'HSBC', r'hsbc', 'HSBC', 'Other US'),
    # Wells Fargo
    (r'Wells Fargo|Propel', r'wellsfargo|propel', 'Wells Fargo', 'Wells Fargo'),
    # Synchrony
    (r'Banana Republic|Verizon', r'synchrony|synchony', 'Synchrony', 'Other US'),
    # PenFed
    (r'Penfed', r'penfed', 'PenFed', 'Other US'),
]

# Specific name → (issuer, category) overrides for tricky cards
NAME_OVERRIDES = {
    'Apple Card': ('Apple / Goldman Sachs', 'Other US'),
    'Goldman Sachs Apple Card': ('Apple / Goldman Sachs', 'Other US'),
    'Apple Cash': ('Apple', 'Other US'),
    'Apple Account': ('Apple', 'Other US'),
    'Brex Card': ('Brex', 'Other US'),
    'Brex金属卡': ('Brex', 'Other US'),
    'Brex预算管理虚拟卡': ('Brex', 'Other US'),
    'Manchester United': ('Cardless', 'Other US'),
    'Cleveland Cavaliers': ('Cardless', 'Other US'),
    'Boston Celtic': ('Cardless', 'Other US'),
    'Deserve Edu': ('Deserve', 'Other US'),
    'Ducks Unlimited credit card': ('First Bankcard', 'Other US'),
    'CB&T AmaZing Cash for Business': ('CB&T', 'Other US'),
    'Fidelity Bloom': ('Fidelity', 'Other US'),
    'Fidelity': ('Fidelity', 'Other US'),
    'Fidelity HSA': ('Fidelity', 'Other US'),
    'ETrade': ('E*Trade', 'Other US'),
    'Etrade Checking': ('E*Trade', 'Other US'),
    'Digital Credit Union': ('DCU', 'Other US'),
    'Fairwinds': ('Fairwinds', 'Other US'),
    'Genisys credit union': ('Genisys CU', 'Other US'),
    'Gesa': ('Gesa CU', 'Other US'),
    'HMBradley': ('HMBradley', 'Other US'),
    'Zebra': ('HMBradley', 'Other US'),
    'Zebra vertical': ('HMBradley', 'Other US'),
    'Teal': ('HMBradley', 'Other US'),
    'Teal vertical': ('HMBradley', 'Other US'),
    'Pink': ('HMBradley', 'Other US'),
    'Pink vertical': ('HMBradley', 'Other US'),
    'Green vertical': ('HMBradley', 'Other US'),
    'Lili': ('Lili', 'Other US'),
    'Mercury Business': ('Mercury', 'Other US'),
    'Meta Mask': ('MetaMask', 'Other US'),
    'Monifi': ('Monifi', 'Other US'),
    'Morgan Stanley': ('Morgan Stanley', 'Other US'),
    'N26': ('N26', 'Other US'),
    'Netspend': ('Netspend', 'Other US'),
    'One Card': ('One', 'Other US'),
    'Onjuno': ('Onjuno', 'Other US'),
    'Passbook': ('Passbook', 'Other US'),
    'Paypal': ('PayPal', 'Other US'),
    'The Bancorp Bank: PayPal Debit Mastercard': ('PayPal', 'Other US'),
    'PNC LGBT+': ('PNC', 'Other US'),
    'PNC Virtual Wallet Debit': ('PNC', 'Other US'),
    'PNC University of Michigan Debit': ('PNC', 'Other US'),
    'Revolut': ('Revolut', 'Other US'),
    'Revolut Virtual': ('Revolut', 'Other US'),
    'Robinhood': ('Robinhood', 'Other US'),
    'Sable': ('Sable', 'Other US'),
    'Santander': ('Santander', 'Other US'),
    'Securityplus Federal Credit Union': ('SecurityPlus FCU', 'Other US'),
    'Sofi': ('SoFi', 'Other US'),
    'Spiral': ('Spiral', 'Other US'),
    'Sunflower Bank': ('Sunflower Bank', 'Other US'),
    'TD Bank': ('TD Bank', 'Other US'),
    'Treecard': ('Treecard', 'Other US'),
    'Upgrade': ('Upgrade', 'Other US'),
    'Varo': ('Varo', 'Other US'),
    'Venmo': ('Venmo', 'Other US'),
    'Venmo 2': ('Venmo', 'Other US'),
    'Verity': ('Verity CU', 'Other US'),
    'Workers Credit Union': ('Workers CU', 'Other US'),
    'Fiz': ('Fiz', 'Other US'),
    'AOD Visa Signature': ('AOD FCU', 'Other US'),
    'Bank of Hawaii': ('Bank of Hawaii', 'Other US'),
    'Bilt': ('Bilt', 'Other US'),
    'BlackHawks AB InBev': ('AB InBev', 'Other US'),
    'Acorns': ('Acorns', 'Other US'),
    'Albert': ('Albert', 'Other US'),
    'Ally': ('Ally', 'Other US'),
    # BoA cards the regex missed
    'Alasak Atmos Ascent': ('Bank of America', 'Bank of America'),
    'Alaska Atmos Summit': ('Bank of America', 'Bank of America'),
    'Cash Rewards Old': ('Bank of America', 'Bank of America'),
    'Columbia': ('Bank of America', 'Bank of America'),
    'Default': ('Bank of America', 'Bank of America'),
    'Another Default': ('Bank of America', 'Bank of America'),
    'NWF Fox': ('Bank of America', 'Bank of America'),
    'Premium Rewards': ('Bank of America', 'Bank of America'),
    'Premium Rewards Elite': ('Bank of America', 'Bank of America'),
    'UTAM': ('Bank of America', 'Bank of America'),
    'University of Michigan': ('Bank of America', 'Bank of America'),
    'UCI': ('Bank of America', 'Bank of America'),
    'WWF': ('Bank of America', 'Bank of America'),
    'Susan G Komen': ('Bank of America', 'Bank of America'),
    'MLB': ('Bank of America', 'Bank of America'),
    'Travel Rewards': ('Bank of America', 'Bank of America'),
    # Chase cards the regex missed
    'Platinum business': ('Chase', 'Chase'),
    'Sapphire Reserve Biz': ('Chase', 'Chase'),
    'Amazon (not prime)': ('Chase', 'Chase'),
    # Corrections for regex collisions
    'Amazon Business Prime': ('American Express', 'Amex'),
    'Citigold Private Client': ('Citi', 'Citi'),
    'AAdvantage Aviator': ('Barclays', 'Barclays'),
    'AAdvantage Executive': ('Citi', 'Citi'),
    'AAdvantage MileUp': ('Citi', 'Citi'),
    'AAdvantage Platinum Select': ('Citi', 'Citi'),
    'Ally Debit': ('Ally', 'Other US'),
    'NFCU More Rewards American Express\u00ae Card': ('Navy Federal', 'Other US'),
    'NFCU More Rewards American Express® Card': ('Navy Federal', 'Other US'),
    'NFCU Flagship Travel Rewards Credit Card': ('Navy Federal', 'Other US'),
    'OCCU The Duck Card': ('OCCU', 'Other US'),
    'TD Aeroplane': ('TD', 'Other US'),
    'TD First Class Travel': ('TD', 'Other US'),
    'Wealthsimple': ('Wealthsimple', 'Other US'),
    'World Elite Business': ('World Elite', 'Other US'),
    'eMGC': ('Mastercard Gift', 'Other US'),
    'T-Mobile K&amp;S eMGC': ('T-Mobile', 'Other US'),
    'T-Mobile K&S eMGC': ('T-Mobile', 'Other US'),
    'Sutton Bank MGC': ('Sutton Bank', 'Other US'),
    'Hyatt Digital Key': ('Hyatt', 'Other US'),
    'Send': ('Zelle', 'Other US'),
    'RBC Avion VI': ('RBC', 'Other US'),
    # US state ID cards
    'Arizona': ('State ID', 'Other US'),
    'California': ('State ID', 'Other US'),
    'Georgia': ('State ID', 'Other US'),
    'Maryland': ('State ID', 'Other US'),
    'Ohio': ('State ID', 'Other US'),
    'Hawaii': ('State ID', 'Other US'),
    'Iowa': ('State ID', 'Other US'),
    'Puerto Rico': ('State ID', 'Other US'),
    'New Mexico': ('State ID', 'Other US'),
    # UK cards  
    'Monzo Debit': ('Monzo', 'Other UK'),
    'Amex British Airways': ('American Express', 'Other UK'),
    'Chase UK Debit': ('Chase', 'Other UK'),
    'Curve': ('Curve', 'Other UK'),
    'Starling Bank': ('Starling Bank', 'Other UK'),
    'Amex Flying Blue': ('American Express', 'Other EU'),
}

# URL-based issuer detection as fallback
URL_PATTERNS = {
    r'chase': ('Chase', 'Chase'),
    r'boa|bankamerica': ('Bank of America', 'Bank of America'),
    r'citi': ('Citi', 'Citi'),
    r'amex': ('American Express', 'Amex'),
    r'discover': ('Discover', 'Discover'),
    r'wellsfargo|propel': ('Wells Fargo', 'Wells Fargo'),
    r'usbank': ('US Bank', 'US Bank'),
    r'hsbc': ('HSBC', 'Other US'),
    r'barclay': ('Barclays', 'Barclays'),
    r'quicksilver|venture': ('Capital One', 'Capital One'),
}


def parse_swift_entries(text):
    """Extract CommunityCard entries from Swift-like text."""
    pattern = r'CommunityCard\(id:\s*"([^"]*)",\s*name:\s*"([^"]*)",\s*issuer:\s*"([^"]*)",\s*country:\s*"([^"]*)",\s*category:\s*"([^"]*)",\s*imageURL:\s*"([^"]*)",\s*author:\s*(nil|"[^"]*")\)'
    cards = []
    for m in re.finditer(pattern, text):
        cards.append({
            'id': m.group(1),
            'name': m.group(2),
            'old_issuer': m.group(3),
            'country': m.group(4),
            'category': m.group(5),
            'url': m.group(6),
            'author': m.group(7),
        })
    return cards


def fix_issuer(card):
    """Determine the correct issuer and category for a card."""
    name = card['name']
    url = card['url']
    
    # Handle ambiguous names where URL determines correct issuer
    AMBIGUOUS = {
        'Green': [
            (r'amexgreen', 'American Express', 'Amex'),
            (r'hmbradley', 'HMBradley', 'Other US'),
            (r'discover|uscardforum.*9cf1c', 'Discover', 'Discover'),
        ],
        'Pride': [
            (r'discover', 'Discover', 'Discover'),
            (r'usbank|uscardforum.*ddf97', 'US Bank', 'US Bank'),
        ],
        'Debit': [
            (r'amex|974570e', 'American Express', 'Amex'),
            (r'citi|23c79b', 'Citi', 'Citi'),
        ],
        'debit': [
            (r'amex|974570e', 'American Express', 'Amex'),
        ],
        'Premier Credit': [
            (r'db5cd1', 'HSBC', 'Other US'),
            (r'867681', 'HSBC', 'Other US'),
        ],
    }
    if name in AMBIGUOUS:
        for pat, issuer, cat in AMBIGUOUS[name]:
            if re.search(pat, url, re.IGNORECASE):
                return issuer, cat
    
    # Check exact name overrides first
    if name in NAME_OVERRIDES:
        issuer, cat = NAME_OVERRIDES[name]
        return issuer, cat
    
    # Check HTML entity version
    name_decoded = name.replace('&amp;', '&')
    if name_decoded in NAME_OVERRIDES:
        issuer, cat = NAME_OVERRIDES[name_decoded]
        return issuer, cat
    
    # Check regex rules
    for name_pat, url_pat, issuer, cat in RULES:
        if re.search(name_pat, name, re.IGNORECASE):
            return issuer, cat
        # Also check URL for clues
        url_base = url.split('/')[-1].lower()
        if re.search(url_pat, url_base, re.IGNORECASE):
            return issuer, cat
    
    # Check URL patterns as final fallback
    url_lower = url.lower()
    for pat, (issuer, cat) in URL_PATTERNS.items():
        if re.search(pat, url_lower):
            return issuer, cat
    
    # If card was already correctly assigned to a known issuer, keep it
    known_issuers = {'American Express', 'Chase', 'Citi', 'Capital One', 'Barclays', 
                     'Discover', 'HSBC', 'US Bank', 'Bank of America', 'Wells Fargo', 'Synchrony'}
    if card['old_issuer'] in known_issuers:
        return card['old_issuer'], card['category']
    
    # Default: Other US
    return card['old_issuer'], 'Other US'


def make_id(issuer, name):
    """Generate a clean unique-ish id."""
    prefix = issuer.lower().replace(' ', '-').replace('/', '-').replace('&', 'and')[:15]
    suffix = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:30]
    return f"{prefix}-{suffix}"


def generate_swift(cards):
    """Generate clean Swift builtInCards array."""
    # Fix all issuers
    for card in cards:
        issuer, cat = fix_issuer(card)
        card['issuer'] = issuer
        card['category'] = cat
    
    # Detect UK/EU cards that got country=US
    for card in cards:
        if card['category'] == 'Other UK':
            card['country'] = 'UK'
        elif card['category'] == 'Other EU':
            card['country'] = 'EU'
    
    # Deduplicate: keep first URL for each (issuer, name) pair, but allow alt URLs as separate entries with suffix
    seen = {}
    deduped = []
    for card in cards:
        key = (card['issuer'], card['name'])
        if key not in seen:
            seen[key] = 1
            card['id'] = make_id(card['issuer'], card['name'])
            deduped.append(card)
        else:
            seen[key] += 1
            # Add as alt version
            alt_name = f"{card['name']} (alt {seen[key]})"
            card['name'] = alt_name
            card['id'] = make_id(card['issuer'], alt_name)
            deduped.append(card)
    
    # Sort by country → category → issuer → name
    CATEGORY_SORT = {
        'Amex': 0, 'Chase': 1, 'Capital One': 2, 'Citi': 3, 
        'Bank of America': 4, 'Barclays': 5, 'Discover': 6, 
        'US Bank': 7, 'Wells Fargo': 8, 'Other US': 9,
        'Other UK': 10, 'Other EU': 11,
    }
    deduped.sort(key=lambda c: (
        0 if c['country'] == 'US' else 1,
        CATEGORY_SORT.get(c['category'], 99),
        c['issuer'],
        c['name'],
    ))
    
    # Generate Swift
    lines = []
    current_section = None
    for card in deduped:
        section = f"{card['country']} ── {card['issuer']}"
        if section != current_section:
            if current_section:
                lines.append("")
            lines.append(f"    // ── {card['country']} ── {card['issuer']} ──")
            current_section = section
        
        author = card['author']
        name_escaped = card['name'].replace('"', '\\"')
        issuer_escaped = card['issuer'].replace('"', '\\"')
        
        lines.append(
            f'    CommunityCard(id: "{card["id"]}", name: "{name_escaped}", '
            f'issuer: "{issuer_escaped}", country: "{card["country"]}", '
            f'category: "{card["category"]}", '
            f'imageURL: "{card["url"]}", author: {author}),'
        )
    
    return '\n'.join(lines), deduped


def main():
    # Read the parser output
    input_file = r"C:\Users\j4v13\AppData\Roaming\Code\User\workspaceStorage\09c6b337373b40ea1516e5b369282894\GitHub.copilot-chat\chat-session-resources\1df5a08a-dce3-45c4-9e6f-b67e9aaf2fec\toolu_bdrk_0186gfGixWHvikJdiQ52tuYR__vscode-1775344887979\content.txt"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    cards = parse_swift_entries(text)
    print(f"Parsed {len(cards)} raw cards")
    
    swift_code, deduped = generate_swift(cards)
    
    # Stats
    issuers = {}
    categories = {}
    countries = {}
    for c in deduped:
        issuers[c['issuer']] = issuers.get(c['issuer'], 0) + 1
        categories[c['category']] = categories.get(c['category'], 0) + 1
        countries[c['country']] = countries.get(c['country'], 0) + 1
    
    print(f"\nTotal unique cards: {len(deduped)}")
    print(f"\nCountries: {dict(sorted(countries.items()))}")
    print(f"\nCategories:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print(f"\nIssuers:")
    for iss, count in sorted(issuers.items()):
        print(f"  {iss}: {count}")
    
    # Write output
    output_file = r"D:\CardioSword\builtInCards_fixed.swift"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("private let builtInCards: [CommunityCard] = [\n")
        f.write(swift_code)
        f.write("\n]\n")
    
    print(f"\nWrote to {output_file}")


if __name__ == '__main__':
    main()
