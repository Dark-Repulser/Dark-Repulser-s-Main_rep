import pandas as pd
import requests
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pytz

# Configura logs
logging.basicConfig(level=logging.INFO)

# === Cargar entorno y tokens ===
def load_environment():
    dotenv_path = r"C:\Users\david_romerom\OneDrive - Corporación Unificada Nacional de Educación Superior - CUN\Documentos\cs.env"
    load_dotenv(dotenv_path=dotenv_path)
    
    required_vars = ["ACCESSTK", "REFRESHTK", "CLIENTID", "CLIENTST"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Faltan variables de entorno: {', '.join(missing_vars)}")
        raise EnvironmentError(f"Faltan variables de entorno: {', '.join(missing_vars)}")
    
    return {
        "ACCESS_TOKEN": os.getenv("ACCESSTK"),
        "REFRESH_TOKEN": os.getenv("REFRESHTK"),
        "CLIENT_ID": os.getenv("CLIENTID"),
        "CLIENT_SECRET": os.getenv("CLIENTST")
    }

def refresh_access_token(env_vars):
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": env_vars["REFRESH_TOKEN"],
        "client_id": env_vars["CLIENT_ID"],
        "client_secret": env_vars["CLIENT_SECRET"],
        "grant_type": "refresh_token"
    }
    logging.info("Refrescando token...")
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Error al refrescar token: {response.status_code} - {response.text}")

def get_headers(token):
    return {
        "Authorization": f"Zoho-oauthtoken {token}",
        "Content-Type": "application/json"
    }

# === Fechas del mes pasado hasta hoy ===
def calcular_rango_fechas():
    tz = pytz.timezone("America/Bogota")
    hoy = datetime.now(tz)
    primer_dia_mes_pasado = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
    return primer_dia_mes_pasado, hoy

# === Buscar en Deals por teléfono ===
def buscar_por_telefono(headers, telefono, fecha_inicio, fecha_fin):
    url = "https://www.zohoapis.com/crm/v5/Deals/search"
    params = {
        "criteria": f'(Tel_fono:equals:{telefono})'
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        resultados = []
        for deal in data:
            created_str = deal.get("Created_Time", "")[:19]
            if created_str:
                created_dt = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S")
                created_dt = pytz.timezone("America/Bogota").localize(created_dt)
                if fecha_inicio <= created_dt <= fecha_fin:
                    resultados.append(deal)
        return resultados
    elif response.status_code == 204:
        logging.warning(f"No hay datos para {telefono}")
        return []
    else:
        logging.warning(f"Error buscando {telefono}: {response.status_code} -> {response.text}")
        return []

# === PROCESO PRINCIPAL ===
def main():
    env_vars = load_environment()
    access_token = refresh_access_token(env_vars)
    headers = get_headers(access_token)

    fecha_inicio, fecha_fin = calcular_rango_fechas()

    df = pd.read_csv("telefonos.csv")
    todos_resultados = []

    for telefono in df["TEL"]:
        tel = str(telefono).strip()
        if tel:
            resultados = buscar_por_telefono(headers, tel, fecha_inicio, fecha_fin)
            todos_resultados.extend(resultados)

    print(f"\n🔍 Se encontraron {len(todos_resultados)} registros del mes pasado hasta hoy.\n")

    if todos_resultados:
        df_resultados = pd.json_normalize(todos_resultados)
        df_resultados.to_excel("resultados_deals.xlsx", index=False)
        print("📁 Resultados guardados en: resultados_deals.xlsx")

if __name__ == "__main__":
    main()
