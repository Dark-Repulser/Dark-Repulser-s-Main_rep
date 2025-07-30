import pandas as pd
import requests
import json
from datetime import datetime

access_token = {VARIABLE DE ENTORNO}
refresh_token = {VARIABLE DE ENTORNO}
client_id = {VARIABLE DE ENTORNO}
client_secret = {VARIABLE DE ENTORNO}

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
        new_tokens = response.json()
        global access_token
        access_token = new_tokens['access_token']
        print("Access token actualizado correctamente.")
    else:
        print("Error al actualizar el access token:", response.status_code)
        print(response.text)

# Función para obtener encabezados de autenticación
def get_headers():
    return {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

# Función para convertir la fecha del CSV en formato datetime
def convert_to_datetime(date_str):
    # Cambiado el formato de fecha para coincidir con el formato en el archivo 'm/d/yy H:M'
    return datetime.strptime(date_str, "%d/%m/%Y %H:%M")

# Función para convertir la fecha del CRM en formato datetime
def crm_datetime_to_iso(crm_date_str):
    if crm_date_str:
        return datetime.fromisoformat(crm_date_str[:-6])
    return None

# Inicializar lista para registros no actualizados
no_actualizados = []

# Función recursiva para procesar registros binarios
def process_records_binary(df, start, end):
    if start > end:
        return

    mid = (start + end) // 2
    row = df.iloc[mid]
    cadaid = row['Id']
    hora_modificacion_excel = convert_to_datetime(row['Hora_de_modificación'])
    
    url = f'https://www.zohoapis.com/crm/v2/Leads/{cadaid}'
    response = requests.get(url, headers=get_headers())

    if response.status_code == 401:
        print("Token expirado, intentando actualizar el access token...")
        refresh_access_token()
        return process_records_binary(df, start, end)  

    if response.status_code == 200:
        data = response.json()
        crm_data = data.get('data', [])[0]  # Obtener el primer registro
        hora_modificacion_crm_str = crm_data.get('Hora_Modificaci_n')
        hora_modificacion_crm = crm_datetime_to_iso(hora_modificacion_crm_str)

        if hora_modificacion_crm is None or hora_modificacion_excel >= hora_modificacion_crm:
            # Datos para actualización (para el test, se asignan valores ficticios)
            subestado =  row['Sub_Estado']
            subestadoII =  row["Sub_Estado_II"]
            subestadoIII = row["Sub_Estado_III"]
            etapa = row["Etapa_del_Registro"]
            update_data = {
                "data": [{
                    'Sub_estado': subestado,
                    'Sub_estado_II': subestadoII,
                    'Sub_Estado_III': subestadoIII,
                    'Estado_del_Registro' : etapa
                }]
            }

            # Aquí comentarías la actualización para pruebas
            update_url = f"https://www.zohoapis.com/crm/v2/Leads/{cadaid}"
            update_response = requests.put(update_url, headers=get_headers(), data=json.dumps(update_data))

            if update_response.status_code != 200:
                 no_actualizados.append(row)
        else:
            # Añadir registro no actualizado a la lista
            no_actualizados.append(row)
    else:
        # Si hay error, añadir registro no actualizado
        no_actualizados.append(row)
    
    # Llamadas recursivas para el siguiente registro
    process_records_binary(df, start, mid - 1)
    process_records_binary(df, mid + 1, end)

# Cargar datos y ejecutar el procesamiento
df = pd.read_csv('Libro2_modified.csv')

# Ejecutar el proceso de actualización
process_records_binary(df, 0, len(df) - 1)

# Guardar registros no actualizados en CSV
no_actualizados_df = pd.DataFrame(no_actualizados)
no_actualizados_df.to_csv("no_actualizados.csv", index=False)

print("Proceso completado. Archivo 'test_one.csv' generado con registros no actualizados.")
