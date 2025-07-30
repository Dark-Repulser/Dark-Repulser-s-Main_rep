import requests

REFRESH_TOKEN = "1000.f2b6b27f10859fe33e74b38ec7624137.f890092bfc96c3d1c14e052f171eac80"
CLIENT_ID = "1000.MJQNWM6HFG34LUVG0LG7SAP1RV6T4U"
CLIENT_SECRET = "bde5461bde3baf3bc40f696dc4d53045ef6fc85f31"

access_token_global = None

def refresh_zoho_token():
    global access_token_global
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        access_token_global = response.json()["access_token"]
        return access_token_global
    else:
        return None

def hacer_peticion_zoho(url, metodo="GET", data=None, headers=None, reintento=True):
    global access_token_global
    if not access_token_global:
        refresh_zoho_token()
    headers = headers or {}
    headers["Authorization"] = f"Zoho-oauthtoken {access_token_global}"
    if metodo.upper() == "GET":
        response = requests.get(url, headers=headers)
    elif metodo.upper() == "POST":
        response = requests.post(url, headers=headers, json=data)
    else:
        raise ValueError("Método HTTP no soportado")
    if response.status_code == 401 and reintento:
        refresh_zoho_token()
        return hacer_peticion_zoho(url, metodo, data, headers, reintento=False)
    return response
