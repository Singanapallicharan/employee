import requests
import json

# Firebase Realtime Database URL
url = "https://eligo-members-eaea1-default-rtdb.firebaseio.com/profiles.json"

def fetch_profiles():
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad status codes
        data = response.json()

        # Print the formatted data
        print(json.dumps(data, indent=4))

        # Optionally, return data for further processing
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    fetch_profiles()
