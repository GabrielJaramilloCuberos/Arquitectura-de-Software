import argparse

from correo import enviar_correo
from imagen import cargar_imagen, decodificar_imagen
from mqtt_cliente import conectar_mqtt, publicar_codigo, suscribir_grupo

NUMERO_GRUPO = 0

# Función para imprimir eventos con emojis según el tipo de evento
def imprimir_evento(*lineas):
  print("\n" + "─" * 35)
  for linea in lineas:
    if linea.startswith("Conectado"):
      emoji = "📡"
    elif linea.startswith("Mensaje recibido"):
      emoji = "📨"
    elif linea.startswith("Enviando"):
      emoji = "📤"
    elif linea.startswith("Se envió"):
      emoji = "✅"
    elif linea.startswith("Código decodificado"):
      emoji = "🔍"
    else:
      emoji = "ℹ️"
    print(f"{emoji} {linea}")
  print("─" * 35)

# Función de callback para cuando el cliente se conecta al broker MQTT
def on_connect(cliente, userdata, flags, razon, propiedades):
  imprimir_evento("Conectado al broker")
  suscribir_grupo(cliente, NUMERO_GRUPO)

# Función para actualizar el código incrementando los dos últimos dígitos
def actualizar_codigo(codigo: str) -> str:
  return codigo[:-2] + str(int(codigo[-2:]) + 1).zfill(2)

# Función para enviar un nuevo código al grupo correspondiente
def enviar_nuevo_codigo(cliente, codigo: str, posicion_actual: int):
  grupo_destino = codigo[posicion_actual + 1]
  nuevo_codigo = actualizar_codigo(codigo)
  imprimir_evento(f"Enviando nuevo código: {nuevo_codigo} al grupo {grupo_destino}")
  return publicar_codigo(cliente, int(grupo_destino), nuevo_codigo)

# Función de callback para cuando se recibe un mensaje en el broker MQTT
def on_message(cliente, userdata, mensaje):
  contenido = mensaje.payload.decode("utf-8")
  imprimir_evento(f"Mensaje recibido en {mensaje.topic}: {contenido}")

  # Recorre las posiciones del código para determinar a qué grupo pertenece y enviar el nuevo código
  for posicion in range(1, 5):
    if contenido[posicion] == str(NUMERO_GRUPO):
      if posicion != 4:
        enviar_nuevo_codigo(cliente, contenido, posicion)
      else:
        contenido = actualizar_codigo(contenido)
        imprimir_evento(
          f"Se envió el código final: {contenido} desde el grupo {NUMERO_GRUPO} al correo correspondiente."
        )
        enviar_correo(contenido, NUMERO_GRUPO)
      break

# Función para obtener el número de grupo desde los argumentos de línea de comandos
def obtener_numero_grupo() -> int:
  parser = argparse.ArgumentParser(
    description="Ejecuta la participación de un grupo en el taller MQTT."
  )
  parser.add_argument(
    "grupo",
    type=int,
    choices=range(1, 6),
    help="Número del grupo que se va a ejecutar (1 a 5).",
  )
  argumentos = parser.parse_args()
  return argumentos.grupo

def main():
  numero_grupo = obtener_numero_grupo()
  global NUMERO_GRUPO
  NUMERO_GRUPO = numero_grupo

  imagen = cargar_imagen("codigo-barras-2.png")
  codigo = decodificar_imagen(imagen)

  if codigo[0] == str(NUMERO_GRUPO):
    cliente = conectar_mqtt()
    cliente.loop_start()
    imprimir_evento(f"Código decodificado: {codigo}")
    enviar_nuevo_codigo(cliente, codigo, 0).wait_for_publish()
    cliente.loop_stop()
    cliente.disconnect()
  else:
    cliente = conectar_mqtt(on_connect=on_connect, on_message=on_message)
    cliente.loop_forever()


if __name__ == "__main__":
  main()
