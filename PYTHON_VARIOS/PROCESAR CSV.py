import pandas as pd
import re
import logging
from datetime import datetime

# ---------------------------
# CONFIGURACIÓN DE LOGS
# ---------------------------
fecha_log = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    filename=f"procesamiento_BC_{fecha_log}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Inicio del proceso de organización de datos BC")

# ---------------------------
# LECTURA DEL CSV
# ---------------------------
try:
    df = pd.read_csv("tu_archivo.csv", encoding="utf-8")  # Cambia el nombre del archivo aquí
    logging.info(f"Archivo leído correctamente. Total filas: {len(df)}")
except Exception as e:
    logging.error(f"Error al leer el archivo CSV: {e}")
    raise

# ---------------------------
# FUNCIÓN DE EXTRACCIÓN
# ---------------------------
def extraer_campos(texto):
    """
    Extrae pares tipo 'Campo : Valor' de un texto y devuelve un dict.
    Si no hay estructura, retorna None.
    """
    if not isinstance(texto, str):
        return None

    # Expresión regular para detectar "Campo : Valor"
    pares = re.findall(r'([\wÁÉÍÓÚÑáéíóúüÜ\s¿?]+)\s*:\s*([^:]+?)(?=\s+\w+\s*:|$)', texto)

    if not pares:
        return None

    # Convertir a dict limpiando espacios
    datos = {clave.strip(): valor.strip() for clave, valor in pares}
    return datos if datos else None

# ---------------------------
# PROCESAMIENTO DE LA COLUMNA BC
# ---------------------------
procesadas = 0
no_procesadas = 0
registros_extraidos = []

for i, fila in df["BC"].items():
    try:
        extraido = extraer_campos(fila)
        if extraido:
            registros_extraidos.append(extraido)
            procesadas += 1
        else:
            registros_extraidos.append({})
            no_procesadas += 1
    except Exception as e:
        logging.error(f"Error procesando fila {i}: {e}")
        registros_extraidos.append({})
        no_procesadas += 1

logging.info(f"Filas procesadas correctamente: {procesadas}")
logging.info(f"Filas sin estructura reconocible: {no_procesadas}")

# ---------------------------
# CREAR NUEVAS COLUMNAS
# ---------------------------
df_expandidas = pd.DataFrame(registros_extraidos)
df_final = pd.concat([df, df_expandidas], axis=1)

# ---------------------------
# GUARDAR RESULTADO EN EXCEL
# ---------------------------
nombre_salida = f"BC_procesado_{fecha_log}.xlsx"
try:
    with pd.ExcelWriter(nombre_salida, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Datos Procesados")
    logging.info(f"Archivo procesado guardado como {nombre_salida}")
except Exception as e:
    logging.error(f"Error al guardar el archivo Excel: {e}")
    raise

# ---------------------------
# RESUMEN FINAL
# ---------------------------
print("✅ Proceso completado con éxito")
print(f"➡️ Filas totales: {len(df)}")
print(f"📂 Filas procesadas: {procesadas}")
print(f"⚠️ Filas no estructuradas: {no_procesadas}")
print(f"📘 Archivo resultante: {nombre_salida}")
print(f"🪵 Logs guardados en: procesamiento_BC_{fecha_log}.log")
