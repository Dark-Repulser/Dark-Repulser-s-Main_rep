import os
import requests
import threading
import time
from dotenv import load_dotenv

# Cargar variables de entorno
dotenv_path = r"C:\Users\david_romerom\OneDrive - Corporación Unificada Nacional de Educación Superior - CUN\Documentos\cs.env"
load_dotenv(dotenv_path=dotenv_path)

ACCESS_TOKEN = os.getenv("ACCESSTK")
REFRESH_TOKEN = os.getenv("REFRESHTK")
CLIENT_ID = os.getenv("CLIENTID")
CLIENT_SECRET = os.getenv("CLIENTST")

# URLs de Zoho
token_url = "https://accounts.zoho.com/oauth/v2/token"
base_url = "https://www.zohoapis.com/crm/v5/Egresados_filantropia"

OWNER_ID_ACTUAL = "4402173000000251001"
OWNER_ID_NUEVO = "4402173000686613005"
PER_PAGE = 200
MAX_PAGES = 5
THREAD_LIMIT = 10  # Límite de hilos simultáneos

def refresh_access_token():
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
    return {
        "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def fetch_records(page):
    params = {"criteria": f"(Owner.id:equals:{OWNER_ID_ACTUAL})", "page": page, "per_page": PER_PAGE}
    response = requests.get(f"{base_url}/search", headers=get_headers(), params=params)
    
    if response.status_code == 401:
        refresh_access_token()
        response = requests.get(f"{base_url}/search", headers=get_headers(), params=params)
    
    if response.status_code != 200:
        raise Exception(f"Error en la búsqueda de registros: {response.text}")
    
    return response.json().get("data", [])

def update_record(record_id):
    payload = {"data": [{"id": record_id, "Owner": {"id": OWNER_ID_NUEVO}}]}
    response = requests.put(f"{base_url}/{record_id}", headers=get_headers(), json=payload)
    
    if response.status_code == 401:
        refresh_access_token()
        response = requests.put(f"{base_url}/{record_id}", headers=get_headers(), json=payload)
    
    if response.status_code == 200:
        print(f"Registro {record_id} actualizado exitosamente.")
    else:
        print(f"Error al actualizar el registro {record_id}: {response.text}")

def actualizar_prop():
    threads = []
    for page in range(1, MAX_PAGES + 1):
        records = fetch_records(page)
        if not records:
            print(f"No hay más registros en la página {page}.")
            break
        
        for record in records:
            while threading.active_count() > THREAD_LIMIT:
                time.sleep(1)  # Esperar si se alcanzó el límite de hilos
            
            thread = threading.Thread(target=update_record, args=(record.get("id"),))
            threads.append(thread)
            thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    actualizar_prop()