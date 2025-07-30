import requests
import pandas as pd

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

# Función para buscar un ticket por su número y obtener su ID
def buscar_ticket_por_numero(ticket_number):
    url = f'https://desk.zoho.com/api/v1/tickets/search?limit=1&ticketNumber={ticket_number}'
    response = requests.get(url, headers=get_headers())

    if response.status_code == 401:  # Si el token está expirado
        print("Token expirado, intentando actualizar el access token...")
        refresh_access_token()
        response = requests.get(url, headers=get_headers())  # Intenta de nuevo con el nuevo token

    if response.status_code == 200:
        data = response.json()
        print(data)
        if 'data' in data and len(data['data']) > 0:
            return data['data'][0]['id']  # Retorna el ID del ticket print(data)
        else:
            print(f"No se encontró ticket con el número: {ticket_number}")
            return None
    else:
        print(f"Error al buscar el ticket {ticket_number}: {response.status_code}")
        print(response.text)
        return None

# Función principal para procesar todos los tickets del CSV y obtener los IDs
def procesar_tickets(test_csv):
    df = pd.read_csv(test_csv)
    ticket_ids = []  # Lista para almacenar los IDs de los tickets

    for index, row in df.iterrows():
        ticket_number = row['tnum']  # Número de ticket del CSV
        print(f"Buscando ticket {ticket_number}...")

        # Buscar el ticket y obtener su ID
        ticket_id = buscar_ticket_por_numero(ticket_number)
        
        if ticket_id:
            ticket_ids.append({"Ticket Number": ticket_number, "Ticket ID": ticket_id})

    # Crear un dataframe con los resultados
    df_ids = pd.DataFrame(ticket_ids)
    return df_ids


csv_file = 'test.csv' 

df_ids = procesar_tickets(csv_file)




