#!/usr/bin/env python3
"""Try to find the right Dynalist API endpoint for shared docs."""
import urllib.request, json, ssl

ctx = ssl.create_default_context()
doc_id = "ldKY6rbMR3LPnWz4fTvf_HCh"

# The read_shared endpoint responded - let's see what it says
for payload in [
    {"file_id": doc_id},
    {"file_id": doc_id, "token": ""},
    {"token": "", "file_id": doc_id},
]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://dynalist.io/api/doc/read_shared",
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        body = json.loads(resp.read().decode())
        print(f"Payload: {payload}")
        print(f"  Response: {json.dumps(body, indent=2)[:500]}")
    except Exception as e:
        print(f"Payload: {payload} -> Error: {e}")

# Also try v1 endpoints
for endpoint in [
    "https://dynalist.io/api/v1/doc/read",
    "https://dynalist.io/api/v1/doc/read_shared",
]:
    for payload in [
        {"file_id": doc_id, "token": ""},
        {"file_id": doc_id},
    ]:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        try:
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)
            body = json.loads(resp.read().decode())
            code = body.get("_code", "?")
            msg = body.get("_msg", "?")
            nodes = body.get("nodes", [])
            print(f"\n{endpoint} + {payload}")
            print(f"  code={code}, msg={msg}, nodes={len(nodes)}")
            if nodes:
                print(f"  First node: {json.dumps(nodes[0])[:200]}")
        except urllib.error.HTTPError as e:
            print(f"\n{endpoint}: HTTP {e.code}")
        except Exception as e:
            print(f"\n{endpoint}: {e}")
