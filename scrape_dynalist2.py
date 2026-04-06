#!/usr/bin/env python3
"""
Scrape dynalist using their internal API for shared documents.
The shared doc endpoint is different from the user API.
"""
import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()

# Try the shared document data endpoint
urls_to_try = [
    "https://dynalist.io/u/ldKY6rbMR3LPnWz4fTvf_HCh",
    "https://dynalist.io/api/v1/doc/read",
]

# First, let's try fetching the page and looking for the data loading XHR
# Dynalist loads shared docs via an internal endpoint
doc_id = "ldKY6rbMR3LPnWz4fTvf_HCh"

# Try the internal endpoint that shared docs use
data = json.dumps({"file_id": doc_id}).encode()
req = urllib.request.Request(
    "https://dynalist.io/doc/get_shared",
    data=data,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://dynalist.io",
        "Referer": "https://dynalist.io/d/" + doc_id,
    }
)

try:
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    body = resp.read().decode("utf-8")
    result = json.loads(body)
    print(f"Response keys: {list(result.keys())}")
    
    nodes = result.get("nodes", [])
    if not nodes and "data" in result:
        nodes = result["data"].get("nodes", [])
    
    print(f"Got {len(nodes)} nodes")
    
    # Find all cubeupload URLs in nodes
    cube_urls = []
    for node in nodes:
        content = node.get("content", "") + " " + node.get("note", "")
        urls = re.findall(r'https?://u\.cubeupload\.com/[^\s\"\'\)\]]+', content)
        for u in urls:
            cube_urls.append((node.get("content", ""), u))
    
    print(f"\nFound {len(cube_urls)} cubeupload URLs:")
    for name, url in cube_urls:
        clean_name = re.sub(r'\[.*?\]\(.*?\)', '', name).strip()
        print(f"  {clean_name}: {url}")
        
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    body = e.read().decode("utf-8", errors="replace")
    print(f"Response: {body[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Also try alternative endpoints
for endpoint in ["https://dynalist.io/doc/get", "https://dynalist.io/api/doc/read_shared"]:
    try:
        data2 = json.dumps({"file_id": doc_id}).encode()
        req2 = urllib.request.Request(
            endpoint,
            data=data2,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
                "Origin": "https://dynalist.io",
                "Referer": "https://dynalist.io/d/" + doc_id,
            }
        )
        resp2 = urllib.request.urlopen(req2, timeout=10, context=ctx)
        body2 = resp2.read().decode("utf-8")
        result2 = json.loads(body2)
        print(f"\n{endpoint}: keys={list(result2.keys())}")
    except urllib.error.HTTPError as e:
        print(f"\n{endpoint}: HTTP {e.code}")
    except Exception as e:
        print(f"\n{endpoint}: {e}")
