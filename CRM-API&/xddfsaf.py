import customtkinter as ctk
import random
import time

def girar_ruleta():
    nombres = [entrada1.get(), entrada2.get()]
    nombres = [nombre for nombre in nombres if nombre.strip()]
    if nombres:
        for _ in range(20):  # Simulación de animación de ruleta
            resultado.set(random.choice(nombres))
            ventana.update()
            time.sleep(0.2)
        resultado.set(random.choice(nombres))
    else:
        resultado.set("Ingrese nombres válidos")

# Configuración de la ventana
ctk.set_appearance_mode("dark")
ventana = ctk.CTk()
ventana.title("Ruleta de Nombres")
ventana.geometry("300x250")

# Variables
resultado = ctk.StringVar()

# Entradas
entrada1 = ctk.CTkEntry(ventana, placeholder_text="Nombre 1")
entrada1.pack(pady=10)

entrada2 = ctk.CTkEntry(ventana, placeholder_text="Nombre 2")
entrada2.pack(pady=10)

# Botón para girar la ruleta
boton_girar = ctk.CTkButton(ventana, text="Girar", command=girar_ruleta)
boton_girar.pack(pady=10)

# Etiqueta de resultado
label_resultado = ctk.CTkLabel(ventana, textvariable=resultado, font=("Arial", 16))
label_resultado.pack(pady=10)

ventana.mainloop()
