#HECHO POR DAVID ROMERO.
#FUNCION PARA TRAER COLUMNAS ESPECIFICAS DE UN CSV

import pandas as pd


archivo = 'result_test_open.csv'


columnas_a_cargar = ["ID de la solicitud"]  

 
df = pd.read_csv(archivo, usecols=columnas_a_cargar, low_memory=False)


df.to_csv('COLUMNAS_SERGIO.csv', index=False)

print("El archivo se ha guardado como 'COLUMNAS_SERGIO.csv'")

