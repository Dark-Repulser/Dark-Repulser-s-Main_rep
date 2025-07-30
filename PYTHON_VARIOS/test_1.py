import pandas as pd

# Ruta del archivo (debe estar en la carpeta del código)
archivo = "Tickets_Zoho_Desk.csv"
df = pd.read_csv(archivo, low_memory=False) 

# Filtro por columna y valor, manteniendo solo las filas donde "Estado" sea "Cerrado FCR"
filtro = df[df["Estado"].str.contains("Open",  case=False, na=True) | df["Estado"].isna()]
print(len(filtro))
# Seleccionar solo las columnas "ID" y "Estado"
filtro = filtro[['ID de la solicitud', 'Estado']]

#print(filtro.head(20))

# Exportar el resultado a un archivo Excel
filtro.to_excel('resultados_op_na.xlsx', index=False)

print("El archivo se ha guardado")

