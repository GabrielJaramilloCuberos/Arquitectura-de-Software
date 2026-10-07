import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

# ================ FUNCIONES DE CORREO ================

# Cargar variables de entorno desde el archivo .env
load_dotenv(Path(__file__).with_name(".env"))

# Función para enviar un correo electrónico con el código final
def enviar_correo(codigo: str, grupo: int) -> None:

  # Se obtienen las credenciales del remitente y destinatario desde las variables de entorno
  remitente = os.getenv("CORREO_REMITENTE")
  destinatario = os.getenv("CORREO_DESTINATARIO")
  clave = os.getenv("CORREO_CLAVE")

  # Se crea el mensaje de correo electrónico con el código final recibido
  mensaje = EmailMessage()
  mensaje["Subject"] = "Arquitectura de Software - Taller MQTT: Código Final"
  mensaje["From"] = remitente
  mensaje["To"] = destinatario
  mensaje.set_content(f"El código final es: {codigo}\nEnviado desde el grupo {grupo}")

  # Se envía el mensaje a través del servidor SMTP
  with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
    servidor.login(remitente, clave)
    servidor.send_message(mensaje)
