#!/usr/bin/env python3
import requests
import json

def test_trending_endpoint():
    print("Testing trending endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/crypto/trending")
        if response.status_code == 200:
            data = response.json()
            print("Success! Endpoint returned status 200")
            print(f"Number of trending coins: {len(data.get('coins', []))}")
            if 'coins' in data and data['coins']:
                print("First trending coin:", json.dumps(data['coins'][0], indent=2))
            return True
        else:
            print(f"Error: Endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_trending_endpoint() 