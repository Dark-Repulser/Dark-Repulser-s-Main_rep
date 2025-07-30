from tkinter import messagebox
import customtkinter as ctk

que_le_gusta_a_juan = str(input("¿Qué come Juan? "))

if que_le_gusta_a_juan == "pilin":
    messagebox.showinfo ("xd",f"verda si come")
    
else:
     messagebox.showerror("xd", f"NOPE, COME PILIN XD")
    
        
        

def ask_juan():
            root = ctk.CTk()
            root.withdraw()  # Hide the root window
            answer = ctk.CTkInputDialog(text="¿Qué come Juan?", title="Pregunta").get_input()
            root.destroy()
            return answer

que_le_gusta_a_juan = ask_juan()

if que_le_gusta_a_juan == "pilin":
            messagebox.showinfo("xd", "verda si come")
else:
          messagebox.showerror("xd", "NOPE, COME PILIN XD")