import requests

release = True

if not release:
    client_id = 755645853590356099
    client_secret = "igqAYbPcGlQqkiMG3RW3hS5ciR9nCTNR"
    redirect_uri = "http://127.0.0.1/auth"
else:
    client_id = 752367350657056851
    client_secret = " "
    redirect_uri = " "


def gat(code):
    global client_id, client_secret, redirect_uri

    data = {
        "client_id": str(client_id),
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": "identify%20email%20guilds"
    }

    at = requests.post(url="https://discord.com/api/oauth2/token", data=data).json()
    return at.get("access_token")

def get_user_json(access_token):
    url = "https://discord.com/api/users/@me"
    headers = {"Authorization": f"Bearer {access_token}"}

    user_obj = requests.get(url, headers=headers).json()
    return user_obj

def get_guilds(access_token):
    url = "https://discord.com/api/guilds/@me"
    headers = {"Authorization": f"Bearer {access_token}"}

    user_obj = requests.get(url, headers=headers).json()
    return user_obj