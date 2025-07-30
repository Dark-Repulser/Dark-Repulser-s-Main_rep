import pandas as pd
import requests
import json

# Variables globales para la autenticación en la API de Zoho
access_token = {VARIABLE DE ENTORNO}
refresh_token = {VARIABLE DE ENTORNO}
client_id = {VARIABLE DE ENTORNO}
client_secret = {VARIABLE DE ENTORNO}

# Función para refrescar el token de acceso cuando expira
def refresh_access_token():
    url = "https://accounts.zoho.com/oauth/v2/token"  # Endpoint para actualizar el token
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"  # Tipo de solicitud para actualizar el token
    }
    
    # Hacer una solicitud POST para obtener un nuevo access token
    response = requests.post(url, data=data)
    
    if response.status_code == 200:  # Si la solicitud fue exitosa
        new_tokens = response.json()  # Convertir la respuesta a formato JSON
        global access_token  # Actualizar la variable global del access token
        access_token = new_tokens['access_token']  # Asignar el nuevo access token
        print("Access token actualizado correctamente.")  # Confirmación
    else:
        print("Error al actualizar el access token:", response.status_code)  # Mensaje de error
        print(response.text)  # Imprimir respuesta de error para depuración

# Función para obtener los headers de autorización para cada solicitud
def get_headers():
    return {
        "Authorization": f"Zoho-oauthtoken {access_token}",  # Token de acceso para la autenticación
        "Content-Type": "application/json"  # Especifica que el contenido será JSON
    }

# Leer el archivo Excel que contiene los datos de Leads
df = pd.read_csv('test_1.csv')  # Asegúrate de que este Excel tiene las columnas: 'Id', 'hora de modificacion', 'estado', 'subestado'

# Lista para almacenar todos los datos obtenidos del CRM
all_data = []

# Lista para almacenar los registros que no se actualizaron
no_actualizados = []

# Iterar sobre cada fila en el archivo Excel
for index, row in df.iterrows():
    cadaid = row['Id']  # Obtener el ID de cada registro (Lead) del Excel
    hora_modificacion_excel = row['hora de modificacion']  # Hora de modificación en el archivo Excel

    # Construir la URL para obtener los datos del Lead en el CRM
    url = f'https://www.zohoapis.com/crm/v2/Leads/{cadaid}'
    
    # Hacer la solicitud GET para obtener los datos del CRM
    response = requests.get(url, headers=get_headers())

    # Manejar la expiración del token (código de error 401)
    if response.status_code == 401:
        print("Token expirado, intentando actualizar el access token...")
        refresh_access_token()  # Llamar a la función para refrescar el token
        response = requests.get(url, headers=get_headers())  # Reintentar la solicitud con el nuevo token

    # Si la solicitud GET fue exitosa (código 200)
    if response.status_code == 200:
        data = response.json()  # Convertir la respuesta a formato JSON
        crm_data = data.get('data', [])[0]  # Obtener el primer registro de la lista de datos
        
        # Obtener la hora de modificación desde el CRM
        hora_modificacion_crm = crm_data.get('Hora_Modificaci_n')

        # Comparar las horas de modificación (si la hora en Excel es mayor o igual, actualizar)
        if hora_modificacion_excel >= hora_modificacion_crm:
            # Obtener los valores de estado y subestado desde el Excel
            estado = row['Estado']
            subestado = row['sub estado']
            subestadoII =row["sub estado II"]
            subestadoIII = row["sub estado III"]

            # Preparar los datos para la actualización en el CRM
            update_data = {
                "data": [
                    {
                        'Estado_del_Registro': estado,  # Campo de estado que se actualizará
                        'Sub_estado': subestado, # Campo de subestado que se actualizará
                        'Sub_estado_II': subestadoII ,
                        'Sub_Estado_III' : subestadoIII
                    }
                ]
            }

            # Construir la URL para hacer la solicitud PUT de actualización
            update_url = f"https://www.zohoapis.com/crm/v2/Leads/{cadaid}"
            
            # Hacer la solicitud PUT para actualizar los datos en el CRM
            update_response = requests.put(update_url, headers=get_headers(), data=json.dumps(update_data))

            # Verificar si la actualización fue exitosa
            if update_response.status_code == 200:
                print(f"Registro {cadaid} actualizado correctamente.")  # Confirmación de éxito
            else:
                # Si hubo un error al actualizar, mostrar el mensaje de error
                print(f"Error al actualizar el registro {cadaid}: {update_response.status_code}")
                print(update_response.text)
                no_actualizados.append(row)  # Agregar el registro a la lista de no actualizados
        else:
            # Si la hora de modificación en el Excel es menor que en el CRM, no actualizar
            print(f"No se necesita actualizar el registro {cadaid}, la hora de modificación en el archivo es menor o igual.")
            no_actualizados.append(row)  # Agregar el registro a la lista de no actualizados
        
        # Guardar los datos obtenidos del CRM en la lista all_data
        all_data.extend(data.get('data', []))
    else:
        # Si hubo un error al obtener los datos del CRM, mostrar el mensaje de error
        print(f"Error al obtener datos para el ID {cadaid}: {response.status_code}")
        print(response.text)
        no_actualizados.append(row)  # Agregar el registro a la lista de no actualizados

# Crear un DataFrame con los datos obtenidos del CRM
df_result = pd.DataFrame(all_data)

# Crear un DataFrame con los registros que no se actualizaron
df_no_actualizados = pd.DataFrame(no_actualizados)

# Guardar los resultados en archivos Excel
df_result.to_excel('datos_obtenidos.xlsx', index=False)  # Guardar los datos obtenidos del CRM
df_no_actualizados.to_csv('no_actualizados.csv', index=False)  # Guardar los registros no actualizados
