import requests
import json
import os

# OAuth 2.0 Configuration
AUTH_URL = "https://your-fhir-server/oauth2/authorize"
TOKEN_URL = "https://your-fhir-server/oauth2/token"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "openid profile email"

TOKEN_FILE = "access_token.json"
AUTH_CODE_FILE = "url_from_browser.txt"


def get_access_token():
    """
    Exchange authorization code for access token.
    Authorization code must be stored in url_from_browser.txt
    after user grants access via browser.
    """
    with open(AUTH_CODE_FILE, "r") as f:
        auth_code = f.read().strip()

    response = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })

    if response.status_code == 200:
        token_data = response.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
        print("Access token retrieved and saved.")
        return token_data["access_token"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def refresh_access_token():
    """
    Use refresh token to obtain a new access token
    when the current one expires.
    """
    with open(TOKEN_FILE, "r") as f:
        token_data = json.load(f)

    refresh_token = token_data.get("refresh_token")

    response = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })

    if response.status_code == 200:
        new_token_data = response.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(new_token_data, f, indent=2)
        print("Access token refreshed successfully.")
        return new_token_data["access_token"]
    else:
        print(f"Refresh failed: {response.status_code} - {response.text}")
        return None


def load_token():
    """
    Load existing access token from file.
    """
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        return token_data.get("access_token")
    return None


if __name__ == "__main__":
    token = get_access_token()
    print(f"Token: {token[:20]}..." if token else "Failed to retrieve token.")
