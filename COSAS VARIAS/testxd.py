import customtkinter as ctk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter.messagebox as msgbox
import threading
import sys
import os

# Configuración de CustomTkinter
try:
    ctk.set_appearance_mode("system")  # Usa el tema del sistema
    ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"
except Exception as e:
    print(f"Error configurando tema: {e}")

class EmailSenderApp:
    def __init__(self):
        try:
            # Inicializar la ventana principal
            self.root = ctk.CTk()
            self.root.title("Envío de Correos Electrónicos")
            self.root.geometry("650x750")
            self.root.minsize(600, 700)
            self.root.resizable(True, True)
            
            # Centrar la ventana
            self.center_window()
            
            # Variables
            self.email_destino = "e62d1k6jc9kx569nz7@trigger.zohoflow.com"  
            
            # Configurar la interfaz
            self.setup_ui()
            
        except Exception as e:
            print(f"Error inicializando la aplicación: {e}")
            sys.exit(1)
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        try:
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            window_width = 650
            window_height = 750
            
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        except Exception as e:
            print(f"Error centrando ventana: {e}")
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        try:
            # Scrollable frame principal
            main_frame = ctk.CTkScrollableFrame(self.root)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Título
            title_label = ctk.CTkLabel(
                main_frame, 
                text="📧 Envío de Correos Electrónicos", 
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=(10, 20))
            
            # Dirección de destino
            dest_frame = ctk.CTkFrame(main_frame, fg_color="#404040")
            dest_frame.pack(fill="x", padx=10, pady=(10, 15))
            
            ctk.CTkLabel(dest_frame, text="📧 Dirección de destino:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            dest_label = ctk.CTkLabel(dest_frame, text=f"→ {self.email_destino}", font=ctk.CTkFont(size=12))
            dest_label.pack(anchor="w", padx=10, pady=(0, 5))
            
            warning_label = ctk.CTkLabel(
                dest_frame, 
                text="HECHO POR DAVID ROMERO UWU ZOHO",
                font=ctk.CTkFont(size=10),
                text_color="#FFA500"
            )
            warning_label.pack(anchor="w", padx=10, pady=(0, 10))
            
            # Dirección remitente
            ctk.CTkLabel(main_frame, text="Tu dirección de correo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            self.email_entry = ctk.CTkEntry(main_frame, placeholder_text="tu_email@gmail.com", height=35)
            self.email_entry.pack(fill="x", padx=10, pady=(0, 15))
            
            # Contraseña
            ctk.CTkLabel(main_frame, text="Contraseña de aplicación:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            self.password_entry = ctk.CTkEntry(main_frame, placeholder_text="Contraseña o App Password", show="*", height=35)
            self.password_entry.pack(fill="x", padx=10, pady=(0, 10))
            
            # Información sobre contraseña
            info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            info_label = ctk.CTkLabel(
                info_frame, 
                text="💡 Para Gmail, usa una 'Contraseña de aplicación'",
                font=ctk.CTkFont(size=11)
            )
            info_label.pack(side="left", padx=5)
            
            help_button = ctk.CTkButton(
                info_frame,
                text="❓ Ayuda",
                width=60,
                height=25,
                font=ctk.CTkFont(size=10),
                command=self.show_help
            )
            help_button.pack(side="right", padx=5)
            
            # Proveedor
            ctk.CTkLabel(main_frame, text="Proveedor de correo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            self.provider_var = ctk.StringVar(value="Gmail")
            provider_menu = ctk.CTkOptionMenu(
                main_frame, 
                values=["Gmail", "Outlook/Hotmail", "Yahoo"],
                variable=self.provider_var,
                height=35
            )
            provider_menu.pack(fill="x", padx=10, pady=(0, 15))
            
            # Asunto
            ctk.CTkLabel(main_frame, text="Asunto del correo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            self.subject_entry = ctk.CTkEntry(main_frame, placeholder_text="Asunto del mensaje", height=35)
            self.subject_entry.pack(fill="x", padx=10, pady=(0, 15))
            
            # Contenido
            ctk.CTkLabel(main_frame, text="Contenido del correo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            self.content_text = ctk.CTkTextbox(main_frame, height=120)
            self.content_text.pack(fill="x", padx=10, pady=(0, 15))
            
            # Código de actividad
            ctk.CTkLabel(main_frame, text="Código de actividad:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            self.activity_code_entry = ctk.CTkEntry(main_frame, placeholder_text="Código de actividad", height=35)
            self.activity_code_entry.pack(fill="x", padx=10, pady=(0, 20))
            
            # Botón de envío
            self.send_button = ctk.CTkButton(
                main_frame,
                text="📤 Enviar Correo",
                command=self.send_email_threaded,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            self.send_button.pack(fill="x", padx=10, pady=10)
            
            # Barra de progreso
            self.progress_bar = ctk.CTkProgressBar(main_frame)
            self.progress_bar.pack(fill="x", padx=10, pady=10)
            self.progress_bar.set(0)
            
            # Estado
            self.status_label = ctk.CTkLabel(main_frame, text="Listo para enviar correo")
            self.status_label.pack(pady=10)
            
        except Exception as e:
            print(f"Error configurando UI: {e}")
            msgbox.showerror("Error", f"Error configurando la interfaz: {e}")
    
    def show_help(self):
        """Muestra ayuda para configurar contraseñas de aplicación"""
        help_text = """🔐 CONFIGURACIÓN DE CONTRASEÑAS DE APLICACIÓN

📧 PARA GMAIL:
1. Ve a: myaccount.google.com
2. Click en "Seguridad" (menú izquierdo)
3. Activar "Verificación en 2 pasos" (si no está activa)
4. Buscar "Contraseñas de aplicaciones"
5. Seleccionar "Correo" → "Otro"
6. Escribir nombre: "Mi App Correo"
7. Copiar la contraseña de 16 dígitos
8. Usar ESA contraseña (no tu contraseña normal)

📧 PARA OUTLOOK/HOTMAIL:
1. Ve a: account.microsoft.com
2. "Seguridad" → "Opciones de seguridad avanzadas"
3. "Contraseñas de aplicación" → "Crear nueva"
4. Usar la contraseña generada

📧 PARA YAHOO:
1. Ve a: account.yahoo.com
2. "Seguridad de la cuenta" → "Generar contraseña de aplicación"
3. Seleccionar "Correo" → "Generar"
4. Usar la contraseña generada

⚠️ IMPORTANTE:
• NO uses tu contraseña normal de email
• SIEMPRE usa la contraseña de aplicación generada
• Guarda la contraseña en un lugar seguro"""

        # Crear ventana de ayuda
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("Ayuda - Configuración de Contraseñas")
        help_window.geometry("500x600")
        help_window.resizable(False, False)
        
        # Centrar ventana de ayuda
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Contenido de ayuda
        help_textbox = ctk.CTkTextbox(help_window, wrap="word")
        help_textbox.pack(fill="both", expand=True, padx=20, pady=20)
        help_textbox.insert("1.0", help_text)
        help_textbox.configure(state="disabled")
        
        # Botón cerrar
        close_button = ctk.CTkButton(
            help_window,
            text="Cerrar",
            command=help_window.destroy,
            width=100
        )
        close_button.pack(pady=(0, 20))
        
    def get_smtp_config(self, provider):
        """Obtiene la configuración SMTP según el proveedor"""
        configs = {
            "Gmail": ("smtp.gmail.com", 587),
            "Outlook/Hotmail": ("smtp-mail.outlook.com", 587),
            "Yahoo": ("smtp.mail.yahoo.com", 587)
        }
        return configs.get(provider, configs["Gmail"])
        
    def validate_fields(self):
        """Valida que todos los campos estén llenos y correctos"""
        email = self.email_entry.get().strip()
        if not email:
            msgbox.showerror("Error", "Por favor ingresa tu dirección de correo")
            return False
        
        # Validación básica de formato de email
        if "@" not in email or "." not in email.split("@")[-1]:
            msgbox.showerror("Error", "Por favor ingresa un email válido\nEjemplo: tu_email@gmail.com")
            return False
        
        if not self.password_entry.get().strip():
            msgbox.showerror("Error", "Por favor ingresa tu contraseña\n\n💡 Para Gmail, usa una 'Contraseña de aplicación'")
            return False
        if not self.subject_entry.get().strip():
            msgbox.showerror("Error", "Por favor ingresa el asunto del correo")
            return False
        if not self.content_text.get("1.0", "end").strip():
            msgbox.showerror("Error", "Por favor ingresa el contenido del correo")
            return False
        if not self.activity_code_entry.get().strip():
            msgbox.showerror("Error", "Por favor ingresa el código de actividad")
            return False
        return True
        
    def send_email_threaded(self):
        """Ejecuta el envío de email en un hilo separado para no bloquear la UI"""
        if not self.validate_fields():
            return
            
        # Deshabilitar botón y mostrar progreso
        self.send_button.configure(state="disabled", text="Enviando...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Preparando envío...")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.send_email)
        thread.daemon = True
        thread.start()
        
    def send_email(self):
        """Función principal para enviar el correo"""
        try:
            # Actualizar progreso
            self.root.after(0, lambda: self.progress_bar.set(0.2))
            self.root.after(0, lambda: self.status_label.configure(text="Configurando servidor..."))
            
            # Obtener datos
            sender_email = self.email_entry.get().strip()
            password = self.password_entry.get().strip()
            subject = self.subject_entry.get().strip()
            content = self.content_text.get("1.0", "end").strip()
            activity_code = self.activity_code_entry.get().strip()
            provider = self.provider_var.get()
            
            # Construir el cuerpo del mensaje con el código de actividad
            full_content = f"{content}\n\nCódigo de actividad: {activity_code}"
            
            # Actualizar progreso
            self.root.after(0, lambda: self.progress_bar.set(0.4))
            self.root.after(0, lambda: self.status_label.configure(text="Creando mensaje..."))
            
            # Crear el mensaje
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = self.email_destino
            msg['Subject'] = subject
            
            # Agregar el cuerpo del mensaje
            msg.attach(MIMEText(full_content, 'plain', 'utf-8'))
            
            # Actualizar progreso
            self.root.after(0, lambda: self.progress_bar.set(0.6))
            self.root.after(0, lambda: self.status_label.configure(text="Conectando al servidor..."))
            
            # Configuración del servidor SMTP
            smtp_server, smtp_port = self.get_smtp_config(provider)
            
            # Enviar correo
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Habilitar seguridad
                
                # Actualizar progreso
                self.root.after(0, lambda: self.progress_bar.set(0.8))
                self.root.after(0, lambda: self.status_label.configure(text="Autenticando..."))
                
                server.login(sender_email, password)
                
                # Actualizar progreso
                self.root.after(0, lambda: self.progress_bar.set(0.9))
                self.root.after(0, lambda: self.status_label.configure(text="Enviando correo..."))
                
                text = msg.as_string()
                server.sendmail(sender_email, self.email_destino, text)
            
            # Éxito
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            self.root.after(0, lambda: self.status_label.configure(text="✅ ¡Correo enviado exitosamente!"))
            self.root.after(0, lambda: msgbox.showinfo("✅ Éxito", f"¡Correo enviado exitosamente!\n\nPara: {self.email_destino}\nAsunto: {subject}"))
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "🔐 ERROR DE AUTENTICACIÓN\n\n"
            
            if "gmail" in sender_email.lower():
                error_msg += "Para GMAIL:\n" \
                           "1. Ve a myaccount.google.com\n" \
                           "2. Seguridad → Verificación en 2 pasos (activar)\n" \
                           "3. Seguridad → Contraseñas de aplicaciones\n" \
                           "4. Genera una contraseña de 16 dígitos\n" \
                           "5. Usa ESA contraseña (no tu contraseña normal)\n\n"
            elif "outlook" in sender_email.lower() or "hotmail" in sender_email.lower():
                error_msg += "Para OUTLOOK/HOTMAIL:\n" \
                           "1. Ve a account.microsoft.com\n" \
                           "2. Seguridad → Opciones de seguridad avanzadas\n" \
                           "3. Contraseñas de aplicación → Crear nueva\n" \
                           "4. Usa esa contraseña generada\n\n"
            else:
                error_msg += "Verifica:\n" \
                           "• Email correcto\n" \
                           "• Contraseña correcta\n" \
                           "• Si es Gmail/Outlook, usa contraseña de aplicación\n\n"
            
            error_msg += f"Error técnico: {str(e)}"
            
            self.root.after(0, lambda: msgbox.showerror("Error de Autenticación", error_msg))
            self.root.after(0, lambda: self.status_label.configure(text="❌ Error de autenticación"))
        except smtplib.SMTPException as e:
            error_msg = f"🌐 ERROR DEL SERVIDOR DE CORREO\n\n"
            error_msg += f"Problema: {str(e)}\n\n"
            error_msg += "Posibles soluciones:\n"
            error_msg += "• Verifica tu conexión a internet\n"
            error_msg += "• El servidor puede estar temporalmente no disponible\n"
            error_msg += "• Verifica que el proveedor de correo sea correcto\n"
            error_msg += "• Algunos antivirus bloquean conexiones SMTP"
            
            self.root.after(0, lambda: msgbox.showerror("Error del Servidor", error_msg))
            self.root.after(0, lambda: self.status_label.configure(text="❌ Error del servidor"))
        except Exception as e:
            error_msg = f"❌ ERROR INESPERADO\n\n"
            error_msg += f"Error: {str(e)}\n\n"
            error_msg += "Posibles causas:\n"
            error_msg += "• Conexión a internet inestable\n"
            error_msg += "• Firewall o antivirus bloqueando\n"
            error_msg += "• Problema temporal del servidor"
            
            self.root.after(0, lambda: msgbox.showerror("Error Inesperado", error_msg))
            self.root.after(0, lambda: self.status_label.configure(text="❌ Error inesperado"))
        finally:
            # Rehabilitar botón
            self.root.after(0, lambda: self.send_button.configure(state="normal", text="📤 Enviar Correo"))
            if self.progress_bar.get() != 1.0:
                self.root.after(0, lambda: self.progress_bar.set(0))
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error ejecutando aplicación: {e}")
            msgbox.showerror("Error Fatal", f"Error ejecutando la aplicación: {e}")

def main():
    """Función principal"""
    try:
        # Verificar que CustomTkinter esté instalado
        import customtkinter
        print("Iniciando aplicación de envío de correos...")
        
        # Crear y ejecutar la aplicación
        app = EmailSenderApp()
        app.run()
        
    except ImportError:
        print("Error: CustomTkinter no está instalado.")
        print("Instala con: pip install customtkinter")
        input("Presiona Enter para salir...")
    except Exception as e:
        print(f"Error fatal: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()