import pandas as pd

def unir_csv(lista_archivos, nombre_salida):
    """
    Une varios archivos CSV en un solo archivo CSV.

    :param lista_archivos: Lista de rutas de archivos CSV a unir.
    :param nombre_salida: Nombre del archivo CSV resultante.
    """
    # Leer y concatenar todos los archivos CSV de la lista
    datos_combinados = pd.concat([pd.read_csv(archivo) for archivo in lista_archivos])

    # Guardar el archivo CSV resultante
    datos_combinados.to_csv(nombre_salida, index=False)

# Ejemplo de uso:
lista_de_archivos = ["DATA/Notes_001.csv", "DATA/Notes_002.csv", "DATA/Notes_003.csv", "DATA/Notes_004.csv", "DATA/Notes_005.csv", "DATA/Notes_006.csv", "DATA/Notes_007.csv", "DATA/Notes_008.csv", "DATA/Notes_009.csv", "DATA/Notes_010.csv", "DATA/Notes_011.csv", "DATA/Notes_012.csv", "DATA/Notes_013.csv", "DATA/Notes_014.csv", "DATA/Notes_015.csv", "DATA/Notes_016.csv", "DATA/Notes_017.csv", "DATA/Notes_018.csv", "DATA/Notes_019.csv", "DATA/Notes_020.csv", "DATA/Notes_021.csv", "DATA/Notes_022.csv", "DATA/Notes_023.csv", "DATA/Notes_024.csv", "DATA/Notes_025.csv", "DATA/Notes_026.csv", "DATA/Notes_027.csv", "DATA/Notes_028.csv", "DATA/Notes_029.csv", "DATA/Notes_030.csv", "DATA/Notes_031.csv", "DATA/Notes_032.csv", "DATA/Notes_033.csv", "DATA/Notes_034.csv"]

unir_csv(lista_de_archivos, 'resultado.csv')
