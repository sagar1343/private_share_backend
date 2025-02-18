import requests
from rest_framework_simplejwt.tokens import RefreshToken


def verify_google_token(token):
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def generate_token_pair(user):
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    return [access_token, refresh]
