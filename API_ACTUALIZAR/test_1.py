import pandas as pd
from datetime import datetime

# Función para convertir una fecha en string a formato datetime
def convert_to_datetime(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y %H:%M")

# Esta función procesará los registros de forma binaria y simulará la actualización de datos
def process_records_binary(df, start, end, registros_actualizados):
    if start > end:
        return

    mid = (start + end) // 2
    row = df.iloc[mid]
    cadaid = row['Id']
    hora_modificacion_excel = convert_to_datetime(row['fecha'])

    # Simulación de la fecha de modificación en el CRM (usar una fecha ficticia para la comparación)
    hora_modificacion_crm = datetime(2023, 1, 1, 12, 0)  # Fecha ficticia

    if hora_modificacion_excel >= hora_modificacion_crm:
        # Si el registro necesita actualización, lo añadimos con los nuevos datos
        registro_actualizado = {
            'Id': cadaid,
            'Estado_del_Registro':"x", #row['Estado'],
            'Sub_estado':"z",#row['sub estado'],
            'Sub_estado_II':"ss", #row['sub estado II'],
            'Sub_estado_III': "xd", #row['sub estado III'],
            'Hora_Modificaci_n': hora_modificacion_excel.strftime("%Y-%m-%d %H:%M:%S")
        }
        registros_actualizados.append(registro_actualizado)
    else:
        # Si no requiere actualización, lo añadimos tal cual
        registro_no_actualizado = {
            'Id': cadaid,
            'Estado_del_Registro': "No Actualizado",
            'Sub_estado': "No Actualizado",
            'Sub_estado_II': "No Actualizado",
            'Sub_estado_III': "No Actualizado",
            'Hora_Modificaci_n': hora_modificacion_crm.strftime("%Y-%m-%d %H:%M:%S")
        }
        registros_actualizados.append(registro_no_actualizado)

    # Llamadas recursivas
    process_records_binary(df, start, mid - 1, registros_actualizados)
    process_records_binary(df, mid + 1, end, registros_actualizados)

# Cargar los datos desde el CSV
df = pd.read_csv('testo.csv')
registros_actualizados = []

# Llamar a la función para procesar los registros
process_records_binary(df, 0, len(df) - 1, registros_actualizados)

# Convertir la lista de registros actualizados en un DataFrame y guardarlo en un nuevo archivo CSV
df_actualizados = pd.DataFrame(registros_actualizados)
df_actualizados.to_csv('registros_actualizados.csv', index=False)

print("Archivo 'registros_actualizados.csv' creado con los registros simulados como actualizados en el CRM.")
