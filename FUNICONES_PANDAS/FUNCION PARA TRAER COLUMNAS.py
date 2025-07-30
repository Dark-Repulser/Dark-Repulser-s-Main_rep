import pandas as pd

# Nombre del archivo
archivo = 'resultado.csv'

# Columnas a cargar, incluida la columna 'Estado', 'Hora de modificación', y 'Parent Id.Module'
columnas_a_cargar = ["Parent Id.Module", "ID principal.id", "Hora de modificación"]

# Cargar las columnas específicas del archivo CSV
df = pd.read_csv(archivo, usecols=columnas_a_cargar, low_memory=False)

# Convertir la columna 'Hora de modificación' a formato de fecha
df['Hora de modificación'] = pd.to_datetime(df['Hora de modificación'], errors='coerce')

# Definir las fechas de inicio y fin para el filtro
fecha_inicio = '2023-10-01'
fecha_fin = '2024-09-13'


df_filtrado = df[(df['Hora de modificación'] >= fecha_inicio) & (df['Hora de modificación'] <= fecha_fin) & (df['Parent Id.Module'] == 'Leads')]


df_filtrado['Parent Id.Module'] = df_filtrado['Parent Id.Module'].str.replace('Leads', '', regex=False)


df_filtrado['ID principal.id'] = df_filtrado['ID principal.id'].str.replace('zcrm_', '', regex=False)


df_resultado = df_filtrado[['ID principal.id',"Parent Id.Module"]]


df_resultado.to_csv('ids_estado_filtrado_leads.csv', index=False)

print("El archivo filtrado se ha guardado como 'ids_estado_filtrado_leads.csv'")
