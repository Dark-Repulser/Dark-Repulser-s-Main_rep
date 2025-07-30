import requests
from requests.auth import HTTPBasicAuth
import json

# URL de tu sitio con el endpoint personalizado
url = "http://test24654.wordpress.com/wp-json/jetpack-form/v1/entradas"

# Credenciales de un usuario válido en WordPress (preferiblemente con permisos de lectura)
usuario = "davidromerom8f0531a7ee"
contraseña = "David_17"

# Petición a la API
response = requests.get(url, auth=HTTPBasicAuth(usuario, contraseña))

# Procesar la respuesta
if response.status_code == 200:
    formularios = response.json()
    print("Formularios encontrados:\n")
    for form in formularios:
        print(f"Nombre: {form['nombre']}")
        print(f"Correo: {form['correo']}")
        print(f"Mensaje: {form['mensaje']}")
        print(f"Fecha: {form['fecha']}\n")
else:
    print(f"Error {response.status_code}: {response.text}")
