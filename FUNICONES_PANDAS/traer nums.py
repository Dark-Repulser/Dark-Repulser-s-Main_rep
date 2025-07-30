import requests
import pandas as pd

# Configuración de tokens y credenciales
access_token = "1000.dba34ae264a19812708646cd6d75d6ce.eb303209057c5ed8fb8de2d258c7b774"
refresh_token = "1000.d09996e678c6cedda7c07a06c62f297e.a2c6ea6e22561e3e18913b1e18510b56"
client_id = "1000.9KLJEBGO230LA4N7PDKFH9G9G69WXH"
client_secret = "ccba688719aba106669ffd09fcfe1eb5ecd12e28c2"
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

# Función para buscar un lead por número de teléfono
def buscar_lead_por_numero(telefono):
    url = f'https://www.zohoapis.com/crm/v2/Leads/search?criteria=(Phone:equals:{telefono})'
    response = requests.get(url, headers=get_headers())

    if response.status_code == 401:  # Si el token está expirado
        print("Token expirado, intentando actualizar el access token...")
        refresh_access_token()
        response = requests.get(url, headers=get_headers())  # Intenta de nuevo con el nuevo token

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            lead = data['data'][0]
            return lead['id'], lead.get('Full_Name', 'Nombre no disponible')  # Retorna el ID y el nombre
        else:
            print(f"No se encontró lead con el número: {telefono}")
            return None, None
    else:
        print(f"Error al buscar el lead con el número {telefono}: {response.status_code}")
        print(response.text)
        return None, None

# Función principal para procesar todos los números del CSV y obtener los IDs y nombres
def procesar_leads(csv_file):
    df = pd.read_csv(csv_file)
    lead_data = []  # Lista para almacenar los IDs y nombres de los leads

    for index, row in df.iterrows():
        telefono = row['TELEFONO ']  # Número de teléfono del CSV
        print(f"Buscando lead con número {telefono}...")

        # Buscar el lead y obtener su ID y nombre
        lead_id, lead_name = buscar_lead_por_numero(telefono)
        
        if lead_id:
            lead_data.append({"Telefono": telefono, "Lead ID": lead_id, "Nombre": lead_name})

    # Crear un dataframe con los resultados
    df_leads = pd.DataFrame(lead_data)
    return df_leads

# Archivo CSV con los números de teléfono
csv_file = 'updated_telefonos.csv' 

# Procesar los leads y obtener los IDs y nombres
df_leads = procesar_leads(csv_file)
print(df_leads)

# Guardar los resultados en un archivo CSV
df_leads.to_csv("Leads_IDS_Nombres.csv", index=False)
