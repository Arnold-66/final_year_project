# test_cwa.py
import requests
import json

BASE_URL = "http://localhost:8100"

print("Testing CWA Configuration...")

# Test 1: Check if config file is served
print("\n1. Testing /cwaclientcfg.json...")
try:
    response = requests.get(f"{BASE_URL}/cwaclientcfg.json")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        config = response.json()
        print(f"Config loaded: {json.dumps(config, indent=2)[:500]}...")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Check static files
print("\n2. Testing static files...")
static_files = [
    "/static/cwa/allcsa.js",
    "/static/cwa/cwasa.css",
    "/static/cwa/cwaclientcfg.json",
]

for file in static_files:
    try:
        response = requests.head(f"{BASE_URL}{file}")
        print(f"{file}: {'✓' if response.status_code < 400 else '✗'} ({response.status_code})")
    except Exception as e:
        print(f"{file}: ✗ ({e})")