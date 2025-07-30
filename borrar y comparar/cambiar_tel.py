import os
import requests
import pandas as pd
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
base_url = "https://www.zohoapis.com/crm/v5/Leads"

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

def update_lead_phone(record_id, phone):
    """Actualiza el campo de teléfono de un lead en Zoho CRM."""
    url = f"{base_url}/{record_id}"
    data = {
        "data": [{
            "Phone": phone
        }]
    }
    response = requests.put(url, headers=get_headers(), json=data)
    
    if response.status_code == 401:  # Token expirado
        print("Token expirado, renovando...")
        refresh_access_token()
        response = requests.put(url, headers=get_headers(), json=data)
    
    if response.status_code == 200:
        print(f"Teléfono del lead {record_id} actualizado correctamente a {phone}.")
    else:
        print(f"Error al actualizar el lead {record_id}: {response.status_code} {response.text}")

def process_csv(file_path="fechas.csv"):
    """Lee un archivo CSV y actualiza el teléfono de cada lead en Zoho CRM."""
    try:
        df = pd.read_csv(file_path, dtype={"ID": str, "TEL": str})
        if "ID" not in df.columns or "TEL" not in df.columns:
            print("El archivo CSV debe tener las columnas 'ID' y 'TEL'.")
            return
        
        for _, row in df.iterrows():
            record_id = row["ID"].strip()
            phone = row["TEL"].strip()
            
            if not phone.startswith("+"):
                phone = "+" + phone
            
            if record_id and phone:
                update_lead_phone(record_id, phone)
    
    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")

# Ejecutar la función para procesar el CSV
process_csv()
