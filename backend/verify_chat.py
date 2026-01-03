import requests
import json
import sys

def test_chat():
    url = "http://localhost:8000/chat"
    payload = {"message": "Hello, are you online?"}
    try:
        print(f"Sending request to {url}...")
        with requests.post(url, json=payload, stream=True) as response:
            if response.status_code == 200:
                print("Response received:")
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        print(chunk.decode('utf-8'), end='', flush=True)
                print("\n\nTest Passed!")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                sys.exit(1)
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_chat()
