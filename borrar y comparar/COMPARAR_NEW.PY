import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
dotenv_path = r"C:\Users\david_romerom\OneDrive - Corporación Unificada Nacional de Educación Superior - CUN\Documentos\cs.env"
load_dotenv(dotenv_path=dotenv_path)

ACCESS_TOKEN = os.getenv("ACCESSTK")
REFRESH_TOKEN = os.getenv("REFRESHTK")
CLIENT_ID = os.getenv("CLIENTID")
CLIENT_SECRET = os.getenv("CLIENTST")

# URLs de Zoho
token_url = "https://accounts.zoho.com/oauth/v2/token"
base_url_leads = "https://www.zohoapis.com/crm/v5/Leads"
base_url_interesados = "https://www.zohoapis.com/crm/v5/Contacts/search"

# ID de la campaña CODE
NEW_CAMPAIGN_ID = "4402173000502487933"

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

def search_in_module(module_url, documento):
    url = f"{module_url}?criteria=(N_mero_de_identificaci_n1:equals:{documento})"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 401:
        refresh_access_token()
        response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        data = response.json().get("data", [])
        return data[0] if data else None
    else:
        print(f"Error al buscar en módulo: {response.status_code} {response.text}")
        return None

def search_lead_by_document_or_email(documento, correo):
    lead = search_in_module(base_url_leads, documento)
    if not lead and correo:
        url = f"{base_url_leads}/search?criteria=(Email:equals:{correo})"
        response = requests.get(url, headers=get_headers())
        if response.status_code == 401:
            refresh_access_token()
            response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            data = response.json().get("data", [])
            lead = data[0] if data else None
        else:
            print(f"Error buscando por correo: {response.status_code} {response.text}")
    return lead

def update_lead_campaign(lead_id, row):
    url = f"{base_url_leads}/{lead_id}"
    periodo = row.get("Periodo")
    data = {
        "data": [{
            "First_Name": row.get("Nombre", ""),
            "Last_Name": row.get("Apellido", ""),
            "Genero": row.get("Género", ""),
            "Periodo": periodo,
            "Email": row.get("Correo_electrónico_agregado", ""),
            "N_mero_de_identificaci_n1": str(row.get("Número_de_documento", "")),
            "Tipo_de_documento": row.get("Tipo_de_documento", ""),
            "Phone": str(row.get("Teléfono", "")),
            "Edad": str(row.get("Edad", "")),
            "Campa_a_mercadeo": {"id": NEW_CAMPAIGN_ID},
            "Modalidad": row.get("Modalidad de tu interés", ""),
            "Destino_Lead": "Diplomado" if periodo == "25C04" else "Carrera"
        }]
    }
    response = requests.put(url, headers=get_headers(), json=data)
    if response.status_code == 401:
        refresh_access_token()
        response = requests.put(url, headers=get_headers(), json=data)
    if response.status_code == 200:
        print(f"Lead {lead_id} actualizado correctamente.")
    else:
        print(f"Error al actualizar lead {lead_id}: {response.status_code} {response.text}")

def create_lead_from_csv_row(row):
    url = base_url_leads
    data = {
        "data": [{
            "First_Name": row.get("Nombre", ""),
            "Last_Name": row.get("Apellido", ""),
            "Genero": row.get("Género", ""),
            "Periodo": row.get("Periodo", ""),
            "Email": row.get("Correo_electrónico_agregado", ""),
            "N_mero_de_identificaci_n1": str(row.get("Número_de_documento", "")),
            "Tipo_de_documento": row.get("Tipo_de_documento", ""),
            "Phone": str(row.get("Teléfono", "")),
            "Edad": str(row.get("Edad", "")),
            "Campa_a_mercadeo": {"id": NEW_CAMPAIGN_ID},
            "Modalidad": row.get("Modalidad de tu interés", "")
        }]
    }
    response = requests.post(url, headers=get_headers(), json=data)
    if response.status_code == 401:
        refresh_access_token()
        response = requests.post(url, headers=get_headers(), json=data)
    if response.status_code == 201:
        print(f"Lead creado correctamente: {row.get('Nombre')}")
        return True
    else:
        print(f"Error al crear lead: {response.status_code} - {response.text}")
        return False

def process_csv(file_path="TRUE.csv"):
    interesados_guardados = []
    try:
        df = pd.read_csv(file_path).fillna('')
        for _, row in df.iterrows():
            documento = str(row["Número_de_documento"]).strip()
            correo = row.get("Correo_electrónico_agregado", "").strip()
            fecha_csv = datetime.strptime(row["fecha de creacion"].strip(), "%d/%m/%Y %H:%M:%S").date()

            interesado = search_in_module(base_url_interesados, documento)
            if interesado:
                interesados_guardados.append(interesado["id"])
                continue

            lead = search_lead_by_document_or_email(documento, correo)
            if lead:
                lead_id = lead["id"]
                created_time = lead.get("Created_Time")
                if created_time:
                    fecha_crm = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S%z").date()
                    if fecha_crm >= fecha_csv:
                        update_lead_campaign(lead_id, row)
                    else:
                        print(f"Lead {lead_id} tiene fecha anterior a la del CSV. No se actualiza.")
                else:
                    print(f"Lead {lead_id} no tiene fecha de creación.")
            else:
                create_lead_from_csv_row(row)

        if interesados_guardados:
            df_guardados = pd.DataFrame(interesados_guardados, columns=["ID Interesado"])
            df_guardados.to_excel("interesados_encontrados2.xlsx", index=False)
            print("IDs de interesados guardados en interesados_encontrados.xlsx")

    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")

# Ejecutar
if __name__ == "__main__":
    process_csv()
