from pathlib import Path

import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol

# ================ FUNCIONES DE IMAGEN ================

# Se carga la imagen desde la ruta especificada
def cargar_imagen(nombre):
  ruta_imagen = Path(__file__).with_name(nombre)
  datos_imagen = np.fromfile(ruta_imagen, dtype=np.uint8)
  imagen = cv2.imdecode(datos_imagen, cv2.IMREAD_COLOR)

  if imagen is None:
      raise FileNotFoundError(f"No se pudo cargar la imagen: {ruta_imagen}")

  return imagen

# Se decodifica la imagen para obtener el código de barras EAN-13
def decodificar_imagen(imagen) -> str:
  codigos = decode(imagen, symbols=[ZBarSymbol.EAN13])
  if not codigos:
      raise ValueError("No se detectó ningún código de barras EAN-13 en la imagen.")

  codigo = codigos[0].data.decode("utf-8")
  return codigo
