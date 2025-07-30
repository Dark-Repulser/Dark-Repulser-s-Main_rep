import os
import requests
import threading
import time
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno
# Este código ya está configurado para leer los IDs del archivo CSV y eliminarlos del CRM.
# Asegúrate de que el archivo CSV tenga una columna llamada 'ID' con los IDs de los registros a eliminar.
dotenv_path = r"C:\Users\david_romerom\OneDrive - Corporación Unificada Nacional de Educación Superior - CUN\Documentos\cs.env"
load_dotenv(dotenv_path=dotenv_path)

ACCESS_TOKEN = os.getenv("ACCESSTK")
REFRESH_TOKEN = os.getenv("REFRESHTK")
CLIENT_ID = os.getenv("CLIENTID")
CLIENT_SECRET = os.getenv("CLIENTST")

# URLs de Zoho
token_url = "https://accounts.zoho.com/oauth/v2/token"
base_url = "https://www.zohoapis.com/crm/v5/Leads"

THREAD_LIMIT = 10  # Límite de hilos simultáneos

def refresh_access_token():
    """Refresca el access token si ha expirado."""
    global ACCESS_TOKEN
    data = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        ACCESS_TOKEN = response.json()['access_token']
        print("Access token actualizado correctamente.")
    else:
        raise Exception(f"Error al actualizar el token: {response.status_code} {response.text}")

def get_headers():
    """Genera los headers para la autenticación en Zoho CRM."""
    return {
        "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def delete_record(record_id):
    """Elimina un registro de Zoho CRM por ID."""
    url = f"{base_url}/{record_id}"
    response = requests.delete(url, headers=get_headers())

    if response.status_code == 401:  # Token expirado
        print(f"Token expirado, renovando...")
        refresh_access_token()
        response = requests.delete(url, headers=get_headers())

    if response.status_code == 200:
        print(f"Registro {record_id} eliminado correctamente.")
    else:
        print(f"Error al eliminar {record_id}: {response.status_code} {response.text}")

def delete_records_from_csv(file_path="BORRAR.csv"):
    """Lee un archivo CSV y elimina los registros en Zoho CRM usando la columna 'id'."""
    try:
        df = pd.read_csv(file_path)  # Cargar CSV
        if "ID" not in df.columns:
            print("El archivo CSV debe tener una columna 'ID'.")
            return
        
        record_ids = df["ID"].dropna().astype(str).tolist()
        if not record_ids:
            print("No hay IDs en el archivo CSV.")
            return

        print(f"Se encontraron {len(record_ids)} registros para eliminar.")
        
        threads = []
        for record_id in record_ids:
            while threading.active_count() > THREAD_LIMIT:
                time.sleep(1)
            thread = threading.Thread(target=delete_record, args=(record_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print("Proceso de eliminación completado.")
    
    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")

# Ejecutar la función de eliminación
delete_records_from_csv()
