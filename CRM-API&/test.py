import requests
import json  

# Configuración de tokens y credenciales
access_token = "1000.b8ebe2c3abcb90f1d15469a24cc723c2.c7c34fea599261b25b2da5e2d7ae677f"
refresh_token = "1000.f070420cfb6ec12db91d5b8bfba8695e.3418b69edd4551861203a9681e4bee27"
client_id = "1000.92V4JIXVSDFU7O8AY0KF18OE32TCTS"
client_secret = "9010dbc06967b15c0a45476a5134bf28a605616eb6"
org_id = '707762349'

# Función para refrescar el access token
def refresh_access_token():
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        new_tokens = response.json()
        global access_token
        access_token = new_tokens['access_token']
        print("Access token actualizado correctamente.")
    else:
        print(f"Error al actualizar el access token: {response.status_code}")
        print(response.text)

# Función para generar los headers
def get_headers():
    return {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'orgId': org_id,
        'Content-Type': 'application/json'
    }

# Función para buscar un ticket por su número y obtener su información
def obtener_datos_ticket(ticket_number):
    url = f'https://desk.zoho.com/api/v1/tickets/search?limit=1&ticketNumber={ticket_number}'
    response = requests.get(url, headers=get_headers())

    if response.status_code == 401:  # Si el token está expirado
        print("Token expirado, intentando actualizar el access token...")
        refresh_access_token()
        response = requests.get(url, headers=get_headers())  # Intenta de nuevo con el nuevo token

    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return data['data'][0]  # Retorna la información completa del ticket
        else:
            print("No se encontró el ticket.")
            return None
    else:
        print(f"Error al obtener el ticket: {response.status_code}")
        print(response.text)
        return None

# Solicitar número de ticket al usuario
ticket_number = input("Ingrese el número de ticket: ")
ticket_data = obtener_datos_ticket(ticket_number)

if ticket_data:
    print("Información del Ticket:")
    print(json.dumps(ticket_data, indent=4, ensure_ascii=False))