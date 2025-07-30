import pandas as pd

#ruta del archivo(debe estar en la carpeta del codigo)
archivo = "Tickets_Zoho_Desk.csv" 
df = pd.read_csv(archivo, low_memory=False)

print(len(df))
#print(df.head(10))
#filtro por columna y valor
filtro = df[df["Estado"].str.contains("Cerrado FCR", case=False, na=False)]

columnas = ["ID de la solicitud", "Estado"] + [col for col in filtro.columns if col not in ["ID de la solicitud", "Estado"]]
filtro = filtro[columnas]

# filas = filtro.rows
# cant = len(filas)
# print(cant)
# print(filtro.head(15))

#filtro.to_csv('result.csv', index=False)

# print("El archivo se ha guardado como 'result.xlsx'")


