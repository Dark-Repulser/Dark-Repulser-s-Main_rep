import requests  # Librería para conectar con APIs
import pandas as pd  # Nota: Corrige el import de pandas

client_id = {VARIABLE DE ENTORNO} 
client_secret = {VARIABLE DE ENTORNO}  
refresh_token = {VARIABLE DE ENTORNO}  
access_token = {VARIABLE DE ENTORNO}

# Función para obtener un nuevo access token usando el refresh token
def refresh_access_token():
    global access_token  # Necesitamos actualizar la variable global
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


# Encabezados que se deben poner según la documentación de Zoho
headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}"
}


ids = [4402173000542462403]


all_data = []


for cadaid in ids:
    # URL para buscar por ID según la documentación de la API de Zoho
    url = f'https://www.zohoapis.com/crm/v2/Leads/{cadaid}'

    # Realizar la solicitud GET
    response = requests.get(url, headers=headers)
    
    # Solo se activa si la conexión es exitosa (código: 200)
    if response.status_code == 200:
        data = response.json()
        print(data)
        
        all_data.extend(data.get('data', []))
    else:
        print(f"Error al obtener datos para el ID {cadaid}: {response.status_code}")
        print(response.text)

df = pd.DataFrame(all_data)

print(df)


csv = df.to_csv('test_o1.csv')

