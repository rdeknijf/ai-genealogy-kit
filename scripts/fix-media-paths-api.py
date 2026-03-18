#!/usr/bin/env python3
"""Fix media paths in Gramps Web: strip /root/gramps/ prefix via REST API."""
import json
import os
import sys
import urllib.request

BASE_URL = os.environ["GRAMPSWEB_URL"]
USER = os.environ["GRAMPSWEB_USER"]
PASSWORD = os.environ["GRAMPSWEB_PASSWORD"]

def api(method, path, data=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# Authenticate
auth_data = json.dumps({"username": USER, "password": PASSWORD}).encode()
req = urllib.request.Request(f"{BASE_URL}/api/token/", data=auth_data, method="POST")
req.add_header("Content-Type", "application/json")
with urllib.request.urlopen(req) as resp:
    TOKEN = json.loads(resp.read())["access_token"]

# Fetch all media objects
page = 1
fixed = 0
skipped = 0
while True:
    media_list = api("GET", f"/api/media/?page={page}&pagesize=50")
    if not media_list:
        break
    for m in media_list:
        old_path = m["path"]
        if old_path.startswith("/root/gramps/"):
            m["path"] = old_path.removeprefix("/root/gramps/")
            handle = m["handle"]
            api("PUT", f"/api/media/{handle}", m)
            fixed += 1
            print(f"  Fixed: {old_path} → {m['path']}")
        else:
            skipped += 1
    page += 1

print(f"\nDone: {fixed} fixed, {skipped} already OK")
