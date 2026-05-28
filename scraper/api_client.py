
import httpx
import json
import os
import sys

API_URL = os.getenv("BED_API_URL", "http://localhost:8787/api/data")
API_TOKEN = os.getenv("BED_API_TOKEN", "")

def send_to_api(data: list):
    """Send scraped bed data to the Cloudflare Worker API."""
    payload = {"rows": data}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
    }
    try:
        resp = httpx.post(API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        print(f"Inserted {result.get('inserted', 0)} rows via API")
    except Exception as e:
        print(f"Failed to send data to API: {e}")
        sys.exit(1)
