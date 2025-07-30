import os
import requests
import pandas as pd
import logging
from dotenv import load_dotenv
from datetime import datetime

# Configuración del sistema de logs
def setup_logging():
    log_file = f"zoho_validacion_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Para mostrar logs en consola también
        ]
    )
    logging.info("Iniciando proceso de validación de leads en Zoho CRM")
    return log_file

# Cargar variables de entorno
def load_environment():
    dotenv_path = r"C:\Users\david_romerom\OneDrive - Corporación Unificada Nacional de Educación Superior - CUN\Documentos\cs.env"
    load_dotenv(dotenv_path=dotenv_path)
    
    # Verificar que todas las variables necesarias estén disponibles
    required_vars = ["ACCESSTK", "REFRESHTK", "CLIENTID", "CLIENTST"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Faltan variables de entorno: {', '.join(missing_vars)}")
        raise EnvironmentError(f"Faltan variables de entorno: {', '.join(missing_vars)}")
    
    logging.info("Variables de entorno cargadas correctamente")
    return {
        "ACCESS_TOKEN": os.getenv("ACCESSTK"),
        "REFRESH_TOKEN": os.getenv("REFRESHTK"),
        "CLIENT_ID": os.getenv("CLIENTID"),
        "CLIENT_SECRET": os.getenv("CLIENTST")
    }

# URLs de Zoho
token_url = "https://accounts.zoho.com/oauth/v2/token"
base_url_leads = "https://www.zohoapis.com/crm/v5/Leads"

def refresh_access_token(env_vars):
    data = {
        "refresh_token": env_vars["REFRESH_TOKEN"],
        "client_id": env_vars["CLIENT_ID"],
        "client_secret": env_vars["CLIENT_SECRET"],
        "grant_type": "refresh_token"
    }
    logging.info("Intentando refrescar el access token...")
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        new_token = response.json().get('access_token')
        logging.info("Access token actualizado correctamente")
        return new_token
    else:
        error_msg = f"Error al actualizar el token: {response.status_code} {response.text}"
        logging.error(error_msg)
        raise Exception(error_msg)

def get_headers(access_token):
    return {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

def search_lead_by_document_or_email(cedula, correo, access_token):
    """
    Busca un lead por cédula y si no lo encuentra, por correo.
    Retorna el ID del lead, el periodo, cómo se encontró, y el access_token actualizado.
    """
    logging.info(f"Buscando lead por cédula: {cedula} o correo: {correo}")
    
    lead_id = None
    found_by = None
    periodo = None
    
    # Primero buscar por cédula
    if cedula and not pd.isna(cedula):
        cedula_str = str(cedula).strip()
        lead_by_doc_url = f"{base_url_leads}/search?criteria=(N_mero_de_identificaci_n1:equals:{cedula_str})&fields=id,Email,First_Name,Last_Name,N_mero_de_identificaci_n1,Periodo"
        
        response = requests.get(lead_by_doc_url, headers=get_headers(access_token))
        if response.status_code == 401:
            logging.warning("Token expirado, refrescando...")
            access_token = refresh_access_token(env_vars)
            response = requests.get(lead_by_doc_url, headers=get_headers(access_token))
            
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                # Verificar que el número de documento realmente coincide
                for lead_data in data:
                    actual_doc = lead_data.get("N_mero_de_identificaci_n1")
                    if actual_doc == cedula_str:
                        lead_id = lead_data.get("id")
                        periodo = lead_data.get("Periodo")
                        found_by = "cedula"
                        logging.info(f"Lead encontrado por cédula: {cedula_str} (ID: {lead_id}, Periodo: {periodo})")
                        break
                    else:
                        logging.warning(f"Zoho devolvió un lead con cédula {actual_doc} que no coincide con {cedula_str}")
            
            if not lead_id:
                logging.info(f"No se encontró lead exacto por cédula: {cedula_str}")
        elif response.status_code != 204:  # Si no es 204 (No Content), registrar el error
            error_msg = f"Error buscando por cédula: {response.status_code} {response.text}"
            logging.error(error_msg)
    
    # Si no se encontró por cédula, buscar por correo
    if not lead_id and correo and not pd.isna(correo):
        correo_str = str(correo).strip().lower()
        url = f"{base_url_leads}/search?criteria=(Email:equals:{correo_str})&fields=id,Email,First_Name,Last_Name,N_mero_de_identificaci_n1,Periodo"
        logging.info(f"No encontrado por cédula, buscando por correo: {correo_str}")
        
        response = requests.get(url, headers=get_headers(access_token))
        if response.status_code == 401:
            logging.warning("Token expirado, refrescando...")
            access_token = refresh_access_token(env_vars)
            response = requests.get(url, headers=get_headers(access_token))
        
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                # Verificar que el correo realmente coincide
                for lead_data in data:
                    actual_email = lead_data.get("Email")
                    if actual_email and actual_email.lower() == correo_str:
                        lead_id = lead_data.get("id")
                        periodo = lead_data.get("Periodo")
                        found_by = "correo"
                        logging.info(f"Lead encontrado por correo: {correo_str} (ID: {lead_id}, Periodo: {periodo})")
                        break
                    else:
                        logging.warning(f"Zoho devolvió un lead con correo {actual_email} que no coincide con {correo_str}")
                
                if not lead_id:
                    logging.info(f"No se encontró lead exacto por correo: {correo_str}")
            else:
                logging.info(f"No se encontró lead por correo: {correo_str}")
        elif response.status_code != 204:  # Si no es 204 (No Content), registrar el error
            error_msg = f"Error buscando por correo: {response.status_code} {response.text}"
            logging.error(error_msg)
    
    return lead_id, periodo, found_by, access_token

def validar_leads_desde_csv(file_path="validar.csv", access_token=None):
    """
    Lee un archivo CSV con columnas 'cedula' y 'correo', 
    busca cada registro en Zoho CRM y guarda los resultados en un CSV.
    """
    resultados = []
    leads_encontrados = 0
    leads_no_encontrados = 0
    registros_procesados = 0
    
    try:
        logging.info(f"Leyendo archivo CSV: {file_path}")
        df = pd.read_csv(file_path)
        total_registros = len(df)
        logging.info(f"Total de registros a validar: {total_registros}")
        
        # Verificar si las columnas necesarias existen
        if 'cedula' not in df.columns:
            msg = "La columna 'cedula' no existe en el CSV"
            logging.error(msg)
            raise ValueError(msg)
        
        if 'correo' not in df.columns:
            msg = "La columna 'correo' no existe en el CSV"
            logging.error(msg)
            raise ValueError(msg)
        
        for index, row in df.iterrows():
            registros_procesados += 1
            
            try:
                cedula = row['cedula']
                correo = row['correo']
                
                # Registrar información básica
                resultado = {
                    "Cedula": cedula,
                    "Correo": correo
                }
                
                # Buscar lead en Zoho
                lead_id, periodo, found_by, access_token = search_lead_by_document_or_email(cedula, correo, access_token)
                
                if lead_id:
                    resultado["Lead_ID"] = lead_id
                    resultado["Periodo"] = periodo if periodo else "No especificado"
                    resultado["Encontrado"] = "Si"
                    resultado["Encontrado_Por"] = found_by
                    leads_encontrados += 1
                else:
                    resultado["Lead_ID"] = None
                    resultado["Periodo"] = None
                    resultado["Encontrado"] = "No"
                    resultado["Encontrado_Por"] = None
                    leads_no_encontrados += 1
                
                # Agregar a los resultados
                resultados.append(resultado)
                
                # Log de progreso cada 10 registros
                if registros_procesados % 10 == 0:
                    logging.info(f"Progreso: {registros_procesados}/{total_registros} registros procesados ({(registros_procesados/total_registros)*100:.1f}%)")
                
            except Exception as e:
                logging.error(f"Error al procesar la fila {index+1}: {str(e)}")
                resultado = {
                    "Cedula": cedula if 'cedula' in locals() else None,
                    "Correo": correo if 'correo' in locals() else None,
                    "Lead_ID": None,
                    "Periodo": None,
                    "Encontrado": "Error",
                    "Encontrado_Por": None,
                    "Error": str(e)
                }
                resultados.append(resultado)
                continue
        
        # Guardar resultados en CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"leads_validados_{timestamp}.csv"
        df_resultados = pd.DataFrame(resultados)
        df_resultados.to_csv(output_file, index=False)
        
        # Resumen final
        logging.info("=" * 50)
        logging.info("RESUMEN DE VALIDACIÓN:")
        logging.info(f"Total de registros procesados: {registros_procesados}/{total_registros}")
        logging.info(f"Leads encontrados: {leads_encontrados}")
        logging.info(f"Leads no encontrados: {leads_no_encontrados}")
        logging.info(f"Resultados guardados en: {output_file}")
        logging.info("=" * 50)
        
        return {
            "registros_procesados": registros_procesados,
            "leads_encontrados": leads_encontrados,
            "leads_no_encontrados": leads_no_encontrados,
            "archivo_resultados": output_file
        }
        
    except Exception as e:
        error_msg = f"Error al procesar el archivo CSV: {str(e)}"
        logging.error(error_msg)
        raise

def main(file_path="validar.csv"):
    """
    Función principal que ejecuta el proceso de validación.
    """
    log_file = setup_logging()
    try:
        # Cargar variables de entorno
        global env_vars
        env_vars = load_environment()
        access_token = env_vars["ACCESS_TOKEN"]
        
        # Validar leads desde CSV
        resultados = validar_leads_desde_csv(file_path, access_token)
        
        logging.info(f"Proceso completado exitosamente. Revisa el archivo de log: {log_file}")
        logging.info(f"Se han guardado los resultados en: {resultados['archivo_resultados']}")
        return resultados
    except Exception as e:
        logging.critical(f"Error fatal en el proceso: {str(e)}")
        return None

# Ejecutar
if __name__ == "__main__":
    main()