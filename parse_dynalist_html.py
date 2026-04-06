#!/usr/bin/env python3
"""Parse the downloaded dynalist HTML to extract card name -> URL mappings with hierarchy."""
import re, json

with open(r"D:\CardioSword\Apple Pay High Res (or paypal low res) Card Backgrounds - Dynalist.htm", "r", encoding="utf-8", errors="replace") as f:
    html = f.read()

# Dynalist renders items as nested <div> elements with class "Node"
# Each node has content in a span and links in <a> tags
# Let's find all the text content with their associated cubeupload links

# Strategy: find all <a> tags that link to cubeupload and extract the preceding text
# Pattern: text content followed by link to cubeupload
# In dynalist, the link text IS the card name, and the href is the image URL

# Find all links to cubeupload
link_pattern = r'<a[^>]*href="(https?://u\.cubeupload\.com/[^"]+)"[^>]*>([^<]*)</a>'
matches = re.findall(link_pattern, html)
print(f"Found {len(matches)} direct cubeupload links with text")
for url, text in matches[:10]:
    print(f"  {text.strip()} -> {url}")

print("\n---\n")

# Also try: find all Node divs and extract hierarchy
# Dynalist uses data attributes or class names for hierarchy
# Let's look for the node structure

# Actually, let's find ALL text near cubeupload URLs
# Find patterns like: card name text ... cubeupload URL
all_cubeupload = re.findall(r'https?://u\.cubeupload\.com/[^\s"\'<>\)]+', html)
print(f"Total cubeupload URLs in HTML: {len(all_cubeupload)}")

# Let's look at the raw HTML structure around cubeupload links
for i, m in enumerate(re.finditer(r'https?://u\.cubeupload\.com/[^\s"\'<>\)]+', html)):
    start = max(0, m.start() - 300)
    end = min(len(html), m.end() + 50)
    context = html[start:end]
    # Extract text content from the context (strip HTML tags)
    text_only = re.sub(r'<[^>]+>', ' ', context)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    if i < 5:
        print(f"\n--- Context {i} ---")
        print(f"URL: {m.group()}")
        print(f"Text context: ...{text_only[-200:]}...")

# Let's also look for the hierarchy markers (country/issuer/category)
# Find all "Node-contentContainer" or similar class content
node_contents = re.findall(r'class="[^"]*Node-contentContainer[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
print(f"\nFound {len(node_contents)} Node-contentContainer elements")

# Better approach: extract all visible text content in order
# Remove script/style tags first
clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)

# Find all lines that contain cubeupload
lines_with_cube = []
for line in clean.split('\n'):
    if 'cubeupload.com' in line:
        # Extract the URL
        url_match = re.search(r'https?://u\.cubeupload\.com/[^\s"\'<>\)]+', line)
        # Extract text content  
        text = re.sub(r'<[^>]+>', '', line).strip()
        if url_match:
            lines_with_cube.append((text, url_match.group()))

print(f"\nLines with cubeupload ({len(lines_with_cube)} total):")
for text, url in lines_with_cube[:20]:
    # Clean up the text
    text = re.sub(r'\s+', ' ', text).strip()
    print(f"  [{text[:80]}] -> {url}")
