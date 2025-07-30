import os
import requests
import time
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
        print("✅ Access token actualizado correctamente.")
    else:
        raise Exception(f"❌ Error al actualizar el token: {response.status_code} {response.text}")

def get_headers():
    """Genera los headers para la autenticación en Zoho CRM."""
    return {
        "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def crear_lead(row):
    """Crea un Lead en Zoho CRM usando los datos de la fila."""
    try:
        # Validar y convertir edad
        try:
            edad = int(float(row.get("Edad", 0)))
        except (ValueError, TypeError):
            edad = None

        data = {
            "data": [
                {
                    "Correo_electr_nico_Continua": row.get("correo", ""),
                    "Campaigns": {
                        "id": row.get("campaña id", "")
                    },
                    "First_Name": row.get("First_Name", ""),
                    "Last_Name": row.get("Last_Name", ""),
                    "Genero": row.get("Genero", ""),
                    "Periodo": row.get("Periodo", ""),
                    "N_mero_de_identificaci_n1": str(row.get("N_mero_de_identificaci_n1", "")),
                    "Tipo_de_documento": row.get("Tipo_de_documento", ""),
                    "Tel_fono_Continua": str(row.get("Phone", "")),
                    "Edad": edad
                }
            ],
            "trigger": ["workflow"]
        }

        response = requests.post(base_url, headers=get_headers(), json=data)

        if response.status_code == 401:
            print("⚠️ Token expirado, esperando 10 segundos para reintentar...")
            time.sleep(10)
            refresh_access_token()
            response = requests.post(base_url, headers=get_headers(), json=data)

        if response.status_code == 201:
            print(f"✅ Lead creado: {row.get('correo', '')}")
        else:
            print(f"❌ Error creando Lead ({row.get('correo', '')}): {response.status_code}")
            print(response.json())

    except Exception as e:
        print(f"❌ Error en crear_lead: {e}")


def main():
    try:
        df = pd.read_csv("CONT 1.csv")

        for index, row in df.iterrows():
            print(f"🔄 Procesando fila {index + 1}/{len(df)}")
            crear_lead(row)
            time.sleep(1)  # Pausa opcional para evitar sobrecarga

        print("✅ Todos los Leads han sido procesados.")

    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")

if __name__ == "__main__":
    main()
