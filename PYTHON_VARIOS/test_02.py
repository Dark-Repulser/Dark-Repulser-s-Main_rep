import requests
import pandas as pd

# Credenciales necesarias
client_id = "1000.92V4JIXVSDFU7O8AY0KF18OE32TCTS"
client_secret = "9010dbc06967b15c0a45476a5134bf28a605616eb6"
refresh_token = "1000.fe76d63c71bd6131fdc8a4b288733f30.6e8b13a14a18a7ee7b316e700f507b29"
access_token = "1000.c005b41d9cef844c764b5659371dc2eb.cd2e8437710e70d22e85893cf8cba866"

# Función para obtener un nuevo access token usando el refresh token
def refresh_access_token():
    global access_token
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
        access_token = new_tokens['access_token']
        print("Access token actualizado correctamente.")
    else:
        print("Error al actualizar el access token:", response.status_code)
        print(response.text)
        raise Exception("No se pudo actualizar el access token")

# Función para obtener datos de tickets desde Zoho Desk
def fetch_tickets_and_save_to_csv():
    global access_token

    # Refrescar token al inicio
    refresh_access_token()

    # Configuración inicial
    org_id = '707762349'
    per_page = 100  # Número máximo de registros por página
    ticket_data = []  # Lista para almacenar la información de los tickets
    url = 'c'

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "orgId": org_id,
        "Content-Type": "application/json"
    }

    # Paginación para obtener todos los tickets
    page = 1
    while True:
        params = {
            'from': (page - 1) * per_page + 1,  # Índice inicial de los datos
            'limit': per_page  # Límite de datos por página
        }
        response = requests.get(url, headers=headers, params=params)

        # Si el token ha expirado, refrescarlo y reintentar
        if response.status_code == 401:  # Código de token expirado
            print("Token expirado. Actualizando...")
            refresh_access_token()
            headers["Authorization"] = f"Zoho-oauthtoken {access_token}"
            response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        # Obtener los datos de los tickets
        tickets = response.json().get('data')
        if not tickets:  # Salir si no hay más tickets
            break

        # Procesar e imprimir los datos de cada ticket
        for ticket in tickets:
            ticket_id = ticket.get("ticketNumber", "ID desconocido")
            print(f"Ticket número {ticket_id} extraído")
            ticket_data.append(ticket)

        # Incrementar la página para la siguiente iteración
        page += 1

    # Guardar los datos en un archivo CSV
    df = pd.DataFrame(ticket_data)
    df.to_csv('tickets_full_data.csv', index=False)
    print("Archivo 'tickets_full_data.csv' creado exitosamente.")

# Ejecutar la función
fetch_tickets_and_save_to_csv()
