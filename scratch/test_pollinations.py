import requests
import json

def test_pollinations_get():
    prompt = "Generate a JSON with one field 'test': 'hello world'. Respond only with JSON."
    url = f"https://text.pollinations.ai/{prompt}"
    params = {
        "model": "qwen",
        "json": "true"
    }
    print(f"Testing GET request to: {url}")
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_pollinations_get()
