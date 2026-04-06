#!/usr/bin/env python3
"""Scrape all cubeupload URLs from the dynalist shared page."""
import urllib.request
import re
import json
import ssl

ctx = ssl.create_default_context()
url = "https://dynalist.io/d/ldKY6rbMR3LPnWz4fTvf_HCh"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})
resp = urllib.request.urlopen(req, timeout=30, context=ctx)
html = resp.read().decode("utf-8", errors="replace")

# Look for cubeupload URLs
cube_urls = re.findall(r'https?://u\.cubeupload\.com/[^\s"\'<>]+\.png', html)
cube_urls2 = re.findall(r'https?://u\.cubeupload\.com/[^\s"\'<>]+', html)

print(f"Found {len(cube_urls)} PNG URLs, {len(cube_urls2)} total cubeupload URLs")
for u in sorted(set(cube_urls)):
    print(u)

# Also look for any JSON data embedded in the page
json_blocks = re.findall(r'nodeMap\s*[:=]\s*(\{[^}]{100,})', html)
print(f"\nFound {len(json_blocks)} potential JSON blocks")

# Look for any data that might contain card info
if "cubeupload" in html:
    # Find context around cubeupload mentions
    for m in re.finditer(r'cubeupload', html):
        start = max(0, m.start() - 100)
        end = min(len(html), m.end() + 100)
        snippet = html[start:end].replace('\n', ' ')
        print(f"\nContext: ...{snippet}...")

# Check if there's initial state / preloaded data
state_match = re.search(r'__INITIAL_STATE__\s*=\s*(\{.*?\});', html, re.DOTALL)
if state_match:
    print("\nFound __INITIAL_STATE__!")
    
# Look for any window.xxx data
for pattern in [r'window\.__data\s*=\s*(\{.*?\});', r'window\.nodeData\s*=\s*(\[.*?\]);', r'"nodes"\s*:\s*\[']:
    matches = re.findall(pattern, html[:50000], re.DOTALL)
    if matches:
        print(f"\nFound pattern '{pattern}': {len(matches)} matches")

print(f"\nTotal HTML size: {len(html)} bytes")
# Print first 2000 chars to see page structure  
print("\nFirst 2000 chars:")
print(html[:2000])
