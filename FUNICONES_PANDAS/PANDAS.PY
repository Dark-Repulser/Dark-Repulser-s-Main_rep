import pandas as pd
import requests
import json
from datetime import datetime

access_token = {VARIABLE DE ENTORNO}
refresh_token = {VARIABLE DE ENTORNO}
client_id = {VARIABLE DE ENTORNO}
client_secret = {VARIABLE DE ENTORNO}
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
        print("Error al actualizar el access token:", response.status_code)  
        print(response.text)  

def get_headers():
    return {
        "Authorization": f"Zoho-oauthtoken {access_token}", 
        "Content-Type": "application/json"  
    }

def parse_duration(duration_str):
    try:
        hours, minutes, seconds = map(int, duration_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        print(f"Formato de duración inválido: {duration_str}. Usando 0 segundos.")
        return 0

# Leer el archivo CSV
df = pd.read_csv('testn - Hoja 1.csv')

no_creados = []

for index, row in df.iterrows():
    # Crear los datos que se enviarán al módulo "Calls"
    call_data = {
        "data": [
            {
                'Call_Type': row['TIPO DE LLAMADA'],
                'Call_Start_Time': datetime.strptime(row['MARCA DE HORA'], "%a, %d %b %Y %H:%M:%S").isoformat(),
                'Subject': f"Llamada con {row['NOMBRE DEL AGENTE']}",
                'Call_Duration_in_seconds': parse_duration(row['TIEMPO DE LLAMADA']),
                'Call_Result': row['DISPOSICIÓN'],
                'Phone': row['TELEFONO'],
                'Owner': {'email': row['AGENTE']},
                'Description': f"Agente: {row['NOMBRE DEL AGENTE']}\nDisposición: {row['DISPOSICIÓN']}"
            }
        ]
    }

    # URL para crear el registro en el módulo "Calls"
    create_url = "https://www.zohoapis.com/crm/v2/Calls"

    # Hacer la solicitud POST para crear el registro
    response = requests.post(create_url, headers=get_headers(), data=json.dumps(call_data))

    if response.status_code == 401:
        print("Token expirado, intentando actualizar el access token...")
        refresh_access_token()
        response = requests.post(create_url, headers=get_headers(), data=json.dumps(call_data))
    
    if response.status_code == 201:
        print(f"Llamada creada correctamente para la fila {index}.")
    else:
        print(f"Error al crear la llamada para la fila {index}: {response.status_code}")
        print(response.text)
        no_creados.append(row)

# Exportar las filas que no pudieron ser creadas
df_no_creados = pd.DataFrame(no_creados)
df_no_creados.to_csv("no_creados.csv", index=False)
print("Los registros no creados se han guardado en 'no_creados.csv'")