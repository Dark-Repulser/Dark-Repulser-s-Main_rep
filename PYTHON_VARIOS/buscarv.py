import pandas as pd

def compare_and_extract_differences(csv_a_path, csv_b_path, output_csv_path):
    # Cargar los archivos CSV
    df_a = pd.read_csv(csv_a_path)
    df_b = pd.read_csv(csv_b_path)
    
    # Definir las columnas a comparar
    columns_to_compare = ['Etapa_del_Registro', 'Sub_Estado', 'Sub_Estado_II', 'Sub_Estado_III']
    
    # Filtrar para los registros en df_b que tengan alguna diferencia con los mismos registros en df_a
    # Esto requiere una clave o índice común para asegurar que estamos comparando el mismo registro
    df_diff = df_b[~df_b[columns_to_compare].apply(tuple, 1).isin(df_a[columns_to_compare].apply(tuple, 1))]
    
    # Guardar el resultado en un nuevo archivo CSV
    df_diff.to_csv(output_csv_path, index=False)

# Uso de la función
compare_and_extract_differences('Posibles_Clientes (15).csv', 'Libro2_modified.csv', 'archivo_diferencias.csv')
