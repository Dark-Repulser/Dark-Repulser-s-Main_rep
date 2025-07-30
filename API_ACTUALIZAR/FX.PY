import pandas as pd
import requests
import json
from datetime import datetime

# Define los tokens y credenciales
access_token = "1000.d9a6ec9e7dddf9668be1f7bcac0812c7.ac72907364870253e5f11fb8ce70d307"
refresh_token = "1000.0b8233b62707b577fe16832434abc213.b66c40f4c700c262ce57fedb128d3f06"
client_id = "1000.9KLJEBGO230LA4N7PDKFH9G9G69WXH"
client_secret = "ccba688719aba106669ffd09fcfe1eb5ecd12e28c2"

# Función para refrescar el token de acceso
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
        global access_token
        access_token = response.json()['access_token']
        print("Access token actualizado correctamente.")
    else:
        print("Error al actualizar el access token:", response.status_code)
        print(response.text)

# Encabezados de autenticación para solicitudes
def get_headers():
    return {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

# Conversión de formato de fecha
def convert_to_datetime(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y %H:%M")

def crm_datetime_to_iso(crm_date_str):
    return datetime.fromisoformat(crm_date_str[:-6])

# Leer archivo CSV
df = pd.read_csv('no_actualizados.csv')
no_actualizados = []

# Refresca el token una vez antes del bucle principal
refresh_access_token()

for index, row in df.iterrows():
    cadaid = row['Id']
    hora_modificacion_excel = convert_to_datetime(row['hora de modificacion'])
    url = f'https://www.zohoapis.com/crm/v2/Leads/{cadaid}'

    # Solicitud para obtener los datos del registro
    response = requests.get(url, headers=get_headers())

    # Si el token ha expirado, actualízalo y reintenta la solicitud una vez
    if response.status_code == 401:
        print("Token expirado, actualizando y reintentando...")
        refresh_access_token()
        response = requests.get(url, headers=get_headers())

    if response.status_code == 200:
        crm_data = response.json().get('data', [])[0]
        print (crm_data)

#         hora_modificacion_crm_str = crm_data.get('Hora_Modificaci_n')
#         hora_modificacion_crm = crm_datetime_to_iso(hora_modificacion_crm_str)

#         # Compara las fechas para decidir si se debe actualizar
#         if hora_modificacion_excel >= hora_modificacion_crm:
#             estado = row['Estado']
#             subestado = row['sub estado']
#             subestadoII = row["sub estado II"]
#             subestadoIII = row["sub estado III"]

#             # Datos para actualización
#             update_data = {
#                 "data": [
#                     {
#                         'Estado_del_Registro': estado,
#                         'Sub_estado': subestado,
#                         'Sub_estado_II': subestadoII,
#                         'Sub_Estado_III': subestadoIII
#                     }
#                 ]
#             }

#             # Actualizar el registro
#             update_url = f"https://www.zohoapis.com/crm/v2/Leads/{cadaid}"
#             update_response = requests.put(update_url, headers=get_headers(), data=json.dumps(update_data))

#             if update_response.status_code == 200:
#                 print(f"Registro {cadaid} actualizado correctamente.")
#             else:
#                 print(f"Error al actualizar el registro {cadaid}: {update_response.status_code}")
#                 no_actualizados.append(row)
#         else:
#             print(f"No se necesita actualizar el registro {cadaid}.")
#             no_actualizados.append(row)
#     else:
#         print(f"Error al obtener datos para el ID {cadaid}: {response.status_code}")
#         no_actualizados.append(row)

# # Exporta solo una vez al final
# df.to_csv("test_2.csv", index=False)
# print("El archivo se ha guardado como 'test_2.csv'")
