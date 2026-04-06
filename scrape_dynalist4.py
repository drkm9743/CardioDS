#!/usr/bin/env python3
"""
Try to get a full cached or plain-text version of the dynalist document.
Use web.archive.org's raw CDX API or the Google cache.
"""
import urllib.request, json, ssl, re

ctx = ssl.create_default_context()

# Try the Wayback Machine CDX API to find snapshots
cdx_url = "https://web.archive.org/cdx/search/cdx?url=dynalist.io/d/ldKY6rbMR3LPnWz4fTvf_HCh&output=json&limit=5&fl=timestamp,statuscode,mimetype,length"
req = urllib.request.Request(cdx_url, headers={"User-Agent": "Mozilla/5.0"})
try:
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    rows = json.loads(resp.read().decode())
    print("Wayback CDX snapshots:")
    for r in rows:
        print(f"  {r}")
except Exception as e:
    print(f"CDX error: {e}")

# Try Google's text cache
google_cache = "https://webcache.googleusercontent.com/search?q=cache:dynalist.io/d/ldKY6rbMR3LPnWz4fTvf_HCh&strip=1"
req2 = urllib.request.Request(google_cache, headers={"User-Agent": "Mozilla/5.0"})
try:
    resp2 = urllib.request.urlopen(req2, timeout=15, context=ctx)
    html = resp2.read().decode("utf-8", errors="replace")
    urls = re.findall(r'https?://u\.cubeupload\.com/[^\s"\'<>\)]+', html)
    print(f"\nGoogle cache: found {len(urls)} cubeupload URLs")
    for u in urls[:20]:
        print(f"  {u}")
except Exception as e:
    print(f"\nGoogle cache error: {e}")

# Try a specific Wayback Machine snapshot URL (raw download)
# Use the id_ modifier to get the raw original content
wb_url = "https://web.archive.org/web/20251209050353id_/https://dynalist.io/d/ldKY6rbMR3LPnWz4fTvf_HCh"
req3 = urllib.request.Request(wb_url, headers={"User-Agent": "Mozilla/5.0"})
try:
    resp3 = urllib.request.urlopen(req3, timeout=20, context=ctx)
    html3 = resp3.read().decode("utf-8", errors="replace")
    urls3 = re.findall(r'https?://u\.cubeupload\.com/[^\s"\'<>\)]+', html3)
    print(f"\nWayback raw: {len(html3)} bytes, {len(urls3)} cubeupload URLs")
    if urls3:
        for u in urls3[:30]:
            print(f"  {u}")
    else:
        # Check if there's any data
        if "cubeupload" in html3:
            for m in re.finditer(r'cubeupload', html3):
                s = max(0, m.start()-50)
                e = min(len(html3), m.end()+100)  
                print(f"  Context: {html3[s:e]}")
except Exception as e:
    print(f"\nWayback raw error: {e}")
