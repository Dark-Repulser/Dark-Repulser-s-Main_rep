import requests
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

access_token = "1000.d9a6ec9e7dddf9668be1f7bcac0812c7.ac72907364870253e5f11fb8ce70d307"
refresh_token = "1000.0b8233b62707b577fe16832434abc213.b66c40f4c700c262ce57fedb128d3f06"
client_id = "1000.9KLJEBGO230LA4N7PDKFH9G9G69WXH"
client_secret = "ccba688719aba106669ffd09fcfe1eb5ecd12e28c2"

def refresh_access_token():
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        global access_token
        access_token = response.json()['access_token']
        print("Access token actualizado correctamente.")
    else:
        print("Error al actualizar el access token:", response.status_code)
        print(response.text)

def get_headers():
    return {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

def actualizar_registro(numero_cedula):
    # Buscar el registro por número de cédula
    url_search = f"https://www.zohoapis.com/crm/v2/Contacts/search?criteria=(N_mero_de_identificaci_n1:equals:{numero_cedula})"
    response = requests.get(url_search, headers=get_headers())
    
    if response.status_code == 401:  # Token expirado, intenta refrescarlo
        refresh_access_token()
        response = requests.get(url_search, headers=get_headers())

    if response.status_code == 200:
        data = response.json()
        print(data)
        if not data.get('data'):
            messagebox.showinfo("Información", "No se encontró ningún registro con esa cédula.")
            return

        interesado = data['data'][0]
        interesado_id = interesado['id']

        # Verificar campos Proceso y Fecha de pago
        proceso = interesado.get('Proceso', '')
        fecha_pago = interesado.get('Fecha_de_pago', '')

        update_data = {
            "data": [
                {
                    "Estado_del_Registro": "En tramite",
                    "Estado_de_Pionero": "En proceso de matricula",
                    "Estado": "En proceso de matricula"
                }
            ]
        }

        if not proceso:
            update_data["data"][0]["Proceso"] = "Inicia"

        if not fecha_pago:
            update_data["data"][0]["Fecha_de_pago"] = datetime.now().strftime("%Y-%m-%d")

        # Actualizar el registro en CRM
        update_url = f"https://www.zohoapis.com/crm/v2/Contacts/{interesado_id}"
        update_response = requests.put(update_url, headers=get_headers(), data=json.dumps(update_data))

        if update_response.status_code == 200:
            messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
        else:
            messagebox.showerror("Error", f"Error al actualizar el registro: {update_response.status_code}")
    else:
        messagebox.showerror("Error", f"Error al buscar el registro: {response.status_code}")

def mostrar_ventana():

    def enviar_cedula():
        numero_cedula = entrada_cedula.get()
        if numero_cedula:
            actualizar_registro(numero_cedula)
        else:
            messagebox.showwarning("Advertencia", "Por favor, ingrese un número de cédula.")
    
    ctk.set_appearance_mode("dark")  # Modos: "light", "dark", "system"
    ctk.set_default_color_theme("green")  # Temas: "blue", "green", "dark-blue"

    ventana = ctk.CTk()  # Crear la ventana principal
    ventana.title("Desbloquear registro por cédula")
    ventana.geometry("550x300")
    ventana.resizable(False, False)

    # Contenedor principal
    frame = ctk.CTkFrame(ventana, corner_radius=20, fg_color="#2E2E2E")  # Fondo oscuro
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # Etiqueta estilizada
    etiqueta = ctk.CTkLabel(frame, text="Ingrese número de cédula", font=("Terminal", 18, "bold"), text_color="#FFFFFF")
    etiqueta.pack(pady=10)
    et2 = ctk.CTkLabel(frame, text="made by David RM-zohito xd", font=("Terminal", 16, "bold"), text_color="#0ED44E")
    et2.pack(pady=10)

    # Campo de entrada más grande y estilizado 
    entrada_cedula = ctk.CTkEntry(
        frame, 
        placeholder_text="Número de cédula", 
        width=300, 
        height=40, 
        corner_radius=10
    )
    entrada_cedula.pack(pady=10)

    # Botón estilizado con color personalizado
    boton_enviar = ctk.CTkButton(
        frame,
        text="Desbloquear",
        font=("Calibri", 14, "bold"),
        width=200,
        height=30,
        command=enviar_cedula,
        corner_radius=15,
        fg_color="#C82AE8",  # Verde suave #5FBF6E
        hover_color="#B225CF"  # Más oscuro al pasar el mouse #FFFFF
    )
    boton_enviar.pack(pady=15)

    ventana.mainloop()

if __name__ == "__main__":
    mostrar_ventana()