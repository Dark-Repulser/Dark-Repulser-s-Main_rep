import tkinter as tk
import pandas as pd

root = tk.Tk()
root.title("Formulario")

nombre_var = tk.StringVar()
telefono_var = tk.StringVar()
correo_var = tk.StringVar()
monto_var = tk.StringVar()
lugarEnvio_var = tk.StringVar()

def guardar_datos():
    nombre = nombre_var.get()
    telefono = telefono_var.get()
    correo = correo_var.get()
    monto = monto_var.get()
    lugar = lugarEnvio_var.get()
 
    datos = {
        'Nombre': [nombre],
        'Telefono': [telefono],
        'Correo': [correo],
        'Monto': [monto],
        'Lugar': [lugar]
    }

    df = pd.DataFrame(datos)

    df.to_csv('datos_formulario.csv', mode='a', header=False, index=False)

    nombre_var.set("")
    telefono_var.set("")
    correo_var.set("")
    monto_var.set("")
    lugarEnvio_var.set("")

    print("Datos guardados con éxito")

tk.Label(root, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=nombre_var).grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Teléfono:").grid(row=1, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=telefono_var).grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Correo:").grid(row=2, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=correo_var).grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Monto:").grid(row=3, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=monto_var).grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Lugar de Envío:").grid(row=4, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=lugarEnvio_var).grid(row=4, column=1, padx=10, pady=5)

tk.Button(root, text="Guardar", command=guardar_datos).grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
