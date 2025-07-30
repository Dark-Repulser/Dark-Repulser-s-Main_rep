import pandas as pd
import requests
import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Optional

# URLs de Zoho
token_url = "https://accounts.zoho.com/oauth/v2/token"
base_url_leads = "https://www.zohoapis.com/crm/v5/Leads"
base_url_interesados = "https://www.zohoapis.com/crm/v5/Contacts"

def setup_logging():
    """Configura el sistema de logging"""
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
def load_environment():
    """Cargar variables de entorno"""
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

def refresh_access_token(env_vars):
    """Refresca el access token de Zoho"""
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
    """Genera headers para las peticiones a Zoho"""
    return {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

def read_ids_from_csv(csv_file_path: str, id_column: str = 'id') -> List[str]:
    """
    Lee los IDs desde un archivo CSV
    
    Args:
        csv_file_path (str): Ruta al archivo CSV
        id_column (str): Nombre de la columna que contiene los IDs
    
    Returns:
        List[str]: Lista de IDs a buscar
    """
    try:
        df = pd.read_csv(csv_file_path)
        
        if id_column not in df.columns:
            available_columns = ', '.join(df.columns.tolist())
            raise ValueError(f"Columna '{id_column}' no encontrada. Columnas disponibles: {available_columns}")
        
        # Limpiar y convertir IDs a string, eliminar valores nulos
        ids = df[id_column].dropna().astype(str).tolist()
        
        # Remover espacios en blanco
        ids = [id_val.strip() for id_val in ids if id_val.strip()]
        
        logging.info(f"Se leyeron {len(ids)} IDs desde el archivo CSV: {csv_file_path}")
        return ids
        
    except Exception as e:
        logging.error(f"Error al leer el archivo CSV {csv_file_path}: {str(e)}")
        raise

def search_leads_by_ids(ids: List[str], access_token: str, batch_size: int = 100) -> Dict:
    """
    Busca leads en Zoho CRM usando una lista de IDs
    
    Args:
        ids (List[str]): Lista de IDs a buscar
        access_token (str): Token de acceso de Zoho
        batch_size (int): Número de IDs por lote (máximo 100 para Zoho)
    
    Returns:
        Dict: Resultados de la búsqueda con leads encontrados y no encontrados
    """
    headers = get_headers(access_token)
    
    found_leads = []
    not_found_ids = []
    total_ids = len(ids)
    
    logging.info(f"Iniciando búsqueda de {total_ids} leads en lotes de {batch_size}")
    
    # Procesar en lotes
    for i in range(0, total_ids, batch_size):
        batch_ids = ids[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_ids + batch_size - 1) // batch_size
        
        logging.info(f"Procesando lote {batch_num}/{total_batches} ({len(batch_ids)} IDs)")
        
        try:
            # Método 1: Usar endpoint con múltiples IDs en la URL
            ids_param = ','.join(batch_ids)
            get_url = f"{base_url_leads}"
            params = {
                "ids": ids_param,
                "fields": "id,Last_Name,First_Name,Email,Phone,Lead_Status,Created_Time,Periodo"
            }
            
            response = requests.get(get_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    batch_leads = data['data']
                    found_leads.extend(batch_leads)
                    
                    # Identificar IDs encontrados
                    found_ids_in_batch = [lead['id'] for lead in batch_leads]
                    
                    # Identificar IDs no encontrados en este lote
                    not_found_in_batch = [id_val for id_val in batch_ids if id_val not in found_ids_in_batch]
                    not_found_ids.extend(not_found_in_batch)
                    
                    logging.info(f"Lote {batch_num}: {len(batch_leads)} leads encontrados, {len(not_found_in_batch)} no encontrados")
                else:
                    # Si no hay data, todos los IDs del lote no fueron encontrados
                    not_found_ids.extend(batch_ids)
                    logging.info(f"Lote {batch_num}: No se encontraron leads")
                    
            elif response.status_code == 204:
                # No hay contenido - ningún lead encontrado en este lote
                not_found_ids.extend(batch_ids)
                logging.info(f"Lote {batch_num}: No se encontraron leads (204)")
                
            else:
                logging.error(f"Error en lote {batch_num}: {response.status_code} - {response.text}")
                
                # Si falla el método de múltiples IDs, intentar uno por uno
                logging.info(f"Intentando búsqueda individual para lote {batch_num}")
                batch_results = search_leads_individually(batch_ids, headers)
                found_leads.extend(batch_results['found'])
                not_found_ids.extend(batch_results['not_found'])
                
        except Exception as e:
            logging.error(f"Excepción en lote {batch_num}: {str(e)}")
            # Si hay excepción, intentar búsqueda individual
            try:
                logging.info(f"Intentando búsqueda individual para lote {batch_num}")
                batch_results = search_leads_individually(batch_ids, headers)
                found_leads.extend(batch_results['found'])
                not_found_ids.extend(batch_results['not_found'])
            except:
                not_found_ids.extend(batch_ids)
        
        # Pausa entre lotes para evitar límites de API
        if i + batch_size < total_ids:
            time.sleep(1)
    
    results = {
        'found_leads': found_leads,
        'not_found_ids': not_found_ids,
        'summary': {
            'total_searched': total_ids,
            'found_count': len(found_leads),
            'not_found_count': len(not_found_ids),
            'success_rate': (len(found_leads) / total_ids * 100) if total_ids > 0 else 0
        }
    }
    
    logging.info(f"Búsqueda completada: {len(found_leads)} encontrados, {len(not_found_ids)} no encontrados")
    return results

def search_leads_individually(ids: List[str], headers: Dict) -> Dict:
    """
    Busca leads uno por uno cuando falla la búsqueda en lote
    
    Args:
        ids (List[str]): Lista de IDs a buscar
        headers (Dict): Headers para las peticiones HTTP
    
    Returns:
        Dict: Diccionario con leads encontrados y no encontrados
    """
    found = []
    not_found = []
    
    for lead_id in ids:
        try:
            url = f"{base_url_leads}/{lead_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    found.append(data['data'][0])
                    logging.debug(f"Lead encontrado: {lead_id}")
                else:
                    not_found.append(lead_id)
                    logging.debug(f"Lead no encontrado: {lead_id}")
            else:
                not_found.append(lead_id)
                logging.debug(f"Error al buscar lead {lead_id}: {response.status_code}")
                
            # Pequeña pausa entre peticiones individuales
            time.sleep(0.1)
            
        except Exception as e:
            logging.error(f"Error al buscar lead individual {lead_id}: {str(e)}")
            not_found.append(lead_id)
    
    return {'found': found, 'not_found': not_found}

def update_leads_periodo(leads: List[Dict], access_token: str, periodo_value: str = "25V04", batch_size: int = 100) -> Dict:
    """
    Actualiza el campo Periodo de los leads encontrados
    
    Args:
        leads (List[Dict]): Lista de leads a actualizar
        access_token (str): Token de acceso de Zoho
        periodo_value (str): Valor a asignar al campo Periodo
        batch_size (int): Número de leads por lote (máximo 100 para Zoho)
    
    Returns:
        Dict: Resultados de la actualización
    """
    headers = get_headers(access_token)
    
    updated_leads = []
    failed_updates = []
    total_leads = len(leads)
    
    logging.info(f"Iniciando actualización de {total_leads} leads con Periodo = {periodo_value}")
    
    # Procesar en lotes
    for i in range(0, total_leads, batch_size):
        batch_leads = leads[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_leads + batch_size - 1) // batch_size
        
        logging.info(f"Actualizando lote {batch_num}/{total_batches} ({len(batch_leads)} leads)")
        
        try:
            # Preparar datos para actualización
            update_data = []
            for lead in batch_leads:
                update_data.append({
                    "id": lead["id"],
                    "Periodo": periodo_value
                })
            
            # Crear payload para Zoho
            payload = {
                "data": update_data,
                "trigger": ["approval", "workflow", "blueprint"]
            }
            
            # Hacer petición de actualización
            update_url = f"{base_url_leads}"
            response = requests.put(update_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    # Procesar respuesta de cada lead
                    for result in data['data']:
                        if result.get('status') == 'success':
                            updated_leads.append({
                                'id': result.get('details', {}).get('id'),
                                'status': 'success',
                                'periodo_updated': periodo_value
                            })
                            logging.debug(f"Lead {result.get('details', {}).get('id')} actualizado correctamente")
                        else:
                            failed_updates.append({
                                'id': result.get('details', {}).get('id'),
                                'status': 'failed',
                                'error': result.get('message', 'Error desconocido')
                            })
                            logging.warning(f"Error al actualizar lead {result.get('details', {}).get('id')}: {result.get('message')}")
                    
                    logging.info(f"Lote {batch_num}: {len([r for r in data['data'] if r.get('status') == 'success'])} actualizados correctamente")
                else:
                    # Si no hay data en la respuesta, marcar todos como fallidos
                    for lead in batch_leads:
                        failed_updates.append({
                            'id': lead['id'],
                            'status': 'failed',
                            'error': 'Sin respuesta de datos'
                        })
                        
            else:
                logging.error(f"Error en actualización lote {batch_num}: {response.status_code} - {response.text}")
                # Marcar todos los leads del lote como fallidos
                for lead in batch_leads:
                    failed_updates.append({
                        'id': lead['id'],
                        'status': 'failed',
                        'error': f'HTTP {response.status_code}'
                    })
                    
        except Exception as e:
            logging.error(f"Excepción en actualización lote {batch_num}: {str(e)}")
            # Marcar todos los leads del lote como fallidos
            for lead in batch_leads:
                failed_updates.append({
                    'id': lead['id'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Pausa entre lotes para evitar límites de API
        if i + batch_size < total_leads:
            time.sleep(1)
    
    update_results = {
        'updated_leads': updated_leads,
        'failed_updates': failed_updates,
        'summary': {
            'total_to_update': total_leads,
            'updated_count': len(updated_leads),
            'failed_count': len(failed_updates),
            'success_rate': (len(updated_leads) / total_leads * 100) if total_leads > 0 else 0
        }
    }
    
    logging.info(f"Actualización completada: {len(updated_leads)} actualizados, {len(failed_updates)} fallidos")
    return update_results

def search_and_update_leads_from_csv(csv_file_path: str, env_vars: Dict, id_column: str = 'id', 
                                   periodo_value: str = "25V04", output_file: Optional[str] = None) -> Dict:
    """
    Función principal que lee IDs desde CSV, busca leads y actualiza el campo Periodo
    
    Args:
        csv_file_path (str): Ruta al archivo CSV con los IDs
        env_vars (Dict): Variables de entorno con tokens de Zoho
        id_column (str): Nombre de la columna que contiene los IDs
        periodo_value (str): Valor a asignar al campo Periodo
        output_file (Optional[str]): Archivo donde guardar los resultados
    
    Returns:
        Dict: Resultados de la búsqueda y actualización
    """
    try:
        # Obtener access token actualizado
        access_token = refresh_access_token(env_vars)
        
        # Leer IDs desde CSV
        ids = read_ids_from_csv(csv_file_path, id_column)
        
        if not ids:
            logging.warning("No se encontraron IDs válidos en el archivo CSV")
            return {
                'search_results': {'found_leads': [], 'not_found_ids': [], 'summary': {'total_searched': 0}},
                'update_results': {'updated_leads': [], 'failed_updates': [], 'summary': {'total_to_update': 0}}
            }
        
        # PASO 1: Buscar leads
        logging.info("=" * 50)
        logging.info("PASO 1: BÚSQUEDA DE LEADS")
        logging.info("=" * 50)
        search_results = search_leads_by_ids(ids, access_token)
        
        # Guardar resultados de búsqueda si se especifica archivo de salida
        if output_file:
            save_results_to_file(search_results, f"{output_file}_search")
        
        # Mostrar resumen de búsqueda
        search_summary = search_results['summary']
        logging.info(f"""
        RESUMEN DE BÚSQUEDA:
        - Total buscados: {search_summary['total_searched']}
        - Encontrados: {search_summary['found_count']}
        - No encontrados: {search_summary['not_found_count']}
        - Tasa de éxito: {search_summary['success_rate']:.2f}%
        """)
        
        # PASO 2: Actualizar leads encontrados
        update_results = {'updated_leads': [], 'failed_updates': [], 'summary': {'total_to_update': 0}}
        
        if search_results['found_leads']:
            logging.info("=" * 50)
            logging.info(f"PASO 2: ACTUALIZACIÓN DE CAMPO PERIODO = {periodo_value}")
            logging.info("=" * 50)
            
            update_results = update_leads_periodo(search_results['found_leads'], access_token, periodo_value)
            
            # Guardar resultados de actualización
            if output_file:
                save_update_results_to_file(update_results, f"{output_file}_update")
            
            # Mostrar resumen de actualización
            update_summary = update_results['summary']
            logging.info(f"""
            RESUMEN DE ACTUALIZACIÓN:
            - Total a actualizar: {update_summary['total_to_update']}
            - Actualizados: {update_summary['updated_count']}
            - Fallidos: {update_summary['failed_count']}
            - Tasa de éxito: {update_summary['success_rate']:.2f}%
            """)
        else:
            logging.warning("No se encontraron leads para actualizar")
        
        # RESUMEN GENERAL
        logging.info("=" * 50)
        logging.info("RESUMEN GENERAL DEL PROCESO")
        logging.info("=" * 50)
        logging.info(f"IDs procesados: {search_summary['total_searched']}")
        logging.info(f"Leads encontrados: {search_summary['found_count']}")
        logging.info(f"Leads actualizados: {update_results['summary']['updated_count']}")
        logging.info(f"Leads con errores: {update_results['summary']['failed_count']}")
        
        return {
            'search_results': search_results,
            'update_results': update_results
        }
        
    except Exception as e:
        logging.error(f"Error en el proceso de búsqueda y actualización: {str(e)}")
        raise

def save_results_to_file(results: Dict, output_file: str):
    """
    Guarda los resultados de búsqueda en archivos CSV
    
    Args:
        results (Dict): Resultados de la búsqueda
        output_file (str): Nombre base del archivo de salida
    """
    try:
        # Guardar leads encontrados
        if results['found_leads']:
            found_df = pd.DataFrame(results['found_leads'])
            found_file = f"{output_file}_found_leads.csv"
            found_df.to_csv(found_file, index=False)
            logging.info(f"Leads encontrados guardados en: {found_file}")
        
        # Guardar IDs no encontrados
        if results['not_found_ids']:
            not_found_df = pd.DataFrame({'id': results['not_found_ids']})
            not_found_file = f"{output_file}_not_found_ids.csv"
            not_found_df.to_csv(not_found_file, index=False)
            logging.info(f"IDs no encontrados guardados en: {not_found_file}")
        
        # Guardar resumen
        summary_df = pd.DataFrame([results['summary']])
        summary_file = f"{output_file}_summary.csv"
        summary_df.to_csv(summary_file, index=False)
        logging.info(f"Resumen guardado en: {summary_file}")
        
    except Exception as e:
        logging.error(f"Error al guardar resultados de búsqueda: {str(e)}")

def save_update_results_to_file(results: Dict, output_file: str):
    """
    Guarda los resultados de actualización en archivos CSV
    
    Args:
        results (Dict): Resultados de la actualización
        output_file (str): Nombre base del archivo de salida
    """
    try:
        # Guardar leads actualizados
        if results['updated_leads']:
            updated_df = pd.DataFrame(results['updated_leads'])
            updated_file = f"{output_file}_updated_leads.csv"
            updated_df.to_csv(updated_file, index=False)
            logging.info(f"Leads actualizados guardados en: {updated_file}")
        
        # Guardar actualizaciones fallidas
        if results['failed_updates']:
            failed_df = pd.DataFrame(results['failed_updates'])
            failed_file = f"{output_file}_failed_updates.csv"
            failed_df.to_csv(failed_file, index=False)
            logging.info(f"Actualizaciones fallidas guardadas en: {failed_file}")
        
        # Guardar resumen de actualización
        summary_df = pd.DataFrame([results['summary']])
        summary_file = f"{output_file}_update_summary.csv"
        summary_df.to_csv(summary_file, index=False)
        logging.info(f"Resumen de actualización guardado en: {summary_file}")
        
    except Exception as e:
        logging.error(f"Error al guardar resultados de actualización: {str(e)}")

# Función principal modificada
def main():
    """
    Función principal que busca leads desde CSV y actualiza el campo Periodo
    """
    # Configurar logging
    log_file = setup_logging()
    
    try:
        # Cargar variables de entorno
        env_vars = load_environment()
        
        # Especificar archivo CSV con los IDs
        csv_file = "Posibles_Clientes (1).csv"  # Cambia por tu archivo
        id_column = "lead_id"  # Cambia por el nombre de tu columna
        periodo_value = "25V04"  # Valor a actualizar en el campo Periodo
        
        # Ejecutar búsqueda y actualización
        results = search_and_update_leads_from_csv(
            csv_file_path=csv_file,
            env_vars=env_vars,
            id_column=id_column,
            periodo_value=periodo_value,
            output_file="leads_proceso_completo"
        )
        
        # Mostrar resultado final
        search_summary = results['search_results']['summary']
        update_summary = results['update_results']['summary']
        
        print(f"""
        ===== PROCESO COMPLETADO =====
        ✓ IDs procesados: {search_summary['total_searched']}
        ✓ Leads encontrados: {search_summary['found_count']}
        ✓ Leads actualizados con Periodo='{periodo_value}': {update_summary['updated_count']}
        ✗ Errores en actualización: {update_summary['failed_count']}
        
        📄 Ver logs detallados en: {log_file}
        """)
        
    except Exception as e:
        logging.error(f"Error en el proceso principal: {str(e)}")
        print(f"❌ Error: {str(e)}")
        print(f"📄 Ver logs en: {log_file}")
        raise

if __name__ == "__main__":
    main()