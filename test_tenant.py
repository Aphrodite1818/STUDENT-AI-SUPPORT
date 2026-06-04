import urllib.request
import json

url = "http://127.0.0.1:8080/api/v1/tenants/register"
data = {
    "school_name": "Test Academy",
    "email": "admin@testacademy.com",
    "password": "Password123!"
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")
