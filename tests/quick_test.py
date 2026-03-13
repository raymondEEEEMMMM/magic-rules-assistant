#!/usr/bin/env python3
import requests
import json

response = requests.get("https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/api/keyword?k=飞行", timeout=10)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
