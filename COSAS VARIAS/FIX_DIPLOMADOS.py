import os
import requests
import pandas as pd
import logging
from dotenv import load_dotenv
from datetime import datetime

# Configuración del sistema de logs
def setup_logging():
    log_file = f"zoho_fix_diplomados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Para mostrar logs en consola también
        ]
    )
    logging.info("Iniciando proceso de actualización de diplomados en Zoho CRM")
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

def get_lead_by_id(lead_id, access_token):
    """
    Obtiene la información de un lead por su ID
    """
    url = f"{base_url_leads}/{lead_id}"
    logging.info(f"Obteniendo información del lead ID: {lead_id}")
    
    response = requests.get(url, headers=get_headers(access_token))
    if response.status_code == 401:
        logging.warning("Token expirado, refrescando...")
        access_token = refresh_access_token(env_vars)
        response = requests.get(url, headers=get_headers(access_token))
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data and len(data) > 0:
            lead_data = data[0]
            logging.info(f"Lead encontrado: {lead_data.get('First_Name', '')} {lead_data.get('Last_Name', '')}")
            return lead_data, access_token
        else:
            logging.warning(f"No se encontró información para el lead ID: {lead_id}")
            return None, access_token
    else:
        error_msg = f"Error al obtener lead {lead_id}: {response.status_code} {response.text}"
        logging.error(error_msg)
        return None, access_token

def update_lead(lead_id, data, access_token):
    """
    Actualiza un lead con los datos proporcionados
    """
    url = f"{base_url_leads}/{lead_id}"
    
    update_data = {
        "data": [data]
    }
    
    logging.info(f"Actualizando lead ID: {lead_id} con datos: {data}")
    response = requests.put(url, headers=get_headers(access_token), json=update_data)
    
    if response.status_code == 401:
        logging.warning("Token expirado, refrescando...")
        access_token = refresh_access_token(env_vars)
        response = requests.put(url, headers=get_headers(access_token), json=update_data)
    
    if response.status_code == 200:
        logging.info(f"Lead {lead_id} actualizado correctamente")
        return True, access_token
    else:
        error_msg = f"Error al actualizar lead {lead_id}: {response.status_code} {response.text}"
        logging.error(error_msg)
        return False, access_token

def fix_diplomados(lead_ids, access_token):
    """
    Replica la funcionalidad del código Deluge "FIX_DIPLOMADOS"
    """
    actualizados = 0
    no_actualizados = 0
    errores = 0
    resultados = []
    
    for lead_id in lead_ids:
        try:
            # Obtener información del lead
            lead_data, access_token = get_lead_by_id(lead_id, access_token)
            
            if not lead_data:
                logging.warning(f"No se pudo obtener información del lead ID: {lead_id}. Saltando al siguiente.")
                resultados.append({
                    "Lead_ID": lead_id,
                    "Estado": "Error",
                    "Mensaje": "No se pudo obtener información del lead"
                })
                errores += 1
                continue
            
            correo = lead_data.get("Email")
            correo_dipl = lead_data.get("Correo_electr_nico_Continua")
            telefono = lead_data.get("Phone")
            telefono_dipl = lead_data.get("Tel_fono_Continua")
            
            logging.info(f"Lead {lead_id} - Email: {correo}, Email Continua: {correo_dipl}, Phone: {telefono}, Phone Continua: {telefono_dipl}")
            
            # Verificar condiciones para actualización
            if correo and correo_dipl is None and telefono and telefono_dipl is None:
                update_data = {
                    "Correo_electr_nico_Continua": correo,
                    "Tel_fono_Continua": telefono
                }
                
                success, access_token = update_lead(lead_id, update_data, access_token)
                
                if success:
                    logging.info(f"Lead {lead_id} actualizado: se copiaron correo y teléfono a campos Continua")
                    resultados.append({
                        "Lead_ID": lead_id,
                        "Estado": "Actualizado",
                        "Mensaje": "Se actualizaron los campos Correo_electr_nico_Continua y Tel_fono_Continua"
                    })
                    actualizados += 1
                else:
                    logging.error(f"Error al actualizar lead {lead_id}")
                    resultados.append({
                        "Lead_ID": lead_id,
                        "Estado": "Error",
                        "Mensaje": "Error al actualizar los campos"
                    })
                    errores += 1
            else:
                logging.info(f"Lead {lead_id} no requiere actualización - ya tiene datos o faltan campos origen")
                resultados.append({
                    "Lead_ID": lead_id,
                    "Estado": "No Actualizado",
                    "Mensaje": "No cumple las condiciones para actualización"
                })
                no_actualizados += 1
        
        except Exception as e:
            logging.error(f"Error procesando lead {lead_id}: {str(e)}")
            resultados.append({
                "Lead_ID": lead_id,
                "Estado": "Error",
                "Mensaje": str(e)
            })
            errores += 1
    
    # Generar CSV con resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"fix_diplomados_resultado_{timestamp}.csv"
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv(output_file, index=False)
    
    # Resumen
    logging.info("=" * 50)
    logging.info("RESUMEN DE ACTUALIZACIÓN DE DIPLOMADOS:")
    logging.info(f"Total de leads procesados: {len(lead_ids)}")
    logging.info(f"Leads actualizados: {actualizados}")
    logging.info(f"Leads que no requerían actualización: {no_actualizados}")
    logging.info(f"Leads con errores: {errores}")
    logging.info(f"Resultados guardados en: {output_file}")
    logging.info("=" * 50)
    
    return {
        "total_procesados": len(lead_ids),
        "actualizados": actualizados,
        "no_actualizados": no_actualizados,
        "errores": errores,
        "archivo_resultados": output_file
    }

def cargar_ids_desde_csv(file_path):
    """
    Carga los IDs de leads desde un archivo CSV, buscando específicamente la columna 'Lead_ID'
    """
    logging.info(f"Cargando IDs desde archivo: {file_path}")
    try:
        df = pd.read_csv(file_path)
        
        # Verificar si existe la columna 'Lead_ID'
        if 'Lead_ID' in df.columns:
            # Extraer IDs y eliminar duplicados
            lead_ids = df['Lead_ID'].dropna().astype(str).tolist()
            lead_ids = [id.strip() for id in lead_ids if id.strip()]
            lead_ids = list(set(lead_ids))  # Eliminar duplicados
            
            logging.info(f"Se cargaron {len(lead_ids)} IDs únicos desde el CSV de la columna 'Lead_ID'")
            return lead_ids
        else:
            # Si no existe la columna específica, mostrar las columnas disponibles y lanzar error
            logging.error(f"No se encontró la columna 'Lead_ID' en el CSV. Columnas disponibles: {list(df.columns)}")
            raise ValueError("El CSV no contiene la columna 'Lead_ID'. Verifique el formato del archivo.")
            
    except Exception as e:
        logging.error(f"Error al cargar IDs desde CSV: {str(e)}")
        raise

def main(csv_path="leads_ids.csv"):
    """
    Función principal
    """
    log_file = setup_logging()
    try:
        # Cargar variables de entorno
        global env_vars
        env_vars = load_environment()
        access_token = env_vars["ACCESS_TOKEN"]
        
        # Cargar IDs desde CSV
        lead_ids = cargar_ids_desde_csv(csv_path)
        
        if not lead_ids:
            logging.error("No se encontraron IDs para procesar. Verifique el archivo CSV.")
            return None
            
        # Ejecutar la actualización
        resultados = fix_diplomados(lead_ids, access_token)
        
        logging.info(f"Proceso completado exitosamente. Revisa el archivo de log: {log_file}")
        return resultados
        
    except Exception as e:
        logging.critical(f"Error fatal en el proceso: {str(e)}")
        return None

# Ejecutar
if __name__ == "__main__":
    main()