import os
import requests
import pandas as pd
import logging
from dotenv import load_dotenv
from datetime import datetime
#Hecho por David Romero-Zohito
#con mucho amor uwu 
# para quien lo necesite xd 

# Configuración del sistema de logs
def setup_logging():
    log_file = f"zoho_crm_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Para mostrar logs en consola también
        ]
    )
    logging.info("Iniciando proceso de sincronización con Zoho CRM")
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
base_url_interesados = "https://www.zohoapis.com/crm/v5/Contacts"

# ID de la campaña CODE
NEW_CAMPAIGN_ID = "4402173000502487933"

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

def search_in_module(module_url, documento, access_token):
    # Use the search endpoint and include the document number field
    url = f"{module_url}/search?criteria=(N_mero_de_identificaci_n1:equals:{documento})&fields=id,Created_Time,N_mero_de_identificaci_n1"
    logging.info(f"Buscando documento {documento} en {module_url}")
    
    response = requests.get(url, headers=get_headers(access_token))
    if response.status_code == 401:
        logging.warning("Token expirado, refrescando...")
        access_token = refresh_access_token(env_vars)
        response = requests.get(url, headers=get_headers(access_token))
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            # Verify the document number actually matches
            for record in data:
                actual_doc = record.get("N_mero_de_identificaci_n1")
                if actual_doc == documento:
                    logging.info(f"Encontrado registro con documento {documento} (ID: {record.get('id')})")
                    return record, access_token
                else:
                    logging.warning(f"Zoho devolvió un registro con documento {actual_doc} que no coincide con {documento}")
            
            logging.info(f"No se encontró registro exacto con documento {documento}")
            return None, access_token
        else:
            logging.info(f"No se encontró registro con documento {documento}")
            return None, access_token
    elif response.status_code == 204:  # No Content - No se encontraron resultados
        logging.info(f"No se encontró registro con documento {documento} (Código 204)")
        return None, access_token
    else:
        error_msg = f"Error al buscar en módulo: {response.status_code} {response.text}"
        logging.error(error_msg)
        return None, access_token

def search_lead_by_document_or_email(documento, correo, access_token):
    logging.info(f"Buscando lead por documento: {documento} o correo: {correo}")
    
    # Use the exact criteria with equals: operator and properly enclose the value
    lead_by_doc_url = f"{base_url_leads}/search?criteria=(N_mero_de_identificaci_n1:equals:{documento})&fields=id,Created_Time,Email,First_Name,Last_Name,N_mero_de_identificaci_n1"
    
    response = requests.get(lead_by_doc_url, headers=get_headers(access_token))
    if response.status_code == 401:
        logging.warning("Token expirado, refrescando...")
        access_token = refresh_access_token(env_vars)
        response = requests.get(lead_by_doc_url, headers=get_headers(access_token))
        
    
    lead = None
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            # Verify that the document number actually matches what we're looking for
            for lead_data in data:
                actual_doc = lead_data.get("N_mero_de_identificaci_n1")
                if actual_doc == documento:
                    lead = lead_data
                    logging.info(f"Lead encontrado por documento: {documento} (ID: {lead.get('id')})")
                    break
                else:
                    logging.warning(f"Zoho devolvió un lead con documento {actual_doc} que no coincide con {documento}")
        
        if not lead:
            logging.info(f"No se encontró lead exacto por documento: {documento}")
    elif response.status_code != 204:  # Si no es 204 (No Content), registrar el error
        error_msg = f"Error buscando por documento: {response.status_code} {response.text}"
        logging.error(error_msg)
    
    # Si no se encontró por documento, buscar por correo
    if not lead and correo:
        url = f"{base_url_leads}/search?criteria=(Email:equals:{correo})&fields=id,Created_Time,Email,First_Name,Last_Name,N_mero_de_identificaci_n1"
        logging.info(f"No encontrado por documento, buscando por correo: {correo}")
        
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
                    if actual_email and actual_email.lower() == correo.lower():
                        lead = lead_data
                        logging.info(f"Lead encontrado por correo: {correo} (ID: {lead.get('id')})")
                        logging.info(lead_data)
                        break
                    else:
                        logging.warning(f"Zoho devolvió un lead con correo {actual_email} que no coincide con {correo}")
                
                if not lead:
                    logging.info(f"No se encontró lead exacto por correo: {correo}")
            else:
                logging.info(f"No se encontró lead por correo: {correo}")
        elif response.status_code != 204:  # Si no es 204 (No Content), registrar el error
            error_msg = f"Error buscando por correo: {response.status_code} {response.text}"
            logging.error(error_msg)
    
    return lead, access_token

def update_lead_campaign(lead_id, row, access_token):
    url = f"{base_url_leads}/{lead_id}"
    periodo = row.get("Periodo", "")
    
    # Datos básicos del lead
    data_dict = {
        "First_Name": row.get("Nombre", ""),
        "Last_Name": row.get("Apellido", ""),
        "Genero": row.get("Género", ""),
        "Periodo": periodo,
        "Email": row.get("Correo_electrónico_agregado", ""),
        "N_mero_de_identificaci_n1": str(row.get("Número_de_documento", "")),
        "Tipo_de_documento": row.get("Tipo_de_documento", ""),
        "Phone": str(row.get("Teléfono", "")),
        "Campa_a_mercadeo": {"id": NEW_CAMPAIGN_ID},
        "Destino_Lead": "Diplomado" if periodo == "25C06" else "Carrera",
        "Programa": row.get("programa", "")
    }
    
    # Verificar si existe programa_ID y añadirlo solo si es válido
    programa_id = row.get("programa_ID", "")
    if programa_id and str(programa_id).strip():
        data_dict["Programa_de_interes"] = {"id": str(programa_id).strip()}
        logging.info(f"Asignando Programa_de_interes ID: {programa_id} para actualizar lead {lead_id}")
    else:
        logging.warning(f"No se encontró programa_ID válido para actualizar lead {lead_id}")
    
    # Agregar edad solo si es un valor válido
    if pd.notna(row.get("Edad")) and row.get("Edad") != "":
        try:
            data_dict["Edad"] = int(float(str(row.get("Edad")).strip()))
        except (ValueError, TypeError):
            logging.warning(f"No se pudo convertir Edad a entero: {row.get('Edad')}")
    
    data = {
        "data": [data_dict]
    }
    
    # Registrar los datos que se enviarán para debugging
    logging.info(f"Datos para actualizar lead: {data}")
    
    logging.info(f"Actualizando lead {lead_id} con campaña {NEW_CAMPAIGN_ID}")
    response = requests.put(url, headers=get_headers(access_token), json=data)
    
    if response.status_code == 401:
        logging.warning("Token expirado, refrescando...")
        access_token = refresh_access_token(env_vars)
        response = requests.put(url, headers=get_headers(access_token), json=data)
    
    if response.status_code == 200:
        logging.info(f"Lead {lead_id} actualizado correctamente")
        return True, access_token
    else:
        error_msg = f"Error al actualizar lead {lead_id}: {response.status_code} {response.text}"
        logging.error(error_msg)
        return False, access_token

def create_lead_from_csv_row(row, access_token):
    url = base_url_leads
    periodo = row.get("Periodo", "")
    
    # Datos básicos del lead
    data_dict = {
        "First_Name": row.get("Nombre", ""),
        "Last_Name": row.get("Apellido", ""),
        "Genero": row.get("Género", ""),
        "Periodo": periodo,
        "Email": row.get("Correo_electrónico_agregado", ""),
        "N_mero_de_identificaci_n1": str(row.get("Número_de_documento", "")),
        "Tipo_de_documento": row.get("Tipo_de_documento", ""),
        "Phone": str(row.get("Teléfono", "")),
        "Campa_a_mercadeo": {"id": NEW_CAMPAIGN_ID},
        "Destino_Lead": "Diplomado" if periodo == "25C06" else "Carrera",
        "Programa": row.get("programa", "")
    }
    
    # Verificar si existe programa_ID y añadirlo solo si es válido
    programa_id = row.get("programa_ID", "")
    if programa_id and str(programa_id).strip():
        data_dict["Programa_de_interes"] = {"id": str(programa_id).strip()}
        logging.info(f"Asignando Programa_de_interes ID: {programa_id} para nuevo lead")
    else:
        logging.warning(f"No se encontró programa_ID válido para crear nuevo lead")
    
    # Agregar edad solo si es un valor válido
    if pd.notna(row.get("Edad")) and row.get("Edad") != "":
        try:
            data_dict["Edad"] = int(float(str(row.get("Edad")).strip()))
        except (ValueError, TypeError):
            logging.warning(f"No se pudo convertir Edad a entero: {row.get('Edad')}")
    
    data = {
        "data": [data_dict]
    }
    
    # Registrar los datos que se enviarán para debugging
    logging.info(f"Datos para crear lead: {data}")
    
    logging.info(f"Creando nuevo lead para {row.get('Nombre', '')} {row.get('Apellido', '')}")
    response = requests.post(url, headers=get_headers(access_token), json=data)
    
    if response.status_code == 401:
        logging.warning("Token expirado, refrescando...")
        access_token = refresh_access_token(env_vars)
        response = requests.post(url, headers=get_headers(access_token), json=data)
    
    if response.status_code == 201:
        created_id = response.json().get("data", [{}])[0].get("details", {}).get("id")
        logging.info(f"Lead creado correctamente con ID: {created_id}")
        return True, access_token
    else:
        error_msg = f"Error al crear lead: {response.status_code} - {response.text}"
        logging.error(error_msg)
        return False, access_token

def process_csv(file_path="ARCHIVO FINAL FULL_v2.csv", access_token=None):
    interesados_guardados = []
    leads_actualizados = 0
    leads_creados = 0
    leads_fallidos = 0
    registros_procesados = 0
    
    try:
        logging.info(f"Procesando archivo CSV: {file_path}")
        df = pd.read_csv(file_path)
        total_registros = len(df)
        logging.info(f"Total de registros a procesar: {total_registros}")
        
        # Corrección: Verificar las columnas existentes en el CSV y mapear los nombres
        columnas_esperadas = ["Nombre", "Apellido", "Género", "Periodo", "Correo_electrónico_agregado", 
                             "Número_de_documento", "Tipo_de_documento", "Teléfono", "Edad", "programa", "programa_ID"]
        
        # Mapeo de nombres de columnas del CSV real a los nombres esperados
        column_mapping = {
            'n de documento': 'Número_de_documento',
            'fecha de creacion': 'fecha_de_creacion',
            # Agregar más mapeos según sea necesario
        }
        
        # Renombrar columnas si existen en el dataframe
        for col_original, col_nuevo in column_mapping.items():
            if col_original in df.columns:
                df.rename(columns={col_original: col_nuevo}, inplace=True)
        
        # Mostrar las columnas disponibles en el CSV para debug
        logging.info(f"Columnas en el CSV: {list(df.columns)}")
        
        for index, row in df.iterrows():
            registros_procesados += 1
            
            # Adaptar el acceso a las columnas según los nombres reales del CSV
            documento_col = "Número_de_documento" if "Número_de_documento" in df.columns else "n de documento"
            fecha_col = "fecha_de_creacion" if "fecha_de_creacion" in df.columns else "fecha de creacion"
            
            # Verificar campos obligatorios
            if pd.isna(row.get(documento_col)) or pd.isna(row.get(fecha_col)):
                logging.warning(f"Fila {index+1}: Falta documento o fecha de creación. Omitiendo registro.")
                continue
                
            try:
                documento = str(row[documento_col]).strip()
                correo = str(row.get("Correo_electrónico_agregado", "")).strip() if pd.notna(row.get("Correo_electrónico_agregado")) else ""
                
                # Crear un diccionario con los datos de la fila actual (para pasar a las funciones)
                row_data = {}
                for col in columnas_esperadas:
                    if col in df.columns:
                        row_data[col] = row[col]
                    else:
                        # Intentar buscar el nombre alternativo si existe
                        for orig, nuevo in column_mapping.items():
                            if nuevo == col and orig in df.columns:
                                row_data[col] = row[orig]
                                break
                
                # Parsear fecha con manejo de errores
                try:
                    fecha_csv = datetime.strptime(row[fecha_col].strip(), "%d-%m-%Y %H:%M:%S").date()
                except ValueError:
                    logging.warning(f"Fila {index+1}: Formato de fecha inválido: {row[fecha_col]}. Intentando formatos alternativos.")
                    try:
                        fecha_csv = pd.to_datetime(row[fecha_col]).date()
                    except:
                        logging.error(f"Fila {index+1}: No se pudo interpretar la fecha. Omitiendo registro.")
                        continue
                
                logging.info(f"Procesando registro {index+1}/{total_registros}: Documento {documento}, Correo {correo}")
                
                # Verificar si existe programa_ID en esta fila
                if "programa_ID" in row_data and pd.notna(row_data["programa_ID"]):
                    logging.info(f"Fila {index+1}: Tiene programa_ID = {row_data['programa_ID']}")
                else:
                    logging.warning(f"Fila {index+1}: No tiene programa_ID o es nulo")
                
                # Búsqueda en módulo de Interesados (Contacts)
                interesado, access_token = search_in_module(base_url_interesados, documento, access_token)
                
                if interesado:
                    interesado_id = interesado.get("id")
                    interesados_guardados.append({"ID Interesado": interesado_id, "Documento": documento})
                    logging.info(f"Registro ya existe como Interesado (Contact) con ID: {interesado_id}. Omitiendo.")
                    continue
                
                # Buscar en módulo de Leads
                lead, access_token = search_lead_by_document_or_email(documento, correo, access_token)
                if lead:
                    lead_id = lead.get("id")
                    created_time = lead.get("Created_Time")
                    if created_time:
                        try:
                            fecha_crm = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S%z").date()
                            logging.info(f"Lead encontrado con ID {lead_id}, fecha CRM: {fecha_crm}, fecha CSV: {fecha_csv}")
                            
                            if fecha_csv >= fecha_crm:
                                success, access_token = update_lead_campaign(lead_id, row_data, access_token)
                                if success:
                                    leads_actualizados += 1
                            else:
                                logging.info(f"Lead {lead_id} tiene fecha anterior a la del CSV. No se actualiza.")
                        except ValueError:
                            logging.warning(f"No se pudo interpretar la fecha del CRM: {created_time}. Actualizando de todas formas.")
                            success, access_token = update_lead_campaign(lead_id, row_data, access_token)
                            if success:
                                leads_actualizados += 1
                    else:
                        logging.warning(f"Lead {lead_id} no tiene fecha de creación. Actualizando de todas formas.")
                        success, access_token = update_lead_campaign(lead_id, row_data, access_token)
                        if success:
                            leads_actualizados += 1
                else:
                    # Crear nuevo lead
                    success, access_token = create_lead_from_csv_row(row_data, access_token)
                    if success:
                        leads_creados += 1
                    else:
                        leads_fallidos += 1
                
                # Log de progreso cada 10 registros
                if registros_procesados % 10 == 0:
                    logging.info(f"Progreso: {registros_procesados}/{total_registros} registros procesados ({(registros_procesados/total_registros)*100:.1f}%)")
                    
            except Exception as e:
                logging.error(f"Error al procesar la fila {index+1}: {str(e)}")
                leads_fallidos += 1
                continue
        
        # Guardar los IDs de interesados encontrados
        if interesados_guardados:
            output_file = "interesados_encontrados.csv"
            df_guardados = pd.DataFrame(interesados_guardados)
            df_guardados.to_csv(output_file, index=False)
            logging.info(f"{len(interesados_guardados)} IDs de interesados guardados en {output_file}")
        
        # Resumen final
        logging.info("=" * 50)
        logging.info("RESUMEN DE PROCESAMIENTO:")
        logging.info(f"Total de registros procesados: {registros_procesados}/{total_registros}")
        logging.info(f"Leads creados: {leads_creados}")
        logging.info(f"Leads actualizados: {leads_actualizados}")
        logging.info(f"Interesados ya existentes: {len(interesados_guardados)}")
        logging.info(f"Leads con errores: {leads_fallidos}")
        logging.info("=" * 50)
        
        return {
            "registros_procesados": registros_procesados,
            "leads_creados": leads_creados,
            "leads_actualizados": leads_actualizados,
            "interesados_existentes": len(interesados_guardados),
            "leads_fallidos": leads_fallidos
        }
        
    except Exception as e:
        error_msg = f"Error al procesar el archivo CSV: {str(e)}"
        logging.error(error_msg)
        raise

# Función principal
def main(file_path="ARCHIVO FINAL FULL_v2.csv"):
    log_file = setup_logging()
    try:
        # Cargar variables de entorno
        global env_vars
        env_vars = load_environment()
        access_token = env_vars["ACCESS_TOKEN"]
        
        # Procesar CSV
        resultados = process_csv(file_path, access_token)
        
        logging.info(f"Proceso completado exitosamente. Revisa el archivo de log: {log_file}")
        return resultados
    except Exception as e:
        logging.critical(f"Error fatal en el proceso: {str(e)}")
        return None

# Ejecutar
if __name__ == "__main__":
    main()