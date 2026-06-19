import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, path, data=None):
    print(f"\n=== {name} ===")
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            r = requests.get(url)
        else:
            r = requests.post(url, json=data)
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

# 1. Health check
test_endpoint("Health Check", "GET", "/api/health")

# 2. API Status
test_endpoint("API Status", "GET", "/api/status")

# 3. Root endpoint
test_endpoint("Root Endpoint", "GET", "/")

# 4. Contact form (success)
test_endpoint("Contact Form (valid)", "POST", "/api/contact", {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+79991234567",
    "comment": "Hello, I want to discuss a project"
})

# 5. Contact form (validation error)
test_endpoint("Contact Form (invalid email)", "POST", "/api/contact", {
    "name": "Test",
    "email": "invalid-email",
    "comment": "Test message"
})

# 6. Get all contacts
test_endpoint("Get All Contacts", "GET", "/api/contacts")

# 7. Metrics
test_endpoint("Metrics", "GET", "/api/metrics")

print("\n=== All tests completed ===")
