import os
import requests
import pandas as pd
from dotenv import load_dotenv
from time import sleep
import sys

# ===================== CONFIGURACIÓN INICIAL =====================

dotenv_path = r"C:\\Users\\david_romerom\\OneDrive - Corporación Unificada Nacional de Educación Superior - CUN\\Documentos\\cs.env"
load_dotenv(dotenv_path=dotenv_path)

ACCESS_TOKEN = os.getenv("ACCESSTK")
REFRESH_TOKEN = os.getenv("REFRESHTK")
CLIENT_ID = os.getenv("CLIENTID")
CLIENT_SECRET = os.getenv("CLIENTST")

# URLs de la API Zoho
TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
URL_LEADS_SEARCH = "https://www.zohoapis.com/crm/v5/Leads/search"
URL_CONTACTS_SEARCH = "https://www.zohoapis.com/crm/v5/Contacts/search"

# ===================== FUNCIONES AUXILIARES =====================

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """Muestra una barra de progreso en la consola"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()

# ===================== FUNCIONES PRINCIPALES =====================

def refresh_access_token():
    """Refresca el token de acceso usando el refresh token"""
    global ACCESS_TOKEN
    data = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        ACCESS_TOKEN = response.json()['access_token']
        print("\n✅ Access token actualizado correctamente.")
        return True
    else:
        print(f"\n❌ Error al actualizar el token: {response.status_code} - {response.text}")
        return False

def get_headers():
    """Genera los headers para las solicitudes a la API"""
    return {
        "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def generar_criterios_por_lote(lista_docs):
    """Genera criterios de búsqueda para un lote de documentos"""
    criterios = [f"(Email:equals:{doc})" for doc in lista_docs]
    return "(" + " or ".join(criterios) + ")"

def buscar_en_modulo(url, lista_docs, modulo, total_docs):
    """Busca documentos en un módulo específico de Zoho CRM"""
    if not lista_docs:
        return [], lista_docs  # Devuelve la lista original como no encontrada

    resultados = []
    no_encontrados = []
    procesados = 0
    
    print(f"\n🔍 Buscando en módulo {modulo}...")
    
    # Dividir en lotes de 10 (límite de Zoho)
    for i in range(0, len(lista_docs), 10):
        lote = lista_docs[i:i+10]
        criterios = generar_criterios_por_lote(lote)
        params = {"criteria": criterios}
        
        # Actualizar barra de progreso
        procesados += len(lote)
        print_progress_bar(procesados, len(lista_docs), prefix=' Progreso:', suffix=f'Completado ({procesados}/{len(lista_docs)})', length=30)
        
        try:
            response = requests.get(url, headers=get_headers(), params=params)
            
            if response.status_code == 401:
                print("\n🔄 Token expirado, intentando actualizar...")
                if refresh_access_token():
                    response = requests.get(url, headers=get_headers(), params=params)
                else:
                    no_encontrados.extend(lote)
                    continue
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    resultados.extend(data["data"])
                    # Identificar qué documentos del lote no fueron encontrados
                    encontrados_en_lote = [str(r.get("Email", "")) for r in data["data"]]
                    no_encontrados.extend([d for d in lote if d not in encontrados_en_lote])
            elif response.status_code == 204:
                no_encontrados.extend(lote)
            else:
                print(f"\n⚠️ Error en la búsqueda en {modulo}: {response.status_code} - {response.text}")
                no_encontrados.extend(lote)
            
            sleep(0.5)  # Esperar para evitar rate limiting
            
        except Exception as e:
            print(f"\n⚠️ Excepción al buscar en {modulo}: {str(e)}")
            no_encontrados.extend(lote)
    
    return resultados, no_encontrados

def procesar_csv(path_csv):
    """Procesa el CSV de entrada y busca en Zoho CRM"""
    try:
        # Leer el CSV original conservando todos los documentos
        df_original = pd.read_csv(path_csv)
        
        # Limpieza de correos electrónicos
        df_original['doc_clean'] = df_original['doc'].apply(
            lambda x: str(x).strip() if pd.notnull(x) and str(x).strip() != '' else None
        )
        
        # Correos únicos para búsqueda (excluyendo None)
        docs_unicos = sorted(set(d for d in df_original['doc_clean'] if d is not None))
        
        print(f"\n📊 Iniciando proceso para {len(docs_unicos)} correos únicos...")

        resultados_completos = {}

        # 1. Buscar en Contactos (Interesados)
        contactos, no_encontrados_contactos = buscar_en_modulo(
            URL_CONTACTS_SEARCH, docs_unicos, "Interesados", len(docs_unicos)
        )
        
        for c in contactos:
            doc = str(c.get("Email", ""))
            resultados_completos[doc] = {
                "doc": doc,
                "nombre": c.get("Full_Name") or f"{c.get('First_Name', '')} {c.get('Last_Name', '')}".strip(),
                "modulo": "Interesados",
                "id": c.get("id", ""),
                "email": c.get("Email", ""),
                "telefono": c.get("Phone", ""),
                "estado": c.get("Estado_interesado", ""),
                "encontrado": True
            }
        
        if no_encontrados_contactos:
            leads, no_encontrados_leads = buscar_en_modulo(
                URL_LEADS_SEARCH, no_encontrados_contactos, "Posibles Clientes", len(no_encontrados_contactos))
            
            for l in leads:
                doc = str(l.get("Email", ""))
                resultados_completos[doc] = {
                    "doc": doc,
                    "nombre": l.get("Full_Name") or f"{l.get('First_Name', '')} {l.get('Last_Name', '')}".strip(),
                    "modulo": "Posibles Clientes",
                    "id": l.get("id", ""),
                    "email": l.get("Email", ""),
                    "telefono": l.get("Phone", ""),
                    "estado": l.get("Estado_lead", ""),
                    "encontrado": True,
                    "campaña": l.get("Campan_a_mercadeo", {"name": ""}).get("name", "")     
                }
            
            for doc in no_encontrados_leads:
                resultados_completos[doc] = {
                    "doc": doc,
                    "nombre": "NO ENCONTRADO",
                    "modulo": "NO ENCONTRADO",
                    "id": "",
                    "email": "",
                    "telefono": "",
                    "estado": "",
                    "encontrado": False
                }
        
        resultados_finales = []
        
        for _, row in df_original.iterrows():
            doc_original = row['doc']
            doc_clean = row['doc_clean']
            
            if doc_clean in resultados_completos:
                resultado = resultados_completos[doc_clean].copy()
                resultado['doc_original'] = doc_original
                resultados_finales.append(resultado)
            else:
                resultados_finales.append({
                    "doc": doc_clean if doc_clean else str(doc_original),
                    "doc_original": doc_original,
                    "nombre": "DOCUMENTO INVÁLIDO" if pd.isnull(doc_original) or str(doc_original).strip() == 'nan' else "NO PROCESADO",
                    "modulo": "NO PROCESADO",
                    "id": "",
                    "email": "",
                    "telefono": "",
                    "estado": "",
                    "encontrado": False
                })
        
        return pd.DataFrame(resultados_finales)
    
    except Exception as e:
        print(f"\n❌ Error al procesar el CSV: {str(e)}")
        return pd.DataFrame()

# ===================== EJECUCIÓN PRINCIPAL =====================

if __name__ == "__main__":
    csv_path = "test1.csv"  # Cambia esto según tu archivo de entrada
    
    try:
        print("\n🚀 Iniciando proceso de búsqueda en Zoho CRM")
        resultado_df = procesar_csv(csv_path)
        
        if not resultado_df.empty:
            # Guardar resultados
            output_path = "resultado_correo.csv"
            
            # Ordenar columnas para mejor presentación
            column_order = ['doc_original', 'doc', 'nombre', 'modulo', 'encontrado', 'email', 'telefono', 'estado', 'id']
            column_order = [c for c in column_order if c in resultado_df.columns]
            resultado_df = resultado_df[column_order + [c for c in resultado_df.columns if c not in column_order]]
            
            resultado_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            # Mostrar resumen estadístico
            print("\n" + "="*60)
            print("📊 RESUMEN FINAL".center(60))
            print("="*60)
            
            total = len(resultado_df)
            encontrados_interesados = len(resultado_df[resultado_df['modulo'] == 'Interesados'])
            encontrados_leads = len(resultado_df[resultado_df['modulo'] == 'Posibles Clientes'])
            no_encontrados = len(resultado_df[resultado_df['modulo'] == 'NO ENCONTRADO'])
            no_procesados = len(resultado_df[resultado_df['modulo'] == 'NO PROCESADO'])
            documentos_invalidos = len(resultado_df[resultado_df['nombre'] == 'DOCUMENTO INVÁLIDO'])
            
            print(f"\n🔹 Total registros en CSV original: {total}")
            print(f"🔹 Documentos válidos procesados: {total - documentos_invalidos - no_procesados}")
            print(f"🔹 Encontrados en Interesados: {encontrados_interesados} ({encontrados_interesados/total*100:.1f}%)")
            print(f"🔹 Encontrados en Posibles Clientes: {encontrados_leads} ({encontrados_leads/total*100:.1f}%)")
            print(f"🔹 No encontrados: {no_encontrados} ({no_encontrados/total*100:.1f}%)")
            print(f"🔹 Documentos inválidos/no procesados: {documentos_invalidos + no_procesados} ({(documentos_invalidos + no_procesados)/total*100:.1f}%)")
            
            print(f"\n✅ Proceso finalizado. Resultados completos guardados en '{output_path}'")
            print("="*60)
            
            # Mostrar algunos ejemplos de no encontrados
            if no_encontrados > 0:
                print("\n🔍 Ejemplos de documentos no encontrados:")
                print(resultado_df[resultado_df['modulo'] == 'NO ENCONTRADO'][['doc_original', 'doc']].head(5).to_string(index=False))
            
            if documentos_invalidos > 0:
                print("\n⚠️ Ejemplos de documentos inválidos/no procesados:")
                print(resultado_df[resultado_df['nombre'] == 'DOCUMENTO INVÁLIDO'][['doc_original']].head(5).to_string(index=False))
        else:
            print("\n❌ No se generaron resultados. Verifica los errores anteriores.")
    
    except Exception as e:
        print(f"\n❌ Error en la ejecución principal: {str(e)}")